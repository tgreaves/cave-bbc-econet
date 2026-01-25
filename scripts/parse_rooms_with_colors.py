#!/usr/bin/env python3
"""
Parse BBC Micro room files and preserve Teletext color codes
Converts color codes to HTML-style markup for web display
"""

import os
import re
import yaml

# BBC Micro Teletext color codes
COLOR_CODES = {
    0x81: 'red',
    0x82: 'green',
    0x83: 'yellow',
    0x84: 'blue',
    0x85: 'magenta',
    0x86: 'cyan',
    0x87: 'white',
}

def parse_exits(exits_data):
    """Parse exits from first 64 bytes"""
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
    
    return exits

def parse_room_file(filepath):
    """Parse a BBC Micro room file and convert color codes to markup"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # First part (before 0x40) contains exits and metadata
    # Description starts at 0x40 (64 bytes in)
    exits_data = data[:64]
    desc_data = data[64:] if len(data) > 64 else b''
    
    # Parse exits
    exits = parse_exits(exits_data)
    
    # Find first carriage return in description data to avoid reading next room
    cr_pos = desc_data.find(b'\r')
    if cr_pos != -1:
        desc_data = desc_data[:cr_pos]
    
    # Convert to string with color markup
    result = []
    current_color = 'white'  # Default color
    
    for byte in desc_data:
        if byte in COLOR_CODES:
            # Color code - add markup
            new_color = COLOR_CODES[byte]
            if new_color != current_color:
                result.append(f'<color:{new_color}>')
                current_color = new_color
        elif byte == 0x00:  # Null terminator
            break
        elif 0x20 <= byte <= 0x7E:  # Printable ASCII
            result.append(chr(byte))
        # Skip other control codes (but not carriage returns - already handled above)
    
    description = ''.join(result).strip()
    
    return {
        'exits': exits,
        'description': description,
        'has_colors': '<color:' in description
    }

def parse_all_rooms(room_dir, output_file):
    """Parse all room files and create YAML with color markup"""
    rooms = {}
    
    # Get all room files (numbered 1-157)
    for i in range(1, 158):
        room_file = os.path.join(room_dir, str(i))
        if os.path.exists(room_file):
            try:
                room_data = parse_room_file(room_file)
                if room_data['description'] or room_data['exits']:
                    rooms[i] = room_data
                    if room_data['has_colors']:
                        print(f"Room {i}: Found color codes")
            except Exception as e:
                print(f"Error parsing room {i}: {e}")
    
    # Write to YAML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# ============================================================================\n")
        f.write("# CAVE-PLUS ROOM DATA WITH TELETEXT COLORS\n")
        f.write("# ============================================================================\n")
        f.write("# Parsed from original BBC Micro room files with color codes preserved\n")
        f.write("# Color markup format: <color:red>text<color:white>\n")
        f.write("# \n")
        f.write("# BBC Micro Teletext colors:\n")
        f.write("#   0x81 = Red\n")
        f.write("#   0x82 = Green\n")
        f.write("#   0x83 = Yellow\n")
        f.write("#   0x84 = Blue\n")
        f.write("#   0x85 = Magenta\n")
        f.write("#   0x86 = Cyan\n")
        f.write("#   0x87 = White\n")
        f.write("# ============================================================================\n\n")
        
        f.write("rooms:\n")
        for room_num in sorted(rooms.keys()):
            room_data = rooms[room_num]
            f.write(f"  {room_num}:\n")
            
            f.write(f"    description: |\n")
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
            
            f.write(f"    has_colors: {str(room_data['has_colors']).lower()}\n")
            f.write("\n")
    
    print(f"\nParsed {len(rooms)} rooms")
    colored_rooms = sum(1 for r in rooms.values() if r.get('has_colors'))
    print(f"Found {colored_rooms} rooms with color codes")

if __name__ == '__main__':
    room_dir = '../cave-plus/original/R'
    output_file = '../cave-plus/modern/rooms-with-colors.yml'
    
    parse_all_rooms(room_dir, output_file)
    print(f"\nOutput written to: {output_file}")
