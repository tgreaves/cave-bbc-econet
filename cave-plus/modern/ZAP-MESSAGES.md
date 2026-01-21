# ZAP Command Messages - Implementation Notes

## Overview
The ZAP command now displays messages in two separate areas, matching the BBC Micro source code behavior.

## BBC Micro Source Code Reference
From `Cave-annotated.basic`:
- **Line 4920 (PROCG)**: Main area message - "!ZAPPING!"
- **Line 5020 (PROCB)**: Status area message - "The [creature] is !ZAPPED! stamina now [X]"

## Implementation

### Commands.py
The ZAP command returns two separate message fields:
```python
return {
    "message": "!ZAPPING!",              # Main area (PROCG)
    "status_message": "The Dragon is !ZAPPED! stamina now 45",  # Status area (PROCB)
    "combat": True,
    "creature_died": False,
    "beeps": 3
}
```

### Main.py
The server now handles both message types:
1. **message**: Sent to main display area (style determined by combat flag or explicit style)
2. **status_message**: Sent to status area (always uses "combat" style)

```python
# Send main message
if result.get("message"):
    await send_to_player(player, {
        "type": "message",
        "text": result["message"],
        "style": style,
        "beeps": beeps
    })

# Send status message separately
if result.get("status_message"):
    await send_to_player(player, {
        "type": "message",
        "text": result["status_message"],
        "style": "combat"  # Always status area
    })
```

## Message Flow
1. Player types: `ZAP DRAGON`
2. Main area displays: `!ZAPPING!` (with 3 beeps)
3. Status area displays: `The Dragon is !ZAPPED! stamina now 45`

## Notes
- Staff charges are NOT displayed in messages (as per BBC source)
- ZAP produces 3 beeps (VDU7,7,7) - the most dramatic sound effect
- Only Wizards with Staff of Merlin and charges can use ZAP
- If creature dies: status message changes to "obliterated" with points awarded
