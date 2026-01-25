#!/usr/bin/env python3
"""
Cave-Plus Web Recreation - Main Server
FastAPI + WebSocket server for real-time multiplayer
"""

import asyncio
import json
import time
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

async def handle_player_death(player: Player, skip_death_message: bool = False):
    """
    Handle player death with authentic BBC Micro death sequence
    Based on line 1520: PRINT'"Life is slipping away...You are going";:PROCF:...:PRINT"..":*GOING
    
    Args:
        player: The player who is dying
        skip_death_message: If True, skip "Life is slipping away" message (for cave collapse, etc.)
    """
    try:
        # Save player data before death
        from player_data import save_player
        
        print(f"🪦 Starting death sequence for {player.name} (skip_message={skip_death_message})")
        
        # Disable command input immediately
        await send_to_player(player, {
            "type": "disable_input"
        })
        
        if not skip_death_message:
            # Line 1520: "Life is slipping away...You are going"
            # PRINT'"..." means: blank line, then the message
            # This appears in main screen area (PRINT, not PROCB)
            await send_to_player(player, {
                "type": "message",
                "text": "\nLife is slipping away...You are going",
                "style": "normal"  # Main screen, not status area
            })
            
            print(f"   Sent 'Life is slipping away' message, waiting 1.5s...")
            # Longer delay to let player process what's happening
            await asyncio.sleep(1.5)
        
        # Save player data (PROCF cleanup)
        save_data = player.to_save_dict()
        if hasattr(player, 'password_hash'):
            save_data['password_hash'] = player.password_hash
        
        print(f"   Saving player {player.name} data on death")
        
        # Send disk activity notification
        await send_to_player(player, {
            "type": "disk_activity",
            "operation": "write"
        })
        
        success, disk_time = save_player(save_data)
        print(f"📀 Death save completed (disk time: {disk_time:.2f}s)")
        
        # Small additional delay for visual effect
        await asyncio.sleep(0.3)
        
        if not skip_death_message:
            print(f"   Sending '..' message, waiting 1.5s...")
            # Line 1520: ".." (appends to previous line)
            await send_to_player(player, {
                "type": "message",
                "text": "..",
                "style": "normal"  # Main screen, not status area
            })
            
            # Longer final delay before GOING
            await asyncio.sleep(1.5)
        
        print(f"   Sending disconnect message for GOING screen")
        # Send disconnect to trigger GOING screen
        await send_to_player(player, {
            "type": "disconnect",
            "message": "You have died."
        })
        
        # Small delay to ensure message is sent before closing
        await asyncio.sleep(0.2)
        
        print(f"   Closing websocket for {player.name}")
        # Close connection
        await player.websocket.close()
        
        print(f"✅ Death sequence complete for {player.name}")
        
    except Exception as e:
        print(f"❌ Error in death sequence for {player.name}: {e}")
        import traceback
        traceback.print_exc()

async def game_loop():
    """Main game loop - runs every second"""
    while True:
        try:
            # Check for timed-out disconnected players
            timed_out_players = []
            for player_name, player in list(game_state.players.items()):
                if player.is_timeout_expired():
                    timed_out_players.append(player)
            
            # Remove timed-out players and save their data
            for player in timed_out_players:
                print(f"⏱️  {player.name} disconnect timeout expired - saving and removing")
                
                # Save player data
                from player_data import save_player
                save_data = player.to_save_dict()
                if hasattr(player, 'password_hash'):
                    save_data['password_hash'] = player.password_hash
                success, disk_time = save_player(save_data)
                print(f"📀 Auto-saved {player.name} on timeout (disk time: {disk_time:.2f}s)")
                
                # Announce to room
                await broadcast_to_room(player.room_id, {
                    "type": "message",
                    "text": f"{player.name} has been removed from the cave (timeout).",
                    "style": "action"
                })
                
                # Remove from game
                game_state.remove_player(player)
            
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
                            "style": "combat",
                            "beeps": 2  # Being hit by creature = 2 beeps
                        })
                        
                        # Update player stats
                        await send_to_player(target_player, {
                            "type": "player_update",
                            "player": target_player.to_dict()
                        })
                        
                        # Check if player died
                        if target_player.stamina <= 0:
                            target_player.deaths += 1
                            
                            # Make all creatures forget about this player
                            game_state.reset_creatures_targeting_player(target_player.name)
                            
                            # Broadcast death to room before player is removed
                            await broadcast_to_room(room_id, {
                                "type": "message",
                                "text": f"{target_player.name} has died!",
                                "style": "combat"
                            }, exclude=target_player.name)
                            
                            # Handle death sequence (save, show messages, GOING screen)
                            await handle_player_death(target_player)
                            
                            # Remove player from game state
                            game_state.remove_player(target_player)
                            if target_player.name in active_connections:
                                del active_connections[target_player.name]
                            
                            continue  # Skip room update since player is disconnected
                    
                    # Broadcast to others in room
                    await broadcast_to_room(room_id, {
                        "type": "message",
                        "text": f"The {creature_name} {verb} {target_name}!",
                        "style": "combat"
                    }, exclude=target_name)
            
            await asyncio.sleep(1.0)  # 1 second tick
            
            # Update all players' vodka/poison status
            for player in list(game_state.players.values()):
                # Sober up gradually (line 1460)
                player.update_vodka_level()
                
                # Apply poison damage (line 1480: OH=D:IFM D=D-0.05)
                if player.poisoned:
                    # Store old stamina before applying damage (line 1480: OH=D)
                    old_stamina = player.stamina
                    
                    # Apply poison damage (line 1480: IFM D=D-0.05)
                    player.update_poison_damage()
                    
                    # Line 1500: IFMANDINTD<INTOHPROCB("I am poisoned")
                    # Show "I am poisoned" when stamina crosses whole number boundary
                    if int(player.stamina) < int(old_stamina):
                        await send_to_player(player, {
                            "type": "message",
                            "text": "I am poisoned",
                            "style": "combat",
                            "beeps": 1
                        })
                        
                        # Update player stats
                        await send_to_player(player, {
                            "type": "player_update",
                            "player": player.to_dict()
                        })
                    
                    # Check if player died from poison
                    if player.stamina <= 0:
                        player.deaths += 1
                        
                        # Make all creatures forget about this player
                        game_state.reset_creatures_targeting_player(player.name)
                        
                        # Broadcast death to room
                        await broadcast_to_room(player.room_id, {
                            "type": "message",
                            "text": f"{player.name} has succumbed to poison!",
                            "style": "combat"
                        }, exclude=player.name)
                        
                        # Handle death sequence
                        await handle_player_death(player)
                        
                        # Remove player from game state
                        game_state.remove_player(player)
                        if player.name in active_connections:
                            del active_connections[player.name]
                        
                        continue  # Skip low stamina check for dead player
                
                # Line 1510: IFD<5ANDRND(20)=1PROCB("You are almost dead"):SOUND1,-10,0,1
                # 1/20 chance per tick to show "You are almost dead" when stamina < 5
                import random
                if player.stamina < 5 and random.randint(1, 20) == 1:
                    await send_to_player(player, {
                        "type": "message",
                        "text": "You are almost dead",
                        "style": "combat",
                        "beeps": 1  # SOUND1,-10,0,1 = beep
                    })

                
        except Exception as e:
            print(f"Game loop error: {e}")

@app.websocket("/ws/{player_name}")
async def websocket_endpoint(websocket: WebSocket, player_name: str):
    """WebSocket endpoint for player connections"""
    await websocket.accept()
    
    # Apply BBC Micro name processing (FNB function):
    # 1. Convert to uppercase
    # 2. Keep only letters (remove spaces, numbers, special chars)
    player_name = ''.join(c.upper() for c in player_name if c.isalpha())
    
    # Validate player name
    if not player_name or len(player_name) < 2 or len(player_name) > 20:
        await websocket.send_json({
            "type": "error",
            "message": "Player name must be 2-20 characters"
        })
        await websocket.close()
        return
    
    # Check if player is already in game (disconnected but still active)
    existing_player = game_state.players.get(player_name)
    if existing_player and existing_player.is_disconnected:
        # Reconnection! Need to verify password first
        print(f"🔄 {player_name} attempting reconnection (was disconnected for {time.time() - existing_player.disconnect_time:.1f}s)")
        
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
        
        # Verify password
        from player_data import verify_password
        if not hasattr(existing_player, 'password_hash') or not verify_password(password, existing_player.password_hash):
            await websocket.send_json({
                "type": "error",
                "message": f"Sorry, I know someone called {player_name} and that is not the password."
            })
            await websocket.close()
            return
        
        # Password verified - reconnect!
        print(f"✅ {player_name} reconnected successfully")
        existing_player.reconnect(websocket)
        active_connections[player_name] = websocket
        player = existing_player
        
        # Send welcome-style message to trigger UI transition
        await send_to_player(player, {
            "type": "welcome",
            "message": "Reconnected! You are still in the cave.",
            "player_list": "",  # No player list on reconnect
            "player": player.to_dict(),
            "new_player": False
        })
        
        # Announce to room
        await broadcast_to_room(player.room_id, {
            "type": "message",
            "text": f"{player_name} has reconnected.",
            "style": "action"
        }, exclude=player_name)
        
        # Send current room state
        await send_room_update(player)
        
    elif player_name in game_state.players:
        # Player is already connected (not disconnected)
        await websocket.send_json({
            "type": "error",
            "message": f"Name '{player_name}' is already logged in"
        })
        await websocket.close()
        return
    else:
        # New connection - normal login flow
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
            # Send disk activity notification
            await websocket.send_json({
                "type": "disk_activity",
                "operation": "read"
            })
            
            result = load_player(player_name, password)
            if result is None:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Sorry, I know someone called {player_name} and that is not the password."
                })
                await websocket.close()
                return
            
            saved_data, disk_time = result
            print(f"📀 Loaded player {player_name} (disk time: {disk_time:.2f}s)")
        else:
            # New player - create account
            print(f"Creating new player: {player_name}")
            saved_data = create_player(player_name, password)
            saved_data['password_hash'] = hash_password(password)
            
            # Send disk activity notification
            await websocket.send_json({
                "type": "disk_activity",
                "operation": "write"
            })
            
            # Save immediately
            success, disk_time = save_player(saved_data)
            if not success:
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to create player account. Please try again."
                })
                await websocket.close()
                return
            
            is_new_player = True
            print(f"✅ New player {player_name} created and saved (disk time: {disk_time:.2f}s)")
        
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
        
        # Check if there are other players (matching BBC Micro behavior)
        other_players = [p for p in game_state.players.values() if p.name != player_name]
        
        if len(other_players) == 0:
            # You are alone
            player_list_msg = "You are the only caver here."
        else:
            # Show player list (matching WHO command format exactly)
            player_list_msg = "These people are in CAVE\n"
            
            is_wizard = (player.rank == "Wizard")
            
            for p in other_players:
                # Print player name
                player_list_msg += p.name
                
                # Wizards see extra info (stamina and station number)
                if is_wizard:
                    # TAB(8) = column 8, TAB(22) = column 22
                    # Pad to column 8, show stamina, pad to column 22, show station
                    padding1 = max(1, 8 - len(p.name))
                    player_list_msg += " " * padding1
                    stamina_text = f"stamina {int(p.stamina)}"
                    player_list_msg += stamina_text
                    
                    # Calculate padding to reach column 22
                    current_pos = len(p.name) + padding1 + len(stamina_text)
                    padding2 = max(1, 22 - current_pos)
                    player_list_msg += " " * padding2
                    player_list_msg += f"stn {p.room_id}"
                
                player_list_msg += "\n"
        
        await send_to_player(player, {
            "type": "welcome",
            "message": welcome_msg,
            "player_list": player_list_msg,
            "player": player.to_dict(),
            "new_player": is_new_player
        })
        
        # Send initial room state
        await send_room_update(player)
        
        # Announce to other players in room
        await broadcast_to_room(player.room_id, {
            "type": "message",
            "text": f"{player_name} has entered the cave.",
            "style": "action"  # Changed to action so it goes to status area
        }, exclude=player_name)
    
    try:
        while True:
            # Receive command from client
            data = await websocket.receive_json()
            await handle_command(player, data)
            
    except WebSocketDisconnect:
        # Check if this was an intentional quit
        if hasattr(player, 'is_quitting') and player.is_quitting:
            print(f"👋 {player_name} quit normally")
            # Player already removed in QUIT handler, nothing more to do
            return
        
        # Player disconnected unexpectedly - keep them in game for 5 minutes
        print(f"🔌 {player_name} disconnected - keeping in game for {player.disconnect_timeout}s")
        
        # If portcullis is up, lower it (player let go of rope)
        if game_state.portcullis_up:
            print(f"🪢 {player_name} disconnected while holding rope - lowering portcullis")
            game_state.portcullis_up = False
            
            # Broadcast to rooms 29 and 30
            await broadcast_to_room(29, {
                "type": "message",
                "text": "The portcullis FALLS",
                "style": "action"
            })
            await broadcast_to_room(30, {
                "type": "message",
                "text": "The portcullis FALLS",
                "style": "action"
            })
            # No need to refresh room display - the message is enough
        
        player.mark_disconnected()
        del active_connections[player_name]
        
        # Announce to other players (they're still in the game, just disconnected)
        await broadcast_to_room(player.room_id, {
            "type": "message",
            "text": f"{player_name} has lost connection (still in cave).",
            "style": "action"
        })
        
    except Exception as e:
        print(f"WebSocket error for {player_name}: {e}")
        if player_name in active_connections:
            del active_connections[player_name]
        
        # If portcullis is up, lower it (player let go of rope)
        if game_state.portcullis_up:
            print(f"🪢 {player_name} error while holding rope - lowering portcullis")
            game_state.portcullis_up = False
            
            # Broadcast to rooms 29 and 30
            await broadcast_to_room(29, {
                "type": "message",
                "text": "The portcullis FALLS",
                "style": "action"
            })
            await broadcast_to_room(30, {
                "type": "message",
                "text": "The portcullis FALLS",
                "style": "action"
            })
            # No need to refresh room display - the message is enough
        
        # Mark as disconnected but don't remove from game
        if player_name in game_state.players:
            game_state.players[player_name].mark_disconnected()

async def handle_command(player: Player, data: dict):
    """Handle a command from a player"""
    command = data.get("command", "").strip()
    
    if not command:
        return
    
    # Parse and execute command
    result = await command_parser.parse(player, command)
    
    # Handle QUIT sequence with delays (matching BBC Micro timing)
    if result.get("quit_sequence"):
        # Disable input immediately (before "Hold on" appears)
        await send_to_player(player, {
            "type": "disable_input"
        })
        
        # Line 2720: "Hold on"
        await send_to_player(player, {
            "type": "message",
            "text": "Hold on",
            "style": "system"
        })
        
        # Delay before first dots
        await asyncio.sleep(0.8)
        
        # Line 2740: ".."
        await send_to_player(player, {
            "type": "message",
            "text": "..",
            "style": "system"
        })
        
        # Save player data
        from player_data import save_player
        
        save_data = player.to_save_dict()
        
        # Add password hash (stored on player object)
        if hasattr(player, 'password_hash'):
            save_data['password_hash'] = player.password_hash
        else:
            print(f"⚠️  Warning: Player {player.name} has no password_hash!")
            await send_to_player(player, {
                "type": "message",
                "text": "Error: Cannot save without password. Please contact admin.",
                "style": "error",
                "beeps": 1
            })
            return
        
        print(f"Saving player {player.name} data: {save_data}")
        
        # Send disk activity notification
        await send_to_player(player, {
            "type": "disk_activity",
            "operation": "write"
        })
        
        success, disk_time = save_player(save_data)
        print(f"📀 Save completed (disk time: {disk_time:.2f}s)")
        
        # Delay during save (already included in save_player, but add a bit more for visual effect)
        await asyncio.sleep(0.3)
        
        # Line 2740: "."
        await send_to_player(player, {
            "type": "message",
            "text": ".",
            "style": "system"
        })
        
        # Delay after final dot
        await asyncio.sleep(0.8)
        
        if success:
            # Line 2810: "Saved."
            await send_to_player(player, {
                "type": "message",
                "text": "Saved.",
                "style": "system"
            })
            
            # Delay before GOING screen
            await asyncio.sleep(1.0)
            
            # Send disconnect message to trigger GOING screen
            await send_to_player(player, {
                "type": "disconnect",
                "message": "Goodbye!"
            })
            
            # Mark player as intentionally quitting (not a disconnect)
            player.is_quitting = True
            
            # Remove player from game immediately
            game_state.remove_player(player)
            if player.name in active_connections:
                del active_connections[player.name]
            
            # Announce to room
            await broadcast_to_room(player.room_id, {
                "type": "message",
                "text": f"{player.name} has left the cave.",
                "style": "action"
            })
            
            # Close connection
            await player.websocket.close()
        else:
            await send_to_player(player, {
                "type": "message",
                "text": "Error saving your data. Please try again.",
                "style": "error",
                "beeps": 1
            })
        
        return
    
    # Handle QUIT command (old style, shouldn't be reached)
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
    
    # Handle holding rope - tell client to wait for RETURN (BEFORE sending the message)
    if result.get("holding_rope"):
        await send_to_player(player, {
            "type": "holding_rope"
        })
    
    # Send result to player
    if result.get("message"):
        # Determine style - check for combat flag or explicit style
        if result.get("combat"):
            style = "combat"
        else:
            style = result.get("style", "normal")
        
        # Get beep count (VDU7 simulation)
        beeps = result.get("beeps", 0)
        
        print(f"DEBUG: Sending message: '{result['message']}' with style: {style}")
        
        await send_to_player(player, {
            "type": "message",
            "text": result["message"],
            "style": style,
            "beeps": beeps
        })
    
    # Send status_message separately (for commands like ZAP that have both main and status messages)
    if result.get("status_message"):
        print(f"DEBUG: Sending status_message: '{result['status_message']}'")
        await send_to_player(player, {
            "type": "message",
            "text": result["status_message"],
            "style": "combat"  # Status messages always go to status area
        })
    
    # Send player update if vodka/poison/medicine was consumed or player state changed
    if result.get("healed") or result.get("poisoned") or result.get("cured") or result.get("vodka_level"):
        print(f"Sending player_update for {player.name}. Vodka level: {player.vodka_level}")
        await send_to_player(player, {
            "type": "player_update",
            "player": player.to_dict()
        })
    
    # Update room if player moved (normal movement)
    if result.get("moved"):
        await send_room_update(player)
        
        # Announce to old room (only if different from new room)
        if result.get("old_room") and result["old_room"] != player.room_id:
            await broadcast_to_room(result["old_room"], {
                "type": "message",
                "text": f"{player.name} left {result.get('direction', '')}.",
                "style": "action"
            })
        
        # Announce to new room (only if different from old room)
        if result.get("old_room") != player.room_id:
            await broadcast_to_room(player.room_id, {
                "type": "message",
                "text": f"{player.name} arrived.",
                "style": "action"
            }, exclude=player.name)
    
    # Update room if player teleported (WIZ, TELEPORT, ROOM commands)
    if result.get("room_changed"):
        await send_room_update(player)
        
        # Announce to old room if teleport flag is set
        if result.get("teleport") and result.get("old_room") and result["old_room"] != player.room_id:
            await broadcast_to_room(result["old_room"], {
                "type": "message",
                "text": f"{player.name} vanishes!",
                "style": "action"
            })
        
        # Announce to new room if teleport flag is set
        if result.get("teleport") and result.get("old_room") != player.room_id:
            await broadcast_to_room(player.room_id, {
                "type": "message",
                "text": f"{player.name} appears!",
                "style": "action"
            }, exclude=player.name)
    
    # Broadcast to all players (HELP command - BBC Micro PROCA(&7700,&77FE))
    if result.get("broadcast_all"):
        message_text = result.get("broadcast_all")
        await broadcast_to_all({
            "type": "message",
            "text": message_text,
            "style": "action",  # Goes to status area
            "beeps": result.get("beeps", 0)
        })
    
    # Broadcast chat messages (to room only)
    if result.get("broadcast"):
        # Check if this is a raw broadcast (like HELLO command)
        if result.get("broadcast_raw"):
            broadcast_text = f"{player.name} {result['broadcast']}"
        else:
            broadcast_text = f"{player.name} says: {result['broadcast']}"
        
        await broadcast_to_room(player.room_id, {
            "type": "message",
            "text": broadcast_text,
            "style": "action"  # Changed to action so it goes to status area
        }, exclude=player.name)
    
    # Handle TELL messages (line 4120: PROCC(1,?(T+8),E$+":"+M$))
    if result.get("tell_all"):
        # Broadcast to all players (Wizard only)
        message_text = result.get("tell_message")
        await broadcast_to_all({
            "type": "message",
            "text": message_text,
            "style": "combat"  # PROCC type 1 = status area
        })
    elif result.get("tell_target"):
        # Send to specific player
        target_name = result.get("tell_target")
        target_player = game_state.get_player(target_name)
        if target_player:
            message_text = result.get("tell_message")
            await send_to_player(target_player, {
                "type": "message",
                "text": message_text,
                "style": "combat"  # PROCC type 1 = status area (appears in status window)
            })
    
    # Handle ANNOY messages (line 3640: PROCC(1,?(T+8),E$+" is ANNOYing you!"))
    if result.get("annoy_player"):
        target_name = result.get("annoy_player")
        target_player = game_state.get_player(target_name)
        if target_player:
            message_text = result.get("annoy_message")
            await send_to_player(target_player, {
                "type": "message",
                "text": message_text,
                "style": "combat"  # PROCC type 1 = status area
            })
    
    # Handle LIGHTS broadcast (line 2970/2980: "The Lights come ON/OFF")
    if result.get("lights_broadcast"):
        # Broadcast to all players (not just room)
        await broadcast_to_all({
            "type": "message",
            "text": result.get("lights_broadcast"),
            "style": "action"  # Status area
        })
        
        # Refresh room display for all players (lighting changed)
        for p in game_state.players.values():
            await send_room_update(p)
    
    # Handle PULL rope (portcullis) - line 3730: raise portcullis temporarily
    if result.get("portcullis_raised"):
        # Broadcast to rooms 29 and 30
        await broadcast_to_room(29, {
            "type": "message",
            "text": "The portcullis goes UP",
            "style": "action"
        })
        await broadcast_to_room(30, {
            "type": "message",
            "text": "The portcullis goes UP",
            "style": "action"
        })
        # No need to refresh room display - the message is enough
    
    # Handle RELEASE rope (portcullis lowered) - line 3770
    if result.get("portcullis_lowered"):
        # Broadcast to rooms 29 and 30
        await broadcast_to_room(29, {
            "type": "message",
            "text": "The portcullis FALLS",
            "style": "action"
        })
        await broadcast_to_room(30, {
            "type": "message",
            "text": "The portcullis FALLS",
            "style": "action"
        })
        # No need to refresh room display - the message is enough
    
    # Handle COLLAPSE command (line 2620: Wizard triggers cave collapse for all players)
    if result.get("collapse"):
        wizard_name = result.get("wizard_name")
        print(f"💥 {wizard_name} triggered COLLAPSE - killing all other players!")
        
        # Get list of players to kill (everyone except the wizard who issued the command)
        players_to_kill = [p for p in list(game_state.players.values()) if p.name != wizard_name]
        
        # Disable input for all players who will die
        for p in players_to_kill:
            await send_to_player(p, {
                "type": "disable_input"
            })
        
        # Send collapse message once to all players (including wizard)
        await broadcast_to_all({
            "type": "message",
            "text": "Cave collapses",
            "style": "normal",  # Main screen, not status
            "beeps": 3  # Dramatic!
        })
        
        # Small pause before death sequence
        await asyncio.sleep(1.0)
        
        # Kill all players except the wizard (matching line 1620: PROCF:*GOING)
        for p in players_to_kill:
            p.deaths += 1
            
            # Make all creatures forget about this player
            game_state.reset_creatures_targeting_player(p.name)
            
            # Handle death sequence (save and GOING screen, but skip "Life is slipping away" message)
            # Cave collapse goes straight to PROCF:*GOING without the death message
            await handle_player_death(p, skip_death_message=True)
            
            # Remove player from game state
            game_state.remove_player(p)
            if p.name in active_connections:
                del active_connections[p.name]
        
        print(f"✅ COLLAPSE complete - {len(players_to_kill)} players killed, {wizard_name} survives")
        return
    
    # Handle SUMMON player (line 2170: PROCC(8,?(T+8),CHR$B) - event 8 = teleport)
    if result.get("summon_player"):
        target_name = result.get("summon_player")
        target_player = game_state.get_player(target_name)
        if target_player:
            summon_room = result.get("summon_to_room")
            old_room = target_player.room_id
            
            # Notify summoned player (line 1670: PROCY(?&7702):PRINTJ$;C$;)
            await send_to_player(target_player, {
                "type": "message",
                "text": f"You have been summoned by {player.name}!",
                "style": "combat"
            })
            
            # Announce to old room
            await broadcast_to_room(old_room, {
                "type": "message",
                "text": f"{target_player.name} vanishes!",
                "style": "action"
            }, exclude=target_player.name)
            
            # Update summoned player's room
            target_player.room_id = summon_room
            await send_room_update(target_player)
            
            # Announce to new room
            await broadcast_to_room(summon_room, {
                "type": "message",
                "text": f"{target_player.name} appears!",
                "style": "action"
            }, exclude=target_player.name)
    
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
                # Check if this is a BITE command with custom victim message
                if result.get("victim_message"):
                    # BITE command: custom message for victim
                    await send_to_player(target_player, {
                        "type": "message",
                        "text": result.get("victim_message"),
                        "style": "combat",
                        "beeps": 2  # Being bitten = 2 beeps
                    })
                else:
                    # BBC Micro line 1610: 
                    # Victim receives: PROCB(H$(RND(3))+" by "+attacker) - status bar
                    # Attacker receives: PROCC sends back "victim IS HIT! stamina down to X"
                    
                    import random
                    hit_messages = ["I am hit", "I am struck", "I am thumped"]
                    hit_message = random.choice(hit_messages)
                    
                    # Message for victim: Status bar message
                    await send_to_player(target_player, {
                        "type": "message",
                        "text": f"{hit_message} by {player.name}",
                        "style": "combat",
                        "beeps": 2  # Being hit = 2 beeps (VDU7,7)
                    })
                    
                    # Message for attacker: Stamina feedback (status bar)
                    # Line 1580: PROCB(?&7702) - received PROCC message displayed via PROCB
                    await send_to_player(player, {
                        "type": "message",
                        "text": f"{target_player.name} IS HIT! stamina down to {target_player.stamina}",
                        "style": "combat",
                        "beeps": 1  # Notification beep for attacker
                    })
                
                # Update target's stats
                await send_to_player(target_player, {
                    "type": "player_update",
                    "player": target_player.to_dict()
                })
                
                # If target died, handle death sequence
                if result.get("target_died"):
                    # Broadcast death to room
                    await broadcast_to_room(target_player.room_id, {
                        "type": "message",
                        "text": f"{target_player.name} has been slain by {player.name}!",
                        "style": "combat"
                    }, exclude=target_player.name)
                    
                    # Handle death sequence (save, show messages, GOING screen)
                    await handle_player_death(target_player)
                    
                    # Remove player from game state
                    game_state.remove_player(target_player)
                    if target_player.name in active_connections:
                        del active_connections[target_player.name]

async def send_room_update(player: Player):
    """
    Send complete room state to player
    Checks lighting state (BBC Micro line 1060):
    - If lights OFF AND player doesn't have Crystal Ball: show "It is too dark to see"
    - Otherwise: show normal room description
    """
    room = game_state.get_room(player.room_id)
    
    if not room:
        return
    
    # Send disk activity notification (loading room data from disk)
    await send_to_player(player, {
        "type": "disk_activity",
        "operation": "read"
    })
    
    # Simulate disk read delay (room data loading)
    import asyncio
    await asyncio.sleep(0.15)  # Short delay for room loading
    
    # Check lighting (BBC Micro line 1060)
    # Show room if: lights_on OR player has Crystal Ball
    has_crystal_ball = any("crystal" in item.lower() and "ball" in item.lower() for item in player.inventory)
    
    if not game_state.lights_on and not has_crystal_ball:
        # Too dark to see - send minimal room info
        await send_to_player(player, {
            "type": "room",
            "room": {
                "id": room["id"],
                "name": room.get("name", f"Room {room['id']}"),
                "description": "It is too dark to see",
                "exits": room["exits"],
                "has_graphic": False,  # No graphics in darkness
                "graphic_url": None
            },
            "players": [],  # Can't see other players in darkness
            "objects": [],  # Can't see objects in darkness
            "creatures": [],  # Can't see creatures in darkness
            "player": player.to_dict()
        })
        return
    
    # Normal room display (lights on or has Crystal Ball)
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
    
    # Add portcullis status for rooms 29 and 30 (BBC Micro line 1300)
    # Status appears AFTER the room description
    description = room["description"]
    if player.room_id in [29, 30]:
        portcullis_status = "UP" if game_state.portcullis_up else "DOWN"
        description = f"{description}\n\nThe Portcullis is {portcullis_status}"
    
    # Check fast mode (BBC Micro line 1080: IFjORn=B n=B:ENDPROC)
    # When fast mode is enabled (j=TRUE), skip graphics display
    has_graphic = room["id"] in game_state.rooms_with_graphics and not player.fast_mode
    graphic_url = f"/graphics/room_{room['id']}.png" if has_graphic else None
    
    await send_to_player(player, {
        "type": "room",
        "room": {
            "id": room["id"],
            "name": room.get("name", f"Room {room['id']}"),
            "description": description,
            "exits": room["exits"],
            "has_graphic": has_graphic,
            "graphic_url": graphic_url
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
app.mount("/graphics", StaticFiles(directory="../static/graphics"), name="graphics")
app.mount("/static", StaticFiles(directory="../static"), name="static")

@app.get("/")
async def root():
    """Serve the main game page"""
    return FileResponse("../static/index.html")

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
