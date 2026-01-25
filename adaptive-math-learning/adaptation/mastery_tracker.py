"""
EMA-based Mastery Tracking System.

Implements Exponential Moving Average for tracking learner mastery
with noise-resistant score updates and difficulty mapping.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum


class MasteryLevel(str, Enum):
    """Human-readable mastery levels."""
    NOVICE = "Novice"
    BEGINNER = "Beginner"
    DEVELOPING = "Developing"
    PROFICIENT = "Proficient"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


@dataclass
class MasteryRecord:
    """Tracks mastery for a specific topic/skill."""
    topic_id: str
    subtopic_id: Optional[str] = None
    mastery_score: float = 0.5  # 0.0 to 1.0
    attempts: int = 0
    correct: int = 0
    streak: int = 0  # Current correct streak
    best_streak: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    history: List[float] = field(default_factory=list)  # Recent scores

    @property
    def accuracy(self) -> float:
        """Calculate overall accuracy."""
        if self.attempts == 0:
            return 0.0
        return self.correct / self.attempts

    @property
    def level(self) -> MasteryLevel:
        """Get human-readable mastery level."""
        if self.mastery_score < 0.15:
            return MasteryLevel.NOVICE
        elif self.mastery_score < 0.30:
            return MasteryLevel.BEGINNER
        elif self.mastery_score < 0.50:
            return MasteryLevel.DEVELOPING
        elif self.mastery_score < 0.70:
            return MasteryLevel.PROFICIENT
        elif self.mastery_score < 0.85:
            return MasteryLevel.ADVANCED
        else:
            return MasteryLevel.EXPERT


class MasteryTracker:
    """
    EMA-based mastery tracking system.

    Formula: mastery_new = α × performance + (1 - α) × mastery_old

    Where:
    - α (alpha) = 0.3 by default (configurable)
    - performance = 1.0 if correct, 0.0 if incorrect

    The EMA approach provides:
    - Noise resistance (single mistakes don't crash scores)
    - Recent performance weighting
    - Smooth difficulty transitions
    """

    DEFAULT_ALPHA = 0.3
    INITIAL_MASTERY = 0.5
    MAX_HISTORY = 20

    def __init__(self, alpha: float = DEFAULT_ALPHA):
        """
        Initialize mastery tracker.

        Args:
            alpha: EMA smoothing factor (0.0 to 1.0)
                   Higher = more responsive to recent performance
                   Lower = more stable, slower to change
        """
        if not 0.0 < alpha < 1.0:
            raise ValueError("Alpha must be between 0 and 1")

        self.alpha = alpha
        self._records: Dict[str, MasteryRecord] = {}

    def get_mastery(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None
    ) -> float:
        """
        Get current mastery score for a topic.

        Args:
            topic_id: The topic identifier
            subtopic_id: Optional subtopic identifier

        Returns:
            Mastery score from 0.0 to 1.0
        """
        key = self._make_key(topic_id, subtopic_id)
        if key not in self._records:
            return self.INITIAL_MASTERY
        return self._records[key].mastery_score

    def get_record(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None
    ) -> MasteryRecord:
        """Get the full mastery record for a topic."""
        key = self._make_key(topic_id, subtopic_id)
        if key not in self._records:
            return MasteryRecord(
                topic_id=topic_id,
                subtopic_id=subtopic_id,
                mastery_score=self.INITIAL_MASTERY,
            )
        return self._records[key]

    def update(
        self,
        topic_id: str,
        is_correct: bool,
        subtopic_id: Optional[str] = None,
        response_time_ms: Optional[int] = None,
    ) -> float:
        """
        Update mastery score based on latest response.

        Args:
            topic_id: The topic identifier
            is_correct: Whether the answer was correct
            subtopic_id: Optional subtopic identifier
            response_time_ms: Response time in milliseconds (optional)

        Returns:
            The new mastery score
        """
        key = self._make_key(topic_id, subtopic_id)

        # Get or create record
        if key not in self._records:
            self._records[key] = MasteryRecord(
                topic_id=topic_id,
                subtopic_id=subtopic_id,
                mastery_score=self.INITIAL_MASTERY,
            )

        record = self._records[key]

        # Calculate performance score
        performance = 1.0 if is_correct else 0.0

        # Optional: Factor in response time for fluency
        if response_time_ms is not None and is_correct:
            time_bonus = self._calculate_time_bonus(response_time_ms)
            performance = min(1.0, performance * time_bonus)

        # Apply EMA formula
        old_mastery = record.mastery_score
        new_mastery = self.alpha * performance + (1 - self.alpha) * old_mastery

        # Update record
        record.mastery_score = new_mastery
        record.attempts += 1
        record.correct += 1 if is_correct else 0
        record.last_updated = datetime.utcnow()

        # Update streak
        if is_correct:
            record.streak += 1
            record.best_streak = max(record.best_streak, record.streak)
        else:
            record.streak = 0

        # Update history
        record.history.append(performance)
        if len(record.history) > self.MAX_HISTORY:
            record.history = record.history[-self.MAX_HISTORY:]

        return new_mastery

    def get_recommended_difficulty(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None
    ) -> float:
        """
        Map mastery score to recommended question difficulty.

        The mapping ensures students are appropriately challenged:
        - Low mastery → Easy questions (build confidence)
        - Medium mastery → Medium questions (practice)
        - High mastery → Hard questions (challenge)

        With a slight offset to maintain engagement.

        Returns:
            Recommended difficulty from 0.0 to 1.0
        """
        mastery = self.get_mastery(topic_id, subtopic_id)

        # Piecewise linear mapping with challenge offset
        # Students should be slightly challenged (difficulty slightly above mastery)
        if mastery < 0.2:
            # Novice: very easy questions
            return 0.1 + (mastery / 0.2) * 0.15  # 0.1 - 0.25
        elif mastery < 0.4:
            # Beginner: easy questions
            return 0.25 + ((mastery - 0.2) / 0.2) * 0.15  # 0.25 - 0.4
        elif mastery < 0.6:
            # Developing: medium questions
            return 0.4 + ((mastery - 0.4) / 0.2) * 0.15  # 0.4 - 0.55
        elif mastery < 0.8:
            # Proficient: medium-hard questions
            return 0.55 + ((mastery - 0.6) / 0.2) * 0.15  # 0.55 - 0.7
        elif mastery < 0.9:
            # Advanced: hard questions
            return 0.7 + ((mastery - 0.8) / 0.1) * 0.15  # 0.7 - 0.85
        else:
            # Expert: very hard questions
            return 0.85 + ((mastery - 0.9) / 0.1) * 0.15  # 0.85 - 1.0

    def get_level(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None
    ) -> MasteryLevel:
        """Get human-readable mastery level."""
        return self.get_record(topic_id, subtopic_id).level

    def get_all_records(self) -> Dict[str, MasteryRecord]:
        """Get all mastery records."""
        return self._records.copy()

    def get_topic_summary(self, topic_id: str) -> Dict[str, any]:
        """Get summary statistics for a topic including all subtopics."""
        records = [r for k, r in self._records.items() if r.topic_id == topic_id]

        if not records:
            return {
                "topic_id": topic_id,
                "average_mastery": self.INITIAL_MASTERY,
                "total_attempts": 0,
                "total_correct": 0,
                "accuracy": 0.0,
                "subtopic_count": 0,
            }

        return {
            "topic_id": topic_id,
            "average_mastery": sum(r.mastery_score for r in records) / len(records),
            "total_attempts": sum(r.attempts for r in records),
            "total_correct": sum(r.correct for r in records),
            "accuracy": sum(r.correct for r in records) / max(1, sum(r.attempts for r in records)),
            "subtopic_count": len(records),
        }

    def reset(self, topic_id: str, subtopic_id: Optional[str] = None) -> None:
        """Reset mastery for a topic/subtopic."""
        key = self._make_key(topic_id, subtopic_id)
        if key in self._records:
            del self._records[key]

    def reset_all(self) -> None:
        """Reset all mastery records."""
        self._records.clear()

    # Helper methods

    def _make_key(self, topic_id: str, subtopic_id: Optional[str]) -> str:
        """Create unique key for topic/subtopic combination."""
        if subtopic_id:
            return f"{topic_id}:{subtopic_id}"
        return topic_id

    def _calculate_time_bonus(self, response_time_ms: int) -> float:
        """
        Calculate time-based performance bonus.

        Fast correct answers indicate higher fluency/mastery.

        Args:
            response_time_ms: Response time in milliseconds

        Returns:
            Multiplier from 0.8 to 1.1
        """
        # Thresholds in milliseconds
        FAST_THRESHOLD = 5000      # 5 seconds
        SLOW_THRESHOLD = 30000     # 30 seconds
        VERY_SLOW_THRESHOLD = 60000  # 60 seconds

        if response_time_ms < FAST_THRESHOLD:
            # Fast response: slight bonus
            bonus = 1.0 + (FAST_THRESHOLD - response_time_ms) / FAST_THRESHOLD * 0.1
            return min(1.1, bonus)
        elif response_time_ms < SLOW_THRESHOLD:
            # Normal response: no adjustment
            return 1.0
        elif response_time_ms < VERY_SLOW_THRESHOLD:
            # Slow response: slight penalty
            penalty = (response_time_ms - SLOW_THRESHOLD) / (VERY_SLOW_THRESHOLD - SLOW_THRESHOLD) * 0.1
            return max(0.9, 1.0 - penalty)
        else:
            # Very slow response: larger penalty
            return 0.8

    def to_dict(self) -> Dict[str, any]:
        """Serialize tracker state for persistence."""
        return {
            "alpha": self.alpha,
            "records": {
                key: {
                    "topic_id": r.topic_id,
                    "subtopic_id": r.subtopic_id,
                    "mastery_score": r.mastery_score,
                    "attempts": r.attempts,
                    "correct": r.correct,
                    "streak": r.streak,
                    "best_streak": r.best_streak,
                    "last_updated": r.last_updated.isoformat(),
                    "history": r.history,
                }
                for key, r in self._records.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "MasteryTracker":
        """Deserialize tracker state from persistence."""
        tracker = cls(alpha=data.get("alpha", cls.DEFAULT_ALPHA))

        for key, record_data in data.get("records", {}).items():
            tracker._records[key] = MasteryRecord(
                topic_id=record_data["topic_id"],
                subtopic_id=record_data.get("subtopic_id"),
                mastery_score=record_data["mastery_score"],
                attempts=record_data["attempts"],
                correct=record_data["correct"],
                streak=record_data.get("streak", 0),
                best_streak=record_data.get("best_streak", 0),
                last_updated=datetime.fromisoformat(record_data["last_updated"]),
                history=record_data.get("history", []),
            )

        return tracker


# Convenience function for difficulty mapping
def mastery_to_difficulty(mastery: float) -> float:
    """
    Direct function to map mastery to difficulty.

    Can be used without instantiating a full tracker.
    """
    tracker = MasteryTracker()
    tracker._records["temp"] = MasteryRecord(
        topic_id="temp",
        mastery_score=mastery,
    )
    return tracker.get_recommended_difficulty("temp")
