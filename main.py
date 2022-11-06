from screen import Screen

import pygame

import sys

if __name__ == '__main__':
    sys.path.insert(0, 'BotAlgorithms/')
    pygame.init()

    screen = Screen()

    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        screen.run()

        screen.clock.tick(screen.FPS)
