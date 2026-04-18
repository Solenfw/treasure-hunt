# Game settings
SCREEN_WIDTH = 1280
FPS = 60

# Map settings
GRID_COLS = 20
GRID_ROWS = 20
TILE_SIZE = 32  # so map is 640x640
MAP_WIDTH = GRID_COLS * TILE_SIZE
MAP_HEIGHT = GRID_ROWS * TILE_SIZE
HUD_HEIGHT = 88
CLUE_BOX_HEIGHT = 92
SCREEN_HEIGHT = HUD_HEIGHT + MAP_HEIGHT + CLUE_BOX_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (50, 200, 50)
BROWN = (120, 72, 0)
RED = (200, 30, 30)
YELLOW = (240, 230, 140)

# Game constants
STARTING_HEALTH = 2
ROUND_TIME_SECONDS = 120.0
ROUND_TIME_MS = int(ROUND_TIME_SECONDS * 1000)

SKILL_FEEDBACK_DURATION = 1.1
SKILL_BALANCE = {
    'freeze': {
        'label': 'Freeze',
        'max_cooldown': 18.0,
        'duration': 2.8,
        'requires_target': True,
    },
    'blind': {
        'label': 'Blind',
        'max_cooldown': 20.0,
        'duration': 4.0,
        'requires_target': True,
    },
    'extra_hint': {
        'label': 'Extra Hint',
        'max_cooldown': 24.0,
        'duration': 0.0,
        'requires_target': False,
    },
}

PLAYER_DIG_TIMINGS = {
    'bomb': {'stun': 1.5, 'cooldown': 1.5},
    'empty': {'stun': 0.5, 'cooldown': 2.0},
    'locked': {'stun': 0.5, 'cooldown': 2.0},
    'already_dug': {'stun': 0.0, 'cooldown': 0.15},
    'unavailable': {'stun': 0.0, 'cooldown': 0.15},
    'blocked': {'stun': 0.0, 'cooldown': 0.15},
    'hint_correct': {'stun': 0.0, 'cooldown': 0.5},
    'treasure': {'stun': 0.0, 'cooldown': 0.0},
}

BOT_DIG_TIMINGS = {
    'hint_correct': {'stun': 0.0, 'cooldown': 0.3},
    'bomb': {'stun': 1.5, 'cooldown': 1.5},
    'empty': {'stun': 0.5, 'cooldown': 2.0},
    'locked': {'stun': 0.5, 'cooldown': 2.0},
    'already_dug': {'stun': 0.0, 'cooldown': 0.15},
    'unavailable': {'stun': 0.0, 'cooldown': 0.15},
    'blocked': {'stun': 0.0, 'cooldown': 0.15},
    'treasure': {'stun': 0.0, 'cooldown': 0.0},
}

BOT_DIFFICULTY_BALANCE = {
    'easy': {
        'move_speed': 1.05,
        'dig_probability': 0.18,
        'search_weight': 0.45,
        'wrong_dig_probability': 0.28,
        'skill_aggression': 0.20,
        'skill_check_delay': 7.0,
    },
    'normal': {
        'move_speed': 0.58,
        'dig_probability': 0.12,
        'search_weight': 0.80,
        'wrong_dig_probability': 0.10,
        'skill_aggression': 0.42,
        'skill_check_delay': 5.0,
    },
    'hard': {
        'move_speed': 0.28,
        'dig_probability': 0.08,
        'search_weight': 0.98,
        'wrong_dig_probability': 0.02,
        'skill_aggression': 0.70,
        'skill_check_delay': 3.5,
    },
}

# Assets paths
ASSETS_DIR = 'assets'
IMAGES_DIR = ASSETS_DIR + '/images'
SOUNDS_DIR = ASSETS_DIR + '/sounds'
FONTS_DIR = ASSETS_DIR + '/fonts'
