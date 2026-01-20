#!/usr/bin/env python3
"""
Parse Cave-Plus room files and generate YAML
"""

import os
import re
import json

def parse_room_file(filepath):
    """Parse a single room file"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # First part (before 0x40) contains exits and metadata
    # Description starts at 0x40 (64 bytes in)
    exits_data = data[:64]
    desc_data = data[64:] if len(data) > 64 else b''
    
    # Parse exits from first line
    try:
        exits_text = exits_data.decode('ascii', errors='ignore')
    except:
        exits_text = exits_data.decode('latin-1', errors='ignore')
    
    # First line before \r contains exits
    exits_line = exits_text.split('\r')[0] if '\r' in exits_text else exits_text.split('\n')[0]
    
    # Parse exits (format: D2S3E72 = Down to 2, South to 3, East to 72)
    exits = {}
    direction_map = {
        'N': 'north',
        'S': 'south', 
        'E': 'east',
        'W': 'west',
        'U': 'up',
        'D': 'down'
    }
    
    # Find all direction codes
    for direction, full_name in direction_map.items():
        # Look for pattern like D2 or D72 or D123
        pattern = direction + r'(\d+)'
        matches = re.findall(pattern, exits_line)
        if matches:
            exits[full_name] = int(matches[0])
    
    # Parse description from offset 0x40 onwards
    # Description ends at first carriage return (0x0D)
    try:
        # Find first carriage return in description data
        cr_pos = desc_data.find(b'\r')
        if cr_pos != -1:
            desc_data = desc_data[:cr_pos]
        
        description = desc_data.decode('ascii', errors='replace')
    except:
        description = desc_data.decode('latin-1', errors='replace')
    
    # Clean up description
    # Remove null bytes
    description = description.replace('\x00', '')
    # Remove any remaining carriage returns and newlines
    description = description.replace('\r', ' ')
    description = description.replace('\n', ' ')
    # Remove control characters except printable ones
    description = ''.join(c if (ord(c) >= 32 and ord(c) < 127) or ord(c) >= 128 else ' ' for c in description)
    # Remove multiple spaces
    description = re.sub(r'\s+', ' ', description)
    description = description.strip()
    
    return {
        'exits': exits,
        'description': description
    }

def main():
    rooms_dir = 'cave-plus/original/R'
    rooms = {}
    
    # Special room annotations
    special_rooms = {
        1: {'name': 'Main Entrance / Altar', 'note': 'Staff of Merlin can be charged here. Dragon boss starts here.'},
        12: {'name': 'Green Room', 'note': 'Light switch location'},
        16: {'name': "Wizard's Room", 'note': 'Central hub of wizard domain'},
        17: {'name': 'Limbo', 'note': 'No natural way out - teleport trap'},
        18: {'name': "Wizard's Dungeon", 'note': 'No exits - prison'},
        19: {'name': 'Mortuary', 'note': 'Where dead creatures go'},
        20: {'name': 'Armoury', 'note': 'Where exorcised objects are moved. Contains defensive items.'},
        26: {'name': 'Snake Pit', 'note': 'Multiple snakes spawn here'},
        29: {'name': 'Portcullis West', 'note': 'Portcullis entrance'},
        30: {'name': "Demon's Room / Portcullis East", 'note': 'Portcullis exit, leads to torture caves'},
        56: {'name': 'Bank / Crystal Tower Top', 'note': 'Deposit treasure here for points'},
        72: {'name': 'Hall of Knowledge', 'note': 'Tutorial area with instruction rooms'},
    }
    
    # Initial object/creature placement from OBJINIT
    initial_objects = {
        1: ['Dragon', 'Staff of Merlin', 'Amulet', 'Treasure', 'Guardian (item)', 'Guardian (creature)'],
        2: ['Vodka'],
        3: ['(unnamed creature 36)'],
        5: ['Poison', 'Dagger', 'Maggot'],
        8: ['Skeleton'],
        11: ['Medicine', '(unnamed creature 20)'],
        13: ['Dwarf', 'Necromancer'],
        14: ['(unnamed creature 40)'],
        15: ['Knife'],
        20: ['Ruby', 'Shield', 'Spider', 'Viper', 'Drunk', 'Guardian'],
        23: ['(unnamed creature 18)'],
        25: ['Flamethrower'],
        26: ['Cobra', 'Python', 'Adder', 'Worm'],
        30: ['Arrow'],
        32: ['Stick', '(unnamed creature 31)'],
        37: ['Crystal Ball', 'Centipede'],
        38: ['Troll'],
        39: ['Author (easter egg)'],
        46: ['Killer'],
        55: ['Goblin (65535 HP bug)'],
        63: ['Toad', '(unnamed creature 33)'],
        67: ['Coward'],
        83: ['Caveman'],
    }
    
    # Get all room files
    room_files = []
    for filename in os.listdir(rooms_dir):
        if filename.isdigit():
            room_files.append(int(filename))
    
    room_files.sort()
    
    print(f"Found {len(room_files)} room files")
    
    for room_num in room_files:
        filepath = os.path.join(rooms_dir, str(room_num))
        try:
            room_data = parse_room_file(filepath)
            if room_data['description'] or room_data['exits']:
                # Add special room info
                if room_num in special_rooms:
                    room_data['special'] = special_rooms[room_num]
                
                # Add initial objects/creatures
                if room_num in initial_objects:
                    room_data['initial_objects'] = initial_objects[room_num]
                
                rooms[room_num] = room_data
                print(f"Parsed room {room_num}: {len(room_data['description'])} chars, {len(room_data['exits'])} exits")
        except Exception as e:
            print(f"Error parsing room {room_num}: {e}")
    
    # Generate YAML manually
    with open('cave-plus/rooms-parsed.yml', 'w') as f:
        f.write("# ============================================================================\n")
        f.write("# CAVE-PLUS ROOM DATA\n")
        f.write("# ============================================================================\n")
        f.write("# Parsed from original BBC Micro room files in cave-plus/original/R/\n")
        f.write("# \n")
        f.write("# This file contains complete room data for the Cave-Plus multiplayer game:\n")
        f.write("# - Room descriptions\n")
        f.write("# - Exit connections (north, south, east, west, up, down)\n")
        f.write("# - Special room annotations (Altar, Bank, Armoury, etc.)\n")
        f.write("# - Initial object and creature placement from OBJINIT file\n")
        f.write("# \n")
        f.write("# GAME STATISTICS:\n")
        f.write("#   Total Rooms:     157\n")
        f.write("#   Items:           15 (Vodka, Stick, Poison, Dagger, Arrow, Medicine, etc.)\n")
        f.write("#   Creatures:       27 (Dragon, Troll, Spider, Snakes, Author, etc.)\n")
        f.write("#   Special Rooms:   12 (Altar, Bank, Armoury, Mortuary, etc.)\n")
        f.write("# \n")
        f.write("# KEY LOCATIONS:\n")
        f.write("#   Room 1:  Main Entrance / Altar - Dragon boss, Staff of Merlin\n")
        f.write("#   Room 12: Green Room - Light switch\n")
        f.write("#   Room 19: Mortuary - Where dead creatures go\n")
        f.write("#   Room 20: Armoury - Defensive items (Ruby, Shield)\n")
        f.write("#   Room 26: Snake Pit - Multiple snakes\n")
        f.write("#   Room 30: Demon's Room - Portcullis, leads to torture caves\n")
        f.write("#   Room 56: Bank - Deposit treasure for points\n")
        f.write("#   Room 72: Hall of Knowledge - Tutorial area\n")
        f.write("# \n")
        f.write("# ============================================================================\n\n")
        
        f.write("metadata:\n")
        f.write("  total_rooms: {}\n".format(len(rooms)))
        f.write("  game: 'Cave-Plus'\n")
        f.write("  version: '1.00'\n")
        f.write("  notes: 'Parsed from original BBC Micro room files'\n")
        f.write("  parser_version: '2.0'\n")
        f.write("  includes_initial_objects: true\n")
        f.write("  includes_special_annotations: true\n\n")
        
        f.write("rooms:\n")
        for room_num in sorted(rooms.keys()):
            room_data = rooms[room_num]
            f.write(f"  {room_num}:\n")
            
            # Add special room name if present
            if 'special' in room_data:
                f.write(f"    name: '{room_data['special']['name']}'\n")
                f.write(f"    note: '{room_data['special']['note']}'\n")
            
            f.write(f"    description: |\n")
            # Wrap description
            desc = room_data['description']
            if desc:
                # Split into lines of ~70 chars
                words = desc.split()
                line = "      "
                for word in words:
                    if len(line) + len(word) + 1 > 76:
                        f.write(line + "\n")
                        line = "      " + word
                    else:
                        if line == "      ":
                            line += word
                        else:
                            line += " " + word
                if line.strip():
                    f.write(line + "\n")
            else:
                f.write("      (No description)\n")
            
            if room_data['exits']:
                f.write(f"    exits:\n")
                for direction in ['north', 'south', 'east', 'west', 'up', 'down']:
                    if direction in room_data['exits']:
                        f.write(f"      {direction}: {room_data['exits'][direction]}\n")
            else:
                f.write(f"    exits: {{}}\n")
            
            # Add initial objects/creatures if present
            if 'initial_objects' in room_data:
                f.write(f"    initial_objects:\n")
                for obj in room_data['initial_objects']:
                    f.write(f"      - '{obj}'\n")
            
            f.write("\n")
    
    print(f"\nGenerated rooms-parsed.yml with {len(rooms)} rooms")

if __name__ == '__main__':
    main()
