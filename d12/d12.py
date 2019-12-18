from itertools import permutations
import sys
sys.path.append("..")

from common import qp, Point

class Planet(object):
    def __init__(self, pos):
        self.pos = pos
        self.vel = Point((0, 0, 0))

    def step(self):
        self.pos = self.pos + self.vel

    def __repr__(self):
        return f"<Planet: pos=({self.pos}), vel=({self.vel})>"

planets = []
with open("input", "r") as f:
    for line in f:
        planets.append(Planet(Point(qp(line))))

for i in range(1000):
    for p1, p2 in permutations(planets, 2):
        p1.vel = p1.vel + p1.pos.cmp(p2.pos)
    for planet in planets:
        planet.step()
print(sum(sum(abs(p.pos))*sum(abs(p.vel)) for p in planets))

nsteps = 0