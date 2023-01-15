import pygame
import sys
from levels import load_levels
from background import Background, PALETTES
from player import PLAYER_PALETTE, PLAYER_SIZE, load_player, player_to_surface

SCREEN = None
CLOCK = None
LEVELS = None

CURRENT_BACKGROUND_SURFACE = None
CURRENT_PLAYER_SURFACE = None

SCREEN_SIZE = (224, 288)
COLOR_BLACK = (0, 0, 0)
CLOCK_RATE = 60

GAME_BOARD_POSITION = (0, 24)
CURRENT_LEVEL = 0
BACKGROUNDS = {}

# this position is in game board coordinates 
CURRENT_PLAYER_POSITION = (104, 132)
CURRENT_PLAYER_DIRECTION = (0, 0)

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
    global BACKGROUNDS
    level_tile_list = LEVELS.tile_dict[CURRENT_LEVEL]
    background = Background(level_tile_list, PALETTES[CURRENT_LEVEL])
    BACKGROUNDS[CURRENT_LEVEL] = background
    CURRENT_BACKGROUND_SURFACE = background.get_surface()


def load_player_surface():
    global CURRENT_PLAYER_SURFACE
    player = load_player()
    CURRENT_PLAYER_SURFACE = player_to_surface(player, PLAYER_SIZE, PLAYER_PALETTE)


# sets a new CURRENT_PLAYER_DIRECTION
def read_inputs():
    DirectionMap = {
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_SPACE: (0, 0),
    }
    global CURRENT_PLAYER_DIRECTION
    for event in pygame.event.get(eventtype=pygame.KEYDOWN):
        # Just interested in the first keydown event
        if event.key in DirectionMap:
            CURRENT_PLAYER_DIRECTION = DirectionMap[event.key]
        break


def check_player_wall_collision():
    global CURRENT_PLAYER_DIRECTION
    # Compute new player_position
    new_x = CURRENT_PLAYER_POSITION[0] + CURRENT_PLAYER_DIRECTION[0]
    new_y = CURRENT_PLAYER_POSITION[1] + CURRENT_PLAYER_DIRECTION[1]
    # this is the top left corner of the thing right?
    current_background = BACKGROUNDS[CURRENT_LEVEL]
    # Should check based on the direction of movement.
    # I did this in asm already, forgot about it.
    tile = current_background.tile_at(new_x + 7, new_y + 7)
    # will that enter a movable background square?
    if not tile.is_wokkable():
        # if not, set CURRENT_PLAYER_DIRECTION to (0, 0)
        CURRENT_PLAYER_DIRECTION = (0, 0)
    # If so, do nothing


def update_player_position():
    global CURRENT_PLAYER_POSITION
    NEW_X = CURRENT_PLAYER_POSITION[0] + CURRENT_PLAYER_DIRECTION[0]
    NEW_Y = CURRENT_PLAYER_POSITION[1] + CURRENT_PLAYER_DIRECTION[1]
    CURRENT_PLAYER_POSITION = (NEW_X, NEW_Y)


def draw_game_board():
    SCREEN.blit(CURRENT_BACKGROUND_SURFACE, GAME_BOARD_POSITION)


def draw_player():
    # sprite-like thing. Not using pygame sprites so I can understand collision detection and 
    # old, simple movement & drawing

    # CURRENT_PLAYER_POSITION is in game-board coordinates
    # if blit directly onto that, no need to offset but then I've got player smeared all over
    # so blit with the offset
    position = (
        CURRENT_PLAYER_POSITION[0] + GAME_BOARD_POSITION[0], 
        CURRENT_PLAYER_POSITION[1] + GAME_BOARD_POSITION[1],
        )
    SCREEN.blit(CURRENT_PLAYER_SURFACE, position)


init_screen()
load_data()
# load the background for the current level
load_level_background()
load_player_surface()

# game loop
while True:
    for event in pygame.event.get(eventtype=pygame.QUIT):
        sys.exit()
    # fill the background wit black
    SCREEN.fill(COLOR_BLACK)

    read_inputs()
    # Check player wall collision
    check_player_wall_collision()
    update_player_position()

    # now draw
    draw_game_board()
    draw_player()

    # where is she?
    # BACKGROUNDS[CURRENT_LEVEL].tile_at(*CURRENT_PLAYER_POSITION).draw()

    # This draws - flip the buffer
    pygame.display.flip()
    CLOCK.tick(CLOCK_RATE)
