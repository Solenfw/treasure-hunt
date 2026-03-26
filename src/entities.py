import pygame
from settings import TILE_SIZE, GREEN, RED

class Player:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.health = 2
        self.current_hint_level = -1
        self.color = GREEN
        self.digging = False
        self.dig_timer = 0

    def update(self, dt, game_map):
        keys = pygame.key.get_pressed()
        if not self.digging:
            if keys[pygame.K_w] and self.row > 0:
                self.row -= 1
            elif keys[pygame.K_s] and self.row < 19:
                self.row += 1
            elif keys[pygame.K_a] and self.col > 0:
                self.col -= 1
            elif keys[pygame.K_d] and self.col < 19:
                self.col += 1

    def render(self, surface):
        rect = pygame.Rect(self.col * TILE_SIZE, self.row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, RED, rect, 2)
