import sys
from enum import Enum
from itertools import product
from collections import namedtuple, deque, OrderedDict, defaultdict
import heapq
from functools import lru_cache
sys.path.append("..")

from common import Point, Grid, Dir

class TileType(Enum):
    WALL = '#'
    FLOOR = '.'
    KEY = 3
    DOOR = 4

TileMap = {
    TileType.WALL:  "█",
    TileType.FLOOR: '.',
    TileType.KEY:    'k',
    TileType.DOOR:  'K',
}

SearchNode = namedtuple("SearchNode", ("pos", "prev", "dist", "doors"))
DFSSearchNode = namedtuple("DFSSearchNode", ("dist", "pos", "unlocked"))
FoundKey = namedtuple("FoundKey", ("key", "pos", "dist", "doors"))

class Dykstra:
    def __init__(self, grid, all_keys, all_doors):
        self.grid = grid
        self.all_keys = all_keys
        self.all_doors = all_doors

    @lru_cache(maxsize=30)
    def dykstra(self, start):
        next_nodes = deque()
        visited = set()
        keys = []

        # Fill in initial step
        next_nodes.append(SearchNode(start, None, 0, set()))
        # Then search the whole graph
        while next_nodes:
            # Check the next point
            cstep = next_nodes.popleft()

            # fill in the next steps
            for d in Dir:
                npos = cstep.pos + d.value
                if npos not in visited and self.grid[npos] is TileType.FLOOR:
                    next_nodes.append(SearchNode(npos, cstep, cstep.dist+1, cstep.doors))
                    visited.add(npos)
                if npos not in visited and self.grid[npos] is TileType.DOOR:
                    new_doors = cstep.doors.copy()
                    new_doors.add(self.all_doors[npos].lower())
                    next_nodes.append(SearchNode(npos, cstep, cstep.dist+1, new_doors))
                    visited.add(npos)
                elif npos not in visited and self.grid[npos] is TileType.KEY:
                    next_nodes.append(SearchNode(npos, cstep, cstep.dist+1, cstep.doors))
                    keys.append(FoundKey(self.all_keys[npos], npos, cstep.dist+1, cstep.doors))
                    visited.add(npos)

        return keys

def dfs(grid, start, all_keys, all_doors, ignore_doors=False):
    next_nodes = []
    total = set(all_keys.values())
    visited = set()
    dk = Dykstra(grid, all_keys, all_doors)

    # Fill in initial step
    heapq.heappush(next_nodes, DFSSearchNode(0, start, set()))

    while next_nodes:
        # Get the next node
        cstep = heapq.heappop(next_nodes)
        # If we've already visited it, we have found a shorter path to this point
        if (cstep.pos, tuple(sorted(cstep.unlocked))) in visited:
            continue
        # Otherwise, we have now...
        visited.add((cstep.pos, tuple(sorted(cstep.unlocked))))

        # Check if this is the final node
        if cstep.unlocked == total:
            print(f"Done in {abs(cstep.dist)} steps")
            return cstep.dist

        # Get list of accessible keys
        keys = dk.dykstra(cstep.pos)

        # Then, make a node after visiting each key
        for key in keys:
            # Check that it's accessible
            if not ignore_doors and len(key.doors.difference(cstep.unlocked)) != 0:
                continue
            # And that we haven't already collected it
            if key.key in cstep.unlocked:
                continue
            nunlocked = cstep.unlocked | set((key.key,))
            heapq.heappush(next_nodes, DFSSearchNode(cstep.dist + key.dist, key.pos, nunlocked))

grid = Grid(default=TileType.WALL, tilemap=TileMap)
start = None
keys = {}
doors = {}

with open("input", "r") as f:
    cpoint = Point((0, 0))
    for line in f:
        for c in line.strip():
            if c.islower():
                grid[cpoint] = TileType.KEY
                keys[cpoint] = c
            elif c.isupper():
                grid[cpoint] = TileType.DOOR
                doors[cpoint] = c
            elif c == "@":
                grid[cpoint] = TileType.FLOOR
                assert start is None
                start = cpoint
            else:
                grid[cpoint] = TileType(c)
            cpoint = cpoint + Dir.RIGHT
        cpoint = Point((0, cpoint[1]+1))

# Part 1
dfs(grid, start, keys, doors)

# Part 2
# Fix grid
grid[start] = TileType.WALL
for d in Dir:
    grid[start+d] = TileType.WALL

# Figure out new starts, and locations of keys
starts = {}
gkeys = defaultdict(dict)
for d1, d2 in product((Dir.UP, Dir.DOWN), (Dir.LEFT, Dir.RIGHT)):
    starts[start.cmp(start+d1+d2)] = start+d1+d2
for pos, key in keys.items():
    gkeys[start.cmp(pos)][pos] = key

# Then run the search for each robot
dists = []
for k in gkeys.keys():
    dists.append(dfs(grid, starts[k], gkeys[k], doors, ignore_doors=True))
print(f"Total sum: {sum(dists)}")
#grid.print_grid(highlight=starts)