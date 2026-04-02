"""Bot AI logic for PvE and EvE game modes."""

import random
import pygame
from src.settings import GRID_COLS, GRID_ROWS, TILE_SIZE, RED
from src.game_mode import Difficulty


class BotAI:
    """AI controller for bot players with difficulty levels."""
    
    def __init__(self, bot_id, col, row, difficulty=Difficulty.NORMAL):
        self.bot_id = bot_id
        self.col = col
        self.row = row
        self.health = 2
        self.current_hint_level = -1
        self.color = (100, 149, 237)  # Cornflower blue
        self.difficulty = difficulty
        
        # Behavior parameters based on difficulty
        self.move_cooldown = 0.0
        self.dig_cooldown = 0.0
        self.dig_stun = 0.0
        
        # Difficulty-based parameters
        if difficulty == Difficulty.EASY:
            self.move_speed = 1.0  # Seconds between moves
            self.dig_probability = 0.2  # 20% chance to dig
            self.accuracy = 0.4  # 40% chance of intelligent dig
        elif difficulty == Difficulty.HARD:
            self.move_speed = 0.3
            self.dig_probability = 0.5
            self.accuracy = 0.9
        else:  # NORMAL
            self.move_speed = 0.6
            self.dig_probability = 0.35
            self.accuracy = 0.65
        
        # Memory of found hints
        self.hint_memory = set()
        self.bomb_memory = set()
        self.searched_tiles = set()

    def update(self, dt, game_map):
        """Update bot AI logic each frame."""
        self.move_cooldown = max(0, self.move_cooldown - dt)
        self.dig_cooldown = max(0, self.dig_cooldown - dt)
        self.dig_stun = max(0, self.dig_stun - dt)
        
        # Can't move while stunned
        if self.dig_stun > 0:
            return
        
        # Movement logic
        if self.move_cooldown <= 0:
            self._make_move(game_map)
            self.move_cooldown = self.move_speed
        
        # Digging logic
        if self.dig_cooldown <= 0 and random.random() < self.dig_probability:
            self._try_dig(game_map)

    def _make_move(self, game_map):
        """Decide where to move based on AI difficulty."""
        if self.difficulty == Difficulty.EASY:
            # Random movement
            direction = random.choice(['up', 'down', 'left', 'right', 'stay'])
        else:
            # Intelligent movement towards unexplored areas or hints
            direction = self._calculate_intelligent_move(game_map)
        
        self._move_in_direction(direction)

    def _calculate_intelligent_move(self, game_map):
        """Calculate movement based on logic and memory."""
        # Prefer moving towards unexplored tiles
        unexplored = []
        
        # Check adjacent tiles
        for direction, (dx, dy) in [('up', (0, -1)), ('down', (0, 1)), 
                                     ('left', (-1, 0)), ('right', (1, 0))]:
            nx, ny = self.col + dx, self.row + dy
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                tile = game_map.get_tile(nx, ny)
                if tile and not tile.revealed and (nx, ny) not in self.bomb_memory:
                    unexplored.append(direction)
        
        if unexplored:
            return random.choice(unexplored)
        
        # Otherwise random walk
        return random.choice(['up', 'down', 'left', 'right', 'stay'])

    def _move_in_direction(self, direction):
        """Move in specified direction."""
        if direction == 'up' and self.row > 0:
            self.row -= 1
        elif direction == 'down' and self.row < GRID_ROWS - 1:
            self.row += 1
        elif direction == 'left' and self.col > 0:
            self.col -= 1
        elif direction == 'right' and self.col < GRID_COLS - 1:
            self.col += 1

    def _try_dig(self, game_map):
        """Attempt to dig at current position."""
        tile = game_map.get_tile(self.col, self.row)
        if not tile or tile.revealed:
            return
        
        # Intelligent digging based on difficulty
        if self.difficulty == Difficulty.EASY:
            # Random digging
            should_dig = random.random() < self.dig_probability
        elif self.difficulty == Difficulty.HARD:
            # Dig if likely to be a hint (based on unexplored patterns)
            should_dig = (self.col, self.row) not in self.searched_tiles
        else:
            # Normal: dig if seems promising
            should_dig = random.random() < self.dig_probability
        
        if not should_dig:
            return
        
        result = game_map.try_dig(self)
        self.searched_tiles.add((self.col, self.row))
        
        # Update memory
        if result == 'hint_correct':
            self.hint_memory.add((self.col, self.row))
            self.dig_cooldown = 0.3
        elif result == 'bomb':
            self.bomb_memory.add((self.col, self.row))
            self.dig_stun = 1.5
            self.dig_cooldown = 1.5
        elif result == 'empty':
            self.dig_stun = 0.5
            self.dig_cooldown = 2.0
        elif result == 'treasure':
            self.dig_cooldown = 0.0
            # Treasure found!

    def render(self, surface):
        """Render bot on the surface."""
        rect = pygame.Rect(self.col * TILE_SIZE, self.row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, RED, rect, 2)
