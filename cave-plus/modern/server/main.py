#!/usr/bin/env python3
"""
Cave-Plus Web Recreation - Main Server
FastAPI + WebSocket server for real-time multiplayer
"""

import asyncio
import json
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from game_state import GameState
from player import Player
from commands import CommandParser

app = FastAPI(title="Cave-Plus Recreation")

# Game state
game_state = GameState()
command_parser = CommandParser(game_state)

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize game and start game loop"""
    await game_state.initialize()
    asyncio.create_task(game_loop())
    print("🎮 Cave-Plus server started!")
    print("📍 Navigate to http://localhost:8000")

async def game_loop():
    """Main game loop - runs every second"""
    while True:
        try:
            events = await game_state.update()
            attack_events = events.get("attacks", [])
            movement_events = events.get("movements", [])
            
            # Broadcast creature movements
            for movement in movement_events:
                old_room = movement["old_room"]
                new_room = movement["new_room"]
                creature_name = movement["creature_name"]
                movement_type = movement["type"]
                
                if movement_type == "walk":
                    # Walking messages (normal movement) - go to status window
                    await broadcast_to_room(old_room, {
                        "type": "message",
                        "text": f"The {creature_name} has left",
                        "style": "action"
                    })
                    
                    await broadcast_to_room(new_room, {
                        "type": "message",
                        "text": f"The {creature_name} has just wandered in",
                        "style": "action"
                    })
                else:
                    # Teleport messages (rare, magical) - go to status window
                    disappear_msg = movement["disappear_msg"]
                    appear_msg = movement["appear_msg"]
                    
                    await broadcast_to_room(old_room, {
                        "type": "message",
                        "text": f"The {creature_name} {disappear_msg}",
                        "style": "action"
                    })
                    
                    await broadcast_to_room(new_room, {
                        "type": "message",
                        "text": f"The {creature_name} {appear_msg}!",
                        "style": "action"
                    })
            
            # Broadcast creature attacks to affected players
            if attack_events:
                for attack in attack_events:
                    room_id = attack.get("room_id")
                    creature_name = attack.get("creature")
                    target_name = attack.get("target")
                    damage = attack.get("damage")
                    verb = attack.get("verb")
                    
                    # Notify target player
                    target_player = game_state.get_player(target_name)
                    if target_player:
                        await send_to_player(target_player, {
                            "type": "message",
                            "text": f"The {creature_name} {verb} you for {damage} damage!",
                            "style": "combat"
                        })
                        
                        # Update player stats
                        await send_to_player(target_player, {
                            "type": "player_update",
                            "player": target_player.to_dict()
                        })
                        
                        # Check if player died
                        if target_player.stamina <= 0:
                            target_player.deaths += 1
                            target_player.respawn()
                            target_player.room_id = 1
                            target_player.inventory = []
                            
                            # Make all creatures forget about this player
                            game_state.reset_creatures_targeting_player(target_player.name)
                            
                            await send_to_player(target_player, {
                                "type": "message",
                                "text": "You have been slain! Respawning at entrance...",
                                "style": "death"
                            })
                            await send_room_update(target_player)
                    
                    # Broadcast to others in room
                    await broadcast_to_room(room_id, {
                        "type": "message",
                        "text": f"The {creature_name} {verb} {target_name}!",
                        "style": "combat"
                    }, exclude=target_name)
            
            await asyncio.sleep(1.0)  # 1 second tick
        except Exception as e:
            print(f"Game loop error: {e}")

@app.websocket("/ws/{player_name}")
async def websocket_endpoint(websocket: WebSocket, player_name: str):
    """WebSocket endpoint for player connections"""
    await websocket.accept()
    
    # Validate player name
    if not player_name or len(player_name) < 2 or len(player_name) > 20:
        await websocket.send_json({
            "type": "error",
            "message": "Player name must be 2-20 characters"
        })
        await websocket.close()
        return
    
    # Check if name is taken (already logged in)
    if player_name in game_state.players:
        await websocket.send_json({
            "type": "error",
            "message": f"Name '{player_name}' is already logged in"
        })
        await websocket.close()
        return
    
    # Wait for password from client
    try:
        auth_data = await websocket.receive_json()
        password = auth_data.get("password", "").strip()
    except:
        await websocket.send_json({
            "type": "error",
            "message": "Authentication failed"
        })
        await websocket.close()
        return
    
    if not password or len(password) < 4:
        await websocket.send_json({
            "type": "error",
            "message": "Password must be at least 4 characters"
        })
        await websocket.close()
        return
    
    # Try to load existing player or create new one
    from player_data import load_player, player_exists, create_player, save_player, hash_password
    
    saved_data = None
    is_new_player = False
    
    if player_exists(player_name):
        # Existing player - verify password
        saved_data = load_player(player_name, password)
        if saved_data is None:
            await websocket.send_json({
                "type": "error",
                "message": f"Sorry, I know someone called {player_name} and that is not the password."
            })
            await websocket.close()
            return
    else:
        # New player - create account
        print(f"Creating new player: {player_name}")
        saved_data = create_player(player_name, password)
        saved_data['password_hash'] = hash_password(password)
        
        # Save immediately
        if not save_player(saved_data):
            await websocket.send_json({
                "type": "error",
                "message": "Failed to create player account. Please try again."
            })
            await websocket.close()
            return
        
        is_new_player = True
        print(f"✅ New player {player_name} created and saved")
    
    # Create player object
    player = Player(player_name, websocket, saved_data)
    player.password_hash = saved_data['password_hash']  # Store for saving later
    game_state.add_player(player)
    active_connections[player_name] = websocket
    
    # Send welcome message (matching original BBC Micro game)
    if player.rank == "Wizard":
        welcome_msg = "Welcome Powerful Wizard"
    elif not is_new_player:
        welcome_msg = "Welcome again to CAVE"
    else:
        welcome_msg = "Welcome new caver"
    
    await send_to_player(player, {
        "type": "welcome",
        "message": welcome_msg,
        "player": player.to_dict(),
        "new_player": is_new_player
    })
    
    # Send initial room state
    await send_room_update(player)
    
    # Announce to other players in room
    await broadcast_to_room(player.room_id, {
        "type": "message",
        "text": f"{player_name} has entered the cave.",
        "style": "system"
    }, exclude=player_name)
    
    try:
        while True:
            # Receive command from client
            data = await websocket.receive_json()
            await handle_command(player, data)
            
    except WebSocketDisconnect:
        # Player disconnected
        game_state.remove_player(player)
        del active_connections[player_name]
        
        # Announce to other players
        await broadcast_to_room(player.room_id, {
            "type": "message",
            "text": f"{player_name} has left the cave.",
            "style": "system"
        })
        
    except Exception as e:
        print(f"WebSocket error for {player_name}: {e}")
        if player_name in active_connections:
            del active_connections[player_name]
        game_state.remove_player(player)

async def handle_command(player: Player, data: dict):
    """Handle a command from a player"""
    command = data.get("command", "").strip()
    
    if not command:
        return
    
    # Parse and execute command
    result = await command_parser.parse(player, command)
    
    # Handle QUIT command
    if result.get("quit"):
        # Send goodbye message
        await send_to_player(player, {
            "type": "message",
            "text": result.get("message", "Your progress has been saved. Farewell!"),
            "style": "system"
        })
        
        # Disconnect player
        if result.get("disconnect"):
            await send_to_player(player, {
                "type": "disconnect",
                "message": "Goodbye!"
            })
            # Close will be handled by the disconnect exception
            await player.websocket.close()
        return
    
    # Send result to player
    if result.get("message"):
        await send_to_player(player, {
            "type": "message",
            "text": result["message"],
            "style": result.get("style", "normal")
        })
    
    # Update room if player moved
    if result.get("moved"):
        await send_room_update(player)
        
        # Announce to old room
        if result.get("old_room"):
            await broadcast_to_room(result["old_room"], {
                "type": "message",
                "text": f"{player.name} left {result.get('direction', '')}.",
                "style": "action"
            })
        
        # Announce to new room
        await broadcast_to_room(player.room_id, {
            "type": "message",
            "text": f"{player.name} arrived.",
            "style": "action"
        }, exclude=player.name)
    
    # Broadcast chat messages
    if result.get("broadcast"):
        # Check if this is a raw broadcast (like HELLO command)
        if result.get("broadcast_raw"):
            broadcast_text = f"{player.name} {result['broadcast']}"
        else:
            broadcast_text = f"{player.name} says: {result['broadcast']}"
        
        await broadcast_to_room(player.room_id, {
            "type": "message",
            "text": broadcast_text,
            "style": "chat"
        }, exclude=player.name)
    
    # Update inventory
    if result.get("inventory_changed"):
        await send_to_player(player, {
            "type": "inventory",
            "items": player.inventory
        })
    
    # Handle PvP combat
    if result.get("pvp"):
        # Notify target player
        target_name = result.get("target_player")
        if target_name:
            target_player = game_state.get_player(target_name)
            if target_player:
                await send_to_player(target_player, {
                    "type": "message",
                    "text": f"{player.name} attacks you!",
                    "style": "combat"
                })
                
                # Update target's stats
                await send_to_player(target_player, {
                    "type": "player_update",
                    "player": target_player.to_dict()
                })
                
                # If target died, notify them and move them
                if result.get("target_died"):
                    await send_to_player(target_player, {
                        "type": "message",
                        "text": "You have been defeated! Respawning at entrance...",
                        "style": "death"
                    })
                    await send_room_update(target_player)
        
        # Broadcast to room (excluding attacker and target)
        await broadcast_to_room(player.room_id, {
            "type": "message",
            "text": f"{player.name} attacks {target_name}!",
            "style": "combat"
        }, exclude=player.name)

async def send_room_update(player: Player):
    """Send complete room state to player"""
    room = game_state.get_room(player.room_id)
    
    if not room:
        return
    
    # Get other players in room
    other_players = [
        p.name for p in game_state.get_players_in_room(player.room_id)
        if p.name != player.name
    ]
    
    # Get objects in room
    objects = game_state.get_objects_in_room(player.room_id)
    
    # Get creatures in room
    creatures = game_state.get_creatures_in_room(player.room_id)
    creature_data = [c.to_dict() for c in creatures]
    
    await send_to_player(player, {
        "type": "room",
        "room": {
            "id": room["id"],
            "name": room.get("name", f"Room {room['id']}"),
            "description": room["description"],
            "exits": room["exits"],
            "has_graphic": room["id"] in game_state.rooms_with_graphics,
            "graphic_url": f"/graphics/room_{room['id']}.png" if room["id"] in game_state.rooms_with_graphics else None
        },
        "players": other_players,
        "objects": objects,
        "creatures": creature_data,
        "player": player.to_dict()
    })

async def send_to_player(player: Player, message: dict):
    """Send a message to a specific player"""
    if player.name in active_connections:
        try:
            await active_connections[player.name].send_json(message)
        except Exception as e:
            print(f"Error sending to {player.name}: {e}")

async def broadcast_to_room(room_id: int, message: dict, exclude: str = None):
    """Broadcast a message to all players in a room"""
    players = game_state.get_players_in_room(room_id)
    
    for player in players:
        if exclude and player.name == exclude:
            continue
        await send_to_player(player, message)

async def broadcast_to_all(message: dict):
    """Broadcast a message to all connected players"""
    for player_name, websocket in active_connections.items():
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error broadcasting to {player_name}: {e}")

# Serve static files
app.mount("/graphics", StaticFiles(directory="../analysed/graphics"), name="graphics")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Serve the main game page"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "players": len(game_state.players),
        "rooms": len(game_state.rooms)
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
