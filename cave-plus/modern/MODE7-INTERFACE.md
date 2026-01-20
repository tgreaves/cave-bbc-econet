# BBC Micro MODE 7 Interface

## Overview

The web interface has been redesigned to authentically replicate the BBC Micro MODE 7 Teletext display used in the original game (1985-1988).

## MODE 7 Specifications

### Display Format
- **Resolution**: 40 columns × 25 rows (character-based)
- **Font**: ModeSeven (authentic SAA5050 Teletext font)
- **Colors**: Black background with colored text (yellow, cyan, green, magenta, red)
- **Character Size**: 16px width × 20px height (scales on smaller screens)

### Screen Layout

The original game divided the screen into three areas:

```
┌────────────────────────────────────────┐
│ Rows 0-5: STATUS AREA (6 rows)        │  ← Player info & combat messages
├────────────────────────────────────────┤
│ Row 6: SEPARATOR                       │
├────────────────────────────────────────┤
│ Rows 7-23: MAIN GAME AREA (17 rows)   │  ← Room descriptions & messages
├────────────────────────────────────────┤
│ Row 24: COMMAND INPUT                  │  ← Player commands
└────────────────────────────────────────┘
```

## Implementation Details

### Status Area (Rows 0-5)

The status area displays:
- Player name and rank
- Current stamina / max stamina
- Score
- Inventory count

During combat or important events, temporary messages appear here (like "You are HIT!") and automatically clear after 3 seconds.

This matches the original PROCB procedure from line 3810:
```basic
DEFPROCB(X$)
  VDU26,28,0,5,39,0,31,0,5  : REM Set text window rows 0-5
  PRINTX$
  VDU26,28,0,23,39,7        : REM Restore main window
```

### Main Game Area (Rows 7-23)

The main area shows:
- Room names and descriptions
- Objects in the room
- Other players present
- Game messages and responses
- Combat results

All text scrolls automatically, with the most recent messages at the bottom.

### Command Input (Row 24)

A simple prompt (`>`) followed by the input field. No placeholder text to maintain authenticity.

## Font Details

### ModeSeven Font
- **Source**: [OnlineWebFonts.com](https://www.onlinewebfonts.com/download/a0cb693c715aaf804e67963c4d0d4d90)
- **Creator**: Andrew Bulhak (1998)
- **Based on**: BBC Micro Teletext character generator
- **License**: Freeware
- **Optimal Size**: 20px or multiples thereof

The font is loaded via CDN:
```css
@import url(https://db.onlinewebfonts.com/c/a0cb693c715aaf804e67963c4d0d4d90?family=ModeSeven);
```

### Alternative Fonts

Other authentic MODE 7 fonts available:
- **Teletext50** - From the Bedstead project (supports full Latin-1)
- **MODE7** - BBC Micro ASCII-only font from Galax.xyz

## Color Scheme

Following MODE 7 Teletext conventions:

- **Yellow** (`#ffff00`) - Headings, prompts, important text
- **Cyan** (`#00ffff`) - System messages, player names
- **Green** (`#00ff00`) - Success messages, stats
- **Magenta** (`#ff00ff`) - Combat messages
- **Red** (`#ff0000`) - Death messages, errors
- **White** (`#ffffff`) - Normal text
- **Black** (`#000000`) - Background

## Responsive Design

The interface scales down on smaller screens:
- **Desktop**: 16px × 20px characters
- **Tablet** (< 800px): 12px × 16px characters
- **Mobile** (< 600px): 10px × 14px characters

The 40×25 grid is maintained at all sizes.

## Technical Implementation

### HTML Structure
```html
<div class="game-container">
  <div class="status-area">
    <div id="status-messages"></div>
  </div>
  <div class="main-game-area">
    <div id="message-log"></div>
  </div>
  <div class="command-area">
    <span class="prompt">&gt;</span>
    <input id="command-input">
  </div>
</div>
```

### CSS Variables
```css
:root {
  --char-width: 16px;
  --char-height: 20px;
  --cols: 40;
  --rows: 25;
}
```

### JavaScript Status Updates

The status area is dynamically updated:
- Normal state: Shows player stats
- Combat/events: Shows temporary messages
- Auto-restore: Returns to stats after 3 seconds

## Differences from Original

### Kept from Original
- 40×25 character grid
- Black background
- Status area at top (rows 0-5)
- Main area in middle (rows 7-23)
- Command input at bottom (row 24)
- Teletext font aesthetic

### Modern Enhancements
- Smooth scrolling in message area
- Command history (arrow keys)
- WebSocket real-time updates
- Responsive scaling for different screen sizes
- Anti-aliased font rendering (can be disabled for pure pixel look)

## Future Improvements

Potential enhancements while maintaining MODE 7 authenticity:
- [ ] Teletext control codes (double height, flashing text)
- [ ] Scanline effect for CRT simulation
- [ ] Phosphor glow effect
- [ ] Authentic MODE 7 color palette (limited to 7 colors per row)
- [ ] Separated/contiguous graphics mode
- [ ] Hold graphics mode

## References

- [BBC Micro MODE 7 Documentation](http://www.bbcbasic.co.uk/bbcwin/manual/bbcwin3.html#mode7)
- [SAA5050 Teletext Character Generator](https://en.wikipedia.org/wiki/SAA5050)
- [ModeSeven Font](https://www.fontspace.com/modeseven-font-f2369)
- [Bedstead/Teletext50 Project](https://github.com/glxxyz/bedstead)

---

Last Updated: January 20, 2026
