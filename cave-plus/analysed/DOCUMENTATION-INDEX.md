# Cave-Plus Documentation Index

Complete documentation for the Cave-Plus multiplayer ECONET adventure game for BBC Micro.

## Quick Start

**New to Cave-Plus?** Start here:
1. Read `README-DATA-FILES.md` for an overview
2. Check `ECONET-NETWORKING.md` to understand multiplayer
3. Browse `data-annotated.txt` to see all creatures and items

**Want to modify the game?** See:
1. `data-annotated.txt` - Change creature stats and behavior
2. `OBJINIT-annotated.txt` - Change starting locations
3. `Cave-annotated.basic` - Modify game logic

## Documentation Files

### Game Data
- **`README-DATA-FILES.md`** - Overview of all data files and how to modify them
- **`data-annotated.txt`** - Complete decode of data.strings with creature stats
- **`OBJINIT-annotated.txt`** - Initial placement of all objects and creatures
- **`rooms-parsed.yml`** - Complete room data with exits, descriptions, and initial objects (157 rooms)
- **`ROOMS-README.md`** - Guide to room structure, special rooms, and navigation
- **`GRAPHICS-FORMAT.md`** - BBC Micro Teletext Mode 7 graphics format explained
- **`graphics/`** - PNG renderings of all 25 room graphics (ready for web use)

### Source Code
- **`Cave-annotated.basic`** - Main game code with full commentary
- **`CHEADER.basic`** - Title screen and initialization
- **`MC.basic`** - Machine code for ECONET networking
- **`Check.basic`** - Player validation
- **`CaveSt.basic`** - Game startup
- **`Manage.basic`** - Network management utilities

### Networking
- **`ECONET-NETWORKING.md`** - Complete guide to multiplayer networking
  - How ECONET works
  - Network protocols
  - Message types
  - Synchronization
  - Troubleshooting
  
- **`ECONET-DIAGRAMS.txt`** - Visual diagrams
  - Network topology
  - Memory layout
  - Message flow
  - Packet structure
  - State machines

### Tools
- **`scripts/decode_objinit.py`** - Python tool to decode OBJINIT binary file
- **`scripts/parse_rooms.py`** - Python tool to parse room files and generate YAML
- **`scripts/decode_picture.py`** - Python tool to decode Teletext Mode 7 graphics (text output)
- **`scripts/teletext_to_ppm.py`** - Python tool to convert Teletext graphics to PPM/PNG images

## Key Concepts

### Game Structure
```
Cave-Plus
├── 157 Rooms (interconnected maze)
├── 42 Objects (15 items + 27 creatures)
├── 16 Player slots (multiplayer via ECONET)
└── Real-time combat and interaction
```

### Creature Properties
Each creature has a 22-character property string encoding:
- Behavior (Aggressive/Passive)
- Attack chances
- Teleport/Follow behavior
- Attack type and damage
- Health points

See `data-annotated.txt` for complete details.

### Network Architecture
```
BBC Micro Stations (1-254)
    ↓
ECONET Network (250 Kbps)
    ↓
Shared Player Table (&900-&9FF)
    ↓
Real-time Updates via Poke/Peek
```

See `ECONET-NETWORKING.md` for complete details.

## Common Tasks

### View All Creatures
```bash
# See data-annotated.txt, section "CREATURES (Objects 16-42)"
# Lists all 27 creatures with stats
```

### Change Creature Stats
1. Edit `data.strings`
2. Modify the 22-character property string
3. Reload game data

Example - Make Spider more aggressive:
```
Original: B10010005010010002H040
Modified: B50050005050500002H040
          ^^  ^^     ^^
          Attack%  Follow%
```

### Change Starting Locations
1. Use `python3 scripts/decode_objinit.py` to view current placement
2. Edit binary OBJINIT file (advanced)
3. Or modify PROCU in Cave.basic to change random placement

### Debug Network Issues
```basic
USERS          ' List all connected players
EXORCISE       ' Remove ghost players
ACTIVITY 5     ' Set creature activity level
```

## Game Statistics

### Objects
- **15 Items**: Vodka, Stick, Poison, Dagger, Arrow, Medicine, Knife, Flamethrower, Ruby, Shield, Crystal, Staff, Amulet, Treasure, Guardian
- **27 Creatures**: Dragon, Troll, Maggot, Spider, Killer, Snakes (4), Worm, Drunk, Toad, Guardian, Goblin, Dwarf, Necromancer, Centipede, Skeleton, Caveman, etc.

### Rooms
- **157 Total Rooms** (see `rooms-parsed.yml` for complete map)
- **Special Rooms**:
  - Room 1: Main Entrance / Altar (charge Staff of Merlin, Dragon boss)
  - Room 12: Green Room (light switch)
  - Room 16: Wizard's Room (central hub)
  - Room 17: Limbo (teleport trap, no exits)
  - Room 18: Wizard's Dungeon (prison, no exits)
  - Room 19: Mortuary (dead creatures)
  - Room 20: Armoury (exorcised objects, defensive items)
  - Room 26: Snake Pit (multiple snakes)
  - Room 29-30: Portcullis rooms (demon's room, torture caves)
  - Room 56: Bank / Crystal Tower Top (deposit treasure)
  - Room 72: Hall of Knowledge (tutorial area)

### Players
- **Max 16 simultaneous players**
- **Player progression**: New → Warrior → Master Caver → Wizard
- **Carrying capacity**: 2-5 items (depending on rank)

### Network
- **Max 254 stations** (ECONET limit)
- **~7 bytes/sec per player** (typical traffic)
- **0.36% network utilization** (16 players)

## Boss Monsters

1. **Dragon** (Room 1)
   - 600 HP
   - Burn attack: 160-240 damage
   - Passive until provoked
   - Awards major points when killed

2. **Guardian** (Room 20)
   - 999 HP (nearly invincible!)
   - Zap attack: 50-75 damage
   - Blocks magic when present

3. **Necromancer** (Room 13)
   - 500 HP
   - Zap attack: 30-45 damage
   - Powerful magic user

4. **Author** (Room 39) - Easter Egg!
   - 500 HP
   - Follows 99.9% of the time
   - Zap attack: 120-180 damage
   - The game creator as a character!

## Easter Eggs

1. **Author Character**: Nearly invincible NPC that follows you everywhere
2. **Goblin Bug**: Has 65535 HP in OBJINIT (max value)
3. **Debug Command**: Type "DEBUG" for hidden message
4. **Wizard Teleport**: Type "WIZ" as wizard to teleport to room 16

## Technical Details

### Memory Map
```
&0070-&0071   Network temp pointer
&0287-&0289   Network jump vector
&0900-&09FF   Player table (16 × 16 bytes)
&0A00-&0AFC   Object table (42 × 4 bytes)
&7700-&77FF   Message buffer
&7800-&7BFF   Machine code routines
&7900         Poke routine
&7991         Find routine
&795B         Send routine
```

### File Structure
```
CAVE-PLUS/
├── CAVE          Main game executable
├── DATA          Game data (text strings, object names, creature stats)
├── OBJINIT       Binary file (initial object placement)
├── CHECK         Player validation
├── CHEADER       Title screen
├── MC            Machine code network routines
├── CAVEST        Startup script
├── MANAGE        Network management
├── SCENE         Title graphics
├── R/1-157       Room descriptions
├── P/1-99        Room pictures (graphics)
└── C/*           Character save files
```

### ECONET Operations
- **OSWORD &81**: Peek (read remote memory)
- **OSWORD &82**: Poke (write remote memory)
- **OSBYTE &32**: Poll for completion
- **Port 0**: Default port for Cave-Plus

## Troubleshooting

### "CAVE FULL"
- Too many players (max 16)
- Wait for someone to quit

### "Already in CAVE"
- Duplicate login detected
- Use EXORCISE to clear ghost
- Rejoin game

### Lock File Stuck
- LOCK file not deleted properly
- Manually delete from file server
- Or wait for timeout

### Invisible Players
- Player table out of sync
- Use EXORCISE command
- Resynchronizes network

### Network Lag
- Too many players
- Reduce creature activity: ACTIVITY 0
- Check ECONET cable connections

## Credits

**Original Cave**  
(C) GJL WOTWECP 1985

**Cave-Plus**  
(C) XOB 1988 Version 1.00

**Documentation**  
Created 2026 for preservation and study

## Further Reading

- BBC Micro Advanced User Guide (ECONET chapter)
- Acorn ECONET System User Guide
- BBC BASIC Reference Manual
- 6502 Assembly Language Programming

## Contributing

To improve this documentation:
1. Test the game on real BBC Micro hardware or emulator
2. Document any undiscovered features
3. Add more examples and tutorials
4. Create tools for easier game modification

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Status**: Complete

For questions or corrections, please refer to the individual documentation files listed above.
