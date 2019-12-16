import numpy as np
from itertools import product

with open("input.txt", "rb") as f:
    d = f.read().strip()
d = np.frombuffer(d, dtype=np.uint8) - 48
d = d.reshape((d.size//(25*6), 6, 25))

counts = []
for layer in d:
    layer = layer.ravel()
    counts.append((sum(layer == 0), sum(layer == 1), sum(layer == 2)))

# Part 1
mc = min(counts)
print(mc, mc[1]*mc[2])

# Part 2
image = np.full((6, 25), 2, dtype=np.uint8)
for layer in d:
    for x, y in product(range(25), range(6)):
        if image[y, x] == 2:
            image[y, x] = layer[y, x]
for y in range(6):
    for x in range(25):
        print(" " if image[y, x] == 0 else "█", end='')
    print()
