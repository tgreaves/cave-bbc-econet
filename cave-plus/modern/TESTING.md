# Testing the Cave-Plus Recreation

## Quick Test

The server is currently running! You can test it right now:

1. **Open your browser** to: http://localhost:8000
2. **Enter a player name** (2-20 characters)
3. **Click "Enter the Cave"**

You should see:
- Welcome message
- Room 1 description (Main Entrance)
- Available exits
- Command prompt

## Basic Testing Checklist

### ✅ Connection Test
- [ ] Open http://localhost:8000
- [ ] Enter name and connect
- [ ] See welcome message
- [ ] See Room 1 description

### ✅ Movement Test
```
n     - Move north (should work)
s     - Move south (should work)
e     - Try east (may not have exit)
look  - Re-examine current room
```

### ✅ Inventory Test
```
look              - See what objects are in room
get staff         - Pick up Staff of Merlin
inventory         - Check your inventory
drop staff        - Drop the staff
look              - Verify it's back in the room
```

### ✅ Multiplayer Test
1. Open a **second browser tab** (or incognito window)
2. Connect with a **different name**
3. In tab 1, type: `say hello`
4. In tab 2, you should see: "Player1 says: hello"
5. Try moving between rooms and see each other

### ✅ Graphics Test
Visit these rooms to see original BBC Micro graphics:
```
From Room 1:
n     - Room 2 (has graphic)
s     - Room 3 (has graphic)
```

Other rooms with graphics:
- Room 9, 11, 12, 13, 16, 17, 18, 19, 20
- Room 25, 29, 30, 32, 37, 49, 50, 51
- Room 55, 60, 99, 141, 148, 150

### ✅ Command Test
```
help      - Show all commands
who       - List online players
score     - Show your stats
i         - Short for inventory
l         - Short for look
```

## Advanced Testing

### Test Multiple Players
1. Open 3-4 browser tabs
2. Connect with different names
3. All move to the same room
4. Chat with `say` command
5. Pick up and drop items
6. Use `who` to see all players

### Test Edge Cases
```
# Try invalid commands
xyz           - Should show "Unknown command"

# Try invalid movement
u             - Try going up (no exit in Room 1)

# Try invalid items
get banana    - Should say "There is no 'banana' here"

# Try full inventory
get item1
get item2
... (repeat 10 times)
get item11    - Should say "You can't carry any more"
```

### Test Disconnection
1. Connect with a player
2. Close the browser tab
3. In another tab, use `who` command
4. Disconnected player should be gone

## Performance Testing

### Load Test
Open 10+ browser tabs and connect simultaneously. Server should handle all connections without crashing.

### Stress Test
Have multiple players:
- Moving rapidly between rooms
- Picking up and dropping items
- Sending chat messages
- All at the same time

## Known Limitations (Expected Behavior)

1. **No Combat** - You can't attack creatures yet
2. **Static Creatures** - Creatures don't move or attack
3. **No Death** - Health decreases but you can't die
4. **No Persistence** - Restart server = reset game
5. **No Special Rooms** - Portcullis, light switch don't work yet

## Debugging

### Check Server Logs
The server terminal shows all activity:
- Player connections/disconnections
- Commands executed
- Errors and warnings

### Browser Console
Press F12 to open developer tools:
- Check Console tab for JavaScript errors
- Check Network tab for WebSocket connection
- Should see "Connected to Cave-Plus server!" message

### Common Issues

**Can't connect:**
- Check server is running: `ps aux | grep python`
- Check port 8000 is available: `lsof -i :8000`
- Try refreshing the page

**Name already taken:**
- Someone else is using that name
- Try a different name
- Or close all tabs and reconnect

**Graphics not showing:**
- Check browser console for 404 errors
- Verify graphics directory exists: `ls ../analysed/graphics/`
- Only 25 rooms have graphics

**Commands not working:**
- Check spelling and syntax
- Type `help` to see available commands
- Check server logs for errors

## Success Criteria

The recreation is working correctly if:

✅ Server starts without errors
✅ Browser connects via WebSocket
✅ Can move between rooms
✅ Can pick up and drop items
✅ Multiple players can connect
✅ Players can see each other
✅ Chat system works
✅ Graphics display in correct rooms
✅ Command history works (arrow keys)
✅ Server handles disconnections gracefully

## Next Steps After Testing

Once basic functionality is confirmed:

1. **Add Combat System** - Implement attack/defend
2. **Add Creature AI** - Make creatures move and attack
3. **Add Special Rooms** - Portcullis, light switch, etc.
4. **Add Persistence** - Save player data
5. **Add More Features** - Banking, quests, etc.

## Reporting Issues

If you find bugs:
1. Note the exact steps to reproduce
2. Check server logs for error messages
3. Check browser console for errors
4. Document expected vs actual behavior

## Have Fun!

The game is fully playable for exploration and multiplayer chat. Enjoy discovering all 157 rooms and finding the 25 rooms with original graphics!

---

**Current Server Status**: ✅ Running on http://localhost:8000
**Players Online**: Check with `who` command
**Rooms Available**: 157
**Graphics Available**: 25
