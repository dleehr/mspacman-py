from bitplanes import load, chunk8
from map import pat
from pathlib import Path
import re

DOT_POINTS = 10
PP_POINTS = 50


def load_palette(filename):
    rows = load(filename)
    palette = {}
    for i, row in enumerate(rows):
      # parse text and convert to hex
      components = [int(x, base=16) for x in re.findall('..', row) ]
      palette[i] = components
    return palette


class Wall(object):
    def __init__(self, index, rows):
        self.index = index
        self.rows = rows


CLEAR_WALL = Wall(0, ['0' * 8] * 8)


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

    def is_wokkable(self):
        # Full-black, with dot, and with power pellet all true
        return self.wall.index in [0, 1, 2]

    def is_edible(self):
        return self.wall.index in [1, 2]

    def get_points(self):
        if self.wall.index == 1:
            return DOT_POINTS
        elif self.wall.index == 2:
            return PP_POINTS
        else:
            return 0

    # initially tried changing the index on the wall, but that changes ALL the
    # tiles using the same wall. So instead we change the underlying wall to
    # the CLEAR_WALL, which is index 0 and then 8x8 '0'
    def clear_wall(self):
        self.wall = CLEAR_WALL


class Levels(object):

    def __init__(self, wall_list, tile_dict, palettes_dict):
        self.wall_list = wall_list
        self.tile_dict = tile_dict
        self.palettes_dict = palettes_dict


def load_levels():
    walls = Path(__file__).parent.parent / 'mspacman-snes' / 'walls.chr'
    tiles = Path(__file__).parent.parent / 'mspacman-snes' / 'level1.map'
    palette = Path(__file__).parent.parent / 'mspacman-snes' / 'level1.pxt'

    # These are the wall indices
    wall_rows = load(walls)
    wall_rows = [r for r in wall_rows if r]

    # generator to list
    walls = [w for w in chunk8(wall_rows)]

    wall_list = []

    for i, w in enumerate(walls):
        wall = Wall(i, w)
        wall_list.append(wall)

    tile_list = generate_tile_list(tiles, wall_list)
    # This is a dict now but should probably just be a list
    tile_dict = {0: tile_list}
    palettes_dict = {0: load_palette(palette)}
    levels = Levels(wall_list, tile_dict, palettes_dict)
    return levels


def generate_tile(tile, wall_list):
    vals = re.search(pat, tile)
    # Group 2 is the repeats
    # Group 3 is the tile
    # group 4 is h flip
    # group 5 is v lip
    piece = int(vals.group(3), base=16)
    repeat = int(vals.group(2) or 1)
    flips = vals.group(4)
    if piece > 1 << 10:
        raise Exception('Piece index too large: {}'.format(piece))
    for x in range(repeat):
        wall = wall_list[piece]
        tile = Tile(flips, wall)
        yield tile


def generate_tile_list(tiles, wall_list):
    tile_list = []
    # now load the tiles
    tiles_rows = load(tiles)
    tiles_rows = [r for r in tiles_rows if r]
    for row in tiles_rows:
        tile_row = []
        for tile_code in row.split():
            for t in generate_tile(tile_code, wall_list):
                tile_row.append(t)
        tile_list.append(tile_row)
    return tile_list
