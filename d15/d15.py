import sys
from enum import Enum, IntEnum, auto
from collections import namedtuple, deque
sys.path.append("..")

from intcode import IntCode
from common import qp, Point, Grid, Dir

class TileType(IntEnum):
    UNEXP = 0
    WALL = 1
    FLOOR = 2
    OXY = 3
    BOUNDARY = 4
TileMap = {
    TileType.UNEXP: " ",
    TileType.WALL: "█",
    TileType.FLOOR: ".",
    TileType.OXY: "o",
    TileType.BOUNDARY: "#",
}

class RetVal(IntEnum):
    WALL = 0
    MOVE = 1
    OXY = 2

class State(Enum):
    TRAVERSE = auto()
    EXPLORE = auto()
    EXPLORED = auto()

DIRTORET = {
    Dir.UP: 1,
    Dir.DOWN: 2,
    Dir.LEFT: 3,
    Dir.RIGHT: 4
}

SearchNode = namedtuple("SearchNode", ("pos", "prev", "dist"))

class Robot(object):
    def __init__(self, grid):
        self.grid = grid
        self.pos = Point((0, 0))

        # The state of the robot
        self.last_dir = None
        self.target = None
        self.state = State.EXPLORE
        self.ip = None
        self.oxy = None

        # Set the explored boundary
        self.boundary = deque()

    def set_ip(self, ip):
        self.ip = ip

    def bfs(self, target, pos=None):
        next_nodes = deque()
        visited = set()

        # Fill in initial step
        if pos is None:
            pos = self.pos
        next_nodes.append(SearchNode(pos, None, 0))

        while next_nodes:
            # Check the next point
            cstep = next_nodes.popleft()
            visited.add(cstep.pos)
            if (nstep := cstep.pos.adjacent(target)):
                # Return the path
                path = deque()
                path.appendleft(nstep)
                while cstep.prev is not None:
                    path.appendleft(Dir(cstep.pos - cstep.prev.pos))
                    cstep = cstep.prev
                return path

            # Otherwise fill in the next steps
            for d in Dir:
                npos = cstep.pos + d.value
                if npos not in visited and self.grid[npos] is TileType.FLOOR:
                    next_nodes.append(SearchNode(npos, cstep, cstep.dist+1))
        return None

    def input(self):
        if self.state is State.EXPLORE:
            # Expand the boundary around the current position
            for d in Dir: # Expand the boundaries of the map
                if self.grid[self.pos + d.value] is TileType.UNEXP:
                    self.boundary.append(self.pos + d.value)
                    self.grid[self.pos + d.value] = TileType.BOUNDARY

            # Get the next boundary value to explore
            try:
                self.target = self.boundary.pop()
                self.target_path = self.bfs(self.target)
            except IndexError:
                self.state = State.EXPLORED
                self.ip.term()
                return -1

            self.state = State.TRAVERSE
        # Moving to the next point to explore
        if self.state is State.TRAVERSE:
            self.last_dir = self.target_path.popleft()
            if not self.target_path:
                self.state = State.EXPLORE
            return DIRTORET[self.last_dir]
        raise RuntimeError("Shouldn't have gotten here")

    def output(self, val):
        val = RetVal(val)
        if val is RetVal.WALL: # Robot hit a wall
            self.grid[self.pos + self.last_dir.value] = TileType.WALL
        else:
            self.pos += self.last_dir.value
            if val is RetVal.OXY:
                self.grid[self.pos] = TileType.OXY
                self.oxy = self.pos
                print(f"Oxy found at pos {self.pos}")
                self.grid.print_grid(flipy=True)
            else:
                self.grid[self.pos] = TileType.FLOOR

with open("input", "r") as inp:
    init = tuple(qp(inp.read()))

grid = Grid(default=TileType.UNEXP, tilemap=TileMap)
grid[Point((0, 0))] = TileType.FLOOR
robot = Robot(grid)
ip = IntCode(init, input_callback=robot.input, output_callback=robot.output)
robot.set_ip(ip)
ip.run()

grid.print_grid(flipy=True)
print(f"Path to oxy: {len(robot.bfs(robot.oxy, Point((0, 0))))}")

# Then, figure out how long oxygen takes to fill
iters = 0
grid.tiles[robot.oxy] = TileType.BOUNDARY
while any(tile is TileType.FLOOR for tile in grid.tiles.values()):
    oxy_tiles = tuple(filter(lambda tile: tile[1] is TileType.BOUNDARY, grid.tiles.items()))
    for oxy_tile, _ in oxy_tiles:
        for d in Dir:
            if grid[oxy_tile + d.value] is TileType.FLOOR:
                grid[oxy_tile + d.value] = TileType.BOUNDARY
        grid[oxy_tile] = TileType.OXY
    iters += 1
print(f"Mins to fill: {iters}")
