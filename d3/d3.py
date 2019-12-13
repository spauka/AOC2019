class Point(tuple):
    def __add__(self, o):
        return Point((x+y for x, y in zip(self, o)))
dirs = {"U": Point((0, 1)),
        "D": Point((0, -1)),
        "L": Point((-1, 0)),
        "R": Point((1, 0))}

d = []
with open("input", "r") as inp:
    for line in inp:
        d.append(tuple((l[0], int(l[1:]))
                 for l in line.strip().split(',')))

def fill_grid(moves):
    visited = {}
    curr = Point((0, 0))
    nmoves = 0
    for move, count in moves:
        for _ in range(count):
            nmoves += 1
            curr = curr + dirs[move]
            if curr not in visited:
                visited[curr] = nmoves
    return visited

visited_w1 = fill_grid(d[0])
visited_w2 = fill_grid(d[1])

dists = []
delays = []
for p in visited_w1.keys() & visited_w2.keys():
    dists.append(abs(p[0]) + abs(p[1]))
    delays.append(visited_w1[p] + visited_w2[p])
print(min(dists))
print(min(delays))
