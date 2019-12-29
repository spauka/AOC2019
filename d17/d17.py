import sys
from enum import Enum, IntEnum, auto
from collections import namedtuple, deque, defaultdict
from itertools import product, islice
sys.path.append("..")

from intcode import IntCode
from common import qp, Point, Grid, Dir

class TileType(IntEnum):
    UNKNOWN  = 0
    BOUNDARY = 1
    INTERSECT = 2
    SCAFFOLD = ord('#')
    SPACE    = ord('.')
    ROBOT_L  = ord('<')
    ROBOT_D  = ord('v')
    ROBOT_R  = ord('>')
    ROBOT_U  = ord('^')

TileMap = {
    TileType.UNKNOWN:  " ",
    TileType.INTERSECT: 'O',
    TileType.SCAFFOLD: "█",
    TileType.SPACE:    '.',
    TileType.ROBOT_L:  '<',
    TileType.ROBOT_D:  'v',
    TileType.ROBOT_R:  '>',
    TileType.ROBOT_U:  '^',
}

RobotDir = {
    TileType.ROBOT_L: Dir.LEFT,
    TileType.ROBOT_D: Dir.DOWN,
    TileType.ROBOT_R: Dir.RIGHT,
    TileType.ROBOT_U: Dir.UP,
}
DirRobot = {v: k for k, v in RobotDir.items()}

class State(Enum):
    MAPPING = auto()
    MAPPED = auto()
    PROGRAM = auto()
    PROGRAMMING = auto()
    PROGRAMMED = auto()

SearchNode = namedtuple("SearchNode", ("pos", "dir", "prev", "visited"))
def get_path(cnode):
    path = []
    while cnode:
        path.append(Dir.LETTER_MAP[cnode.dir])
        cnode = cnode.prev
    path.reverse()
    return "".join(path)
def visited_nodes(cnode):
    visited = set()
    while cnode:
        visited.add(cnode.pos)
        cnode = cnode.prev
    return visited
def rle_path(path):
    enc_path = []
    cstep = path[0]
    for nstep in path[1:]:
        if nstep != cstep:
            if Dir(nstep) == Dir(cstep).turn_left():
                enc_path.append("R") # Flipped due to coordinate choice
            elif Dir(nstep) == Dir(cstep).turn_right():
                enc_path.append("L") # Flipped due to coordinate choice
            else:
                RuntimeError(f"How to turn from {cstep} to {nstep}")
            enc_path.append(-1)
        enc_path[-1] += 1
        cstep = nstep
    return enc_path

class Robot(object):
    def __init__(self, grid):
        self.grid = grid
        self.pos = Point((0, 0))
        self.ip = None

        # The state of the robot
        self.dir = None
        self.target = None
        self.state = State.MAPPING
        self.map_pos = Point((0, 0))

        # Intersections
        self.intersections = None

        # Directions for the robot
        self.main = ''
        self.A = ''
        self.B = ''
        self.C = ''
        self.debug = ''

    def set_ip(self, ip):
        self.ip = ip

    def _nav_to_intersection(self, cnode):
        cpos = cnode.pos
        cdir = cnode.dir
        npos = cnode.pos + cnode.dir
        while True:
            # Keep moving forward until we hit a corner
            while self.grid[npos] is TileType.SCAFFOLD:
                cpos = npos
                npos = npos + cdir
                cnode = cnode._replace(pos=cpos, prev=cnode)

            # If we've hit an instersection, we are done
            if self.grid[npos] is TileType.INTERSECT:
                cnode = cnode._replace(pos=npos, prev=cnode)
                return cnode, False

            # Otherwise, we need to turn. Figure out which way
            if self.grid[cpos + cdir.turn_left()] is TileType.SCAFFOLD:
                turn = Dir.turn_left
            elif self.grid[cpos + cdir.turn_right()] is TileType.SCAFFOLD:
                turn = Dir.turn_right
            else:
                # Dead end, return
                return cnode, True

            cdir = turn(cdir)
            npos = cpos + cdir
            cnode = cnode._replace(dir=cdir, prev=cnode)

    def visit_all(self):
        next_nodes = deque()
        visited = set()
        valid_path = set()
        all_scaffold = set(p for p, v in self.grid.tiles.items() if v in (TileType.SCAFFOLD, TileType.INTERSECT))

        # Fill in initial step
        next_nodes.append(SearchNode(self.pos, self.dir, None, ()))
        while next_nodes:
            # Check the next point (using a dfs, since bfs paths seem to be longer and harder to find...)
            cstep = next_nodes.pop()

            # Navigate to the next intersection or dead-end
            cstep, deadend = self._nav_to_intersection(cstep)

            if visited_nodes(cstep) == all_scaffold:
                valid_path.add(cstep)
                print(f"Valid Path: {get_path(cstep)}")
                # Doesn't seem to find better paths. Let's just work with the first one...
                return get_path(cstep)

            if not deadend:
                # Disallow overly loopy loops
                if (cstep.pos, cstep.dir.turn_left().turn_left()) not in visited:
                    nvisited = ((cstep.pos, cstep.dir.turn_left().turn_left()),)
                    cstep = cstep._replace(visited=cstep.visited+nvisited)

                # Add next steps
                if (cstep.pos, cstep.dir.turn_left()) not in visited:
                    nvisit = (cstep.pos, cstep.dir.turn_left())
                    next_nodes.append(cstep._replace(dir=cstep.dir.turn_left(), prev=cstep, visited=cstep.visited+(nvisit,)))
                if (cstep.pos, cstep.dir.turn_right()) not in visited:
                    nvisit = (cstep.pos, cstep.dir.turn_right())
                    next_nodes.append(cstep._replace(dir=cstep.dir.turn_right(), prev=cstep, visited=cstep.visited+(nvisit,)))
                if (cstep.pos, cstep.dir) not in visited:
                    nvisit = (cstep.pos, cstep.dir)
                    next_nodes.append(cstep._replace(visited=cstep.visited+(nvisit,)))
        return None

    def input(self):
        # Prepare the input
        if self.state == State.PROGRAM:
            self.program = "\n".join((self.final, self.A, self.B, self.C, self.debug)) + "\n"
            self.atchar = 0
            self.state = State.PROGRAMMING
        self.atchar += 1
        if len(self.program)-1 == self.atchar:
            self.state = State.PROGRAMMED
        return ord(self.program[self.atchar-1])

    def output(self, val):
        if self.state == State.MAPPING:
            if val == ord('\n'):
                self.map_pos = Point((0, self.map_pos[1] - 1))
            else:
                self.grid[self.map_pos] = TileType(val)
                if self.grid[self.map_pos] in RobotDir:
                    self.pos = self.map_pos
                    self.dir = RobotDir[self.grid[self.map_pos]]
                    self.grid[self.map_pos] = TileType.SCAFFOLD
                    print(f"Robot found at position {self.pos} facing {self.dir}")
                self.map_pos = self.map_pos + Dir.LEFT
        elif self.state in (State.PROGRAM, State.PROGRAMMING):
            pass # Ignore values in this step
        elif self.state is State.PROGRAMMED:
            if val < 128:
                pass # Ignore values in this step
            else:
                print(f"Robot returned {val}")
        else:
            raise RuntimeError(f"Shouldn't have gotten here yet. In state {self.state}")

    def find_intersections(self):
        if self.state != State.MAPPING:
            raise RuntimeError("Incorrect state to find intersections")
        self.intersections = []
        for x, y in product(range(self.grid.tl[0]+1, -1), range(self.grid.br[1]+1, -1)):
            cpos = Point((x, y))
            if self.grid[cpos] is TileType.SCAFFOLD and all(self.grid[cpos+d] is TileType.SCAFFOLD for d in Dir):
                self.grid[cpos] = TileType.INTERSECT
                self.intersections.append(cpos)
        self.intersections = tuple(self.intersections)
        self.state = State.MAPPED

with open("input", "r") as inp:
    init = tuple(qp(inp.read()))

grid = Grid(default=TileType.UNKNOWN, tilemap=TileMap)
robot = Robot(grid)
ip = IntCode(init, input_callback=robot.input, output_callback=robot.output)
robot.set_ip(ip)
ip.run()
robot.find_intersections()
grid.print_grid(flipy=True, highlight=robot.pos, highlight_val=DirRobot[robot.dir])
print(robot.intersections)
print(f"Alignment Param: {sum(x[0]*x[1] for x in robot.intersections)}")
# Run search
path = robot.visit_all()
path = rle_path(path)
path = tuple(f"{x},{y}" for x, y in zip(islice(path, 0, None, 2), islice(path, 1, None, 2)))
print(len(path), ", ".join(path))

repeats = defaultdict(int)
for start in range(len(path)):
    for mlen in range(min(len(path)-start, 5)):
        prog = ",".join(path[start:start+mlen+1])
        if len(prog) > 20:
            continue
        repeats[prog] += 1

for val, reps in sorted(repeats.items(), key=lambda x: (x[1], len(x[0]))):
    print(f"{reps}: {val}")

# TODO: Figure out how to do this step automatically
robot.A = 'L,10,L,6,R,10'
robot.B = 'R,6,R,8,R,8,L,6,R,8'
robot.C = 'L,10,R,8,R,8,L,10'
robot.final = ",".join(path).replace(robot.A, 'A').replace(robot.B, 'B').replace(robot.C, 'C')
robot.debug = 'n'

# Rerun the robot
ip.reset()
ip.mem[0] = 2
robot.state = State.PROGRAM
ip.run()
