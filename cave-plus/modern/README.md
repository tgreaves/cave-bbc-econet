# Cave-Plus Web Recreation

A modern web-based multiplayer recreation of the classic BBC Micro game Cave-Plus.

## 🎮 Status: PLAYABLE!

**Server is running**: http://localhost:8000

The core game is fully functional with real-time multiplayer, room navigation, inventory system, and original graphics!

## ✅ Implemented Features

- **Real-time Multiplayer** - WebSocket-based multiplayer with instant updates
- **157 Rooms** - Complete cave system from the original game
- **25 Original Graphics** - BBC Micro Teletext Mode 7 graphics converted to PNG
- **Retro Terminal UI** - Green-on-black CRT aesthetic
- **Movement System** - Navigate in 6 directions (N/S/E/W/U/D)
- **Inventory System** - Pick up and drop items (10 item limit)
- **Chat System** - Talk to other players in the same room
- **Player Stats** - Health, stamina, score, rank tracking
- **Command History** - Arrow keys to navigate previous commands

## 🚧 Coming Soon

- Combat system (attack/defend)
- Creature AI (movement and attacks)
- Special rooms (portcullis, light switch, bank)
- Death and respawn
- Persistent player data

## Quick Start

### 1. Install Dependencies

```bash
cd cave-plus/recreation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Server

```bash
./start.sh
```

Or manually:
```bash
source venv/bin/activate
cd server
python3 main.py
```

### 3. Open in Browser

Navigate to **http://localhost:8000**

## Commands

### Movement
- `n`, `s`, `e`, `w`, `u`, `d` - Move north, south, east, west, up, down

### Objects
- `get <item>` - Pick up an item
- `drop <item>` - Drop an item
- `inventory` or `i` - Show inventory
- `look` or `l` - Examine current room

### Social
- `say <message>` - Chat with other players in the room
- `who` - List all online players

### Information
- `score` - Show your stats (health, stamina, kills, deaths)
- `help` - Show available commands

## Testing Multiplayer

1. Open multiple browser tabs
2. Connect with different player names
3. Move to the same room
4. Chat with `say hello`
5. Pick up and drop items
6. Use `who` to see all players

## Architecture

```
Browser (WebSocket Client)
    ↕ JSON messages
FastAPI Server (Python)
    ↕ Game state updates
Game State (Rooms, Players, Objects)
```

## Project Structure

```
recreation/
├── server/
│   ├── main.py          - FastAPI WebSocket server
│   ├── game_state.py    - Game state management
│   ├── player.py        - Player class
│   └── commands.py      - Command parser
├── static/
│   ├── index.html       - Game UI
│   ├── css/style.css    - Retro terminal styling
│   └── js/game.js       - WebSocket client
├── venv/                - Python virtual environment
├── rooms-parsed.yml     - 157 rooms data
├── requirements.txt     - Python dependencies
└── start.sh            - Startup script
```

## Documentation

- **QUICKSTART.md** - Setup and installation guide
- **STATUS.md** - Detailed implementation status
- **TESTING.md** - Testing guide and checklist
- **COMPLETED.md** - Summary of achievements

## Technical Details

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time bidirectional communication
- **PyYAML** - YAML data parsing
- **Asyncio** - Asynchronous game loop

### Frontend
- **Vanilla JavaScript** - No frameworks, pure JS
- **WebSocket API** - Real-time server communication
- **CSS Grid** - Responsive layout
- **Retro Styling** - CRT terminal aesthetic

### Data Format
- **YAML** - Room definitions and game data
- **PNG** - Converted Teletext graphics
- **JSON** - WebSocket message protocol

## Credits

- **Original Game**: GJL WOTWECP (1985), XOB (1988)
- **Platform**: BBC Micro with ECONET networking
- **Recreation**: Based on complete source code analysis
- **Graphics**: Converted from Teletext Mode 7 format

## License

This is a fan recreation for educational and preservation purposes.
Original game © GJL WOTWECP 1985, XOB 1988.
