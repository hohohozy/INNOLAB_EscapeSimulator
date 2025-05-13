from flask import Flask, render_template, jsonify
import random
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

app = Flask(__name__)

MAP_WIDTH = 9
MAP_HEIGHT = 9
FLOORS = 2

@dataclass
class Cell:
    x: int
    y: int
    floor: int
    is_wall: bool = False
    is_fire: bool = False
    is_exit: bool = False
    is_stairs: bool = False
    is_medical: bool = False
    is_extinguisher: bool = False

@dataclass
class Person:
    pos: Tuple[int, int, int]
    path: List[Tuple[int, int, int]] = field(default_factory=list)
    status: str = "alive"  # alive, escaped, trapped
    speed: float = 1.0  # 1: normal, 2: fast, 0.5: slow
    name: Optional[str] = None

@dataclass
class SimulationState:
    turn: int = 0
    evacuee: Person = None
    people: List[Person] = field(default_factory=list)
    fire: List[Tuple[int, int, int]] = field(default_factory=list)
    walls: List[Tuple[int, int]] = field(default_factory=list)
    medical_points: List[Tuple[int, int, int]] = field(default_factory=list)
    extinguishers: List[Tuple[int, int, int]] = field(default_factory=list)
    history: List[dict] = field(default_factory=list)  # 每一轮记录一次状态快照

# Global state
state = SimulationState()

def init_simulation():
    global state
    state = SimulationState()
    state.fire = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1), random.randint(0, FLOORS-1))]
    state.evacuee = Person(pos=(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1), 1))
    state.people = [Person(pos=(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1), random.randint(0, FLOORS-1))) for _ in range(random.randint(8, 15))]
    state.walls = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(random.randint(5, 10))]
    state.medical_points = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1), random.randint(0, FLOORS-1)) for _ in range(random.randint(1, 3))]
    state.extinguishers = [(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1), random.randint(0, FLOORS-1)) for _ in range(random.randint(1, 3))]

def expand_fire():
    global state
    new_fire = state.fire[:]
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for x, y, f in state.fire:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                new_cell = (nx, ny, f)
                if new_cell not in new_fire:
                    new_fire.append(new_cell)
    state.fire = new_fire

def find_escape_path(start):
    from collections import deque
    visited = set()
    queue = deque()
    queue.append((start, [start]))
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        (x, y, f), path = queue.popleft()
        if (x, y, f) in state.fire:
            continue
        if (x, y, f) in state.walls:
            continue
        if (x, y, f) in state.extinguishers:
            continue
        if (x, y, f) in state.medical_points:
            continue
        if (x, y, f) == (0, 8, 0):
            return path
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                next_pos = (nx, ny, f)
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))
    return []

@app.route('/')
def index():
    init_simulation()
    return render_template(
        'index.html',
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        evacuee=state.evacuee,
        stairs=[(4, 4)],
        exits=[(0, 8, 0), (8, 8, 0)],
        people=state.people,
        floor_count=FLOORS,
        fire=state.fire,
        walls=state.walls,
        medical_points=state.medical_points,
        extinguishers=state.extinguishers
    )

@app.route('/next')
def next_step():
    expand_fire()
    path = find_escape_path(state.evacuee.pos)
    state.turn += 1
    state.history.append({
        'turn': state.turn,
        'fire': state.fire,
        'people': [(p.pos, p.status) for p in state.people]
    })
    return jsonify({
        'fire': state.fire,
        'path': path,
        'people': [{'pos': p.pos, 'status': p.status} for p in state.people],
        'turn': state.turn
    })

@app.route('/replay/<int:step>')
def replay(step):
    if 0 <= step < len(state.history):
        return jsonify(state.history[step])
    return jsonify({'error': 'Invalid step'}), 404

if __name__ == '__main__':
    app.run(debug=True)
