from bitplanes import load, chunk8
from pathlib import Path
from levels import load_palette
from pygame import Surface

CHR_SIZE = (8, 8)

# In levels.py I have walls and tiles but they're probably named incorrectly
def load_score_tiles():
    tiles_file = Path(__file__).parent.parent / 'mspacman-snes' / 'alphanum.chr'

    # These are the wall indices
    tile_rows = load(tiles_file)
    tile_rows = [t for t in tile_rows if t]

    # generator to list
    tiles = [t for t in chunk8(tile_rows)]
    return tiles


# How do I want to draw this? Just look up a tile? Blit onto a surface? I think I need to just
# load the individual surfaces here and blit them

def load_score_surfaces(tiles):
    palette_file = Path(__file__).parent.parent / 'mspacman-snes' / 'level1.pxt'
    palette = load_palette(palette_file)
    surfaces = []
    for t in tiles:
        s = Surface(CHR_SIZE, depth=8)
        s.set_palette(palette)
        for y in range(CHR_SIZE[1]):
            for x in range(CHR_SIZE[0]):
                s.set_at((x, y), int(t[y][x]))
        surfaces.append(s)
    return surfaces


if __name__ == '__main__':
    tiles = load_score_tiles()
    for t in tiles:
        print(t)
