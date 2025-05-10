from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# 设置一些基本参数
map_width = 9
map_height = 9
fire_zone = []
path_list = []

# 模拟火灾的扩展
def simulate_fire_spread():
    global fire_zone
    new_fire_zone = []
    for x, y in fire_zone:
        # 假设火灾会向四个方向扩展
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < map_width and 0 <= new_y < map_height:
                new_fire_zone.append((new_x, new_y))
    fire_zone = new_fire_zone
    return fire_zone

# 计算最短逃生路径
def find_escape_route():
    # 用简单的广度优先搜索（BFS）来规划路径
    # 假设出口在右下角
    exit_pos = (map_width - 1, map_height - 1)
    path = []
    start_pos = (0, 0)  # 假设主人公从左上角开始

    queue = [(start_pos, [start_pos])]
    visited = set()

    while queue:
        current_pos, current_path = queue.pop(0)
        if current_pos == exit_pos:
            return current_path
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = current_pos[0] + dx, current_pos[1] + dy
            if 0 <= new_x < map_width and 0 <= new_y < map_height:
                if (new_x, new_y) not in visited:
                    visited.add((new_x, new_y))
                    queue.append(((new_x, new_y), current_path + [(new_x, new_y)]))
    return path

@app.route('/')
def index():
    # 初始化火灾位置
    global fire_zone
    fire_zone = [(random.randint(0, map_width-1), random.randint(0, map_height-1))]  # 随机生成一个火灾点
    # 返回首页（可以展示地图）
    return render_template('index.html', fire_zone=fire_zone, map_width=map_width, map_height=map_height)

@app.route('/simulate_fire')
def simulate_fire():
    # 扩展火灾区域
    fire_zone = simulate_fire_spread()
    return jsonify({'fire_zone': fire_zone})

@app.route('/get_escape_route')
def get_escape_route():
    # 获取逃生路径
    escape_route = find_escape_route()
    return jsonify({'escape_route': escape_route})

if __name__ == '__main__':
    app.run(debug=True)
