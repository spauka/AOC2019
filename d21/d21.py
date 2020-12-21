import sys
from enum import Enum, IntEnum, auto
from collections import deque
sys.path.append("..")

from intcode import IntCode
from common import qp, Point, Grid, Dir

class State(Enum):
    PROGRAM = auto()
    READ = auto()

class Robot(object):
    def __init__(self):
        self.state = State.PROGRAM
        self.ip = None
        self.pos = None

    def set_ip(self, ip):
        self.ip = ip

    def input(self):
        pass

    def output(self, val):
        pass

with open("input", "r") as inp:
    init = tuple(qp(inp.read()))

robot = Robot()
ip = IntCode(init, input_callback=robot.input, output_callback=robot.output)
robot.set_ip(ip)
