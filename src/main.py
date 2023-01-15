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
CLOCK_RATE = 20

GAME_BOARD_POSITION = (0, 24)
CURRENT_LEVEL = 0
BACKGROUNDS = {}

# Just some constants to make movement easier to write
class Move:
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    UP = (0, -1)
    STOP = (0, 0)


# this position is in game board pixel coordinates 
CURRENT_PLAYER_POSITION = (104, 132)
CURRENT_PLAYER_DIRECTION = Move.STOP
DESIRED_PLAYER_DIRECTION = Move.STOP

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


# sets a new DESIRED_PLAYER_DIRECTION
def read_inputs():
    DirectionMap = {
        pygame.K_LEFT: Move.LEFT,
        pygame.K_RIGHT: Move.RIGHT,
        pygame.K_UP: Move.UP,
        pygame.K_DOWN: Move.DOWN,
        pygame.K_SPACE: Move.STOP,
    }
    global DESIRED_PLAYER_DIRECTION
    for event in pygame.event.get(eventtype=pygame.KEYDOWN):
        # Just interested in the first keydown event
        if event.key in DirectionMap:
            DESIRED_PLAYER_DIRECTION = DirectionMap[event.key]
        break


def check_player_wall_collision():
    global CURRENT_PLAYER_DIRECTION
    # Compute coordinates to check for collision
    # In asm I check the direction of movement and look at the corners
    # But here I was thinking I could just divide the coordinates down to the 28x31 matrix
    # of background tiles and see where we landed.
    # Mostly working but there's still a little bit of wiggle
    # The thought here is
    #
    # 1. start at the player position (where the top left corner of the sprite is drawn)
    # 2. Add 8 to each - it's a 16x16 sprite, so that brings us to the middle pixel location.
    # 3. Then, move based on the direction. 4 px times the direction vector. That should be 
    #   just enough to move our pixel coordinate into a new square if we're going to enter one
    # 4. finally, divide by 8 to get the tile coordinate
    # But in the initial case it's still moving up/down a couple of pixels.

    x_offset = 8
    y_offset = 8
    if True:
        ypos = CURRENT_PLAYER_POSITION[1]
        dpd = DESIRED_PLAYER_DIRECTION[1]
        dpd_mult = 5
        target_y = ypos + y_offset + (dpd * dpd_mult)
        target_y_tile = int(target_y / 8)
        print('ypos', ypos)
        print('ypos + offset', ypos + y_offset)
        print('dpd', dpd)
        print('dpd * mult', dpd * dpd_mult)
        print('target y', target_y)
        print('target_y_tile', target_y_tile)
        print()

    # I see, the problem here was when movement stops. the direction vector goes
    # went -1 to 0, so that 4 px offset to bump into the next square wasn't being included
    # Updated to store DESIRED_PLAYER_DIRECTION and copy it into CURRENT_PLAYER_DIRECTION 
    # if wokkable

    # Getting closer on basic, initial movement with the 5, but the axis we're not moving here is still causing DPD to equal zero
    # and throwing off the collision detection for turning.


    target_player_tile = (
        int((CURRENT_PLAYER_POSITION[0] + x_offset + (DESIRED_PLAYER_DIRECTION[0] * 5)) / 8),
        int((CURRENT_PLAYER_POSITION[1] + y_offset + (DESIRED_PLAYER_DIRECTION[1] * 5)) / 8),
    )

    current_background = BACKGROUNDS[CURRENT_LEVEL]
    tile = current_background.tile_at(
        target_player_tile[0],
        target_player_tile[1]
        )
    # will that enter a movable background square?
    tile.draw()
    
    if tile.is_wokkable():
        CURRENT_PLAYER_DIRECTION = DESIRED_PLAYER_DIRECTION
        print("wokkable")
    else:
        # if not, set CURRENT_PLAYER_DIRECTION to (0, 0)
        # But leave desired direction unchanged
        CURRENT_PLAYER_DIRECTION = Move.STOP
        print("not wokkable")
   

def update_player_position():
    global CURRENT_PLAYER_POSITION
    NEW_X = CURRENT_PLAYER_POSITION[0] + CURRENT_PLAYER_DIRECTION[0]
    NEW_Y = CURRENT_PLAYER_POSITION[1] + CURRENT_PLAYER_DIRECTION[1]
    CURRENT_PLAYER_POSITION = (NEW_X, NEW_Y)
    print(CURRENT_PLAYER_POSITION)


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
    print('*' * 20)
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
