"""Entry point for Treasure Hunt game."""

import pygame
from src.game import Game
from src.settings import FPS


def main():
    """Initialize pygame and run the game."""
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()


if __name__ == '__main__':
    main()
