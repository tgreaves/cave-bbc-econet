# ECONET Networking in Cave-Plus

## Overview

Cave-Plus is a multiplayer adventure game that uses **ECONET** (Acorn's local area network system) to enable real-time multiplayer gameplay across BBC Micro computers. This document explains how the networking works, the protocols used, and the data structures involved.

## What is ECONET?

ECONET was Acorn's proprietary local area network system for BBC Micro computers, introduced in 1984. It allowed up to 254 stations (computers) to communicate over a shared network using:
- **Station Numbers**: Each computer has a unique station ID (1-254)
- **Network Numbers**: Networks could be interconnected
- **Port Numbers**: Different services use different ports (like TCP/IP ports)

## Network Architecture

### Station Identification

Each player's BBC Micro has a unique station number stored at memory location `&D22`:
```basic
MyStat = ?&D22    ' Read station number from OS
```

The game uses station numbers to:
1. Identify players uniquely
2. Route messages between players
3. Track which player is in which room

### Memory Layout

```
&7900-&7BFF  Machine code routines for ECONET operations
&7A38 (I)    Local station ID storage
&7A39 (a)    Message buffer pointer
&7981 (q)    Queue pointer for outgoing messages
&7991 (r)    Network routine for checking connections
&795B (y)    Send message routine
&79E2 (e)    Error/status byte
&79F8 (CA)   Cave address

&900-&9FF    Player table (16 bytes per player, up to 16 players)
&A00-&AFC    Object/creature table (4 bytes per object, 42 objects)
```

## Player Table Structure

Each player occupies 16 bytes in the player table (&900-&9F0):

```
Offset  Size  Description
------  ----  -----------
+0      8     Player name (string)
+8      1     Station number (which computer they're on)
+9      1     Current room number
+10     2     Reserved
+12     4     Current stamina (health)
```

Example for player at &910:
```
&910-&917: "WIZARD  "  (name, 8 chars)
&918:      42          (station number)
&919:      15          (room 15)
&91C:      150         (150 stamina)
```

## Machine Code Network Routines

The game uses three main machine code routines defined in MC.basic:

### 1. Find Routine (&7900 + offset)

**Purpose**: Scans the network to find all active Cave players

**How it works**:
1. Iterates through station numbers 1-254
2. Sends a "ping" packet to each station
3. Looks for response containing "CAV" signature
4. Updates `Stat` variable with count of found players

**ECONET Operation**: Uses OSWORD &81 (Peek operation)
```assembly
LDA #&81        ; OSWORD 81 = Peek
STA FindBLK
LDA #&10        ; Control block size
LDX #FindBLK MOD 256
LDY #FindBLK DIV 256
JSR &FFF1       ; Call OSWORD
```

### 2. Peek Routine

**Purpose**: Reads player data from remote stations

**How it works**:
1. Calls Find to locate active players
2. For each found station, reads memory &908-&AFF
3. This range contains player name, position, and stamina
4. Updates local player table with remote data

**ECONET Operation**: Uses OSWORD &81 (Peek) to read remote memory
```assembly
EQUB &81        ; Peek operation
EQUB 0          ; Port number
EQUW 0          ; Station number (filled in)
EQUD &908       ; Start address on remote machine
EQUD &AFF       ; End address on remote machine
EQUD &908       ; Local destination address
```

### 3. Poke Routine

**Purpose**: Writes local player data to remote stations

**How it works**:
1. Broadcasts current player state to all other stations
2. Updates remote player tables with local player's position/stamina
3. Called whenever player moves or takes damage

**ECONET Operation**: Uses OSWORD &82 (Poke) to write remote memory
```assembly
EQUB &82        ; Poke operation
EQUB 0          ; Port number
EQUW 0          ; Station number (filled in)
EQUD SBLK       ; Start of data to send
EQUD SBLK+&F0   ; End of data to send
EQUD &7700      ; Destination address on remote machine
```

## High-Level Network Functions

### PROCA(w, HA) - Broadcast Data

**Location**: Line 6240  
**Purpose**: Broadcasts a block of memory to all connected players

```basic
DEFPROCA(w,HA)
  !(K+4)=w      ' Start address
  !(K+8)=HA     ' End address
  !(K+12)=w     ' Destination address
  CALLp         ' Call Poke routine
ENDPROC
```

**Usage Examples**:
```basic
PROCA(A,A+15)              ' Broadcast player record
PROCA(&A00,&AFF)           ' Broadcast all objects
PROCA(&7700,&77FE)         ' Broadcast message
```

### PROCC(CO, v, S$) - Send Message

**Location**: Line 6170  
**Purpose**: Sends a text message to a specific station

```basic
DEFPROCC(CO,v,S$)
  IFv<1ORv>253ENDPROC      ' Validate station number
  ?a=CO                     ' Command code
  ?(a+1)=?I                 ' Sender station
  $(a+2)=S$                 ' Message text
  ?(q+2)=v                  ' Destination station
  CALLy                     ' Call send routine
ENDPROC
```

**Command Codes**:
- 1 = General message
- 2 = Hit notification
- 5 = Poison notification
- 6 = Stab notification
- 7 = Force command failed
- 8 = Summon object
- 9 = Force command
- 10 = Bite notification
- 11 = Burn notification
- 12 = Zap notification
- 13 = Shoot notification

### PROCD(CO, RO, S$) - Broadcast to Room

**Location**: Line 5100  
**Purpose**: Sends message to all players in a specific room

```basic
DEFPROCD(CO,RO,S$)
  FORN=&910TO&9F0STEP&10
    IF?N<>0AND$N<>E$AND(!(N+8)DIV&100)=RO
      PROCC(CO,?(N+8),S$)  ' Send to each player in room
    ENDIF
  NEXT
ENDPROC
```

## Network Synchronization

### Lock File System

To prevent race conditions during login, Cave uses a file-based lock:

```basic
670 QQ=OPENIN"LOCK"
680 IFQQ<>0CLOSE#QQ:PRINT".";:A$=INKEY$100:GOTO670  ' Wait for lock
690 *SA."LOCK"0 0                                    ' Create lock file
...
780 *DELETE LOCK                                     ' Release lock
```

This ensures only one player can modify the player table at a time.

### Player Table Synchronization

When a player joins:
1. **Lock** the player table
2. **Find** all active players (CALLr)
3. **Check** for duplicate names/stations
4. **Allocate** a slot in the player table
5. **Broadcast** new player data (PROCA)
6. **Release** the lock

### Real-Time Updates

During gameplay, the game continuously:
1. **Broadcasts** player position when moving (line 1010)
2. **Broadcasts** stamina changes when damaged
3. **Receives** updates from other players via Peek
4. **Displays** other players in the same room (PROCL)

## Message Types and Flow

### 1. Movement Announcements

When a player moves rooms:
```basic
' Announce arrival in new room
PROCC(1,?(T+8),E$+" has arrived.")

' Announce departure from old room  
PROCC(1,?(T+8),E$+" has just left.")
```

### 2. Combat Messages

When attacking another player:
```basic
' Notify victim of hit
PROCC(2,?(T+8),CHR$(damage)+attacker_name)

' Notify room of combat
PROCD(1,B,E$+" IS HIT! stamina down to "+STR$(INTD))
```

### 3. Object Interactions

When summoning an object:
```basic
' Tell object owner to drop it
PROCC(8,?(T+8),CHR$B)  ' B = destination room
```

### 4. Force Commands

Wizards can force other players to execute commands:
```basic
' Send forced command
$(a+&40)=C$              ' Command
$(a+&80)=D$              ' Parameter
PROCC(9,?(T+8),I$)       ' Send to victim
```

## Ghost Detection and Cleanup

The EXORCISE command removes "ghost" players (disconnected but still in table):

```basic
3060 ?e=?(T+8)-1:CALLr   ' Check if station still responds
3060 IF?e<>?(T+8)?T=0    ' If no response, clear player slot
```

This uses the Find routine to verify each station is still active.

## Network Performance

### Bandwidth Considerations

- **Player updates**: ~16 bytes per player, broadcast on movement
- **Object updates**: ~4 bytes per object, broadcast on state change
- **Messages**: Variable length, sent point-to-point
- **Typical game**: 4-8 players, ~50-100 bytes/second per player

### Latency

ECONET was relatively slow by modern standards:
- **Speed**: 200-250 Kbps (kilobits per second)
- **Latency**: 10-50ms on local network
- **Packet size**: Typically 128-256 bytes

The game minimizes network traffic by:
1. Only broadcasting changes (not full state)
2. Using compact binary formats
3. Sending messages only to affected players

## Network Initialization Sequence

```
1. *NET                          ' Enable ECONET
2. *FX 200 1                     ' Set ECONET escape action
3. Read station ID from &D22     ' Get local station number
4. Initialize machine code       ' Setup Poke/Peek/Find routines
5. Wait for LOCK file            ' Synchronize with other players
6. CALLr (Find)                  ' Scan for active players
7. Allocate player slot          ' Find empty slot in table
8. PROCA(A,A+15)                 ' Broadcast player data
9. Delete LOCK                   ' Release synchronization lock
10. Enter game loop              ' Begin gameplay
```

## Error Handling

### Network Errors

The game handles several network error conditions:

1. **Station not responding**: Detected during Peek/Poke operations
   ```basic
   TXA
   AND#&80      ' Check error bit
   BNE retry    ' Retry if error
   ```

2. **Duplicate player**: Checked during login
   ```basic
   IF$T=E$OR(?T<>0AND?(T+8)=?I)
     PRINT"You are already in the CAVE!!!"
   ```

3. **Cave full**: All 16 player slots occupied
   ```basic
   IFT>&9F0PRINT"CAVE FULL"
   ```

### Recovery Mechanisms

- **Automatic retry**: Poke/Peek operations retry on timeout
- **Ghost cleanup**: EXORCISE command removes dead connections
- **Lock timeout**: Lock file prevents indefinite hangs

## Security Considerations

### Cheating Prevention

The game has minimal cheat prevention:
- **Checksum**: Player files have checksums (line 590)
- **Score limit**: Scores over 4000 are deleted (line 610)
- **Wizard domain**: Rooms 16-20 protected from non-wizards

### Vulnerabilities

As a 1980s game, Cave-Plus has several exploitable issues:
1. **Memory peeking**: Players can read other players' memory
2. **Memory poking**: Players can write to other players' memory
3. **No authentication**: Station numbers are trusted
4. **No encryption**: All data sent in plaintext

These were acceptable in the trusted environment of a school network.

## Example Network Scenarios

### Scenario 1: Player Joins Game

```
Station 42 (WIZARD):
1. Opens LOCK file
2. Calls Find routine
3. Finds stations: 23, 35, 42
4. Allocates slot at &920
5. Writes: "WIZARD  " + 42 + 70 + 150
6. Broadcasts to all stations
7. Deletes LOCK file

Station 23 (GOBLIN):
1. Receives Poke from station 42
2. Updates &920 with WIZARD's data
3. Displays "WIZARD has arrived" (if in same room)
```

### Scenario 2: Combat Between Players

```
Station 42 (WIZARD) attacks Station 23 (GOBLIN):

1. WIZARD: Calculates damage (10 points)
2. WIZARD: PROCC(2,23,CHR$(10)+"WIZARD")
3. Station 23 receives message
4. GOBLIN: Reduces stamina by 10
5. GOBLIN: Broadcasts updated stamina
6. GOBLIN: Displays "You are HIT by WIZARD"
7. All players in room see: "GOBLIN IS HIT!"
```

### Scenario 3: Object Summoning

```
Station 42 (WIZARD) summons Staff from Station 23:

1. WIZARD: Finds Staff at station 23
2. WIZARD: PROCC(8,23,CHR$42)  ' Summon to room 42
3. Station 23 receives summon command
4. GOBLIN: Moves Staff to room 42
5. GOBLIN: Broadcasts object update
6. WIZARD: Sees "The Staff appears!"
```

## Debugging Network Issues

### Useful Commands

- **USERS/CAVERS**: Lists all connected players
- **EXORCISE**: Removes ghost players
- **ACTIVITY**: Sets creature activity level (affects network load)

### Common Problems

1. **"CAVE FULL"**: Too many players (max 16)
   - Solution: Wait for someone to quit

2. **"Already in CAVE"**: Duplicate login detected
   - Solution: EXORCISE to clear ghost, then rejoin

3. **Lock file stuck**: LOCK file not deleted
   - Solution: Manually delete LOCK file from file server

4. **Invisible players**: Player table out of sync
   - Solution: EXORCISE to resynchronize

## Technical Specifications

### ECONET OSWORD Calls

The game uses these BBC Micro OSWORD calls:

**OSWORD &81 (Peek)**
```
Control Block:
  +0: &81 (operation)
  +1: Port number
  +2: Station number (2 bytes)
  +4: Remote start address (4 bytes)
  +8: Remote end address (4 bytes)
  +12: Local destination (4 bytes)
```

**OSWORD &82 (Poke)**
```
Control Block:
  +0: &82 (operation)
  +1: Port number
  +2: Station number (2 bytes)
  +4: Local start address (4 bytes)
  +8: Local end address (4 bytes)
  +12: Remote destination (4 bytes)
```

**OSBYTE &32 (Poll for completion)**
```
Returns:
  X bit 7: Error flag
  X bit 6: Retry flag
```

### Memory Map Summary

```
&0070-&0071   Temporary pointer for network operations
&0287-&0289   Jump vector for network routines
&0900-&09FF   Player table (16 players × 16 bytes)
&0A00-&0AFC   Object table (42 objects × 4 bytes)
&0D22         Station number (OS variable)
&7700-&77FF   Message buffer
&7800-&7BFF   Machine code routines
&7900         Poke routine entry point
&7991         Find routine entry point
&795B         Send message routine entry point
```

## Conclusion

Cave-Plus demonstrates sophisticated use of ECONET for real-time multiplayer gaming on 1980s hardware. The combination of:
- Memory-mapped player tables
- Broadcast updates for state changes
- Point-to-point messages for interactions
- Lock-based synchronization

...creates a surprisingly robust multiplayer experience, allowing up to 16 players to explore the cave simultaneously, interact with each other, and compete for treasure.

The networking code is a testament to the ingenuity of 1980s programmers working within severe hardware constraints (1-2 MHz CPU, 32KB RAM, 250 Kbps network) to create engaging multiplayer experiences.

---

**References**:
- Cave.basic (main game code)
- MC.basic (machine code network routines)
- BBC Micro Advanced User Guide (ECONET chapter)
- Acorn ECONET System User Guide
