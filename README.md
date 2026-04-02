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
├── assets/                 # Nguồn tải trên mạng (Pixel art, audio)
│   ├── images/             # spritesheet nhân vật, đất, bom, kho báu
│   ├── sounds/             # nhạc nền, tiếng đào đất, tiếng nổ bom
│   └── fonts/              # file .ttf (pixel font)
├── src/                    # Thư mục chứa code chính
│   ├── __init__.py
│   ├── main.py             # Entry point (khởi tạo game loop)
│   ├── settings.py         # Chứa hằng số (FPS, WIDTH, HEIGHT, TILE_SIZE=32)
│   ├── game_state.py       # Quản lý State (Menu, Chơi game, Thắng/Thua)
│   ├── player.py           # Class Player (Update vị trí, quản lý máu)
│   ├── map.py              # Class Grid 20x20 (Tạo bản đồ, logic đào bới)
│   ├── hint_system.py      # Logic thuật toán sinh chuỗi Gợi ý & Đặt bom
│   ├── bot_ai.py           # Logic cho PvE và EvE
│   ├── game.py             # Game loop chính
│   └── ui_manager.py       # Vẽ HUD, Text, Thanh tiến trình, Menu
├── main.py                 # Entry point wrapper
├── settings.py             # Backward compatibility redirect
├── .gitignore              # Bỏ qua __pycache__/, venv/ v.v..
├── README.md               # Copy Markdown ở phần 1 vào đây
└── requirements.txt        # Chứa thư viện cần thiết (pygame)

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
