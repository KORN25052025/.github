"""
XP (Experience Points) System.

Manages experience points for student motivation and progression tracking.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum


class XPEvent(str, Enum):
    """Events that award XP."""
    QUESTION_CORRECT = "question_correct"
    QUESTION_CORRECT_STREAK = "question_correct_streak"
    QUESTION_FIRST_TRY = "question_first_try"
    DAILY_LOGIN = "daily_login"
    SESSION_COMPLETE = "session_complete"
    MASTERY_MILESTONE = "mastery_milestone"
    BADGE_EARNED = "badge_earned"
    PERFECT_SESSION = "perfect_session"
    QUICK_ANSWER = "quick_answer"


@dataclass
class XPRecord:
    """XP record for a user."""
    user_id: str
    total_xp: int = 0
    level: int = 1
    xp_this_level: int = 0
    xp_to_next_level: int = 100

    # XP history
    xp_today: int = 0
    xp_this_week: int = 0
    xp_this_month: int = 0

    # Tracking
    last_updated: datetime = field(default_factory=datetime.utcnow)
    history: List[Dict] = field(default_factory=list)


class XPSystem:
    """
    XP system for gamification.

    Level progression uses a quadratic formula:
    XP needed for level N = 100 * N^1.5

    Level caps at 100 for K-12 context.
    """

    # XP rewards for different events
    XP_REWARDS = {
        XPEvent.QUESTION_CORRECT: 10,
        XPEvent.QUESTION_CORRECT_STREAK: 5,  # Bonus per streak question
        XPEvent.QUESTION_FIRST_TRY: 5,
        XPEvent.DAILY_LOGIN: 20,
        XPEvent.SESSION_COMPLETE: 50,
        XPEvent.MASTERY_MILESTONE: 100,
        XPEvent.BADGE_EARNED: 50,
        XPEvent.PERFECT_SESSION: 100,
        XPEvent.QUICK_ANSWER: 5,  # Under 10 seconds
    }

    MAX_LEVEL = 100

    def __init__(self):
        """Initialize XP system."""
        self._records: Dict[str, XPRecord] = {}

    def get_record(self, user_id: str) -> XPRecord:
        """Get XP record for a user."""
        if user_id not in self._records:
            self._records[user_id] = XPRecord(user_id=user_id)
        return self._records[user_id]

    def award_xp(
        self,
        user_id: str,
        event: XPEvent,
        multiplier: float = 1.0,
        bonus: int = 0
    ) -> Dict:
        """
        Award XP for an event.

        Args:
            user_id: User identifier
            event: XP event type
            multiplier: XP multiplier (for streaks, etc.)
            bonus: Additional bonus XP

        Returns:
            Dict with xp_earned, new_total, leveled_up, new_level
        """
        record = self.get_record(user_id)
        base_xp = self.XP_REWARDS.get(event, 0)
        xp_earned = int(base_xp * multiplier) + bonus

        old_level = record.level
        record.total_xp += xp_earned
        record.xp_today += xp_earned
        record.xp_this_week += xp_earned
        record.xp_this_month += xp_earned
        record.last_updated = datetime.utcnow()

        # Add to history
        record.history.append({
            "event": event.value,
            "xp": xp_earned,
            "timestamp": datetime.utcnow().isoformat(),
        })
        if len(record.history) > 100:
            record.history = record.history[-100:]

        # Check for level up
        self._update_level(record)
        leveled_up = record.level > old_level

        return {
            "xp_earned": xp_earned,
            "new_total": record.total_xp,
            "leveled_up": leveled_up,
            "new_level": record.level,
            "xp_this_level": record.xp_this_level,
            "xp_to_next_level": record.xp_to_next_level,
        }

    def award_for_answer(
        self,
        user_id: str,
        is_correct: bool,
        response_time_ms: int,
        streak: int = 0,
        first_try: bool = True
    ) -> Dict:
        """
        Award XP for answering a question.

        Args:
            user_id: User identifier
            is_correct: Whether answer was correct
            response_time_ms: Response time in milliseconds
            streak: Current correct answer streak
            first_try: Whether this was first attempt

        Returns:
            XP award result
        """
        if not is_correct:
            return {"xp_earned": 0, "new_total": self.get_record(user_id).total_xp}

        total_xp = 0
        results = []

        # Base XP for correct answer
        result = self.award_xp(user_id, XPEvent.QUESTION_CORRECT)
        total_xp += result["xp_earned"]
        results.append(result)

        # Streak bonus
        if streak >= 3:
            streak_multiplier = min(streak / 3, 3.0)  # Cap at 3x
            result = self.award_xp(
                user_id,
                XPEvent.QUESTION_CORRECT_STREAK,
                multiplier=streak_multiplier
            )
            total_xp += result["xp_earned"]
            results.append(result)

        # First try bonus
        if first_try:
            result = self.award_xp(user_id, XPEvent.QUESTION_FIRST_TRY)
            total_xp += result["xp_earned"]
            results.append(result)

        # Quick answer bonus (under 10 seconds)
        if response_time_ms < 10000:
            result = self.award_xp(user_id, XPEvent.QUICK_ANSWER)
            total_xp += result["xp_earned"]
            results.append(result)

        record = self.get_record(user_id)
        return {
            "xp_earned": total_xp,
            "new_total": record.total_xp,
            "level": record.level,
            "leveled_up": any(r.get("leveled_up") for r in results),
            "breakdown": results,
        }

    def _update_level(self, record: XPRecord) -> None:
        """Update level based on total XP."""
        # Calculate level from XP
        # Level N requires total XP = sum(100 * i^1.5 for i in 1..N-1)
        level = 1
        total_xp_needed = 0

        while level < self.MAX_LEVEL:
            xp_for_level = int(100 * (level ** 1.5))
            if record.total_xp < total_xp_needed + xp_for_level:
                break
            total_xp_needed += xp_for_level
            level += 1

        record.level = level
        record.xp_this_level = record.total_xp - total_xp_needed
        record.xp_to_next_level = int(100 * (level ** 1.5)) if level < self.MAX_LEVEL else 0

    def get_xp_for_level(self, level: int) -> int:
        """Get total XP required to reach a level."""
        if level <= 1:
            return 0
        total = 0
        for i in range(1, level):
            total += int(100 * (i ** 1.5))
        return total

    def get_level_progress(self, user_id: str) -> Dict:
        """Get level progress for a user."""
        record = self.get_record(user_id)
        progress = record.xp_this_level / record.xp_to_next_level if record.xp_to_next_level > 0 else 1.0

        return {
            "level": record.level,
            "total_xp": record.total_xp,
            "xp_this_level": record.xp_this_level,
            "xp_to_next_level": record.xp_to_next_level,
            "progress": progress,
            "xp_today": record.xp_today,
        }

    def reset_daily(self, user_id: str) -> None:
        """Reset daily XP counter."""
        record = self.get_record(user_id)
        record.xp_today = 0

    def reset_weekly(self, user_id: str) -> None:
        """Reset weekly XP counter."""
        record = self.get_record(user_id)
        record.xp_this_week = 0

    def to_dict(self, user_id: str) -> Dict:
        """Serialize XP record."""
        record = self.get_record(user_id)
        return {
            "user_id": record.user_id,
            "total_xp": record.total_xp,
            "level": record.level,
            "xp_this_level": record.xp_this_level,
            "xp_to_next_level": record.xp_to_next_level,
            "xp_today": record.xp_today,
            "xp_this_week": record.xp_this_week,
            "xp_this_month": record.xp_this_month,
            "last_updated": record.last_updated.isoformat(),
        }
