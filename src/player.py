from bitplanes import load, chunk8
from pathlib import Path
from pygame import Surface

# load 'mspacman.chr'

# Need to load different animation sets somehow

PLAYER_PALETTE = {
    0: (0x00, 0x00, 0x00),
    1: (0xff, 0xfb, 0x01),
    2: (0xff, 0x25, 0x00),
    3: (0x20, 0x2b, 0xde),
    4: (0xff, 0xff, 0xff),
}

PLAYER_SIZE = (16, 16)

class Player():

    # These are structured differently than background tiles.

    # 16x16. blocks should be a list of 8x8, laid out 
    # 0 1
    # 2 3
    def __init__(self, blocks):
        self.blocks = blocks

    # Returns the palette value (character) in the 16x16 grid
    def get_at(self, x, y):
        # 0 and 1 make the top left and top right
        # 2 and 3 make bototm left and bottom right
        squares = [
            [self.blocks[0], self.blocks[1]],
            [self.blocks[2], self.blocks[3]]
        ]
        # if x is 0-7 we want block 0 or 2. If it's 8-15 we want 1 or 3
        # if y is 0-7 we want block 0 or 1. If it's 8-15 we want 2 or 3
        s_x, x = int(x / 8), x % 8
        s_y, y = int(y / 8), y % 8
        block = squares[s_y][s_x]
        return block[y][x]

    def print_all(self):
        # Just for debugging
        for y in range(16):
            for x in range(16):
                print(self.get_at(x, y), end='')
            print()


def load_player():
    player_file = Path(__file__).parent.parent / 'mspacman-snes' / 'mspacman.chr'
    # Each line in the file has 8 characters
    # We're interested in block 0, 1, 16, 17 for now.
    # They're laid out that way for SNES graphics
    rows = load(player_file)
    rows = [r for r in rows if r]
    blocks = [x for x in chunk8(rows)]
    blocks = [blocks[0], blocks[1], blocks[16], blocks[17]]
    p = Player(blocks)
    return p


def player_to_surface(player, size, palette):
    s = Surface(size)
    for y in range(size[1]):
        for x in range(size[0]):
            palette_value_str = player.get_at(x, y)
            s.set_at((x, y), palette[int(palette_value_str)])
    return s


if __name__ == '__main__':
    p = load_player()
    p.print_all()
    print(player_to_surface(p, PLAYER_SIZE, PLAYER_PALETTE))
