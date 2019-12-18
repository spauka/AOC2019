import sys
from asyncio import Queue
sys.path.append("..")

from intcode import IntCode
from common import qp

with open("input.txt", "r") as inp:
    init = tuple(qp(inp.read()))

input_buffer = Queue()
output_buffer = Queue()
input_buffer.put_nowait(1)
p1 = IntCode(init, input_callback=input_buffer.get, output_callback=output_buffer.put)
p1.run()
while not output_buffer.empty():
    print(output_buffer.get_nowait())
