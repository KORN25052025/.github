"""
Diagnostic Assessment Service.

Provides adaptive placement testing to determine a student's mastery level
across all 16 math topics. Uses a binary-search-style difficulty adjustment
algorithm to efficiently converge on each topic's mastery boundary.

Features:
- Adaptive question selection (binary search on difficulty)
- Per-topic mastery detection with confidence scoring
- Early termination when confidence thresholds are met
- Coverage of all 16 QuestionType topics (2-3 questions each)
- Minimum 15 / maximum 40 question bounds
- Grade-level-aware question generation

Turkish math curriculum alignment:
    Topics are ordered roughly by Turkish MEB curriculum progression,
    starting with arithmetic fundamentals and advancing through algebra,
    geometry, trigonometry, and formal logic.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from question_engine.base import (
    DifficultyTier,
    GeneratedQuestion,
    QuestionType,
)
from question_engine.registry import registry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_QUESTIONS: int = 15
MAX_QUESTIONS: int = 40

# Number of questions to ask per topic before moving on (2-3).
MIN_QUESTIONS_PER_TOPIC: int = 2
MAX_QUESTIONS_PER_TOPIC: int = 3

# Confidence threshold (0-1). When the estimated mastery confidence for a
# topic exceeds this value, we stop probing that topic.
CONFIDENCE_THRESHOLD: float = 0.85

# Global early-termination confidence: if *all* assessed topics exceed this
# confidence we may stop even before MAX_QUESTIONS (though we still enforce
# the minimum).
GLOBAL_CONFIDENCE_THRESHOLD: float = 0.90

# Difficulty bounds used by the binary-search algorithm.
DIFFICULTY_FLOOR: float = 0.05
DIFFICULTY_CEILING: float = 0.95

# Initial difficulty for a brand-new diagnostic (medium).
DEFAULT_INITIAL_DIFFICULTY: float = 0.50

# All topics in curriculum-progression order.
ALL_TOPICS: List[QuestionType] = [
    QuestionType.ARITHMETIC,
    QuestionType.FRACTIONS,
    QuestionType.PERCENTAGES,
    QuestionType.RATIOS,
    QuestionType.EXPONENTS,
    QuestionType.NUMBER_THEORY,
    QuestionType.ALGEBRA,
    QuestionType.INEQUALITIES,
    QuestionType.SYSTEMS_OF_EQUATIONS,
    QuestionType.POLYNOMIALS,
    QuestionType.FUNCTIONS,
    QuestionType.GEOMETRY,
    QuestionType.COORDINATE_GEOMETRY,
    QuestionType.TRIGONOMETRY,
    QuestionType.STATISTICS,
    QuestionType.SETS_AND_LOGIC,
]


class DiagnosticStatus(str, Enum):
    """Lifecycle states for a diagnostic session."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MasteryLevel(str, Enum):
    """Human-readable mastery designation derived from the raw score."""
    NOT_ASSESSED = "not_assessed"
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TopicAssessment:
    """Tracks the adaptive state for a single topic during a diagnostic."""

    topic: QuestionType

    # Binary-search bounds for difficulty.
    difficulty_low: float = DIFFICULTY_FLOOR
    difficulty_high: float = DIFFICULTY_CEILING

    # Current probe difficulty (midpoint of low/high).
    current_difficulty: float = DEFAULT_INITIAL_DIFFICULTY

    # Running tallies.
    questions_asked: int = 0
    questions_correct: int = 0

    # Per-question records: list of (question_id, difficulty, is_correct).
    history: List[Tuple[str, float, bool]] = field(default_factory=list)

    # Estimated mastery score (0-1) and confidence (0-1).
    mastery_score: float = 0.0
    confidence: float = 0.0

    # Whether we have gathered enough data for this topic.
    is_settled: bool = False

    # ---- Derived helpers ----

    @property
    def accuracy(self) -> float:
        """Raw accuracy ratio; 0.0 when no questions have been asked."""
        if self.questions_asked == 0:
            return 0.0
        return self.questions_correct / self.questions_asked

    @property
    def mastery_level(self) -> MasteryLevel:
        """Map the continuous mastery score to a discrete level."""
        if self.questions_asked == 0:
            return MasteryLevel.NOT_ASSESSED
        return _score_to_mastery_level(self.mastery_score)

    @property
    def recommended_difficulty(self) -> float:
        """
        Suggested starting difficulty for regular practice after placement.

        Slightly below the estimated mastery boundary so the student starts
        in their zone of proximal development.
        """
        return max(DIFFICULTY_FLOOR, self.mastery_score - 0.10)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API responses."""
        return {
            "topic": self.topic.value,
            "mastery_score": round(self.mastery_score, 3),
            "mastery_level": self.mastery_level.value,
            "confidence": round(self.confidence, 3),
            "questions_asked": self.questions_asked,
            "questions_correct": self.questions_correct,
            "accuracy": round(self.accuracy, 3),
            "recommended_difficulty": round(self.recommended_difficulty, 3),
            "is_settled": self.is_settled,
        }


@dataclass
class DiagnosticSession:
    """Full state of an in-progress or completed diagnostic assessment."""

    session_id: str
    user_id: str
    grade_level: int
    status: DiagnosticStatus = DiagnosticStatus.IN_PROGRESS

    # Per-topic adaptive state, keyed by QuestionType.
    topic_assessments: Dict[QuestionType, TopicAssessment] = field(
        default_factory=dict,
    )

    # Ordered queue of topics still to be assessed.
    topic_queue: List[QuestionType] = field(default_factory=list)

    # Index into topic_queue pointing at the topic currently being probed.
    current_topic_index: int = 0

    # Global question counter.
    total_questions_asked: int = 0

    # Map of question_id -> (QuestionType, difficulty) for answer look-up.
    pending_questions: Dict[str, Tuple[QuestionType, float]] = field(
        default_factory=dict,
    )

    # The most recently generated question (so callers can re-fetch it).
    current_question: Optional[GeneratedQuestion] = None

    # Timestamps.
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # ---- Derived helpers ----

    @property
    def current_topic(self) -> Optional[QuestionType]:
        """The topic currently being probed, or None if finished."""
        if self.current_topic_index < len(self.topic_queue):
            return self.topic_queue[self.current_topic_index]
        return None

    @property
    def progress_fraction(self) -> float:
        """Rough 0-1 progress indicator."""
        if MAX_QUESTIONS == 0:
            return 1.0
        return min(1.0, self.total_questions_asked / MAX_QUESTIONS)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API responses."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "grade_level": self.grade_level,
            "status": self.status.value,
            "total_questions_asked": self.total_questions_asked,
            "progress": round(self.progress_fraction, 3),
            "current_topic": (
                self.current_topic.value if self.current_topic else None
            ),
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


@dataclass
class PlacementResult:
    """Final output of a completed diagnostic assessment."""

    session_id: str
    user_id: str
    grade_level: int

    # Per-topic results.
    topic_results: Dict[QuestionType, TopicAssessment] = field(
        default_factory=dict,
    )

    # Aggregate metrics.
    overall_mastery: float = 0.0
    overall_accuracy: float = 0.0
    total_questions: int = 0
    total_correct: int = 0

    # Recommended starting difficulty per topic.
    recommended_difficulties: Dict[str, float] = field(default_factory=dict)

    # Suggested topics to focus on (lowest mastery first).
    focus_topics: List[str] = field(default_factory=list)

    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API responses."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "grade_level": self.grade_level,
            "overall_mastery": round(self.overall_mastery, 3),
            "overall_accuracy": round(self.overall_accuracy, 3),
            "total_questions": self.total_questions,
            "total_correct": self.total_correct,
            "recommended_difficulties": {
                k: round(v, 3) for k, v in self.recommended_difficulties.items()
            },
            "focus_topics": self.focus_topics,
            "topic_results": {
                qt.value: ta.to_dict()
                for qt, ta in self.topic_results.items()
            },
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _score_to_mastery_level(score: float) -> MasteryLevel:
    """Convert a 0-1 mastery score to a discrete MasteryLevel."""
    if score < 0.20:
        return MasteryLevel.NOVICE
    if score < 0.40:
        return MasteryLevel.BEGINNER
    if score < 0.60:
        return MasteryLevel.INTERMEDIATE
    if score < 0.80:
        return MasteryLevel.ADVANCED
    return MasteryLevel.EXPERT


def _score_to_difficulty_tier(score: float) -> DifficultyTier:
    """Convert a 0-1 score to the engine's DifficultyTier enum."""
    if score < 0.20:
        return DifficultyTier.NOVICE
    if score < 0.40:
        return DifficultyTier.BEGINNER
    if score < 0.60:
        return DifficultyTier.INTERMEDIATE
    if score < 0.80:
        return DifficultyTier.ADVANCED
    return DifficultyTier.EXPERT


def _topics_for_grade(grade_level: int) -> List[QuestionType]:
    """
    Return the subset of topics appropriate for a given grade level.

    Lower grades only see foundational topics; higher grades see all.
    This mirrors the Turkish MEB curriculum progression.
    """
    # Grades 1-4: core arithmetic
    core = [
        QuestionType.ARITHMETIC,
        QuestionType.FRACTIONS,
        QuestionType.PERCENTAGES,
        QuestionType.RATIOS,
    ]
    # Grades 5-6: add number-sense and basic geometry
    intermediate = core + [
        QuestionType.EXPONENTS,
        QuestionType.NUMBER_THEORY,
        QuestionType.GEOMETRY,
        QuestionType.STATISTICS,
    ]
    # Grades 7-8: pre-algebra, coordinate geometry
    pre_algebra = intermediate + [
        QuestionType.ALGEBRA,
        QuestionType.INEQUALITIES,
        QuestionType.COORDINATE_GEOMETRY,
    ]
    # Grades 9+: full curriculum
    full = list(ALL_TOPICS)  # all 16 topics

    if grade_level <= 4:
        return core
    if grade_level <= 6:
        return intermediate
    if grade_level <= 8:
        return pre_algebra
    return full


# ---------------------------------------------------------------------------
# DiagnosticService
# ---------------------------------------------------------------------------

class DiagnosticService:
    """
    Orchestrates adaptive diagnostic assessments.

    Usage::

        svc = DiagnosticService()
        session = svc.start_diagnostic(user_id="u1", grade_level=7)

        while True:
            question = svc.get_next_question(session.session_id)
            if question is None:
                break
            # ... present question to student, collect answer ...
            svc.submit_answer(session.session_id, question.question_id, answer)

        result = svc.complete_diagnostic(session.session_id)
    """

    def __init__(self) -> None:
        # In-memory session store.  In production this would be backed by a
        # database or cache (e.g. Redis), but the service layer itself stays
        # storage-agnostic.
        self._sessions: Dict[str, DiagnosticSession] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_diagnostic(
        self,
        user_id: str,
        grade_level: int,
    ) -> DiagnosticSession:
        """
        Begin a new diagnostic placement test for a user.

        Args:
            user_id: Unique identifier of the student.
            grade_level: The student's declared or estimated grade (1-12).

        Returns:
            A fresh DiagnosticSession ready for question delivery.

        Raises:
            ValueError: If *grade_level* is outside the 1-12 range.
        """
        if not 1 <= grade_level <= 12:
            raise ValueError(
                f"grade_level must be between 1 and 12, got {grade_level}"
            )

        session_id = self._generate_session_id()
        topics = _topics_for_grade(grade_level)

        # Pre-build a TopicAssessment for every topic in scope.
        topic_assessments: Dict[QuestionType, TopicAssessment] = {}
        for topic in topics:
            initial_diff = self._initial_difficulty_for_topic(topic, grade_level)
            topic_assessments[topic] = TopicAssessment(
                topic=topic,
                current_difficulty=initial_diff,
                difficulty_low=DIFFICULTY_FLOOR,
                difficulty_high=DIFFICULTY_CEILING,
            )

        session = DiagnosticSession(
            session_id=session_id,
            user_id=user_id,
            grade_level=grade_level,
            topic_assessments=topic_assessments,
            topic_queue=list(topics),
            current_topic_index=0,
        )

        self._sessions[session_id] = session
        logger.info(
            "Diagnostic started: session=%s user=%s grade=%d topics=%d",
            session_id,
            user_id,
            grade_level,
            len(topics),
        )
        return session

    def get_next_question(
        self,
        session_id: str,
    ) -> Optional[GeneratedQuestion]:
        """
        Select and return the next adaptive question for the session.

        The algorithm:
        1. Pick the current topic from the ordered queue.
        2. Generate a question at the topic's current probe difficulty.
        3. If the topic is settled or has reached its per-topic cap, advance
           to the next topic.
        4. Return None when the diagnostic is finished (all topics
           settled, or MAX_QUESTIONS reached, or early termination).

        Args:
            session_id: An active diagnostic session identifier.

        Returns:
            A GeneratedQuestion to present to the student, or None
            if the diagnostic is complete.

        Raises:
            KeyError: If *session_id* does not exist.
            RuntimeError: If the session has already been completed.
        """
        session = self._get_session(session_id)

        if session.status != DiagnosticStatus.IN_PROGRESS:
            raise RuntimeError(
                f"Diagnostic session {session_id} is not in progress "
                f"(status={session.status.value})"
            )

        # ---- Check global termination conditions ----
        if self._should_terminate(session):
            return None

        # ---- Find the next topic to probe ----
        topic = self._advance_to_next_topic(session)
        if topic is None:
            return None

        assessment = session.topic_assessments[topic]

        # ---- Generate a question at the current probe difficulty ----
        question = self._generate_question(
            topic=topic,
            difficulty=assessment.current_difficulty,
            grade_level=session.grade_level,
        )

        if question is None:
            # Generator unavailable for this topic; skip it.
            logger.warning(
                "No generator available for topic %s; skipping.", topic.value
            )
            assessment.is_settled = True
            return self.get_next_question(session_id)

        # Register the pending question so submit_answer can look it up.
        session.pending_questions[question.question_id] = (
            topic,
            assessment.current_difficulty,
        )
        session.current_question = question

        logger.debug(
            "Diagnostic question: session=%s topic=%s diff=%.2f qid=%s",
            session_id,
            topic.value,
            assessment.current_difficulty,
            question.question_id,
        )

        return question

    def submit_answer(
        self,
        session_id: str,
        question_id: str,
        answer: Any,
    ) -> Dict[str, Any]:
        """
        Record the student's answer and update the adaptive state.

        Args:
            session_id: Active diagnostic session identifier.
            question_id: The question_id of a previously delivered question.
            answer: The student's submitted answer (any format accepted by
                the question engine's answer comparison).

        Returns:
            A dict with is_correct, correct_answer, and the updated
            topic_assessment state.

        Raises:
            KeyError: If *session_id* or *question_id* is unknown.
            RuntimeError: If the session is not in progress.
        """
        session = self._get_session(session_id)

        if session.status != DiagnosticStatus.IN_PROGRESS:
            raise RuntimeError(
                f"Diagnostic session {session_id} is not in progress "
                f"(status={session.status.value})"
            )

        if question_id not in session.pending_questions:
            raise KeyError(
                f"Question {question_id} not found in session {session_id}. "
                "It may have already been answered or was never issued."
            )

        topic, difficulty = session.pending_questions.pop(question_id)
        assessment = session.topic_assessments[topic]

        # ---- Determine correctness ----
        is_correct = self._check_answer(session, question_id, answer)

        # ---- Update assessment state ----
        assessment.questions_asked += 1
        session.total_questions_asked += 1

        if is_correct:
            assessment.questions_correct += 1

        assessment.history.append((question_id, difficulty, is_correct))

        # ---- Adaptive difficulty adjustment (binary search) ----
        self._adjust_difficulty(assessment, is_correct)

        # ---- Recompute mastery estimate and confidence ----
        self._update_mastery_estimate(assessment)

        # ---- Check if this topic is settled ----
        if self._is_topic_settled(assessment):
            assessment.is_settled = True
            # Advance to the next unsettled topic.
            session.current_topic_index += 1

        logger.debug(
            "Answer recorded: session=%s qid=%s topic=%s correct=%s "
            "mastery=%.2f conf=%.2f",
            session_id,
            question_id,
            topic.value,
            is_correct,
            assessment.mastery_score,
            assessment.confidence,
        )

        return {
            "is_correct": is_correct,
            "correct_answer": self._get_correct_answer(session, question_id),
            "topic": topic.value,
            "topic_assessment": assessment.to_dict(),
            "total_questions_asked": session.total_questions_asked,
            "progress": round(session.progress_fraction, 3),
        }

    def complete_diagnostic(
        self,
        session_id: str,
    ) -> PlacementResult:
        """
        Finalize the diagnostic and compute placement results.

        This may be called explicitly by the caller, or implicitly when
        get_next_question returns None.  Calling it on an already-
        completed session simply returns the cached result.

        Args:
            session_id: The diagnostic session to finalize.

        Returns:
            A PlacementResult with per-topic mastery and recommendations.

        Raises:
            KeyError: If *session_id* does not exist.
        """
        session = self._get_session(session_id)

        if session.status == DiagnosticStatus.COMPLETED:
            # Idempotent: just rebuild the result object.
            return self._build_placement_result(session)

        session.status = DiagnosticStatus.COMPLETED
        session.completed_at = datetime.utcnow()

        # Ensure final mastery estimates are up to date for every topic.
        for assessment in session.topic_assessments.values():
            self._update_mastery_estimate(assessment)

        result = self._build_placement_result(session)

        logger.info(
            "Diagnostic completed: session=%s user=%s questions=%d "
            "overall_mastery=%.2f",
            session_id,
            session.user_id,
            session.total_questions_asked,
            result.overall_mastery,
        )

        return result

    def get_placement_result(
        self,
        session_id: str,
    ) -> PlacementResult:
        """
        Retrieve the placement result for a completed (or in-progress) session.

        If the session is still in progress, the returned result reflects the
        *current* estimated mastery.  Fields may change as more answers arrive.

        Args:
            session_id: The diagnostic session identifier.

        Returns:
            A PlacementResult snapshot.

        Raises:
            KeyError: If *session_id* does not exist.
        """
        session = self._get_session(session_id)
        return self._build_placement_result(session)

    def get_session(self, session_id: str) -> DiagnosticSession:
        """
        Public accessor for the raw session object.

        Useful for progress displays and debugging.

        Args:
            session_id: The diagnostic session identifier.

        Returns:
            The DiagnosticSession instance.

        Raises:
            KeyError: If *session_id* does not exist.
        """
        return self._get_session(session_id)

    # ------------------------------------------------------------------
    # Private helpers: session management
    # ------------------------------------------------------------------

    def _get_session(self, session_id: str) -> DiagnosticSession:
        """Look up a session or raise KeyError."""
        try:
            return self._sessions[session_id]
        except KeyError:
            raise KeyError(
                f"Diagnostic session '{session_id}' not found. "
                "It may have expired or never existed."
            )

    @staticmethod
    def _generate_session_id() -> str:
        """Produce a short, unique session identifier."""
        return f"diag-{uuid.uuid4().hex[:12]}"

    # ------------------------------------------------------------------
    # Private helpers: topic selection and termination
    # ------------------------------------------------------------------

    def _advance_to_next_topic(
        self,
        session: DiagnosticSession,
    ) -> Optional[QuestionType]:
        """
        Walk the topic queue to find the next topic that still needs probing.

        Returns the QuestionType to probe next, or None if all topics
        are settled (or the global question cap is hit).
        """
        queue = session.topic_queue
        start_index = session.current_topic_index

        # Scan forward from the current index, wrapping at most once.
        for offset in range(len(queue)):
            idx = (start_index + offset) % len(queue)
            topic = queue[idx]
            assessment = session.topic_assessments[topic]

            if not assessment.is_settled:
                session.current_topic_index = idx
                return topic

        # Every topic is settled.
        return None

    def _should_terminate(self, session: DiagnosticSession) -> bool:
        """
        Decide whether the diagnostic should end.

        Termination occurs when:
        - We have reached MAX_QUESTIONS.
        - All topics are settled AND we have asked at least MIN_QUESTIONS.
        - Global confidence is above threshold AND minimum met.
        """
        if session.total_questions_asked >= MAX_QUESTIONS:
            return True

        all_settled = all(
            a.is_settled for a in session.topic_assessments.values()
        )

        if all_settled and session.total_questions_asked >= MIN_QUESTIONS:
            return True

        # Early termination via global confidence.
        if session.total_questions_asked >= MIN_QUESTIONS:
            assessed = [
                a for a in session.topic_assessments.values()
                if a.questions_asked > 0
            ]
            if assessed and all(
                a.confidence >= GLOBAL_CONFIDENCE_THRESHOLD for a in assessed
            ):
                return True

        return False

    def _is_topic_settled(self, assessment: TopicAssessment) -> bool:
        """
        Decide whether we have enough data for this topic.

        A topic is settled when:
        - It has reached the per-topic maximum, OR
        - It has met the minimum AND confidence exceeds the threshold.
        """
        if assessment.questions_asked >= MAX_QUESTIONS_PER_TOPIC:
            return True

        if (
            assessment.questions_asked >= MIN_QUESTIONS_PER_TOPIC
            and assessment.confidence >= CONFIDENCE_THRESHOLD
        ):
            return True

        return False

    # ------------------------------------------------------------------
    # Private helpers: adaptive algorithm
    # ------------------------------------------------------------------

    @staticmethod
    def _initial_difficulty_for_topic(
        topic: QuestionType,
        grade_level: int,
    ) -> float:
        """
        Choose a sensible starting difficulty for a topic based on grade.

        Higher-grade students start higher within foundational topics and
        at medium for advanced topics.
        """
        # Topic intrinsic "curriculum position" (0 = earliest, 1 = latest).
        topic_order = {
            qt: i / max(1, len(ALL_TOPICS) - 1)
            for i, qt in enumerate(ALL_TOPICS)
        }
        position = topic_order.get(topic, 0.5)

        # Grade influence: higher grade -> can handle more difficulty.
        grade_factor = (grade_level - 1) / 11.0  # 0.0 for grade 1, 1.0 for grade 12

        # For early-curriculum topics a high-grade student starts harder;
        # for late-curriculum topics everyone starts near the middle.
        if position < 0.4:
            # Foundational topic: scale up with grade.
            initial = 0.30 + 0.40 * grade_factor
        elif position < 0.7:
            # Mid-curriculum topic.
            initial = 0.25 + 0.30 * grade_factor
        else:
            # Advanced topic: always start near medium.
            initial = 0.20 + 0.25 * grade_factor

        return max(DIFFICULTY_FLOOR, min(DIFFICULTY_CEILING, initial))

    @staticmethod
    def _adjust_difficulty(
        assessment: TopicAssessment,
        is_correct: bool,
    ) -> None:
        """
        Binary-search-style difficulty update.

        If the student answered correctly, the lower bound moves up
        (they can handle at least this difficulty).  If incorrect, the
        upper bound moves down (this difficulty is too hard).  The next
        probe difficulty is the midpoint of the updated interval.
        """
        current = assessment.current_difficulty

        if is_correct:
            # Student can handle *at least* this level.
            assessment.difficulty_low = max(assessment.difficulty_low, current)
        else:
            # This level is *at or above* the student's boundary.
            assessment.difficulty_high = min(assessment.difficulty_high, current)

        # New probe = midpoint.
        assessment.current_difficulty = (
            assessment.difficulty_low + assessment.difficulty_high
        ) / 2.0

    @staticmethod
    def _update_mastery_estimate(assessment: TopicAssessment) -> None:
        """
        Recompute estimated mastery score and confidence for a topic.

        Mastery estimate
        ~~~~~~~~~~~~~~~~
        We use the midpoint of the converged difficulty interval, weighted by
        accuracy.  Intuitively, if the binary-search interval has converged
        to [0.55, 0.65] and the student answered 2/3 questions correctly, the
        mastery estimate is around 0.60 * (2/3 blend).

        Confidence
        ~~~~~~~~~~
        Confidence increases with:
        - More questions answered (diminishing returns after 3).
        - A narrower difficulty interval (binary search has converged).
        """
        if assessment.questions_asked == 0:
            assessment.mastery_score = 0.0
            assessment.confidence = 0.0
            return

        # Interval midpoint is our best estimate of the mastery boundary.
        interval_mid = (
            assessment.difficulty_low + assessment.difficulty_high
        ) / 2.0
        interval_width = assessment.difficulty_high - assessment.difficulty_low

        # Accuracy adjustment: blend interval midpoint toward 0 for low
        # accuracy and toward 1 for perfect accuracy.
        accuracy = assessment.accuracy
        mastery = interval_mid * (0.5 + 0.5 * accuracy)

        # Clamp to valid range.
        assessment.mastery_score = max(0.0, min(1.0, mastery))

        # Confidence from question count (logistic-ish curve, plateaus ~3).
        count_confidence = min(1.0, assessment.questions_asked / 3.0)

        # Confidence from interval convergence.
        max_interval = DIFFICULTY_CEILING - DIFFICULTY_FLOOR
        convergence_confidence = 1.0 - (interval_width / max_interval)

        # Combined confidence (weighted average for a conservative estimate).
        assessment.confidence = (
            count_confidence * 0.4 + convergence_confidence * 0.6
        )

    # ------------------------------------------------------------------
    # Private helpers: question generation
    # ------------------------------------------------------------------

    def _generate_question(
        self,
        topic: QuestionType,
        difficulty: float,
        grade_level: int,
    ) -> Optional[GeneratedQuestion]:
        """
        Generate a single question via the question-engine registry.

        Returns None if no generator is registered for *topic*.
        """
        generator = registry.get(topic)
        if generator is None:
            logger.warning(
                "No generator registered for topic %s.", topic.value
            )
            return None

        try:
            question = generator.generate(
                difficulty=difficulty,
                grade_level=grade_level,
            )
            return question
        except Exception:
            logger.exception(
                "Question generation failed for topic=%s difficulty=%.2f",
                topic.value,
                difficulty,
            )
            return None

    # ------------------------------------------------------------------
    # Private helpers: answer checking
    # ------------------------------------------------------------------

    def _check_answer(
        self,
        session: DiagnosticSession,
        question_id: str,
        answer: Any,
    ) -> bool:
        """
        Compare the student's answer against the correct answer.

        Uses the current_question if the IDs match; otherwise falls back
        to a string comparison.  In a production deployment this would
        delegate to the AnswerValidator service.
        """
        question = session.current_question
        if question is not None and question.question_id == question_id:
            correct = question.correct_answer
            return self._answers_match(answer, correct)

        # Fallback: cannot validate without the original question data.
        logger.warning(
            "Could not locate correct answer for question %s; "
            "marking as incorrect by default.",
            question_id,
        )
        return False

    @staticmethod
    def _answers_match(user_answer: Any, correct_answer: Any) -> bool:
        """
        Flexible answer comparison supporting numeric and string answers.

        Handles int/float coercion and basic string normalization.
        """
        # Exact match shortcut.
        if user_answer == correct_answer:
            return True

        # Numeric comparison with tolerance.
        try:
            user_num = float(str(user_answer))
            correct_num = float(str(correct_answer))
            if abs(user_num - correct_num) < 1e-6:
                return True
            # Integer tolerance (handles "7" vs 7).
            if user_num == int(user_num) and correct_num == int(correct_num):
                return int(user_num) == int(correct_num)
        except (ValueError, TypeError, OverflowError):
            pass

        # Normalized string comparison.
        try:
            user_str = str(user_answer).strip().lower().replace(" ", "")
            correct_str = str(correct_answer).strip().lower().replace(" ", "")
            if user_str == correct_str:
                return True
        except (ValueError, TypeError):
            pass

        return False

    def _get_correct_answer(
        self,
        session: DiagnosticSession,
        question_id: str,
    ) -> Any:
        """Retrieve the correct answer for a previously issued question."""
        question = session.current_question
        if question is not None and question.question_id == question_id:
            return question.correct_answer
        return None

    # ------------------------------------------------------------------
    # Private helpers: result building
    # ------------------------------------------------------------------

    def _build_placement_result(
        self,
        session: DiagnosticSession,
    ) -> PlacementResult:
        """Assemble a PlacementResult from the current session state."""
        total_q = 0
        total_c = 0
        mastery_sum = 0.0
        assessed_count = 0

        recommended: Dict[str, float] = {}
        topic_results: Dict[QuestionType, TopicAssessment] = {}

        for qt, assessment in session.topic_assessments.items():
            topic_results[qt] = assessment
            total_q += assessment.questions_asked
            total_c += assessment.questions_correct
            recommended[qt.value] = round(assessment.recommended_difficulty, 3)

            if assessment.questions_asked > 0:
                mastery_sum += assessment.mastery_score
                assessed_count += 1

        overall_mastery = (
            mastery_sum / assessed_count if assessed_count > 0 else 0.0
        )
        overall_accuracy = total_c / total_q if total_q > 0 else 0.0

        # Focus topics: lowest mastery first, limited to assessed topics.
        focus = sorted(
            [
                (qt, a.mastery_score)
                for qt, a in session.topic_assessments.items()
                if a.questions_asked > 0
            ],
            key=lambda pair: pair[1],
        )
        focus_topics = [qt.value for qt, _ in focus if _ < 0.60]

        return PlacementResult(
            session_id=session.session_id,
            user_id=session.user_id,
            grade_level=session.grade_level,
            topic_results=topic_results,
            overall_mastery=overall_mastery,
            overall_accuracy=overall_accuracy,
            total_questions=total_q,
            total_correct=total_c,
            recommended_difficulties=recommended,
            focus_topics=focus_topics,
            completed_at=session.completed_at,
        )


# ---------------------------------------------------------------------------
# Module-level singleton (mirrors pattern used by other services)
# ---------------------------------------------------------------------------

diagnostic_service = DiagnosticService()
