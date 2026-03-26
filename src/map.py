import random
import pygame
from settings import GRID_COLS, GRID_ROWS, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, BROWN, GREEN, GRAY, YELLOW, RED


class Tile:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.type = 'dirt'  # dirt, bomb, hint, treasure, empty
        self.revealed = False
        self.diggable = True
        self.hint_level = None


class Map:
    def __init__(self):
        self.cols = GRID_COLS
        self.rows = GRID_ROWS
        self.tiles = [[Tile(c, r) for r in range(self.rows)] for c in range(self.cols)]
        self.generate_hint_chain()

    def generate_hint_chain(self):
        # simple: place treasure randomly then create linear hints leading to it
        tx = random.randrange(self.cols)
        ty = random.randrange(self.rows)
        self.treasure_pos = (tx, ty)
        # mark treasure
        self.get_tile(tx, ty).type = 'treasure'
        self.get_tile(tx, ty).hint_level = 999

        # place 5 hints in a chain
        chain_len = 5
        cx, cy = tx, ty
        for level in range(chain_len - 1, -1, -1):
            # move away from treasure
            nx = max(0, min(self.cols - 1, cx + random.choice([-1, 0, 1])))
            ny = max(0, min(self.rows - 1, cy + random.choice([-1, 0, 1])))
            cx, cy = nx, ny
            t = self.get_tile(cx, cy)
            if t.type == 'dirt':
                t.type = 'hint'
                t.hint_level = level

        # place some bombs randomly
        for _ in range(30):
            bx = random.randrange(self.cols)
            by = random.randrange(self.rows)
            t = self.get_tile(bx, by)
            if t.type == 'dirt':
                t.type = 'bomb'

    def get_tile(self, col, row):
        return self.tiles[col][row]

    def try_dig(self, player):
        tx, ty = player.col, player.row
        tile = self.get_tile(tx, ty)
        if not tile.diggable:
            return 'unavailable'
        # simple rules: if hint_level is higher than player's current_hint_level -> show empty
        if tile.type == 'hint':
            if tile.hint_level == player.current_hint_level + 1:
                tile.revealed = True
                player.current_hint_level += 1
                return 'hint'
            else:
                tile.revealed = True
                return 'empty'
        elif tile.type == 'treasure':
            if player.current_hint_level >= 4:
                tile.revealed = True
                return 'treasure'
            else:
                tile.revealed = True
                return 'empty'
        elif tile.type == 'bomb':
            tile.revealed = True
            player.health -= 1
            return 'bomb'
        else:
            tile.revealed = True
            return 'empty'

    def update(self, dt):
        pass

    def render(self, surface):
        # draw map at top-left corner
        for c in range(self.cols):
            for r in range(self.rows):
                t = self.get_tile(c, r)
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = BROWN
                if t.revealed:
                    if t.type == 'bomb':
                        color = RED
                    elif t.type == 'hint':
                        color = YELLOW
                    elif t.type == 'treasure':
                        color = GREEN
                    else:
                        color = GRAY
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 1)
