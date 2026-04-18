import pygame
from src.settings import GRID_COLS, GRID_ROWS, GREEN, PLAYER_DIG_TIMINGS, RED, STARTING_HEALTH, TILE_SIZE
from src.skills import apply_blind, apply_freeze, create_skill_state, tick_actor_effects, use_actor_skill


class Player:
    """Player class for movement, digging, and health management."""

    MAX_HEALTH = STARTING_HEALTH
    DIG_AUDIO_EVENTS = {
        'hint_correct': 'key',
        'treasure': 'treasure',
        'bomb': 'bomb',
        'locked': 'locked',
        'empty': 'dig',
    }
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
            'skill': pygame.K_q,
            'skill_freeze': pygame.K_q,
            'skill_blind': pygame.K_e,
            'skill_extra_hint': pygame.K_f,
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
            'skill': pygame.K_i,
            'skill_freeze': pygame.K_i,
            'skill_blind': pygame.K_o,
            'skill_extra_hint': pygame.K_p,
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
        self.control_hint = control_hint or ('WASD / SPACE / QEF' if player_id == 1 else 'ARROWS / ENTER / IOP')
        self.dig_cooldown = 0.0  # Seconds until player can dig again
        self.stun_time = 0.0  # Stunned by bomb
        self.move_repeat_timer = 0.0
        self.found_treasure = False
        self.skills = create_skill_state()
        self.pending_audio_events = []
        self.is_frozen = False
        self.freeze_time = 0.0
        self.freeze_end_time = 0.0
        self.is_blinded = False
        self.blind_time = 0.0
        self.last_skill_result = None
        self.skill_feedback = None

    def update(self, dt, game_map):
        """Update player cooldowns and temporary status effects."""
        self.dig_cooldown = max(0, self.dig_cooldown - dt)
        self.stun_time = max(0, self.stun_time - dt)
        self.move_repeat_timer = max(0, self.move_repeat_timer - dt)
        tick_actor_effects(self, dt)

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
        if self.dig_cooldown > 0 or self.stun_time > 0 or self.is_frozen:
            return None

        result = game_map.try_dig(self)
        self._queue_audio_event(self.DIG_AUDIO_EVENTS.get(result))

        timing = PLAYER_DIG_TIMINGS.get(result)
        if timing:
            self.stun_time = timing['stun']
            self.dig_cooldown = timing['cooldown']

        return result

    def use_skill(self, skill_name, own_map=None, target=None, target_map=None):
        """Use a skill if available."""
        success = use_actor_skill(self, skill_name, own_map=own_map, target=target, target_map=target_map)
        if success:
            self._queue_audio_event(skill_name)
        return success

    def freeze(self, duration):
        """Apply freeze effect to player."""
        apply_freeze(self, duration)

    def blind(self, duration):
        """Apply blind effect to player."""
        apply_blind(self, duration)

    def apply_damage(self):
        """Apply damage (from bomb or other source)."""
        self.health -= 1
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        """Check if player is still alive."""
        return self.health > 0

    def consume_audio_events(self):
        """Return and clear any queued audio events."""
        events = list(self.pending_audio_events)
        self.pending_audio_events.clear()
        return events

    def _queue_audio_event(self, event_name):
        """Store one short audio cue for the game loop to play."""
        if event_name:
            self.pending_audio_events.append(event_name)

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
        self._render_skill_effects(surface, rect)
        
        # Draw stun indicator if stunned
        if self.stun_time > 0:
            pygame.draw.circle(surface, (255, 0, 0), rect.center, 5)

        self._render_skill_feedback(surface, rect)

    def _render_skill_effects(self, surface, rect):
        """Render active freeze/blind effects on top of the player."""
        if self.is_frozen:
            ice_overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            ice_overlay.fill((80, 190, 255, 120))
            surface.blit(ice_overlay, rect.topleft)
            pygame.draw.rect(surface, (180, 235, 255), rect, 3)
            pygame.draw.line(surface, (220, 250, 255), rect.midtop, rect.midbottom, 2)
            pygame.draw.line(surface, (220, 250, 255), rect.midleft, rect.midright, 2)

        if self.is_blinded:
            blind_overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            blind_overlay.fill((30, 20, 55, 135))
            surface.blit(blind_overlay, rect.topleft)
            pygame.draw.circle(surface, (170, 110, 255), rect.center, 10, 2)
            pygame.draw.line(surface, (170, 110, 255), rect.topleft, rect.bottomright, 2)

    def _render_skill_feedback(self, surface, rect):
        """Render short skill text above the actor."""
        feedback = self.skill_feedback
        if not feedback:
            return

        remaining = feedback.get('time', 0.0)
        duration = max(0.01, feedback.get('duration', 1.0))
        alpha = max(0, min(255, int(255 * remaining / duration)))
        if alpha <= 0:
            return

        font = pygame.font.SysFont('Arial', 14, bold=True)
        text = font.render(feedback.get('message', ''), True, (255, 245, 170))
        text.set_alpha(alpha)
        text_rect = text.get_rect(center=(rect.centerx, rect.top - 8))
        surface.blit(text, text_rect)
