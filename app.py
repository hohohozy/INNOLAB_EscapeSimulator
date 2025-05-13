from flask import Flask, render_template, jsonify
import random
from collections import deque

app = Flask(__name__)

MAP_WIDTH = 9
MAP_HEIGHT = 9
FLOORS = 2
EXIT_LOCATIONS = [(0, 8), (8, 8)]  # Ground floor exits
STAIRS = [(4, 4)]  # Shared stair location across floors

# Global simulation state
people = []
fire_zones = []
evacuee_pos = (0, 0)  # Main character position
walls = []  # Walls blocking the path
extinguishers = []  # Locations of fire extinguishers
medical_points = []  # Locations for medical stations

# Initialize the simulation
def init_simulation():
    global people, fire_zones, evacuee_pos, walls, extinguishers, medical_points
    fire_zones = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1))]
    evacuee_pos = (0, 0)
    people = [{'x': random.randint(0, MAP_WIDTH-1), 'y': random.randint(0, MAP_HEIGHT-1), 'type': 'person'} for _ in range(random.randint(5, 15))]
    walls = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(random.randint(3, 7))]
    extinguishers = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(random.randint(1, 3))]
    medical_points = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(random.randint(1, 2))]

# Spread the fire to adjacent cells
def expand_fire():
    global fire_zones
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Up, Down, Left, Right
    new_fire = []
    for (x, y) in fire_zones:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT and (nx, ny) not in fire_zones:
                new_fire.append((nx, ny))
    fire_zones.extend(new_fire)

# Find the escape path for the main character
def find_escape_path(start):
    visited = set()
    queue = deque([(start, [start])])  # (position, path)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) in EXIT_LOCATIONS:
            return path  # Path to exit found

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT) and (nx, ny) not in visited and (nx, ny) not in fire_zones and (nx, ny) not in walls:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    return []

@app.route('/')
def index():
    init_simulation()
    return render_template(
        'index.html',
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        evacuee=evacuee_pos,
        stairs=STAIRS,
        exits=EXIT_LOCATIONS,
        people=people,
        floor_count=FLOORS,
        fire=fire_zones,
        walls=walls,
        extinguishers=extinguishers,
        medical_points=medical_points
    )

@app.route('/next')
def next_step():
    expand_fire()
    path = find_escape_path(evacuee_pos)
    return jsonify({
        'fire': fire_zones,
        'path': path
    })

if __name__ == '__main__':
    app.run(debug=True)
