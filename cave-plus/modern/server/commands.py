"""
Command Parser for Cave-Plus

IMPLEMENTED COMMANDS:
=====================
Movement:
  N/NORTH, S/SOUTH, E/EAST, W/WEST, U/UP, D/DOWN - Move in a direction

Interaction:
  LOOK/L          - Look at current room
  GET/TAKE/PICKUP - Pick up an object
  DROP/LEAVE      - Drop an object
  INVENTORY/I/INV - Show inventory
  SAY/CHAT/TALK   - Say something to players in room
  HELLO           - Say hello (broadcasts "PlayerName says HELLO!" to room)
  KILL            - Shows message "Life is not that simple...try HIT"
  
Combat:
  HIT/ATTACK/FIGHT - Attack with bare hands or stick
  STAB            - Attack with dagger/knife
  BURN            - Attack with flamethrower
  SHOOT           - Attack with arrow
  ZAP/STAFF       - Wizard-only: Attack with Staff of Merlin (requires wizard rank, staff + charges)

Magic/Special:
  TELEPORT/TELE   - Teleport to an object or creature
  CHARGE          - Charge Staff of Merlin at altar (room 1)
  
Information:
  SCORE/STATS/STATUS - Show score and stamina
  WHO/PLAYERS/LIST   - List all players in game
  HELP/COMMANDS/?    - Show help

System:
  QUIT/EXIT       - Save and quit game

Wizard-Only Commands:
  WIZ             - Teleport to room 16 (Wizard's domain)

NOT YET IMPLEMENTED:
====================
Basic Commands:
  SUMMON          - Summon an object or creature to you
  EXORCISE        - Exorcise an object to the armoury
  DRINK           - Drink vodka, poison, or medicine
  POISON          - Poison another player
  VIEW            - Use crystal ball to view remote location
  EXAMINE         - Examine an object (shows "nothing special")
  DEPOSIT         - Deposit treasure at bank (room 56)
  PULL            - Pull rope (portcullis in rooms 29/30)
  ANNOY           - Make creature aggressive
  BITE            - Bite attack (creature-like)
  TELL            - Send message to specific player or all
  LIGHTS/SWITCH/POWER - Toggle lights on/off (room 12)
  GO/WALK/RUN     - Alternative movement command
  DEBUG           - Debug command (shows error message)
  END             - End game (alternative to quit)

Wizard-Only Commands (Not Implemented):
  FAST            - Enable fast mode (skip graphics)
  SLOW            - Disable fast mode
  DEPLOY          - Deploy creature from mortuary
  PACIFY          - Make creature passive
  ALIAS           - Change player name
  ACTIVITY        - Set activity level
  REGEN           - Regenerate objects
  COLLAPSE        - Trigger cave collapse for all players
  FORCE           - Force another player to execute a command

ALIASES:
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
        command = command.lower().strip()
        parts = command.split(maxsplit=1)
        
        if not parts:
            return {"message": ""}
        
        cmd = parts[0]
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
            return {"message": "Life is not that simple...try HIT"}
        
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
        
        # Teleport command
        if cmd in ['teleport', 'tele']:
            return await self.teleport(player, args)
        
        # Charge command (Staff of Merlin at altar)
        if cmd in ['charge']:
            return await self.charge_staff(player)
        
        # Wiz command (Wizard teleport to room 16)
        if cmd in ['wiz']:
            return await self.wiz(player)
        
        # Hello command (broadcast to room)
        if cmd in ['hello']:
            return await self.hello(player)
            return await self.teleport(player, args)
        
        # Quit command (save and exit)
        if cmd in ['quit', 'exit']:
            return await self.quit_game(player)
        
        # Unknown command
        return {"message": f"Unknown command: {cmd}. Type 'help' for available commands."}
    
    async def move(self, player: Player, direction: str) -> Dict:
        """Move player in a direction"""
        can_move, next_room = self.game_state.can_move(player, direction)
        
        if not can_move:
            return {"message": f"You can't go {direction} from here."}
        
        old_room = player.room_id
        player.room_id = next_room
        
        return {
            "message": f"You move {direction}.",
            "moved": True,
            "old_room": old_room,
            "direction": direction
        }
    
    async def look(self, player: Player) -> Dict:
        """Look at current room (matching BBC Micro PROCK)"""
        room = self.game_state.get_room(player.room_id)
        
        if not room:
            return {"message": "You are nowhere."}
        
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
                return {"message": f"The {creature.name} is getting annoyed"}
        
        # Check if player can carry more
        if not player.can_carry_more():
            return {"message": "My hands are full-I can carry no more."}
        
        # Find item in room (case-insensitive partial match)
        objects = self.game_state.get_objects_in_room(player.room_id)
        
        found_item = None
        for obj in objects:
            if item_name_lower in obj.lower():
                found_item = obj
                break
        
        if not found_item:
            return {"message": f"I don't see a {item_name} here."}
        
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
            return {"message": f"You don't have a '{item_name}'."}
        
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
        """List all players"""
        players = list(self.game_state.players.values())
        
        if not players:
            return {"message": "No players online."}
        
        player_list = []
        for p in players:
            room = self.game_state.get_room(p.room_id)
            room_name = room.get("name", f"Room {p.room_id}") if room else "Unknown"
            player_list.append(f"{p.name} ({p.rank}) - {room_name}")
        
        return {"message": "Players online:\n" + "\n".join(player_list)}
    
    async def score(self, player: Player) -> Dict:
        """Show player score and stats"""
        stats = f"""Score is {player.score}
Stamina is {player.stamina}
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
            return await self.hit_player(player, target_player)
        
        # Otherwise attack creature
        return await self.attack_creature(player, target_name)
    
    async def attack_player(self, attacker: Player, target: Player) -> Dict:
        """Player vs Player combat"""
        if attacker.name == target.name:
            return {"message": "You can't attack yourself!"}
        
        # Determine weapon (check inventory for best weapon)
        weapon = None
        weapon_bonus = 0
        
        if any("stick" in item.lower() for item in attacker.inventory):
            weapon = "Stick"
            weapon_bonus = 3
        
        # Calculate damage (1-3 base + weapon bonus)
        base_damage = random.randint(1, 3)
        total_damage = base_damage + weapon_bonus
        
        # Apply damage
        target_died = target.take_damage(total_damage)
        
        # Build message
        weapon_text = f" with your {weapon}" if weapon else ""
        message = f"You hit {target.name}{weapon_text} for {total_damage} damage!"
        
        if target_died:
            message += f"\n\n{target.name} has been defeated!"
            attacker.kills += 1
            attacker.score += 50  # PvP kill bonus
            target.deaths += 1
            # Respawn target at entrance
            target.room_id = 1
            target.respawn()
            target.inventory = []  # Drop all items on death
            
            # Make all creatures forget about the dead player
            self.game_state.reset_creatures_targeting_player(target.name)
        else:
            message += f"\n{target.name} has {target.stamina}/{target.max_stamina} stamina remaining."
        
        return {
            "message": message,
            "combat": True,
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
        
        # Determine weapon (check inventory for best weapon)
        weapon = None
        weapon_priority = ["Flamethrower", "Staff", "Dagger", "Knife", "Stick"]
        for w in weapon_priority:
            if any(w.lower() in item.lower() for item in player.inventory):
                weapon = w
                break
        
        # Perform attack
        result = await self.game_state.player_attack_creature(player, target_creature, weapon)
        
        # Build message
        weapon_text = f" with your {weapon}" if weapon else ""
        message = f"You hit the {result['creature_name']}{weapon_text} for {result['damage']} damage."
        
        if result['creature_died']:
            message += f"\n\nThe {result['creature_name']} is dead! You gain {result['points_awarded']} points."
        else:
            message += f"\nThe {result['creature_name']} has {target_creature.stamina}/{target_creature.max_stamina} stamina remaining."
            if not target_creature.is_aggressive:
                message += f"\nThe {result['creature_name']} becomes aggressive!"
        
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
            return {"message": "You do not have the Staff of Merlin."}
        
        # Check 3: Staff must have charges
        if player.staff_charges <= 0:
            return {"message": "Nothing happens."}  # Staff is out of charges
        
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
        
        message = f"!ZAPPING!\nYou ZAP the {result['creature_name']} for {result['damage']} damage!"
        message += f"\n(Staff charges remaining: {player.staff_charges})"
        
        if result['creature_died']:
            message += f"\n\nThe {result['creature_name']} is obliterated! You gain {result['points_awarded']} points."
        else:
            message += f"\nThe {result['creature_name']} has {target_creature.stamina}/{target_creature.max_stamina} stamina remaining."
        
        return {
            "message": message,
            "combat": True,
            "creature_died": result['creature_died']
        }

    async def stab(self, player: Player, target_name: str) -> Dict:
        """Stab with dagger or knife"""
        if not target_name:
            return {"message": "Stab what?"}
        
        # Check if player has dagger or knife
        has_dagger = any("dagger" in item.lower() for item in player.inventory)
        has_knife = any("knife" in item.lower() for item in player.inventory)
        
        if not has_dagger and not has_knife:
            return {"message": "But you do not have the dagger or knife!"}
        
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
        
        # Stab attack (6-9 damage)
        result = await self.game_state.player_attack_creature(player, target_creature, weapon)
        
        message = f"You STAB the {result['creature_name']} with your {weapon} for {result['damage']} damage!"
        
        if result['creature_died']:
            message += f"\n\nThe {result['creature_name']} is dead! You gain {result['points_awarded']} points."
        else:
            message += f"\nThe {result['creature_name']} has {target_creature.stamina}/{target_creature.max_stamina} stamina remaining."
        
        return {
            "message": message,
            "combat": True,
            "creature_died": result['creature_died']
        }
    
    async def burn(self, player: Player, target_name: str) -> Dict:
        """Burn with flamethrower"""
        if not target_name:
            return {"message": "Burn what?"}
        
        # Check if player has flamethrower
        has_flamethrower = any("flamethrower" in item.lower() for item in player.inventory)
        
        if not has_flamethrower:
            return {"message": "With what? You need a flamethrower!"}
        
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
        
        # Burn attack (50-75 damage)
        result = await self.game_state.player_attack_creature(player, target_creature, "Flamethrower")
        
        message = f"You BURN the {result['creature_name']} with your Flamethrower for {result['damage']} damage!"
        
        if result['creature_died']:
            message += f"\n\nThe {result['creature_name']} is incinerated! You gain {result['points_awarded']} points."
        else:
            message += f"\nThe {result['creature_name']} has {target_creature.stamina}/{target_creature.max_stamina} stamina remaining."
        
        return {
            "message": message,
            "combat": True,
            "creature_died": result['creature_died']
        }
    
    async def shoot(self, player: Player, target_name: str) -> Dict:
        """Shoot with arrow at creature or player"""
        if not target_name:
            return {"message": "Shoot what?"}
        
        # Check if player has arrow
        has_arrow = any("arrow" in item.lower() for item in player.inventory)
        
        if not has_arrow:
            return {"message": "You have no Arrow!"}
        
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
            if arrow_item and player.current_room in self.game_state.rooms:
                room = self.game_state.rooms[player.current_room]
                if arrow_item not in room.objects:
                    room.objects.append(arrow_item)
            
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
        
        # Shoot attack (30-40 damage) - Arrow is dropped in current room
        result = await self.game_state.player_attack_creature(player, target_creature, "Arrow")
        
        # Remove arrow from inventory and drop it in the current room
        arrow_item = None
        for item in player.inventory:
            if "arrow" in item.lower():
                arrow_item = item
                player.remove_item(item)
                break
        
        # Add arrow to current room's objects
        if arrow_item and player.current_room in self.game_state.rooms:
            room = self.game_state.rooms[player.current_room]
            if arrow_item not in room.objects:
                room.objects.append(arrow_item)
        
        message = f"You SHOOT the {result['creature_name']} with your Arrow for {result['damage']} damage!"
        message += "\nYour arrow falls to the ground."
        
        if result['creature_died']:
            message += f"\n\nThe {result['creature_name']} is dead! You gain {result['points_awarded']} points."
        else:
            message += f"\nThe {result['creature_name']} has {target_creature.stamina}/{target_creature.max_stamina} stamina remaining."
        
        return {
            "message": message,
            "combat": True,
            "creature_died": result['creature_died'],
            "inventory_changed": True
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
        
        # Show new location (same as LOOK command)
        look_result = await self.look(player)
        
        return {
            "message": f"You concentrate... and suddenly find yourself elsewhere!\n\n{look_result['message']}",
            "room_changed": True,
            "teleport": True
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
        
        # Get room info for display
        look_result = await self.look(player)
        
        return {
            "message": f"You vanish in a puff of smoke!\n\n{look_result['message']}",
            "moved": True,
            "old_room": old_room,
            "direction": "magically"
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

    async def quit_game(self, player: Player) -> Dict:
        """
        Quit and save player data
        Based on original game QUIT command
        """
        # Check if player is under influence of vodka (if we implement that)
        # Original: IFV>1PRINT"Unable to QUIT while under the influence"
        
        # Check if player is poisoned (if we implement that)
        # Original: IFMPRINT"I need some medical help for the POISON"
        
        # Check if stamina is too low
        if player.stamina < 6:
            return {
                "message": "You are too weak to quit safely. Rest first!",
                "quit_denied": True
            }
        
        # Save player data
        from player_data import save_player
        
        save_data = player.to_save_dict()
        
        # Add password hash (stored on player object)
        if hasattr(player, 'password_hash'):
            save_data['password_hash'] = player.password_hash
        else:
            print(f"⚠️  Warning: Player {player.name} has no password_hash!")
            return {
                "message": "Error: Cannot save without password. Please contact admin.",
                "quit_denied": True
            }
        
        print(f"Saving player {player.name} data: {save_data}")
        success = save_player(save_data)
        
        if success:
            return {
                "message": "Your progress has been saved. Farewell!",
                "quit": True,
                "disconnect": True
            }
        else:
            return {
                "message": "Error saving your data. Please try again.",
                "quit_denied": True
            }
