import pygame
import sys
import levels

SCREEN = None
CLOCK = None

SCREEN_SIZE = (224, 288)
COLOR_BLACK = (0,0,0)
CLOCK_RATE = 60


CURRENT_LEVEL = 1


pygame.init()

def init_screen():
    global SCREEN # needed to set/modify
    global CLOCK
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    CLOCK = pygame.time.Clock()

def read_inputs():
    pass

def draw_game_board():
    # pixel array?
    pass

def draw_player():
    # sprite
    pass

init_screen()

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
    

