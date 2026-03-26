import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, GREEN

class UI:
    def __init__(self):
        self.font = pygame.font.SysFont('Arial', 24)

    def render_menu(self, surface):
        text = self.font.render('TREASURE HUNT - Press ENTER to Start', True, WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        surface.blit(text, rect)

    def render_hud(self, surface, player):
        # Draw health
        health_text = self.font.render(f'Health: {player.health}', True, RED)
        surface.blit(health_text, (10, 10))
        # Draw hint level
        hint_text = self.font.render(f'Hint Level: {player.current_hint_level+1}', True, GREEN)
        surface.blit(hint_text, (10, 40))
