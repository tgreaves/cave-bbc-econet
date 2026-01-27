"""
Player class for Cave-Plus
"""
import random

class Player:
    def __init__(self, name: str, websocket, saved_data: dict = None):
        self.name = name  # Login name (never changes)
        self.display_name = name  # Display name (can be changed by ALIAS for Wizards)
        self.websocket = websocket
        self.player_id = id(self)  # Unique ID for this session
        
        # Disconnect tracking
        self.is_disconnected = False
        self.disconnect_time = None
        self.disconnect_timeout = 300  # 5 minutes in seconds
        
        if saved_data:
            # Load from saved data (BBC Micro format: name, score, room)
            self.room_id = saved_data.get('room_id', 1)
            self.score = saved_data.get('score', 0)
            
            # Calculate rank from score
            self.update_rank()
            
            # Everything else starts fresh on login
            self.kills = 0
            self.deaths = 0
            self.inventory = []
            self.staff_charges = 0
            self.vodka_level = 0
            self.poisoned = False
            self.fast_mode = False  # BBC Micro: j=FALSE (line 200)
            self.has_magic_item = False  # BBC Micro: h=FALSE (line 200)
            self.max_inventory = self._calculate_max_inventory()
        else:
            # New player
            self.room_id = 1  # Start at main entrance
            self.score = 0
            self.rank = "Novice"
            self.kills = 0
            self.deaths = 0
            self.inventory = []
            self.staff_charges = 0
            self.vodka_level = 0
            self.poisoned = False
            self.fast_mode = False  # BBC Micro: j=FALSE (line 200)
            self.has_magic_item = False  # BBC Micro: h=FALSE (line 200)
            self.max_inventory = 3
        
        # Calculate stamina based on score (always fresh on login)
        self.calculate_stamina()
        # Respawn with random stamina (50-100% of max)
        self.respawn()
        
        # Stamina regeneration tracking (BBC Micro line 2050: i=TIME)
        import time
        self.last_command_time = time.time()
        
        # FORCE command state tracking
        self.force_state = None  # None, 'awaiting_command', 'awaiting_method'
        self.force_target = None
        self.force_command = None
    
    def to_save_dict(self):
        """
        Convert player to dictionary for saving to disk
        BBC Micro only saves: name, score, room (B), password
        Rank is calculated from score on login
        """
        return {
            'name': self.name,
            'room_id': self.room_id,
            'score': self.score
        }
        
    def _calculate_max_inventory(self):
        """Calculate max inventory based on rank"""
        if self.rank == "Wizard":
            return 7
        elif self.rank == "Master Caver":
            return 6
        elif self.rank == "Warrior":
            return 5
        elif self.rank == "Adventurer":
            return 4
        else:
            return 3
    
    def calculate_stamina(self):
        """
        Calculate max stamina based on score and rank (from original game logic)
        Base: 50 + score/5
        Wizard bonus: +250
        Master Caver bonus: +50
        Warrior bonus: +25
        """
        # Base stamina calculation
        max_stam = 50 + (self.score // 5)
        
        # Rank bonuses
        if self.rank == "Wizard":
            max_stam += 250
        elif self.rank == "Master Caver":
            max_stam += 50
        elif self.rank == "Warrior":
            max_stam += 25
        
        self.max_stamina = max_stam
        
    def respawn(self):
        """
        Respawn player with randomized stamina (50-100% of max)
        Matches original: D=J/2+RND(J/2)
        """
        self.calculate_stamina()
        # Random stamina between 50% and 100% of max
        self.stamina = self.max_stamina // 2 + random.randint(0, self.max_stamina // 2)
        
    def to_dict(self):
        """Convert player to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "room_id": self.room_id,
            "stamina": int(self.stamina),  # Round to whole number for display
            "max_stamina": self.max_stamina,
            "inventory": self.inventory,
            "max_inventory": self.max_inventory,
            "score": self.score,
            "rank": self.rank,
            "kills": self.kills,
            "deaths": self.deaths,
            "staff_charges": self.staff_charges,
            "vodka_level": self.vodka_level,
            "poisoned": self.poisoned,
            "is_disconnected": self.is_disconnected
        }
    
    def mark_disconnected(self):
        """Mark player as disconnected but keep in game"""
        import time
        self.is_disconnected = True
        self.disconnect_time = time.time()
        self.websocket = None  # Clear websocket reference
    
    def reconnect(self, websocket):
        """Reconnect player with new websocket"""
        self.is_disconnected = False
        self.disconnect_time = None
        self.websocket = websocket
    
    def is_timeout_expired(self) -> bool:
        """Check if disconnect timeout has expired"""
        if not self.is_disconnected or self.disconnect_time is None:
            return False
        import time
        return (time.time() - self.disconnect_time) > self.disconnect_timeout
    
    def can_carry_more(self):
        """Check if player can carry more items"""
        return len(self.inventory) < self.max_inventory
    
    def add_item(self, item: str):
        """
        Add item to inventory
        BBC Micro line 5856: IFINSTR(Hh$,D$)<>0 h=TRUE
        Sets magic item flag if picking up a magic item
        """
        if self.can_carry_more():
            self.inventory.append(item)
            # Check if this is a magic item (BBC Micro line 5856)
            if self.is_magic_item(item):
                self.has_magic_item = True
            return True
        return False
    
    def remove_item(self, item: str):
        """
        Remove item from inventory
        BBC Micro line 6025: IFINSTR(Hh$,D$)<>0 h=FALSE
        Clears magic item flag if dropping a magic item
        """
        if item in self.inventory:
            self.inventory.remove(item)
            # Check if this was a magic item (BBC Micro line 6025)
            if self.is_magic_item(item):
                self.has_magic_item = False
            return True
        return False
    
    @staticmethod
    def is_magic_item(item: str) -> bool:
        """
        Check if an item is a magic item
        BBC Micro line 40: Hh$="CrystalAmuletStaffShieldGuardian"
        Magic items: Crystal Ball, Amulet, Staff of Merlin, Shield, Guardian
        """
        item_lower = item.lower()
        magic_items = ["crystal", "amulet", "staff", "shield", "guardian"]
        return any(magic in item_lower for magic in magic_items)
    
    def has_item(self, item: str):
        """Check if player has an item"""
        return item in self.inventory
    
    def take_damage(self, amount: int):
        """Take damage"""
        self.stamina = max(0, self.stamina - amount)
        return self.stamina <= 0  # Returns True if dead
    
    def heal(self, amount: int):
        """Heal player"""
        self.stamina = min(self.max_stamina, self.stamina + amount)
    
    def add_score(self, points: int):
        """Add to score and update rank"""
        self.score += points
        self.update_rank()
        # Recalculate stamina when score changes
        self.calculate_stamina()
    
    def update_rank(self):
        """Update player rank based on score"""
        if self.score >= 1000:
            self.rank = "Wizard"
            self.max_inventory = 7
        elif self.score >= 500:
            self.rank = "Master Caver"
            self.max_inventory = 6
        elif self.score >= 200:
            self.rank = "Warrior"
            self.max_inventory = 5
        elif self.score >= 50:
            self.rank = "Adventurer"
            self.max_inventory = 4
        else:
            self.rank = "Novice"
            self.max_inventory = 3


    def charge_staff(self):
        """Charge the Staff of Merlin when picked up (gets 7 charges)"""
        self.staff_charges = 7
    
    def use_staff_charge(self) -> bool:
        """
        Use one charge from the Staff of Merlin
        Returns True if charge was used, False if no charges left
        """
        if self.staff_charges > 0:
            self.staff_charges -= 1
            return True
        return False
    
    def has_staff(self) -> bool:
        """Check if player has the Staff of Merlin"""
        return any("staff" in item.lower() and "merlin" in item.lower() for item in self.inventory)
    
    def drink_vodka(self) -> dict:
        """
        Drink vodka - increases vodka level, heals stamina
        Based on line 5300: V=V+1:?&A01=1:D=D+5+RND(2)
        Line 5320: IFV>5 V=V-1:?&A01=0:D=D-7
        
        Note: Original game shows NO message when successfully drinking vodka
        """
        import random
        
        # Check if already too drunk
        if self.vodka_level > 5:
            self.vodka_level -= 1
            damage = 7
            self.take_damage(damage)
            return {
                "message": "WWhat!! MORE Vodka?",
                "beeps": 1,
                "too_drunk": True,
                "damage": damage
            }
        
        # Drink vodka (silently - no message in original)
        self.vodka_level += 1
        heal_amount = 5 + random.randint(1, 2)  # 6-7 stamina
        self.heal(heal_amount)
        
        return {
            "message": "",  # No message in original game
            "healed": heal_amount,
            "vodka_level": self.vodka_level
        }
    
    def drink_poison(self) -> dict:
        """
        Drink poison - sets poisoned flag
        Based on line 5340: M=TRUE:PRINT"It tastes terrible!"
        """
        self.poisoned = True
        return {
            "message": "It tastes terrible!",
            "beeps": 1,
            "poisoned": True
        }
    
    def drink_medicine(self) -> dict:
        """
        Drink medicine - cures poison if poisoned, otherwise just tastes bad
        Based on line 5350: M=FALSE:PRINT"You are cured"
        Line 5360: PRINT"YUCK!"
        """
        if self.poisoned:
            self.poisoned = False
            return {
                "message": "You are cured",
                "cured": True
            }
        else:
            return {
                "message": "YUCK!",
                "beeps": 1
            }
    
    def update_vodka_level(self):
        """
        Slowly decrease vodka level over time (sobering up)
        Based on line 1460: IFV>1 V=V-.001
        Called each game tick
        """
        if self.vodka_level > 1:
            self.vodka_level -= 0.001
            if self.vodka_level < 1:
                self.vodka_level = 0
    
    def update_poison_damage(self):
        """
        Apply poison damage over time
        Based on line 1480: IFM D=D-0.05
        Called each game tick
        """
        if self.poisoned:
            self.take_damage(0.05)
    
    def is_drunk(self) -> bool:
        """Check if player is drunk (vodka level > 1)"""
        return self.vodka_level > 1


    def regenerate_stamina(self):
        """
        Regenerate stamina based on time elapsed since last command
        BBC Micro line 2050:
        - D=D-0.2                        : REM Stamina cost for command
        - D=D+(TIME-i)/(2000+G*1000):i=TIME  : REM Regeneration
        - IFD>J D=J                      : REM Cap at maximum
        
        TIME is in centiseconds (1/100 second)
        G is wizard flag: 0 for non-wizards, -1 for wizards
        So: (2000+G*1000) = 2000 for non-wizards, 1000 for wizards
        Wizards regenerate slower!
        """
        import time
        
        # Calculate time elapsed in seconds
        current_time = time.time()
        time_elapsed = current_time - self.last_command_time
        
        # Convert to centiseconds (BBC Micro TIME unit)
        centiseconds_elapsed = time_elapsed * 100
        
        # Apply command cost (0.2 stamina per command)
        self.stamina -= 0.2
        
        # Calculate regeneration
        # Wizards: divisor = 1000 (slower regen)
        # Non-wizards: divisor = 2000 (faster regen)
        wizard_penalty = -1 if self.rank == "Wizard" else 0
        divisor = 2000 + wizard_penalty * 1000
        
        regeneration = centiseconds_elapsed / divisor
        self.stamina += regeneration
        
        # Cap at maximum
        if self.stamina > self.max_stamina:
            self.stamina = self.max_stamina
        
        # Prevent stamina from going below 0
        if self.stamina < 0:
            self.stamina = 0
        
        # Update last command time
        self.last_command_time = current_time
