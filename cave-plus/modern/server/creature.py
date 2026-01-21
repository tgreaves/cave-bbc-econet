"""
Creature System for Cave-Plus
Based on original BBC Micro game logic
"""

import random
from typing import Dict, Optional

class Creature:
    """Represents a creature/monster in the game"""
    
    # Attack type constants
    ATTACK_MESSAGE = 1
    ATTACK_HIT = 2
    ATTACK_CAVE_COLLAPSE = 3
    ATTACK_AWARD_POINTS = 4
    ATTACK_POISON = 5
    ATTACK_STAB = 6
    ATTACK_UPDATE = 7
    ATTACK_TELEPORT = 8
    ATTACK_FORCE_COMMAND = 9
    ATTACK_BITE = 10
    ATTACK_BURN = 11
    ATTACK_ZAP = 12
    ATTACK_SHOOT = 13
    
    ATTACK_NAMES = {
        ATTACK_HIT: "hits",
        ATTACK_STAB: "stabs",
        ATTACK_BITE: "bites",
        ATTACK_BURN: "burns",
        ATTACK_ZAP: "zaps",
        ATTACK_SHOOT: "shoots"
    }
    
    def __init__(self, obj_id: int, name: str, properties: str, room_id: int, initial_stamina: int = 0):
        self.obj_id = obj_id
        self.name = name
        self.room_id = room_id
        self.target_player = None  # Player being targeted
        
        # Parse properties string (22 characters)
        # Format: BAAASSTTFFAADDDHHHH
        # B = Behavior (A=Aggressive, B=Passive)
        # AAA = Attack chance (0-999)
        # SS = Secondary attack chance
        # TT = Teleport chance (0-999, *100)
        # FF = Follow chance (0-999, /1000)
        # AA = Attack type (01-13)
        # DDD = Base damage
        # H = 'H' marker
        # HHH = Health points
        
        if len(properties) >= 22:
            self.behavior = properties[0]  # 'A' or 'B'
            self.attack_chance = int(properties[1:4])  # 0-999
            self.secondary_attack = int(properties[4:7])  # 0-999
            self.teleport_chance = int(properties[7:10])  # 0-999
            self.follow_chance = int(properties[10:13])  # 0-999
            self.attack_type = int(properties[13:15])  # 01-13
            self.base_damage = int(properties[15:18])  # Base damage
            self.max_stamina = int(properties[19:22])  # Max stamina
        else:
            # Default values for invalid data
            self.behavior = 'B'
            self.attack_chance = 0
            self.secondary_attack = 0
            self.teleport_chance = 0
            self.follow_chance = 0
            self.attack_type = self.ATTACK_HIT
            self.base_damage = 1
            self.max_stamina = 10
        
        # Current stamina (use initial stamina if provided, otherwise max stamina)
        self.stamina = initial_stamina if initial_stamina > 0 else self.max_stamina
        
        # State flags
        self.is_aggressive = (self.behavior == 'A')  # Aggressive by default?
        self.is_dead = False
        self.last_action_tick = 0
    
    def is_passive(self) -> bool:
        """Check if creature is currently passive"""
        return not self.is_aggressive
    
    def make_aggressive(self):
        """Make creature aggressive (e.g., when attacked) - PROCJ(T,"A")"""
        self.is_aggressive = True
        self.behavior = 'A'  # Update behavior flag (BBC: B$=A$+RIGHT$(B$,LEN(B$)-1))
    
    def make_passive(self):
        """Make creature passive - PROCJ(T,"B")"""
        self.is_aggressive = False
        self.behavior = 'B'  # Update behavior flag
    
    def should_attack(self, activity_level: int = 0) -> bool:
        """
        Determine if creature should attack this tick
        Based on BBC Micro lines 2890-2910:
        - Line 2890: Q=RND(attack_chance):IFQ<=activity_level ANDQ>=1 PROCQ
        - Line 2910: Q=RND(secondary_attack):IFLEFT$(K$,1)="A"ANDQ<=activity_level ANDQ>=1 PROCQ
        
        Aggressive creatures (behavior='A') get TWO attack chances per tick
        """
        if self.is_dead:
            return False
        
        # First attack chance (line 2890) - all creatures
        if self.attack_chance > 0:
            roll = random.randint(1, self.attack_chance)
            if roll <= activity_level and roll >= 1:
                return True
        
        # Second attack chance (line 2910) - only if behavior flag is 'A'
        # BBC: IFLEFT$(K$,1)="A"ANDQ<=activity_level ANDQ>=1PROCQ
        if self.behavior == 'A' and self.secondary_attack > 0:
            roll = random.randint(1, self.secondary_attack)
            if roll <= activity_level and roll >= 1:
                return True
        
        return False
    
    def should_teleport(self, activity_level: int = 0) -> bool:
        """
        Determine if creature should teleport this tick
        Based on BBC Micro line 2920:
        Q=RND(100*teleport_chance):IFQ<=activity_level ANDQ>=1 PROCO(...)
        """
        if self.is_dead:
            return False
        if self.teleport_chance == 0:
            return False
        # Line 2920: RND(100*teleport_chance)
        roll = random.randint(1, 100 * self.teleport_chance)
        return roll <= activity_level and roll >= 1
    
    def should_walk(self, activity_level: int = 0) -> bool:
        """
        Determine if creature should walk to adjacent room this tick
        Based on BBC Micro line 2930:
        Q=RND(10*teleport_chance):IFQ<=activity_level ANDQ>=1 PROCI(...)
        Note: Uses teleport_chance, not a separate walk chance
        """
        if self.is_dead:
            return False
        if self.teleport_chance == 0:
            return False
        # Line 2930: RND(10*teleport_chance) - 10x more likely than teleport
        roll = random.randint(1, 10 * self.teleport_chance)
        return roll <= activity_level and roll >= 1
    
    def should_follow(self, target_player) -> bool:
        """Determine if creature should follow a player"""
        if self.is_dead:
            return False
        if not target_player:
            return False
        roll = random.randint(0, 999)
        return roll < self.follow_chance
    
    def calculate_damage(self) -> int:
        """Calculate damage for an attack (base + random(base/2))"""
        return self.base_damage + random.randint(0, self.base_damage // 2)
    
    def get_attack_verb(self) -> str:
        """Get the verb for this creature's attack type"""
        return self.ATTACK_NAMES.get(self.attack_type, "attacks")
    
    def take_damage(self, damage: int) -> bool:
        """
        Apply damage to creature
        Returns True if creature died
        """
        self.stamina -= damage
        if self.stamina <= 0:
            self.stamina = 0
            self.is_dead = True
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Convert creature to dictionary for client"""
        return {
            "id": self.obj_id,
            "name": self.name,
            "room_id": self.room_id,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
            "is_aggressive": self.is_aggressive,
            "is_dead": self.is_dead,
            "attack_type": self.get_attack_verb()
        }


# Creature database (from data file analysis)
CREATURE_DATA = {
    16: ("Dragon", "B00015000000011160H600"),
    17: ("Troll", "B30005030060002004H080"),
    19: ("Maggot", "B20020005085010006H060"),
    21: ("Author", "B00000210099912120H500"),
    22: ("Spider", "B10010005010010002H040"),
    23: ("Coward", "B50000002000002003H050"),
    24: ("Killer", "B00004080095006008H100"),
    25: ("Viper", "B20004060050010006H035"),
    26: ("Cobra", "B20004060050010006H035"),
    27: ("Python", "B20004060050010006H035"),
    28: ("Adder", "B20004060050010006H035"),
    29: ("Worm", "B95000030000002002H005"),
    30: ("Drunk", "B30010070020002002H040"),
    32: ("Toad", "B50010020040010006H040"),
    34: ("Guardian", "B00000000000012050H999"),
    35: ("Goblin", "B50010020040006006H050"),
    37: ("Dwarf", "B50010020040010008H060"),
    38: ("Necromancer", "B20010010050012030H500"),
    39: ("Centipede", "B50010020040010008H080"),
    41: ("Skeleton", "B10000505005002001H100"),
    42: ("Caveman", "B10000505005002001H150"),
}

# Initial creature placement (from OBJINIT file - corrected with 4-byte header offset)
INITIAL_CREATURE_PLACEMENT = {
    3: [(35, 50)],  # Goblin
    5: [(18, 48)],  # (unnamed)
    8: [(40, 100)],  # (unnamed)
    11: [(19, 67)],  # Maggot
    13: [(36, 20), (37, 60)],  # (unnamed), Dwarf
    14: [(39, 80)],  # (unnamed)
    20: [(21, 579), (24, 112), (29, 6), (33, 0)],  # Author, Killer, Worm, (unnamed)
    23: [(17, 87)],  # Troll
    26: [(25, 42), (26, 42), (27, 42), (28, 42)],  # Viper, Cobra, Python, Adder
    32: [(30, 55)],  # Drunk
    37: [(38, 50)],  # Necromancer
    38: [(16, 784)],  # Dragon (in Dragon's Lair!)
    39: [(20, 34)],  # (unnamed)
    46: [(23, 38)],  # Coward
    55: [(34, 65535)],  # Guardian
    63: [(31, 48), (32, 60)],  # (unnamed), Toad
    67: [(22, 49)],  # Spider
    83: [(41, 100)],  # Skeleton
    85: [(42, 150)],  # Caveman
}
