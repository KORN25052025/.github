"""
Streak Tracking System.

Manages daily and answer streaks for motivation.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime, timedelta


@dataclass
class StreakRecord:
    """Streak record for a user."""
    user_id: str

    # Answer streak (consecutive correct answers)
    current_answer_streak: int = 0
    best_answer_streak: int = 0

    # Daily streak (consecutive days practiced)
    current_daily_streak: int = 0
    best_daily_streak: int = 0
    last_practice_date: Optional[datetime] = None

    # Weekly streak
    current_weekly_streak: int = 0
    best_weekly_streak: int = 0

    # Tracking
    total_practice_days: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class StreakTracker:
    """
    Streak tracking for gamification.

    Tracks:
    - Answer streaks (consecutive correct answers)
    - Daily streaks (consecutive days practiced)
    - Weekly streaks (consecutive weeks practiced)
    """

    # Streak freeze: Allow 1 day miss with streak freeze
    STREAK_FREEZE_ENABLED = True

    def __init__(self):
        """Initialize streak tracker."""
        self._records: Dict[str, StreakRecord] = {}

    def get_record(self, user_id: str) -> StreakRecord:
        """Get streak record for a user."""
        if user_id not in self._records:
            self._records[user_id] = StreakRecord(user_id=user_id)
        return self._records[user_id]

    def update_answer_streak(
        self,
        user_id: str,
        is_correct: bool
    ) -> Dict:
        """
        Update answer streak after an answer.

        Args:
            user_id: User identifier
            is_correct: Whether answer was correct

        Returns:
            Dict with streak info
        """
        record = self.get_record(user_id)

        if is_correct:
            record.current_answer_streak += 1
            record.best_answer_streak = max(
                record.best_answer_streak,
                record.current_answer_streak
            )
            streak_broken = False
        else:
            streak_broken = record.current_answer_streak > 0
            record.current_answer_streak = 0

        record.last_updated = datetime.utcnow()

        return {
            "current_streak": record.current_answer_streak,
            "best_streak": record.best_answer_streak,
            "streak_broken": streak_broken,
        }

    def update_daily_streak(self, user_id: str) -> Dict:
        """
        Update daily streak (call when user practices).

        Args:
            user_id: User identifier

        Returns:
            Dict with daily streak info
        """
        record = self.get_record(user_id)
        today = datetime.utcnow().date()

        if record.last_practice_date is None:
            # First practice
            record.current_daily_streak = 1
            record.total_practice_days = 1
        else:
            last_date = record.last_practice_date.date()
            days_diff = (today - last_date).days

            if days_diff == 0:
                # Already practiced today
                pass
            elif days_diff == 1:
                # Consecutive day
                record.current_daily_streak += 1
                record.total_practice_days += 1
            elif days_diff == 2 and self.STREAK_FREEZE_ENABLED:
                # Streak freeze - one day grace
                record.current_daily_streak += 1
                record.total_practice_days += 1
            else:
                # Streak broken
                record.current_daily_streak = 1
                record.total_practice_days += 1

        record.best_daily_streak = max(
            record.best_daily_streak,
            record.current_daily_streak
        )
        record.last_practice_date = datetime.utcnow()
        record.last_updated = datetime.utcnow()

        return {
            "current_daily_streak": record.current_daily_streak,
            "best_daily_streak": record.best_daily_streak,
            "total_practice_days": record.total_practice_days,
            "streak_at_risk": self._is_streak_at_risk(record),
        }

    def _is_streak_at_risk(self, record: StreakRecord) -> bool:
        """Check if daily streak is at risk of breaking."""
        if record.last_practice_date is None:
            return False

        today = datetime.utcnow().date()
        last_date = record.last_practice_date.date()
        days_diff = (today - last_date).days

        # Streak is at risk if they haven't practiced today
        # and they have an active streak
        return days_diff >= 1 and record.current_daily_streak > 0

    def get_streak_status(self, user_id: str) -> Dict:
        """
        Get comprehensive streak status.

        Args:
            user_id: User identifier

        Returns:
            Complete streak information
        """
        record = self.get_record(user_id)

        return {
            "answer_streak": {
                "current": record.current_answer_streak,
                "best": record.best_answer_streak,
            },
            "daily_streak": {
                "current": record.current_daily_streak,
                "best": record.best_daily_streak,
                "at_risk": self._is_streak_at_risk(record),
            },
            "total_practice_days": record.total_practice_days,
            "last_practice": record.last_practice_date.isoformat() if record.last_practice_date else None,
        }

    def check_milestone(self, user_id: str) -> Optional[Dict]:
        """
        Check if user hit a streak milestone.

        Args:
            user_id: User identifier

        Returns:
            Milestone info if hit, None otherwise
        """
        record = self.get_record(user_id)

        # Answer streak milestones
        answer_milestones = [3, 5, 10, 15, 25, 50, 100]
        if record.current_answer_streak in answer_milestones:
            return {
                "type": "answer_streak",
                "value": record.current_answer_streak,
                "message_tr": f"Arka arkaya {record.current_answer_streak} doğru!",
            }

        # Daily streak milestones
        daily_milestones = [3, 7, 14, 30, 60, 100, 365]
        if record.current_daily_streak in daily_milestones:
            return {
                "type": "daily_streak",
                "value": record.current_daily_streak,
                "message_tr": f"{record.current_daily_streak} gün arka arkaya!",
            }

        return None

    def reset_answer_streak(self, user_id: str) -> None:
        """Reset answer streak for a user."""
        record = self.get_record(user_id)
        record.current_answer_streak = 0

    def to_dict(self, user_id: str) -> Dict:
        """Serialize streak record."""
        record = self.get_record(user_id)
        return {
            "user_id": record.user_id,
            "current_answer_streak": record.current_answer_streak,
            "best_answer_streak": record.best_answer_streak,
            "current_daily_streak": record.current_daily_streak,
            "best_daily_streak": record.best_daily_streak,
            "total_practice_days": record.total_practice_days,
            "last_practice_date": record.last_practice_date.isoformat() if record.last_practice_date else None,
            "last_updated": record.last_updated.isoformat(),
        }
