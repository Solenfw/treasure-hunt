"""Bot AI logic for PvE and EvE game modes."""

import heapq
import random
import pygame
from src.settings import BOT_DIFFICULTY_BALANCE, BOT_DIG_TIMINGS, GRID_COLS, GRID_ROWS, RED, STARTING_HEALTH, TILE_SIZE
from src.game_mode import Difficulty
from src.skills import apply_blind, apply_freeze, create_skill_state, tick_actor_effects, use_actor_skill


class BotAI:
    """AI controller for bot players with difficulty levels."""

    DIG_AUDIO_EVENTS = {
        'hint_correct': 'key',
        'treasure': 'treasure',
        'bomb': 'bomb',
        'locked': 'locked',
        'empty': 'dig',
    }

    def __init__(self, bot_id, col, row, difficulty=Difficulty.NORMAL):
        self.bot_id = bot_id
        self.player_id = bot_id
        self.col = col
        self.row = row
        self.health = STARTING_HEALTH
        self.current_hint_level = -1
        self.color = (100, 149, 237)  # Cornflower blue
        self.display_name = f"AI {bot_id}"
        self.control_hint = "AUTO"
        self.difficulty = difficulty
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
        
        # Behavior parameters based on difficulty
        self.move_cooldown = 0.0
        self.dig_cooldown = 0.0
        self.dig_stun = 0.0
        
        difficulty_key = {
            Difficulty.EASY: 'easy',
            Difficulty.NORMAL: 'normal',
            Difficulty.HARD: 'hard',
        }[difficulty]
        config = BOT_DIFFICULTY_BALANCE[difficulty_key]
        self.move_speed = config['move_speed']
        self.dig_probability = config['dig_probability']
        self.search_weight = config['search_weight']
        self.wrong_dig_probability = config['wrong_dig_probability']
        self.skill_aggression = config['skill_aggression']
        self.skill_check_delay = config['skill_check_delay']
        
        # Memory of found hints
        self.hint_memory = set()
        self.bomb_memory = set()
        self.searched_tiles = set()
        self.current_target = None
        self.skill_decision_cooldown = random.uniform(self.skill_check_delay * 0.5, self.skill_check_delay)

    def update(self, dt, game_map, opponent=None, opponent_map=None):
        """Update bot AI logic each frame."""
        tick_actor_effects(self, dt)
        self.move_cooldown = max(0, self.move_cooldown - dt)
        self.dig_cooldown = max(0, self.dig_cooldown - dt)
        self.dig_stun = max(0, self.dig_stun - dt)
        
        # Can't act while stunned or frozen.
        if self.dig_stun > 0 or self.is_frozen:
            return

        self._maybe_use_skill(dt, game_map, opponent, opponent_map)
        
        # Movement logic
        if self.move_cooldown <= 0:
            self._make_move(game_map)
            self.move_cooldown = self.move_speed
        
        # Digging logic
        target = self._get_current_target(game_map)
        on_target = target == (self.col, self.row)
        if self.dig_cooldown <= 0 and (on_target or random.random() < self.dig_probability):
            self._try_dig(game_map)

    def _maybe_use_skill(self, dt, game_map, opponent=None, opponent_map=None):
        """Use skills occasionally without interrupting movement/pathfinding."""
        self.skill_decision_cooldown = max(0.0, self.skill_decision_cooldown - dt)
        if self.skill_decision_cooldown > 0.0 or self.is_blinded:
            return

        jitter = random.uniform(0.8, 1.25)
        self.skill_decision_cooldown = self.skill_check_delay * jitter

        if random.random() > self.skill_aggression:
            return

        opponent_progress = getattr(opponent, 'current_hint_level', -1) if opponent is not None else -1
        if opponent is not None and opponent_progress >= self.current_hint_level:
            if self.use_skill('freeze', own_map=game_map, target=opponent, target_map=opponent_map):
                return
            if self.use_skill('blind', own_map=game_map, target=opponent, target_map=opponent_map):
                return

        if random.random() < 0.6:
            self.use_skill('extra_hint', own_map=game_map, target=opponent, target_map=opponent_map)

    def _make_move(self, game_map):
        """Decide where to move based on AI difficulty."""
        if self.is_blinded:
            available_directions = self._available_directions(game_map)
            direction = random.choice(available_directions + ['stay', 'stay']) if available_directions else 'stay'
        else:
            direction = self._pick_search_move(game_map, search_weight=self.search_weight)
        
        self._move_in_direction(direction, game_map)

    def _pick_search_move(self, game_map, search_weight):
        """Prefer a search-driven step toward the next objective."""
        if random.random() <= search_weight:
            direction = self._calculate_intelligent_move(game_map)
            if direction is not None:
                return direction

        available_directions = self._available_directions(game_map)
        if not available_directions:
            return 'stay'
        return random.choice(available_directions + ['stay'])

    def _available_directions(self, game_map):
        """Return all directions that are not blocked by walls or edges."""
        directions = []
        for direction, (dx, dy) in [('up', (0, -1)), ('down', (0, 1)), ('left', (-1, 0)), ('right', (1, 0))]:
            nx = self.col + dx
            ny = self.row + dy
            if game_map.is_walkable(nx, ny):
                directions.append(direction)
        return directions

    def _calculate_intelligent_move(self, game_map):
        """Calculate movement using A* toward the next required target."""
        target = self._get_current_target(game_map)
        self.current_target = target
        if target is not None:
            direction = self._get_path_direction(game_map, target)
            if direction is not None:
                return direction

        unexplored = []
        for direction, (dx, dy) in [('up', (0, -1)), ('down', (0, 1)), ('left', (-1, 0)), ('right', (1, 0))]:
            nx, ny = self.col + dx, self.row + dy
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and game_map.is_walkable(nx, ny):
                tile = game_map.get_tile(nx, ny)
                if tile and not tile.revealed and (nx, ny) not in self.bomb_memory:
                    unexplored.append(direction)

        if unexplored:
            return random.choice(unexplored)

        return None

    def _get_current_target(self, game_map):
        """Return the next hint or treasure coordinate the bot should pursue."""
        next_level = self.current_hint_level + 1
        if next_level < game_map.HINT_CHAIN_LENGTH:
            return game_map.hint_positions.get(next_level)
        return game_map.treasure_pos

    def _heuristic(self, position, goal):
        """Manhattan distance for A* on the grid."""
        return abs(position[0] - goal[0]) + abs(position[1] - goal[1])

    def _reconstruct_path(self, came_from, current):
        """Build the path from start to the current node."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def _find_path(self, game_map, goal):
        """Find a path to the target using A* search."""
        start = (self.col, self.row)
        if goal is None or start == goal:
            return [start]
        if not game_map.is_walkable(*goal):
            return None

        frontier = [(self._heuristic(start, goal), 0, start)]
        came_from = {}
        cost_so_far = {start: 0}

        while frontier:
            _, current_cost, current = heapq.heappop(frontier)
            if current == goal:
                return self._reconstruct_path(came_from, current)

            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                next_pos = (current[0] + dx, current[1] + dy)
                if not game_map.is_walkable(*next_pos):
                    continue

                move_cost = 1
                if next_pos in self.bomb_memory:
                    move_cost += 4

                new_cost = current_cost + move_cost
                if next_pos in cost_so_far and new_cost >= cost_so_far[next_pos]:
                    continue

                cost_so_far[next_pos] = new_cost
                priority = new_cost + self._heuristic(next_pos, goal)
                came_from[next_pos] = current
                heapq.heappush(frontier, (priority, new_cost, next_pos))

        return None

    def _get_path_direction(self, game_map, target):
        """Convert the first A* step into a movement direction."""
        path = self._find_path(game_map, target)
        if not path or len(path) < 2:
            return None

        next_col, next_row = path[1]
        dx = next_col - self.col
        dy = next_row - self.row

        if dx == 1:
            return 'right'
        if dx == -1:
            return 'left'
        if dy == 1:
            return 'down'
        if dy == -1:
            return 'up'
        return None

    def _move_in_direction(self, direction, game_map):
        """Move in specified direction."""
        if direction == 'up' and self.row > 0 and game_map.is_walkable(self.col, self.row - 1):
            self.row -= 1
        elif direction == 'down' and self.row < GRID_ROWS - 1 and game_map.is_walkable(self.col, self.row + 1):
            self.row += 1
        elif direction == 'left' and self.col > 0 and game_map.is_walkable(self.col - 1, self.row):
            self.col -= 1
        elif direction == 'right' and self.col < GRID_COLS - 1 and game_map.is_walkable(self.col + 1, self.row):
            self.col += 1

    def _try_dig(self, game_map):
        """Attempt to dig at current position."""
        tile = game_map.get_tile(self.col, self.row)
        if not tile or tile.revealed or tile.type == 'wall':
            return

        target = None if self.is_blinded else self._get_current_target(game_map)
        on_target = target == (self.col, self.row)
        
        # Intelligent digging based on difficulty
        if on_target:
            should_dig = True
        else:
            should_dig = (
                (self.col, self.row) not in self.searched_tiles
                and random.random() < self.wrong_dig_probability
            )
        
        if not should_dig:
            return
        
        result = game_map.try_dig(self)
        self._queue_audio_event(self.DIG_AUDIO_EVENTS.get(result))
        if result != 'locked':
            self.searched_tiles.add((self.col, self.row))

        timing = BOT_DIG_TIMINGS.get(result)
        if timing:
            self.dig_stun = timing['stun']
            self.dig_cooldown = timing['cooldown']

        if result == 'hint_correct':
            self.hint_memory.add((self.col, self.row))
        elif result == 'bomb':
            self.bomb_memory.add((self.col, self.row))

    def use_skill(self, skill_name, own_map=None, target=None, target_map=None):
        """Use a skill if available."""
        success = use_actor_skill(self, skill_name, own_map=own_map, target=target, target_map=target_map)
        if success:
            self._queue_audio_event(skill_name)
        return success

    def freeze(self, duration):
        """Apply freeze effect to bot."""
        apply_freeze(self, duration)

    def blind(self, duration):
        """Apply blind effect to bot."""
        apply_blind(self, duration)

    def consume_audio_events(self):
        """Return and clear any queued audio events."""
        events = list(self.pending_audio_events)
        self.pending_audio_events.clear()
        return events

    def _queue_audio_event(self, event_name):
        """Store one short audio cue for the main game loop to play."""
        if event_name:
            self.pending_audio_events.append(event_name)

    def render(self, surface, x_offset=0, y_offset=0):
        """Render bot on the surface."""
        rect = pygame.Rect(
            x_offset + self.col * TILE_SIZE,
            y_offset + self.row * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
        )
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, RED, rect, 2)
        self._render_skill_effects(surface, rect)
        self._render_skill_feedback(surface, rect)

    def _render_skill_effects(self, surface, rect):
        """Render active freeze/blind effects on top of the bot."""
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
