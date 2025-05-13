from flask import Flask, render_template, jsonify
import random
from collections import deque
import time

app = Flask(__name__)

MAP_WIDTH = 9
MAP_HEIGHT = 9
FLOORS = 2
EXIT_LOCATIONS = [(0, 8), (8, 8)]  # Ground floor exits
STAIRS = [(4, 4)]  # Shared stair location across floors

# Global simulation state
floors = {}
fire_expansion_interval = 0.5  # Seconds between fire expansions

# Initialize the simulation with multiple floors
def init_simulation():
    global floors
    floors = {}
    for floor in range(FLOORS):
        fire_zones = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1))]
        evacuee_pos = (0, 0)
        people = [{'x': random.randint(0, MAP_WIDTH-1), 'y': random.randint(0, MAP_HEIGHT-1), 'type': 'person'} for _ in range(random.randint(5, 15))]
        walls = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(random.randint(3, 7))]
        extinguishers = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(random.randint(1, 3))]
        medical_points = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(random.randint(1, 2))]

        # Store floor data
        floors[floor] = {
            'fire': fire_zones,
            'evacuee': evacuee_pos,
            'people': people,
            'walls': walls,
            'extinguishers': extinguishers,
            'medical_points': medical_points,
        }

# Spread the fire to adjacent cells (automatic expansion)
def expand_fire(floor):
    global floors
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Up, Down, Left, Right
    new_fire = []
    for (x, y) in floors[floor]['fire']:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT and (nx, ny) not in floors[floor]['fire']:
                new_fire.append((nx, ny))
    floors[floor]['fire'].extend(new_fire)

# Find the escape path for the main character
def find_escape_path(start, floor):
    visited = set()
    queue = deque([(start, [start])])  # (position, path)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) in EXIT_LOCATIONS:
            return path  # Path to exit found

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT) and (nx, ny) not in visited and (nx, ny) not in floors[floor]['fire'] and (nx, ny) not in floors[floor]['walls']:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    return []

# Start the fire expansion and path generation simulation
@app.route('/start_simulation')
def start_simulation():
    init_simulation()

    # Expand fire automatically for a few cycles (simulate over time)
    for _ in range(5):  # Adjust the number of expansions based on the desired speed
        time.sleep(fire_expansion_interval)  # Simulate time delay for fire expansion
        expand_fire(0)  # Currently expanding on floor 0, modify for multi-floor logic if needed

    # Calculate the escape path
    path = find_escape_path(floors[0]['evacuee'], 0)
    
    return jsonify({
        'fire': floors[0]['fire'],
        'path': path
    })

@app.route('/')
def index():
    return render_template(
        'index.html',
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        floors=FLOORS,
        exits=EXIT_LOCATIONS,
        stairs=STAIRS,
    )

if __name__ == '__main__':
    app.run(debug=True)
