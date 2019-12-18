import sys
from asyncio import Queue, create_task, run
from itertools import permutations
sys.path.append("..")

from intcode import IntCode
from common import qp

with open("input.txt", "r") as inp:
    init = tuple(qp(inp.read()))

async def p1(phase_values):
    input_buffer = Queue()
    start_buffer = input_buffer

    tasks = []
    for phase in phase_values:
        output_buffer = Queue()
        input_buffer.put_nowait(phase)
        amp = IntCode(init, input_callback=input_buffer.get,
                      output_callback=output_buffer.put)
        tasks.append(create_task(amp.async_run()))
        input_buffer = output_buffer

    start_buffer.put_nowait(0)
    for task in tasks:
        await task
    return output_buffer.get_nowait()

async def p2(phase_values):
    input_buffer = Queue()
    start_buffer = input_buffer

    amps = []
    tasks = []
    for phase in phase_values:
        output_buffer = Queue()
        input_buffer.put_nowait(phase)
        amp = IntCode(init, input_callback=input_buffer.get,
                      output_callback=output_buffer.put)
        amps.append(amp)
        tasks.append(create_task(amp.async_run()))
        input_buffer = output_buffer
    # Create loop
    amps[-1].output_callback = start_buffer.put
    start_buffer.put_nowait(0)

    for task in tasks:
        await task
    return start_buffer.get_nowait()


vals = []
for perm in permutations((0, 1, 2, 3, 4)):
    vals.append((run(p1(perm)), perm))
print(max(vals))

vals = []
for perm in permutations((5, 6, 7, 8, 9)):
    vals.append((run(p2(perm)), perm))
print(max(vals))
