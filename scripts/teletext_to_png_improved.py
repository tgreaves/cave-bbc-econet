#!/usr/bin/env python3
"""
Improved BBC Micro Teletext Mode 7 picture converter to PNG
Handles graphics characters more accurately and supports single file conversion
"""

import sys
import os
from PIL import Image, ImageDraw

# BBC Micro Teletext control codes
CONTROL_CODES = {
    # Text colors (0x81-0x87) - disable graphics mode
    0x81: 'RED',
    0x82: 'GREEN', 
    0x83: 'YELLOW',
    0x84: 'BLUE',
    0x85: 'MAGENTA',
    0x86: 'CYAN',
    0x87: 'WHITE',
    # Display effects
    0x88: 'FLASH',
    0x89: 'STEADY',
    0x8C: 'NORMAL_HEIGHT',
    0x8D: 'DOUBLE_HEIGHT',
    # Graphics colors (0x91-0x97) - enable graphics mode  
    0x91: 'RED_GRAPHICS',
    0x92: 'GREEN_GRAPHICS',
    0x93: 'YELLOW_GRAPHICS',
    0x94: 'BLUE_GRAPHICS',
    0x95: 'MAGENTA_GRAPHICS',
    0x96: 'CYAN_GRAPHICS',
    0x97: 'WHITE_GRAPHICS',
    # Background and graphics control
    0x9C: 'BLACK_BG',
    0x9D: 'NEW_BG',
    0x99: 'SEPARATED_GRAPHICS',
    0x9A: 'CONTIGUOUS_GRAPHICS',
}

# Teletext colors (RGB) - BBC Micro palette
COLORS = {
    'BLACK': (0, 0, 0),
    'RED': (255, 85, 85),
    'GREEN': (85, 255, 85),
    'YELLOW': (255, 255, 85),
    'BLUE': (85, 85, 255),
    'MAGENTA': (255, 85, 255),
    'CYAN': (85, 255, 255),
    'WHITE': (255, 255, 255),
}

def decode_graphics_char(byte):
    """
    Decode a teletext graphics character into a 2x3 block pattern
    Returns a list of 6 booleans representing which blocks are filled
    """
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

def render_teletext_to_png(filepath, output_path, scale=16):
    """
    Render a Teletext picture file to PNG with accurate block graphics
    
    Args:
        filepath: Path to the Teletext picture file
        output_path: Path to save the PNG
        scale: Pixel size for each character cell (default 16 for better quality)
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Teletext is 40 characters wide
    width = 40
    
    # Parse the data into lines (stop at first 0x0D or after 320 bytes = 8 lines)
    lines = []
    current_line = []
    
    for i, byte in enumerate(data):
        if byte == 0x0D:  # Carriage return - end of line
            if current_line:
                lines.append(current_line)
            current_line = []
        elif i > 0 and i % width == 0:
            lines.append(current_line)
            current_line = []
            current_line.append(byte)
        else:
            current_line.append(byte)
        
        # Stop after 8 lines (typical picture height)
        if len(lines) >= 8:
            break
    
    if current_line and len(lines) < 8:
        lines.append(current_line)
    
    # Pad lines to 40 characters
    for line in lines:
        while len(line) < width:
            line.append(0x20)  # Space
    
    # Create image
    img_width = width * scale
    img_height = len(lines) * scale
    
    img = Image.new('RGB', (img_width, img_height), COLORS['BLACK'])
    draw = ImageDraw.Draw(img)
    
    for line_num, line in enumerate(lines):
        # Reset state at start of each line
        fg_color = COLORS['WHITE']
        bg_color = COLORS['BLACK']
        graphics_mode = False
        contiguous = True
        flash = False
        
        for char_num, byte in enumerate(line):
            x = char_num * scale
            y = line_num * scale
            
            # Handle control codes
            if byte in CONTROL_CODES:
                code = CONTROL_CODES[byte]
                
                # Text color codes (disable graphics mode)
                if code in ['RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE']:
                    fg_color = COLORS[code]
                    graphics_mode = False
                # Graphics color codes (enable graphics mode)
                elif code in ['RED_GRAPHICS', 'GREEN_GRAPHICS', 'YELLOW_GRAPHICS', 'BLUE_GRAPHICS', 
                              'MAGENTA_GRAPHICS', 'CYAN_GRAPHICS', 'WHITE_GRAPHICS']:
                    color_name = code.replace('_GRAPHICS', '')
                    fg_color = COLORS[color_name]
                    graphics_mode = True
                elif code == 'NEW_BG':
                    bg_color = fg_color
                elif code == 'BLACK_BG':
                    bg_color = COLORS['BLACK']
                elif code == 'BLACK_FG':
                    fg_color = COLORS['BLACK']
                # Ignore FLASH and STEADY - just preserve colors
                elif code == 'FLASH':
                    pass  # Don't change colors for flash
                elif code == 'STEADY':
                    pass  # Don't change colors for steady
                elif code == 'CONTIGUOUS_GRAPHICS':
                    contiguous = True
                elif code == 'SEPARATED_GRAPHICS':
                    contiguous = False
                
                # Draw background for control code position
                draw.rectangle([x, y, x + scale - 1, y + scale - 1], fill=bg_color)
                
            # Handle graphics characters (0xA0-0xBF and 0xC0-0xFF in graphics mode)
            elif (0xA0 <= byte <= 0xBF) or (graphics_mode and byte >= 0xC0):
                # Draw background
                draw.rectangle([x, y, x + scale - 1, y + scale - 1], fill=bg_color)
                
                # Decode and draw blocks
                # For bytes >= 0xC0 in graphics mode, mask to 0xA0-0xBF range
                graphics_byte = byte if byte <= 0xBF else (byte & 0x3F) | 0xA0
                blocks = decode_graphics_char(graphics_byte)
                if blocks:
                    # Each character is divided into 2x3 blocks
                    block_width = scale // 2
                    block_height = scale // 3
                    
                    # Add separation for separated graphics mode
                    sep = 1 if not contiguous else 0
                    
                    # Draw each block (ignore flash state, preserve colors)
                    for i, filled in enumerate(blocks):
                        if filled:
                            col = i % 2
                            row = i // 2
                            bx = x + col * block_width + sep
                            by = y + row * block_height + sep
                            bw = block_width - (2 * sep if sep else 0)
                            bh = block_height - (2 * sep if sep else 0)
                            draw.rectangle(
                                [bx, by, bx + bw - 1, by + bh - 1],
                                fill=fg_color
                            )
            
            # Handle regular characters (space, text, etc.)
            else:
                # Draw background
                draw.rectangle([x, y, x + scale - 1, y + scale - 1], fill=bg_color)
                
                # Only render text if NOT in graphics mode
                if not graphics_mode:
                    # Handle BBC Micro lowercase encoding (0xC0-0xFF -> subtract 0x80)
                    if byte >= 0xC0:
                        char = chr(byte - 0x80)
                    elif 0x20 <= byte < 0x7F:
                        char = chr(byte)
                    else:
                        char = None
                    
                    # Draw text character if we have one
                    if char and char != ' ':
                        # Use PIL to draw text (simple monospace representation)
                        # Calculate font size to fit in cell
                        font_size = int(scale * 0.8)
                        try:
                            from PIL import ImageFont
                            # Try to use a monospace font
                            try:
                                font = ImageFont.truetype("cour.ttf", font_size)
                            except:
                                try:
                                    font = ImageFont.truetype("Courier New.ttf", font_size)
                                except:
                                    font = ImageFont.load_default()
                        except:
                            font = None
                        
                        if font:
                            # Center the character in the cell (ignore flash, preserve colors)
                            bbox = draw.textbbox((0, 0), char, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                            text_x = x + (scale - text_width) // 2
                            text_y = y + (scale - text_height) // 2 - bbox[1]
                            draw.text((text_x, text_y), char, fill=fg_color, font=font)
                        else:
                            # Fallback: draw a simple filled area
                            margin = scale // 6
                            draw.rectangle(
                                [x + margin, y + margin, x + scale - margin - 1, y + scale - margin - 1],
                                fill=fg_color
                            )
                else:
                    # In graphics mode, treat high bytes as graphics characters
                    # (some may be invalid graphics chars, just draw background)
                    pass
    
    # Save the image
    img.save(output_path)
    print(f"Saved: {output_path} ({img_width}x{img_height})")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 teletext_to_png_improved.py <input_file_or_dir> <output_file_or_dir> [scale]")
        print()
        print("Examples:")
        print("  Single file: python3 teletext_to_png_improved.py cave-plus/original/P/2 room_2.png 16")
        print("  Directory:   python3 teletext_to_png_improved.py cave-plus/original/P output/ 16")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    
    # Check if input is a file or directory
    if os.path.isfile(input_path):
        # Single file conversion
        render_teletext_to_png(input_path, output_path, scale)
    elif os.path.isdir(input_path):
        # Directory conversion
        os.makedirs(output_path, exist_ok=True)
        
        files = sorted([f for f in os.listdir(input_path) if not f.startswith('.')])
        print(f"Converting {len(files)} Teletext pictures to PNG...")
        print(f"Scale: {scale}x{scale} pixels per character")
        print()
        
        for filename in files:
            input_file = os.path.join(input_path, filename)
            output_file = os.path.join(output_path, f"room_{filename}.png")
            
            try:
                render_teletext_to_png(input_file, output_file, scale)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        print()
        print(f"Done! Converted {len(files)} pictures to {output_path}/")
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        sys.exit(1)

if __name__ == '__main__':
    main()
