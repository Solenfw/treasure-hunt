# Treasure Hunt (Pygame)

A grid-based competitive treasure hunting game built with Pygame. Supports local PvP, PvE (vs AI), and EvE (AI vs AI) modes, sabotage skills, and a split-screen UI.

## Features
- Main Menu: Play (PvP, PvE, EvE), Settings, Exit
- 20x20 grid map with fog of war
- Player and AI movement (grid-based, WASD)
- Digging, hints, bombs, and treasure logic
- Sabotage skills: Freeze, Blind, Extra Hint
- Split-screen for dual maps
- HUD: Timer, hearts, skill icons, clue box, tension bar
- Pixel art and sound effects (assets folder)

## Project Structure
```
TreasureHunt/
├── main.py                # Game entry point
├── settings.py            # Game constants
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore rules
├── assets/                # Sprites, audio, fonts
├── src/
│   ├── __init__.py
│   ├── game.py            # Game loop & state
│   ├── map.py             # Map/grid logic
│   ├── entities.py        # Player & Bot classes
│   ├── ui.py              # UI rendering
│   ├── skills.py          # Sabotage skills
│   └── utils.py           # Helper functions
```

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the game:
   ```bash
   python main.py
   ```

## Controls
- **W/A/S/D**: Move
- **Space**: Dig
- **E**: Use skill (when available)
- **P**: Pause/Unpause
- **Enter**: Start game from menu

## Assets
- Place your pixel art, audio, and fonts in the `assets/` folder.
- Recommended sources: [Kenney.nl](https://kenney.nl/), [itch.io](https://itch.io/game-assets)

## Roadmap
- [x] Foundation: Grid, movement, digging
- [ ] Core logic: Hints, bombs, treasure
- [ ] Dual map & UI
- [ ] AI & game modes
- [ ] Sabotage skills
- [ ] Polish: Art, sound, animation

## License
MIT (add your own license if needed)
