import pygame
from src.game import Game
from settings import FPS


def main():
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()


if __name__ == '__main__':
    main()
