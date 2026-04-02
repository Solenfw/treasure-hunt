"""Game mode definitions and enumeration."""

from enum import Enum


class GameMode(Enum):
    """Supported game modes."""
    PVP = "pvp"  # Player vs Player
    PVE_EASY = "pve_easy"  # Player vs AI (Easy)
    PVE_NORMAL = "pve_normal"  # Player vs AI (Normal)
    PVE_HARD = "pve_hard"  # Player vs AI (Hard)
    EVE = "eve"  # AI vs AI (Spectator)


class Difficulty(Enum):
    """AI Difficulty levels."""
    EASY = 1
    NORMAL = 2
    HARD = 3
