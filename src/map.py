from collections import deque
import random
import pygame
from src.settings import GRID_COLS, GRID_ROWS, TILE_SIZE, BROWN, GREEN, GRAY, YELLOW, RED, WHITE


class Tile:
    """Represents a single tile on the game map."""

    HIDDEN = 'hidden'
    VISIBLE = 'visible'
    DUG = 'dug'

    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.type = 'dirt'  # dirt, bomb, hint, treasure
        self.state = self.HIDDEN
        self.hint_level = None  # 0-4 for hints, -1 for treasure, None for bombs/empty

    @property
    def revealed(self):
        """Compatibility helper for old call sites."""
        return self.state == self.DUG

    @revealed.setter
    def revealed(self, value):
        if value:
            self.state = self.DUG
        elif self.state == self.DUG:
            self.state = self.HIDDEN

    @property
    def visible(self):
        """Compatibility helper for old call sites."""
        return self.state == self.VISIBLE

    @visible.setter
    def visible(self, value):
        if value and self.state == self.HIDDEN:
            self.state = self.VISIBLE
        elif not value and self.state == self.VISIBLE:
            self.state = self.HIDDEN

    def mark_visible(self):
        """Expose a tile without digging it up."""
        if self.state == self.HIDDEN:
            self.state = self.VISIBLE

    def mark_dug(self):
        """Mark the tile as fully dug and revealed."""
        self.state = self.DUG


class Map:
    """Manages the game grid, tiles, and digging logic with enforced hint chain sequence."""

    HINT_CHAIN_LENGTH = 3  # Hints 0-2, then Treasure
    GENERATION_ATTEMPTS = 50
    MIN_CHAIN_DISTANCE = 6
    MIN_FIRST_HINT_SPAWN_DISTANCE = 4
    WALL_SEGMENT_COUNT = 12
    WALL_SEGMENT_MIN_LENGTH = 2
    WALL_SEGMENT_MAX_LENGTH = 5
    WALL_PLACEMENT_ATTEMPTS = 120
    STEP_DIRECTIONS = ((0, -1), (0, 1), (-1, 0), (1, 0))

    def __init__(self, layout=None, spawn_positions=None):
        self.cols = GRID_COLS
        self.rows = GRID_ROWS
        self.tiles = []
        self.treasure_pos = None
        self.hint_positions = {}  # {hint_level: (col, row)}
        self.bomb_positions = []
        self.wall_positions = []
        if layout is None:
            self.generate_map(spawn_positions=spawn_positions)
        else:
            self.load_layout(layout)

    def _reset_layout(self):
        """Reset the map so a fresh layout can be generated."""
        self.tiles = [[Tile(c, r) for r in range(self.rows)] for c in range(self.cols)]
        self.treasure_pos = None
        self.hint_positions = {}
        self.bomb_positions = []
        self.wall_positions = []

    def generate_map(self, spawn_positions=None):
        """Generate the map with enforced hint chain and bombs."""
        for _ in range(self.GENERATION_ATTEMPTS):
            self._reset_layout()
            if self.generate_hint_chain(spawn_positions=spawn_positions):
                if not self.place_walls(spawn_positions=spawn_positions):
                    continue
                self.place_bombs(spawn_positions=spawn_positions)
                return

        raise RuntimeError("Failed to generate a valid map layout.")

    def _manhattan_distance(self, position_a, position_b):
        """Return Manhattan distance between two grid positions."""
        return abs(position_a[0] - position_b[0]) + abs(position_a[1] - position_b[1])

    def _find_open_tile(self, origin_col, origin_row, reserved_positions=None, min_distance=0, extra_filters=None):
        """Find an unused tile that satisfies chain-distance constraints."""
        reserved_positions = reserved_positions or set()
        extra_filters = extra_filters or []

        candidates = []
        for col in range(self.cols):
            for row in range(self.rows):
                tile = self.get_tile(col, row)
                position = (col, row)
                if tile is None or tile.type != 'dirt' or position in reserved_positions:
                    continue

                distance = self._manhattan_distance((origin_col, origin_row), position)
                if distance < min_distance:
                    continue
                if any(not rule(position) for rule in extra_filters):
                    continue

                candidates.append((random.random(), col, row))

        if not candidates:
            return None

        _, col, row = min(candidates)
        return col, row

    def generate_hint_chain(self, spawn_positions=None):
        """Place treasure and create a linear hint chain with direction clues."""
        reserved_positions = set(spawn_positions or [])

        # Place treasure randomly
        for _ in range(50):
            tx = random.randrange(self.cols)
            ty = random.randrange(self.rows)
            if (tx, ty) not in reserved_positions:
                break
        else:
            return False

        self.treasure_pos = (tx, ty)
        
        # Mark treasure
        treasure_tile = self.get_tile(tx, ty)
        treasure_tile.type = 'treasure'
        treasure_tile.hint_level = -1
        self.hint_positions[-1] = (tx, ty)

        # Place hints in a backwards chain from treasure
        chain_len = self.HINT_CHAIN_LENGTH
        cx, cy = tx, ty
        
        for level in range(chain_len - 1, -1, -1):
            extra_filters = []
            if level == 0 and spawn_positions:
                extra_filters.append(
                    lambda position: all(
                        self._manhattan_distance(position, spawn_pos) >= self.MIN_FIRST_HINT_SPAWN_DISTANCE
                        for spawn_pos in spawn_positions
                    )
                )

            next_pos = self._find_open_tile(
                cx,
                cy,
                reserved_positions=reserved_positions,
                min_distance=self.MIN_CHAIN_DISTANCE,
                extra_filters=extra_filters,
            )
            if next_pos is None:
                return False

            cx, cy = next_pos
            tile = self.get_tile(cx, cy)
            tile.type = 'hint'
            tile.hint_level = level
            self.hint_positions[level] = (cx, cy)
            reserved_positions.add((cx, cy))

        first_hint_pos = self.hint_positions.get(0)
        if first_hint_pos:
            self.get_tile(*first_hint_pos).mark_visible()

        return len(self.hint_positions) == self.HINT_CHAIN_LENGTH + 1

    def _get_required_path_points(self, spawn_positions=None):
        """Return the ordered points that must remain connected."""
        points = list(spawn_positions or [])
        for level in range(self.HINT_CHAIN_LENGTH):
            position = self.hint_positions.get(level)
            if position:
                points.append(position)
        if self.treasure_pos:
            points.append(self.treasure_pos)
        return points

    def is_walkable(self, col, row):
        """Return True when a tile can be occupied by a player or bot."""
        tile = self.get_tile(col, row)
        return tile is not None and tile.type != 'wall'

    def _has_path(self, start, goal):
        """Breadth-first search to ensure walls do not block mandatory routes."""
        if start is None or goal is None:
            return False
        if not self.is_walkable(*start) or not self.is_walkable(*goal):
            return False

        frontier = deque([start])
        visited = {start}

        while frontier:
            col, row = frontier.popleft()
            if (col, row) == goal:
                return True

            for dx, dy in self.STEP_DIRECTIONS:
                next_col = col + dx
                next_row = row + dy
                next_pos = (next_col, next_row)
                if next_pos in visited or not self.is_walkable(next_col, next_row):
                    continue
                visited.add(next_pos)
                frontier.append(next_pos)

        return False

    def _routes_are_valid(self, spawn_positions=None):
        """Return True when all mandatory objectives remain reachable in sequence."""
        required_points = self._get_required_path_points(spawn_positions=spawn_positions)
        if len(required_points) < 2:
            return True

        for start, goal in zip(required_points, required_points[1:]):
            if not self._has_path(start, goal):
                return False
        return True

    def _build_wall_segment(self, reserved_positions):
        """Create a wall segment candidate in one of four directions."""
        direction = random.choice(self.STEP_DIRECTIONS)
        length = random.randint(self.WALL_SEGMENT_MIN_LENGTH, self.WALL_SEGMENT_MAX_LENGTH)
        start_col = random.randrange(self.cols)
        start_row = random.randrange(self.rows)

        segment = []
        col = start_col
        row = start_row

        for _ in range(length):
            if not (0 <= col < self.cols and 0 <= row < self.rows):
                return None

            tile = self.get_tile(col, row)
            position = (col, row)
            if position in reserved_positions or tile.type != 'dirt':
                return None

            segment.append(position)
            col += direction[0]
            row += direction[1]

        return segment

    def place_walls(self, spawn_positions=None):
        """Place random wall segments while preserving all required routes."""
        reserved_positions = set(spawn_positions or [])
        reserved_positions.update(self.hint_positions.values())
        if self.treasure_pos:
            reserved_positions.add(self.treasure_pos)

        walls_placed = 0
        attempts = 0

        while walls_placed < self.WALL_SEGMENT_COUNT and attempts < self.WALL_PLACEMENT_ATTEMPTS:
            segment = self._build_wall_segment(reserved_positions)
            attempts += 1
            if not segment:
                continue

            applied_tiles = []
            for col, row in segment:
                tile = self.get_tile(col, row)
                tile.type = 'wall'
                tile.mark_visible()
                self.wall_positions.append((col, row))
                applied_tiles.append(tile)

            if self._routes_are_valid(spawn_positions=spawn_positions):
                walls_placed += 1
                continue

            for tile in applied_tiles:
                tile.type = 'dirt'
                tile.state = Tile.HIDDEN
                self.wall_positions.remove((tile.col, tile.row))

        return walls_placed >= max(1, self.WALL_SEGMENT_COUNT // 2)

    def export_layout(self):
        """Return a serializable layout so both competitors can play equivalent maps."""
        return {
            'treasure_pos': tuple(self.treasure_pos) if self.treasure_pos else None,
            'hint_positions': dict(self.hint_positions),
            'bomb_positions': list(self.bomb_positions),
            'wall_positions': list(self.wall_positions),
        }

    def load_layout(self, layout):
        """Load a previously generated layout into a fresh map instance."""
        self._reset_layout()

        self.treasure_pos = tuple(layout['treasure_pos']) if layout.get('treasure_pos') else None
        self.hint_positions = {int(level): tuple(pos) for level, pos in layout.get('hint_positions', {}).items()}
        self.bomb_positions = [tuple(pos) for pos in layout.get('bomb_positions', [])]
        self.wall_positions = [tuple(pos) for pos in layout.get('wall_positions', [])]

        if self.treasure_pos:
            treasure_tile = self.get_tile(*self.treasure_pos)
            treasure_tile.type = 'treasure'
            treasure_tile.hint_level = -1

        for level, position in self.hint_positions.items():
            if level < 0:
                continue
            tile = self.get_tile(*position)
            tile.type = 'hint'
            tile.hint_level = level

        for position in self.bomb_positions:
            self.get_tile(*position).type = 'bomb'

        for position in self.wall_positions:
            tile = self.get_tile(*position)
            tile.type = 'wall'
            tile.mark_visible()

        first_hint_pos = self.hint_positions.get(0)
        if first_hint_pos:
            self.get_tile(*first_hint_pos).mark_visible()

    def place_bombs(self, bomb_count=30, spawn_positions=None):
        """Place bombs randomly around the map, concentrated near hints and treasure."""
        protected_positions = set(spawn_positions or [])
        placed = 0
        attempts = 0
        max_attempts = bomb_count * 15
        
        while placed < bomb_count and attempts < max_attempts:
            bx = random.randrange(self.cols)
            by = random.randrange(self.rows)
            tile = self.get_tile(bx, by)
            
            # Don't place bombs on hints or treasure
            if tile.type == 'dirt' and (bx, by) not in protected_positions:
                # 30% chance to place bomb near hints (closer clustering)
                if random.random() < 0.3 and self.hint_positions:
                    hint_pos = random.choice(list(self.hint_positions.values()))
                    dist = abs(bx - hint_pos[0]) + abs(by - hint_pos[1])
                    if dist < 8:  # Place near hints
                        tile.type = 'bomb'
                        self.bomb_positions.append((bx, by))
                        placed += 1
                elif random.random() < 0.7:  # Random placement
                    tile.type = 'bomb'
                    self.bomb_positions.append((bx, by))
                    placed += 1
            
            attempts += 1

    def get_tile(self, col, row):
        """Get tile at specified column and row."""
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.tiles[col][row]
        return None

    def try_dig(self, player):
        """Process digging action by player at current position."""
        tx, ty = player.col, player.row
        tile = self.get_tile(tx, ty)

        if tile is None:
            return 'unavailable'
        if tile.type == 'wall':
            return 'blocked'
        if tile.revealed:
            return 'already_dug'

        result = None
        reveal_tile = True

        if tile.type == 'hint':
            # Only give hint if it's the next one in sequence
            if tile.hint_level == player.current_hint_level + 1:
                player.current_hint_level += 1
                result = 'hint_correct'
            else:
                result = 'locked'
                reveal_tile = False
        
        elif tile.type == 'treasure':
            # Can only find treasure after getting all hints
            if player.current_hint_level >= self.HINT_CHAIN_LENGTH - 1:
                player.found_treasure = True
                result = 'treasure'
            else:
                result = 'locked'
                reveal_tile = False
        
        elif tile.type == 'bomb':
            player.health = max(0, player.health - 1)
            result = 'bomb'
        
        else:  # Empty dirt
            result = 'empty'

        if reveal_tile:
            tile.mark_dug()
        return result

    def get_clue_text(self, hint_level):
        """Generate coordinate clue text for the next target."""
        def format_coords(position):
            col, row = position
            return f"X={col + 1}, Y={row + 1}"

        if hint_level < 0:
            first_hint = self.hint_positions.get(0)
            if first_hint is None:
                return "Hint 1 is unavailable."
            return f"Hint 1 is at {format_coords(first_hint)}"

        if hint_level not in self.hint_positions:
            return "No more hints!"
        
        next_level = hint_level + 1
        
        if hint_level >= self.HINT_CHAIN_LENGTH - 1:
            next_pos = self.treasure_pos
            next_level = -1
        elif next_level in self.hint_positions:
            next_pos = self.hint_positions[next_level]
        else:
            return "Cannot compute next clue"

        if next_level == -1:
            return f"Treasure is at {format_coords(next_pos)}. You need all {self.HINT_CHAIN_LENGTH} hints to open it."
        else:
            return f"Hint {next_level + 1} is at {format_coords(next_pos)}"

    def update(self, dt):
        """Update map state each frame."""
        pass

    def render(self, surface, x_offset=0, y_offset=0):
        """Render the entire map on the surface."""
        for c in range(self.cols):
            for r in range(self.rows):
                tile = self.get_tile(c, r)
                rect = pygame.Rect(
                    x_offset + c * TILE_SIZE,
                    y_offset + r * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
                color = BROWN

                if tile.type == 'wall':
                    color = (70, 70, 70)
                elif tile.state == Tile.DUG:
                    if tile.type == 'bomb':
                        color = RED
                    elif tile.type == 'hint':
                        color = YELLOW
                    elif tile.type == 'treasure':
                        color = GREEN
                    else:
                        color = GRAY

                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 1)

                if tile.type == 'wall':
                    inner_rect = rect.inflate(-8, -8)
                    pygame.draw.rect(surface, (160, 160, 160), inner_rect, 2)
                elif tile.state == Tile.VISIBLE:
                    marker_color = YELLOW if tile.type == 'hint' else WHITE
                    marker_rect = rect.inflate(-12, -12)
                    pygame.draw.rect(surface, marker_color, marker_rect, 3)
