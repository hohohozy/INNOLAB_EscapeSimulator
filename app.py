from flask import Flask, render_template, jsonify
import random
import heapq

app = Flask(__name__)

MAP_WIDTH = 9
MAP_HEIGHT = 9
FLOORS = 2

# 全局状态
fire_zones = []
evacuee_pos = (0, 0, 1)
stairs = [(4, 4)]
exits = [(0, 8, 0), (8, 8, 0)]
people = []

def init_simulation():
    """初始化火灾与人员位置"""
    global fire_zones, evacuee_pos, people
    fire_zones = [(random.randint(0, 8), random.randint(0, 8), random.randint(0, 1))]
    evacuee_pos = (random.randint(0, 8), random.randint(0, 8), 1)
    people = [(random.randint(0, 8), random.randint(0, 8), random.randint(0, 1)) for _ in range(random.randint(8, 15))]

def expand_fire():
    """使用细胞自动机模拟火灾蔓延"""
    global fire_zones
    new_fire = set(fire_zones)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    for x, y, f in fire_zones:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT and random.random() < 0.4:  # 40%几率蔓延
                new_fire.add((nx, ny, f))
    
    fire_zones = list(new_fire)

def heuristic(a, b):
    """A*算法启发式函数，计算曼哈顿距离"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_escape_path(start):
    """使用 A* 算法寻找逃生路径"""
    from collections import deque
    queue = []
    heapq.heappush(queue, (0, [start]))  # (优先级, 路径)
    visited = set()

    while queue:
        _, path = heapq.heappop(queue)
        x, y, f = path[-1]
        
        if (x, y, f) in exits:
            return path
        
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            next_pos = (nx, ny, f)
            if (0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT and next_pos not in visited and next_pos not in fire_zones):
                visited.add(next_pos)
                heapq.heappush(queue, (heuristic(next_pos, exits[0]), path + [next_pos]))
        
        # 处理楼梯
        if (x, y) in stairs:
            new_floor = 1 - f
            stair_pos = (x, y, new_floor)
            if stair_pos not in visited and stair_pos not in fire_zones:
                visited.add(stair_pos)
                heapq.heappush(queue, (heuristic(stair_pos, exits[0]), path + [stair_pos]))
    
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
