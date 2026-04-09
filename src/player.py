import pygame
from src.settings import TILE_SIZE, GREEN, RED, GRID_COLS, GRID_ROWS


class Player:
    """Player class for movement, digging, and health management."""
    
    MAX_HEALTH = 2  # Two hearts
    MOVE_REPEAT_DELAY = 0.14
    DEFAULT_CONTROLS = {
        1: {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'up_scan': 26,
            'down_scan': 22,
            'left_scan': 4,
            'right_scan': 7,
            'dig': (pygame.K_SPACE, pygame.K_LCTRL),
            'skill': pygame.K_e,
        },
        2: {
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'up_scan': 82,
            'down_scan': 81,
            'left_scan': 80,
            'right_scan': 79,
            'dig': (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_RCTRL),
            'skill': (pygame.K_RSHIFT, pygame.K_SLASH),
        },
    }
    
    def __init__(self, col, row, player_id=1, controls=None, display_name=None, control_hint=None):
        self.player_id = player_id
        self.col = col
        self.row = row
        self.health = self.MAX_HEALTH
        self.current_hint_level = -1  # -1 means no hints found yet
        self.color = GREEN if player_id == 1 else (100, 149, 237)  # Blue for player 2
        self.display_name = display_name or f"Player {player_id}"
        self.controls = dict(controls or self.DEFAULT_CONTROLS.get(player_id, self.DEFAULT_CONTROLS[1]))
        self.control_hint = control_hint or ('WASD / SPACE' if player_id == 1 else 'ARROWS / ENTER')
        self.dig_cooldown = 0.0  # Seconds until player can dig again
        self.step_cooldown = 0.0
        self.stun_time = 0.0  # Stunned by bomb
        self.found_treasure = False
        self.skills = {
            'freeze': {'cooldown': 0.0, 'max_cooldown': 20.0, 'duration': 3.0},
            'blind': {'cooldown': 0.0, 'max_cooldown': 20.0, 'duration': 5.0},
            'extra_hint': {'cooldown': 0.0, 'max_cooldown': 30.0}
        }
        self.is_frozen = False
        self.freeze_end_time = 0.0

    def update(self, dt, game_map, pressed_keys=None, pressed_scancodes=None):
        """Update player cooldowns and temporary status effects."""
        # Update cooldowns
        self.dig_cooldown = max(0, self.dig_cooldown - dt)
        self.step_cooldown = max(0, self.step_cooldown - dt)
        self.stun_time = max(0, self.stun_time - dt)
        
        # Update freeze state
        if self.is_frozen:
            if self.freeze_end_time <= dt:
                self.is_frozen = False
                self.freeze_end_time = 0.0
            else:
                self.freeze_end_time -= dt
        
        # Update skill cooldowns
        for skill in self.skills.values():
            skill['cooldown'] = max(0, skill['cooldown'] - dt)

        self._handle_keyboard_movement(game_map, pressed_keys, pressed_scancodes)

    def _binding_pressed(self, pressed_keys, binding):
        """Return True when any key from the binding is pressed."""
        if isinstance(binding, (tuple, list, set)):
            return any(key in pressed_keys for key in binding)
        return binding in pressed_keys

    def _scan_pressed(self, pressed_scancodes, control_name):
        """Return True when the physical key for a direction is pressed."""
        if pressed_scancodes is None:
            return False

        scan_code = self.controls.get(f'{control_name}_scan')
        return scan_code in pressed_scancodes if scan_code is not None else False

    def _handle_keyboard_movement(self, game_map, pressed_keys, pressed_scancodes):
        """Move continuously while a direction is held, but at grid intervals."""
        if pressed_keys is None:
            return

        if not self.can_move() or self.step_cooldown > 0:
            return

        moved = False

        if self._binding_pressed(pressed_keys, self.controls['up']) or self._scan_pressed(pressed_scancodes, 'up'):
            moved = self.move('up', game_map)
        elif self._binding_pressed(pressed_keys, self.controls['down']) or self._scan_pressed(pressed_scancodes, 'down'):
            moved = self.move('down', game_map)
        elif self._binding_pressed(pressed_keys, self.controls['left']) or self._scan_pressed(pressed_scancodes, 'left'):
            moved = self.move('left', game_map)
        elif self._binding_pressed(pressed_keys, self.controls['right']) or self._scan_pressed(pressed_scancodes, 'right'):
            moved = self.move('right', game_map)

        if moved:
            self.step_cooldown = self.MOVE_REPEAT_DELAY

    def can_move(self):
        """Check whether the player can move this frame."""
        return self.stun_time <= 0 and self.dig_cooldown <= 0 and not self.is_frozen

    def move(self, direction, game_map=None):
        """Move one tile in the given direction when movement is allowed."""
        if not self.can_move():
            return False

        next_col = self.col
        next_row = self.row

        if direction == 'up' and self.row > 0:
            next_row -= 1
        elif direction == 'down' and self.row < GRID_ROWS - 1:
            next_row += 1
        elif direction == 'left' and self.col > 0:
            next_col -= 1
        elif direction == 'right' and self.col < GRID_COLS - 1:
            next_col += 1
        else:
            return False

        if game_map is not None and not game_map.is_walkable(next_col, next_row):
            return False

        self.col = next_col
        self.row = next_row

        return True

    def dig(self, game_map):
        """Attempt to dig at current position."""
        if self.dig_cooldown > 0 or self.stun_time > 0:
            return None
        
        result = game_map.try_dig(self)
        
        # Apply stun/cooldown based on result
        if result == 'bomb':
            self.stun_time = 1.5  # Stunned for 1.5 seconds
            self.dig_cooldown = 1.5
        elif result in ('empty', 'locked'):
            self.dig_cooldown = 2.0
            self.stun_time = 0.5
        elif result in ('already_dug', 'unavailable', 'blocked'):
            self.dig_cooldown = 0.15
        elif result == 'hint_correct':
            self.dig_cooldown = 0.5  # Quick recovery
        elif result == 'treasure':
            self.dig_cooldown = 0.0
        
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

    def render(self, surface, x_offset=0, y_offset=0):
        """Render player as a colored square on the surface."""
        rect = pygame.Rect(
            x_offset + self.col * TILE_SIZE,
            y_offset + self.row * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
        )
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, RED, rect, 2)
        
        # Draw stun indicator if stunned
        if self.stun_time > 0:
            pygame.draw.circle(surface, (255, 0, 0), rect.center, 5)
