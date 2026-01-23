#!/usr/bin/env python3
"""
Player Data Tool for Cave-Plus
Allows manipulation of player data files with automatic checksum recalculation
"""

import sys
import os
import json
import hashlib
import argparse

def calculate_rank(score: int) -> str:
    """Calculate rank based on score (matching server logic)"""
    if score >= 1000:
        return "Wizard"
    elif score >= 500:
        return "Master Caver"
    elif score >= 200:
        return "Warrior"
    elif score >= 50:
        return "Adventurer"
    else:
        return "Novice"

def calculate_checksum(data: dict) -> str:
    """Calculate checksum for data validation (matching server logic)"""
    check_string = f"{data['name']}{data['score']}{data['room_id']}{data['password_hash']}"
    return hashlib.md5(check_string.encode()).hexdigest()

def load_player(filepath: str) -> dict:
    """Load player data from JSON file"""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        return json.load(f)

def save_player(filepath: str, data: dict):
    """Save player data with only required fields and recalculated checksum"""
    # Keep only the fields that should be saved
    saved_fields = {
        'name': data['name'],
        'score': data['score'],
        'room_id': data['room_id'],
        'password_hash': data['password_hash']
    }
    
    # Calculate checksum
    saved_fields['checksum'] = calculate_checksum(saved_fields)
    
    # Save to file
    with open(filepath, 'w') as f:
        json.dump(saved_fields, f, indent=2)
    
    calculated_rank = calculate_rank(saved_fields['score'])
    print(f"✅ Saved {filepath}")
    print(f"   Rank (calculated): {calculated_rank}")
    print(f"   Checksum: {saved_fields['checksum']}")

def display_player(data: dict):
    """Display player information"""
    calculated_rank = calculate_rank(data['score'])
    print("\n" + "="*50)
    print(f"Player: {data['name']}")
    print("="*50)
    print(f"Score:       {data['score']}")
    print(f"Room:        {data['room_id']}")
    print(f"Rank:        {calculated_rank} (calculated from score)")
    print(f"Checksum:    {data.get('checksum', 'MISSING')}")
    print("="*50)
    print("Note: Only name, score, room_id, password_hash are saved")
    print("      Rank, stamina, inventory, etc. are calculated on login")
    print("="*50 + "\n")

def verify_checksum(data: dict) -> bool:
    """Verify if checksum is valid"""
    stored = data.get('checksum', '')
    data_copy = data.copy()
    data_copy.pop('checksum', None)
    calculated = calculate_checksum(data_copy)
    return stored == calculated

def cmd_show(args):
    """Show player information"""
    data = load_player(args.file)
    display_player(data)
    
    # Verify checksum
    if verify_checksum(data):
        print("✅ Checksum valid")
    else:
        print("❌ Checksum invalid!")
        data_copy = data.copy()
        data_copy.pop('checksum', None)
        print(f"   Expected: {calculate_checksum(data_copy)}")
        print(f"   Got:      {data.get('checksum', 'MISSING')}")

def cmd_set_score(args):
    """Set player score (rank will be calculated on login)"""
    data = load_player(args.file)
    old_score = data['score']
    old_rank = calculate_rank(old_score)
    data['score'] = args.score
    new_rank = calculate_rank(args.score)
    
    print(f"Changing score: {old_score} → {args.score}")
    if old_rank != new_rank:
        print(f"Rank will be: {old_rank} → {new_rank}")
    save_player(args.file, data)

def cmd_set_room(args):
    """Set player room"""
    data = load_player(args.file)
    old_room = data['room_id']
    data['room_id'] = args.room
    
    print(f"Changing room: {old_room} → {args.room}")
    save_player(args.file, data)

def cmd_fix_checksum(args):
    """Clean up file and recalculate checksum"""
    data = load_player(args.file)
    old_checksum = data.get('checksum', 'MISSING')
    
    # List fields that will be removed
    extra_fields = [k for k in data.keys() if k not in ['name', 'score', 'room_id', 'password_hash', 'checksum']]
    if extra_fields:
        print(f"Removing extra fields: {', '.join(extra_fields)}")
    
    print(f"Old checksum: {old_checksum}")
    save_player(args.file, data)

def main():
    parser = argparse.ArgumentParser(
        description='Cave-Plus Player Data Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show player info
  python player_data_tool.py show cave-plus/modern/player_data/MEWCENARY.json
  
  # Set score (rank calculated automatically)
  python player_data_tool.py set-score cave-plus/modern/player_data/MEWCENARY.json 1000
  
  # Set room
  python player_data_tool.py set-room cave-plus/modern/player_data/MEWCENARY.json 16
  
  # Fix checksum and rank
  python player_data_tool.py fix-checksum cave-plus/modern/player_data/MEWCENARY.json

Note: Only name, score, room_id, and password_hash are saved.
      Rank is automatically calculated from score on login.
      Stamina, inventory, kills, deaths are reset on login.
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True
    
    # Show command
    parser_show = subparsers.add_parser('show', help='Show player information')
    parser_show.add_argument('file', help='Player data file (e.g., MEWCENARY.json)')
    parser_show.set_defaults(func=cmd_show)
    
    # Set score command
    parser_score = subparsers.add_parser('set-score', help='Set player score (rank auto-calculated)')
    parser_score.add_argument('file', help='Player data file')
    parser_score.add_argument('score', type=int, help='New score value')
    parser_score.set_defaults(func=cmd_set_score)
    
    # Set room command
    parser_room = subparsers.add_parser('set-room', help='Set player room')
    parser_room.add_argument('file', help='Player data file')
    parser_room.add_argument('room', type=int, help='Room ID (1-157)')
    parser_room.set_defaults(func=cmd_set_room)
    
    # Fix checksum command
    parser_fix = subparsers.add_parser('fix-checksum', help='Recalculate rank and checksum')
    parser_fix.add_argument('file', help='Player data file')
    parser_fix.set_defaults(func=cmd_fix_checksum)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
