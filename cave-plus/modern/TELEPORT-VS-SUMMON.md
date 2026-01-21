# TELEPORT vs SUMMON - Key Differences

## Overview

Both TELEPORT and SUMMON are magical transportation commands, but they work differently and have different target restrictions.

## TELEPORT Command (PROCw)

### What It Does
Teleports **you** to the location of an object or creature.

### Target Search Method
- Line 3110: `T=0:REPEATT=T+1:UNTILA$(T)=D$ORT=F+1`
- Manually searches through `A$()` array (objects 1-42)
- Does NOT use the `FND()` function

### Valid Targets
- ✅ Objects (Vodka, Stick, Dagger, etc.)
- ✅ Creatures (Dragon, Troll, Maggot, etc.)
- ❌ Players (NOT supported)

### Error Messages
- "Known OBJECTS & CREATURES only!" - Target not found or is a player
- "That object is being carried by a CAVER" - Object in another player's inventory
- "That is in the WIZARD's domain" - Target in rooms 16-20 (non-wizards only)
- "Nothing happens" - Failed success roll

### Success Chance
- Wizards: Always succeed
- Level 2 (score >= 500) with Ruby: Always succeed
- Level 2 without Ruby: 50% chance
- Level 1 without Ruby: 2% chance

### Example Usage
```
> teleport dragon
You concentrate... and suddenly find yourself elsewhere!

[You are now in the Dragon's room]
```

## SUMMON Command (PROCZ)

### What It Does
Summons an object, creature, **or player** to **your** location.

### Target Search Method
- Line 2100: `PROCG("SUMMONing")` which calls `FND(D$)`
- `FND()` searches in order:
  1. Objects/creatures in current room
  2. Objects/creatures anywhere
  3. **Players** (line 4450)

### Valid Targets
- ✅ Objects (Vodka, Stick, Dagger, etc.)
- ✅ Creatures (Dragon, Troll, Maggot, etc.)
- ✅ **Players** (supported!)

### How It Works
- **Objects**: Moved to your room
- **Creatures**: Teleported to your room (unless in mortuary)
- **Players**: Line 2170 sends event 8 (teleport) to player

### Error Messages
- "Sorry...wasted effort...[name] is not in CAVE" - Target not found
- "Nothing Happens" - Failed success roll or creature in mortuary

### Success Chance
- Wizards: Always succeed
- Level 2 (score >= 500) with Amulet: Very high chance
- Level 2 without Amulet: Moderate chance
- Level 1 without Amulet: Low chance

### Example Usage

**Summoning an Object:**
```
> summon dagger
The Dagger appears!
```

**Summoning a Creature:**
```
> summon troll
The Troll is here.
```

**Summoning a Player:**
```
> summon Bob
Bob has been summoned!

[Bob receives: "You have been summoned by Alice!"]
[Bob's old room sees: "Bob vanishes!"]
[Your room sees: "Bob appears!"]
```

## Comparison Table

| Feature | TELEPORT | SUMMON |
|---------|----------|--------|
| **Direction** | You go TO target | Target comes TO you |
| **Objects** | ✅ Yes | ✅ Yes |
| **Creatures** | ✅ Yes | ✅ Yes |
| **Players** | ❌ No | ✅ Yes |
| **Search Method** | Manual A$() loop | FND() function |
| **Success Item** | Ruby (Shield in code) | Amulet |
| **Wizard Bonus** | Always succeed | Always succeed |

## BBC Micro Code References

### TELEPORT (PROCw) - Lines 3110-3170
```basic
3110 DEFPROCw
3110 T=0:REPEATT=T+1:UNTILA$(T)=D$ORT=F+1
3110 IFT=F+1PRINT"Known OBJECTS & CCMS only!":ENDPROC
3135 IFINSTR(Hh$,D$)<>0PRINT"A magical force prevents this.":VDU7:ENDPROC
3136 IFD$="Treasure"PRINT"Not allowed !!":VDU7:ENDPROC
3140 T=&A00+T*4
3140 IF?T=0PRINT"That object is being carried by a CAVER":ENDPROC
3150 IFG=FALSEAND?T>15AND?T<21PRINT"That is in the WIZARD's domain":ENDPROC
3160 IFG=FALSEANDRND(50/z)>1-4*((A*&100)=!&A28)PRINT"Nothing happens":ENDPROC
3170 PROCY(?T):ENDPROC
```

### SUMMON (PROCZ) - Lines 2100-2170
```basic
2100 DEFPROCZ
2100 PROCG("SUMMONing")
2100 IFGTHEN2140
2130 IFRND(20/z)>1-3*(!&A28=A*&100)PRINT"Nothing Happens":ENDPROC
2140 IFT>&A00 AND ?T<>19 PROCO(T,?T,B):ENDPROC
2150 IFT>&A00ENDPROC
2160 IFT=&A00PRINT"Sorry...wasted effort...";D$;" is not"'"in CAVE":ENDPROC
2165 IFNOTFNIVDU7:ENDPROC
2170 PROCC(8,?(T+8),CHR$B):ENDPROC
```

### FND Function - Lines 4390-4480
```basic
4390 DEFFND(D$)
4390 mo=0:T=&A00
4390 REPEATT=T+4
4390 UNTIL((A$((T-&A00)/4)=D$ANDB$((T-&A00)/4)<>"")AND?T=B)OR(T-&A00)/4>=F+1
4390 IF(T-&A00)/4<=FTHEN=T
4430 T=&A00
4430 REPEATT=T+4
4430 UNTIL((A$((T-&A00)/4)=D$ AND B$((T-&A00)/4)<>"")) OR (T-&A00)/4>=F+1
4430 IF(T-&A00)/4<=F THEN=T
4450 D$=FNB(D$):T=&900              : REM Search for player
4450 REPEATT=T+&10:UNTILT>=&A00OR$T=D$
4450 IFT=&A00PRINT"I don't know who that is":VDU7
4480 =T
```

## Strategic Implications

### For Players
- **TELEPORT**: Use to quickly travel to known object/creature locations
- **SUMMON**: Use to bring objects, creatures, or other players to you
- **PvP**: SUMMON is the only way to forcibly teleport another player

### For Wizards
- Both commands always succeed
- SUMMON players for meetings or to help them
- TELEPORT to objects/creatures for quick access

### For Non-Wizards
- Carry Ruby for reliable TELEPORT
- Carry Amulet for reliable SUMMON
- Can only carry one magic item at a time!

## Implementation Status

✅ Both commands fully implemented in Cave-Plus modern version
✅ Player summoning working correctly
✅ All BBC Micro behavior matched

---

**Last Updated**: January 21, 2026
**Version**: 1.0.0
