# Cave-Plus Recreation - Quick Start Guide

## Installation & Setup

### 1. Install Dependencies

The server uses a Python virtual environment to manage dependencies.

```bash
cd cave-plus/recreation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Server

**Option A: Using the start script (recommended)**
```bash
./start.sh
```

**Option B: Manually with virtual environment**
```bash
source venv/bin/activate
cd server
python3 main.py
```

### 3. Open in Browser

Navigate to: **http://localhost:8000**

The server is now running and ready for multiplayer gameplay!

## First Steps

1. **Enter your name** (2-20 characters)
2. **Click "Enter the Cave"**
3. You'll start in Room 1 (Main Entrance)

## Basic Commands

### Movement
```
n, s, e, w, u, d    - Move north, south, east, west, up, down
north, south, etc.  - Full direction names also work
```

### Looking Around
```
look    - Examine your current room
l       - Short form of look
```

### Inventory
```
inventory   - Show what you're carrying
i           - Short form
get sword   - Pick up an item
drop shield - Drop an item
```

### Social
```
say hello       - Chat with other players in the room
who             - List all online players
```

### Information
```
score   - Show your stats and score
help    - Show all available commands
```

## Tips

- **Graphics**: 25 rooms have original BBC Micro graphics that will display automatically
- **Multiplayer**: Open multiple browser tabs to test multiplayer features
- **History**: Use ↑ and ↓ arrow keys to navigate command history
- **Shortcuts**: Most commands have short forms (n for north, i for inventory, etc.)

## Troubleshooting

### Server won't start
- Make sure Python 3.8+ is installed: `python3 --version`
- Check if port 8000 is available: `lsof -i :8000`
- Try a different port: Edit `server/main.py` and change port number

### Can't connect
- Make sure the server is running
- Check browser console for errors (F12)
- Try refreshing the page

### Name already taken
- Someone else is using that name
- Choose a different name
- Or wait for them to disconnect

## Development Mode

For development with auto-reload:

```bash
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## What's Implemented

✅ **Core Features**
- Real-time multiplayer via WebSockets
- 157 interconnected rooms
- Movement system with exits
- Inventory management (get/drop items)
- Chat system (say command)
- Player stats (health, stamina, score, rank)
- Original Teletext graphics (25 rooms)
- Retro terminal UI

🚧 **Coming Soon**
- Combat system
- Creature AI
- Banking and treasure
- Special room mechanics (portcullis, light switch)
- Death and respawn
- Persistent player data

## Architecture

```
Browser (WebSocket Client)
    ↕
FastAPI Server (Python)
    ↕
Game State (Rooms, Players, Objects)
```

## File Structure

```
recreation/
├── server/
│   ├── main.py          - WebSocket server
│   ├── game_state.py    - Game state management
│   ├── player.py        - Player class
│   └── commands.py      - Command parser
├── static/
│   ├── index.html       - Game UI
│   ├── css/style.css    - Retro styling
│   └── js/game.js       - WebSocket client
└── rooms-parsed.yml     - Room data (157 rooms)
```

## Next Steps

1. **Explore the cave** - Try moving around and discovering rooms
2. **Pick up items** - Use `get` to collect objects
3. **Chat with others** - Open multiple tabs and chat between them
4. **Check the graphics** - Visit rooms 2, 16, 30, 37 for cool graphics
5. **Read the code** - See how WebSockets and game state work

## Credits

- **Original Game**: GJL WOTWECP (1985), XOB (1988)
- **Recreation**: Based on complete source code analysis
- **Graphics**: Converted from BBC Micro Teletext Mode 7

Enjoy exploring the cave! 🏰
