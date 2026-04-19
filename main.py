"""Entry point for Treasure Hunt game."""

import pygame

from src.game import Game


def main():
    """Initialize pygame and run the game."""
    pygame.init()
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        # Allow Ctrl+C in the terminal to close the game without a traceback.
        return 130
    finally:
        pygame.quit()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
