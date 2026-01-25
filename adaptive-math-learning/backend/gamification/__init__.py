"""
Gamification module for the adaptive math learning system.

Provides:
- XP (Experience Points) system
- Badge/Achievement system
- Streak tracking
- Leaderboard functionality
"""

from .xp_system import XPSystem, XPEvent, XPRecord
from .badges import BadgeSystem, Badge, BadgeCategory
from .streaks import StreakTracker, StreakRecord
from .leaderboard import Leaderboard, LeaderboardEntry

__all__ = [
    "XPSystem",
    "XPEvent",
    "XPRecord",
    "BadgeSystem",
    "Badge",
    "BadgeCategory",
    "StreakTracker",
    "StreakRecord",
    "Leaderboard",
    "LeaderboardEntry",
]
