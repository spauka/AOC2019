import sys
sys.path.append("..")
from itertools import permutations
from functools import reduce

from common import qp, Point, lcm

def step_sim(planets):
    for p1, p2 in permutations(planets, 2):
        p1.vel = p1.vel + p1.pos.cmp(p2.pos)
    for planet in planets:
        planet.step()

class Planet(object):
    def __init__(self, pos):
        self.pos = pos
        self.vel = Point((0, 0, 0))

    def step(self):
        self.pos = self.pos + self.vel

    def __repr__(self):
        return f"<Planet: pos=({self.pos}), vel=({self.vel})>"

    def energy(self):
        return sum(abs(self.pos)) * sum(abs(self.vel))

planets = []
with open("input", "r") as f:
    for line in f:
        planets.append(Planet(Point(qp(line))))

nsteps = 0
cycle_find = [{}, {}, {}]
cycle_len = [None, None, None]
while not all(p is not None for p in cycle_len) or nsteps < 1000:
    for coord in range(3):
        pv = tuple((p.pos[coord], p.vel[coord]) for p in planets)
        if cycle_len[coord] is None:
            if pv in cycle_find[coord]:
                cycle_len[coord] = (cycle_find[coord][pv], nsteps - cycle_find[coord][pv])
            else:
                cycle_find[coord][pv] = nsteps
    step_sim(planets)
    nsteps += 1
    if nsteps == 1000:
        print(sum(p.energy() for p in planets))

print(cycle_len)
print(reduce(lcm, (c[1] for c in cycle_len)))