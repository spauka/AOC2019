import sys
from enum import Enum, IntEnum
sys.path.append("..")

from intcode import IntCode
from common import qp, Point, Grid

class Color(IntEnum):
    BLK = 0
    WHI = 1

class RobotState(Enum):
    PAINT = 0
    TURN = 1

class Dir(Enum):
    UP = Point((0, 1))
    RIGHT = Point((1, 0))
    DOWN = Point((0, -1))
    LEFT = Point((-1, 0))
    DIRS = ["UP", "RIGHT", "DOWN", "LEFT"]

    @classmethod
    def turn_left(cls, val):
        return getattr(cls, cls.DIRS.value[(cls.DIRS.value.index(val.name)-1)%4])
    @classmethod
    def turn_right(cls, val):
        return getattr(cls, cls.DIRS.value[(cls.DIRS.value.index(val.name)+1)%4])

class Robot(object):
    def __init__(self, grid):
        self.grid = grid
        self.pos = Point((0, 0))
        self.dir = Dir.UP
        self.state = RobotState.PAINT

    def input(self):
        return self.grid[self.pos]

    def output(self, val):
        if self.state == RobotState.PAINT:
            self.grid[self.pos] = val
            self.state = RobotState.TURN
        else:
            if val:
                self.dir = Dir.turn_right(self.dir)
            else:
                self.dir = Dir.turn_left(self.dir)
            self.pos = self.pos + self.dir.value
            self.state = RobotState.PAINT


with open("input", "r") as inp:
    init = tuple(qp(inp.read()))


grid = Grid(default=Color.BLK)
grid[Point((0, 0))] = Color.WHI
robot = Robot(grid)
p1 = IntCode(init, input_callback=robot.input, output_callback=robot.output)
p1.run()
grid.print_grid(True)
print(len(grid.tiles))
