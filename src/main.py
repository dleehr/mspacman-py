import pygame
import sys
from levels import load_levels
from background import level_to_surface

SCREEN = None
CLOCK = None
LEVELS = None

CURRENT_BACKGROUND_SURFACE = None

SCREEN_SIZE = (224, 288)
COLOR_BLACK = (0, 0, 0)
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


def load_level_background():
    global CURRENT_BACKGROUND_SURFACE
    CURRENT_BACKGROUND_SURFACE = level_to_surface(LEVELS.tile_dict[CURRENT_LEVEL], SCREEN_SIZE)


def read_inputs():
    pass


def draw_game_board():
    SCREEN.blit(CURRENT_BACKGROUND_SURFACE, (0, 0))
    # CURRENT_BACKGROUND_SURFACE.blit(SCREEN, (0, 0))


def draw_player():
    # sprite
    pass


init_screen()
load_data()
# load the background for the current level
load_level_background()


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
