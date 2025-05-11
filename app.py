from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# 设置地图尺寸
map_width = 9
map_height = 9
fire_zone = []

# 模拟火灾扩展
def simulate_fire_spread():
    global fire_zone
    new_fire_zone = fire_zone.copy()
    for x, y in fire_zone:
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < map_width and 0 <= new_y < map_height:
                if (new_x, new_y) not in new_fire_zone:
                    new_fire_zone.append((new_x, new_y))
    fire_zone = new_fire_zone
    return fire_zone

# 逃生路径（广度优先搜索）
def find_escape_route():
    exit_pos = (map_width - 1, map_height - 1)
    start_pos = (0, 0)
    queue = [(start_pos, [start_pos])]
    visited = set()

    while queue:
        current_pos, path = queue.pop(0)
        if current_pos == exit_pos:
            return path
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            new_x, new_y = current_pos[0]+dx, current_pos[1]+dy
            next_pos = (new_x, new_y)
            if (0 <= new_x < map_width and 0 <= new_y < map_height and
                next_pos not in visited and next_pos not in fire_zone):
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))
    return []

@app.route('/')
def index():
    global fire_zone
    fire_zone = [(random.randint(0, map_width-1), random.randint(0, map_height-1))]
    return render_template('index.html', fire_zone=fire_zone, map_width=map_width, map_height=map_height)

@app.route('/simulate_fire')
def simulate_fire():
    global fire_zone
    fire_zone = simulate_fire_spread()
    return jsonify({'fire_zone': fire_zone})

@app.route('/get_escape_route')
def get_escape_route():
    escape_route = find_escape_route()
    return jsonify({'escape_route': escape_route})

if __name__ == '__main__':
    app.run(debug=True)
