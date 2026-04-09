"""Bot AI logic for PvE and EvE game modes."""

import heapq
import random
import pygame
from src.settings import GRID_COLS, GRID_ROWS, TILE_SIZE, RED
from src.game_mode import Difficulty


class BotAI:
    """AI controller for bot players with difficulty levels."""
    
    def __init__(self, bot_id, col, row, difficulty=Difficulty.NORMAL):
        self.bot_id = bot_id
        self.player_id = bot_id
        self.col = col
        self.row = row
        self.health = 2
        self.current_hint_level = -1
        self.color = (100, 149, 237)  # Cornflower blue
        self.display_name = f"AI {bot_id}"
        self.control_hint = "AUTO"
        self.difficulty = difficulty
        self.found_treasure = False
        
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
        self.current_target = None

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
        target = self._get_current_target(game_map)
        on_target = target == (self.col, self.row)
        if self.dig_cooldown <= 0 and (on_target or random.random() < self.dig_probability):
            self._try_dig(game_map)

    def _make_move(self, game_map):
        """Decide where to move based on AI difficulty."""
        if self.difficulty == Difficulty.EASY:
            direction = self._pick_search_move(game_map, search_weight=0.65)
        else:
            search_weight = 0.85 if self.difficulty == Difficulty.NORMAL else 1.0
            direction = self._pick_search_move(game_map, search_weight=search_weight)
        
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

        target = self._get_current_target(game_map)
        on_target = target == (self.col, self.row)
        
        # Intelligent digging based on difficulty
        if on_target:
            should_dig = True
        elif self.difficulty == Difficulty.EASY:
            should_dig = random.random() < (self.dig_probability * 0.35)
        elif self.difficulty == Difficulty.HARD:
            should_dig = (self.col, self.row) not in self.searched_tiles and random.random() < self.accuracy
        else:
            should_dig = random.random() < (self.dig_probability * 0.5)
        
        if not should_dig:
            return
        
        result = game_map.try_dig(self)
        if result != 'locked':
            self.searched_tiles.add((self.col, self.row))
        
        # Update memory
        if result == 'hint_correct':
            self.hint_memory.add((self.col, self.row))
            self.dig_cooldown = 0.3
        elif result == 'bomb':
            self.bomb_memory.add((self.col, self.row))
            self.dig_stun = 1.5
            self.dig_cooldown = 1.5
        elif result in ('empty', 'locked'):
            self.dig_stun = 0.5
            self.dig_cooldown = 2.0
        elif result in ('already_dug', 'unavailable', 'blocked'):
            self.dig_cooldown = 0.15
        elif result == 'treasure':
            self.dig_cooldown = 0.0
            # Treasure found!

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
