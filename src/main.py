import pygame
import sys
from levels import load_levels
from background import Background
from score import load_score_surfaces, load_score_tiles
from player import PLAYER_SIZE, load_players, player_to_surface

SCREEN = None
CLOCK = None
LEVELS = None

CURRENT_BACKGROUND_SURFACE = None
CURRENT_PLAYER_SURFACES = None
SCORE_SURFACES = None

SCREEN_SIZE = (224, 288)
COLOR_BLACK = (0, 0, 0)
CLOCK_RATE = 60
TICK_COUNTER = 0

GAME_BOARD_POSITION = (0, 24)
SCORE_DRAW_POSITION = [
  (0, 1),               # ends at 6, 1, e.g. .....00. Could just always draw the final 0 every time
  None                  # TODO: Where to put 2UP score
]
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
CURRENT_PLAYER_ANIMATION_FRAME_INDEX = 0
PLAYER_ANIMATION_FRAMES = [0, 1, 0, 2]


# Game state - globals
CURRENT_PLAYER = 0
PLAYER_SCORES = [0,0]
HIGH_SCORE = 0


pygame.init()


def init_screen():
    global SCREEN  # needed to set/modify
    global CLOCK
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    CLOCK = pygame.time.Clock()


def load_data():
    global LEVELS
    global SCORE_SURFACES
    LEVELS = load_levels()
    score_tiles = load_score_tiles()
    SCORE_SURFACES = load_score_surfaces(score_tiles)


def load_level_background():
    global CURRENT_BACKGROUND_SURFACE
    global BACKGROUNDS
    level_tile_list = LEVELS.tile_dict[CURRENT_LEVEL]
    background = Background(level_tile_list, LEVELS.palettes[CURRENT_LEVEL])
    BACKGROUNDS[CURRENT_LEVEL] = background
    background.draw_full_surface()
    CURRENT_BACKGROUND_SURFACE = background.surface


def load_player_surfaces():
    global CURRENT_PLAYER_SURFACES
    CURRENT_PLAYER_SURFACES = [player_to_surface(p, PLAYER_SIZE) for p in load_players()]


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
        PLAYER_SCORES[CURRENT_PLAYER] += points
        tile.clear_wall()
        # now reload the background there
        BACKGROUNDS[CURRENT_LEVEL].draw_tile_on_surface(
            CURRENT_PLAYER_TILE_POSITION[0],
            CURRENT_PLAYER_TILE_POSITION[1]
            )


def draw_score():
    y = SCORE_DRAW_POSITION[CURRENT_PLAYER][1] * 8
    x_base = SCORE_DRAW_POSITION[CURRENT_PLAYER][0] * 8

    # The score is always a multiple of 10, so we actually don't store the
    # single digits and always draw a trailing 0. So a score shown as
    # 1460 is internally 146. Deflation!

    # Draw that trailing zero
    SCREEN.blit(SCORE_SURFACES[0], (x_base + 48, y))

    # see, look. we didn't even get the score yet
    score = PLAYER_SCORES[CURRENT_PLAYER]

    # A zero score should be drawn as 00. The second 0 is already drawn,
    # so just draw the first and be done. Probably not how the cabinet does it
    # but we can do it this way.
    if score == 0:
        # if zero, should draw 00 and be done
        SCREEN.blit(SCORE_SURFACES[0], (x_base + 40, y))
        return
    else:
        # make room for 5 other digits
        offset = 5
        while score > 0:
            # divide and modulo the score by 10 repeatedly to get each digit
            digit = score % 10
            score = int(score / 10)
            # Since the digit is an int, we can get the surface_digit by indexing into the list
            surface_digit = SCORE_SURFACES[digit]
            # Where to draw it? draw it at our offset position times the width
            x = x_base + (offset * 8)
            SCREEN.blit(surface_digit, (x, y))
            # now move the position to the left
            offset -= 1


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
    FRAME = PLAYER_ANIMATION_FRAMES[CURRENT_PLAYER_ANIMATION_FRAME_INDEX]
    SCREEN.blit(CURRENT_PLAYER_SURFACES[FRAME], position)


def tick():
    global TICK_COUNTER
    TICK_COUNTER += 1
    CLOCK.tick(CLOCK_RATE)


def animate_player_changes():
    global CURRENT_PLAYER_ANIMATION_FRAME_INDEX
    if TICK_COUNTER % 2 == 0:
        CURRENT_PLAYER_ANIMATION_FRAME_INDEX += 1
        CURRENT_PLAYER_ANIMATION_FRAME_INDEX %= len(PLAYER_ANIMATION_FRAMES)


def animate_palette_changes():
    if TICK_COUNTER % 10 == 0:
        # Update the palette on the background
        BACKGROUNDS[CURRENT_LEVEL].cycle_pellet_pallette()


init_screen()
load_data()
# load the background for the current level
load_level_background()
load_player_surfaces()

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
    animate_palette_changes()
    animate_player_changes()
    draw_game_board()
    draw_score()
    draw_player()

    # where is she?
    # BACKGROUNDS[CURRENT_LEVEL].tile_at(*CURRENT_PLAYER_POSITION).draw()

    # This draws - flip the buffer
    pygame.display.flip()
    tick()
