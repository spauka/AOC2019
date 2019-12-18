import sys
from functools import partial
sys.path.append("..")

from intcode import IntCode
from common import qp

with open("input", "r") as inp:
    init = tuple(qp(inp.read()))

p1 = IntCode(init, input_callback=lambda: int(input("Input: ")), output_callback=print)
p1.run()