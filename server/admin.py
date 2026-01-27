"""
Admin functionality for CAVE-Plus
Handles admin authentication, WebSocket connections, and game management
"""

import asyncio
from typing import Dict
from fastapi import WebSocket


async def broadcast_game_state_to_admins(admin_connections: Dict[str, WebSocket], game_state, active_connections):
    """Broadcast current game state to all connected admins"""
    if not admin_connections:
        return
    
    # Collect game state data
    players_data = []
    for player in game_state.players.values():
        players_data.append({
            "name": player.name,
            "rank": player.rank,
            "room_id": player.room_id,
            "stamina": int(player.stamina),
            "max_stamina": player.max_stamina,
            "score": player.score,
            "inventory": player.inventory,
            "is_disconnected": player.is_disconnected
        })
    
    # Sort players alphabetically by name
    players_data.sort(key=lambda p: p["name"])
    
    # Collect object data - track all objects from rooms
    objects_data = []
    objects_seen = set()
    
    for room_id, obj_list in game_state.objects.items():
        for obj_name in obj_list:
            objects_data.append({
                "name": obj_name,
                "room_id": room_id,
                "held_by": None
            })
            objects_seen.add(obj_name)
    
    # Add objects held by players (even if not in rooms)
    for player in game_state.players.values():
        for obj_name in player.inventory:
            if obj_name not in objects_seen:
                # Object is held but not in any room - add it
                objects_data.append({
                    "name": obj_name,
                    "room_id": None,
                    "held_by": player.name
                })
                objects_seen.add(obj_name)
            else:
                # Object exists in room list - mark as held
                for obj_data in objects_data:
                    if obj_data["name"] == obj_name and obj_data["held_by"] is None:
                        obj_data["held_by"] = player.name
                        # Keep room_id to show where it was picked up from
                        break
    
    # Sort objects alphabetically by name
    objects_data.sort(key=lambda o: o["name"])
    
    # Collect creature data
    creatures_data = []
    for creature in game_state.creatures.values():
        creatures_data.append({
            "name": creature.name,
            "room_id": creature.room_id,
            "stamina": int(creature.stamina),
            "max_stamina": creature.max_stamina,
            "behavior": creature.behavior
        })
    
    # Sort creatures alphabetically by name
    creatures_data.sort(key=lambda c: c["name"])
    
    # Environment data
    environment_data = {
        "lights_on": game_state.lights_on,
        "portcullis_up": game_state.portcullis_up,
        "activity_level": game_state.activity_level,
        "staff_charges": game_state.staff_charges
    }
    
    message = {
        "type": "game_state",
        "players": players_data,
        "objects": objects_data,
        "creatures": creatures_data,
        "environment": environment_data
    }
    
    # Send to all admins
    for admin_name, ws in list(admin_connections.items()):
        try:
            await ws.send_json(message)
        except Exception as e:
            print(f"Error sending to admin {admin_name}: {e}")


async def handle_admin_command(command_data: dict, game_state, active_connections, broadcast_to_all):
    """Handle admin commands"""
    command = command_data.get("command")
    
    if command == "toggle_lights":
        game_state.lights_on = not game_state.lights_on
        message = "The lights go ON!" if game_state.lights_on else "The lights go OFF!"
        await broadcast_to_all({
            "type": "message",
            "text": message,
            "style": "action"
        })
        
    elif command == "toggle_portcullis":
        game_state.portcullis_up = not game_state.portcullis_up
        message = "The portcullis goes UP!" if game_state.portcullis_up else "The portcullis goes DOWN!"
        await broadcast_to_all({
            "type": "message",
            "text": message,
            "style": "action"
        })
        
    elif command == "set_activity":
        value = command_data.get("value", 2)
        game_state.activity_level = max(0, min(9, value))
        await broadcast_to_all({
            "type": "message",
            "text": f"Activity level set to {game_state.activity_level}",
            "style": "action"
        })
        
    elif command == "set_staff":
        value = command_data.get("value", 0)
        game_state.staff_charges = max(0, min(127, value))
        await broadcast_to_all({
            "type": "message",
            "text": f"Staff charges set to {game_state.staff_charges}",
            "style": "action"
        })
        
    elif command == "kick_player":
        player_name = command_data.get("player_name")
        player = game_state.get_player(player_name)
        if player:
            # Send disconnect message
            if player_name in active_connections:
                try:
                    await active_connections[player_name].send_json({
                        "type": "disconnect",
                        "message": "You have been kicked by an administrator."
                    })
                    await active_connections[player_name].close()
                except:
                    pass
            
            # Remove from game
            game_state.remove_player(player)
            if player_name in active_connections:
                del active_connections[player_name]
            
            # Announce to others
            await broadcast_to_all({
                "type": "message",
                "text": f"{player_name} has been kicked by an administrator.",
                "style": "action"
            })
