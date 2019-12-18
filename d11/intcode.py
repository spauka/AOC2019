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

class Color(IntEnum):
    BLK = 0
    WHI = 1

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


class Point(tuple):
    def __add__(self, o):
        return Point((x+y for x, y in zip(self, o)))

    def __sub__(self, o):
        return Point((x-y) for x, y in zip(self, o))
    
    def __abs__(self):
        return Point(abs(x) for x in self)

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

class Grid(object):
    def __init__(self):
        self.tiles = {}
        self.tl = Point((0, 0))
        self.br = Point((0, 0))
    
    def __getitem__(self, point):
        if point in self.tiles:
            return self.tiles[point]
        return Color.BLK

    def __setitem__(self, point, color):
        color = Color(color)
        self.tiles[point] = color
        self.tl = Point((min(point[0], self.tl[0]), max(point[1], self.tl[1])))
        self.br = Point((max(point[0], self.br[0]), min(point[1], self.br[1])))

    def print_grid(self):
        for y in range(self.tl[1], self.br[1]-1, -1):
            for x in range(self.tl[0], self.br[0]+1):
                print("." if self[Point((x, y))] == Color.BLK else "█", end="")
            print()

class RobotState(Enum):
    PAINT = 0
    TURN = 1

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


grid = Grid()
grid[Point((0, 0))] = Color.WHI
robot = Robot(grid)
p1 = IntCode(init, input_callback=robot.input, output_callback=robot.output)
p1.run()
grid.print_grid()
print(len(grid.tiles))
