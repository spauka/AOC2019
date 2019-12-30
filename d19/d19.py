import sys
from enum import Enum, IntEnum, auto
from collections import deque
sys.path.append("..")

from intcode import IntCode
from common import qp, Point, Grid, Dir

class TileType(IntEnum):
    BEAM  = 1
    SPACE = 0
    UNKNOWN = 2

TileMap = {
    TileType.BEAM:  "█",
    TileType.SPACE: '.',
    TileType.UNKNOWN: " ",
}

class State(Enum):
    PASS_X = auto()
    PASS_Y = auto()
    READ = auto()

class Robot(object):
    def __init__(self, grid):
        self.state = State.PASS_X
        self.grid = grid
        self.ip = None
        self.x_pos = None
        self.y_pos = None

    def set_ip(self, ip):
        self.ip = ip

    def input(self):
        if self.state is State.PASS_X:
            self.state = State.PASS_Y
            return int(self.x_pos)
        if self.state is State.PASS_Y:
            self.state = State.READ
            return int(self.y_pos)
        raise RuntimeError(f"Invalid input instr in state {self.state}")

    def output(self, val):
        if self.state is State.READ:
            tt = TileType(val)
            self.grid[Point((self.x_pos, self.y_pos))] = tt
            self.state = State.PASS_X
        else:
            raise RuntimeError(f"Invalid output instr in state {self.state}")

with open("input", "r") as inp:
    init = tuple(qp(inp.read()))

grid = Grid(default=TileType.UNKNOWN, tilemap=TileMap)
grid[Point((0, 0))] = TileType.BEAM
robot = Robot(grid)
ip = IntCode(init, input_callback=robot.input, output_callback=robot.output)
robot.set_ip(ip)

def query_point(robot, p):
    robot.ip.reset()
    robot.x_pos, robot.y_pos = p
    robot.ip.run()
    return robot.grid[p]

def find_tl(robot):
    sq = 1
    while True:
        for p in range(sq):
            xp = query_point(robot, Point((p, sq)))
            yp = query_point(robot, Point((sq, p)))
            if xp is TileType.BEAM:
                return Point((p, sq))
            if yp is TileType.BEAM:
                return Point((sq, p))
        sq += 1

def fill(grid, start, maxp):
    next_nodes = deque()
    next_nodes.append(start)
    added = set(next_nodes)

    while next_nodes:
        cpos = next_nodes.popleft()
        grid[cpos] = TileType.BEAM
        for d in (Dir.UP, Dir.RIGHT, Dir.UP+Dir.RIGHT):
            npos = cpos + d
            if npos in added:
                continue
            if any(p <= 0 for p in npos.cmp(maxp)):
                continue
            if grid[npos] is TileType.SPACE:
                continue
            next_nodes.append(npos)
            added.add(npos)
    return cpos

def follow_line(robot, start, max_p, dirs):
    npos = start
    pos = start
    while all(p == 1 for p in npos.cmp(max_p)):
        pos = npos
        if query_point(robot, pos) is TileType.BEAM:
            npos = pos + dirs[0]
        else:
            npos = pos + dirs[1]
    return pos

def follow_down(robot, start, max_p):
    return follow_line(robot, start, max_p, dirs = (Dir.UP, Dir.RIGHT))
def follow_right(robot, start, max_p):
    return follow_line(robot, start, max_p, dirs = (Dir.RIGHT, Dir.UP))

def calc_extent(grid, start, m_dir=Dir.DOWN, reqd_ext=50):
    cpos = start + m_dir
    extent = 1
    while grid[cpos] is TileType.UNKNOWN and extent < (reqd_ext-1):
        extent += 1
        cpos = cpos + m_dir
    extent += 1
    return extent, cpos

# Part 1
max_p = Point((50, 50))
start = find_tl(robot)
print(f"Found start @ {start}")
d_max = follow_down(robot, start, max_p)
r_max = follow_right(robot, start, max_p)
n_fill = fill(grid, start, max_p)
print(f"Affected: {len(tuple(None for p, x in grid.tiles.items() if x is TileType.BEAM and p[0] < 50 and p[1] < 50))}")

# Part 2
max_p = max_p + Point((float('inf'), 1))
tl = p2_final = None
while ((((tl := calc_extent(grid, d_max, m_dir=Dir.DOWN, reqd_ext=100))[0]) < 100) or
    (calc_extent(grid, tl[1], m_dir=Dir.RIGHT, reqd_ext=100)[0] < 100)):
    d_max = follow_down(robot, d_max, max_p)
    r_max = follow_right(robot, r_max, max_p)
    max_p = max_p + Point((float('inf'), 1))
    p2_final = tl

print(p2_final)