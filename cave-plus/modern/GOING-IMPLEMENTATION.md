# GOING Screen Implementation

## Overview
Implemented the BBC Micro GOING exit screen functionality in the modern web version of Cave-Plus, including the authentic quit sequence with delays.

## Original Behavior (from Going.asm and Cave.basic)

### Quit Sequence (lines 2680-2810)
When player types QUIT in the original BBC Micro version:
1. Line 2720: Display "Hold on" (no newline)
2. Line 2740: Display ".." (continuing same line)
3. Save player file
4. Line 2740: Display "." (continuing same line, so shows "Hold on...")
5. Line 2810: Display "Saved." on new line
6. Execute `*GOING` command

### GOING Screen
When `*GOING` is executed:
1. Clears the screen
2. Switches to MODE 7 (teletext)
3. Displays farewell message:
   - Yellow text: "You have just left.."
   - Double-height cyan text: "CAVE"
   - Yellow text: "(C) 1985 XOB Partners."
4. Executes BYE command (logs off Econet)
5. Returns to BASIC prompt

## Modern Implementation

### Quit Sequence with Delays
**Server-Side (main.py):**
- When `quit_sequence` flag is returned from command parser:
  1. Send "Hold on" message
  2. Wait 0.5 seconds
  3. Send ".." message (appends to previous line)
  4. Save player data to JSON file
  5. Wait 0.3 seconds
  6. Send "." message (appends to previous line)
  7. Wait 0.5 seconds
  8. Send "Saved." message
  9. Wait 0.5 seconds
  10. Send disconnect message and close WebSocket

**Client-Side (game.js):**
- Modified `addMessage()` to detect ".." and "." messages
- These special messages append to the previous line instead of creating new line
- Result: "Hold on..." appears progressively, matching BBC Micro behavior

### GOING Screen
**Client-Side (game.js):**
Added `showGoing()` method that:
1. Clears the screen (switches to login screen)
2. Displays the farewell message matching the original format:
   - Yellow text: "You have just left.."
   - Double-height cyan text: "CAVE" (using Bedstead Ultra Condensed font)
   - Yellow text: "(C) 1985 XOB Partners."
3. Shows "Press any key to start again..." prompt
4. Waits for any keypress, then returns to login screen

### Timing Details
Total quit sequence takes approximately 2.3 seconds:
- 0.5s after "Hold on"
- 0.3s after ".."
- 0.5s after "."
- 0.5s after "Saved." before GOING screen

This gives the player time to see each message, matching the feel of the original BBC Micro version with disk I/O delays.

## Files Modified
- `cave-plus/modern/server/commands.py` - Modified `quit_game()` to return `quit_sequence` flag
- `cave-plus/modern/server/main.py` - Added delayed quit sequence handler with asyncio.sleep()
- `cave-plus/modern/static/js/game.js` - Modified `addMessage()` to append dots, added `showGoing()` method
- `cave-plus/analysed/Going.basic` → `cave-plus/analysed/Going.asm` - Renamed for clarity

## Triggered By
Currently implemented for:
- **QUIT/EXIT command** (intentional logout with save sequence)
  - "Hold on" → ".." → "." → "Saved." → GOING screen
- **Player death** (from combat or other causes)
  - "Life is slipping away...You are going" → ".." → GOING screen
  - Player data is saved before disconnect
- **WebSocket disconnect** (connection lost - shows GOING screen immediately)

### Future Enhancements
Could be extended to show Going screen for:
- Cave collapse (line 1620 in original)
- Exorcise (line 1470 in original)
- Fatal errors
- "Killed by an act of God" (line 105 in original)

## Testing
To test QUIT sequence:
1. Start the server: `cd cave-plus/modern && ./start.sh`
2. Login to the game
3. Type `QUIT` or `EXIT`
4. Should see:
   - "Hold on" appear
   - ".." append after 0.8s
   - "." append after 0.6s (showing "Hold on...")
   - "Saved." appear after 0.8s
   - GOING screen appear after 1.0s with farewell message
5. Press any key to return to login screen

To test death sequence:
1. Login to the game
2. Find a creature and attack it until it kills you (or let it attack you)
3. When stamina reaches 0, should see:
   - "Life is slipping away...You are going" appear
   - ".." append after 0.8s (showing "Life is slipping away...You are going..")
   - GOING screen appear after 1.0s with farewell message
4. Press any key to return to login screen
5. Your progress (including death count) will be saved
