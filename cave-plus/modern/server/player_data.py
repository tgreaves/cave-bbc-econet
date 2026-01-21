"""
Player Data Persistence System
Handles saving/loading player data like the original BBC Micro game
"""

import json
import hashlib
import os
import time
from typing import Optional, Dict, Tuple

# Use absolute path relative to this file
PLAYER_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "player_data")

# Authentic BBC Micro disk timing (in seconds)
DISK_SEEK_TIME = 0.2  # Head seek time
DISK_READ_TIME = 0.4  # Read operation
DISK_WRITE_TIME = 0.6  # Write operation (slower than read)

def ensure_data_dir():
    """Create player data directory if it doesn't exist"""
    os.makedirs(PLAYER_DATA_DIR, exist_ok=True)
    print(f"Player data directory: {os.path.abspath(PLAYER_DATA_DIR)}")

def hash_password(password: str) -> str:
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_checksum(data: Dict) -> str:
    """Calculate checksum for data validation (like original game)"""
    # Concatenate key fields like original: name+score+room+wizard+password
    check_string = f"{data['name']}{data['score']}{data['room_id']}{data['rank']}{data['password_hash']}"
    return hashlib.md5(check_string.encode()).hexdigest()

def save_player(player_data: Dict) -> Tuple[bool, float]:
    """
    Save player data to file
    Format similar to original: name, score, room, wizard_flag, password, checksum
    Returns: (success, disk_time_seconds)
    """
    ensure_data_dir()
    
    start_time = time.time()
    
    try:
        # Make a copy to avoid modifying original
        data_to_save = player_data.copy()
        
        # Add checksum
        data_to_save['checksum'] = calculate_checksum(player_data)
        
        filename = os.path.join(PLAYER_DATA_DIR, f"{player_data['name']}.json")
        
        # Simulate disk seek time
        time.sleep(DISK_SEEK_TIME)
        
        with open(filename, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        
        # Simulate disk write time
        time.sleep(DISK_WRITE_TIME)
        
        elapsed = time.time() - start_time
        print(f"✅ Saved player data for {player_data['name']} to {filename} (took {elapsed:.2f}s)")
        return True, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error saving player data: {e}")
        import traceback
        traceback.print_exc()
        return False, elapsed

def load_player(name: str, password: str) -> Optional[Tuple[Dict, float]]:
    """
    Load player data from file and verify password
    Returns: (player_data, disk_time_seconds) or None if player doesn't exist or password is wrong
    """
    ensure_data_dir()
    
    start_time = time.time()
    filename = os.path.join(PLAYER_DATA_DIR, f"{name}.json")
    
    if not os.path.exists(filename):
        return None
    
    try:
        # Simulate disk seek time
        time.sleep(DISK_SEEK_TIME)
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Simulate disk read time
        time.sleep(DISK_READ_TIME)
        
        # Verify checksum
        stored_checksum = data.get('checksum', '')
        data_copy = data.copy()
        data_copy.pop('checksum', None)
        calculated_checksum = calculate_checksum(data_copy)
        
        if stored_checksum != calculated_checksum:
            print(f"Checksum mismatch for player {name}")
            return None
        
        # Verify password
        password_hash = hash_password(password)
        if data.get('password_hash') != password_hash:
            return None
        
        elapsed = time.time() - start_time
        return data, elapsed
    except Exception as e:
        print(f"Error loading player data: {e}")
        return None

def player_exists(name: str) -> bool:
    """Check if a player file exists"""
    ensure_data_dir()
    filename = os.path.join(PLAYER_DATA_DIR, f"{name}.json")
    exists = os.path.exists(filename)
    print(f"Checking if player {name} exists: {exists} ({filename})")
    return exists

def create_player(name: str, password: str) -> Dict:
    """
    Create new player data
    Returns initial player data dict
    """
    import random
    
    player_data = {
        'name': name,
        'password_hash': hash_password(password),
        'score': 0,
        'room_id': 1,  # Start at entrance
        'rank': 'Novice',
        'kills': 0,
        'deaths': 0,
        'inventory': [],
        'max_stamina': 50,  # Base stamina for new player
        'stamina': 25 + random.randint(0, 25)  # 50-100% of max
    }
    
    return player_data
