"""Hint system and bomb placement logic for the game map."""

import random
from src.settings import GRID_COLS, GRID_ROWS


class HintSystem:
    """Manages hint chain generation and bomb placement."""
    
    def __init__(self, map_obj):
        self.map = map_obj
        self.treasure_pos = None
        self.hint_chain = []
    
    def generate_hint_chain(self):
        """Generate a hint chain leading to the treasure."""
        # Place treasure randomly
        tx = random.randrange(GRID_COLS)
        ty = random.randrange(GRID_ROWS)
        self.treasure_pos = (tx, ty)
        
        # Mark treasure tile
        treasure_tile = self.map.get_tile(tx, ty)
        treasure_tile.type = 'treasure'
        treasure_tile.hint_level = 999
        self.hint_chain.append((tx, ty, 999))
        
        # Place 5 hints in a chain leading to treasure
        chain_len = 5
        cx, cy = tx, ty
        for level in range(chain_len - 1, -1, -1):
            # Move away from treasure
            nx = max(0, min(GRID_COLS - 1, cx + random.choice([-1, 0, 1])))
            ny = max(0, min(GRID_ROWS - 1, cy + random.choice([-1, 0, 1])))
            cx, cy = nx, ny
            
            tile = self.map.get_tile(cx, cy)
            if tile.type == 'dirt':
                tile.type = 'hint'
                tile.hint_level = level
                self.hint_chain.append((cx, cy, level))
    
    def place_bombs(self, bomb_count=30):
        """Place bombs randomly on the map."""
        placed = 0
        attempts = 0
        max_attempts = bomb_count * 10
        
        while placed < bomb_count and attempts < max_attempts:
            bx = random.randrange(GRID_COLS)
            by = random.randrange(GRID_ROWS)
            tile = self.map.get_tile(bx, by)
            
            if tile.type == 'dirt':
                tile.type = 'bomb'
                placed += 1
            
            attempts += 1
