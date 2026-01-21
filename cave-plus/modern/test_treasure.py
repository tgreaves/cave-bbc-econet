#!/usr/bin/env python3
"""
Test script for treasure system
Verifies that:
1. Objects 11-15 spawn randomly (not in wizard's domain 16-20)
2. DEPOSIT command works correctly
3. Treasure respawns after deposit
"""

import asyncio
import sys
sys.path.insert(0, 'server')

from game_state import GameState
from player import Player
from commands import CommandParser

async def test_treasure_system():
    print("🧪 Testing Treasure System\n")
    
    # Initialize game state
    game_state = GameState()
    await game_state.initialize()
    
    # Test 1: Check random object placement
    print("Test 1: Random Object Placement")
    print("-" * 50)
    
    random_objects = ["Crystal Ball", "Staff of Merlin", "Amulet", "Treasure", "Guardian"]
    found_objects = {}
    
    for room_id, objects in game_state.objects.items():
        for obj in objects:
            if obj in random_objects:
                found_objects[obj] = room_id
                # Check if in wizard's domain (should NOT be)
                if 16 <= room_id <= 20:
                    print(f"❌ FAIL: {obj} found in wizard's domain (room {room_id})")
                else:
                    print(f"✅ {obj} spawned in room {room_id}")
    
    # Verify all 5 objects were placed
    if len(found_objects) == 5:
        print(f"✅ All 5 random objects placed correctly\n")
    else:
        print(f"❌ FAIL: Only {len(found_objects)}/5 objects placed\n")
    
    # Test 2: DEPOSIT command
    print("Test 2: DEPOSIT Command")
    print("-" * 50)
    
    # Create test player
    player = Player(
        name="TESTPLAYER",
        websocket=None
    )
    player.room_id = 56  # Start at bank
    player.rank = "Wizard"  # Make wizard for testing
    player.score = 100
    
    # Add treasure to inventory
    treasure_room = found_objects.get("Treasure")
    if treasure_room:
        print(f"Treasure initially in room {treasure_room}")
        player.inventory.append("Treasure")
        game_state.objects[treasure_room].remove("Treasure")
    
    # Create command parser
    parser = CommandParser(game_state)
    
    # Test deposit at wrong location
    player.room_id = 1
    result = await parser.deposit(player, "treasure")
    if result["message"] == "Not here I'm afraid.":
        print("✅ DEPOSIT rejected outside bank")
    else:
        print(f"❌ FAIL: Wrong message at wrong location: {result['message']}")
    
    # Test deposit at bank
    player.room_id = 56
    old_score = player.score
    result = await parser.deposit(player, "treasure")
    
    if "inventory_changed" in result:
        points_gained = player.score - old_score
        print(f"✅ DEPOSIT successful, gained {points_gained} points")
        print(f"   Message: {result['message']}")
        
        # Check if treasure respawned
        new_treasure_room = None
        for room_id, objects in game_state.objects.items():
            if "Treasure" in objects:
                new_treasure_room = room_id
                break
        
        if new_treasure_room:
            if 16 <= new_treasure_room <= 20:
                print(f"❌ FAIL: Treasure respawned in wizard's domain (room {new_treasure_room})")
            else:
                print(f"✅ Treasure respawned in room {new_treasure_room}")
        else:
            print("❌ FAIL: Treasure did not respawn")
    else:
        print(f"❌ FAIL: DEPOSIT failed: {result['message']}")
    
    # Test 3: REGEN resets random placement
    print("\nTest 3: REGEN Random Placement")
    print("-" * 50)
    
    await parser.regen(player)
    
    # Check if objects are in different locations
    new_found_objects = {}
    for room_id, objects in game_state.objects.items():
        for obj in objects:
            if obj in random_objects:
                new_found_objects[obj] = room_id
    
    if len(new_found_objects) == 5:
        print("✅ All 5 objects respawned after REGEN")
        
        # Check if any moved
        moved = False
        for obj, room in new_found_objects.items():
            if obj in found_objects and found_objects[obj] != room:
                print(f"   {obj} moved from room {found_objects[obj]} to room {room}")
                moved = True
        
        if moved:
            print("✅ Objects randomized on REGEN")
        else:
            print("⚠️  Objects in same locations (random chance)")
    else:
        print(f"❌ FAIL: Only {len(new_found_objects)}/5 objects after REGEN")
    
    print("\n" + "=" * 50)
    print("🎉 Treasure System Tests Complete!")

if __name__ == "__main__":
    asyncio.run(test_treasure_system())
