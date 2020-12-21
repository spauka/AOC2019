import sys
from itertools import product
from enum import Enum
from collections import deque, defaultdict, namedtuple
from string import ascii_uppercase
sys.path.append("..")

from common import Point, Grid, Dir

class TileType(Enum):
    WALL  = '#'
    PATH  = '.'
    SPACE = ' '
    PORTAL = '◉'

TileMap = {
    TileType.WALL:  "█",
    TileType.PATH:  '.',
    TileType.SPACE: " ",
    TileType.PORTAL:"◉",
}

grid = Grid(default=TileType.SPACE, tilemap=TileMap)

def is_outer(grid, pos):
    # At top or left
    if pos[0] < 3 or pos[1] < 3:
        return True
    if grid.br[0] - pos[0] < 3:
        return True
    if grid.tl[1] - pos[1] < 3:
        return True
    return False

SearchNode = namedtuple("SearchNode", ("pos", "prev", "dist", "portal", "depth"))
def dfs(grid, start, end, portals, pos_portal):
    next_nodes = deque()
    visited = set()

    next_nodes.append(SearchNode(start, None, 0, None, 0))
    while next_nodes:
        cstep = next_nodes.popleft()
        visited.add((cstep.pos, cstep.depth))

        # Check if we are at the end
        if cstep.pos == end and cstep.depth == 0:
            return cstep

        # Check if we are on a portal, and try go through it
        if grid[cstep.pos] is TileType.PORTAL:
            if is_outer(grid, cstep.pos) and cstep.depth > 0 and (portals[cstep.pos], cstep.depth-1) not in visited:
                next_nodes.append(SearchNode(portals[cstep.pos], cstep, cstep.dist+1, pos_portal[cstep.pos], cstep.depth-1))
            elif not is_outer(grid, cstep.pos) and (portals[cstep.pos], cstep.depth+1) not in visited:
                next_nodes.append(SearchNode(portals[cstep.pos], cstep, cstep.dist+1, pos_portal[cstep.pos], cstep.depth+1))
        # Otherwise do a regular search
        for d in Dir:
            npos = cstep.pos + d
            if grid[npos] in (TileType.PATH, TileType.PORTAL) and (npos, cstep.depth) not in visited:
                next_nodes.append(SearchNode(npos, cstep, cstep.dist+1, None, cstep.depth))
    return None

# Read in the grid
pos = Point((0, 0))
pos_portal = {}
portals = defaultdict(tuple)
with open("input", "r") as f:
    for line in f:
        for c in line[:-1]:
            if c in ascii_uppercase:
                grid[pos] = c
            else:
                grid[pos] = TileType(c)
            pos = pos + Dir.RIGHT
        pos = Point((0, pos[1]+1))

# Read in the portals
for x, y in product(range(grid.br[0]), range(grid.tl[1])):
    cpos = Point((x, y))
    if isinstance((l1 := grid[cpos]), str):
        if isinstance((l2 := grid[cpos + Dir.UP]), str):
            grid[cpos] = TileType.SPACE
            grid[cpos + Dir.UP] = TileType.SPACE
            if grid[cpos + Dir.DOWN] is TileType.PATH:
                cpos = cpos + Dir.DOWN
            elif grid[cpos + Dir.UP + Dir.UP] is TileType.PATH:
                cpos = cpos + Dir.UP + Dir.UP
            else:
                raise RuntimeError("Invalid portal position (UP)")
            pos_portal[cpos] = l1+l2
            portals[l1+l2] += (cpos,)
            grid[cpos] = TileType.PORTAL
        elif isinstance((l2 := grid[cpos + Dir.RIGHT]), str):
            grid[cpos] = TileType.SPACE
            grid[cpos + Dir.RIGHT] = TileType.SPACE
            if grid[cpos + Dir.LEFT] is TileType.PATH:
                cpos = cpos + Dir.LEFT
            elif grid[cpos + Dir.RIGHT + Dir.RIGHT] is TileType.PATH:
                cpos = cpos + Dir.RIGHT + Dir.RIGHT
            else:
                raise RuntimeError("Invalid portal position (ACROSS)")
            pos_portal[cpos] = l1+l2
            portals[l1+l2] += (cpos,)
            grid[cpos] = TileType.PORTAL
# Transform portals dict
start = portals['AA'][0]
end = portals['ZZ'][0]
grid[start] = TileType.PATH
grid[end] = TileType.PATH
new_portals = {}
for portal in portals.values():
    if len(portal) == 1:
        continue
    new_portals[portal[0]] = portal[1]
    new_portals[portal[1]] = portal[0]
    assert is_outer(grid, portal[0]) + is_outer(grid, portal[1]) == 1
portals = new_portals

grid.print_grid(highlight=(start, end))
steps = dfs(grid, start, end, portals, pos_portal)
print(steps.dist)
print(grid.tl, grid.br)