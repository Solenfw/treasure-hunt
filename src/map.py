import random
import pygame
from src.settings import GRID_COLS, GRID_ROWS, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, BROWN, GREEN, GRAY, YELLOW, RED


class Tile:
    """Represents a single tile on the game map."""
    
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.type = 'dirt'  # dirt, bomb, hint, treasure
        self.revealed = False
        self.hint_level = None  # 0-4 for hints, -1 for treasure, None for bombs/empty


class Map:
    """Manages the game grid, tiles, and digging logic with enforced hint chain sequence."""
    
    HINT_CHAIN_LENGTH = 5  # Hints 0-4, then Treasure
    
    def __init__(self):
        self.cols = GRID_COLS
        self.rows = GRID_ROWS
        self.tiles = [[Tile(c, r) for r in range(self.rows)] for c in range(self.cols)]
        self.treasure_pos = None
        self.hint_positions = {}  # {hint_level: (col, row)}
        self.bomb_positions = []
        self.generate_map()

    def generate_map(self):
        """Generate the map with enforced hint chain and bombs."""
        self.generate_hint_chain()
        self.place_bombs()

    def generate_hint_chain(self):
        """Place treasure and create a linear hint chain with direction clues."""
        # Place treasure randomly
        tx = random.randrange(self.cols)
        ty = random.randrange(self.rows)
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
            # Move away from treasure with more variation for earlier hints
            steps = chain_len - level
            nx = cx + random.randint(-steps, steps)
            ny = cy + random.randint(-steps, steps)
            
            # Keep within bounds
            nx = max(0, min(self.cols - 1, nx))
            ny = max(0, min(self.rows - 1, ny))
            
            cx, cy = nx, ny
            tile = self.get_tile(cx, cy)
            
            # Only place if not already occupied
            if tile.type == 'dirt':
                tile.type = 'hint'
                tile.hint_level = level
                self.hint_positions[level] = (cx, cy)

    def place_bombs(self, bomb_count=30):
        """Place bombs randomly around the map, concentrated near hints and treasure."""
        placed = 0
        attempts = 0
        max_attempts = bomb_count * 15
        
        while placed < bomb_count and attempts < max_attempts:
            bx = random.randrange(self.cols)
            by = random.randrange(self.rows)
            tile = self.get_tile(bx, by)
            
            # Don't place bombs on hints or treasure
            if tile.type == 'dirt':
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
        
        if tile is None or not tile.revealed is False:
            return 'unavailable'
        
        result = None
        
        if tile.type == 'hint':
            # Only give hint if it's the next one in sequence
            if tile.hint_level == player.current_hint_level + 1:
                player.current_hint_level += 1
                result = 'hint_correct'
            else:
                # Wrong hint or trying to skip ahead
                result = 'empty'
        
        elif tile.type == 'treasure':
            # Can only find treasure after getting all hints
            if player.current_hint_level >= self.HINT_CHAIN_LENGTH - 1:
                result = 'treasure'
            else:
                result = 'empty'
        
        elif tile.type == 'bomb':
            player.health -= 1
            player.dig_cooldown = 3.0  # 3 seconds cooldown
            result = 'bomb'
        
        else:  # Empty dirt
            player.dig_cooldown = 2.0  # 2 seconds cooldown for wrong guess
            result = 'empty'
        
        tile.revealed = True
        return result

    def get_clue_text(self, hint_level):
        """Generate directional clue text from hint to next target."""
        if hint_level not in self.hint_positions:
            return "No more hints!"
        
        current_pos = self.hint_positions[hint_level]
        next_level = hint_level + 1
        
        if next_level == -1:  # Next is treasure
            next_pos = self.treasure_pos
        elif next_level in self.hint_positions:
            next_pos = self.hint_positions[next_level]
        else:
            return "Cannot compute next clue"
        
        # Calculate direction and distance
        dist = abs(current_pos[0] - next_pos[0]) + abs(current_pos[1] - next_pos[1])
        
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        direction = ""
        if dy < 0:
            direction += "North "
        elif dy > 0:
            direction += "South "
        
        if dx < 0:
            direction += "West"
        elif dx > 0:
            direction += "East"
        
        if next_level == -1:
            return f"The treasure is {dist} steps to the {direction.strip()}!"
        else:
            return f"Hint {next_level + 1} is {dist} steps to the {direction.strip()}"

    def update(self, dt):
        """Update map state each frame."""
        pass

    def render(self, surface):
        """Render the entire map on the surface."""
        for c in range(self.cols):
            for r in range(self.rows):
                tile = self.get_tile(c, r)
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = BROWN
                
                if tile.revealed:
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
