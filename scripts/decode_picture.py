#!/usr/bin/env python3
"""
Decode BBC Micro Teletext Mode 7 picture files
These are the P.* files used for room graphics in Cave-Plus
"""

import sys

# BBC Micro Teletext control codes
CONTROL_CODES = {
    0x81: 'RED',
    0x82: 'GREEN', 
    0x83: 'YELLOW',
    0x84: 'BLUE',
    0x85: 'MAGENTA',
    0x86: 'CYAN',
    0x87: 'WHITE',
    0x88: 'FLASH',
    0x89: 'STEADY',
    0x8C: 'NORMAL_HEIGHT',
    0x8D: 'DOUBLE_HEIGHT',
    0x90: 'BLACK_BG',
    0x91: 'NEW_BG',
    0x92: 'GREEN_GRAPHICS',
    0x93: 'YELLOW_GRAPHICS',
    0x94: 'BLUE_GRAPHICS',
    0x95: 'MAGENTA_GRAPHICS',
    0x96: 'CYAN_GRAPHICS',
    0x97: 'WHITE_GRAPHICS',
    0x9C: 'BLACK_FG',
    0x9D: 'SEPARATED_GRAPHICS',
    0x9E: 'CONTIGUOUS_GRAPHICS',
}

# Teletext graphics characters (0xA0-0xBF are block graphics)
# These create 2x3 block patterns
def decode_graphics_char(byte):
    """Decode a teletext graphics character into a visual representation"""
    if byte < 0xA0 or byte > 0xBF:
        return None
    
    # Each bit represents a block in a 2x3 grid:
    # Bit 0 (LSB) = top-left
    # Bit 1 = top-right  
    # Bit 2 = middle-left
    # Bit 3 = middle-right
    # Bit 4 = bottom-left
    # Bit 5 = bottom-right
    
    pattern = byte - 0xA0
    
    # Create a simple block representation
    # Use different characters based on which blocks are filled
    if pattern == 0x00:  # Empty
        return ' '
    elif pattern == 0x3F:  # All filled
        return '█'
    elif pattern & 0x03 == 0x03 and pattern & 0x0C == 0x0C and pattern & 0x30 == 0x30:
        return '█'  # Fully filled
    elif pattern & 0x15 == 0x15:  # Left column
        return '▌'
    elif pattern & 0x2A == 0x2A:  # Right column
        return '▐'
    elif pattern & 0x0F == 0x0F:  # Top half
        return '▀'
    elif pattern & 0x30 == 0x30:  # Bottom half
        return '▄'
    else:
        # Use a generic block character
        return '▓'

def decode_picture(filepath):
    """Decode a BBC Micro picture file"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Teletext is 40 characters wide
    width = 40
    lines = []
    current_line = []
    
    for i, byte in enumerate(data):
        if i > 0 and i % width == 0:
            lines.append(current_line)
            current_line = []
        
        if byte in CONTROL_CODES:
            current_line.append(f'[{CONTROL_CODES[byte]}]')
        elif byte == 0x0D:  # Carriage return
            lines.append(current_line)
            current_line = []
        elif byte == 0xA0:  # Space
            current_line.append(' ')
        elif 0xA0 <= byte <= 0xBF:  # Graphics character
            char = decode_graphics_char(byte)
            if char:
                current_line.append(char)
        elif byte >= 0xC0:  # Lowercase letters (BBC Micro encoding)
            current_line.append(chr(byte - 0x80))
        elif 0x20 <= byte < 0x7F:  # Normal ASCII
            current_line.append(chr(byte))
        else:
            current_line.append(f'[{byte:02X}]')
    
    if current_line:
        lines.append(current_line)
    
    return lines

def print_picture(lines):
    """Print the decoded picture"""
    for line in lines:
        print(''.join(str(c) for c in line))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 decode_picture.py <picture_file>")
        print("Example: python3 decode_picture.py cave-plus/original/P/2")
        sys.exit(1)
    
    filepath = sys.argv[1]
    lines = decode_picture(filepath)
    print_picture(lines)
    
    print(f"\n--- Picture dimensions: {len(lines)} lines ---")

if __name__ == '__main__':
    main()
