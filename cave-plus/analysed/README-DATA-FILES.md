# Cave-Plus Data Files Documentation

This directory contains annotated versions of the Cave-Plus game data files, making it easier to understand and modify the game.

## File Overview

### Original Files
- **`data.strings`** - Text data loaded at startup (messages, object names, creature properties)
- **`original/OBJINIT`** - Binary file containing initial object/creature placement

### Annotated Documentation Files
- **`data-annotated.txt`** - Human-readable version of data.strings with full explanations
- **`OBJINIT-annotated.txt`** - Decoded OBJINIT file showing where everything starts
- **`Cave-annotated.basic`** - Fully commented source code
- **`ECONET-NETWORKING.md`** - Complete guide to multiplayer networking
- **`ECONET-DIAGRAMS.txt`** - Visual diagrams of network architecture

## Quick Reference

### Data File Structure

The `data.strings` file contains (in order):
1. **Message Arrays** (15 entries)
   - G$(1-3): "Can't go that way" messages
   - H$(1-3): Hit messages
   - C$(1-3): Disappear messages
   - F$(1-3): Appear messages
   - E$(1-3): Error messages

2. **Direction Names** (6 entries)
   - North, South, West, East, Down, Up

3. **Objects and Creatures** (42 entries, each with 2 lines)
   - Line 1: Name
   - Line 2: Properties (empty for items, 22-char string for creatures)

### Creature Property String Format

Each creature has a 22-character property string:
```
Position  1:     Behavior (A=Aggressive, B=Passive)
Position  2-4:   Attack chance (0-999)
Position  5-7:   Secondary attack (for Aggressive creatures)
Position  8-10:  Teleport chance (0-999, ×100)
Position 11-13:  Follow chance (0-999, ÷1000)
Position 14-15:  Attack type code (01-13)
Position 16-18:  Base damage
Position 19:     'H' marker
Position 20-22:  Health points
```

### Attack Type Codes
- 01 = Message
- 02 = Hit
- 03 = Cave collapse
- 04 = Award points
- 05 = Poison
- 06 = Stab
- 10 = Bite
- 11 = Burn
- 12 = Zap
- 13 = Shoot

### OBJINIT File Format

Binary file with 4-byte little-endian integers (one per object/creature):
```
Byte 0:     Room number (0-70)
Bytes 1-3:  Initial stamina/health
```

## Notable Creatures

### Boss Monsters
- **Dragon** (Room 1): 600 HP, 160-240 burn damage
- **Guardian** (Room 20): 999 HP, 50-75 zap damage

### Dangerous Enemies
- **Killer** (Room 46): Teleports 80%, follows 95%, stab 8-12 damage
- **Necromancer** (Room 13): 500 HP, zap 30-45 damage
- **Author** (Room 39): Easter egg! 500 HP, follows 99.9%, zap 120-180 damage

### Weakest Enemies
- **Worm** (Room 26): Only 5 HP but attacks 95% of the time
- **Drunk** (Room 20): 40 HP, stumbles around (70% teleport)

## Special Rooms

- **Room 1** (Altar): Where Staff of Merlin can be charged
- **Room 19** (Mortuary): Where dead creatures go
- **Room 20** (Armoury): Where exorcised objects are moved
- **Room 56** (Bank): Where treasure can be deposited for points

## Modifying the Game

### To Change Creature Stats
Edit `data.strings` and modify the property string. For example, to make Spider more aggressive:

Original:
```
Spider
B10010005010010002H040
```

More aggressive (50% attack, follows 50%):
```
Spider
B50010005010500002H040
```

### To Change Initial Placement
You'll need to edit the binary `OBJINIT` file or use the Python decoder script:
```bash
python3 scripts/decode_objinit.py cave-plus/original/OBJINIT
```

### To Add New Creatures
1. Add name and property string to `data.strings`
2. Update F=42 in the code to F=43 (or higher)
3. Add entry to OBJINIT file
4. Recompile the game

## Tools

### Python Decoder Script
Located at `scripts/decode_objinit.py`:
```bash
python3 scripts/decode_objinit.py [path-to-OBJINIT]
```

Outputs human-readable placement information for all objects and creatures.

## Understanding the Code

The game loads data in this sequence:
1. Line 195: `*L.DATA 7200` - Load data.strings to memory
2. Line 200-270: Read arrays using FNget function
3. Line 700: `OSCLI("LO.OBJINIT")` - Load OBJINIT file
4. Line 1001: PROCU - Place creatures randomly (only some creatures)

### Object Memory Layout
Objects are stored at memory addresses &A00-&AFC:
- Each object: 4 bytes
- Byte 0: Room number (or 0 if carried, 19 if dead)
- Bytes 1-3: Current stamina (for creatures)

### Creature Behavior
Creatures act based on:
- Activity level (?&A00): Set by wizard or defaults to 0
- Random rolls against property string values
- Current room and player presence

## Easter Eggs

1. **Author Character**: Nearly invincible character that follows you everywhere
2. **Goblin Bug**: Has 65535 HP in OBJINIT (likely a bug or test creature)
3. **Debug Command**: Type "DEBUG" for a hidden message

## Credits

Original Cave: (C) GJL WOTWECP 1985  
Cave-Plus: (C) XOB 1988 Version 1.00  
Documentation: Created for preservation and study

---

For more details, see the individual annotated files in this directory.
