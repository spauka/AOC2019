import re
from collections import namedtuple, defaultdict
from enum import Enum, auto
from operator import add, mul, lt, eq
from functools import reduce
from itertools import permutations
from asyncio import Queue, create_task, run, iscoroutinefunction


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
    def __init__(self, mem, ip=0, input_buffer=None, output_buffer=None):
        self.__origmem__ = tuple(mem)
        self.mem = Memory(mem)
        self.ip = 0
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
        self.input_buffer = input_buffer
        self.output_buffer = output_buffer

    async def run(self):
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
        return await self.input_buffer.get()

    async def output(self, arg):
        await self.output_buffer.put(arg)

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


with open("input.txt", "r") as inp:
    init = tuple(qp(inp.read()))


input_buffer = Queue()
output_buffer = Queue()
input_buffer.put_nowait(1)
p1 = IntCode(init, input_buffer=input_buffer, output_buffer=output_buffer)
run(p1.run())
while not output_buffer.empty():
    print(output_buffer.get_nowait())
