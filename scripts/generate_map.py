#!/usr/bin/env python3
"""
Generate ASCII map of Cave-Plus game
Reads room data and creates a visual representation of the cave layout
"""

import yaml
from collections import defaultdict, deque

def load_rooms(filename):
    """Load room data from YAML file"""
    with open(filename, 'r') as f:
        data = yaml.safe_load(f)
    return data['rooms']

def build_graph(rooms):
    """Build adjacency graph from room connections"""
    graph = defaultdict(dict)
    for room_id, room_data in rooms.items():
        exits = room_data.get('exits', {})
        for direction, target in exits.items():
            graph[room_id][direction] = target
    return graph

def assign_positions(rooms, graph, start_room=1):
    """
    Assign 2D coordinates to rooms using BFS
    Try to respect directional relationships
    """
    positions = {}
    visited = set()
    queue = deque([(start_room, 0, 0, None)])  # (room_id, x, y, from_direction)
    
    # Direction offsets
    dir_offsets = {
        'north': (0, -2),
        'south': (0, 2),
        'east': (3, 0),
        'west': (-3, 0),
        'up': (0, -2),    # Treat up as north
        'down': (0, 2),   # Treat down as south
    }
    
    while queue:
        room_id, x, y, from_dir = queue.popleft()
        
        if room_id in visited:
            continue
            
        visited.add(room_id)
        
        # Check for collision and resolve
        collision_count = 0
        original_x, original_y = x, y
        while (x, y) in positions.values() and collision_count < 20:
            # Try to offset in a direction perpendicular to arrival
            if from_dir in ['north', 'south', 'up', 'down']:
                x = original_x + (collision_count % 2) * 3 * (1 if collision_count % 4 < 2 else -1)
            else:
                y = original_y + (collision_count % 2) * 2 * (1 if collision_count % 4 < 2 else -1)
            collision_count += 1
        
        positions[room_id] = (x, y)
        
        # Process exits in priority order (prefer cardinal directions)
        exit_priority = ['north', 'south', 'east', 'west', 'up', 'down']
        for direction in exit_priority:
            if direction in graph[room_id]:
                target = graph[room_id][direction]
                if target not in visited and target in rooms:
                    dx, dy = dir_offsets.get(direction, (0, 0))
                    new_x, new_y = x + dx, y + dy
                    queue.append((target, new_x, new_y, direction))
    
    return positions

def create_ascii_map(rooms, positions, scale=1):
    """Create ASCII map from room positions"""
    if not positions:
        return "No rooms to map"
    
    # Find bounds
    min_x = min(x for x, y in positions.values())
    max_x = max(x for x, y in positions.values())
    min_y = min(y for x, y in positions.values())
    max_y = max(y for x, y in positions.values())
    
    # Create grid with extra space
    width = (max_x - min_x + 6)
    height = (max_y - min_y + 4)
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Draw connections first (so they appear behind room numbers)
    for room_id, (x, y) in positions.items():
        nx = x - min_x
        ny = y - min_y
        
        exits = rooms[room_id].get('exits', {})
        
        # North/Up
        for direction in ['north', 'up']:
            if direction in exits:
                target = exits[direction]
                if target in positions:
                    tx, ty = positions[target]
                    tnx = tx - min_x
                    tny = ty - min_y
                    # Draw vertical line
                    if ny > tny:
                        for i in range(tny + 1, ny):
                            if 0 <= i < height:
                                grid[i][nx] = '|'
        
        # South/Down
        for direction in ['south', 'down']:
            if direction in exits:
                target = exits[direction]
                if target in positions:
                    tx, ty = positions[target]
                    tnx = tx - min_x
                    tny = ty - min_y
                    # Draw vertical line
                    if ny < tny:
                        for i in range(ny + 1, tny):
                            if 0 <= i < height:
                                grid[i][nx] = '|'
        
        # East
        if 'east' in exits:
            target = exits['east']
            if target in positions:
                tx, ty = positions[target]
                tnx = tx - min_x
                tny = ty - min_y
                # Draw horizontal line
                if nx < tnx:
                    for i in range(nx + 1, tnx):
                        if 0 <= i < width:
                            grid[ny][i] = '-'
        
        # West
        if 'west' in exits:
            target = exits['west']
            if target in positions:
                tx, ty = positions[target]
                tnx = tx - min_x
                tny = ty - min_y
                # Draw horizontal line
                if nx > tnx:
                    for i in range(tnx + 1, nx):
                        if 0 <= i < width:
                            grid[ny][i] = '-'
    
    # Draw room numbers on top
    for room_id, (x, y) in positions.items():
        nx = x - min_x
        ny = y - min_y
        
        # Draw room number (up to 3 digits)
        room_str = str(room_id)
        for i, char in enumerate(room_str):
            if nx + i < width and 0 <= ny < height:
                grid[ny][nx + i] = char
    
    # Convert grid to string
    return '\n'.join(''.join(row).rstrip() for row in grid)


def generate_legend(rooms):
    """Generate legend for special rooms"""
    special_rooms = []
    boss_creatures = []
    items = []
    
    for room_id, room_data in sorted(rooms.items()):
        note = room_data.get('note', '')
        name = room_data.get('name', '')
        objects = room_data.get('initial_objects', [])
        
        # Special rooms
        if note or name:
            desc = f"  {room_id:3d}: "
            if name:
                desc += name
            if note:
                if name:
                    desc += f" - {note}"
                else:
                    desc += note
            special_rooms.append(desc)
        
        # Boss creatures and important items
        for obj in objects:
            obj_str = str(obj)
            if any(boss in obj_str for boss in ['Dragon', 'Guardian', 'Demon', 'Troll']):
                boss_creatures.append(f"  {room_id:3d}: {obj}")
            elif any(item in obj_str for item in ['Staff', 'Shield', 'Crystal', 'Amulet', 'Ruby']):
                items.append(f"  {room_id:3d}: {obj}")
    
    return special_rooms, boss_creatures, items

def main():
    print("Generating ASCII map of Cave-Plus...")
    
    # Load room data
    rooms = load_rooms('cave-plus/modern/rooms-parsed.yml')
    print(f"Loaded {len(rooms)} rooms")
    
    # Build graph
    graph = build_graph(rooms)
    
    # Assign positions
    positions = assign_positions(rooms, graph, start_room=1)
    print(f"Positioned {len(positions)} rooms")
    
    # Create map
    ascii_map = create_ascii_map(rooms, positions, scale=1)
    
    # Generate legend
    special_rooms, boss_creatures, items = generate_legend(rooms)
    
    # Output
    output = []
    output.append("=" * 100)
    output.append("CAVE-PLUS ASCII MAP - 157 Interconnected Rooms")
    output.append("=" * 100)
    output.append("")
    output.append("LEGEND:")
    output.append("  Numbers = Room IDs")
    output.append("  |  = North/South connections (or Up/Down)")
    output.append("  -- = East/West connections")
    output.append("")
    output.append(ascii_map)
    output.append("")
    output.append("=" * 100)
    output.append("SPECIAL LOCATIONS")
    output.append("=" * 100)
    for item in special_rooms:
        output.append(item)
    
    output.append("")
    output.append("=" * 100)
    output.append("BOSS CREATURES")
    output.append("=" * 100)
    for item in boss_creatures:
        output.append(item)
    
    output.append("")
    output.append("=" * 100)
    output.append("MAGICAL ITEMS")
    output.append("=" * 100)
    for item in items:
        output.append(item)
    
    output.append("")
    output.append("=" * 100)
    output.append("GAME AREAS")
    output.append("=" * 100)
    output.append("  Main Cave System: Rooms 1-71 (entrance, tunnels, chambers)")
    output.append("  Hall of Knowledge: Room 72+ (tutorial area)")
    output.append("  Wizard's Domain: Rooms 16-20 (restricted area)")
    output.append("  Torture Caves: Rooms 30+ (beyond portcullis)")
    output.append("  Upper Levels: Rooms 100+ (complex maze)")
    output.append("")
    output.append("KEY ROOMS:")
    output.append("  Room 1:  Main Entrance / Altar (charge Staff of Merlin here)")
    output.append("  Room 12: Green Room (light switch)")
    output.append("  Room 19: Mortuary (dead creatures respawn here)")
    output.append("  Room 20: Armoury (defensive items)")
    output.append("  Room 26: Snake Pit (multiple snakes)")
    output.append("  Room 56: Bank (deposit treasure for points)")
    output.append("")
    
    map_text = '\n'.join(output)
    
    # Save to file
    with open('cave-plus/modern/MAP.txt', 'w') as f:
        f.write(map_text)
    
    print("\nMap saved to: cave-plus/modern/MAP.txt")
    print(f"\nPreview (first 60 lines):")
    print('\n'.join(output[:60]))

if __name__ == '__main__':
    main()
