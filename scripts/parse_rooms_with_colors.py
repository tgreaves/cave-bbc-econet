#!/usr/bin/env python3
"""
Parse BBC Micro room files and preserve Teletext color codes
Converts color codes to HTML-style markup for web display
"""

import os
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

def parse_room_file(filepath):
    """Parse a BBC Micro room file and convert color codes to markup"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find the room description (starts after the exits data)
    # Format: exits data, then 0x0D (carriage return), then description
    
    # Skip the first part (exits) - look for the description text
    # Room descriptions typically start after "You are in"
    desc_start = data.find(b'You are in')
    if desc_start == -1:
        # Try other common starts
        desc_start = data.find(b'This is')
        if desc_start == -1:
            desc_start = data.find(b'There')
            if desc_start == -1:
                # Just take everything after first 0x0D 0x0D
                double_cr = data.find(b'\r\r')
                if double_cr != -1:
                    desc_start = double_cr + 2
                else:
                    desc_start = 0
    
    # Extract description part
    desc_data = data[desc_start:]
    
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
        elif byte == 0x0D:  # Carriage return
            result.append('\n')
        elif byte == 0x00:  # Null terminator
            break
        elif 0x20 <= byte <= 0x7E:  # Printable ASCII
            result.append(chr(byte))
        # Skip other control codes
    
    return ''.join(result).strip()

def parse_all_rooms(room_dir, output_file):
    """Parse all room files and create YAML with color markup"""
    rooms = {}
    
    # Get all room files (numbered 1-157)
    for i in range(1, 158):
        room_file = os.path.join(room_dir, str(i))
        if os.path.exists(room_file):
            try:
                description = parse_room_file(room_file)
                if description:
                    rooms[i] = {
                        'description': description,
                        'has_colors': '<color:' in description
                    }
                    if rooms[i]['has_colors']:
                        print(f"Room {i}: Found color codes")
            except Exception as e:
                print(f"Error parsing room {i}: {e}")
    
    # Write to YAML
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump({'rooms': rooms}, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\nParsed {len(rooms)} rooms")
    colored_rooms = sum(1 for r in rooms.values() if r.get('has_colors'))
    print(f"Found {colored_rooms} rooms with color codes")

if __name__ == '__main__':
    room_dir = '../cave-plus/original/R'
    output_file = '../cave-plus/modern/rooms-with-colors.yml'
    
    parse_all_rooms(room_dir, output_file)
    print(f"\nOutput written to: {output_file}")
