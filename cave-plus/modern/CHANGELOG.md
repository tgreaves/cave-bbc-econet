# Cave-Plus Recreation - Changelog

## Latest Updates

### Combat System Fixes (Current Session)

**Fixed: Dragon Not Fighting Back**
- Dragon now spawns with 600 HP (was 0 HP, marked as dead)
- Creatures with 0 initial stamina are now skipped (except Dragon)
- Dragon is now a proper boss fight!

**Fixed: Creatures Not Attacking Players**
- Game loop now broadcasts creature attacks to players
- Players receive damage notifications
- Player stats update in real-time
- Death and respawn system working

**Added: Player vs Player (PvP) Combat**
- Players can attack each other with `hit <playername>`
- PvP damage: 1-3 base + Stick bonus (+3)
- Defeated players respawn at entrance
- Defeated players drop all items
- Kill/death tracking for PvP
- 50 point bonus for PvP kills

### Combat System Implementation

**Creature AI**
- ✅ Passive/aggressive behavior
- ✅ Attack probability (0-999 per tick)
- ✅ Teleport probability
- ✅ Follow probability
- ✅ Target tracking

**Attack Types**
- ✅ Hit (2-3 damage)
- ✅ Bite (6-9 damage)
- ✅ Stab (6-12 damage)
- ✅ Burn (160-240 damage - Dragon)
- ✅ Zap (30-180 damage - various)

**Weapon System**
- ✅ Bare hands (1-3 damage)
- ✅ Stick (+3 damage)
- ✅ Dagger/Knife (+6-9 damage)
- ✅ Flamethrower (+50-75 damage)
- ✅ Staff of Merlin (+50-75 damage)
- ✅ Automatic weapon selection

**Creature Spawning**
- ✅ 26 creatures spawned across cave
- ✅ Initial stamina from OBJINIT
- ✅ Creature stats from data file
- ✅ Room-based placement

**Death & Respawn**
- ✅ Creature death
- ✅ Player death (from creatures or PvP)
- ✅ Respawn at entrance
- ✅ Item dropping on death
- ✅ Point scoring
- ✅ Kill/death tracking

### Known Issues

**Not Yet Implemented**
- Creature following between rooms (they teleport but don't walk)
- Creature respawning after death
- Special attack types (poison, cave collapse, etc.)
- Shield blocking mechanics
- Medicine healing
- Vodka effects
- Arrow shooting

**Working Around**
- Creatures attack in their current room only
- Dead creatures stay dead (no respawn yet)
- All attacks are instant (no projectiles)

## Previous Updates

### Initial Release
- 157 rooms loaded
- 25 graphics converted
- Real-time multiplayer
- Movement system
- Inventory system
- Chat system
- Player stats

---

**Current Version**: 1.1.0 - Combat Update
**Server Status**: ✅ Running on http://localhost:8000
**Last Updated**: January 20, 2026
