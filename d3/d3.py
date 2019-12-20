import sys
sys.path.append("..")

from common import Point, Grid, Dir

d = []
with open("input", "r") as inp:
    for line in inp:
        d.append(tuple((l[0], int(l[1:]))
                 for l in line.strip().split(',')))

def fill_grid(grid, moves):
    curr = Point((0, 0))
    nmoves = 0
    for move, count in moves:
        for _ in range(count):
            nmoves += 1
            curr = curr + Dir(move).value
            if curr not in grid:
                grid[curr] = nmoves

grid1, grid2 = Grid(), Grid()
fill_grid(grid1, d[0])
fill_grid(grid2, d[1])

dists = []
delays = []
for p in grid1.points() & grid2.points():
    dists.append(abs(p[0]) + abs(p[1]))
    delays.append(grid1[p] + grid2[p])
print(min(dists))
print(min(delays))
