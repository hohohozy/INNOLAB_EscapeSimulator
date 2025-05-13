from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

MAP_WIDTH = 9
MAP_HEIGHT = 9
FLOORS = 2

# Global states
fire_zones = []
evacuee_pos = (0, 0, 1)  # (x, y, floor)
stairs = [(4, 4)]  # Shared location on both floors
exits = [(0, 8, 0), (8, 8, 0)]  # Ground floor exits
people = []  # Random people positions

def init_simulation():
    global fire_zones, evacuee_pos, people
    fire_zones = [(random.randint(0, 8), random.randint(0, 8), random.randint(0, 1))]
    evacuee_pos = (random.randint(0, 8), random.randint(0, 8), 1)
    people = []
    for _ in range(random.randint(8, 15)):
        people.append((random.randint(0, 8), random.randint(0, 8), random.randint(0, 1)))

def expand_fire():
    global fire_zones
    new_fire = fire_zones[:]
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for x, y, f in fire_zones:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                new_cell = (nx, ny, f)
                if new_cell not in new_fire:
                    new_fire.append(new_cell)
    fire_zones = new_fire

def find_escape_path(start):
    from collections import deque
    visited = set()
    queue = deque()
    queue.append((start, [start]))
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        (x, y, f), path = queue.popleft()
        if (x, y, f) in exits:
            return path
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            next_pos = (nx, ny, f)
            if (0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT
                and next_pos not in visited
                and next_pos not in fire_zones):
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))
        if (x, y) in stairs:
            new_floor = 1 - f
            stair_pos = (x, y, new_floor)
            if stair_pos not in visited and stair_pos not in fire_zones:
                visited.add(stair_pos)
                queue.append((stair_pos, path + [stair_pos]))
    return []

@app.route('/')
def index():
    init_simulation()
    return render_template(
        'index.html',
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        evacuee=evacuee_pos,
        stairs=stairs,
        exits=exits,
        people=people,
        floor_count=FLOORS,
        fire=fire_zones
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
