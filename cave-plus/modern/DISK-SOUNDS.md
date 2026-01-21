# Authentic BBC Micro Disk Sounds

## Overview
The game now includes authentic BBC Micro 5.25" floppy disk drive sounds and delays to recreate the nostalgic experience of the original 1985 game.

## Features

### Disk Operations
The following operations trigger disk activity:
- **Player Login** - Loading existing player data (read operation)
- **New Player Creation** - Saving new player account (write operation)
- **Room Movement** - Loading room data when entering a new room (read operation)
- **QUIT Command** - Saving player progress (write operation)
- **Death** - Auto-saving player state (write operation)

### Authentic Timing
Based on real BBC Micro DFS (Disk Filing System) timings:
- **Seek Time**: 200ms - Head movement between tracks
- **Read Time**: 400ms - Reading data from disk
- **Write Time**: 600ms - Writing data to disk (slower than read)
- **Room Load**: 150ms - Quick read for room data (smaller files)

### Sound Effects
Authentic BBC Micro 5.25" floppy disk drive sounds from real hardware recordings:

1. **seek.wav** - Initial head seek sound as the drive positions the read/write head
2. **step.wav** - Stepper motor steps (played 2-3 times) as the head moves between tracks

The sounds are played in sequence:
- seek.wav (initial positioning)
- 100ms delay
- step.wav × 2-3 (with 50ms between each step)
- Final delay based on operation type (200ms for read, 400ms for write)

### User Controls
- **Sound Toggle Button** (🔊/🔇) - Located on the monitor bezel
  - Enables/disables all sound effects
  - State persists in browser localStorage
  - Disk timing delays remain even when sound is off (authentic behavior)

## Technical Implementation

### Client Side (game.js)
- `playDiskOperation(type)` - Plays seek.wav followed by 2-3 step.wav sounds
- `playWavFile(url)` - Loads and plays WAV files using Web Audio API
- Authentic sound files from real BBC Micro hardware recordings

### Server Side (main.py, player_data.py)
- Sends `disk_activity` messages before disk operations
- Actual file I/O includes authentic delays
- Returns timing information for logging

### Message Protocol
```json
{
  "type": "disk_activity",
  "operation": "read" | "write"
}
```

## Historical Accuracy
The BBC Micro used 5.25" floppy disks with the Acorn DFS (Disk Filing System). The characteristic sounds came from:
- Stepper motor moving the read/write head (seek)
- Spindle motor rotating the disk (constant hum)
- Head reading/writing data (variable pitch based on track position)

These sounds are recreated using Web Audio API synthesis to match the frequency characteristics and timing of the original hardware.

## Future Enhancements
Potential additions:
- Different sounds for different disk operations (format, catalog, etc.)
- Track-based pitch variation (outer tracks = lower pitch)
- Disk error sounds (read/write failures)
- Multiple disk drive support (different pitch per drive)
