"""Game state management for menu, playing, paused, and game over states."""

from src.game_mode import GameMode
from src.settings import ROUND_TIME_SECONDS


class GameState:
    """Manages the current game state."""
    
    MENU = 'menu'
    MODE_SELECT = 'mode_select'
    DIFFICULTY_SELECT = 'difficulty_select'
    SETTINGS = 'settings'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'gameover'
    
    def __init__(self):
        self.current_state = self.MENU
        self.previous_state = None
        self.game_mode = GameMode.PVP
        self.round_time = ROUND_TIME_SECONDS
        self.round_time_remaining = self.round_time
        self.winner = None
        self.message = ""
    
    def set_state(self, state):
        """Set the current game state."""
        self.previous_state = self.current_state
        self.current_state = state
    
    def is_playing(self):
        """Check if game is currently in playing state."""
        return self.current_state == self.PLAYING
    
    def is_menu(self):
        """Check if game is currently in menu state."""
        return self.current_state == self.MENU
    
    def is_mode_select(self):
        """Check if in mode selection."""
        return self.current_state == self.MODE_SELECT
    
    def is_difficulty_select(self):
        """Check if in difficulty selection."""
        return self.current_state == self.DIFFICULTY_SELECT
    
    def is_paused(self):
        """Check if game is currently paused."""
        return self.current_state == self.PAUSED

    def is_settings(self):
        """Check if game is in settings state."""
        return self.current_state == self.SETTINGS
    
    def is_game_over(self):
        """Check if game is over."""
        return self.current_state == self.GAME_OVER
    
    def set_game_mode(self, mode):
        """Set the game mode."""
        self.game_mode = mode
    
    def update_timer(self, dt):
        """Update round timer."""
        if self.is_playing():
            self.round_time_remaining = max(0, self.round_time_remaining - dt)
            return self.round_time_remaining <= 0
        return False
    
    def reset_round(self):
        """Reset for a new round."""
        self.round_time_remaining = self.round_time
        self.winner = None
        self.message = ""

