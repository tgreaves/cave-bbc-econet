# 💎 Treasure System Implementation

## Overview

The treasure system allows players to collect treasure and deposit it at the bank for points. The treasure then respawns in a random location for other players to find.

## DEPOSIT Command

### Original BBC Micro Code (PROCW, lines 3341-3345)

```basic
3341: IFD$<>"Treasure"PRINT"You can't.":ENDPROC
3343: IF!(&A00+15*4)<>A*&100PRINT"But you have no treasure !":VDU7:ENDPROC
3344: IFB<>56PRINT"Not here I'm afraid.":ENDPROC
3345: N=20+RND(20):PRINT"...";N;" points.":H=H+N
3345: REPEATN=RND(b):UNTILN>20ORN<16:!(&A00+15*4)=N:U=U-1:ENDPROC
```

### Implementation

The DEPOSIT command requires:
1. **Item**: Must be depositing "Treasure" (line 3341)
2. **Inventory**: Must have treasure in inventory (line 3343)
3. **Location**: Must be in room 56 (the bank) (line 3344)

When successful:
- Awards 20-40 points randomly (line 3345: `N=20+RND(20)`)
- Removes treasure from player's inventory
- Respawns treasure in random room excluding wizard's domain (rooms 16-20)

### Usage Example

```
> get treasure
Taken.

> inventory
You are carrying: Treasure (1/3)

> [navigate to room 56 - the bank]

> deposit treasure
You deposit the treasure, which vanishes and you get credited with 35 points.

> score
Score is 135
Stamina is 100
Stamina limit is 100
```

## Random Object Placement (DEFPROCU)

### Original BBC Micro Code (line 1001)

```basic
1001 DEFPROCU
1001 FORN=(k+1)TOZ
1001 REPEATT=RND(b):UNTILT>20ORT<16  : REM Find valid room
1001 !(&A00+(N*4))=T                  : REM Place object
1001 NEXT:ENDPROC
```

Where:
- `k=10` (constant)
- `Z=15` (constant)
- Loop from object 11 to 15 (k+1 to Z)

### Objects Affected

The following 5 objects are placed randomly on game initialization and REGEN:

| Object ID | Name | Original Location (OBJINIT) |
|-----------|------|----------------------------|
| 11 | Crystal Ball | Room 37 |
| 12 | Staff of Merlin | Room 1 (Altar) |
| 13 | Amulet | Room 1 (Altar) |
| 14 | Treasure | Room 1 (Altar) |
| 15 | Guardian | Room 1 (Altar) |

### Placement Rules

Objects spawn in random rooms with one restriction:
- **Excluded**: Wizard's domain (rooms 16-20)
- **Allowed**: All other rooms (1-15, 21-157)

This matches the BBC Micro logic: `REPEATT=RND(b):UNTILT>20ORT<16`

### When Randomization Occurs

1. **Game Initialization**: When server starts
2. **REGEN Command**: When wizard runs REGEN to reset the game world

## Fixed Object Placement

Objects 1-10 have fixed starting locations (from OBJINIT):

| Object ID | Name | Room |
|-----------|------|------|
| 1 | Vodka | 2 |
| 2 | Stick | 32 |
| 3 | Poison | 5 |
| 4 | Dagger | 5 |
| 5 | Arrow | 30 |
| 6 | Medicine | 11 |
| 7 | Knife | 15 |
| 8 | Flamethrower | 25 |
| 9 | Ruby | 20 (Armoury) |
| 10 | Shield | 20 (Armoury) |

These objects always spawn in the same locations and are not affected by DEFPROCU.

## Testing

Run the test suite to verify the treasure system:

```bash
cd cave-plus/modern
venv/bin/python3 test_treasure.py
```

### Test Coverage

1. **Random Placement**: Verifies objects 11-15 spawn randomly
2. **Wizard's Domain**: Confirms no objects spawn in rooms 16-20
3. **DEPOSIT at Bank**: Tests successful deposit at room 56
4. **DEPOSIT Elsewhere**: Tests rejection outside bank
5. **Treasure Respawn**: Verifies treasure respawns after deposit
6. **REGEN**: Confirms objects randomize on REGEN

## Implementation Files

- `server/commands.py`: DEPOSIT command implementation
- `server/game_state.py`: Random object placement logic
- `test_treasure.py`: Comprehensive test suite
- `COMPLETED.md`: Feature documentation

## BBC Micro Fidelity

This implementation matches the original BBC Micro behavior exactly:
- ✅ Same point range (20-40)
- ✅ Same location requirement (room 56)
- ✅ Same respawn logic (random room, exclude 16-20)
- ✅ Same random object placement (objects 11-15)
- ✅ Same exclusion zone (wizard's domain)

## Future Enhancements

Potential additions (not in original):
- Visual feedback when treasure respawns
- Notification to all players when treasure is deposited
- Treasure location hints for high-level players
- Multiple treasures with different values

---

**Status**: ✅ Complete and tested
**Last Updated**: January 21, 2026
**Version**: 1.0.0
