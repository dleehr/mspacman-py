import pygame
import sys
from levels import load_levels

SCREEN = None
CLOCK = None
LEVELS = None

SCREEN_SIZE = (224, 288)
COLOR_BLACK = (0,0,0)
CLOCK_RATE = 60


CURRENT_LEVEL = 1


pygame.init()


def init_screen():
    global SCREEN  # needed to set/modify
    global CLOCK
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    CLOCK = pygame.time.Clock()


def load_data():
    global LEVELS
    LEVELS = load_levels()


def read_inputs():
    pass


def draw_game_board():
    # pixel array?
    pass


def draw_player():
    # sprite
    pass


init_screen()
load_data()

level_1_tile_list = LEVELS.tile_dict[1]
for tile_row in level_1_tile_list:
    for y in range(8):
        for tile in tile_row:
            print(tile.get_row(y), end="")
        print()


# game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    # fill the background wit black
    SCREEN.fill(COLOR_BLACK)

    read_inputs()
    draw_game_board()
    draw_player()
    
    # draw the player

    # This flips the buffer
    pygame.display.flip()
    CLOCK.tick(CLOCK_RATE)
    

