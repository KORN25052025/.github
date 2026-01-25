"""
Leaderboard System.

Manages competitive leaderboards for student motivation.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum


class LeaderboardType(str, Enum):
    """Types of leaderboards."""
    DAILY_XP = "daily_xp"
    WEEKLY_XP = "weekly_xp"
    MONTHLY_XP = "monthly_xp"
    ALL_TIME_XP = "all_time_xp"
    STREAK = "streak"
    ACCURACY = "accuracy"


@dataclass
class LeaderboardEntry:
    """Entry in a leaderboard."""
    user_id: str
    display_name: str
    value: float
    rank: int
    avatar_url: Optional[str] = None
    change: int = 0  # Position change from previous period


@dataclass
class UserLeaderboardStats:
    """User's stats across leaderboards."""
    user_id: str
    display_name: str
    xp_today: int = 0
    xp_this_week: int = 0
    xp_this_month: int = 0
    xp_total: int = 0
    best_streak: int = 0
    accuracy: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class Leaderboard:
    """
    Leaderboard system for competitive motivation.

    Provides:
    - Daily/Weekly/Monthly XP leaderboards
    - All-time XP leaderboard
    - Streak leaderboard
    - Accuracy leaderboard
    """

    # Leaderboard size limits
    TOP_N = 100

    def __init__(self):
        """Initialize leaderboard."""
        self._user_stats: Dict[str, UserLeaderboardStats] = {}
        self._leaderboards: Dict[LeaderboardType, List[LeaderboardEntry]] = {}

    def get_user_stats(self, user_id: str) -> UserLeaderboardStats:
        """Get user's leaderboard stats."""
        if user_id not in self._user_stats:
            self._user_stats[user_id] = UserLeaderboardStats(
                user_id=user_id,
                display_name=f"User_{user_id[:6]}",
            )
        return self._user_stats[user_id]

    def update_user_stats(
        self,
        user_id: str,
        display_name: Optional[str] = None,
        xp_earned: int = 0,
        is_correct: Optional[bool] = None,
        streak: int = 0
    ) -> None:
        """
        Update user's leaderboard stats.

        Args:
            user_id: User identifier
            display_name: Optional display name
            xp_earned: XP earned in this update
            is_correct: Whether last answer was correct (for accuracy)
            streak: Current answer streak
        """
        stats = self.get_user_stats(user_id)

        if display_name:
            stats.display_name = display_name

        if xp_earned > 0:
            stats.xp_today += xp_earned
            stats.xp_this_week += xp_earned
            stats.xp_this_month += xp_earned
            stats.xp_total += xp_earned

        if streak > stats.best_streak:
            stats.best_streak = streak

        # Update accuracy (simplified - would use proper calculation in production)
        if is_correct is not None:
            # Rolling accuracy update
            pass

        stats.last_updated = datetime.utcnow()

        # Rebuild relevant leaderboards
        self._rebuild_leaderboards()

    def _rebuild_leaderboards(self) -> None:
        """Rebuild all leaderboards from user stats."""
        users = list(self._user_stats.values())

        # Daily XP
        self._leaderboards[LeaderboardType.DAILY_XP] = self._build_leaderboard(
            users, lambda u: u.xp_today
        )

        # Weekly XP
        self._leaderboards[LeaderboardType.WEEKLY_XP] = self._build_leaderboard(
            users, lambda u: u.xp_this_week
        )

        # Monthly XP
        self._leaderboards[LeaderboardType.MONTHLY_XP] = self._build_leaderboard(
            users, lambda u: u.xp_this_month
        )

        # All-time XP
        self._leaderboards[LeaderboardType.ALL_TIME_XP] = self._build_leaderboard(
            users, lambda u: u.xp_total
        )

        # Streak
        self._leaderboards[LeaderboardType.STREAK] = self._build_leaderboard(
            users, lambda u: u.best_streak
        )

        # Accuracy
        self._leaderboards[LeaderboardType.ACCURACY] = self._build_leaderboard(
            users, lambda u: u.accuracy
        )

    def _build_leaderboard(
        self,
        users: List[UserLeaderboardStats],
        key_func
    ) -> List[LeaderboardEntry]:
        """Build a single leaderboard from user stats."""
        # Sort by value descending
        sorted_users = sorted(users, key=key_func, reverse=True)

        entries = []
        for rank, user in enumerate(sorted_users[:self.TOP_N], start=1):
            entries.append(LeaderboardEntry(
                user_id=user.user_id,
                display_name=user.display_name,
                value=key_func(user),
                rank=rank,
            ))

        return entries

    def get_leaderboard(
        self,
        leaderboard_type: LeaderboardType,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get leaderboard entries.

        Args:
            leaderboard_type: Type of leaderboard
            limit: Number of entries to return
            offset: Starting position

        Returns:
            List of leaderboard entries
        """
        entries = self._leaderboards.get(leaderboard_type, [])
        sliced = entries[offset:offset + limit]

        return [
            {
                "rank": e.rank,
                "user_id": e.user_id,
                "display_name": e.display_name,
                "value": e.value,
                "change": e.change,
            }
            for e in sliced
        ]

    def get_user_rank(
        self,
        user_id: str,
        leaderboard_type: LeaderboardType
    ) -> Optional[Dict]:
        """
        Get user's rank in a leaderboard.

        Args:
            user_id: User identifier
            leaderboard_type: Type of leaderboard

        Returns:
            User's leaderboard entry or None
        """
        entries = self._leaderboards.get(leaderboard_type, [])

        for entry in entries:
            if entry.user_id == user_id:
                return {
                    "rank": entry.rank,
                    "value": entry.value,
                    "total_users": len(entries),
                    "percentile": (1 - entry.rank / len(entries)) * 100 if entries else 0,
                }

        return None

    def get_user_ranks_all(self, user_id: str) -> Dict:
        """
        Get user's rank across all leaderboards.

        Args:
            user_id: User identifier

        Returns:
            Dict with ranks for each leaderboard type
        """
        return {
            lb_type.value: self.get_user_rank(user_id, lb_type)
            for lb_type in LeaderboardType
        }

    def get_nearby_users(
        self,
        user_id: str,
        leaderboard_type: LeaderboardType,
        count: int = 2
    ) -> List[Dict]:
        """
        Get users near the specified user in the leaderboard.

        Args:
            user_id: User identifier
            leaderboard_type: Type of leaderboard
            count: Number of users above and below to return

        Returns:
            List of nearby users
        """
        entries = self._leaderboards.get(leaderboard_type, [])
        user_idx = None

        for idx, entry in enumerate(entries):
            if entry.user_id == user_id:
                user_idx = idx
                break

        if user_idx is None:
            return []

        start = max(0, user_idx - count)
        end = min(len(entries), user_idx + count + 1)

        return [
            {
                "rank": e.rank,
                "user_id": e.user_id,
                "display_name": e.display_name,
                "value": e.value,
                "is_current_user": e.user_id == user_id,
            }
            for e in entries[start:end]
        ]

    def reset_daily(self) -> None:
        """Reset daily leaderboard stats."""
        for user in self._user_stats.values():
            user.xp_today = 0
        self._rebuild_leaderboards()

    def reset_weekly(self) -> None:
        """Reset weekly leaderboard stats."""
        for user in self._user_stats.values():
            user.xp_this_week = 0
        self._rebuild_leaderboards()

    def reset_monthly(self) -> None:
        """Reset monthly leaderboard stats."""
        for user in self._user_stats.values():
            user.xp_this_month = 0
        self._rebuild_leaderboards()
