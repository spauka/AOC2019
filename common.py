import re
from enum import Enum

def qp(line):
    m = re.findall(r"([-+\d]+)", line)
    return tuple(int(x) for x in m)

def gcd(x, y):
    if y == 0: return x
    return gcd(y, x%y)
def lcm(x, y):
    return x*y//gcd(x, y)

class Point(tuple):
    def __add__(self, o):
        return Point((x+y for x, y in zip(self, o)))

    def __sub__(self, o):
        return Point((x-y) for x, y in zip(self, o))

    def __abs__(self):
        return Point(abs(x) for x in self)

    def __repr__(self):
        return f"Point{super().__repr__()}"

    def adjacent(self, other):
        try:
            return Dir(other - self)
        except ValueError:
            return False

    @staticmethod
    def cmpi(i, o):
        if i < o: return 1
        if i == o: return 0
        return -1

    def cmp(self, other):
        return Point(self.cmpi(s, o) for s, o in zip(self, other))


class Grid(object):
    def __init__(self, default=0, tilemap=None):
        self.tiles = {}
        self.tl = Point((0, 0))
        self.br = Point((0, 0))
        self.default = default
        self.tilemap = tilemap

    def __getitem__(self, point):
        if point in self.tiles:
            return self.tiles[point]
        return self.default

    def __setitem__(self, point, tiletype):
        self.tiles[point] = tiletype
        self.tl = Point((min(point[0], self.tl[0]), max(point[1], self.tl[1])))
        self.br = Point((max(point[0], self.br[0]), min(point[1], self.br[1])))

    def print_grid(self, flipy=False, highlight=None, highlight_val="X"):
        output = []
        for y in range(self.br[1], self.tl[1]+1):
            line = []
            for x in range(self.tl[0], self.br[0]+1):
                if highlight == Point((x, y)):
                    line.append(highlight_val)
                elif self.tilemap is not None:
                    line.append(self.tilemap[self[Point((x, y))]])
                else:
                    line.append("█" if self[Point((x, y))] else " ")
            output.append("".join(line))
        if flipy:
            output.reverse()
        print("\n".join(output))


class Dir(Enum):
    UP = Point((0, 1))
    RIGHT = Point((1, 0))
    DOWN = Point((0, -1))
    LEFT = Point((-1, 0))

    @classmethod
    def dirs(cls):
        return tuple(cls.__members__.keys())

    @classmethod
    def turn_left(cls, val):
        return getattr(cls, cls.dirs()[(cls.dirs().index(val.name)-1)%4])
    @classmethod
    def turn_right(cls, val):
        return getattr(cls, cls.dirs()[(cls.dirs().index(val.name)+1)%4])