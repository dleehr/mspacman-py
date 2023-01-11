# this is for making a surface
from pygame import Surface

# hard-coded palette for level 1
PALETTE = {
    0: (0x00, 0x00, 0x00),
    1: (0xfb, 0x00, 0x07),
    2: (0xfd, 0xa9, 0x85),
    3: (0xd6, 0xd6, 0xd6),
    4: (0xff, 0xff, 0xff),
}


# This is pixel-based and probably horribly inefficient
def level_to_surface(level_tile_list, screen_size):
    # level is a tile list
    s = Surface(screen_size, )
    for row_offset, tile_row in enumerate(level_tile_list):
        for tile_y in range(8):
            for col_offset, tile in enumerate(tile_row):
                row_in_tile = tile.get_row(tile_y)
                for tile_x in range(8):
                    palette_value_str = row_in_tile[tile_x]
                    x = (col_offset * 8) + tile_x
                    y = (row_offset * 8) + tile_y
                    # now plot this
                    s.set_at((x, y), PALETTE[int(palette_value_str)])
    return s
