#!/usr/bin/env python3
"""
Decode OBJINIT file from Cave-Plus
Shows initial placement of objects and creatures
"""

import struct
import sys

# Object names from data file
objects = [
    "Vodka", "Stick", "Poison", "Dagger", "Arrow", "Medicine", "Knife",
    "Flamethrower", "Ruby", "Shield", "Crystal", "Staff", "Amulet", "Treasure",
    "Guardian",  # Object 15 (index 14)
    "Dragon", "Troll", "(unnamed)", "Maggot", "(unnamed)", "Author", "Spider",
    "Coward", "Killer", "Viper", "Cobra", "Python", "Adder", "Worm", "Drunk",
    "(unnamed)", "Toad", "(unnamed)", "Guardian", "Goblin", "(unnamed)", "Dwarf",
    "Necromancer", "Centipede", "(unnamed)", "Skeleton", "Caveman"
]

def decode_objinit(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print("=" * 80)
    print("OBJINIT FILE DECODER - Initial Object/Creature Placement")
    print("=" * 80)
    print()
    
    # Read 4-byte little-endian integers
    values = []
    for i in range(0, len(data), 4):
        if i + 4 <= len(data):
            val = struct.unpack('<I', data[i:i+4])[0]
            values.append(val)
    
    print(f"Total entries: {len(values)}")
    print(f"Expected: 42 objects + creatures")
    print()
    
    # Decode each entry
    # Format appears to be: room number in low byte, other data in high bytes
    for idx, val in enumerate(values[:42]):  # First 42 are objects
        if idx < len(objects):
            name = objects[idx]
        else:
            name = f"Object {idx+1}"
        
        # Extract room number (low byte)
        room = val & 0xFF
        
        # Extract high bytes (might be health/stamina for creatures)
        high_bytes = (val >> 8) & 0xFFFF
        
        # Special handling
        if val == 0:
            location = "Not placed / Carried by player"
        elif room == 0:
            location = "Not placed"
        elif room == 19:
            location = "Mortuary (dead/inactive)"
        else:
            location = f"Room {room}"
            if high_bytes > 0:
                location += f" (stamina: {high_bytes})"
        
        print(f"{idx+1:2d}. {name:20s} = 0x{val:08X} -> {location}")
    
    print()
    print("=" * 80)
    print("NOTES:")
    print("- Room 19 = Mortuary (where dead creatures go)")
    print("- Room 20 = Armoury")
    print("- Room 56 = Bank (for treasure deposit)")
    print("- High bytes for creatures = initial stamina/health")
    print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        decode_objinit(sys.argv[1])
    else:
        decode_objinit("cave-plus/original/OBJINIT")
