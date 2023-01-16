import pygame
import sys
from levels import load_levels
from background import Background
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

# Just some constants to make movement easier to write
class Move:
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    UP = (0, -1)
    STOP = (0, 0)


# this position is in game board pixel coordinates, and the top left of the peg
CURRENT_PLAYER_POSITION = (100, 128)
CURRENT_PLAYER_TILE_POSITION = None # Keep the 28x36 coordinate of the tile the player is on or moving to for collision detection
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
    background = Background(level_tile_list, LEVELS.palettes_dict[CURRENT_LEVEL])
    BACKGROUNDS[CURRENT_LEVEL] = background
    background.draw_full_surface()
    CURRENT_BACKGROUND_SURFACE = background.surface


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

# So for momentum in the ASM code I do it a little differently
# First, read the input and check wokkable on that
# If joypad input tried to move into a wall, load last good player direction
# and check wokkable again


def get_current_background_tile(x, y):
    current_background = BACKGROUNDS[CURRENT_LEVEL]
    return current_background.tile_at(x, y)


def get_tile_position(position, direction):
    # If moving up or down, can't move if not aligned on an X tile
    if direction[1] != 0 and position[0] % 8 != 0:
        return None

    # If moving left or right, can't move if not aligned on a Y tile
    if direction[0] != 0 and position[1] % 8 != 0:
        return None

    # First, add 8. Let's explore the initial position (100, 128) for why
    # That's the top left corner of the peg. Looking at the Y-coordinate, 128 is the
    # last row of pixels in the tile at y-index 16. but the character is drawn on tile
    # at y 17. So we add 8 to get to 136, putting us at the last row of tile row 17 for initial calculation.
    #
    # If we move UP, we subtract 1 to get 135. That's the last pixel in row in 16,
    # which is what we want when moving UP from the top of tile row 17
    # If we move DOWN, we add 1 to get 137, then add 7 to get 144. That's the first pixel in row 18
    # which is what we want to check when moving DOWN from the bottom of tile row 18
    # Do the same thing for X for the same reasons

    target_x = position[0] + direction[0] + 8
    target_y = position[1] + direction[1] + 8

    if direction == Move.RIGHT:
        target_x = target_x + 7
    elif direction == Move.DOWN:
        target_y = target_y + 7

    target_tile = (
        int(target_x / 8),
        int(target_y / 8),
    )

    return target_tile


# This checks the desired direction and current direction against
# the map to see if they can move where they're trying to
# It updates CURRENT_PLAYER_DIRECTION and CURRENT_PLAYER_TILE_POSITION if
# the target tile is wokkable
def check_player_wall_collision():
    global CURRENT_PLAYER_DIRECTION
    global CURRENT_PLAYER_TILE_POSITION
    tile_position = get_tile_position(CURRENT_PLAYER_POSITION, DESIRED_PLAYER_DIRECTION)
    if not tile_position:
        return
    tile = get_current_background_tile(tile_position[0], tile_position[1])
    # return tile might be None
    if tile.is_wokkable():
        CURRENT_PLAYER_DIRECTION = DESIRED_PLAYER_DIRECTION
        CURRENT_PLAYER_TILE_POSITION = tile_position
        return
    tile_position = get_tile_position(CURRENT_PLAYER_POSITION, CURRENT_PLAYER_DIRECTION)
    if not tile_position:
        return
    tile = get_current_background_tile(tile_position[0], tile_position[1])
    if tile.is_wokkable():
        CURRENT_PLAYER_DIRECTION = CURRENT_PLAYER_DIRECTION
        CURRENT_PLAYER_TILE_POSITION = tile_position
        return
    CURRENT_PLAYER_DIRECTION = Move.STOP


def check_player_eat_dot():
    # look at current tile
    tile = get_current_background_tile(CURRENT_PLAYER_TILE_POSITION[0], CURRENT_PLAYER_TILE_POSITION[1])
    if tile.is_edible():
        points = tile.get_points()
        print('eat', points)
        tile.clear_wall()
        # now reload the background there
        BACKGROUNDS[CURRENT_LEVEL].draw_tile_on_surface(
            CURRENT_PLAYER_TILE_POSITION[0],
            CURRENT_PLAYER_TILE_POSITION[1]
            )


# This is pretty small. might go better with check wall collision but for now it's
# separate function
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

    # add 4 more so my player position doesn't have to be the top left corner
    position = (
        CURRENT_PLAYER_POSITION[0] + GAME_BOARD_POSITION[0] + 4,
        CURRENT_PLAYER_POSITION[1] + GAME_BOARD_POSITION[1] + 4,
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
    check_player_eat_dot()

    # This just updates the draw location of the player.
    # Collision and other stuff is done elsewhere
    update_player_position()

    # now draw
    draw_game_board()
    draw_player()

    # where is she?
    # BACKGROUNDS[CURRENT_LEVEL].tile_at(*CURRENT_PLAYER_POSITION).draw()

    # This draws - flip the buffer
    pygame.display.flip()
    CLOCK.tick(CLOCK_RATE)
