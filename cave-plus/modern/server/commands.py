"""
Command Parser for Cave-Plus

IMPLEMENTED COMMANDS (33 total):
=================================
Movement (6):
  N/NORTH, S/SOUTH, E/EAST, W/WEST, U/UP, D/DOWN - Move in a direction

Interaction (12):
  LOOK/L          - Look at current room
  GET/TAKE/PICKUP - Pick up an object (prevents picking up creatures)
  DROP/LEAVE      - Drop an object
  INVENTORY/I/INV - Show inventory
  SAY/CHAT/TALK   - Say something to players in room
  HELLO           - Say hello (broadcasts "PlayerName says HELLO!" to room)
  KILL            - Shows message "Life is not that simple...try HIT"
  EXAMINE         - Examine an object (shows "You see nothing special")
  DEPOSIT         - Deposit treasure at bank (room 56) for 20-40 points
  TELL            - Send message to specific player or all (Wizard only for all)
  ANNOY           - Make creature aggressive or annoy a player
  PULL            - Pull rope to raise portcullis (rooms 29/30, auto-lowers after 10 seconds)
  
Combat (7):
  HIT/ATTACK/FIGHT - Attack with bare hands or stick
  STAB            - Attack with dagger/knife
  BURN            - Attack with flamethrower
  SHOOT           - Attack with arrow
  ZAP/STAFF       - Wizard-only: Attack with Staff of Merlin (requires wizard rank, staff + charges)
  BITE            - Bite target (3-6 damage, transfers poison if you're poisoned)
  POISON          - Poison a player (requires poison item, creatures thrive on it)

Magic/Special (4):
  TELEPORT/TELE   - Teleport to an object or creature (success based on rank, score, Shield)
  CHARGE          - Charge Staff of Merlin at altar (room 1)
  DRINK           - Drink vodka, poison, or medicine
  LIGHTS/POWER/SWITCH - Toggle lights on/off (room 12 only)
  
Information (3):
  SCORE/STATS/STATUS - Show score and stamina
  WHO/PLAYERS/LIST   - List all players in game
  HELP/COMMANDS/?    - Show help

System (1):
  QUIT/EXIT       - Save and quit game

Wizard-Only Commands (7):
  WIZ             - Teleport to room 16 (Wizard's domain)
  ROOM <number>   - Teleport to specific room number (e.g., ROOM 21)
  SUMMON <target> - Summon object or creature to your location
  DEPLOY <target> - Resurrect creature from mortuary to your room
  REGEN           - Reset all objects and creatures to initial state
  ACTIVITY <0-9>  - Set CCM activity level (0=passive, 9=maximum aggression)
  COLLAPSE        - Trigger cave collapse - kills all players in the cave

NOT YET IMPLEMENTED (16 commands):
===================================
Basic Commands:
  EXORCISE        - Exorcise an object to the armoury (room 20)
  VIEW            - Use crystal ball to view remote location
  GO/WALK/RUN     - Alternative movement command
  DEBUG           - Debug command (shows error message)
  END             - End game (alternative to quit)

Wizard-Only Commands (Not Implemented):
  FAST            - Enable fast mode (skip graphics/delays)
  SLOW            - Disable fast mode
  PACIFY          - Make creature passive
  ALIAS           - Change player name
  FORCE           - Force another player to execute a command

COMMAND ALIASES:
================
  TAKE/PICKUP -> GET
  LEAVE -> DROP
  CHAT/TALK -> SAY
  PLAYERS/LIST -> WHO
  STATS/STATUS -> SCORE
  COMMANDS/? -> HELP
  EXIT -> QUIT
  STAFF -> ZAP
  TELE -> TELEPORT
  ATTACK/FIGHT -> HIT
  L -> LOOK
  I/INV -> INVENTORY
  POWER/SWITCH -> LIGHTS

IMPLEMENTATION NOTES:
=====================
- GET command now prevents picking up creatures (shows "The [creature] is getting annoyed")
- TELEPORT success depends on: Wizard rank (always succeeds), player level (score >= 500), 
  and Shield possession (guarantees success)
- Staff of Merlin requires: Wizard rank + Staff in inventory + Charges (0-7)
- Staff charging happens at altar (room 1) via CHARGE command
- Creature movement has two types: walk (10x more likely) and teleport (rare)
- Room display matches BBC Micro: no room numbers, no exits, no aggressive status
- DEPOSIT: Treasure can be deposited at bank (room 56) for 20-40 points, then respawns randomly
- Objects 11-15 (Crystal Ball, Staff, Amulet, Treasure, Guardian) spawn randomly on REGEN
- TELL: Messages appear in status area (combat style), Wizards can broadcast to all
- ANNOY: Makes creatures aggressive and target the player, or sends annoy message to players
- LIGHTS: Toggle lights on/off in room 12 (Green room)
  - When lights OFF and no Crystal Ball: "It is too dark to see"
  - When lights ON or player has Crystal Ball: Normal room description shown
  - Broadcasts to all players: "The Lights come ON" / "The Lights go OFF"
- COLLAPSE: Wizard-only command that kills all players in the cave
  - Sends "Cave collapses" message to all players (once)
  - Saves all player data
  - Kicks everyone except the wizard to GOING screen (game over)
  - The wizard who issues the command survives
  - Cannot be used via FORCE command
- BITE: Bite attack that can transfer poison
  - Against creatures: 3-6 damage, 2/3 chance creature dodges
  - Against players: 3-5 damage, 2/3 chance player dodges
  - If biter is poisoned, poison transfers to victim
  - Victim receives: "You are BITEn by [attacker]" (with poison warning if transferred)
- POISON: Poison a player with poison item
  - Requires poison item in inventory
  - Can only target players (not creatures)
  - Creatures display: "The cave [creature] thrives on POISON!!"
  - Successfully poisons target player (sets poisoned flag)
  - Poison causes 0.05 stamina damage per tick
  - "I am poisoned" message when stamina crosses whole number boundary
  - "You are almost dead" message (1/20 chance per tick when stamina < 5)
- PULL: Pull rope to raise portcullis in rooms 29/30
  - Only works in rooms 29 or 30
  - Raises portcullis to allow passage (East from 29, West from 30)
  - Portcullis automatically lowers after 10 seconds
  - Broadcasts "The portcullis goes UP" / "The portcullis FALLS" to both rooms
  - Room descriptions show "The Portcullis is UP" or "The Portcullis is DOWN"
  - Exits are dynamically blocked/unblocked based on portcullis state
"""

import random
from typing import Dict
from player import Player
from game_state import GameState

class CommandParser:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        
        # Direction mappings
        self.directions = {
            'n': 'north', 'north': 'north',
            's': 'south', 'south': 'south',
            'e': 'east', 'east': 'east',
            'w': 'west', 'west': 'west',
            'u': 'up', 'up': 'up',
            'd': 'down', 'down': 'down'
        }
    
    @staticmethod
    def add_article(name: str) -> str:
        """Add 'A' or 'An' before a name based on first letter"""
        vowels = "AEIOU"
        first_letter = name[0].upper() if name else ""
        article = "An" if first_letter in vowels else "A"
        return f"{article} {name}"
    
    async def parse(self, player: Player, command: str) -> Dict:
        """Parse and execute a command"""
        command = command.strip()
        parts = command.split(maxsplit=1)
        
        if not parts:
            return {"message": ""}
        
        # Lowercase only the command word, keep args as-is (uppercase from client)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Movement commands
        if cmd in self.directions:
            return await self.move(player, self.directions[cmd])
        
        # Look command
        if cmd in ['look', 'l']:
            return await self.look(player)
        
        # Inventory command
        if cmd in ['inventory', 'i', 'inv']:
            return await self.inventory(player)
        
        # Get command
        if cmd in ['get', 'take', 'pickup']:
            return await self.get_item(player, args)
        
        # Drop command
        if cmd in ['drop', 'leave']:
            return await self.drop_item(player, args)
        
        # Say command
        if cmd in ['say', 'chat', 'talk']:
            return await self.say(player, args)
        
        # Who command
        if cmd in ['who', 'players', 'list']:
            return await self.who(player)
        
        # Score command
        if cmd in ['score', 'stats', 'status']:
            return await self.score(player)
        
        # Help command
        if cmd in ['help', 'commands', '?']:
            return await self.help(player)
        
        # Attack command
        if cmd in ['hit', 'attack', 'fight']:
            return await self.hit(player, args)
        
        # Kill command (shows message)
        if cmd in ['kill']:
            return {"message": "Life is not that simple...try HIT", "beeps": 1}
        
        # Stab command (Dagger/Knife)
        if cmd in ['stab']:
            return await self.stab(player, args)
        
        # Burn command (Flamethrower)
        if cmd in ['burn']:
            return await self.burn(player, args)
        
        # Zap command (Staff of Merlin)
        if cmd in ['zap', 'staff']:
            return await self.zap(player, args)
        
        # Shoot command (Arrow)
        if cmd in ['shoot']:
            return await self.shoot(player, args)
        
        # Bite command
        if cmd in ['bite']:
            return await self.bite(player, args)
        
        # Poison command
        if cmd in ['poison']:
            return await self.poison(player, args)
        
        # Teleport command
        if cmd in ['teleport', 'tele']:
            return await self.teleport(player, args)
        
        # Summon command (Wizard ability)
        if cmd in ['summon']:
            return await self.summon(player, args)
        
        # Deploy command (Wizard ability)
        if cmd in ['deploy']:
            return await self.deploy(player, args)
        
        # Regen command (Wizard ability)
        if cmd in ['regen']:
            return await self.regen(player)
        
        # Charge command (Staff of Merlin at altar)
        if cmd in ['charge']:
            return await self.charge_staff(player)
        
        # Wiz command (Wizard teleport to room 16)
        if cmd in ['wiz']:
            return await self.wiz(player)
        
        # Room command (Wizard teleport to specific room number)
        if cmd in ['room']:
            return await self.room(player, args)
        
        # Hello command (broadcast to room)
        if cmd in ['hello']:
            return await self.hello(player)
        
        # Drink command
        if cmd in ['drink']:
            return await self.drink(player, args)
        
        # Examine command
        if cmd in ['examine']:
            return await self.examine(player, args)
        
        # Pull command (rope/portcullis)
        if cmd in ['pull']:
            return await self.pull(player, args)
        
        # Release command (internal - triggered by pressing RETURN while holding rope)
        if cmd in ['release', '']:
            return await self.release(player)
        
        # Abbreviated examine/look (shows "Idiot!")
        if cmd in ['exa', 'loo']:
            return {"message": "Idiot!"}
        
        # Activity command (Wizard-only)
        if cmd in ['activity']:
            return await self.activity(player, args)
        
        # Deposit command
        if cmd in ['deposit']:
            return await self.deposit(player, args)
        
        # Tell command
        if cmd in ['tell']:
            return await self.tell(player, args)
        
        # Annoy command
        if cmd in ['annoy']:
            return await self.annoy(player, args)
        
        # Lights command (room 12 only)
        if cmd in ['lights', 'power', 'switch']:
            return await self.lights(player, args)
        
        # Collapse command (Wizard-only)
        if cmd in ['collapse']:
            return await self.collapse(player)
            
        # Quit command (save and exit)
        if cmd in ['quit', 'exit']:
            return await self.quit_game(player)
        
        # Unknown command
        return {"message": f"Unknown command: {cmd}. Type 'help' for available commands."}
    
    async def move(self, player: Player, direction: str) -> Dict:
        """Move player in a direction"""
        can_move, next_room = self.game_state.can_move(player, direction)
        
        if not can_move:
            return {"message": f"You can't go {direction} from here.", "beeps": 1}
        
        old_room = player.room_id
        player.room_id = next_room
        
        return {
            "moved": True,
            "old_room": old_room,
            "direction": direction
        }
    
    async def look(self, player: Player) -> Dict:
        """
        Look at current room (matching BBC Micro PROCK)
        Line 1060: IF(?&A02AND1)=0OR!(&A00+4*12)=A*&100PRINT?&7840
        Line 1060: IF(?&A02AND1)<>0AND!(&A00+4*12)<>A*&100PRINT"It is too dark to see"
        
        Lights check:
        - If lights are ON OR player has Crystal Ball: show room
        - If lights are OFF AND player doesn't have Crystal Ball: "It is too dark to see"
        """
        room = self.game_state.get_room(player.room_id)
        
        if not room:
            return {"message": "You are nowhere."}
        
        # Check lighting (BBC Micro line 1060)
        # Show room if: lights_on OR player has Crystal Ball
        has_crystal_ball = any("crystal" in item.lower() and "ball" in item.lower() for item in player.inventory)
        
        if not self.game_state.lights_on and not has_crystal_ball:
            # Too dark to see
            return {"message": "It is too dark to see"}
        
        # Build description (just the room text, no exits)
        desc = room["description"]
        
        # Add objects (one per line with A/An)
        objects = self.game_state.get_objects_in_room(player.room_id)
        if objects:
            desc += "\n"
            for obj in objects:
                desc += f"\n{self.add_article(obj)} is here."
        
        # Add creatures (one per line with A/An, no status)
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        if creatures:
            desc += "\n"
            for creature in creatures:
                desc += f"\n{self.add_article(creature.name)} is here."
        
        # Add players (one per line, with stamina if viewer is Wizard)
        other_players = [
            p for p in self.game_state.get_players_in_room(player.room_id)
            if p.name != player.name
        ]
        if other_players:
            desc += "\n"
            for other_player in other_players:
                line = f"\n{other_player.name} is here"
                # Wizards can see other players' stamina
                if player.rank == "Wizard":
                    line += f" (stamina {other_player.stamina})"
                desc += line
        
        return {"message": desc}
    
    async def inventory(self, player: Player) -> Dict:
        """Show player inventory"""
        if not player.inventory:
            return {"message": "You are not carrying anything."}
        
        items = ", ".join(player.inventory)
        return {
            "message": f"You are carrying: {items} ({len(player.inventory)}/{player.max_inventory})"
        }
    
    async def get_item(self, player: Player, item_name: str) -> Dict:
        """
        Pick up an item
        Based on PROC_ from original game (line 5770)
        """
        if not item_name:
            return {"message": "Get what?"}
        
        item_name_lower = item_name.lower()
        
        # Check if trying to pick up a creature (line 5840: IF!`>&FF)
        # Creatures have stamina > 255, items don't
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        for creature in creatures:
            if item_name_lower in creature.name.lower():
                return {"message": f"The {creature.name} is getting annoyed", "beeps": 1}
        
        # Check if player can carry more
        if not player.can_carry_more():
            return {"message": "My hands are full-I can carry no more.", "beeps": 1}
        
        # Find item in room (case-insensitive partial match)
        objects = self.game_state.get_objects_in_room(player.room_id)
        
        found_item = None
        for obj in objects:
            if item_name_lower in obj.lower():
                found_item = obj
                break
        
        if not found_item:
            return {"message": f"I don't see a {item_name} here.", "beeps": 1}
        
        # Pick up item
        self.game_state.remove_object_from_room(player.room_id, found_item)
        player.add_item(found_item)
        
        return {
            "message": "Taken.",
            "inventory_changed": True
        }
    
    async def drop_item(self, player: Player, item_name: str) -> Dict:
        """Drop an item"""
        if not item_name:
            return {"message": "Drop what?"}
        
        # Find item in inventory (case-insensitive partial match)
        item_name_lower = item_name.lower()
        
        found_item = None
        for item in player.inventory:
            if item_name_lower in item.lower():
                found_item = item
                break
        
        if not found_item:
            return {"message": f"You don't have a '{item_name}'.", "beeps": 1}
        
        # Drop item
        player.remove_item(found_item)
        self.game_state.add_object_to_room(player.room_id, found_item)
        
        # If dropping Staff of Merlin, reset charges to 0
        if "staff" in found_item.lower() and "merlin" in found_item.lower():
            player.staff_charges = 0
        
        return {
            "message": f"You drop the {found_item}.",
            "inventory_changed": True
        }
    
    async def say(self, player: Player, message: str) -> Dict:
        """Say something to other players"""
        if not message:
            return {"message": "Say what?"}
        
        return {
            "message": f"You say: {message}",
            "broadcast": message
        }
    
    async def who(self, player: Player) -> Dict:
        """List all players (matching BBC Micro format)"""
        players = list(self.game_state.players.values())
        
        if not players:
            return {"message": "No players online."}
        
        # BBC Micro format: "These people are in CAVE"
        message = "These people are in CAVE\n"
        
        is_wizard = (player.rank == "Wizard")
        
        for p in players:
            # Print player name
            message += p.name
            
            # Wizards see extra info (stamina and station number)
            if is_wizard:
                # TAB(8) = column 8, TAB(22) = column 22
                # Pad to column 8, show stamina, pad to column 22, show station
                padding1 = max(1, 8 - len(p.name))
                message += " " * padding1
                stamina_text = f"stamina {int(p.stamina)}"
                message += stamina_text
                
                # Calculate padding to reach column 22
                current_pos = len(p.name) + padding1 + len(stamina_text)
                padding2 = max(1, 22 - current_pos)
                message += " " * padding2
                message += f"stn {p.room_id}"
            
            message += "\n"
        
        return {"message": message}
    
    async def score(self, player: Player) -> Dict:
        """Show player score and stats"""
        stats = f"""Score is {player.score}
Stamina is {int(player.stamina)}
Stamina limit is {player.max_stamina}"""
        
        return {"message": stats}
    
    async def help(self, player: Player) -> Dict:
        """Show help message"""
        help_text = """
Available Commands:

Movement: n, s, e, w, u, d (or north, south, east, west, up, down)
Look: look, l
Inventory: inventory, i
Get: get <item>, take <item>
Drop: drop <item>

Combat:
  hit <target>   - Hit with bare hands or stick
  stab <target>  - Stab with dagger or knife
  burn <target>  - Burn with flamethrower
  zap <target>   - Zap with Staff of Merlin
  shoot <target> - Shoot with arrow (consumed)
  bite <target>  - Bite target (poisons if you're poisoned)
  poison <target> - Poison player (requires poison item)

Social: say <message>
Who: who, players
Score: score, stats
Help: help, ?

Examples:
  n              - Move north
  get dagger     - Pick up the dagger
  stab dragon    - Stab the dragon with dagger
  burn troll     - Burn the troll with flamethrower
  hit Bob        - Hit player Bob (PvP)
        """.strip()
        
        return {"message": help_text}
    
    async def hit(self, player: Player, target_name: str) -> Dict:
        """Hit a creature or player (bare hands or stick)"""
        if not target_name:
            return {"message": "Hit what?"}
        
        # Check for players first (PvP)
        target_player = self.game_state.get_player(target_name)
        if target_player and target_player.room_id == player.room_id:
            return await self.attack_player(player, target_player)
        
        # Otherwise attack creature
        return await self.attack_creature(player, target_name)
    
    async def attack_player(self, attacker: Player, target: Player) -> Dict:
        """Player vs Player combat (matching BBC Micro behavior)"""
        if attacker.name == target.name:
            return {"message": "You can't attack yourself!"}
        
        # Determine weapon (check inventory for Stick)
        has_stick = any("stick" in item.lower() for item in attacker.inventory)
        weapon_bonus = 3 if has_stick else 0
        
        # Calculate damage (1-3 base + weapon bonus)
        base_damage = random.randint(1, 3)
        total_damage = base_damage + weapon_bonus
        
        # Apply damage
        target_died = target.take_damage(total_damage)
        
        # BBC Micro: PROCG uses PRINT (main window), not PROCB (status bar)
        # Attacker sees "Hitting [target]" in main window
        message = f"Hitting {target.name}"
        
        if target_died:
            attacker.kills += 1
            attacker.score += 50  # PvP kill bonus
            target.deaths += 1
            # Respawn target at entrance
            target.room_id = 1
            target.respawn()
            target.inventory = []  # Drop all items on death
            
            # Make all creatures forget about the dead player
            self.game_state.reset_creatures_targeting_player(target.name)
        
        return {
            "message": message,
            # No "combat" flag - goes to main window, not status bar
            "pvp": True,
            "target_player": target.name,
            "target_died": target_died
        }
    
    async def attack_creature(self, player: Player, target_name: str) -> Dict:
        """Attack a creature"""
        # Get creatures in room
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        
        if not creatures:
            return {"message": "There's nothing here to attack."}
        
        # Find matching creature (case-insensitive partial match)
        target_name_lower = target_name.lower()
        target_creature = None
        
        for creature in creatures:
            if target_name_lower in creature.name.lower():
                target_creature = creature
                break
        
        if not target_creature:
            return {"message": f"There is no '{target_name}' here to attack."}
        
        # Check if creature is already dead
        if target_creature.is_dead:
            return {"message": f"The {target_creature.name} is already dead."}
        
        # HIT command only uses bare hands or stick (not other weapons)
        weapon = None
        if any("stick" in item.lower() for item in player.inventory):
            weapon = "Stick"
        
        # Perform attack
        result = await self.game_state.player_attack_creature(player, target_creature, weapon)
        
        # Build message (matching BBC Micro format)
        message = f"The {result['creature_name']} is HIT! stamina now {target_creature.stamina}"
        
        if result['creature_died']:
            message = f"The {result['creature_name']} is dead! You gain {result['points_awarded']} points."
        elif not target_creature.is_aggressive:
            # Creature becomes aggressive after first hit
            pass  # Aggression is handled in game_state
        
        return {
            "message": message,
            "combat": True,
            "creature_died": result['creature_died']
        }
    
    async def zap(self, player: Player, target_name: str) -> Dict:
        """Wizard zap attack using Staff of Merlin (requires wizard rank, staff, and charges)"""
        if not target_name:
            return {"message": "Zap what?"}
        
        # Check 1: Must be a wizard
        if player.rank != "Wizard":
            return {"message": "Only wizards can zap!"}
        
        # Check 2: Must have Staff of Merlin
        if not player.has_staff():
            return {"message": "You do not have the Staff of Merlin.", "beeps": 1}
        
        # Check 3: Staff must have charges
        if player.staff_charges <= 0:
            return {"message": "Nothing happens.", "beeps": 1}  # Staff is out of charges
        
        # Get creatures in room
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        
        if not creatures:
            return {"message": "There's nothing here to zap."}
        
        # Find matching creature
        target_name_lower = target_name.lower()
        target_creature = None
        
        for creature in creatures:
            if target_name_lower in creature.name.lower():
                target_creature = creature
                break
        
        if not target_creature:
            return {"message": f"There is no '{target_name}' here to zap."}
        
        if target_creature.is_dead:
            return {"message": f"The {target_creature.name} is already dead."}
        
        # Use one charge from the staff
        player.use_staff_charge()
        
        # Zap attack (Wizard zap does 50-75 damage)
        result = await self.game_state.player_attack_creature(player, target_creature, "Staff")
        
        # BBC Micro format (line 4920 + 5020):
        # Main area: "!ZAPPING!" (PROCG)
        # Status area: "The [creature] is !ZAPPED! stamina now [X]" (PROCB)
        main_message = "!ZAPPING!"
        status_message = f"The {result['creature_name']} is !ZAPPED! stamina now {target_creature.stamina}"
        
        if result['creature_died']:
            # Line 3310: PROCB("The "+creature+" is dead.")
            status_message = f"The {result['creature_name']} is dead."
        
        return {
            "message": main_message,
            "status_message": status_message,
            "style": "normal",  # Main message goes to main area, not status
            "creature_died": result['creature_died'],
            "beeps": 3  # ZAP = 3 beeps! (VDU7,7,7) - most dramatic!
        }

    async def stab(self, player: Player, target_name: str) -> Dict:
        """Stab with dagger or knife"""
        if not target_name:
            return {"message": "Stab what?"}
        
        # Check if player has dagger or knife
        has_dagger = any("dagger" in item.lower() for item in player.inventory)
        has_knife = any("knife" in item.lower() for item in player.inventory)
        
        if not has_dagger and not has_knife:
            return {"message": "But you do not have the dagger or knife!", "beeps": 1}
        
        weapon = "Dagger" if has_dagger else "Knife"
        
        # Get creatures in room
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        
        if not creatures:
            return {"message": "There's nothing here to stab."}
        
        # Find matching creature
        target_name_lower = target_name.lower()
        target_creature = None
        
        for creature in creatures:
            if target_name_lower in creature.name.lower():
                target_creature = creature
                break
        
        if not target_creature:
            return {"message": f"There is no '{target_name}' here to stab."}
        
        if target_creature.is_dead:
            return {"message": f"The {target_creature.name} is already dead."}
        
        # Stab attack (21-30 damage matching BBC Micro)
        result = await self.game_state.player_attack_creature(player, target_creature, weapon)
        
        # BBC Micro: PROCG displays "STABbing <target>" in main window
        main_message = f"STABbing {target_creature.name}"
        
        # BBC Micro: PROCM displays stamina in status bar
        status_message = f"The {result['creature_name']}'s Stamina={target_creature.stamina}"
        
        if result['creature_died']:
            status_message = f"The {result['creature_name']} is dead!"
        
        return {
            "message": main_message,  # Main window (no combat flag!)
            "status_message": status_message,  # Status bar
            "creature_died": result['creature_died']
        }
    
    async def burn(self, player: Player, target_name: str) -> Dict:
        """Burn with flamethrower"""
        if not target_name:
            return {"message": "Burn what?"}
        
        # Check if player has flamethrower
        has_flamethrower = any("flamethrower" in item.lower() for item in player.inventory)
        
        if not has_flamethrower:
            return {"message": "With what?", "beeps": 1}
        
        # Get creatures in room
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        
        if not creatures:
            return {"message": "There's nothing here to burn."}
        
        # Find matching creature
        target_name_lower = target_name.lower()
        target_creature = None
        
        for creature in creatures:
            if target_name_lower in creature.name.lower():
                target_creature = creature
                break
        
        if not target_creature:
            return {"message": f"There is no '{target_name}' here to burn."}
        
        if target_creature.is_dead:
            return {"message": f"The {target_creature.name} is already dead."}
        
        # Burn attack (51-60 damage matching BBC Micro)
        result = await self.game_state.player_attack_creature(player, target_creature, "Flamethrower")
        
        # BBC Micro: PROCG displays "BURNing <target>" in main window
        main_message = f"BURNing {target_creature.name}"
        
        # BBC Micro: PROCM displays stamina in status bar
        status_message = f"The {result['creature_name']}'s Stamina={target_creature.stamina}"
        
        if result['creature_died']:
            status_message = f"The {result['creature_name']} is Frazzled!"
        
        return {
            "message": main_message,  # Main window (no combat flag!)
            "status_message": status_message,  # Status bar
            "creature_died": result['creature_died']
        }
    
    async def shoot(self, player: Player, target_name: str) -> Dict:
        """Shoot with arrow at creature or player"""
        if not target_name:
            return {"message": "Shoot what?"}
        
        # Check if player has bow (BBC Micro line 4620)
        has_bow = any("bow" in item.lower() for item in player.inventory)
        
        if not has_bow:
            return {"message": "You have nothing to SHOOT with.", "beeps": 1}
        
        # Check if player has arrow (BBC Micro line 4640)
        has_arrow = any("arrow" in item.lower() for item in player.inventory)
        
        if not has_arrow:
            return {"message": "You have no Arrow", "beeps": 1}
        
        # First check if target is a player
        target_player = None
        for p in self.game_state.players.values():
            if p.player_id != player.player_id and p.room_id == player.room_id:
                if target_name.lower() in p.name.lower():
                    target_player = p
                    break
        
        # If targeting a player
        if target_player:
            # Shoot attack (30-40 damage)
            result = await self.game_state.player_attack_player(player, target_player, "Arrow")
            
            # Remove arrow from inventory and drop it in the room
            arrow_item = None
            for item in player.inventory:
                if "arrow" in item.lower():
                    arrow_item = item
                    player.remove_item(item)
                    break
            
            # Add arrow to current room's objects
            if arrow_item:
                if player.room_id not in self.game_state.objects:
                    self.game_state.objects[player.room_id] = []
                if arrow_item not in self.game_state.objects[player.room_id]:
                    self.game_state.objects[player.room_id].append(arrow_item)
            
            message = f"You SHOOT {result['target_name']} with your Arrow for {result['damage']} damage!"
            message += "\nYour arrow falls to the ground."
            
            if result['target_died']:
                message += f"\n\n{result['target_name']} is dead!"
            else:
                message += f"\n{result['target_name']} has {target_player.stamina}/{target_player.max_stamina} stamina remaining."
            
            return {
                "message": message,
                "combat": True,
                "target_died": result['target_died'],
                "inventory_changed": True
            }
        
        # Otherwise check for creatures
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        
        if not creatures:
            return {"message": "There's nothing here to shoot."}
        
        # Find matching creature
        target_name_lower = target_name.lower()
        target_creature = None
        
        for creature in creatures:
            if target_name_lower in creature.name.lower():
                target_creature = creature
                break
        
        if not target_creature:
            return {"message": f"There is no '{target_name}' here to shoot."}
        
        if target_creature.is_dead:
            return {"message": f"The {target_creature.name} is already dead."}
        
        # Shoot attack (31-40 damage matching BBC Micro) - Arrow is dropped in current room
        result = await self.game_state.player_attack_creature(player, target_creature, "Arrow")
        
        # Remove arrow from inventory and drop it in the current room
        arrow_item = None
        for item in player.inventory:
            if "arrow" in item.lower():
                arrow_item = item
                player.remove_item(item)
                break
        
        # Add arrow to current room's objects
        if arrow_item:
            if player.room_id not in self.game_state.objects:
                self.game_state.objects[player.room_id] = []
            if arrow_item not in self.game_state.objects[player.room_id]:
                self.game_state.objects[player.room_id].append(arrow_item)
        
        # BBC Micro: PROCG displays "SHOOTing <target>" in main window
        main_message = f"SHOOTing {target_creature.name}"
        
        # BBC Micro: PROCB displays result in status bar
        status_message = f"The {result['creature_name']} is SHOT stamina now {target_creature.stamina}"
        
        if result['creature_died']:
            status_message = f"The {result['creature_name']} is dead!"
        
        return {
            "message": main_message,  # Main window (no combat flag!)
            "status_message": status_message,  # Status bar
            "creature_died": result['creature_died'],
            "inventory_changed": True
        }

    async def bite(self, player: Player, target_name: str) -> Dict:
        """
        Bite target (can poison if player is poisoned)
        BBC Micro lines 5470-5540 (PROCAA)
        """
        if not target_name:
            return {"message": "Bite what?"}
        
        # Line 5470: PROCG("BITEing")
        # First check if target is a creature
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        target_creature = None
        
        for creature in creatures:
            if target_name.lower() in creature.name.lower():
                target_creature = creature
                break
        
        # Line 5470: IFT>&A00PROCr:ENDPROC (if creature, use PROCr - bite creature)
        if target_creature:
            if target_creature.is_dead:
                return {"message": f"The {target_creature.name} is already dead."}
            
            # Line 5580: IFRND(3)<>1PRINT"The ";D$;" dodges away":ENDPROC
            import random
            if random.randint(1, 3) != 1:
                return {"message": f"The {target_creature.name} dodges away"}
            
            # Line 5600: S=!TAND&FFFF00:S=S-((3+RND(3))*&100)
            # Damage is 3-6 (3+RND(3) where RND(3) is 0-2)
            damage = 3 + random.randint(0, 2)
            
            # Apply damage manually
            creature_died = target_creature.take_damage(damage)
            
            # Make creature aggressive if it wasn't already
            if not creature_died:
                target_creature.make_aggressive()
                target_creature.target_player = player.name
            
            # Award points if creature died
            if creature_died:
                points = target_creature.max_stamina // 10
                player.score += points
                player.kills += 1
                
                # Move creature to mortuary (room 19)
                if target_creature.room_id in self.game_state.creatures_by_room:
                    if target_creature.obj_id in self.game_state.creatures_by_room[target_creature.room_id]:
                        self.game_state.creatures_by_room[target_creature.room_id].remove(target_creature.obj_id)
                
                # Add to mortuary
                target_creature.room_id = 19
                if 19 not in self.game_state.creatures_by_room:
                    self.game_state.creatures_by_room[19] = []
                self.game_state.creatures_by_room[19].append(target_creature.obj_id)
            
            # Line 5610: PROCM (display stamina)
            main_message = f"BITEing {target_creature.name}"
            status_message = f"The {target_creature.name}'s Stamina={target_creature.stamina}"
            
            if creature_died:
                status_message = f"The {target_creature.name} is dead!"
            
            return {
                "message": main_message,
                "status_message": status_message,
                "creature_died": creature_died
            }
        
        # Otherwise check for players
        target_player = None
        for p in self.game_state.players.values():
            if p.player_id != player.player_id and p.room_id == player.room_id:
                if target_name.lower() in p.name.lower():
                    target_player = p
                    break
        
        if not target_player:
            return {"message": f"There is no '{target_name}' here to bite."}
        
        # Line 5500: IFFNA(T)ENDPROC (check if target exists)
        # Line 5510: IFRND(3)<>1PROCC(1,?(T+8),E$+" tries to BITE you!")
        # Line 5510: PRINTD$;" dodges away":ENDPROC
        import random
        if random.randint(1, 3) != 1:
            # Target dodges - send message to target
            return {
                "message": f"{target_player.name} dodges away",
                "tell_target": target_player.name,
                "tell_message": f"{player.name} tries to BITE you!"
            }
        
        # Line 5520: PROCB(E$+" is BITEn")
        # Line 5540: PROCC(10,?(T+8),CHR$3+RND(3))+E$)
        # Damage is 3-5 (CHR$3+RND(3) where RND(3) is 0-2)
        damage = 3 + random.randint(0, 2)
        target_player.take_damage(damage)
        
        # Line 5520: IFMPROCC(5,?(T+8),E$):ENDPROC
        # If biter is poisoned (M=TRUE), poison the target (event 5)
        poison_transferred = False
        if player.poisoned:
            target_player.poisoned = True
            poison_transferred = True
        
        # Check if target died
        target_died = target_player.stamina <= 0
        if target_died:
            target_player.deaths += 1
            player.kills += 1
            player.add_score(10)  # Points for kill
        
        # Message for attacker
        message = f"{target_player.name} is BITEn"
        
        # Message for victim (event 10: "You are BITEn by <attacker>")
        victim_message = f"You are BITEn by {player.name}"
        if poison_transferred:
            victim_message += " - You are poisoned!"
        
        return {
            "message": message,
            "combat": True,
            "beeps": 1,
            "pvp": True,
            "target_player": target_player.name,
            "target_died": target_died,
            "poison_transferred": poison_transferred,
            "victim_message": victim_message
        }

    async def poison(self, player: Player, target_name: str) -> Dict:
        """
        Poison another player or creature
        BBC Micro lines 5380-5450 (PROCe)
        """
        # Line 5380: IF!&A0C<>A*&100PRINT"You do not have the poison":VDU7:ENDPROC
        has_poison = any("poison" in item.lower() for item in player.inventory)
        
        if not has_poison:
            return {"message": "You do not have the poison", "beeps": 1}
        
        # Line 5400: IFD$=C$D$=R$:PRINT"POISONing ";D$
        if not target_name:
            return {"message": "Poison what?"}
        
        # Line 5410: R$=D$:T=FND(D$):IFT>&A00PRINT"The cave ";D$;" thrives on POISON!!":VDU7:ENDPROC
        # First check if target is a creature
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        target_creature = None
        
        for creature in creatures:
            if target_name.lower() in creature.name.lower():
                target_creature = creature
                break
        
        if target_creature:
            # Creatures thrive on poison!
            return {"message": f"The cave {target_creature.name} thrives on POISON!!", "beeps": 1}
        
        # Otherwise check for players
        target_player = None
        for p in self.game_state.players.values():
            if p.player_id != player.player_id and p.room_id == player.room_id:
                if target_name.lower() in p.name.lower():
                    target_player = p
                    break
        
        if not target_player:
            return {"message": f"There is no '{target_name}' here to poison."}
        
        # Line 5440: IFFNA(T)ENDPROC (check if target exists)
        # Line 5450: PROCC(5,?(T+8),E$):ENDPROC (event 5 = poison target)
        target_player.poisoned = True
        
        return {
            "message": f"POISONing {target_player.name}",
            "tell_target": target_player.name,
            "tell_message": f"{player.name} has poisoned you!",
            "beeps": 1
        }

    async def teleport(self, player: Player, target_name: str) -> Dict:
        """
        Teleport to an object or creature
        Based on original game logic (PROCw/PROCp)
        Success depends on player rank, level, and whether they have the Shield
        """
        if not target_name:
            return {"message": "Teleport to what?"}
        
        target_name_lower = target_name.lower()
        
        # Search for object in rooms
        target_room = None
        target_object = None
        
        # Check all rooms for the object
        for room_id, room in self.game_state.rooms.items():
            objects = self.game_state.objects.get(room_id, [])
            for obj in objects:
                if target_name_lower in obj.lower():
                    target_room = room_id
                    target_object = obj
                    break
            if target_room:
                break
        
        # Check creatures
        if not target_room:
            for creature in self.game_state.creatures.values():
                if target_name_lower in creature.name.lower() and not creature.is_dead:
                    target_room = creature.room_id
                    target_object = creature.name
                    break
        
        if not target_room:
            return {"message": "Known OBJECTS & CREATURES only!"}
        
        # Check if object is being carried by another player
        for other_player in self.game_state.players.values():
            if other_player.name != player.name:
                for item in other_player.inventory:
                    if target_name_lower in item.lower():
                        return {"message": "That object is being carried by a CAVER"}
        
        # Check if in Wizard's domain (rooms 16-20) and player is not a wizard
        if player.rank != "Wizard" and 16 <= target_room <= 20:
            return {"message": "That is in the WIZARD's domain"}
        
        # Calculate success chance
        # Wizards always succeed
        if player.rank == "Wizard":
            success = True
        else:
            # Determine player level (1 or 2 based on score)
            player_level = 2 if player.score >= 500 else 1
            
            # Check if player has Ruby (increases magical power)
            has_ruby = any("ruby" in item.lower() for item in player.inventory)
            
            # Original formula: RND(50/z) > 1 - 4*has_ruby
            # With ruby: RND(50/z) > 1-4 = -3 (always succeeds for level 2)
            # Without ruby: RND(50/z) > 1 (50% chance for level 2, 2% for level 1)
            import random
            roll = random.randint(1, 50 // player_level)
            threshold = 1 - (4 if has_ruby else 0)
            success = roll > threshold
        
        if not success:
            return {"message": "Nothing happens"}
        
        # Teleport successful!
        old_room = player.room_id
        player.room_id = target_room
        
        return {
            "message": "You concentrate... and suddenly find yourself elsewhere!",
            "room_changed": True,
            "teleport": True,
            "old_room": old_room
        }
    
    async def summon(self, player: Player, target_name: str) -> Dict:
        """
        Summon an object or creature to player's location
        Based on PROCZ from original game (line 2100)
        Wizards always succeed, others have chance based on level and Amulet
        """
        import random
        
        if not target_name:
            return {"message": "Summon what?"}
        
        target_name_lower = target_name.lower()
        is_wizard = (player.rank == "Wizard")
        
        # Check if player has the Amulet (increases success chance)
        has_amulet = any("amulet" in item.lower() for item in player.inventory)
        
        # Find the target (creature or object)
        target_creature = None
        target_object = None
        target_player = None
        target_room = None
        
        # Search for creatures first
        for creature in self.game_state.creatures.values():
            if target_name_lower in creature.name.lower() and not creature.is_dead:
                target_creature = creature
                target_room = creature.room_id
                break
        
        # If not a creature, search for objects
        if not target_creature:
            for room_id, objects in self.game_state.objects.items():
                for obj in objects:
                    if target_name_lower in obj.lower():
                        target_object = obj
                        target_room = room_id
                        break
                if target_object:
                    break
        
        # If not object or creature, search for players (line 4450: FND searches players)
        if not target_creature and not target_object:
            target_player = self.game_state.get_player(target_name)
            if target_player and target_player.name != player.name:
                target_room = target_player.room_id
        
        # Check if target exists
        if not target_creature and not target_object and not target_player:
            return {"message": f"Sorry...wasted effort...{target_name} is not in CAVE"}
        
        # Non-wizards have a chance to fail
        if not is_wizard:
            # Calculate success chance: RND(20/z) > 1-3*(has_amulet)
            # z = player level (1 or 2), assume 1 for now
            player_level = 2 if player.score >= 500 else 1
            success_threshold = 1 - (3 if has_amulet else 0)
            
            if random.random() * (20 / player_level) > success_threshold:
                return {"message": "Nothing Happens"}
        
        # Summon creature
        if target_creature:
            # Don't summon from mortuary (room 19)
            if target_creature.room_id == 19:
                return {"message": "Nothing Happens"}
            
            # Move creature to player's room
            old_room = target_creature.room_id
            await self.game_state.move_creature(target_creature, player.room_id)
            
            # BBC Micro format: "The [creature] is here." in status area
            return {
                "message": f"The {target_creature.name} is here.",
                "combat": True,  # Send to status area
                "summoned": True
            }
        
        # Summon object
        if target_object:
            # Remove from old room
            if target_room in self.game_state.objects:
                if target_object in self.game_state.objects[target_room]:
                    self.game_state.objects[target_room].remove(target_object)
            
            # Add to player's room
            if player.room_id not in self.game_state.objects:
                self.game_state.objects[player.room_id] = []
            self.game_state.objects[player.room_id].append(target_object)
            
            return {
                "message": f"The {target_object} appears!",
                "summoned": True
            }
        
        # Summon player (line 2170: PROCC(8,?(T+8),CHR$B) - event 8 = teleport)
        if target_player:
            old_room = target_player.room_id
            target_player.room_id = player.room_id
            
            return {
                "message": f"{target_player.name} has been summoned!",
                "summon_player": target_player.name,
                "summon_to_room": player.room_id,
                "summoned": True
            }
    
    async def deploy(self, player: Player, target_name: str) -> Dict:
        """
        Deploy (resurrect) a creature from the mortuary
        Based on PROCb from original game (line 3190)
        Wizard-only command
        """
        import random
        
        # Must be a wizard
        if player.rank != "Wizard":
            return {"message": "Only wizards can deploy creatures!"}
        
        if not target_name:
            return {"message": "DEPLOY What?"}
        
        target_name_lower = target_name.lower()
        
        # Search for creature in mortuary (room 19)
        mortuary_creatures = self.game_state.get_creatures_in_room(19)
        
        target_creature = None
        for creature in mortuary_creatures:
            if target_name_lower in creature.name.lower():
                target_creature = creature
                break
        
        if not target_creature:
            return {"message": "CCM must be in mortuary"}
        
        # Resurrect creature with random health (50-100% of max)
        new_health = target_creature.max_stamina + random.randint(0, target_creature.max_stamina // 2)
        target_creature.stamina = new_health
        target_creature.is_dead = False
        target_creature.is_aggressive = False
        target_creature.target_player = None
        
        # Move from mortuary to player's room
        if 19 in self.game_state.creatures_by_room:
            if target_creature.obj_id in self.game_state.creatures_by_room[19]:
                self.game_state.creatures_by_room[19].remove(target_creature.obj_id)
        
        target_creature.room_id = player.room_id
        if player.room_id not in self.game_state.creatures_by_room:
            self.game_state.creatures_by_room[player.room_id] = []
        self.game_state.creatures_by_room[player.room_id].append(target_creature.obj_id)
        
        return {
            "message": "Deployed.",
            "deployed": True
        }
    
    async def regen(self, player: Player) -> Dict:
        """
        Regenerate all objects and creatures to initial state
        Based on REGEN command from original game (line 2580)
        Wizard-only command - resets the entire game world
        Original: IFC$="REGEN"AND G OSCLI"LO.OBJINIT":PROCU:ENDPROC
        No message is shown in the original
        """
        # Must be a wizard
        if player.rank != "Wizard":
            return {"message": "Only wizards can regenerate!"}
        
        # Clear all player inventories to prevent object duplication
        for p in self.game_state.players.values():
            p.inventory = []
        
        # Reload creatures (this will reset all creatures to initial positions)
        await self.game_state.load_creatures(clear_existing=True)
        
        # Reload objects (reset to initial positions, clearing existing)
        await self.game_state.load_initial_objects(clear_existing=True)
        
        # No message in original - just silently regenerates
        return {
            "message": "",
            "regen": True,
            "inventory_changed": True  # Flag to update inventory display
        }
    
    async def charge_staff(self, player: Player) -> Dict:
        """
        Charge the Staff of Merlin at the altar (room 1)
        Based on DEFPROCf from original game (line 5031)
        """
        # Must have the Staff of Merlin
        if not player.has_staff():
            # Random error message
            messages = ["What?", "Eh?", "Pardon?"]
            return {"message": random.choice(messages)}
        
        # Must be in room 1 (the altar)
        if player.room_id != 1:
            return {"message": "With what ??"}
        
        # If staff already has charges, player gets thrown against wall
        if player.staff_charges > 0:
            damage = random.randint(1, player.staff_charges) * 5
            player.take_damage(damage)
            return {
                "message": f"You are thrown against the wall.\nYou take {damage} damage!",
                "combat": True
            }
        
        # Charge the staff (set to 7 charges, stored as 14 in ?&A02, divided by 2 = 7)
        player.charge_staff()
        
        return {
            "message": "The Staff of Merlin glows in your hand.",
            "staff_charged": True
        }
    
    async def wiz(self, player: Player) -> Dict:
        """
        Wizard command to teleport to room 16 (Wizard's domain)
        Based on line 2610 from original game
        """
        # Must be a wizard
        if player.rank != "Wizard":
            return {"message": "Only wizards can use this command!"}
        
        # Teleport to room 16
        old_room = player.room_id
        player.room_id = 16
        
        return {
            "message": "You vanish in a puff of smoke!",
            "room_changed": True,
            "teleport": True,
            "old_room": old_room
        }
    
    async def room(self, player: Player, room_number: str) -> Dict:
        """
        Wizard command to teleport to a specific room number
        New command not in original game - for wizard convenience
        Usage: ROOM 21
        """
        # Must be a wizard
        if player.rank != "Wizard":
            return {"message": "Only wizards can use this command!"}
        
        # Parse room number
        if not room_number:
            return {"message": "ROOM <number> - Teleport to room number"}
        
        try:
            target_room = int(room_number)
        except ValueError:
            return {"message": "Invalid room number"}
        
        # Check if room exists
        if target_room not in self.game_state.rooms:
            return {"message": f"Room {target_room} does not exist"}
        
        # Teleport to the room (same messaging as TELEPORT)
        old_room = player.room_id
        player.room_id = target_room
        
        return {
            "message": "You concentrate... and suddenly find yourself elsewhere!",
            "room_changed": True,
            "teleport": True,
            "old_room": old_room
        }
    
    async def hello(self, player: Player) -> Dict:
        """
        Say hello and broadcast to room
        Based on line 2360 from original game: PRINT"HELLO!!":PROCD(1,B,E$+" says HELLO!")
        """
        return {
            "message": "HELLO!!",
            "broadcast": "says HELLO!",
            "broadcast_raw": True  # Flag to use raw broadcast without adding "says:"
        }
    
    async def drink(self, player: Player, item_name: str) -> Dict:
        """
        Drink vodka, poison, or medicine
        Based on PROCn (lines 5300-5370)
        """
        if not item_name:
            return {"message": "Drink what?", "beeps": 1}
        
        item_name_lower = item_name.lower()
        
        # Check if player has the item
        found_item = None
        for item in player.inventory:
            if item_name_lower in item.lower():
                found_item = item
                break
        
        if not found_item:
            return {"message": f"You do not have the {item_name}", "beeps": 1}
        
        # Determine what was drunk
        item_lower = found_item.lower()
        
        if "vodka" in item_lower:
            result = player.drink_vodka()
            print(f"Player {player.name} drank vodka. Vodka level now: {player.vodka_level}")
            # Vodka stays in inventory (original behavior - not consumed)
            return result
        
        elif "poison" in item_lower:
            result = player.drink_poison()
            # Poison stays in inventory (original behavior - not consumed)
            return result
        
        elif "medicine" in item_lower:
            result = player.drink_medicine()
            # Medicine stays in inventory (original behavior - not consumed)
            return result
        
        else:
            return {"message": f"You can't drink the {found_item}!", "beeps": 1}
    
    async def examine(self, player: Player, item_name: str) -> Dict:
        """
        Examine an object
        Based on line 2340: IFC$="EXAMINE"PRINT"You see nothing special":ENDPROC
        Always returns the same message regardless of what is examined
        """
        return {"message": "You see nothing special"}
    
    async def pull(self, player: Player, item_name: str) -> Dict:
        """
        Pull rope to raise portcullis (rooms 29-30)
        BBC Micro lines 3700-3770 (PROCu):
        - Line 3700: IFB<>29 AND B<>30PRINT"What Rope?":ENDPROC
        - Line 3720: IF?&A03=1PRINT"But the Rope is already pulled":ENDPROC
        - Line 3730: ?&A03=1 (raise portcullis)
        - Line 3730: PRINT"You pull the rope and the Portcullis goes up!!"
        - Line 3730: PRINT'"Press <RETURN> to let go"
        - Line 3730: PROCD(1,29,"The portcullis goes UP")
        - Line 3730: PROCD(1,30,"The portcullis goes UP")
        - Line 3730: REPEATUNTILFNG=CHR$13 (wait for RETURN)
        - Line 3730: ?&A03=0 (lower portcullis)
        - Line 3770: PRINT"The portcullis falls as you let go of the rope"
        - Line 3770: PROCD(1,29,"The portcullis FALLS")
        - Line 3770: PROCD(1,30,"The portcullis FALLS")
        
        Note: In web version, we'll auto-release after a short time instead of waiting for RETURN
        """
        # Check if in rooms 29 or 30
        if player.room_id not in [29, 30]:
            return {"message": "What Rope?"}
        
        # Check if target is "Rope"
        if not item_name or "rope" not in item_name.lower():
            return {"message": "Pull what?"}
        
        # Check if already pulled
        if self.game_state.portcullis_up:
            return {"message": "But the Rope is already pulled"}
        
        # Raise portcullis
        self.game_state.portcullis_up = True
        
        return {
            "message": "You pull the rope and the Portcullis goes up!!\n\nPress <RETURN> to let go",
            "portcullis_raised": True,
            "holding_rope": True,  # Special flag to tell client to wait for RETURN
            "beeps": 1
        }
    
    async def release(self, player: Player) -> Dict:
        """
        Release rope (lower portcullis)
        BBC Micro line 3770: Player releases RETURN key
        - ?&A03=0 (lower portcullis)
        - PRINT"The portcullis falls as you let go of the rope"
        - PROCD(1,29,"The portcullis FALLS")
        - PROCD(1,30,"The portcullis FALLS")
        """
        # Only works if portcullis is currently up
        if not self.game_state.portcullis_up:
            return {"message": ""}  # Silent - no error
        
        # Lower portcullis
        self.game_state.portcullis_up = False
        
        return {
            "message": "The portcullis falls as you let go of the rope",
            "portcullis_lowered": True
        }

    async def activity(self, player: Player, level_str: str) -> Dict:
        """
        Set CCM activity level (Wizard-only)
        Based on line 2550/2820: IFC$="ACTIVITY"ANDGPROCGA
        PROCGA: PRINT"Enter CCM activity (0-9) ";:A$=FNG:IFA$<"0"ORA$>"9"PRINT;?&A00:ENDPROC
        Line 2850: PRINTA$:?&A00=VALA$:PROCA(&A00,&A01):ENDPROC
        """
        # Must be a wizard
        if player.rank != "Wizard":
            return {"message": "Only wizards can set activity level!"}
        
        # Parse level
        if not level_str:
            # Show current level if no argument
            return {"message": f"Current CCM activity: {self.game_state.activity_level}"}
        
        try:
            level = int(level_str)
        except ValueError:
            return {"message": f"Current CCM activity: {self.game_state.activity_level}", "beeps": 1}
        
        # Validate range (0-9)
        if level < 0 or level > 9:
            return {"message": f"Current CCM activity: {self.game_state.activity_level}", "beeps": 1}
        
        # Set activity level
        self.game_state.activity_level = level
        
        # No message in original - just silently sets the value
        return {"message": ""}
    
    async def deposit(self, player: Player, item_name: str) -> Dict:
        """
        Deposit treasure at bank (room 56)
        Based on PROCW (lines 3341-3345):
        3341: IFD$<>"Treasure"PRINT"You can't.":ENDPROC
        3343: IF!(&A00+15*4)<>A*&100PRINT"But you have no treasure !":VDU7:ENDPROC
        3344: IFB<>56PRINT"Not here I'm afraid.":ENDPROC
        3345: N=20+RND(20):PRINT"...";N;" points.":H=H+N
        3345: REPEATN=RND(b):UNTILN>20ORN<16:!(&A00+15*4)=N:U=U-1:ENDPROC
        """
        import random
        
        # Must be depositing treasure
        if not item_name or "treasure" not in item_name.lower():
            return {"message": "You can't."}
        
        # Must have treasure in inventory
        has_treasure = any("treasure" in item.lower() for item in player.inventory)
        if not has_treasure:
            return {"message": "But you have no treasure !", "beeps": 1}
        
        # Must be in room 56 (the bank)
        if player.room_id != 56:
            return {"message": "Not here I'm afraid."}
        
        # Award points (20-40)
        points = 20 + random.randint(1, 20)
        player.add_score(points)
        
        # Remove treasure from inventory
        for item in player.inventory[:]:
            if "treasure" in item.lower():
                player.remove_item(item)
                break
        
        # Respawn treasure in random room (not in wizard's domain 16-20)
        # Line 3345: REPEATN=RND(b):UNTILN>20ORN<16
        max_room = max(self.game_state.rooms.keys())
        while True:
            new_room = random.randint(1, max_room)
            if new_room > 20 or new_room < 16:
                break
        
        # Add treasure to new room
        if new_room not in self.game_state.objects:
            self.game_state.objects[new_room] = []
        self.game_state.objects[new_room].append("Treasure")
        
        return {
            "message": f"You deposit the treasure, which vanishes and you get credited with {points} points.",
            "inventory_changed": True
        }
    
    async def tell(self, player: Player, args: str) -> Dict:
        """
        Send a message to a specific player or all players
        Based on DEFPROCBA (lines 4030-4120)
        
        Original logic:
        4030: PROCG("Sending message to")
        4030: IFD$="All"ANDNOTGPRINT"Only Wizards can do that!!":VDU7:ENDPROC
        4060: IFD$="All"T=&900:GOTO4080
        4070: IFT=&A00ENDPROC
        4080: PRINT"Enter Message"
        4080: M$=FNK
        4080: IFM$=""PRINT"Not Sent":ENDPROC
        4100: IFT>&A00PRINT"The ";D$;" takes no notice":ENDPROC
        4110: IFD$="All"?&7700=1:?&7701=?I:?&7702=M$
        4110: IFD$="All"PROCA(&7700,&77FE):PRINT"Done.":ENDPROC
        4120: PROCC(1,?(T+8),E$+":"+M$):ENDPROC
        
        Format: TELL <player> <message>
        Example: TELL Bob Hello there!
        """
        if not args:
            return {"message": "TELL who? (Format: TELL <player> <message>)"}
        
        # Parse target and message
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            return {"message": "What message? (Format: TELL <player> <message>)"}
        
        target_name = parts[0]
        message = parts[1]
        
        # Check for "All" broadcast (Wizard-only)
        if target_name.upper() == "ALL":
            if player.rank != "Wizard":
                return {"message": "Only Wizards can do that!!", "beeps": 1}
            
            # Broadcast to all players
            return {
                "message": "Done.",
                "tell_all": True,
                "tell_message": f"{player.name}:{message}"
            }
        
        # Find target player
        target_player = self.game_state.get_player(target_name)
        
        if not target_player:
            # Check if it's a creature
            creatures = self.game_state.creatures.values()
            for creature in creatures:
                if target_name.lower() in creature.name.lower():
                    return {"message": f"The {creature.name} takes no notice"}
            
            return {"message": f"Player '{target_name}' not found"}
        
        # Send message to specific player
        return {
            "message": f"Message sent to {target_player.name}",
            "tell_target": target_player.name,
            "tell_message": f"{player.name}:{message}"
        }
    
    async def annoy(self, player: Player, target_name: str) -> Dict:
        """
        Annoy a creature (makes it aggressive) or player (sends message)
        Based on DEFPROCm (lines 3590-3640)
        
        Original logic:
        3590: PROCG("ANNOY"):IFT=&A00ENDPROC
        3620: IFT>&A00AND?T=BPROCJ(T,"A"):ENDPROC  : REM Set aggressive
        3630: IFT>&A00OR?(T+9)<>BPRINT"But ";D$;" isn't here!!":VDU7:ENDPROC
        3640: PROCC(1,?(T+8),E$+" is ANNOYing you!")  : REM Tell other player
        """
        if not target_name:
            return {"message": "ANNOY what?"}
        
        target_name_lower = target_name.lower()
        
        # Check for creatures in room first
        creatures = self.game_state.get_creatures_in_room(player.room_id)
        for creature in creatures:
            if target_name_lower in creature.name.lower():
                # Found creature - make it aggressive
                if creature.is_dead:
                    return {"message": f"The {creature.name} is dead."}
                
                # Line 3620: PROCJ(T,"A") - make aggressive
                creature.make_aggressive()
                creature.target_player = player.name
                
                return {
                    "message": f"The {creature.name} is now aggressive!",
                    "annoyed_creature": True
                }
        
        # Check for players in room
        target_player = None
        for p in self.game_state.players.values():
            if p.name != player.name and p.room_id == player.room_id:
                if target_name_lower in p.name.lower():
                    target_player = p
                    break
        
        if target_player:
            # Line 3640: PROCC(1,?(T+8),E$+" is ANNOYing you!")
            # Send message to player (appears in status area)
            return {
                "message": f"You annoy {target_player.name}",
                "annoy_player": target_player.name,
                "annoy_message": f"{player.name} is ANNOYing you!"
            }
        
        # Not found
        return {"message": f"But {target_name} isn't here!!", "beeps": 1}
    
    async def lights(self, player: Player, args: str) -> Dict:
        """
        Toggle lights on/off in room 12 (Green room)
        Based on PROC` (lines 2950-2990)
        
        Original logic:
        2270: IF(C$="ON"ORC$="OFF")ANDC$=D$C$="LIGHTS"
        2280: IF(C$="POWER"ORC$="SWITCH"ORLEFT$(C$,5)="LIGHT")ANDB=12PROC`:ENDPROC
        2950: IF(D$="On"AND?&A02=0)OR(D$="Off"AND?&A02=1)PRINT"The switch is already in that position"
        2970: IFD$="On"?&A02=?&A02-1:PROCA(&A02,&A03):?&7700=1:?&7701=I:$&7702="The Lights come ON"
        2980: IFD$="Off"?&A02=?&A02+1:PROCA(&A02,&A03):?&7700=1:?&7701=I:$&7702="The Lights go OFF"
        2990: PRINT"I can only switch the lights On or Off"
        
        Commands: LIGHTS ON/OFF, POWER ON/OFF, SWITCH ON/OFF
        """
        # Must be in room 12 (Green room)
        if player.room_id != 12:
            return {"message": "There is no light switch here."}
        
        # Parse argument (ON or OFF)
        if not args:
            return {"message": "I can only switch the lights On or Off"}
        
        args_upper = args.upper()
        
        # Check if already in that position
        if args_upper == "ON" and self.game_state.lights_on:
            return {"message": "The switch is already in that position"}
        
        if args_upper == "OFF" and not self.game_state.lights_on:
            return {"message": "The switch is already in that position"}
        
        # Toggle lights
        if args_upper == "ON":
            self.game_state.lights_on = True
            broadcast_message = "The Lights come ON"
        elif args_upper == "OFF":
            self.game_state.lights_on = False
            broadcast_message = "The Lights go OFF"
        else:
            return {"message": "I can only switch the lights On or Off"}
        
        # Broadcast to all players
        return {
            "message": "",  # No message to the player who flipped the switch
            "lights_broadcast": broadcast_message,
            "lights_changed": True
        }
    
    async def collapse(self, player: Player) -> Dict:
        """
        Trigger cave collapse - kills all OTHER players in the cave
        Based on line 2620 from original game (Wizard-only)
        
        Original logic:
        2620: IFC$="COLLAPSE"ANDGFORX=1TO10:?&7700=3:PROCA(&7700,&7701):A$=INKEY$10:NEXT:PROCH:?&7700=0
        
        - Wizard-only command
        - Sends "Cave collapses" message once to all players
        - Shows player list after collapse (PROCH)
        - Event 3 handler (line 1620): PRINT"Cave collapses":PROCF:*GOING
        - All OTHER players see "Cave collapses", data is saved, kicked to GOING screen
        - The wizard who issues the command survives
        """
        # Must be a wizard
        if player.rank != "Wizard":
            return {"message": "Only wizards can collapse the cave!"}
        
        # Return collapse flag to trigger the collapse sequence
        # The server will handle broadcasting to all players and the death sequence
        return {
            "collapse": True,
            "wizard_name": player.name
        }

    async def quit_game(self, player: Player) -> Dict:
        """
        Quit and save player data
        Based on original game QUIT command (lines 2680-2810)
        
        Original sequence:
        2680: IFV>1PRINT"Unable to QUIT while under the influence"
        2690: IFMPRINT"I need some medical help for the POISON"
        2700: IFD<6 (too weak to quit)
        2720: PRINT"Hold on";
        2740: PRINT".."; (save file) PRINT"."
        2810: PRINT"Saved." then *GOING
        """
        # Check if player is drunk (line 2680)
        if player.is_drunk():
            return {
                "message": "Unable to QUIT while under the influence",
                "quit_denied": True,
                "beeps": 1
            }
        
        # Check if player is poisoned (line 2690)
        if player.poisoned:
            return {
                "message": "I need some medical help for the POISON",
                "quit_denied": True,
                "beeps": 1
            }
        
        # Check if stamina is too low (line 2700)
        if player.stamina < 6:
            return {
                "message": "You are too weak to quit safely. Rest first!",
                "quit_denied": True,
                "beeps": 1
            }
        
        # Return quit_sequence flag to trigger multi-stage quit process
        # The server will handle the delayed messages
        return {
            "quit_sequence": True,
            "player": player
        }
