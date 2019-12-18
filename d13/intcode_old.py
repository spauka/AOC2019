import re
from collections import namedtuple, defaultdict
from enum import Enum, IntEnum, auto
from operator import add, mul, lt, eq
from functools import reduce
from asyncio import run, iscoroutinefunction

def qp(line):
    m = re.findall(r"([-+\d]+)", line)
    return tuple(int(x) for x in m)

def compose(*functions):
    return reduce(lambda f, g: lambda *x: f(g(*x)), functions, lambda x: x)

Instr = namedtuple("Instr", ("name", "code", "args",
                             "output", "action", "ip_inc"))

class States(Enum):
    RESET = auto()
    RUNNING = auto()
    FINISHED = auto()

class ArgMode(Enum):
    POS = 0
    IMM = 1
    REL = 2

class Memory(list):
    def __init__(self, init):
        super().__init__(init)
        self.extra_addrs = defaultdict(int)

    def __getitem__(self, idx):
        try:
            return super().__getitem__(idx)
        except IndexError:
            return self.extra_addrs[idx]

    def __setitem__(self, idx, val):
        try:
            super().__setitem__(idx, val)
        except IndexError:
            self.extra_addrs[idx] = val

class IntCode(object):
    def __init__(self, mem, ip=0, input_callback=None, output_callback=None):
        self.__origmem__ = tuple(mem)
        self.mem = Memory(mem)
        self.ip = ip
        self.rb = 0
        self.state = States.RESET
        self.instrs = {
            1: Instr("add", 1, 2, True, add, 4),
            2: Instr("mul", 2, 2, True, mul, 4),
            3: Instr("input", 3, 0, True, self.input, 2),
            4: Instr("output", 4, 1, False, self.output, 2),
            5: Instr("jit", 5, 2, False, self.jit, 0),
            6: Instr("jif", 6, 2, False, self.jif, 0),
            7: Instr("lt", 7, 2, True, compose(int, lt), 4),
            8: Instr("gt", 8, 2, True, compose(int, eq), 4),
            9: Instr("rbs", 9, 1, False, self.rbs, 2),
            99: Instr("term", 99, 0, False, self.term, 0),
        }
        self.input_callback = input_callback
        self.output_callback = output_callback

    def run(self):
        return run(self.async_run())

    async def async_run(self):
        self.state = States.RUNNING
        while self.state is States.RUNNING:
            opcode = self.mem[self.ip] % 100
            argmodes = self.mem[self.ip]//100
            c_instr = self.instrs[opcode]
            args, output = self._get_args(
                argmodes, c_instr.args, c_instr.output)
            if iscoroutinefunction(c_instr.action):
                res = await c_instr.action(*args)
            else:
                res = c_instr.action(*args)
            if c_instr.output:
                self.mem[output] = res
            self.ip += c_instr.ip_inc

    def term(self):
        self.state = States.FINISHED

    def reset(self):
        self.mem = Memory(self.__origmem__)
        self.ip = 0
        self.state = States.RESET

    def _get_args(self, modes, n_args, output=True):
        args = []
        arg = -1
        for arg in range(n_args):
            mode = ArgMode((modes//(10**arg)) % 10)
            if mode is ArgMode.IMM:
                args.append(self.mem[self.ip + arg + 1])
            elif mode is ArgMode.POS:
                args.append(self.mem[self.mem[self.ip + arg + 1]])
            elif mode is ArgMode.REL:
                args.append(self.mem[self.mem[self.ip + arg + 1] + self.rb])
            else:
                raise ValueError("Invalid parameter mode")

        if output:
            arg += 1
            output_mode = ArgMode((modes//(10**arg)) % 10)
            if output_mode is ArgMode.POS:
                output = self.mem[self.ip + arg + 1]
            elif output_mode is ArgMode.REL:
                output = self.mem[self.ip + arg + 1] + self.rb
            else:
                raise ValueError(
                    "Parameter shouldn't be able to write in IMM or REL mode")

        return args, output

    # Instrs
    async def input(self):
        if iscoroutinefunction(self.input_callback):
            return await self.input_callback()
        else:
            return self.input_callback()

    async def output(self, arg):
        if iscoroutinefunction(self.output_callback):
            await self.output_callback(arg)
        else:
            self.output_callback(arg)

    def rbs(self, offs):
        self.rb += offs

    def jit(self, cmp, addr):
        if cmp:
            self.ip = addr
        else:
            self.ip += 3

    def jif(self, cmp, addr):
        if cmp == 0:
            self.ip = addr
        else:
            self.ip += 3

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

class Point(tuple):
    def __add__(self, o):
        return Point((x+y for x, y in zip(self, o)))

    def __sub__(self, o):
        return Point((x-y) for x, y in zip(self, o))

    def __abs__(self):
        return Point(abs(x) for x in self)

class Grid(object):
    def __init__(self):
        self.tiles = {}
        self.tl = Point((0, 0))
        self.br = Point((0, 0))

    def __getitem__(self, point):
        if point in self.tiles:
            return self.tiles[point]
        return TileType.EMPTY

    def __setitem__(self, point, tiletype):
        tiletype = TileType(tiletype)
        self.tiles[point] = tiletype
        self.tl = Point((min(point[0], self.tl[0]), max(point[1], self.tl[1])))
        self.br = Point((max(point[0], self.br[0]), min(point[1], self.br[1])))

    def print_grid(self):
        for y in range(self.br[1], self.tl[1]+1):
            for x in range(self.tl[0], self.br[0]+1):
                print(TileMap[self[Point((x, y))]], end="")
            print()


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
        elif self.ball[0] > self.paddle[0]:
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


grid = Grid()
game = Game(grid)
p1 = IntCode(init, input_callback=game.input, output_callback=game.output)
p1.run()
grid.print_grid()
print(len(list(tile for tile in grid.tiles.values() if tile == TileType.BLOCK)))

p1.reset()
p1.mem[0] = 2
p1.run()
grid.print_grid()
print(game.score)