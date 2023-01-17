# this is for making a surface
from pygame import Surface

LEVEL_SIZE = (224, 248)
COLS_PER_ROW = LEVEL_SIZE[0] / 8


# encapsulates the surface and its backing walls/tiles
class Background():

    def __init__(self, level_tile_list, palette) -> None:
        self.level_tile_list = level_tile_list
        self.palette = palette
        self.surface = Surface(LEVEL_SIZE, depth=8)
        self.surface.set_palette(self.palette)

    def cycle_pellet_pallette(self):
        s = self.surface
        tmp = s.get_palette_at(5)
        s.set_palette_at(5, s.get_palette_at(6))
        s.set_palette_at(6, tmp)

    def draw_full_surface(self):
        for y in range(int(LEVEL_SIZE[1] / 8)):
            for x in range(int(LEVEL_SIZE[0] / 8)):
                self.draw_tile_on_surface(x, y)

    def draw_tile_on_surface(self, tile_x, tile_y):
        tile = self.tile_at(tile_x, tile_y)
        for local_y in range(8):
            row_in_tile = tile.get_row(local_y)
            for local_x in range(8):
                palette_value_str = row_in_tile[local_x]
                x = (tile_x * 8) + local_x
                y = (tile_y * 8) + local_y
                self.surface.set_at((x, y), int(palette_value_str))

    # get the tile at the location (not pixel coordinates)
    def tile_at(self, x, y):
        # This is a 2D list
        return self.level_tile_list[y][x]
