# Disconnect Grace Period & Reconnection

## Overview
Players who lose their WebSocket connection remain in the game for 5 minutes, allowing them to reconnect without losing progress.

## How It Works

### When a Player Disconnects
1. Player is marked as `is_disconnected = True`
2. Disconnect timestamp is recorded
3. WebSocket reference is cleared
4. Player remains in the game world:
   - Still visible to other players
   - Still vulnerable to creature attacks
   - Still occupies their room
5. Other players see: "{player} has lost connection (still in cave)."

### During Disconnection
- Player continues to exist in the game
- Creatures can still attack them
- Vodka/poison effects continue
- If killed while disconnected, normal death sequence occurs
- After 5 minutes, player is auto-saved and removed

### Reconnection Flow
1. Player reconnects with same credentials (name + password)
2. Server detects existing disconnected player
3. Player object is reused (no data loss)
4. New WebSocket is attached
5. Player sees: "Reconnected! You are still in the cave."
6. Other players see: "{player} has reconnected."
7. Current room state is sent to player

### Timeout (5 minutes)
1. Game loop checks for expired timeouts every tick
2. Player data is auto-saved
3. Player is removed from game
4. Other players see: "{player} has been removed from the cave (timeout)."

## Implementation Details

### Player Class (`player.py`)
- `is_disconnected`: Boolean flag
- `disconnect_time`: Timestamp when disconnected
- `disconnect_timeout`: 300 seconds (5 minutes)
- `mark_disconnected()`: Called on disconnect
- `reconnect(websocket)`: Called on reconnection
- `is_timeout_expired()`: Checks if 5 minutes have passed

### Main Server (`main.py`)
- Game loop checks for timeouts every tick
- WebSocket handler detects reconnection attempts
- Reuses existing player object on reconnection
- Announces disconnect/reconnect to other players

## Edge Cases Handled
- Player tries to reconnect after timeout: Normal login (loads from disk)
- Player tries to connect while already connected: Error message
- Player dies while disconnected: Normal death sequence
- Multiple disconnect/reconnect cycles: Works correctly

## Testing
1. Connect as a player
2. Close browser/tab (disconnect)
3. Wait a few seconds
4. Reconnect with same credentials
5. Should see "Reconnected!" message and be in same room

## Future Enhancements
- Show disconnected players in WHO list with marker
- Configurable timeout duration
- Admin command to force-disconnect players
- Reconnection token for faster auth
