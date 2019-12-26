import sys
from enum import Enum
from collections import namedtuple, deque, OrderedDict
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

class LRU(OrderedDict):
    def __init__(self, capacity=2**14):
        self.capacity = capacity
        super().__init__()

    def __getitem__(self, key):
        val = self.pop(key)
        self[key] = val
        return val

    def __setitem__(self, key, val):
        try:
            self.pop(key)
        except KeyError:
            if len(self) >= self.capacity:
                self.popitem(last=False)
        super().__setitem__(key, val)

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

def dfs(grid, start, all_keys, all_doors):
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
            return

        # Get list of accessible keys
        keys = dk.dykstra(cstep.pos)

        # Then, make a node after visiting each key
        for key in keys:
            # Check that it's accessible
            if len(key.doors.difference(cstep.unlocked)) != 0:
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

dfs(grid, start, keys, doors)