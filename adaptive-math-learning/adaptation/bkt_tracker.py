"""
Bayesian Knowledge Tracing (BKT) Implementation.

Implements the classic BKT algorithm for tracking learner mastery
as specified in Corbett & Anderson (1994).

BKT Parameters:
- P(L₀): Prior Knowledge - Initial probability of mastery
- P(T): Learn Rate - Probability of learning after practice
- P(G): Guess Rate - Probability of correct answer without mastery
- P(S): Slip Rate - Probability of incorrect answer despite mastery
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import math


class DifficultyTier(int, Enum):
    """Difficulty tiers based on mastery level."""
    NOVICE = 1        # P(L) 0.00 - 0.20
    BEGINNER = 2      # P(L) 0.20 - 0.40
    INTERMEDIATE = 3  # P(L) 0.40 - 0.60
    ADVANCED = 4      # P(L) 0.60 - 0.80
    EXPERT = 5        # P(L) 0.80 - 1.00


@dataclass
class BKTParameters:
    """BKT model parameters for a skill."""
    P_L0: float = 0.1   # Prior Knowledge (initial mastery probability)
    P_T: float = 0.3    # Learn Rate (probability of learning after practice)
    P_G: float = 0.25   # Guess Rate (correct without mastery)
    P_S: float = 0.1    # Slip Rate (incorrect despite mastery)

    def validate(self) -> bool:
        """Validate BKT parameter constraints."""
        # All probabilities must be in [0, 1]
        for p in [self.P_L0, self.P_T, self.P_G, self.P_S]:
            if not 0 <= p <= 1:
                return False
        # Guess + Slip should be < 1 for identifiability
        if self.P_G + self.P_S >= 1:
            return False
        return True


@dataclass
class BKTRecord:
    """Tracks BKT mastery for a specific skill/topic."""
    skill_id: str
    topic_id: str
    subtopic_id: Optional[str] = None

    # Current mastery probability P(L)
    mastery: float = 0.1  # Starts at P(L0)

    # BKT parameters (can be skill-specific)
    params: BKTParameters = field(default_factory=BKTParameters)

    # Statistics
    attempts: int = 0
    correct: int = 0
    streak: int = 0
    best_streak: int = 0

    # History for analysis
    response_history: List[bool] = field(default_factory=list)
    mastery_history: List[float] = field(default_factory=list)

    # Metadata
    last_updated: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def accuracy(self) -> float:
        """Calculate overall accuracy."""
        if self.attempts == 0:
            return 0.0
        return self.correct / self.attempts

    @property
    def difficulty_tier(self) -> DifficultyTier:
        """Get difficulty tier based on mastery."""
        if self.mastery < 0.20:
            return DifficultyTier.NOVICE
        elif self.mastery < 0.40:
            return DifficultyTier.BEGINNER
        elif self.mastery < 0.60:
            return DifficultyTier.INTERMEDIATE
        elif self.mastery < 0.80:
            return DifficultyTier.ADVANCED
        else:
            return DifficultyTier.EXPERT

    @property
    def is_mastered(self) -> bool:
        """Check if skill is considered mastered (P(L) >= 0.95)."""
        return self.mastery >= 0.95


class BKTTracker:
    """
    Bayesian Knowledge Tracing (BKT) mastery tracker.

    The BKT model updates mastery probability P(L) after each response
    using Bayesian inference:

    If correct:
        P(L|correct) = P(L) * (1 - P(S)) / P(correct)
        where P(correct) = P(L) * (1 - P(S)) + (1 - P(L)) * P(G)

    If incorrect:
        P(L|incorrect) = P(L) * P(S) / P(incorrect)
        where P(incorrect) = P(L) * P(S) + (1 - P(L)) * (1 - P(G))

    After observation, apply learning:
        P(L_new) = P(L|observation) + (1 - P(L|observation)) * P(T)

    Reference:
        Corbett, A. T., & Anderson, J. R. (1994). Knowledge tracing:
        Modeling the acquisition of procedural knowledge. UMUAI, 4(4), 253-278.
    """

    # Default BKT parameters from the specification
    DEFAULT_P_L0 = 0.1   # Initial mastery probability
    DEFAULT_P_T = 0.3    # Learn rate
    DEFAULT_P_G = 0.25   # Guess rate
    DEFAULT_P_S = 0.1    # Slip rate

    MAX_HISTORY = 50

    def __init__(
        self,
        P_L0: float = DEFAULT_P_L0,
        P_T: float = DEFAULT_P_T,
        P_G: float = DEFAULT_P_G,
        P_S: float = DEFAULT_P_S,
    ):
        """
        Initialize BKT tracker with default parameters.

        Args:
            P_L0: Initial mastery probability
            P_T: Learn rate (probability of learning after practice)
            P_G: Guess rate (probability of correct without mastery)
            P_S: Slip rate (probability of incorrect despite mastery)
        """
        self.default_params = BKTParameters(
            P_L0=P_L0, P_T=P_T, P_G=P_G, P_S=P_S
        )

        if not self.default_params.validate():
            raise ValueError("Invalid BKT parameters")

        self._records: Dict[str, BKTRecord] = {}

    def get_mastery(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None
    ) -> float:
        """
        Get current mastery probability P(L) for a skill.

        Args:
            topic_id: The topic identifier
            subtopic_id: Optional subtopic identifier

        Returns:
            Mastery probability from 0.0 to 1.0
        """
        key = self._make_key(topic_id, subtopic_id)
        if key not in self._records:
            return self.default_params.P_L0
        return self._records[key].mastery

    def get_record(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None
    ) -> BKTRecord:
        """Get the full BKT record for a skill."""
        key = self._make_key(topic_id, subtopic_id)
        if key not in self._records:
            return BKTRecord(
                skill_id=key,
                topic_id=topic_id,
                subtopic_id=subtopic_id,
                mastery=self.default_params.P_L0,
                params=self.default_params,
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
        Update mastery using BKT algorithm after a response.

        The update follows the standard BKT formulas:
        1. Calculate posterior P(L|observation) using Bayes' rule
        2. Apply learning transition: P(L_new) = P(L|obs) + (1 - P(L|obs)) * P(T)

        Args:
            topic_id: The topic identifier
            is_correct: Whether the answer was correct
            subtopic_id: Optional subtopic identifier
            response_time_ms: Response time (not used in standard BKT)

        Returns:
            The new mastery probability
        """
        key = self._make_key(topic_id, subtopic_id)

        # Get or create record
        if key not in self._records:
            self._records[key] = BKTRecord(
                skill_id=key,
                topic_id=topic_id,
                subtopic_id=subtopic_id,
                mastery=self.default_params.P_L0,
                params=self.default_params,
            )

        record = self._records[key]
        params = record.params
        P_L = record.mastery

        # Step 1: Calculate posterior P(L|observation)
        if is_correct:
            # P(correct) = P(L) * (1 - P(S)) + (1 - P(L)) * P(G)
            P_correct = P_L * (1 - params.P_S) + (1 - P_L) * params.P_G

            # P(L|correct) = P(L) * (1 - P(S)) / P(correct)
            if P_correct > 0:
                P_L_given_obs = (P_L * (1 - params.P_S)) / P_correct
            else:
                P_L_given_obs = P_L
        else:
            # P(incorrect) = P(L) * P(S) + (1 - P(L)) * (1 - P(G))
            P_incorrect = P_L * params.P_S + (1 - P_L) * (1 - params.P_G)

            # P(L|incorrect) = P(L) * P(S) / P(incorrect)
            if P_incorrect > 0:
                P_L_given_obs = (P_L * params.P_S) / P_incorrect
            else:
                P_L_given_obs = P_L

        # Step 2: Apply learning transition
        # P(L_new) = P(L|obs) + (1 - P(L|obs)) * P(T)
        new_mastery = P_L_given_obs + (1 - P_L_given_obs) * params.P_T

        # Ensure bounds [0, 1]
        new_mastery = max(0.0, min(1.0, new_mastery))

        # Update record
        record.mastery = new_mastery
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
        record.response_history.append(is_correct)
        record.mastery_history.append(new_mastery)

        if len(record.response_history) > self.MAX_HISTORY:
            record.response_history = record.response_history[-self.MAX_HISTORY:]
            record.mastery_history = record.mastery_history[-self.MAX_HISTORY:]

        return new_mastery

    def get_difficulty_tier(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None
    ) -> DifficultyTier:
        """
        Get recommended difficulty tier based on mastery.

        Tier mapping (from specification):
        - Tier 1 (Novice): P(L) 0.00-0.20 - Small positive integers
        - Tier 2 (Beginner): P(L) 0.20-0.40 - Range 1-20, may include negatives
        - Tier 3 (Intermediate): P(L) 0.40-0.60 - Range -20 to 50, multi-step
        - Tier 4 (Advanced): P(L) 0.60-0.80 - Range -50 to 100, complex
        - Tier 5 (Expert): P(L) 0.80-1.00 - Full ranges, edge cases

        Returns:
            DifficultyTier enum value
        """
        return self.get_record(topic_id, subtopic_id).difficulty_tier

    def get_recommended_difficulty(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None
    ) -> float:
        """
        Get recommended difficulty as a float (0.0 to 1.0).

        Maps difficulty tier to a continuous value for compatibility
        with existing question generation.

        New users (no practice history) start at a moderate difficulty
        so they get a variety of operations, not just the easiest ones.
        """
        key = self._make_key(topic_id, subtopic_id)
        has_history = key in self._records and self._records[key].attempts > 0

        tier = self.get_difficulty_tier(topic_id, subtopic_id)
        mastery = self.get_mastery(topic_id, subtopic_id)

        # Map tier to base difficulty, then adjust within tier
        tier_ranges = {
            DifficultyTier.NOVICE: (0.0, 0.2),
            DifficultyTier.BEGINNER: (0.2, 0.4),
            DifficultyTier.INTERMEDIATE: (0.4, 0.6),
            DifficultyTier.ADVANCED: (0.6, 0.8),
            DifficultyTier.EXPERT: (0.8, 1.0),
        }

        low, high = tier_ranges[tier]
        # Position within tier based on mastery
        tier_mastery_low = (tier.value - 1) * 0.2
        tier_mastery_high = tier.value * 0.2

        if tier_mastery_high > tier_mastery_low:
            position = (mastery - tier_mastery_low) / (tier_mastery_high - tier_mastery_low)
        else:
            position = 0.5

        position = max(0, min(1, position))

        difficulty = low + position * (high - low)

        # For new users with no history, start at a moderate difficulty
        # so they get a variety of operations (not locked into addition-only)
        if not has_history:
            difficulty = max(difficulty, 0.3)

        return difficulty

    def predict_correct_probability(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None
    ) -> float:
        """
        Predict probability of correct response on next question.

        P(correct) = P(L) * (1 - P(S)) + (1 - P(L)) * P(G)
        """
        record = self.get_record(topic_id, subtopic_id)
        P_L = record.mastery
        params = record.params

        return P_L * (1 - params.P_S) + (1 - P_L) * params.P_G

    def estimate_questions_to_mastery(
        self,
        topic_id: str,
        subtopic_id: Optional[str] = None,
        target_mastery: float = 0.95,
        max_questions: int = 100,
    ) -> int:
        """
        Estimate number of questions needed to reach target mastery.

        Uses simulation assuming all correct answers.
        """
        record = self.get_record(topic_id, subtopic_id)
        params = record.params
        P_L = record.mastery

        questions = 0
        while P_L < target_mastery and questions < max_questions:
            # Simulate correct answer
            P_correct = P_L * (1 - params.P_S) + (1 - P_L) * params.P_G
            if P_correct > 0:
                P_L_given_correct = (P_L * (1 - params.P_S)) / P_correct
            else:
                P_L_given_correct = P_L
            P_L = P_L_given_correct + (1 - P_L_given_correct) * params.P_T
            questions += 1

        return questions

    def get_all_records(self) -> Dict[str, BKTRecord]:
        """Get all BKT records."""
        return self._records.copy()

    def reset(self, topic_id: str, subtopic_id: Optional[str] = None) -> None:
        """Reset mastery for a skill."""
        key = self._make_key(topic_id, subtopic_id)
        if key in self._records:
            del self._records[key]

    def reset_all(self) -> None:
        """Reset all mastery records."""
        self._records.clear()

    def _make_key(self, topic_id: str, subtopic_id: Optional[str]) -> str:
        """Create unique key for skill identification."""
        if subtopic_id:
            return f"{topic_id}:{subtopic_id}"
        return topic_id

    def to_dict(self) -> Dict:
        """Serialize tracker state for persistence."""
        return {
            "default_params": {
                "P_L0": self.default_params.P_L0,
                "P_T": self.default_params.P_T,
                "P_G": self.default_params.P_G,
                "P_S": self.default_params.P_S,
            },
            "records": {
                key: {
                    "skill_id": r.skill_id,
                    "topic_id": r.topic_id,
                    "subtopic_id": r.subtopic_id,
                    "mastery": r.mastery,
                    "params": {
                        "P_L0": r.params.P_L0,
                        "P_T": r.params.P_T,
                        "P_G": r.params.P_G,
                        "P_S": r.params.P_S,
                    },
                    "attempts": r.attempts,
                    "correct": r.correct,
                    "streak": r.streak,
                    "best_streak": r.best_streak,
                    "response_history": r.response_history[-20:],  # Last 20
                    "mastery_history": r.mastery_history[-20:],
                    "last_updated": r.last_updated.isoformat(),
                }
                for key, r in self._records.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "BKTTracker":
        """Deserialize tracker state from persistence."""
        params = data.get("default_params", {})
        tracker = cls(
            P_L0=params.get("P_L0", cls.DEFAULT_P_L0),
            P_T=params.get("P_T", cls.DEFAULT_P_T),
            P_G=params.get("P_G", cls.DEFAULT_P_G),
            P_S=params.get("P_S", cls.DEFAULT_P_S),
        )

        for key, record_data in data.get("records", {}).items():
            r_params = record_data.get("params", {})
            tracker._records[key] = BKTRecord(
                skill_id=record_data["skill_id"],
                topic_id=record_data["topic_id"],
                subtopic_id=record_data.get("subtopic_id"),
                mastery=record_data["mastery"],
                params=BKTParameters(
                    P_L0=r_params.get("P_L0", cls.DEFAULT_P_L0),
                    P_T=r_params.get("P_T", cls.DEFAULT_P_T),
                    P_G=r_params.get("P_G", cls.DEFAULT_P_G),
                    P_S=r_params.get("P_S", cls.DEFAULT_P_S),
                ),
                attempts=record_data["attempts"],
                correct=record_data["correct"],
                streak=record_data.get("streak", 0),
                best_streak=record_data.get("best_streak", 0),
                response_history=record_data.get("response_history", []),
                mastery_history=record_data.get("mastery_history", []),
                last_updated=datetime.fromisoformat(record_data["last_updated"]),
            )

        return tracker


# Backward compatibility alias
MasteryTracker = BKTTracker
