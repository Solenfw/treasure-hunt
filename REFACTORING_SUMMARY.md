# Project Refactoring Summary - Treasure Hunt Game

## Overview
Complete refactoring of the Treasure Hunt project to implement the full game design document specifications. The project has been reorganized to support multiple game modes (PvP, PvE, EvE) with proper AI difficulty levels, hint chain mechanics, and a complete UI system.

## Directory Structure
```
TreasureHunt/
├── assets/                 # Game assets
│   ├── images/             # Sprite sheets and graphics
│   ├── sounds/             # Audio and music files
│   └── fonts/              # Custom font files (.ttf)
├── src/                    # Main source code
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── settings.py         # Game constants and configuration
│   ├── game_state.py       # Game state management
│   ├── game_mode.py        # Game mode and difficulty enumerations
│   ├── player.py           # Player class with skills and mechanics
│   ├── bot_ai.py           # AI bot with difficulty levels
│   ├── game.py             # Main game loop and multiplayer logic
│   ├── map.py              # Map grid and hint chain system
│   ├── ui_manager.py       # Complete UI system
│   ├── hint_system.py      # Hint algorithm (legacy)
│   ├── skills.py           # Skills framework (legacy)
│   ├── utils.py            # Utilities (legacy)
│   ├── entities.py         # Entities (legacy)
│   └── ui.py               # Legacy UI (superseded)
├── main.py                 # Root entry point
├── settings.py             # Backward compatibility redirect
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies (pygame)
├── README.md               # Game documentation
└── RULES.md                # Game design document (Vietnamese)
```

## Key Features Implemented

### 1. Hint Chain System
- **Enforced sequence**: Players cannot skip hints or guess randomly
- **5-level chain**: Hints 0-4 leading to treasure discovery
- **Directional clues**: Each hint provides distance and direction to next target
- **Map generation**: Uses smart bomb placement around hint clusters

```python
# Example clue generation
"Hint 2 is 6 steps to the Northeast"
"The treasure is 4 steps to the South!"
```

### 2. Game Modes
- **PvP (Player vs Player)**: Two players compete on separate symmetric maps
- **PvE Easy/Normal/Hard**: Player vs AI with adjustable difficulty
- **EvE (Spectator)**: AI vs AI battle for entertainment

### 3. Player Mechanics
- **Health System**: 2 hearts per player, lose 1 on bomb hit
- **Dig Cooldown**: 
  - Correct hint: 0.5s cooldown
  - Wrong guess: 2.0s cooldown + stun
  - Bomb hit: 1.5s cooldown + 1.5s stun
- **Skills System**: 
  - Freeze (3 seconds cooldown): Prevent opponent movement
  - Blind (5 seconds cooldown): Hide opponent's map
  - Extra Hint (extends hint chain): Gain extra clues
  - Each skill has max cooldown before availability

### 4. AI Difficulty Levels
**Easy Mode**:
- Random movement and digging
- 40% accuracy in decision making
- Slower movement speed

**Normal Mode**:
- Mix of random and intelligent behavior
- 65% accuracy
- Medium movement speed

**Hard Mode**:
- Intelligent movement towards unexplored tiles
- Memory of found hints and bombs
- 90% accuracy in decisions
- Fast movement speed

### 5. Enhanced UI System
- **Main Menu**: Clean intro with game title
- **Mode Selection**: Choose between PvP/PvE/EvE
- **Game HUD**: 
  - Timer display (2:00 countdown)
  - Player status panels (health, hint level, cooldowns)
  - Clue box with directional hints
  - Progress bars for multiplayer
  - Skill status indicators
- **Pause Overlay**: Semi-transparent overlay with pause info
- **Game Over Screen**: Winner announcement with reason

### 6. Game State Management
States: MENU → MODE_SELECT → PLAYING (paused) → GAME_OVER → MENU

**Game Over Conditions**:
- Found treasure first
- Opponent's health reaches 0
- Time expires (2 minutes) = Draw

### 7. Settings System
```python
# Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Map
GRID_COLS = 20
GRID_ROWS = 20
TILE_SIZE = 32px

# Game
STARTING_HEALTH = 2
ROUND_TIME_MS = 120 seconds
```

## Code Architecture

### Core Classes

**Map** - Grid management with hint chain enforcement
- `generate_hint_chain()`: Create enforced hint sequence
- `place_bombs()`: Smart bomb placement
- `try_dig()`: Enforce correct hint discovery
- `get_clue_text()`: Generate directional hints
- `get_tile()`: Safe tile access

**Player** - Player mechanics and skills
- `update()`: Handle movement and cooldown updates
- `dig()`: Execute dig action with cooldown management
- `use_skill()`: Activate special abilities
- `freeze()`: Apply freeze effect
- `apply_damage()`: Handle bomb damage

**BotAI** - Intelligent opponent
- `update()`: Execute AI behavior each frame
- `_make_move()`: Decide movement based on difficulty
- `_calculate_intelligent_move()`: Pattern-based decision making
- `_try_dig()`: Smart digging with memory
- Memory tracking of hints and bombs

**GameState** - State machine
- Multiple states: MENU, MODE_SELECT, DIFFICULTY_SELECT, PLAYING, PAUSED, GAME_OVER
- Timer management for 2-minute rounds
- Winner tracking and message system

**UIManager** - Comprehensive UI rendering
- `render_main_menu()`: Main menu display
- `render_mode_select()`: Game mode selection
- `render_game_hud()`: In-game HUD with player stats
- `render_clue_box()`: Hint display box
- `render_progress_bar()`: Multiplayer progress comparison
- `render_game_over()`: Game over screen with results
- `render_pause_overlay()`: Pause notification

**Game** - Main game loop orchestrator
- Multiplayer support with proper map separation
- Event handling for all game states
- AI integration for PvE/EvE modes
- Win condition checking
- Frame-by-frame game logic update

## Import Structure
```python
from src.game_mode import GameMode, Difficulty
from src.game_state import GameState
from src.player import Player
from src.bot_ai import BotAI
from src.map import Map
from src.ui_manager import UIManager
```

## Controls
```
W/A/S/D     - Move player (one tile per direction)
Space       - Dig at current position
E           - Activate skill (when available)
P           - Pause/Resume game
Enter       - Start game / Continue from game over
Esc         - Exit to menu / Quit game
1-5         - Select game mode (in mode select screen)
```

## Game Flow
1. **Start**: User runs `python main.py`
2. **Main Menu**: Display title and wait for ENTER
3. **Mode Selection**: Choose PvP/PvE(Easy/Normal/Hard)/EvE
4. **Game Initialization**: Create maps and players based on mode
5. **Gameplay**: 
   - Players move and dig for hints
   - System enforces hint sequence
   - Timer counts down (2 minutes)
   - Skills available for use
6. **Win Conditions**:
   - First to find treasure wins
   - Opponent loses all health = automatic win
   - Time expires = draw
7. **Game Over**: Display winner and reason
8. **Continue**: Return to main menu for next game

## Technical Details

### Tile Types
- **hint**: Numbered 0-4, discoverable only in sequence
- **treasure**: Found after obtaining all 5 hints
- **bomb**: Damages player and applies stun (-1 health, 1.5s stun)
- **dirt**: Empty tile (2s cooldown as penalty)

### Multiplayer Rendering
- **PvP**: Split-screen display (left player 1, right player 2)
- **PvE/EvE**: Single screen focused on player/human observer

### AI Intelligence
- **Memory System**: Tracks found hints and bomb locations
- **Pattern Recognition**: Avoids previously searched empty areas
- **Difficulty Scaling**: Changes probability of correct decisions
- **Movement Strategy**: Targets unexplored regions based on difficulty

## Future Enhancements
- [ ] Asset loading (sprites, audio, fonts)
- [ ] Animation system for digging and movement
- [ ] Sabotage skill animations and effects
- [ ] Sound effects and background music
- [ ] Network multiplayer support
- [ ] Level editor and custom maps
- [ ] Leaderboard and statistics tracking
- [ ] Settings/configuration menu

## Testing Recommendations
1. **Hint Chain**: Verify players must discover hints in order
2. **AI Difficulty**: Test all three difficulty levels for behavior
3. **Multiplayer**: Verify separate maps and fair competition
4. **Edge Cases**: 
   - Both players reach hint 5 simultaneously
   - Time expires during dig action
   - Player dies with remaining hints
5. **UI**: Verify all states render correctly
6. **Controls**: Test all key bindings

---
**Last Updated**: April 2, 2026
**Status**: Core gameplay mechanics complete, ready for asset integration
