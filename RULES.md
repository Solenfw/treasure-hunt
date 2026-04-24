# 🏴‍☠️ GAME DESIGN DOCUMENT: Treasure Hunt

## 1. Overview
- **Game name:** Treasure Hunt
- **Genre:** Puzzle, Competitive Racing, Strategy.
- **Introduction:** Treasure Hunt is a highly competitive puzzle-adventure game. A special feature of the game is that players do not confront each other directly on the same map, but race on two separate, symmetrical maps with equivalent difficulty. The player's task is to use logical thinking to decode a series of "Hints" hidden underground to find the final Treasure. At the same time, players must carefully avoid deadly Bombs and skillfully use special Skills to disrupt the opponent's progress. Whoever touches the Treasure first will be the winner.

## 2. Core Rules

### General gameplay mechanics:
- **Time limit:** Each match lasts up to 2 minutes.
- **Hearts (Lives):** Each player starts with 2 Hearts. If the number of hearts reaches 0, the player immediately loses (Game Over).

### The Hint Chain:
On a 20x20 map, everything is buried (hidden), except for Hint number 1.
1. When a player arrives at and decodes Hint 1, it will provide a clue (coordinates, direction, or a logic puzzle) to find Hint 2.
2. Hint 2 will lead to Hint 3, and so on until it reveals the location of the Treasure.
*(Note: The game mechanics will coordinate so that players can only find the treasure in sequence; there is no such thing as "random digging" or "getting lucky")*

### Digging Mechanics & Risks:
Based on the clues, the player moves to the suspected cell and executes the "Dig" command:
- **Digging a Hint/Treasure:** Unlocks the next target.
- **Digging an Empty Dirt (Wrong Location):** No health loss, but the character gets stunned/loses time digging for about 2-3 seconds (Time penalty).
- **Digging a Bomb:** Loses 1 Heart and gets stunned. Bombs are hidden around Hint/Treasure areas to punish incorrect reasoning.

### Win/Loss Conditions:
- **Win:** Finding the Treasure first, or the opponent steps on a Bomb and loses all hearts.
- **Draw:** If after 2 minutes no one has found the Treasure.

### Game Modes:
1. **Player vs Player (PvP):** Two players compete in parallel. They can pick up "Skill items" for Cross-map Sabotage such as: 3-second freeze, map blind, add hint. There is a Progress Bar to indicate the opponent's progress.
2. **Player vs Computer (PvE):** Play against AI (Easy, Normal, Hard). The AI simulates solving puzzles and moves at pre-programmed speeds.
3. **Computer vs Computer (EvE - Spectator):** 2 Bots compete automatically. The player acts as a referee, watches the puzzle logic, and can fast-forward/slow down.

## 3. Controls & Interface

### Control System:
- `W / A / S / D`: Move the character cell by cell (Grid 20x20).
- `Space`: Interact / Dig at the current cell.
- `E`: Activate Skill item (Sabotage Skill).

### User Interface (UI / HUD):
- **20x20 Map:** Dirt surface (combined with Fog of War for unexplored areas).
- **Personal HUD:**
  - *Top corner:* Countdown timer (2:00), Hearts (2 Hearts).
  - *Clue UI:* Content of the latest Hint (e.g., *"The next hint is 4 steps North from here"*).
  - *Tension UI:* Opponent's status Progress Bar (e.g., *"Opponent has found Hint 2!"*).