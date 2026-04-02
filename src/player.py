import pygame
from src.settings import TILE_SIZE, GREEN, RED, GRID_COLS, GRID_ROWS


class Player:
    """Player class for movement, digging, and health management."""
    
    MAX_HEALTH = 2  # Two hearts
    
    def __init__(self, col, row, player_id=1):
        self.player_id = player_id
        self.col = col
        self.row = row
        self.health = self.MAX_HEALTH
        self.current_hint_level = -1  # -1 means no hints found yet
        self.color = GREEN if player_id == 1 else (100, 149, 237)  # Blue for player 2
        self.dig_cooldown = 0.0  # Seconds until player can dig again
        self.stun_time = 0.0  # Stunned by bomb
        self.skills = {
            'freeze': {'cooldown': 0.0, 'max_cooldown': 20.0, 'duration': 3.0},
            'blind': {'cooldown': 0.0, 'max_cooldown': 20.0, 'duration': 5.0},
            'extra_hint': {'cooldown': 0.0, 'max_cooldown': 30.0}
        }
        self.is_frozen = False
        self.freeze_end_time = 0.0

    def update(self, dt, game_map):
        """Update player position based on keyboard input and cooldowns."""
        # Update cooldowns
        self.dig_cooldown = max(0, self.dig_cooldown - dt)
        self.stun_time = max(0, self.stun_time - dt)
        
        # Update freeze state
        if self.is_frozen:
            if dt >= self.freeze_end_time:
                self.is_frozen = False
            else:
                self.freeze_end_time -= dt
                return  # Can't move while frozen
        
        # Update skill cooldowns
        for skill in self.skills.values():
            skill['cooldown'] = max(0, skill['cooldown'] - dt)
        
        # Handle movement (blocked if stunned or digging)
        if self.stun_time <= 0 and self.dig_cooldown <= 0:
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_w] and self.row > 0:
                self.row -= 1
            elif keys[pygame.K_s] and self.row < GRID_ROWS - 1:
                self.row += 1
            elif keys[pygame.K_a] and self.col > 0:
                self.col -= 1
            elif keys[pygame.K_d] and self.col < GRID_COLS - 1:
                self.col += 1

    def dig(self, game_map):
        """Attempt to dig at current position."""
        if self.dig_cooldown > 0 or self.stun_time > 0:
            return None
        
        result = game_map.try_dig(self)
        
        # Apply stun/cooldown based on result
        if result == 'bomb':
            self.stun_time = 1.5  # Stunned for 1.5 seconds
            self.dig_cooldown = 1.5
        elif result == 'empty':
            self.dig_cooldown = 2.0
            self.stun_time = 0.5
        elif result == 'hint_correct':
            self.dig_cooldown = 0.5  # Quick recovery
        
        return result

    def use_skill(self, skill_name):
        """Use a skill if available."""
        if skill_name not in self.skills:
            return False
        
        skill = self.skills[skill_name]
        if skill['cooldown'] > 0:
            return False
        
        skill['cooldown'] = skill['max_cooldown']
        return True

    def freeze(self, duration):
        """Apply freeze effect to player."""
        self.is_frozen = True
        self.freeze_end_time = duration

    def apply_damage(self):
        """Apply damage (from bomb or other source)."""
        self.health -= 1
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        """Check if player is still alive."""
        return self.health > 0

    def render(self, surface):
        """Render player as a colored square on the surface."""
        rect = pygame.Rect(self.col * TILE_SIZE, self.row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, RED, rect, 2)
        
        # Draw stun indicator if stunned
        if self.stun_time > 0:
            pygame.draw.circle(surface, (255, 0, 0), rect.center, 5)
