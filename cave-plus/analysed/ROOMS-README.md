# Cave-Plus Room Data

This document explains the room data structure and how it was parsed.

## Overview

Cave-Plus contains **157 interconnected rooms** forming a complex maze. Each room has:
- A text description
- Exits (north, south, east, west, up, down)
- Optional initial objects/creatures
- Optional special properties

## Files

### `rooms-parsed.yml`
Complete room database in YAML format with:
- All 157 room descriptions
- Exit connections between rooms
- Special room annotations (Altar, Bank, Armoury, etc.)
- Initial object and creature placement from OBJINIT

### `original/R/1` through `original/R/157`
Original BBC Micro room files (binary format):
- First 64 bytes: Exit data (e.g., "D2S3E72")
- Offset 0x40+: Room description text

## Room File Format

Each room file is a binary file with this structure:

```
Offset 0x00-0x3F (64 bytes):  Exit codes and metadata
Offset 0x40+:                 Room description (ASCII text)
```

### Exit Codes
Format: `D2S3E72` means:
- D2 = Down to room 2
- S3 = South to room 3  
- E72 = East to room 72

Direction codes:
- N = North
- S = South
- E = East
- W = West
- U = Up
- D = Down

## Special Rooms

### Room 1: Main Entrance / Altar
- Starting location
- Dragon boss spawns here
- Staff of Merlin can be charged at the altar
- Contains: Dragon, Staff, Amulet, Treasure, Guardian (×2)

### Room 12: Green Room
- Contains light switch
- Controls lighting in certain areas

### Room 16: Wizard's Room
- Central hub of wizard domain
- Connects to Limbo (17), Dungeon (18), Mortuary (19), Armoury (20)

### Room 17: Limbo
- Teleport trap
- All exits loop back to itself
- No natural way out

### Room 18: Wizard's Dungeon
- Prison with no exits
- Players must teleport out

### Room 19: Mortuary
- Where dead creatures are moved
- One exit to Wizard's Room

### Room 20: Armoury
- Where exorcised objects are moved
- Contains defensive items: Ruby, Shield
- Guarded by: Spider, Viper, Drunk, Guardian

### Room 26: Snake Pit
- Multiple snakes spawn here
- Contains: Cobra, Python, Adder, Worm
- Dangerous area!

### Room 29-30: Portcullis
- Room 29: West side with rope
- Room 30: Demon's Room, leads to torture caves (77+)

### Room 56: Bank / Crystal Tower Top
- Deposit treasure here for points
- Sign says "DEPOSIT treasre here"
- Top of Crystal Tower

### Room 72: Hall of Knowledge
- Tutorial area near main entrance
- Connects to instruction rooms (73-75)
- Room 73: Movement tutorial
- Room 74: Object manipulation tutorial
- Room 75: Combat tutorial

## Room Distribution

### By Area

**Main Entrance Area (1-15)**
- Starting rooms, tutorial area, colored rooms, maze

**Wizard's Domain (16-20)**
- Special rooms: Wizard's Room, Limbo, Dungeon, Mortuary, Armoury

**Eastern Passages (21-30)**
- Doctor's surgery, snake pit, portcullis

**Southern Caverns (31-48)**
- Bar, large cavern with bottomless chasm, colored rooms

**Crystal Tower (54-58)**
- Vertical tower structure leading to Bank

**Underground River (60-71)**
- Water passages, eastern/western shores

**Torture Caves (77-91)**
- Dark passages, torture room, staircase

**Northern Tunnels (92-99)**
- Dimly lit tunnels, crevice, fire cavern

**Fire Cavern (100-107)**
- Large cavern with pillar of fire
- Strange room with locked door (107)

**Eastern Corridors (108-145)**
- Twisting corridors, maze sections

**Maze of Rassalas (146-157)**
- Complex maze area
- Trap door back to room 117

## Initial Object Placement

From OBJINIT file analysis:

### Most Populated Rooms
- **Room 1**: 6 objects (Dragon, Staff, Amulet, Treasure, Guardian ×2)
- **Room 20**: 6 objects (Ruby, Shield, Spider, Viper, Drunk, Guardian)
- **Room 26**: 5 creatures (Cobra, Python, Adder, Worm, +1)

### Strategic Placement
- **Weapons**: Scattered throughout (Stick in 32, Dagger in 5, Flamethrower in 25)
- **Healing**: Medicine in room 11, Vodka in room 2
- **Boss Monsters**: Dragon (1), Guardian (20), Necromancer (13)
- **Easter Eggs**: Author in room 39, Goblin with 65535 HP in room 55

## Parsing Process

The `scripts/parse_rooms.py` tool:

1. Reads all 157 room files from `original/R/`
2. Extracts exit codes from first 64 bytes
3. Reads description from offset 0x40
4. Cleans up control characters and garbage data
5. Adds special room annotations
6. Adds initial object placement from OBJINIT
7. Generates YAML output

### Cleaning Process
- Remove null bytes and control characters
- Trim garbage text at end of descriptions
- Remove multiple spaces
- Decode ASCII/Latin-1 text

## Usage Examples

### Find a Room
```yaml
rooms:
  1:
    name: 'Main Entrance / Altar'
    description: |
      This is the Main Entrance. The cave extends down to the south...
    exits:
      south: 2
      east: 72
      down: 2
```

### Navigate the Cave
- From room 1, you can go: South to 2, East to 72, Down to 2
- From room 2, you can go: North to 1, East to 3, West to 4, Up to 1

### Find Objects
Look for `initial_objects` in room data:
```yaml
initial_objects:
  - 'Dragon'
  - 'Staff of Merlin'
```

## Statistics

- **Total Rooms**: 157
- **Rooms with Objects**: 24
- **Special Rooms**: 12
- **Dead Ends**: 18 (rooms with only 1 exit)
- **Hubs**: 5 (rooms with 4+ exits)
- **Traps**: 2 (Limbo, Wizard's Dungeon)

## Map Connections

### Major Pathways
1. **Main Route**: 1 → 2 → 3 → 6 → 7 → 8 → 21 → ...
2. **Tutorial Route**: 1 → 72 → 73/74/75
3. **Wizard Route**: 7 → 9 → 12/13 → ... → 16 → 17/18/19/20
4. **Tower Route**: 48 → 54 → 55 → 56 (Bank)
5. **Torture Route**: 30 → 77 → 78 → ...

### Isolated Areas
- Room 17 (Limbo): Self-contained trap
- Room 18 (Dungeon): No exits
- Room 126: Locked room, no visible exit

## Future Enhancements

Possible improvements to room data:

1. **Room Features**
   - Lighting status (dark/lit)
   - Special mechanics (portcullis, switches)
   - Environmental hazards

2. **Dynamic Objects**
   - Respawn locations
   - Random placement zones (rooms 16-70)

3. **Map Visualization**
   - Generate graphical map from YAML
   - Show connections between rooms
   - Highlight special areas

4. **Game Balance**
   - Difficulty ratings per room
   - Recommended player levels
   - Treasure/danger ratios

## Credits

- **Original Room Design**: GJL WOTWECP (1985)
- **Cave-Plus Expansion**: XOB (1988)
- **Documentation**: 2026

---

For complete game documentation, see `DOCUMENTATION-INDEX.md`
