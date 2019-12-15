from collections import namedtuple
from queue import Queue


class Planet(object):
    _all_planets = {}

    def __init__(self, name):
        self.name = name
        self.orbits = None
        self.has_orbits = []

    def add_orbit(self, orbits):
        if self.orbits is not None:
            raise RuntimeError(f"Duplicate orbit for {self}")
        self.orbits = orbits
        orbits.has_orbits.append(self)

    @classmethod
    def get_planet(cls, name):
        if name not in cls._all_planets:
            new_planet = cls(name)
            cls._all_planets[name] = new_planet
            return new_planet
        return cls._all_planets[name]

    def __repr__(self):
        if self.orbits is not None:
            return f"<Planet({self.name}) orbits {self.orbits.name}>"
        else:
            return f"<Planet({self.name})>"

    def dist_from_com(self):
        if self.orbits is None:
            return 0
        else:
            return 1+self.orbits.dist_from_com()


SearchStep = namedtuple("SearchStep", ("node", "dist"))


def add_steps(planet, depth, next_nodes, visited):
    for next_planet in planet.has_orbits:
        if next_planet not in visited:
            next_nodes.put(SearchStep(next_planet, depth+1))
    if planet.orbits is not None and planet.orbits not in visited:
        next_nodes.put(SearchStep(planet.orbits, depth+1))


def bfs(start, target):
    next_nodes = Queue()
    visited = set()
    add_steps(start, 0, next_nodes, visited)
    while next_nodes:
        cstep = next_nodes.get()
        visited.add(cstep.node)
        if cstep.node == target:
            return cstep.dist
        add_steps(cstep.node, cstep.dist, next_nodes, visited)
    return None


com = Planet.get_planet("COM")
with open("input.txt", "r") as inp:
    for line in inp:
        p1, p2 = line.strip().split(")")
        Planet.get_planet(p2).add_orbit(Planet.get_planet(p1))

# Part 1
print(sum(p.dist_from_com() for p in Planet._all_planets.values()))

# Part 2
start = Planet.get_planet("YOU").orbits
target = Planet.get_planet("SAN").orbits
print(bfs(start, target))
