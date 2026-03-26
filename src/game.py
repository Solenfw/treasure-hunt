import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from src.map import Map
from src.entities import Player
from src.ui import UI


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Treasure Hunt - Prototype')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'menu'  # menu, playing, paused, gameover

        # For phase 1/2 prototype we only setup a single map and one player
        self.map = Map()
        self.player = Player(0, 0)
        self.ui = UI()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == 'menu' and event.key == pygame.K_RETURN:
                    self.state = 'playing'
                elif self.state == 'playing':
                    if event.key == pygame.K_SPACE:
                        self.map.try_dig(self.player)
                    elif event.key == pygame.K_p:
                        self.state = 'paused'
                elif self.state == 'paused' and event.key == pygame.K_p:
                    self.state = 'playing'

    def update(self, dt):
        if self.state == 'playing':
            self.player.update(dt, self.map)
            self.map.update(dt)

    def render(self):
        self.screen.fill(BLACK)
        if self.state == 'menu':
            self.ui.render_menu(self.screen)
        else:
            self.map.render(self.screen)
            self.player.render(self.screen)
            self.ui.render_hud(self.screen, self.player)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.render()
