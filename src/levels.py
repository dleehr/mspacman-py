from bitplanes import load, chunk8
from map import pat, ROW_WIDTH
from pathlib import Path
import re

walls = Path(__file__).parent.parent / 'mspacman-snes' / 'walls.chr'
tiles = Path(__file__).parent.parent / 'mspacman-snes' / 'level1.map'

# These are the wall indices
wall_rows = load(walls)
wall_rows = [r for r in wall_rows if r]

# generator to list
walls = [w for w in chunk8(wall_rows)]
print(len(walls))
print('walls')

class Wall(object):
    def __init__(self, index, rows):
        self.index = index
        self.rows = rows

class Tile(object):

    def __init__(self, flips, wall):
        self.h_flip = 'H' in flips
        self.v_flip = 'V' in flips
        self.wall = wall

    def draw(self):
        for x in self.wall.rows:
            print(x)

    def get_row(self, y):
        if self.v_flip:
            y = 7-y
        row = self.wall.rows[y]
        if self.h_flip:
            row = row[::-1]
        return row


wall_list = []

for i, w in enumerate(walls):
    wall = Wall(i, w)
    wall_list.append(wall)


def generate_tile(tile):
    vals = re.search(pat, tile)
    # Group 2 is the repeats
    # Group 3 is the tile
    # group 4 is h flip
    # group 5 is v lip
    piece = int(vals.group(3), base=16)
    repeat = int(vals.group(2) or 1)
    flips = vals.group(4)
    h_flip = 'H' in flips
    v_flip = 'V' in flips
    if piece > 1 << 10:
        raise Exception('Piece index too large: {}'.format(piece))
    wall = walls[piece]
    for x in range(repeat):
        print(piece, flips, ":")        
        wall = wall_list[piece]
        tile = Tile(flips, wall)
        yield tile
            
        
def generate_tile_list():
    tile_list = []
    # now load the tiles
    tiles_rows = load(tiles)
    tiles_rows = [r for r in tiles_rows if r]
    for row in tiles_rows:
        tile_row = []
        for tile_code in row.split():
            for t in generate_tile(tile_code):
                tile_row.append(t)
        tile_list.append(tile_row)
    return tile_list
        

tile_list = generate_tile_list()
for tile_row in tile_list:
    for y in range(8):
        for tile in tile_row:
            print(tile.get_row(y), end="")
        print()
        
    