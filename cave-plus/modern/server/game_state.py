"""
Game State Management for Cave-Plus
"""

import yaml
import random
from typing import Dict, List, Optional
from player import Player
from creature import Creature, CREATURE_DATA, INITIAL_CREATURE_PLACEMENT

class GameState:
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.rooms: Dict[int, dict] = {}
        self.objects: Dict[int, List[str]] = {}  # room_id -> list of objects
        self.creatures: Dict[int, Creature] = {}  # creature_id -> Creature
        self.creatures_by_room: Dict[int, List[int]] = {}  # room_id -> list of creature_ids
        self.rooms_with_graphics = set()
        self.tick_count = 0
        # CCM activity level (0-9), default 2 (from OBJINIT file byte 0)
        # Controls creature attack/movement frequency
        # Wizards can change this with ACTIVITY command
        self.activity_level = 2
        
    async def initialize(self):
        """Load game data"""
        await self.load_rooms()
        await self.load_initial_objects()
        await self.load_creatures()
        print(f"✅ Loaded {len(self.rooms)} rooms")
        print(f"✅ {len(self.rooms_with_graphics)} rooms have graphics")
        print(f"✅ Spawned {len(self.creatures)} creatures")
    
    async def load_rooms(self):
        """Load room data from YAML"""
        try:
            with open("../rooms-parsed.yml", "r") as f:
                data = yaml.safe_load(f)
                
            rooms_data = data.get("rooms", {})
            
            for room_id, room_info in rooms_data.items():
                self.rooms[room_id] = {
                    "id": room_id,
                    "name": room_info.get("name", f"Room {room_id}"),
                    "description": room_info.get("description", "").strip(),
                    "exits": room_info.get("exits", {}),
                    "note": room_info.get("note", "")
                }
                
                # Initialize empty object list for each room
                self.objects[room_id] = []
                
        except Exception as e:
            print(f"Error loading rooms: {e}")
            # Create a minimal fallback room
            self.rooms[1] = {
                "id": 1,
                "name": "Main Entrance",
                "description": "This is the main entrance to the cave.",
                "exits": {},
                "note": ""
            }
            self.objects[1] = []
    
    async def load_initial_objects(self, clear_existing: bool = False):
        """
        Load initial object placement
        Based on OBJINIT and DEFPROCU (line 1001)
        DEFPROCU randomly places objects 11-15 in rooms excluding wizard's domain (16-20)
        """
        # Clear existing objects if regenerating
        if clear_existing:
            self.objects.clear()
            # Initialize empty lists for all rooms
            for room_id in self.rooms.keys():
                self.objects[room_id] = []
        
        # Graphics availability (rooms with PNG files)
        self.rooms_with_graphics = {
            2, 3, 9, 11, 12, 13, 16, 17, 18, 19, 20, 25, 29, 30,
            32, 37, 49, 50, 51, 55, 60, 99, 141, 148, 150
        }
        
        # Fixed object placement (objects 1-15 from OBJINIT - corrected mapping)
        # The decoder was off by one starting at object 5 (Bow)
        fixed_placement = {
            32: ["Vodka"],           # Object 1
            5: ["Stick", "Poison"],  # Objects 2, 3
            30: ["Dagger"],          # Object 4
            11: ["Bow"],             # Object 5 (was incorrectly labeled "Arrow")
            15: ["Arrow"],           # Object 6 (was incorrectly labeled "Medicine")
            25: ["Medicine"],        # Object 7 (was incorrectly labeled "Knife")
            20: ["Knife", "Flamethrower"],  # Objects 8, 9 (was "Flamethrower", "Ruby")
            37: ["Ruby"],            # Object 10 (was incorrectly labeled "Shield")
        }
        
        for room_id, objects in fixed_placement.items():
            if room_id not in self.objects:
                self.objects[room_id] = []
            self.objects[room_id] = list(objects)  # Replace with fresh copy
        
        # Random object placement (objects 11-15 from OBJINIT)
        # These all start in room 1 and are randomly placed by DEFPROCU
        # DEFPROCU: REPEATT=RND(b):UNTILT>20ORT<16
        # This places objects in random rooms excluding wizard's domain (16-20)
        random_objects = [
            "Shield",          # Object 11 (was incorrectly labeled "Crystal")
            "Crystal Ball",    # Object 12 (was incorrectly labeled "Staff")
            "Staff of Merlin", # Object 13 (was incorrectly labeled "Amulet")
            "Amulet",          # Object 14 (was incorrectly labeled "Treasure")
            "Treasure",        # Object 15 (was incorrectly labeled "Guardian")
        ]
        
        max_room = max(self.rooms.keys())
        for obj in random_objects:
            # Find random room excluding wizard's domain (16-20)
            while True:
                room = random.randint(1, max_room)
                if room > 20 or room < 16:
                    break
            
            if room not in self.objects:
                self.objects[room] = []
            self.objects[room].append(obj)
    
    async def load_creatures(self, clear_existing: bool = False):
        """Load and spawn initial creatures"""
        # Clear existing creatures if regenerating
        if clear_existing:
            self.creatures.clear()
            self.creatures_by_room.clear()
        
        creature_id_counter = 1000  # Start creature instances at 1000
        
        for room_id, creature_list in INITIAL_CREATURE_PLACEMENT.items():
            if room_id not in self.creatures_by_room:
                self.creatures_by_room[room_id] = []
            
            for obj_id, initial_stamina in creature_list:
                if obj_id in CREATURE_DATA:
                    name, properties = CREATURE_DATA[obj_id]
                    
                    # Skip creatures with 0 stamina (they're inactive/dead)
                    # Exception: Dragon should spawn with full health
                    if initial_stamina == 0 and obj_id != 16:
                        continue
                    
                    # Dragon gets special treatment - spawn with full health
                    if obj_id == 16:
                        initial_stamina = 600  # Dragon's max health
                    
                    # Create creature instance
                    creature = Creature(
                        obj_id=creature_id_counter,
                        name=name if name else f"Creature {obj_id}",
                        properties=properties,
                        room_id=room_id,
                        initial_stamina=initial_stamina
                    )
                    
                    self.creatures[creature_id_counter] = creature
                    self.creatures_by_room[room_id].append(creature_id_counter)
                    creature_id_counter += 1
    
    async def update(self):
        """Update game state (called every tick)"""
        self.tick_count += 1
        
        # Store attack events and movement events to broadcast
        attack_events = []
        movement_events = []
        
        # Update all creatures
        for creature_id, creature in list(self.creatures.items()):
            if creature.is_dead:
                continue
            
            # Check if creature should walk (10x more likely than teleport)
            # Pass activity_level to respect BBC Micro behavior
            if creature.should_walk(self.activity_level):
                movement_info = await self.walk_creature(creature)
                if movement_info:
                    movement_events.append(movement_info)
            # Check if creature should teleport (rare)
            elif creature.should_teleport(self.activity_level):
                movement_info = await self.teleport_creature(creature)
                if movement_info:
                    movement_events.append(movement_info)
            
            # Check if creature should follow a player
            players_in_room = self.get_players_in_room(creature.room_id)
            if players_in_room:
                target = random.choice(players_in_room)
                if creature.should_follow(target):
                    creature.target_player = target.name
            
            # Check if creature should attack
            # Pass activity_level to respect BBC Micro behavior
            if creature.should_attack(self.activity_level):
                attack_info = await self.creature_attack(creature)
                if attack_info:
                    attack_events.append(attack_info)
        
        # Return both attack and movement events for broadcasting
        return {"attacks": attack_events, "movements": movement_events}
    
    def add_player(self, player: Player):
        """Add a player to the game"""
        self.players[player.name] = player
    
    def remove_player(self, player: Player):
        """Remove a player from the game"""
        if player.name in self.players:
            del self.players[player.name]
    
    def get_player(self, name: str) -> Optional[Player]:
        """Get a player by name (case-insensitive, uppercase match)"""
        # Apply BBC Micro FNB function: uppercase, letters only
        normalized_name = ''.join(c.upper() for c in name if c.isalpha())
        return self.players.get(normalized_name)
    
    def get_room(self, room_id: int) -> Optional[dict]:
        """Get room data"""
        return self.rooms.get(room_id)
    
    def get_players_in_room(self, room_id: int) -> List[Player]:
        """Get all players in a specific room"""
        return [p for p in self.players.values() if p.room_id == room_id]
    
    def get_objects_in_room(self, room_id: int) -> List[str]:
        """Get all objects in a specific room"""
        return self.objects.get(room_id, [])
    
    def add_object_to_room(self, room_id: int, obj: str):
        """Add an object to a room"""
        if room_id in self.objects:
            self.objects[room_id].append(obj)
    
    def remove_object_from_room(self, room_id: int, obj: str):
        """Remove an object from a room"""
        if room_id in self.objects and obj in self.objects[room_id]:
            self.objects[room_id].remove(obj)
    
    def can_move(self, player: Player, direction: str) -> tuple[bool, Optional[int]]:
        """Check if player can move in a direction"""
        room = self.get_room(player.room_id)
        
        if not room:
            return False, None
        
        exits = room.get("exits", {})
        next_room = exits.get(direction)
        
        if next_room and next_room in self.rooms:
            return True, next_room
        
        return False, None
    
    def get_creatures_in_room(self, room_id: int) -> List[Creature]:
        """Get all creatures in a specific room"""
        creature_ids = self.creatures_by_room.get(room_id, [])
        
        # In mortuary (room 19), show dead creatures
        # In other rooms, only show living creatures
        if room_id == 19:
            return [self.creatures[cid] for cid in creature_ids if cid in self.creatures]
        else:
            return [self.creatures[cid] for cid in creature_ids if cid in self.creatures and not self.creatures[cid].is_dead]
    
    def reset_creatures_targeting_player(self, player_name: str):
        """
        Reset all creatures that are targeting a specific player
        Called when player dies/respawns so creatures forget about them
        """
        for creature in self.creatures.values():
            if creature.target_player == player_name:
                creature.target_player = None
                # Reset aggression for passive creatures
                if creature.behavior == 'B':
                    creature.is_aggressive = False
                print(f"DEBUG: {creature.name} forgot about {player_name}")
    
    async def teleport_creature(self, creature: Creature):
        """Teleport creature to a random room"""
        import random as rand
        
        # Messages for disappearing/appearing
        disappear_msgs = ["vanishes", "dematerialises", "disappears"]
        appear_msgs = ["appears", "materialises", "appears"]
        
        old_room = creature.room_id
        
        # Remove from current room
        if creature.room_id in self.creatures_by_room:
            if creature.obj_id in self.creatures_by_room[creature.room_id]:
                self.creatures_by_room[creature.room_id].remove(creature.obj_id)
        
        # Pick random room
        new_room = rand.choice(list(self.rooms.keys()))
        creature.room_id = new_room
        
        # Add to new room
        if new_room not in self.creatures_by_room:
            self.creatures_by_room[new_room] = []
        self.creatures_by_room[new_room].append(creature.obj_id)
        
        # Return movement messages for broadcasting
        return {
            "type": "teleport",
            "old_room": old_room,
            "new_room": new_room,
            "creature_name": creature.name,
            "disappear_msg": rand.choice(disappear_msgs),
            "appear_msg": rand.choice(appear_msgs)
        }
    
    async def walk_creature(self, creature: Creature):
        """Move creature to an adjacent room (normal movement)"""
        import random as rand
        
        old_room = creature.room_id
        room = self.get_room(old_room)
        
        if not room or not room.get("exits"):
            return None
        
        # Pick a random exit
        exits = list(room["exits"].values())
        if not exits:
            return None
        
        new_room = rand.choice(exits)
        
        # Remove from current room
        if creature.room_id in self.creatures_by_room:
            if creature.obj_id in self.creatures_by_room[creature.room_id]:
                self.creatures_by_room[creature.room_id].remove(creature.obj_id)
        
        # Move to new room
        creature.room_id = new_room
        
        # Add to new room
        if new_room not in self.creatures_by_room:
            self.creatures_by_room[new_room] = []
        self.creatures_by_room[new_room].append(creature.obj_id)
        
        # Return movement messages for broadcasting
        return {
            "type": "walk",
            "old_room": old_room,
            "new_room": new_room,
            "creature_name": creature.name
        }
    
    async def move_creature(self, creature: Creature, target_room: int):
        """Move creature to a specific room (for SUMMON command)"""
        old_room = creature.room_id
        
        # Remove from current room
        if creature.room_id in self.creatures_by_room:
            if creature.obj_id in self.creatures_by_room[creature.room_id]:
                self.creatures_by_room[creature.room_id].remove(creature.obj_id)
        
        # Move to target room
        creature.room_id = target_room
        
        # Add to new room
        if target_room not in self.creatures_by_room:
            self.creatures_by_room[target_room] = []
        self.creatures_by_room[target_room].append(creature.obj_id)
        
        return {
            "old_room": old_room,
            "new_room": target_room,
            "creature_name": creature.name
        }
    
    async def creature_attack(self, creature: Creature):
        """Creature attacks a player in the same room"""
        players = self.get_players_in_room(creature.room_id)
        if not players:
            return
        
        # Pick a target (prefer targeted player if in room)
        target = None
        if creature.target_player:
            target = self.get_player(creature.target_player)
            if not target or target.room_id != creature.room_id:
                target = None
        
        if not target:
            target = random.choice(players)
        
        # Calculate damage
        damage = creature.calculate_damage()
        target.take_damage(damage)
        
        print(f"DEBUG: {creature.name} attacks {target.name} for {damage} damage! (Stamina: {target.stamina}/{target.max_stamina})")
        
        # Return attack info for broadcasting
        return {
            "creature": creature.name,
            "target": target.name,
            "damage": damage,
            "verb": creature.get_attack_verb(),
            "room_id": creature.room_id
        }
    
    async def player_attack_creature(self, player: Player, creature: Creature, weapon: Optional[str] = None) -> Dict:
        """Player attacks a creature"""
        # Calculate damage based on weapon
        if weapon and "flamethrower" in weapon.lower():
            # BBC Micro: RND(10)+50 = 51-60 damage
            total_damage = random.randint(51, 60)
        elif weapon and "arrow" in weapon.lower():
            # BBC Micro: RND(10)+30 = 31-40 damage
            total_damage = random.randint(31, 40)
        elif weapon and ("knife" in weapon.lower() or "dagger" in weapon.lower()):
            # BBC Micro: RND(10)+20 = 21-30 damage
            total_damage = random.randint(21, 30)
        elif weapon and "stick" in weapon.lower():
            # Base damage + stick bonus
            base_damage = random.randint(1, 3)
            total_damage = base_damage + 3
        else:
            # Base unarmed damage (1-3)
            total_damage = random.randint(1, 3)
        
        # Apply damage to creature
        creature_died = creature.take_damage(total_damage)
        
        # Make creature aggressive if it wasn't already
        if not creature_died:
            was_aggressive = creature.is_aggressive
            creature.make_aggressive()
            creature.target_player = player.name
            print(f"DEBUG: {creature.name} made aggressive (was: {was_aggressive}, now: {creature.is_aggressive})")
            print(f"DEBUG: {creature.name} attack_chance={creature.attack_chance}, secondary_attack={creature.secondary_attack}")
        
        # Award points if creature died
        points = 0
        if creature_died:
            points = creature.max_stamina // 10  # 1 point per 10 stamina
            player.score += points
            player.kills += 1
            
            # Move creature to mortuary (room 19) - matching BBC Micro behavior
            if creature.room_id in self.creatures_by_room:
                if creature.obj_id in self.creatures_by_room[creature.room_id]:
                    self.creatures_by_room[creature.room_id].remove(creature.obj_id)
            
            # Add to mortuary
            creature.room_id = 19
            if 19 not in self.creatures_by_room:
                self.creatures_by_room[19] = []
            self.creatures_by_room[19].append(creature.obj_id)
        
        return {
            "damage": total_damage,
            "creature_died": creature_died,
            "creature_name": creature.name,
            "points_awarded": points
        }
