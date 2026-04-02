"""Main game loop and state management."""

import pygame
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from src.map import Map
from src.player import Player
from src.bot_ai import BotAI
from src.ui_manager import UIManager
from src.game_state import GameState
from src.game_mode import GameMode, Difficulty


class Game:
    """Main game class handling the game loop and state."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('🏴‍☠️ Treasure Hunt - Truy Tìm Kho Báu')
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GameState()
        
        # Game components
        self.map1 = None
        self.map2 = None
        self.player1 = None
        self.player2 = None
        self.ui = UIManager()
        
        # Game logic
        self.selected_mode = 0
        self.ai_difficulty = Difficulty.NORMAL

    def handle_events(self):
        """Process game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Menu
                if self.game_state.is_menu():
                    if event.key == pygame.K_RETURN:
                        self.game_state.set_state(GameState.MODE_SELECT)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                # Mode selection
                elif self.game_state.is_mode_select():
                    if event.key == pygame.K_1:
                        self.game_state.set_game_mode(GameMode.PVP)
                        self._start_game()
                    elif event.key == pygame.K_2:
                        self.game_state.set_game_mode(GameMode.PVE_EASY)
                        self._start_game()
                    elif event.key == pygame.K_3:
                        self.game_state.set_game_mode(GameMode.PVE_NORMAL)
                        self._start_game()
                    elif event.key == pygame.K_4:
                        self.game_state.set_game_mode(GameMode.PVE_HARD)
                        self._start_game()
                    elif event.key == pygame.K_5:
                        self.game_state.set_game_mode(GameMode.EVE)
                        self._start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state.set_state(GameState.MENU)
                
                # Gameplay
                elif self.game_state.is_playing():
                    if event.key == pygame.K_SPACE:
                        self.player1.dig(self.map1)
                    elif event.key == pygame.K_e:
                        self.player1.use_skill('freeze')  # Example
                    elif event.key == pygame.K_p:
                        self.game_state.set_state(GameState.PAUSED)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                # Paused
                elif self.game_state.is_paused():
                    if event.key == pygame.K_p:
                        self.game_state.set_state(GameState.PLAYING)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                # Game Over
                elif self.game_state.is_game_over():
                    if event.key == pygame.K_RETURN:
                        self.game_state.set_state(GameState.MENU)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

    def _start_game(self):
        """Initialize a new game."""
        game_mode = self.game_state.game_mode
        
        # Create maps and players
        self.map1 = Map()
        self.player1 = Player(0, 0, player_id=1)
        
        if game_mode == GameMode.PVP:
            self.map2 = Map()
            self.player2 = Player(0, 0, player_id=2)
        elif game_mode.startswith('pve'):
            # Determine difficulty
            if game_mode == GameMode.PVE_EASY:
                difficulty = Difficulty.EASY
            elif game_mode == GameMode.PVE_HARD:
                difficulty = Difficulty.HARD
            else:
                difficulty = Difficulty.NORMAL
            
            self.map2 = Map()
            self.player2 = BotAI(2, 0, 0, difficulty=difficulty)
        else:  # EVE
            self.map2 = Map()
            self.player2 = BotAI(2, 0, 0, difficulty=Difficulty.NORMAL)
        
        self.game_state.set_state(GameState.PLAYING)
        self.game_state.reset_round()

    def update(self, dt):
        """Update game logic."""
        if self.game_state.is_playing():
            # Update timer
            time_expired = self.game_state.update_timer(dt)
            if time_expired:
                self._end_game("Time's Up!", "Draw - No winner")
                return
            
            # Update players
            self.player1.update(dt, self.map1)
            if isinstance(self.player2, BotAI):
                self.player2.update(dt, self.map2)
            else:
                self.player2.update(dt, self.map2)
            
            # Check win conditions
            if self.player1.current_hint_level >= 4:
                self._end_game(f"Player 1 Wins!", "Found the treasure!")
            elif self.player2.current_hint_level >= 4:
                player2_name = "AI" if isinstance(self.player2, BotAI) else "Player 2"
                self._end_game(f"{player2_name} Wins!", "Found the treasure!")
            elif self.player1.health <= 0:
                player2_name = "AI" if isinstance(self.player2, BotAI) else "Player 2"
                self._end_game(f"{player2_name} Wins!", "Player 1 eliminated!")
            elif self.player2.health <= 0:
                player2_name = "AI" if isinstance(self.player2, BotAI) else "Player 2"
                self._end_game("Player 1 Wins!", f"{player2_name} eliminated!")

    def _end_game(self, winner, reason):
        """End the current game."""
        self.game_state.winner = winner
        self.game_state.message = reason
        self.game_state.set_state(GameState.GAME_OVER)

    def render(self):
        """Render the current frame."""
        self.screen.fill(BLACK)
        
        if self.game_state.is_menu():
            self.ui.render_main_menu(self.screen)
        
        elif self.game_state.is_mode_select():
            self.ui.render_mode_select(self.screen, self.selected_mode)
        
        elif self.game_state.is_playing() or self.game_state.is_paused():
            # Split screen for multiplayer
            game_mode = self.game_state.game_mode
            
            if game_mode == GameMode.PVP:
                # Side-by-side rendering
                left_rect = pygame.Rect(0, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT)
                right_rect = pygame.Rect(SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT)
                
                # Render maps
                self.map1.render(self.screen)
                self.player1.render(self.screen)
                
                # Render second player's map (offset)
                for row in self.map2.tiles:
                    for tile in row:
                        tile.rect.x += SCREEN_WIDTH // 2
                self.map2.render(self.screen)
                
                # Restore positions
                for row in self.map2.tiles:
                    for tile in row:
                        tile.rect.x -= SCREEN_WIDTH // 2
                
                self.player2.render(self.screen)
            else:
                # Single player view
                self.map1.render(self.screen)
                self.player1.render(self.screen)
            
            # Render HUD
            self.ui.render_game_hud(self.screen, self.player1, self.player2 if game_mode == GameMode.PVP else None, 
                                   self.game_state.round_time_remaining)
            
            # Render clue box
            clue_text = self.map1.get_clue_text(self.player1.current_hint_level)
            self.ui.render_clue_box(self.screen, clue_text)
            
            # Render pause overlay if paused
            if self.game_state.is_paused():
                self.ui.render_pause_overlay(self.screen)
        
        elif self.game_state.is_game_over():
            self.ui.render_game_over(self.screen, self.game_state.winner, self.game_state.message)
        
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            self.handle_events()
            self.update(dt)
            self.render()


    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.render()
