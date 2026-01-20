#!/usr/bin/env python3
"""
Convert BBC Micro Teletext Mode 7 picture files to PNG images
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

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
    0x9C: 'BLACK_FG',
    0x9D: 'SEPARATED_GRAPHICS',
    0x9E: 'CONTIGUOUS_GRAPHICS',
}

# Teletext colors (RGB)
COLORS = {
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'YELLOW': (255, 255, 0),
    'BLUE': (0, 0, 255),
    'MAGENTA': (255, 0, 255),
    'CYAN': (0, 255, 255),
    'WHITE': (255, 255, 255),
}

def decode_graphics_char(byte):
    """Decode a teletext graphics character into a 2x3 block pattern"""
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
    blocks = [
        bool(pattern & 0x01),  # top-left
        bool(pattern & 0x02),  # top-right
        bool(pattern & 0x04),  # middle-left
        bool(pattern & 0x08),  # middle-right
        bool(pattern & 0x10),  # bottom-left
        bool(pattern & 0x20),  # bottom-right
    ]
    
    return blocks

def render_teletext_to_png(filepath, output_path, scale=8):
    """
    Render a Teletext picture file to PNG
    
    Args:
        filepath: Path to the Teletext picture file
        output_path: Path to save the PNG
        scale: Pixel size for each character cell (default 8)
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Teletext is 40 characters wide
    width = 40
    
    # Parse the data into lines
    lines = []
    current_line = []
    
    for i, byte in enumerate(data):
        if i > 0 and i % width == 0:
            lines.append(current_line)
            current_line = []
        
        current_line.append(byte)
    
    if current_line:
        lines.append(current_line)
    
    # Create image
    # Each character is scale x scale pixels
    # Each character has 2x3 blocks for graphics
    img_width = width * scale
    img_height = len(lines) * scale
    
    img = Image.new('RGB', (img_width, img_height), COLORS['BLACK'])
    draw = ImageDraw.Draw(img)
    
    # Current state
    fg_color = COLORS['WHITE']
    bg_color = COLORS['BLACK']
    graphics_mode = False
    
    for line_num, line in enumerate(lines):
        # Reset state at start of each line
        fg_color = COLORS['WHITE']
        bg_color = COLORS['BLACK']
        graphics_mode = False
        
        for char_num, byte in enumerate(line):
            x = char_num * scale
            y = line_num * scale
            
            # Handle control codes
            if byte in CONTROL_CODES:
                code = CONTROL_CODES[byte]
                
                if code in ['RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE']:
                    fg_color = COLORS[code]
                    graphics_mode = False
                elif code == 'BLACK_FG':
                    fg_color = COLORS['BLACK']
                elif code == 'NEW_BG':
                    bg_color = fg_color
                elif code == 'BLACK_BG':
                    bg_color = COLORS['BLACK']
                
                # Draw background
                draw.rectangle([x, y, x + scale - 1, y + scale - 1], fill=bg_color)
                
            # Handle graphics characters
            elif 0xA0 <= byte <= 0xBF:
                graphics_mode = True
                
                # Draw background
                draw.rectangle([x, y, x + scale - 1, y + scale - 1], fill=bg_color)
                
                # Decode and draw blocks
                blocks = decode_graphics_char(byte)
                if blocks:
                    block_width = scale // 2
                    block_height = scale // 3
                    
                    # Draw each block
                    for i, filled in enumerate(blocks):
                        if filled:
                            bx = x + (i % 2) * block_width
                            by = y + (i // 2) * block_height
                            draw.rectangle(
                                [bx, by, bx + block_width - 1, by + block_height - 1],
                                fill=fg_color
                            )
            
            # Handle text characters
            elif 0x20 <= byte < 0x7F or byte >= 0xC0:
                # Draw background
                draw.rectangle([x, y, x + scale - 1, y + scale - 1], fill=bg_color)
                
                # For text, we'll just draw a simple representation
                # (proper font rendering would require a Teletext font)
                if byte != 0x20 and byte != 0xA0:  # Not space
                    # Draw a simple filled rectangle to represent text
                    margin = scale // 4
                    draw.rectangle(
                        [x + margin, y + margin, x + scale - margin - 1, y + scale - margin - 1],
                        fill=fg_color
                    )
            
            else:
                # Unknown character - draw background
                draw.rectangle([x, y, x + scale - 1, y + scale - 1], fill=bg_color)
    
    # Save the image
    img.save(output_path)
    print(f"Saved: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 teletext_to_png.py <input_dir> <output_dir> [scale]")
        print("Example: python3 teletext_to_png.py cave-plus/original/P cave-plus/analysed/graphics 8")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all files in input directory
    files = sorted([f for f in os.listdir(input_dir) if not f.startswith('.')])
    
    print(f"Converting {len(files)} Teletext pictures to PNG...")
    print(f"Scale: {scale}x{scale} pixels per character")
    print()
    
    for filename in files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"room_{filename}.png")
        
        try:
            render_teletext_to_png(input_path, output_path, scale)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print()
    print(f"Done! Converted {len(files)} pictures to {output_dir}/")

if __name__ == '__main__':
    main()
