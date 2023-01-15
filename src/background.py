# this is for making a surface
from pygame import Surface

LEVEL_SIZE = (224, 248)
COLS_PER_ROW = LEVEL_SIZE[0] / 8

# hard-coded palette for level 1
PALETTES = [{
    0: (0x00, 0x00, 0x00),
    1: (0xfb, 0x00, 0x07),
    2: (0xfd, 0xa9, 0x85),
    3: (0xd6, 0xd6, 0xd6),
    4: (0xff, 0xff, 0xff),
}]


# encapsulates the surface and its backing walls/tiles
class Background():

    def __init__(self, level_tile_list, palette) -> None:
        self.level_tile_list = level_tile_list
        self.palette = palette

    def get_surface(self):
        # level is a tile list
        s = Surface(LEVEL_SIZE)
        for row_offset, tile_row in enumerate(self.level_tile_list):
            for tile_y in range(8):
                for col_offset, tile in enumerate(tile_row):
                    row_in_tile = tile.get_row(tile_y)
                    for tile_x in range(8):
                        palette_value_str = row_in_tile[tile_x]
                        x = (col_offset * 8) + tile_x
                        y = (row_offset * 8) + tile_y
                        # now plot this
                        s.set_at((x, y), self.palette[int(palette_value_str)])
        return s

    # get the wall at the pixel coordinate
    def tile_at(self, x, y):
        tile_x = int(x / 8)
        tile_y = int(y / 8)
        # This is a 2D list
        return self.level_tile_list[tile_y][tile_x]
