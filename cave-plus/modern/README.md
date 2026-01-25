# Cave-Plus Web Recreation

A modern web-based multiplayer recreation of the classic BBC Micro game Cave-Plus (1988).

## 🎮 Status: FULLY PLAYABLE!

**Server**: http://localhost:8000

The game is feature-complete with authentic BBC Micro behavior, real-time multiplayer, combat, creatures, and original Teletext graphics!

## ✅ Implemented Features (41 Commands)

### Core Systems
- **Real-time Multiplayer** - WebSocket-based with instant updates
- **157 Rooms** - Complete cave system with exits
- **25 Original Graphics** - BBC Micro Teletext Mode 7 graphics (PNG)
- **Teletext Colors** - Authentic color codes preserved in room descriptions
- **Authentic BBC Micro UI** - MODE 7 terminal with Bedstead font
- **Player Persistence** - Save/load with password authentication
- **Disconnect Handling** - 5-minute timeout, reconnection support

### Movement & Exploration (6 commands)
- `n/s/e/w/u/d` - Navigate in 6 directions
- `look` - Examine current room
- Room descriptions with objects, creatures, and other players
- Graphics overlay (BBC Micro style - appears on top of scrolled text)
- Darkness system (lights off + no Crystal Ball = "It is too dark to see")

### Inventory & Objects (4 commands)
- `get/take/pickup` - Pick up items (capacity based on rank)
- `drop/leave` - Drop items
- `inventory/i` - Show inventory
- `examine` - Examine objects
- 15 unique items (Vodka, Stick, Poison, Dagger, Bow, Arrow, Medicine, Knife, Flamethrower, Ruby, Shield, Crystal Ball, Staff of Merlin, Amulet, Treasure)

### Combat System (7 commands)
- `hit/attack` - Bare hands or stick (1-6 damage)
- `stab` - Dagger/knife (21-30 damage)
- `burn` - Flamethrower (51-60 damage)
- `shoot` - Bow + arrow (31-40 damage, arrow consumed)
- `zap` - Staff of Merlin (Wizard-only, 101-140 damage, requires charges)
- `bite` - Bite target (3-6 damage vs creatures, 3-5 vs players, transfers poison)
- `poison` - Poison player with poison item (creatures thrive on it)
- PvP combat supported
- Creature aggression system (passive/aggressive states)

### Creatures & AI
- **21 Creatures** - Dragon, Troll, Spider, Snakes, Goblin, etc.
- **Intelligent AI** - Movement (walk/teleport), targeting, following
- **Attack patterns** - Hit, stab, burn, bite, shoot, zap
- **Mortuary system** - Dead creatures move to room 19
- **Activity levels** - Wizard-controlled (0-9)

### Magic & Special (4 commands)
- `teleport` - Teleport to objects/creatures (success based on rank/Shield)
- `charge` - Charge Staff of Merlin at altar (room 1)
- `drink` - Vodka (drunk typing), poison (damage over time), medicine (cure)
- `lights/power/switch` - Toggle lights in room 12 (Green room)

### Social & Communication (3 commands)
- `say/chat` - Talk to players in room
- `hello` - Broadcast greeting
- `tell` - Send private messages (Wizards can broadcast to all)
- `who/players` - List all online players
- `annoy` - Make creatures aggressive or annoy players

### Game Management (4 commands)
- `score/stats` - Show score, stamina, kills, deaths
- `deposit` - Deposit treasure at bank (room 56) for 20-40 points
- `exorcise` - Remove ghost (disconnected) players, move objects to armoury
- `quit/exit` - Save and quit (with authentic BBC Micro sequence)

### Wizard Commands (7 commands)
- `wiz` - Teleport to room 16 (Wizard's domain)
- `room <number>` - Teleport to any room
- `summon` - Summon objects/creatures/players
- `deploy` - Resurrect creatures from mortuary
- `regen` - Reset all objects and creatures
- `activity <0-9>` - Set creature activity level
- `collapse` - Kill all other players (cave collapse)

### Authentic BBC Micro Features
- **Drunk typing** - Vodka causes random typos and missed keys
- **Poison damage** - Gradual stamina loss over time (0.05 per tick)
- **Poison messages** - "I am poisoned" when stamina crosses whole number
- **Low stamina warning** - "You are almost dead" (1/20 chance when stamina < 5)
- **Stamina regeneration** - Automatic recovery (faster for Wizards)
- **Command cost** - Each command costs 0.2 stamina
- **Rank system** - New Caver → Warrior → Master Caver → Wizard
- **Death sequence** - "Life is slipping away..." with disk save
- **GOING screen** - Authentic exit screen on quit/death
- **Disk activity** - Visual indicators for save/load operations
- **Beep sounds** - VDU7 simulation for alerts
- **HELP command** - Player shouts for help (broadcasts to ALL players in game, no help text shown)
- **Invalid directions** - Random error messages: "I am sorry, but I cannot go in that direction.", "I cannot see how I can go that way."
- **Invalid commands** - Random error messages: "I don't understand", "Could you re-phrase that?"
- **EXORCISE command** - Remove ghost (disconnected) players from game
  - Wizards always succeed
  - Players with < 500 points fail ("Insufficient Experience")
  - Other players have 1/5 chance to succeed
  - Moves ghost players' objects to armoury (room 20)
  - Broadcasts "The ground trembles!!" to all players
- **FAST/SLOW commands** - Fast mode toggle (Wizard-only for FAST)
  - FAST: Skip room entry delays and graphics display for faster navigation
  - SLOW: Restore normal delays and graphics display
  - Useful for experienced players who want to move quickly through the cave
- **PACIFY command** - Make creature passive (Wizard-only, opposite of ANNOY)
  - Removes aggressive behavior from creatures
  - Cannot be used on players (shows: "SORRY- You'll have to talk/TELL [player] out of it")
  - No confirmation message shown

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Local Python

```bash
# Install dependencies
cd server
pip install -r requirements.txt

# Start server
python main.py
```

### Open in Browser

Navigate to **http://localhost:8000**

## Commands Reference

### Movement
```
n, north    - Move north
s, south    - Move south
e, east     - Move east
w, west     - Move west
u, up       - Move up
d, down     - Move down
look, l     - Look at room
```

### Objects
```
get <item>      - Pick up item
drop <item>     - Drop item
inventory, i    - Show inventory
examine <item>  - Examine item
deposit         - Deposit treasure at bank (room 56)
```

### Combat
```
hit <target>    - Attack with bare hands/stick
stab <target>   - Attack with dagger/knife
burn <target>   - Attack with flamethrower
shoot <target>  - Shoot with bow + arrow
zap <target>    - Zap with Staff of Merlin (Wizard)
bite <target>   - Bite target (transfers poison if poisoned)
poison <target> - Poison player (requires poison item)
```

### Magic
```
teleport <target>  - Teleport to object/creature
charge             - Charge Staff at altar (room 1)
drink <item>       - Drink vodka/poison/medicine
lights on/off      - Toggle lights (room 12)
```

### Social
```
say <message>      - Talk to players in room
hello              - Say hello
tell <player> <msg> - Send private message
who, players       - List all players
annoy <target>     - Make creature aggressive
```

### Information
```
score, stats    - Show your stats
who, players    - List all players
help            - Shout for help (broadcasts to all players)
exorcise        - Remove ghost (disconnected) players
fast            - Enable fast mode (Wizard-only, skip graphics/delays)
slow            - Disable fast mode
quit, exit      - Save and quit
```

### Wizard Commands
```
wiz                - Teleport to room 16
room <number>      - Teleport to room
summon <target>    - Summon object/creature/player
deploy <creature>  - Resurrect from mortuary
regen              - Reset objects/creatures
activity <0-9>     - Set creature activity
collapse           - Kill all other players
pacify <target>    - Make creature passive
```

## Testing Multiplayer

1. Open multiple browser tabs
2. Connect with different player names
3. Navigate to the same room
4. Try combat: `hit <player>` or `stab dragon`
5. Chat: `say hello everyone`
6. Check who's online: `who`

## Architecture

```
Browser (WebSocket Client)
    ↕ JSON messages
FastAPI Server (Python)
    ↕ Game state updates
Game State (Rooms, Players, Objects, Creatures)
    ↕ Async game loop (1 second tick)
Creature AI (Movement, Targeting, Attacks)
```

## Project Structure

```
modern/
├── server/
│   ├── main.py          - FastAPI WebSocket server
│   ├── game_state.py    - Game state management
│   ├── player.py        - Player class with stats
│   ├── creature.py      - Creature AI and behavior
│   ├── commands.py      - Command parser (32 commands)
│   └── player_data.py   - Save/load system
├── static/
│   ├── index.html       - Game UI (MODE 7 terminal)
│   ├── css/
│   │   ├── style.css    - BBC Micro MODE 7 styling
│   │   └── banner.css   - GOING screen styling
│   ├── js/
│   │   ├── game.js      - WebSocket client
│   │   └── banner.js    - GOING screen logic
│   ├── fonts/           - Bedstead font (BBC Micro)
│   └── graphics/        - 25 room graphics (PNG)
├── player_data/         - Saved player files (JSON)
├── rooms-parsed.yml     - 157 rooms with Teletext colors
├── requirements.txt     - Python dependencies
└── docker-compose.yml   - Docker configuration
```

## Technical Details

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time bidirectional communication
- **PyYAML** - YAML data parsing
- **Asyncio** - Asynchronous game loop (1 second tick)
- **bcrypt** - Password hashing

### Frontend
- **Vanilla JavaScript** - No frameworks
- **WebSocket API** - Real-time server communication
- **CSS Grid** - MODE 7 terminal layout (40×25 characters)
- **Bedstead Font** - Authentic BBC Micro font
- **Teletext Colors** - HTML spans with CSS color classes

### Data Format
- **YAML** - Room definitions with Teletext color markup
- **JSON** - Player save files and WebSocket messages
- **PNG** - Converted Teletext graphics (320×64 pixels)

### BBC Micro Authenticity
- **MODE 7** - Teletext display mode (40×25 characters)
- **Color codes** - 0x81-0x87 (Red, Green, Yellow, Blue, Magenta, Cyan, White)
- **VDU codes** - Beep sounds, screen control
- **ECONET** - Original multiplayer networking (recreated with WebSockets)
- **Disk timing** - Simulated disk access delays
- **GOING screen** - Authentic exit screen with banner

## Key Rooms

- **Room 1** - Main Entrance / Altar (charge Staff here)
- **Room 12** - Green Room (light switch)
- **Room 19** - Mortuary (dead creatures)
- **Room 20** - Armoury (defensive items)
- **Room 56** - Bank (deposit treasure)
- **Room 16-20** - Wizard's Domain
- **Room 72** - Hall of Knowledge (tutorial)

## Credits

- **Original Game**: GJL WOTWECP (1985), XOB (1988)
- **Platform**: BBC Micro with ECONET networking
- **Recreation**: Based on complete source code analysis
- **Graphics**: Converted from Teletext Mode 7 format
- **Font**: Bedstead by Ben Harris

## License

This is a fan recreation for educational and preservation purposes.
Original game © GJL WOTWECP 1985, XOB 1988.
