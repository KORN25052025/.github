"""
Difficulty Mapping and Parameter Adjustment.

Maps mastery scores to appropriate difficulty levels and
adjusts question parameters accordingly.
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional
from enum import Enum


class DifficultyZone(str, Enum):
    """Learning zones based on challenge level."""
    COMFORT = "comfort"       # Too easy - risk of boredom
    LEARNING = "learning"     # Optimal challenge - Vygotsky's ZPD
    STRUGGLE = "struggle"     # Too hard - risk of frustration


@dataclass
class DifficultyMapping:
    """Mapping result with difficulty and zone information."""
    difficulty: float
    zone: DifficultyZone
    adjustment_reason: str


class DifficultyMapper:
    """
    Maps mastery scores to appropriate difficulty levels.

    Based on the concept of Zone of Proximal Development (ZPD):
    - Questions should be slightly challenging but achievable
    - Too easy = boredom, too hard = frustration
    - Optimal = in the "learning zone"
    """

    # Difficulty offset to keep students slightly challenged
    CHALLENGE_OFFSET = 0.05

    # Zone boundaries (relative to mastery)
    COMFORT_THRESHOLD = -0.15  # Difficulty < mastery - 0.15
    STRUGGLE_THRESHOLD = 0.25  # Difficulty > mastery + 0.25

    def map(self, mastery: float, target_zone: Optional[DifficultyZone] = None) -> DifficultyMapping:
        """
        Map mastery score to difficulty.

        Args:
            mastery: Current mastery score (0.0 to 1.0)
            target_zone: Optional zone to target

        Returns:
            DifficultyMapping with difficulty and zone info
        """
        # Default: target the learning zone
        if target_zone is None or target_zone == DifficultyZone.LEARNING:
            # Slightly above mastery for optimal challenge
            difficulty = mastery + self.CHALLENGE_OFFSET
            adjustment_reason = "Targeting learning zone"

        elif target_zone == DifficultyZone.COMFORT:
            # Below mastery for confidence building
            difficulty = mastery - 0.1
            adjustment_reason = "Building confidence in comfort zone"

        elif target_zone == DifficultyZone.STRUGGLE:
            # Above mastery for pushing limits
            difficulty = mastery + 0.15
            adjustment_reason = "Challenging in struggle zone"

        # Clamp to valid range
        difficulty = max(0.0, min(1.0, difficulty))

        # Determine actual zone
        zone = self._determine_zone(mastery, difficulty)

        return DifficultyMapping(
            difficulty=difficulty,
            zone=zone,
            adjustment_reason=adjustment_reason,
        )

    def adjust_for_streak(
        self,
        base_difficulty: float,
        correct_streak: int,
        incorrect_streak: int = 0
    ) -> float:
        """
        Adjust difficulty based on recent performance streak.

        Args:
            base_difficulty: Base difficulty from mastery mapping
            correct_streak: Number of consecutive correct answers
            incorrect_streak: Number of consecutive incorrect answers

        Returns:
            Adjusted difficulty
        """
        if correct_streak >= 5:
            # Strong streak: increase challenge
            boost = min(0.15, correct_streak * 0.02)
            return min(1.0, base_difficulty + boost)

        elif correct_streak >= 3:
            # Moderate streak: slight increase
            return min(1.0, base_difficulty + 0.05)

        elif incorrect_streak >= 3:
            # Struggling: decrease difficulty
            reduction = min(0.15, incorrect_streak * 0.03)
            return max(0.0, base_difficulty - reduction)

        elif incorrect_streak >= 2:
            # Some struggle: slight decrease
            return max(0.0, base_difficulty - 0.05)

        return base_difficulty

    def get_parameter_ranges(
        self,
        difficulty: float,
        base_ranges: Dict[str, Tuple[int, int]]
    ) -> Dict[str, Tuple[int, int]]:
        """
        Adjust parameter ranges based on difficulty.

        Args:
            difficulty: Target difficulty (0.0 to 1.0)
            base_ranges: Base parameter ranges as {param: (min, max)}

        Returns:
            Adjusted parameter ranges
        """
        adjusted = {}

        for param, (base_min, base_max) in base_ranges.items():
            range_size = base_max - base_min

            # Scale range based on difficulty
            # Low difficulty = use lower portion of range
            # High difficulty = use upper portion of range
            scale_factor = 0.2 + (0.8 * difficulty)

            new_max = base_min + int(range_size * scale_factor)
            new_min = base_min + int((new_max - base_min) * difficulty * 0.3)

            # Ensure valid range
            new_min = max(base_min, new_min)
            new_max = max(new_min + 1, new_max)

            adjusted[param] = (new_min, new_max)

        return adjusted

    def _determine_zone(self, mastery: float, difficulty: float) -> DifficultyZone:
        """Determine which zone the difficulty falls into."""
        diff = difficulty - mastery

        if diff < self.COMFORT_THRESHOLD:
            return DifficultyZone.COMFORT
        elif diff > self.STRUGGLE_THRESHOLD:
            return DifficultyZone.STRUGGLE
        else:
            return DifficultyZone.LEARNING


class AdaptiveScheduler:
    """
    Schedules question difficulty progression over a learning session.

    Implements various progression strategies:
    - Warm-up: Start easy, gradually increase
    - Steady: Maintain consistent challenge
    - Push: Periodically increase challenge
    """

    def __init__(self, strategy: str = "warm_up"):
        """
        Initialize scheduler.

        Args:
            strategy: One of "warm_up", "steady", "push"
        """
        self.strategy = strategy
        self.question_count = 0
        self.correct_count = 0

    def get_next_difficulty(self, base_difficulty: float) -> float:
        """
        Get difficulty for next question based on strategy.

        Args:
            base_difficulty: Base difficulty from mastery

        Returns:
            Adjusted difficulty for next question
        """
        self.question_count += 1

        if self.strategy == "warm_up":
            return self._warm_up_progression(base_difficulty)
        elif self.strategy == "push":
            return self._push_progression(base_difficulty)
        else:  # steady
            return base_difficulty

    def record_response(self, is_correct: bool) -> None:
        """Record a response for progression tracking."""
        if is_correct:
            self.correct_count += 1

    def _warm_up_progression(self, base_difficulty: float) -> float:
        """Warm-up strategy: start easy, increase over first 5 questions."""
        if self.question_count <= 5:
            # Reduce difficulty for warm-up
            reduction = (5 - self.question_count) * 0.04
            return max(0.1, base_difficulty - reduction)
        return base_difficulty

    def _push_progression(self, base_difficulty: float) -> float:
        """Push strategy: increase difficulty every 5 correct answers."""
        push_count = self.correct_count // 5
        boost = min(0.2, push_count * 0.05)
        return min(1.0, base_difficulty + boost)

    def reset(self) -> None:
        """Reset session tracking."""
        self.question_count = 0
        self.correct_count = 0


# Global instances
difficulty_mapper = DifficultyMapper()
