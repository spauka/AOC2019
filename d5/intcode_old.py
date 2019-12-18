import re
from collections import namedtuple
from enum import Enum, auto
from operator import add, mul, lt, eq
from functools import reduce

def qp(pl):
    m = re.findall(r"([-+\d]+)", pl)
    return tuple(int(x) for x in m)

with open("input", "r") as inp:
    for line in inp:
        init = tuple(qp(line))

def compose(*functions):
    return reduce(lambda f, g: lambda *x: f(g(*x)), functions, lambda x: x)

Instr = namedtuple("Instr", ("name", "code", "args", "output", "action", "ip_inc"))
class States(Enum):
    RESET = auto()
    RUNNING = auto()
    FINISHED = auto()
class ArgMode(Enum):
    POS = 0
    IMM = 1

class IntCode(object):
    def __init__(self, mem, ip = 0):
        self.__origmem__ = tuple(mem)
        self.mem = list(mem)
        self.__origip__ = ip
        self.ip = ip
        self.state = States.RESET
        self.instrs = {
            1: Instr("add", 1, 2, True, add, 4),
            2: Instr("mul", 2, 2, True, mul, 4),
            3: Instr("input", 3, 0, True, self.input, 2),
            4: Instr("output", 4, 1, False, self.output, 2),
            5: Instr("jit", 5, 2, False, self.jit, 0),
            6: Instr("jif", 6, 2, False, self.jif, 0),
            7: Instr("lt", 2, 2, True, compose(int, lt), 4),
            8: Instr("gt", 2, 2, True, compose(int, eq), 4),
            99: Instr("term", 99, 0, False, self.term, 0),
        }

    def run(self):
        self.state = States.RUNNING
        while self.state is States.RUNNING:
            opcode = self.mem[self.ip] % 100
            argmodes = self.mem[self.ip]//100
            c_instr = self.instrs[opcode]
            args, output = self._get_args(argmodes, c_instr.args, c_instr.output)
            res = c_instr.action(*args)
            if c_instr.output:
                self.mem[output] = res
            self.ip += c_instr.ip_inc

    def term(self):
        self.state = States.FINISHED

    def reset(self):
        self.mem = list(self.__origmem__)
        self.ip = self.__origip__
        self.state = States.RESET

    def _get_args(self, modes, n_args, output=True):
        args = []
        arg = -1
        for arg in range(n_args):
            mode = ArgMode((modes//(10**arg))%10)
            if mode is ArgMode.IMM:
                args.append(self.mem[self.ip + arg + 1])
            elif mode is ArgMode.POS:
                args.append(self.mem[self.mem[self.ip + arg + 1]])
            else:
                raise ValueError("not comparing")

        if output:
            arg += 1
            output_mode = ArgMode((modes//(10**arg))%10)
            if output_mode is ArgMode.IMM:
                raise ValueError("Parameter shouldn't be able to write in IMM mode")
            elif output_mode is ArgMode.POS:
                output = self.mem[self.ip + arg + 1]

        return args, output

    # Instrs
    def input(self):
        return int(input("Input: "))

    def output(self, arg):
        print(f"Output: {arg}")

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

p1 = IntCode(init)
p1.run()