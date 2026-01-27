# Cave-Plus Graphics Format

## Overview

Cave-Plus uses **BBC Micro Teletext Mode 7** graphics for room pictures. These are stored in the `P/` directory with filenames corresponding to room numbers (e.g., `P/2` for room 2).

## File Format

### Teletext Mode 7 Specifications

- **Resolution**: 40 characters × 25 lines
- **Character Set**: BBC Micro Teletext (similar to Viewdata/Prestel)
- **Colors**: 8 colors (Red, Green, Yellow, Blue, Magenta, Cyan, White, Black)
- **Graphics**: Block graphics using characters 0xA0-0xBF

### File Structure

Each picture file is a raw binary file containing:
- Teletext control codes (colors, graphics mode, etc.)
- Text characters (ASCII 0x20-0x7F)
- Graphics characters (0xA0-0xBF for 2×3 block patterns)
- BBC Micro lowercase letters (0xC0+ encoded as ASCII - 0x80)

Typical file size: 256-320 bytes (8 lines × 40 characters)

## Teletext Control Codes

### Color Codes
```
0x81 = Red text
0x82 = Green text
0x83 = Yellow text
0x84 = Blue text
0x85 = Magenta text
0x86 = Cyan text
0x87 = White text
```

### Graphics Mode
```
0x9C = Black foreground
0x9D = Separated graphics mode
0x9E = Contiguous graphics mode
```

### Display Effects
```
0x88 = Flash on
0x89 = Steady (flash off)
0x8C = Normal height
0x8D = Double height
0x90 = Black background
0x91 = New background (use current foreground as background)
```

## Graphics Characters (0xA0-0xBF)

Each graphics character represents a 2×3 grid of blocks:

```
Bit layout:
  0 1    (top row)
  2 3    (middle row)
  4 5    (bottom row)
```

### Examples

```
0xA0 = 000000 = Empty (space)
0xA1 = 000001 = ▘ (top-left only)
0xA2 = 000010 = ▝ (top-right only)
0xA3 = 000011 = ▀ (top row)
0xAF = 001111 = Top half filled
0xB0 = 010000 = Bottom-left only
0xBF = 111111 = █ (fully filled)
```

### Common Patterns

- **Vertical bars**: 0xA5 (▌ left), 0xAA (▐ right)
- **Horizontal bars**: 0xAF (▀ top), 0xF0 (▄ bottom)
- **Solid block**: 0xBF (█)
- **Checkerboard**: Various combinations

## Picture Files in Cave-Plus

### Available Pictures

Not all 157 rooms have pictures. Only 25 rooms have graphics:

```
P/2   - Main entrance area
P/3   - Tunnel
P/9   - Colored rooms area
P/11  - Red room (hot/fire theme)
P/12  - Green room
P/13  - Blue room
P/16  - Wizard's room (magical effects)
P/17  - Limbo
P/18  - Wizard's dungeon
P/19  - Mortuary
P/20  - Armoury
P/25  - Doctor's surgery
P/29  - Portcullis west
P/30  - Demon's room (fire/bricks)
P/32  - Bar
P/37  - Merlin's room (magical symbols)
P/49  - Cyan room
P/50  - Yellow room
P/51  - Magenta room
P/55  - Crystal tower
P/60  - Underground passages
P/99  - Server info screen
P/141 - Special room
P/148 - Special room
P/150 - Special room
```

### Picture Themes

**Colored Rooms** (11, 12, 13, 49, 50, 51)
- Simple colored backgrounds
- Room name displayed
- Minimal graphics

**Special Locations** (16, 30, 37)
- Complex graphics
- Magical effects (flashing)
- Detailed ASCII art

**Structural** (2, 3, 29, 30)
- Walls, doors, passages
- Brick patterns
- Architectural elements

## How Pictures Are Loaded

From the Cave-Plus code:

```basic
1170 Y=OPENIN("P."+STR$(B)):IFY=0ENDPROC
1190 CLOSE#Y:OSCLI("LO.P."+STR$(B)+CHR$13):ENDPROC
```

Process:
1. Check if picture file exists for current room
2. If exists, load it using OS command
3. Picture is displayed directly to screen memory
4. Text description appears below the picture

## Rendering for Modern Systems

### Terminal/Console

Use Unicode block characters:
```
█ ▀ ▄ ▌ ▐ ▓ ░ ▘ ▝ ▖ ▗
```

With ANSI color codes:
```
\033[31m = Red
\033[32m = Green
\033[33m = Yellow
\033[34m = Blue
\033[35m = Magenta
\033[36m = Cyan
\033[37m = White
```

### Web/Canvas

Convert to:
1. **HTML Canvas**: Draw 2×3 pixel blocks per character
2. **SVG**: Create rect elements for each block
3. **CSS**: Use colored div elements with borders

### Example Conversion

Original Teletext:
```
0x91 0xA0 0xA0 0x86 0xD3 0xF4 0xE1 0xF2 0xF4
[NEW_BG] [SPACE] [SPACE] [CYAN] S t a r t
```

Rendered:
```
[Background color change]   [Cyan text] Start
```

## Decoding Tool

Use `scripts/decode_picture.py`:

```bash
python3 scripts/decode_picture.py cave-plus/original/P/2
```

Output shows:
- Control codes in brackets: `[CYAN]`, `[RED]`, `[FLASH]`
- Graphics as Unicode blocks: `█`, `▀`, `▌`
- Text characters as-is

## Creating New Pictures

To create custom pictures for a modern implementation:

### 1. Design in 40×8 Grid
```
40 characters wide
8 lines tall (typical)
```

### 2. Use Color Codes
```
Start each line with color: [CYAN], [RED], etc.
Change colors mid-line as needed
```

### 3. Use Block Graphics
```
█ = Solid block
▀ = Top half
▄ = Bottom half
▌ = Left half
▐ = Right half
▓ = Medium shade
```

### 4. Add Effects
```
[FLASH] = Flashing text
[DOUBLE_HEIGHT] = Large text
```

## Example Picture Breakdown

**P/37 (Merlin's Room)**:
```
Line 1: Border with 'p' characters
Line 2: Left wall, magical symbols (flashing), right wall
Line 3: Left wall, crystal ball graphics, right wall
Line 4: Left wall, wavy pattern (~), right wall
Line 5: Left wall, "E M" text, right wall
Line 6: Left wall, block pattern, right wall
Line 7: Bottom border
```

Graphics elements:
- Walls: `▌` and `▐` characters
- Borders: `p`, `u`, `z` characters (custom font)
- Magic effects: Flashing blocks
- Text labels: "B S", "E M" (possibly "Ball" and "Merlin")

## Technical Notes

### BBC Micro Specifics

- **Screen Mode**: Mode 7 (Teletext)
- **Memory**: Pictures loaded directly to screen RAM
- **Display**: 40×25 characters, 8 colors
- **Refresh**: 50Hz (PAL) or 60Hz (NTSC)

### Character Encoding

BBC Micro uses a modified ASCII:
- 0x20-0x7F: Standard ASCII
- 0x80-0x9F: Control codes
- 0xA0-0xBF: Graphics characters
- 0xC0-0xFF: Lowercase letters (subtract 0x80 for ASCII)

### File Loading

The `OSCLI("LO.P."+STR$(B))` command:
- Loads file from disk
- Displays directly to screen
- No decompression needed
- Raw Teletext data

## Modern Implementation

For a web-based version:

### Option 1: Pre-render to Images
```python
# Convert all P/* files to PNG images
for picture in pictures:
    render_teletext_to_png(picture)
```

### Option 2: Real-time Canvas Rendering
```javascript
// Render Teletext in browser
function renderTeletext(data) {
    const canvas = document.getElementById('picture');
    const ctx = canvas.getContext('2d');
    
    // Parse control codes
    // Draw blocks and text
    // Apply colors
}
```

### Option 3: CSS/HTML
```html
<div class="teletext-picture">
    <div class="line" style="color: cyan">
        <span class="block">█</span>
        <span class="text">Start</span>
    </div>
</div>
```

## Resources

- **BBC Micro Teletext**: Similar to Viewdata/Prestel standard
- **Character Set**: Based on UK Teletext specification
- **Graphics Mode**: SAA5050 character generator chip
- **Decoding Tool**: `scripts/decode_picture.py`

## Summary

Cave-Plus graphics are:
- ✅ Simple Teletext format
- ✅ 40×8 character grid
- ✅ 8 colors with effects
- ✅ Block graphics (2×3 patterns)
- ✅ Easy to decode and render
- ✅ Can be converted to modern formats

The pictures add visual interest to key rooms while keeping file sizes tiny (256-320 bytes each)!
