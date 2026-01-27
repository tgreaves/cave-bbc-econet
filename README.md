# Cave-Plus Web Recreation

Cave (and later Cave-Plus) were MUDs for the [BBC Micro](https://en.wikipedia.org/wiki/BBC_Micro), initially released back in 1985.

This is a modern-day recreation with authentic BBC Micro behavior, real-time multiplayer, combat, creatures, and original MODE 7 graphics!

I previously made a telnet recreation using the Ranvier MUD engine, and that can be found here: https://github.com/tgreaves/ranviermud-cave 

---

## Play it RIGHT NOW

http://cave.extricate.org:1985

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build the image
docker build -t cave-bbc-econet:latest .

# Or use docker-compose to build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Local Python

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python server/main.py
```

### Open in Browser

Navigate to **http://localhost:8000**

---

## Game Features

### Core Systems
- **Real-time Multiplayer** - WebSocket-based with instant updates
- **157 Rooms** - Complete cave system with directional exits
- **25 Original Graphics** - BBC Micro Teletext Mode 7 graphics (PNG)
- **Teletext Colors** - Authentic color codes preserved in room descriptions
- **Authentic BBC Micro UI** - MODE 7 terminal with Bedstead font
- **Player Persistence** - Save/load with password authentication
- **Disconnect Handling** - 5-minute timeout, reconnection support
- **Interactive Map** - Real-time dungeon map with player position tracking

### Creatures & AI
- **21 Creatures** - Dragon, Troll, Spider, Snakes, Goblin, Author, Wizard, etc.
- **Intelligent AI** - Movement (walk/teleport), targeting, following
- **Attack Patterns** - Hit, stab, burn, bite, shoot, zap
- **Mortuary System** - Dead creatures move to room 19
- **Activity Levels** - Wizard-controlled aggression (0-9)

### Items & Objects
15 unique items with special properties:
- **Weapons**: Stick, Dagger, Knife, Bow, Arrow, Flamethrower
- **Magic Items**: Crystal Ball, Staff of Merlin, Amulet, Shield, Guardian, Ruby
- **Consumables**: Vodka, Poison, Medicine
- **Treasure**: Deposit at bank for points

---

## Complete Command Reference (44 Commands)

### Movement (9 commands)
```
n, north           - Move north
s, south           - Move south
e, east            - Move east
w, west            - Move west
u, up              - Move up
d, down            - Move down
go <direction>     - Alternative movement (e.g., GO NORTH)
walk <direction>   - Alternative movement (e.g., WALK EAST)
run <direction>    - Alternative movement (e.g., RUN SOUTH)
```

### Exploration (2 commands)
```
look, l            - Examine current room
examine <item>     - Examine an object
```

### Inventory (3 commands)
```
get/take/pickup <item>  - Pick up item (capacity based on rank)
drop/leave <item>       - Drop item
inventory, i, inv       - Show inventory
```

### Combat (7 commands)
```
hit/attack/fight <target>  - Attack with bare hands/stick (1-6 damage)
stab <target>              - Attack with dagger/knife (21-30 damage)
burn <target>              - Attack with flamethrower (51-60 damage)
shoot <target>             - Shoot with bow + arrow (31-40 damage, arrow consumed)
zap/staff <target>         - Zap with Staff of Merlin (Wizard-only, 101-140 damage)
bite <target>              - Bite target (3-6 damage, transfers poison)
poison <target>            - Poison player with poison item
```

### Magic & Special (5 commands)
```
teleport/tele <target>     - Teleport to object/creature (success based on rank/Ruby)
charge                     - Charge Staff of Merlin at altar (room 1)
drink <item>               - Drink vodka/poison/medicine
lights/power/switch        - Toggle lights in room 12 (Green room)
view <target>              - Use Crystal Ball to view remote location
```

### Social & Communication (6 commands)
```
say/chat/talk <message>    - Talk to players in room
hello                      - Broadcast greeting to room
tell <player> <message>    - Send private message (Wizards can broadcast to all)
who/players/list           - List all online players
annoy <target>             - Make creature aggressive or annoy player
help/commands/?            - Shout for help (broadcasts to all players)
```

### Game Management (5 commands)
```
score/stats/status         - Show score, stamina, rank
deposit                    - Deposit treasure at bank (room 56) for 20-40 points
exorcise                   - Remove ghost (disconnected) players
pull                       - Pull rope to raise portcullis (rooms 29/30)
quit/exit                  - Save and quit
```

### System (3 commands)
```
fast                       - Enable fast mode (Wizard-only, skip graphics/delays)
slow                       - Disable fast mode
debug                      - Easter egg command
```

### Wizard Commands (9 commands)
```
wiz                        - Teleport to room 16 (Wizard's domain)
room <number>              - Teleport to any room number
summon <target>            - Summon object/creature/player to your location
deploy <creature>          - Resurrect creature from mortuary to your room
regen                      - Reset all objects and creatures to initial state
activity <0-9>             - Set creature activity level (0=passive, 9=max aggression)
collapse                   - Trigger cave collapse (kills all other players)
pacify <target>            - Make creature passive (opposite of ANNOY)
force <target>             - Force another player to execute a command
```

### Admin Commands (1 command)
```
setscore <player> <score>  - Set player's score (updates rank/stamina immediately)
```

**Note**: Admin commands require the player to be listed in `config.json` admins list.

---

## Server Administration

### Configuration File (`config.json`)

The server uses a JSON configuration file for administrative settings:

```json
{
  "admins": [
    "PLAYERNAME1",
    "PLAYERNAME2"
  ],
  "map_available": true,
  "version": "1.1.0"
}
```

**Configuration Options:**

- **`admins`** (array of strings) - List of player names with admin privileges
  - Admin privileges include:
    - Use `SETSCORE` command to modify any player's score
    - Use `ZAP` command without Staff of Merlin (unlimited charges)
    - Teleport to magic objects and Treasure (bypasses restrictions)
  - Player names must be uppercase (e.g., "MEWCENARY")
  
- **`map_available`** (boolean) - Controls map button visibility
  - `true` - MAP button visible to all players
  - `false` - MAP button hidden
  - Changes require server restart
  
- **`version`** (string) - Server version displayed on login screen

### Admin Dashboard

Access the admin dashboard at **http://localhost:8000/admin**

**Features:**
- Real-time game state monitoring
- View all players, objects, and creatures
- Environment controls (lights, portcullis, activity level, staff charges)
- Kick players from the game
- Requires admin credentials (player login + password)

### SETSCORE Command

Admin-only command to modify player scores:

```bash
# Format
SETSCORE <playername> <score>

# Example
SETSCORE FOOBAR 1500
```

**Effects:**
- Updates player's score immediately
- Recalculates rank based on new score
- Recalculates max stamina based on new rank
- Sets current stamina to max
- Sends real-time update to connected players
- Works on any player in the game (including the admin themselves)

**Rank Thresholds:**
- Novice: 0-49 points
- Adventurer: 50-199 points
- Warrior: 200-499 points
- Master Caver: 500-999 points
- Wizard: 1000+ points

### Player Data Tool

Use the `player_data_tool.py` script to manage player data files offline:

```bash
# Show player information
python scripts/player_data_tool.py show player_data/PLAYERNAME.json

# Set player score (rank calculated automatically)
python scripts/player_data_tool.py set-score player_data/PLAYERNAME.json 1000

# Set player room
python scripts/player_data_tool.py set-room player_data/PLAYERNAME.json 16

# Fix checksum and clean up file
python scripts/player_data_tool.py fix-checksum player_data/PLAYERNAME.json
```

**Player Data Format:**

Player files are stored in `player_data/` as JSON with only essential fields:
```json
{
  "name": "PLAYERNAME",
  "score": 1000,
  "room_id": 1,
  "password_hash": "...",
  "checksum": "..."
}
```

**Note**: Rank, stamina, inventory, kills, and deaths are calculated/reset on login.

---

## Key Locations

- **Room 1** - Main Entrance / Altar (charge Staff of Merlin here)
- **Room 12** - Green Room (light switch)
- **Room 16-20** - Wizard's Domain (restricted to Wizards)
- **Room 19** - Mortuary (dead creatures)
- **Room 20** - Armoury (defensive items)
- **Room 29-30** - Portcullis (use PULL command)
- **Room 56** - Bank (deposit treasure for points)
- **Room 72** - Hall of Knowledge (tutorial)

---

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

### Project Structure

```
cave-plus-web/
├── server/
│   ├── main.py          - FastAPI WebSocket server
│   ├── game_state.py    - Game state management
│   ├── player.py        - Player class with stats
│   ├── creature.py      - Creature AI and behavior
│   ├── commands.py      - Command parser (44 commands)
│   ├── player_data.py   - Save/load system
│   └── admin.py         - Admin dashboard backend
├── static/
│   ├── index.html       - Game UI (MODE 7 terminal)
│   ├── admin.html       - Admin dashboard
│   ├── map.html         - Interactive dungeon map
│   ├── css/             - BBC Micro MODE 7 styling
│   ├── js/              - WebSocket clients
│   ├── fonts/           - Bedstead font (BBC Micro)
│   └── graphics/        - 25 room graphics (PNG)
├── player_data/         - Saved player files (JSON)
├── config.json          - Server configuration
├── rooms-parsed.yml     - 157 rooms with Teletext colors
├── requirements.txt     - Python dependencies
├── Dockerfile           - Docker image definition
├── docker-compose.yml   - Docker orchestration
├── scripts/             - Utility scripts
│   ├── player_data_tool.py  - Manage player data offline
│   ├── parse_rooms.py       - Parse room files
│   └── teletext_to_png.py   - Convert graphics
└── original/            - Original BBC Micro files
    ├── cave/            - Original CAVE game
    └── cave-plus/       - Original CAVE-PLUS game
```

---

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
- **Color Codes** - 0x81-0x87 (Red, Green, Yellow, Blue, Magenta, Cyan, White)
- **VDU Codes** - Beep sounds, screen control
- **ECONET** - Original multiplayer networking (recreated with WebSockets)
- **Disk Timing** - Simulated disk access delays with authentic sounds
- **GOING Screen** - Authentic exit screen with banner

---

## Credits

- **Original Game**: GJL WOTWECP (1985), XOB (1988)
- **Platform**: BBC Micro with ECONET networking
- **Recreation**: Based on complete source code analysis
- **Graphics**: Converted from Teletext Mode 7 format
- **Font**: Bedstead by Ben Harris
- **Modern Version**: Tristan Greaves (2026)

