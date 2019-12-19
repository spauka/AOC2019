import sys
from enum import Enum, IntEnum, auto
sys.path.append("..")

from intcode import IntCode
from common import qp, Point, Grid

class TileType(IntEnum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PADDLE = 3
    BALL = 4
TileMap = {
    TileType.EMPTY: " ",
    TileType.WALL: "█",
    TileType.BLOCK: "□",
    TileType.PADDLE: "━",
    TileType.BALL: "o"
}

class GameState(Enum):
    POSX = auto()
    POSY = auto()
    TYPE = auto()

class Game(object):
    def __init__(self, grid):
        self.grid = grid
        self.state = GameState.POSX
        self.x = None
        self.y = None
        self.score = None
        self.ball = None
        self.paddle = None

    def input(self):
        if self.ball[0] < self.paddle[0]:
            return -1
        if self.ball[0] > self.paddle[0]:
            return 1
        return 0
    def output(self, val):
        if self.state is GameState.POSX:
            self.x = val
            self.state = GameState.POSY
        elif self.state is GameState.POSY:
            self.y = val
            self.state = GameState.TYPE
        else:
            if (self.x, self.y) == (-1, 0):
                self.score = val
            else:
                val = TileType(val)
                point = Point((self.x, self.y))
                self.grid[point] = val
                if val is TileType.BALL:
                    self.ball = point
                elif val is TileType.PADDLE:
                    self.paddle = point
            self.state = GameState.POSX

with open("input", "r") as inp:
    init = tuple(qp(inp.read()))

grid = Grid(default=TileType.EMPTY, tilemap=TileMap)
game = Game(grid)
p1 = IntCode(init, input_callback=game.input, output_callback=game.output)
p1.run()
grid.print_grid()
print(len(list(tile for tile in grid.tiles.values() if tile == TileType.BLOCK)))

p1.reset()
p1.mem[0] = 2
p1.run()
#grid.print_grid()
print(game.score)