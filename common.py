import re

def qp(line):
    m = re.findall(r"([-+\d]+)", line)
    return tuple(int(x) for x in m)

class Point(tuple):
    def __add__(self, o):
        return Point((x+y for x, y in zip(self, o)))

    def __sub__(self, o):
        return Point((x-y) for x, y in zip(self, o))

    def __abs__(self):
        return Point(abs(x) for x in self)

    @staticmethod
    def cmpi(i, o):
        if i < o:
            return 1
        elif i == o:
            return 0
        else:
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

    def print_grid(self):
        for y in range(self.br[1], self.tl[1]+1):
            for x in range(self.tl[0], self.br[0]+1):
                if self.tilemap is not None:
                    print(self.tilemap[self[Point((x, y))]], end="")
                else:
                    print("█" if self[Point((x, y))] else " ", end="")
            print()
