# Cave-Plus Combat System

## Overview

The combat system is now fully implemented based on the original BBC Micro game logic. Creatures have individual behaviors, attack patterns, and AI that matches the original game.

## Combat Commands

### Attack Commands
- `hit <creature>` - Attack a creature with your best weapon
- `hit <player>` - Attack another player (PvP)
- `attack <creature/player>` - Same as hit
- `kill <creature/player>` - Same as hit
- `fight <creature/player>` - Same as hit

### Magic Commands
- `zap <creature>` - Use Staff of Merlin (50-75 damage)
- `staff <creature>` - Same as zap

### Examples
```
hit dragon        - Attack the Dragon
attack troll      - Attack a Troll
hit Bob           - Attack player Bob (PvP)
zap spider        - Zap a Spider with magic
```

## Player vs Player (PvP) Combat

### PvP Mechanics
- Players can attack each other in the same room
- Use `hit <playername>` to attack another player
- PvP damage: 1-3 base damage
- Stick bonus: +3 damage (only weapon that works in PvP)
- Other weapons don't provide bonuses in PvP

### PvP Death
When a player is defeated:
- Attacker gains 50 points
- Attacker's kill count increases
- Victim's death count increases
- Victim respawns at Room 1 (entrance)
- Victim's health is restored to full
- Victim drops ALL items

### PvP Strategy
- Get the Stick for +3 damage bonus
- Attack when opponent is weakened by creatures
- Coordinate with creatures to trap players
- Defend valuable items by staying mobile

### PvP Etiquette
- PvP is enabled by default (like the original game)
- Be prepared for attacks in multiplayer
- Form alliances or go solo
- Remember: it's all part of the game!

## Creature Behavior

### Passive vs Aggressive

**Passive Creatures (Behavior: B)**
- Don't attack unless provoked
- Become aggressive when attacked
- May still follow or teleport based on their stats

**Aggressive Creatures (Behavior: A)**
- Attack on sight
- Always hostile
- Will pursue players

### Creature Stats

Each creature has:
- **Attack Chance**: 0-999 (probability of attacking per tick)
- **Teleport Chance**: 0-999 (probability of teleporting)
- **Follow Chance**: 0-999 (probability of following a player)
- **Attack Type**: Hit, Bite, Stab, Burn, Zap, etc.
- **Base Damage**: Randomized (damage + random(damage/2))
- **Health**: Hit points

## Spawned Creatures

### Room 1 (Altar)
- **Dragon** (0 HP - inactive/dead initially)
  - Passive until provoked
  - Burn attack: 160-240 damage
  - 600 HP - Boss monster!

### Room 5
- **Maggot** (48 HP)
  - Loves to follow (85%)
  - Bite: 6-9 damage
  - 60 HP

### Room 8
- **Skeleton** (100 HP)
  - Weak hit: 1-1.5 damage
  - 100 HP

### Room 13
- **Dwarf** (20 HP) + **Necromancer** (60 HP)
  - Dwarf: Bite 8-12 damage, 60 HP
  - Necromancer: Zap 30-45 damage, 500 HP
  - Dangerous room!

### Room 20 (Armoury)
- **Spider** (579 HP), **Viper** (112 HP), **Drunk** (6 HP), **Guardian** (0 HP)
  - Multiple enemies
  - Guardian is nearly invincible (999 HP)

### Room 26 (Snake Pit)
- **Cobra**, **Python**, **Adder**, **Worm** (all 42 HP)
  - Four snakes!
  - Bite: 6-9 damage
  - Teleport frequently (60%)

### Room 38
- **Troll** (784 HP)
  - High initial stamina
  - Hit: 4-6 damage
  - Can teleport (30%) and follow (60%)

### Room 39
- **Author** (34 HP)
  - Easter egg character!
  - Follows almost everywhere (99.9%)
  - Zap: 120-180 damage
  - 500 HP

### Room 46
- **Killer** (38 HP)
  - Teleports frequently (80%)
  - Follows relentlessly (95%)
  - Stab: 8-12 damage
  - 100 HP

### Other Rooms
- Room 3: Unnamed creature
- Room 14: Unnamed creature
- Room 23: Unnamed creature
- Room 32: Unnamed creature
- Room 37: Centipede
- Room 55: Goblin (65535 HP - bugged!)
- Room 63: Toad + Unnamed
- Room 67: Coward
- Room 83: Caveman

## Weapon System

### PvE (Player vs Creature) Damage Bonuses
- **Bare hands**: 1-3 damage
- **Stick**: +3 damage
- **Dagger/Knife**: +6-9 damage
- **Flamethrower**: +50-75 damage
- **Staff of Merlin**: +50-75 damage (Zap attack)

### PvP (Player vs Player) Damage
- **Bare hands**: 1-3 damage
- **Stick**: +3 damage (ONLY weapon that works in PvP)
- **Other weapons**: No bonus in PvP

### Weapon Priority (PvE)
The game automatically uses your best weapon against creatures:
1. Flamethrower (strongest)
2. Staff of Merlin
3. Dagger
4. Knife
5. Stick
6. Bare hands (weakest)

## Combat Mechanics

### Player Attacks
1. Player uses `hit <creature>` command
2. Game finds creature in room
3. Calculates damage (base + weapon bonus)
4. Applies damage to creature
5. Creature becomes aggressive if not already
6. If creature dies, player gains points

### Creature Attacks
1. Every game tick (1 second), creatures check if they should attack
2. Passive creatures only attack if aggressive
3. Attack chance is rolled (0-999)
4. If attack succeeds, damage is calculated
5. Damage is applied to a random player in the room
6. Player receives damage notification

### Creature AI
Every tick, each creature:
1. **Checks teleport** - May randomly teleport to another room
2. **Checks follow** - May follow a player to their room
3. **Checks attack** - May attack if conditions are met

### Death and Scoring
- **Creature dies**: Player gains points (1 point per 10 HP)
- **Player dies**: Respawns at entrance (not yet implemented)
- **Kill count**: Tracked in player stats

## Special Creatures

### Dragon (Room 1)
- Boss monster with 600 HP
- Starts inactive (0 HP in OBJINIT)
- Passive until attacked
- Burn attack deals massive damage
- Killing triggers special message

### Guardian (Room 20)
- Nearly invincible (999 HP)
- Zap attack: 50-75 damage
- Doesn't move or follow
- Guards the Armoury

### Author (Room 39)
- Easter egg character
- Follows you everywhere (99.9%)
- Very powerful (500 HP, 120-180 damage)
- Don't attack unless you're ready!

### Goblin (Room 55)
- Bugged with 65535 HP (max value)
- Effectively unkillable
- Stab: 6-9 damage
- Likely a testing creature

## Strategy Tips

### For Beginners
1. Start with weak creatures (Worm, Spider, Drunk)
2. Get weapons before fighting (Stick, Dagger)
3. Avoid aggressive creatures initially
4. Run from rooms with multiple creatures

### For Advanced Players
1. Get Flamethrower or Staff of Merlin
2. Challenge the Troll or Killer
3. Clear the Snake Pit (Room 26)
4. Attempt the Dragon (Room 1)

### Dangerous Rooms
- **Room 1**: Dragon (boss)
- **Room 13**: Dwarf + Necromancer combo
- **Room 20**: Multiple creatures + Guardian
- **Room 26**: Four snakes
- **Room 39**: The Author
- **Room 46**: Killer (teleports and follows)

## Current Limitations

### Not Yet Implemented
- Player death and respawn
- Creature following between rooms
- Creature respawning
- Special attack types (poison, cave collapse, etc.)
- Shield blocking
- Medicine healing
- Vodka effects

### Working Features
- ✅ Creature spawning
- ✅ Passive/aggressive behavior
- ✅ Attack mechanics (PvE)
- ✅ PvP combat (Player vs Player)
- ✅ Damage calculation
- ✅ Weapon bonuses
- ✅ Creature death
- ✅ Player death and respawn
- ✅ Point scoring
- ✅ Kill tracking
- ✅ Creature stats display
- ✅ Item dropping on death

## Testing Combat

### Test Basic Combat
```
look              - See creatures in room
hit maggot        - Attack the maggot
look              - Check creature health
```

### Test Weapons
```
get stick         - Pick up a weapon
hit spider        - Attack with weapon
drop stick        - Drop weapon
hit spider        - Attack bare-handed
```

### Test Magic
```
get staff         - Get Staff of Merlin
zap dragon        - Use powerful magic
```

### Test Multiple Creatures
```
# Go to Room 26 (Snake Pit)
hit cobra         - Attack one snake
look              - See all snakes
hit python        - Attack another
```

### Test PvP Combat
```
# Open two browser tabs with different names
# Tab 1 (Alice):
get stick         - Get weapon for bonus damage
say ready?        - Coordinate with other player

# Tab 2 (Bob):
say ready!        - Respond

# Tab 1 (Alice):
hit Bob           - Attack Bob
look              - See Bob's status

# Tab 2 (Bob):
hit Alice         - Fight back!
```

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic combat
- ✅ Creature AI
- ✅ Weapon system

### Phase 2 (Next)
- Creature following between rooms
- Player death and respawn
- Creature respawning
- Health regeneration

### Phase 3 (Later)
- Special attack types
- Status effects (poison, etc.)
- Shield mechanics
- Item effects (medicine, vodka)

---

**Combat is now live!** Visit http://localhost:8000 and start fighting!
