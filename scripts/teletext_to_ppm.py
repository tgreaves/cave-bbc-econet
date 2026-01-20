#!/usr/bin/env python3
"""
Convert BBC Micro Teletext Mode 7 picture files to PPM images (no dependencies)
PPM files can be converted to PNG using: convert file.ppm file.png
"""

import sys
import os

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

CONTROL_CODES = {
    0x81: 'RED', 0x82: 'GREEN', 0x83: 'YELLOW', 0x84: 'BLUE',
    0x85: 'MAGENTA', 0x86: 'CYAN', 0x87: 'WHITE',
    0x90: 'BLACK_BG', 0x91: 'NEW_BG', 0x9C: 'BLACK_FG',
}

def decode_graphics_char(byte):
    """Decode teletext graphics character into 2x3 block pattern"""
    if byte < 0xA0 or byte > 0xBF:
        return None
    pattern = byte - 0xA0
    return [
        bool(pattern & 0x01), bool(pattern & 0x02),  # top row
        bool(pattern & 0x04), bool(pattern & 0x08),  # middle row
        bool(pattern & 0x10), bool(pattern & 0x20),  # bottom row
    ]

def render_teletext_to_ppm(filepath, output_path, scale=8):
    """Render Teletext to PPM format (no external dependencies)"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    width = 40
    lines = []
    current_line = []
    
    for i, byte in enumerate(data):
        if i > 0 and i % width == 0:
            lines.append(current_line)
            current_line = []
        current_line.append(byte)
    
    if current_line:
        lines.append(current_line)
    
    # Create pixel array
    img_width = width * scale
    img_height = len(lines) * scale
    pixels = [[(0, 0, 0) for _ in range(img_width)] for _ in range(img_height)]
    
    for line_num, line in enumerate(lines):
        fg_color = COLORS['WHITE']
        bg_color = COLORS['BLACK']
        
        for char_num, byte in enumerate(line):
            x = char_num * scale
            y = line_num * scale
            
            # Handle control codes
            if byte in CONTROL_CODES:
                code = CONTROL_CODES[byte]
                if code in COLORS:
                    fg_color = COLORS[code]
                elif code == 'BLACK_FG':
                    fg_color = COLORS['BLACK']
                elif code == 'NEW_BG':
                    bg_color = fg_color
                elif code == 'BLACK_BG':
                    bg_color = COLORS['BLACK']
                
                # Fill background
                for dy in range(scale):
                    for dx in range(scale):
                        if y + dy < img_height and x + dx < img_width:
                            pixels[y + dy][x + dx] = bg_color
            
            # Handle graphics characters
            elif 0xA0 <= byte <= 0xBF:
                # Fill background
                for dy in range(scale):
                    for dx in range(scale):
                        if y + dy < img_height and x + dx < img_width:
                            pixels[y + dy][x + dx] = bg_color
                
                # Draw blocks
                blocks = decode_graphics_char(byte)
                if blocks:
                    block_width = scale // 2
                    block_height = scale // 3
                    
                    for i, filled in enumerate(blocks):
                        if filled:
                            bx = x + (i % 2) * block_width
                            by = y + (i // 2) * block_height
                            
                            for dy in range(block_height):
                                for dx in range(block_width):
                                    py = by + dy
                                    px = bx + dx
                                    if py < img_height and px < img_width:
                                        pixels[py][px] = fg_color
            
            # Handle text/other
            else:
                for dy in range(scale):
                    for dx in range(scale):
                        if y + dy < img_height and x + dx < img_width:
                            pixels[y + dy][x + dx] = bg_color
                
                # Simple text representation
                if byte not in (0x20, 0xA0):
                    margin = scale // 4
                    for dy in range(margin, scale - margin):
                        for dx in range(margin, scale - margin):
                            py = y + dy
                            px = x + dx
                            if py < img_height and px < img_width:
                                pixels[py][px] = fg_color
    
    # Write PPM file
    with open(output_path, 'w') as f:
        f.write(f'P3\n{img_width} {img_height}\n255\n')
        for row in pixels:
            for r, g, b in row:
                f.write(f'{r} {g} {b} ')
            f.write('\n')
    
    print(f"Saved: {output_path}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 teletext_to_ppm.py <input_dir> <output_dir> [scale]")
        print("Example: python3 teletext_to_ppm.py cave-plus/original/P cave-plus/analysed/graphics 8")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    
    os.makedirs(output_dir, exist_ok=True)
    
    files = sorted([f for f in os.listdir(input_dir) if not f.startswith('.')])
    
    print(f"Converting {len(files)} Teletext pictures to PPM...")
    print(f"Scale: {scale}x{scale} pixels per character")
    print()
    
    for filename in files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"room_{filename}.ppm")
        
        try:
            render_teletext_to_ppm(input_path, output_path, scale)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print()
    print(f"Done! Converted {len(files)} pictures to {output_dir}/")
    print()
    print("To convert PPM to PNG, use ImageMagick:")
    print(f"  cd {output_dir} && for f in *.ppm; do convert $f ${{f%.ppm}}.png; done")

if __name__ == '__main__':
    main()
