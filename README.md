# Treasure Hunt (Pygame)

Treasure Hunt is a local competitive digging game built with Python and Pygame.
The project supports:

- `PvP`: 2 human players on one machine
- `PvE`: 1 human player vs AI
- `EvE`: 2 bots play automatically while you watch

The game is desktop Pygame, not a web game.

## Features

- Main flow: `Start -> Mode -> Difficulty -> Match -> End`
- 20x20 grid map, tile size 32px
- Fair mirrored layout between both sides
- 3-key chain before treasure can be claimed
- Random bombs and walls
- Valid path generation so maps stay playable
- Bot pathfinding with A*
- Skills with real effects: `Freeze`, `Blind`, `Extra Hint`
- Split-screen gameplay UI
- Fullscreen toggle
- Menu and gameplay audio routing

## Requirements

- Python 3.11 recommended
- `pygame`

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the game:

```bash
python main.py
```

## How To Play

Each match takes place on a `20x20` grid.

Your objective is:

1. Find `Key 1`
2. Find `Key 2`
3. Find `Key 3`
4. Dig the treasure

Important rules:

- The treasure is locked until all 3 keys are collected in order.
- Digging the wrong tile causes a short cooldown / stun.
- Digging a bomb removes `1 HP`.
- If HP reaches `0`, that side loses.
- If the timer reaches `0`, the round ends in a draw.
- Walls block movement for both players and bots.

## Skills

Each skill has cooldown and works differently:

- `Freeze`: freezes the opponent for a short time
- `Blind`: limits the opponent's information for a short time
- `Extra Hint`: reveals extra information about your next target

`Freeze` and `Blind` target the opponent.
`Extra Hint` helps the player who casts it.

## Game Modes

### PvP

Two human players play locally on the same machine.

- Both sides follow the same rules
- Both sides get equivalent map layout
- Best mode for direct competitive play

### PvE

One human player fights one bot.

Difficulty levels:

- `Easy`: slower, less efficient, more mistakes
- `Normal`: stable A* behavior with some delay and randomness
- `Hard`: more optimal pathing, better target choice, fewer mistakes

### EvE

Two bots play automatically.

- Useful for observing AI behavior
- Good for checking balance between difficulty levels and map generation

## Controls

### Global

- `F11`: toggle fullscreen
- `Alt + Enter`: toggle fullscreen
- `ESC`: leave fullscreen first, otherwise close/exit current run

### Menu

- `Enter`: confirm / continue
- `1 / 2 / 3`: quick-select mode or difficulty where available
- Mouse click also works on menu buttons

### In Match

- `Tab`: pause / resume
- `F10`: open settings
- `R`: restart current match

### PvP Controls

Player 1:

- `W / A / S / D`: move
- `Space` or `Left Ctrl`: dig
- `Q`: Freeze
- `E`: Blind
- `F`: Extra Hint

Player 2:

- `Arrow Keys`: move
- `Enter`, `Numpad Enter`, or `Right Ctrl`: dig
- `I`: Freeze
- `O`: Blind
- `P`: Extra Hint

### PvE Controls

Human player:

- `W / A / S / D` or `Arrow Keys`: move
- `Space`, `Enter`, `Left Ctrl`, or `Numpad Enter`: dig
- `Q`: Freeze bot
- `E`: Blind bot
- `F`: Extra Hint

### EvE Controls

No direct player control during movement.

Useful observer controls:

- `Tab`: pause / resume
- `R`: restart
- `F10`: settings
- `F11`: fullscreen

## Audio Assets

Background music is loaded from:

- `assets/music/menu.ogg` or `assets/music/menu.mp3`
- `assets/music/gameplay.ogg` or `assets/music/gameplay.mp3`
- `assets/music/result.ogg` or `assets/music/result.mp3`

Sound effects are loaded from `assets/sounds/`.

If a file is missing, the game should continue running without crashing.

## Project Structure

```text
treasure-hunt/
|-- assets/
|   |-- music/
|   |-- sounds/
|-- scripts/
|-- src/
|   |-- audio_manager.py
|   |-- bot_ai.py
|   |-- game.py
|   |-- game_mode.py
|   |-- game_state.py
|   |-- map.py
|   |-- player.py
|   |-- settings.py
|   |-- skills.py
|   `-- ui_manager.py
|-- tests/
|-- main.py
|-- requirements.txt
`-- README.md
```

## Verification

Compile check:

```bash
python -m compileall src
```

Run tests:

```bash
python -m unittest discover -s tests
```

## License

MIT
