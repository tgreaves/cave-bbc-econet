# Cave-Plus Graphics

This directory contains PNG renderings of the original BBC Micro Teletext Mode 7 graphics from Cave-Plus.

## Files

All 25 room graphics have been converted from the original `P/*` files:

| File | Room | Description |
|------|------|-------------|
| room_2.png | 2 | Main entrance area with "Start" and "Lights" labels |
| room_3.png | 3 | Tunnel passage |
| room_9.png | 9 | Colored rooms area with "MAZE" label |
| room_11.png | 11 | Red room (hot/fire theme with brick pattern) |
| room_12.png | 12 | Green room (light switch location) |
| room_13.png | 13 | Blue room |
| room_16.png | 16 | Wizard's room (magical effects with flashing) |
| room_17.png | 17 | Limbo (teleport trap) |
| room_18.png | 18 | Wizard's dungeon |
| room_19.png | 19 | Mortuary |
| room_20.png | 20 | Armoury |
| room_25.png | 25 | Doctor's surgery |
| room_29.png | 29 | Portcullis west |
| room_30.png | 30 | Demon's room (fire/bricks) |
| room_32.png | 32 | Bar |
| room_37.png | 37 | Merlin's room (magical symbols, "B S" and "E M" labels) |
| room_49.png | 49 | Cyan room |
| room_50.png | 50 | Yellow room |
| room_51.png | 51 | Magenta room |
| room_55.png | 55 | Crystal tower |
| room_60.png | 60 | Underground passages |
| room_99.png | 99 | Server info screen ("Cave Ser: 010", "Hinwick Hall : Wellingborough") |
| room_141.png | 141 | Special room |
| room_148.png | 148 | Special room |
| room_150.png | 150 | Special room |

## Image Specifications

- **Format**: PNG (Portable Network Graphics)
- **Dimensions**: 320×64 pixels (40 characters × 8 lines, scaled 8×)
- **Colors**: 8-color palette (Red, Green, Yellow, Blue, Magenta, Cyan, White, Black)
- **Source**: BBC Micro Teletext Mode 7 graphics
- **Scale**: 8 pixels per character cell

## Usage in Web Implementation

These PNG files can be used directly in a web-based version of Cave-Plus:

### HTML Example
```html
<img src="graphics/room_2.png" alt="Room 2 - Main Entrance" class="room-graphic">
```

### CSS Styling
```css
.room-graphic {
    width: 320px;
    height: 64px;
    image-rendering: pixelated; /* Keep sharp pixels */
    image-rendering: crisp-edges;
}
```

### JavaScript Dynamic Loading
```javascript
function loadRoomGraphic(roomNumber) {
    const img = document.getElementById('room-graphic');
    img.src = `graphics/room_${roomNumber}.png`;
    img.alt = `Room ${roomNumber}`;
}
```

## Scaling Options

The images are currently rendered at 8× scale (8 pixels per character cell). To create different sizes:

```bash
# 2× scale (80×16 pixels) - smaller
python3 scripts/teletext_to_ppm.py cave-plus/original/P output_2x 2

# 16× scale (640×128 pixels) - larger
python3 scripts/teletext_to_ppm.py cave-plus/original/P output_16x 16
```

Then convert PPM to PNG:
```bash
for f in output_*/*.ppm; do magick "$f" "${f%.ppm}.png" && rm "$f"; done
```

## Original Format

The original files are BBC Micro Teletext Mode 7 graphics:
- Character-based graphics system
- 2×3 block patterns per character
- Control codes for colors and effects
- See `../GRAPHICS-FORMAT.md` for complete technical details

## Regenerating Graphics

To regenerate all graphics from the original files:

```bash
# Generate PPM files (no dependencies)
python3 scripts/teletext_to_ppm.py cave-plus/original/P cave-plus/analysed/graphics 8

# Convert to PNG (requires ImageMagick)
for f in cave-plus/analysed/graphics/*.ppm; do 
    magick "$f" "${f%.ppm}.png" && rm "$f"
done
```

## Notes

- Only 25 out of 157 rooms have graphics
- Most rooms rely on text descriptions only
- Graphics add visual interest to key locations
- File sizes are tiny (300-550 bytes per PNG)
- Original Teletext files are even smaller (256-320 bytes)

## Color Palette

The 8 Teletext colors used:

| Color | RGB | Hex |
|-------|-----|-----|
| Black | (0, 0, 0) | #000000 |
| Red | (255, 0, 0) | #FF0000 |
| Green | (0, 255, 0) | #00FF00 |
| Yellow | (255, 255, 0) | #FFFF00 |
| Blue | (0, 0, 255) | #0000FF |
| Magenta | (255, 0, 255) | #FF00FF |
| Cyan | (0, 255, 255) | #00FFFF |
| White | (255, 255, 255) | #FFFFFF |

## Credits

- **Original Graphics**: GJL WOTWECP (1985) and XOB (1988)
- **Conversion Tool**: `scripts/teletext_to_ppm.py`
- **Format**: BBC Micro Teletext Mode 7
- **Documentation**: 2026

---

For more information about the graphics format, see `../GRAPHICS-FORMAT.md`
