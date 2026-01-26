"""
LGS / YKS Exam Preparation Service.

Provides structured exam preparation for Turkish national mathematics exams:
- LGS (Liselere Gecis Sinavi): 8th grade high school entrance exam
- TYT (Temel Yeterlilik Testi): University entrance basic proficiency test
- AYT (Alan Yeterlilik Testi): University entrance advanced field test

Features:
- Timed exam sessions with MEB curriculum topic weights
- Full-length mock exams matching official exam formats
- Detailed per-topic performance analysis
- Historical statistics and progress tracking
- Weighted question generation based on official exam distributions

MEB Curriculum Topic Weights (official distribution):
    LGS:  Sayilar %15, Cebir %20, Geometri %25, Veri-Olasilik %15, Olcme %15, Kesirler %10
    TYT:  Temel Matematik %30, Geometri %25, Sayilar %20, Cebir %15, Veri %10
    AYT:  Fonksiyonlar %20, Trigonometri %15, Analitik Geometri %15, Diziler %10,
           Limit-Turev-Integral %25, Sayilar %15
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import math
import random
import logging

from question_engine.base import QuestionType, GeneratedQuestion
from question_engine.registry import registry


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ExamType(str, Enum):
    """Turkish national exam types."""
    LGS = "lgs"   # Liselere Gecis Sinavi - 8th grade
    TYT = "tyt"   # Temel Yeterlilik Testi - university basic
    AYT = "ayt"   # Alan Yeterlilik Testi - university advanced


class ExamSessionStatus(str, Enum):
    """Status of an exam session."""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TopicWeight:
    """A single topic's weight inside an exam blueprint."""
    topic_slug: str
    topic_name_tr: str
    topic_name_en: str
    weight: float              # 0.0-1.0 (e.g. 0.25 = 25 %)
    question_type: QuestionType
    difficulty_range: tuple     # (min_difficulty, max_difficulty) 0.0-1.0


@dataclass
class ExamQuestion:
    """A question within an exam session, with metadata."""
    question_number: int
    generated_question: GeneratedQuestion
    topic_slug: str
    topic_name_tr: str
    user_answer: Optional[Any] = None
    is_correct: Optional[bool] = None
    answered_at: Optional[datetime] = None
    time_spent_seconds: Optional[float] = None


@dataclass
class ExamSession:
    """A complete exam session with timing and question state."""
    session_id: str
    user_id: str
    exam_type: ExamType
    session_type: str                    # "practice" | "mock"
    status: ExamSessionStatus
    questions: List[ExamQuestion]
    total_questions: int
    time_limit_minutes: int
    started_at: datetime
    expires_at: datetime
    completed_at: Optional[datetime] = None

    @property
    def remaining_seconds(self) -> float:
        """Seconds remaining before the session expires."""
        if self.status != ExamSessionStatus.ACTIVE:
            return 0.0
        remaining = (self.expires_at - datetime.utcnow()).total_seconds()
        return max(remaining, 0.0)

    @property
    def is_expired(self) -> bool:
        """Whether the session has exceeded its time limit."""
        return datetime.utcnow() > self.expires_at

    @property
    def answered_count(self) -> int:
        return sum(1 for q in self.questions if q.user_answer is not None)

    @property
    def correct_count(self) -> int:
        return sum(1 for q in self.questions if q.is_correct is True)

    @property
    def accuracy(self) -> float:
        answered = self.answered_count
        if answered == 0:
            return 0.0
        return self.correct_count / answered

    def to_dict(self) -> Dict[str, Any]:
        """Serialise session to a JSON-safe dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "exam_type": self.exam_type.value,
            "session_type": self.session_type,
            "status": self.status.value,
            "total_questions": self.total_questions,
            "answered_count": self.answered_count,
            "correct_count": self.correct_count,
            "accuracy": round(self.accuracy, 4),
            "time_limit_minutes": self.time_limit_minutes,
            "remaining_seconds": round(self.remaining_seconds, 1),
            "started_at": self.started_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "questions": [
                {
                    "question_number": q.question_number,
                    "topic_slug": q.topic_slug,
                    "topic_name_tr": q.topic_name_tr,
                    "question": q.generated_question.to_dict(),
                    "user_answer": q.user_answer,
                    "is_correct": q.is_correct,
                    "answered_at": q.answered_at.isoformat() if q.answered_at else None,
                    "time_spent_seconds": q.time_spent_seconds,
                }
                for q in self.questions
            ],
        }


@dataclass
class TopicResult:
    """Performance result for a single topic within an exam."""
    topic_slug: str
    topic_name_tr: str
    total_questions: int
    correct_answers: int
    accuracy: float
    average_time_seconds: float
    weight_in_exam: float


@dataclass
class ExamResult:
    """Detailed result analysis after an exam is evaluated."""
    session_id: str
    user_id: str
    exam_type: ExamType
    total_questions: int
    correct_answers: int
    wrong_answers: int
    unanswered: int
    raw_score: float               # correct / total
    net_score: float               # TYT/AYT: correct - wrong/4; LGS: correct/total
    weighted_score: float          # weighted by topic weights
    estimated_rank_percentile: Optional[float]
    time_used_seconds: float
    time_limit_seconds: float
    topic_results: List[TopicResult]
    strengths: List[str]           # topic slugs with >= 70 % accuracy
    weaknesses: List[str]          # topic slugs with < 50 % accuracy
    recommendations: List[str]     # actionable study recommendations (TR)
    evaluated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "exam_type": self.exam_type.value,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "wrong_answers": self.wrong_answers,
            "unanswered": self.unanswered,
            "raw_score": round(self.raw_score, 4),
            "net_score": round(self.net_score, 4),
            "weighted_score": round(self.weighted_score, 4),
            "estimated_rank_percentile": (
                round(self.estimated_rank_percentile, 2)
                if self.estimated_rank_percentile is not None
                else None
            ),
            "time_used_seconds": round(self.time_used_seconds, 1),
            "time_limit_seconds": self.time_limit_seconds,
            "topic_results": [
                {
                    "topic_slug": tr.topic_slug,
                    "topic_name_tr": tr.topic_name_tr,
                    "total_questions": tr.total_questions,
                    "correct_answers": tr.correct_answers,
                    "accuracy": round(tr.accuracy, 4),
                    "average_time_seconds": round(tr.average_time_seconds, 1),
                    "weight_in_exam": tr.weight_in_exam,
                }
                for tr in self.topic_results
            ],
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "evaluated_at": self.evaluated_at.isoformat(),
        }


@dataclass
class ExamStatistics:
    """Aggregated exam statistics for a user and exam type."""
    user_id: str
    exam_type: ExamType
    total_sessions: int
    total_questions_answered: int
    overall_accuracy: float
    average_net_score: float
    best_net_score: float
    average_time_per_question_seconds: float
    topic_accuracy: Dict[str, float]
    score_trend: List[float]
    last_session_at: Optional[datetime]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "exam_type": self.exam_type.value,
            "total_sessions": self.total_sessions,
            "total_questions_answered": self.total_questions_answered,
            "overall_accuracy": round(self.overall_accuracy, 4),
            "average_net_score": round(self.average_net_score, 4),
            "best_net_score": round(self.best_net_score, 4),
            "average_time_per_question_seconds": round(
                self.average_time_per_question_seconds, 1
            ),
            "topic_accuracy": {
                k: round(v, 4) for k, v in self.topic_accuracy.items()
            },
            "score_trend": [round(s, 4) for s in self.score_trend],
            "last_session_at": (
                self.last_session_at.isoformat() if self.last_session_at else None
            ),
        }


# ---------------------------------------------------------------------------
# MEB Curriculum Topic Weight Definitions
# ---------------------------------------------------------------------------

_LGS_TOPIC_WEIGHTS: List[TopicWeight] = [
    TopicWeight(
        topic_slug="sayilar",
        topic_name_tr="Sayilar",
        topic_name_en="Numbers",
        weight=0.15,
        question_type=QuestionType.ARITHMETIC,
        difficulty_range=(0.3, 0.7),
    ),
    TopicWeight(
        topic_slug="cebir",
        topic_name_tr="Cebir",
        topic_name_en="Algebra",
        weight=0.20,
        question_type=QuestionType.ALGEBRA,
        difficulty_range=(0.3, 0.8),
    ),
    TopicWeight(
        topic_slug="geometri",
        topic_name_tr="Geometri",
        topic_name_en="Geometry",
        weight=0.25,
        question_type=QuestionType.GEOMETRY,
        difficulty_range=(0.3, 0.8),
    ),
    TopicWeight(
        topic_slug="veri_olasilik",
        topic_name_tr="Veri-Olasilik",
        topic_name_en="Data & Probability",
        weight=0.15,
        question_type=QuestionType.STATISTICS,
        difficulty_range=(0.2, 0.7),
    ),
    TopicWeight(
        topic_slug="olcme",
        topic_name_tr="Olcme",
        topic_name_en="Measurement",
        weight=0.15,
        question_type=QuestionType.GEOMETRY,
        difficulty_range=(0.2, 0.6),
    ),
    TopicWeight(
        topic_slug="kesirler",
        topic_name_tr="Kesirler",
        topic_name_en="Fractions",
        weight=0.10,
        question_type=QuestionType.FRACTIONS,
        difficulty_range=(0.2, 0.7),
    ),
]

_TYT_TOPIC_WEIGHTS: List[TopicWeight] = [
    TopicWeight(
        topic_slug="temel_matematik",
        topic_name_tr="Temel Matematik",
        topic_name_en="Basic Mathematics",
        weight=0.30,
        question_type=QuestionType.ARITHMETIC,
        difficulty_range=(0.3, 0.7),
    ),
    TopicWeight(
        topic_slug="geometri",
        topic_name_tr="Geometri",
        topic_name_en="Geometry",
        weight=0.25,
        question_type=QuestionType.GEOMETRY,
        difficulty_range=(0.3, 0.8),
    ),
    TopicWeight(
        topic_slug="sayilar",
        topic_name_tr="Sayilar",
        topic_name_en="Numbers",
        weight=0.20,
        question_type=QuestionType.NUMBER_THEORY,
        difficulty_range=(0.3, 0.7),
    ),
    TopicWeight(
        topic_slug="cebir",
        topic_name_tr="Cebir",
        topic_name_en="Algebra",
        weight=0.15,
        question_type=QuestionType.ALGEBRA,
        difficulty_range=(0.4, 0.8),
    ),
    TopicWeight(
        topic_slug="veri",
        topic_name_tr="Veri",
        topic_name_en="Data Analysis",
        weight=0.10,
        question_type=QuestionType.STATISTICS,
        difficulty_range=(0.3, 0.7),
    ),
]

_AYT_TOPIC_WEIGHTS: List[TopicWeight] = [
    TopicWeight(
        topic_slug="fonksiyonlar",
        topic_name_tr="Fonksiyonlar",
        topic_name_en="Functions",
        weight=0.20,
        question_type=QuestionType.FUNCTIONS,
        difficulty_range=(0.5, 0.9),
    ),
    TopicWeight(
        topic_slug="trigonometri",
        topic_name_tr="Trigonometri",
        topic_name_en="Trigonometry",
        weight=0.15,
        question_type=QuestionType.TRIGONOMETRY,
        difficulty_range=(0.5, 0.9),
    ),
    TopicWeight(
        topic_slug="analitik_geometri",
        topic_name_tr="Analitik Geometri",
        topic_name_en="Analytic Geometry",
        weight=0.15,
        question_type=QuestionType.COORDINATE_GEOMETRY,
        difficulty_range=(0.5, 0.9),
    ),
    TopicWeight(
        topic_slug="diziler",
        topic_name_tr="Diziler",
        topic_name_en="Sequences",
        weight=0.10,
        question_type=QuestionType.ALGEBRA,
        difficulty_range=(0.5, 0.9),
    ),
    TopicWeight(
        topic_slug="limit_turev_integral",
        topic_name_tr="Limit-Turev-Integral",
        topic_name_en="Limit-Derivative-Integral",
        weight=0.25,
        question_type=QuestionType.POLYNOMIALS,
        difficulty_range=(0.6, 1.0),
    ),
    TopicWeight(
        topic_slug="sayilar",
        topic_name_tr="Sayilar",
        topic_name_en="Numbers",
        weight=0.15,
        question_type=QuestionType.NUMBER_THEORY,
        difficulty_range=(0.4, 0.8),
    ),
]

_TOPIC_WEIGHTS_MAP: Dict[ExamType, List[TopicWeight]] = {
    ExamType.LGS: _LGS_TOPIC_WEIGHTS,
    ExamType.TYT: _TYT_TOPIC_WEIGHTS,
    ExamType.AYT: _AYT_TOPIC_WEIGHTS,
}

# Official exam specifications
_EXAM_SPECS: Dict[ExamType, Dict[str, int]] = {
    ExamType.LGS: {"question_count": 20, "time_limit_minutes": 40},
    ExamType.TYT: {"question_count": 40, "time_limit_minutes": 75},
    ExamType.AYT: {"question_count": 40, "time_limit_minutes": 75},
}


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ExamPrepService:
    """
    Exam preparation service for LGS, TYT and AYT exams.

    Handles the full lifecycle of exam practice:
    1. Session creation with weighted question generation
    2. Timed exam execution with remaining-time tracking
    3. Answer evaluation with net-score calculation
    4. Detailed per-topic result analysis
    5. Historical statistics and trend tracking

    Usage::

        service = ExamPrepService()
        session = service.generate_exam_session(user_id="u1", exam_type=ExamType.LGS)
        result  = service.evaluate_exam(session.session_id, answers={1: "42", 2: "7"})
        stats   = service.get_exam_statistics(user_id="u1", exam_type=ExamType.LGS)
    """

    # In-memory stores (replace with DB in production deployment)
    _sessions: Dict[str, ExamSession] = {}
    _results: Dict[str, ExamResult] = {}
    _user_results: Dict[str, List[ExamResult]] = {}

    def __init__(self, db: Any = None) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_exam_session(
        self,
        user_id: str,
        exam_type: ExamType,
        topic_slug: Optional[str] = None,
        question_count: int = 20,
    ) -> ExamSession:
        """
        Create a timed exam practice session.

        When *topic_slug* is provided the session focuses exclusively on that
        topic; otherwise questions are distributed across topics according to
        the official MEB curriculum weights for the chosen exam type.

        Args:
            user_id: Unique identifier of the student.
            exam_type: One of LGS, TYT, AYT.
            topic_slug: Optional slug to restrict questions to a single topic.
            question_count: Number of questions (default 20).

        Returns:
            A fully populated ``ExamSession`` ready for the student.
        """
        topic_weights = self.get_topic_weights(exam_type)

        # Time limit: scale proportionally from the official mock-exam spec
        spec = _EXAM_SPECS[exam_type]
        time_limit_minutes = max(
            5,
            int(spec["time_limit_minutes"] * question_count / spec["question_count"]),
        )

        # Determine per-topic question counts
        if topic_slug is not None:
            topic_distribution = self._build_single_topic_distribution(
                topic_slug, topic_weights, question_count,
            )
        else:
            topic_distribution = self._build_weighted_distribution(
                topic_weights, question_count,
            )

        # Generate questions
        questions = self._generate_questions(topic_distribution, exam_type)

        now = datetime.utcnow()
        session = ExamSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            exam_type=exam_type,
            session_type="practice",
            status=ExamSessionStatus.ACTIVE,
            questions=questions,
            total_questions=len(questions),
            time_limit_minutes=time_limit_minutes,
            started_at=now,
            expires_at=now + timedelta(minutes=time_limit_minutes),
        )

        self._sessions[session.session_id] = session
        logger.info(
            "Created exam session %s for user %s (%s, %d questions, %d min)",
            session.session_id, user_id, exam_type.value,
            len(questions), time_limit_minutes,
        )
        return session

    def generate_mock_exam(
        self,
        user_id: str,
        exam_type: ExamType,
    ) -> ExamSession:
        """
        Generate a full-length mock exam matching the official format.

        Official specifications:
        - LGS:  20 math questions, 40 minutes
        - TYT:  40 questions, 75 minutes
        - AYT:  40 questions, 75 minutes

        Topic distribution mirrors the MEB curriculum weights exactly.

        Args:
            user_id: Unique identifier of the student.
            exam_type: One of LGS, TYT, AYT.

        Returns:
            A timed ``ExamSession`` representing the full mock exam.
        """
        spec = _EXAM_SPECS[exam_type]
        topic_weights = self.get_topic_weights(exam_type)

        topic_distribution = self._build_weighted_distribution(
            topic_weights, spec["question_count"],
        )
        questions = self._generate_questions(topic_distribution, exam_type)

        now = datetime.utcnow()
        session = ExamSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            exam_type=exam_type,
            session_type="mock",
            status=ExamSessionStatus.ACTIVE,
            questions=questions,
            total_questions=len(questions),
            time_limit_minutes=spec["time_limit_minutes"],
            started_at=now,
            expires_at=now + timedelta(minutes=spec["time_limit_minutes"]),
        )

        self._sessions[session.session_id] = session
        logger.info(
            "Created mock exam %s for user %s (%s, %d questions, %d min)",
            session.session_id, user_id, exam_type.value,
            session.total_questions, session.time_limit_minutes,
        )
        return session

    def get_exam_statistics(
        self,
        user_id: str,
        exam_type: ExamType,
    ) -> ExamStatistics:
        """
        Return aggregated performance statistics for a user and exam type.

        Statistics include overall accuracy, net score trend, per-topic
        accuracy breakdown, and average time per question.

        Args:
            user_id: Unique identifier of the student.
            exam_type: One of LGS, TYT, AYT.

        Returns:
            An ``ExamStatistics`` instance with aggregated data.
        """
        key = f"{user_id}:{exam_type.value}"
        results: List[ExamResult] = self._user_results.get(key, [])

        if not results:
            topic_weights = self.get_topic_weights(exam_type)
            return ExamStatistics(
                user_id=user_id,
                exam_type=exam_type,
                total_sessions=0,
                total_questions_answered=0,
                overall_accuracy=0.0,
                average_net_score=0.0,
                best_net_score=0.0,
                average_time_per_question_seconds=0.0,
                topic_accuracy={tw.topic_slug: 0.0 for tw in topic_weights},
                score_trend=[],
                last_session_at=None,
            )

        total_correct = sum(r.correct_answers for r in results)
        total_answered = sum(
            r.correct_answers + r.wrong_answers for r in results
        )
        total_questions = sum(r.total_questions for r in results)
        overall_accuracy = (
            total_correct / total_answered if total_answered else 0.0
        )

        net_scores = [r.net_score for r in results]
        avg_net = sum(net_scores) / len(net_scores) if net_scores else 0.0
        best_net = max(net_scores) if net_scores else 0.0

        # Per-topic accuracy aggregation
        topic_correct: Dict[str, int] = {}
        topic_total: Dict[str, int] = {}
        for result in results:
            for tr in result.topic_results:
                topic_correct[tr.topic_slug] = (
                    topic_correct.get(tr.topic_slug, 0) + tr.correct_answers
                )
                topic_total[tr.topic_slug] = (
                    topic_total.get(tr.topic_slug, 0) + tr.total_questions
                )
        topic_accuracy = {
            slug: (
                topic_correct[slug] / topic_total[slug]
                if topic_total[slug] else 0.0
            )
            for slug in topic_total
        }

        # Average time per question
        total_time = sum(r.time_used_seconds for r in results)
        avg_time = total_time / total_questions if total_questions else 0.0

        # Score trend (last 20 sessions)
        score_trend = net_scores[-20:]

        return ExamStatistics(
            user_id=user_id,
            exam_type=exam_type,
            total_sessions=len(results),
            total_questions_answered=total_answered,
            overall_accuracy=overall_accuracy,
            average_net_score=avg_net,
            best_net_score=best_net,
            average_time_per_question_seconds=avg_time,
            topic_accuracy=topic_accuracy,
            score_trend=score_trend,
            last_session_at=results[-1].evaluated_at if results else None,
        )

    @staticmethod
    def get_topic_weights(exam_type: ExamType) -> List[TopicWeight]:
        """
        Return the official MEB curriculum topic weights for an exam type.

        The weights sum to 1.0 and represent the percentage of questions
        that should come from each topic in a balanced exam.

        Args:
            exam_type: One of LGS, TYT, AYT.

        Returns:
            List of ``TopicWeight`` instances.

        Raises:
            ValueError: If the exam type is unknown.
        """
        weights = _TOPIC_WEIGHTS_MAP.get(exam_type)
        if weights is None:
            raise ValueError(f"Unknown exam type: {exam_type}")
        return list(weights)

    def evaluate_exam(
        self,
        session_id: str,
        answers: Dict[int, Any],
    ) -> ExamResult:
        """
        Score an exam session and produce a detailed result analysis.

        Scoring rules:
        - LGS: Raw score = correct / total (no negative marking)
        - TYT / AYT: Net score = correct - (wrong / 4)  (OSYM standard)

        The method also computes a weighted score by multiplying each
        topic's accuracy by its curriculum weight, providing a curriculum-
        aligned performance metric.

        Args:
            session_id: ID of the exam session to evaluate.
            answers: Mapping of ``question_number`` (1-based) to the
                     student's answer value.

        Returns:
            A fully populated ``ExamResult`` with per-topic breakdown.

        Raises:
            ValueError: If the session ID is unknown or already evaluated.
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Exam session not found: {session_id}")
        if session.status == ExamSessionStatus.COMPLETED:
            existing = self._results.get(session_id)
            if existing is not None:
                return existing
            raise ValueError(
                f"Session {session_id} already completed but result missing"
            )

        # Mark the session as expired if time ran out
        if session.is_expired:
            session.status = ExamSessionStatus.EXPIRED

        now = datetime.utcnow()

        # Apply answers
        for question in session.questions:
            qnum = question.question_number
            if qnum in answers:
                question.user_answer = answers[qnum]
                question.answered_at = now
                question.is_correct = self._check_answer(
                    question.generated_question, answers[qnum],
                )
                # Estimate time spent (evenly distributed as approximation)
                elapsed = (now - session.started_at).total_seconds()
                question.time_spent_seconds = elapsed / max(len(answers), 1)

        # Mark session completed
        session.status = ExamSessionStatus.COMPLETED
        session.completed_at = now

        # Tally scores
        correct = sum(1 for q in session.questions if q.is_correct is True)
        wrong = sum(
            1 for q in session.questions
            if q.is_correct is False and q.user_answer is not None
        )
        unanswered = sum(
            1 for q in session.questions if q.user_answer is None
        )

        raw_score = (
            correct / session.total_questions
            if session.total_questions else 0.0
        )

        # Net score calculation
        if session.exam_type == ExamType.LGS:
            net_score = raw_score  # LGS: no negative marking
        else:
            # TYT and AYT: net = correct - wrong/4  (OSYM formula)
            net_score = correct - (wrong / 4.0)

        # Per-topic breakdown
        topic_weights = self.get_topic_weights(session.exam_type)
        topic_weight_map = {tw.topic_slug: tw.weight for tw in topic_weights}
        topic_name_map = {
            tw.topic_slug: tw.topic_name_tr for tw in topic_weights
        }

        topic_questions: Dict[str, List[ExamQuestion]] = {}
        for q in session.questions:
            topic_questions.setdefault(q.topic_slug, []).append(q)

        topic_results: List[TopicResult] = []
        weighted_score = 0.0
        strengths: List[str] = []
        weaknesses: List[str] = []

        for slug, qs in topic_questions.items():
            t_total = len(qs)
            t_correct = sum(1 for q in qs if q.is_correct is True)
            t_accuracy = t_correct / t_total if t_total else 0.0
            t_times = [
                q.time_spent_seconds for q in qs
                if q.time_spent_seconds is not None
            ]
            t_avg_time = sum(t_times) / len(t_times) if t_times else 0.0
            t_weight = topic_weight_map.get(slug, 0.0)

            topic_results.append(TopicResult(
                topic_slug=slug,
                topic_name_tr=topic_name_map.get(slug, slug),
                total_questions=t_total,
                correct_answers=t_correct,
                accuracy=t_accuracy,
                average_time_seconds=t_avg_time,
                weight_in_exam=t_weight,
            ))

            weighted_score += t_accuracy * t_weight

            if t_accuracy >= 0.70:
                strengths.append(slug)
            elif t_accuracy < 0.50:
                weaknesses.append(slug)

        # Sort topic results by weight descending
        topic_results.sort(key=lambda tr: tr.weight_in_exam, reverse=True)

        # Rough percentile estimate based on net score
        estimated_percentile = self._estimate_percentile(
            session.exam_type, net_score, session.total_questions,
        )

        # Recommendations
        recommendations = self._generate_recommendations(
            session.exam_type, topic_results, weaknesses,
        )

        time_used = (now - session.started_at).total_seconds()
        time_limit = session.time_limit_minutes * 60.0

        result = ExamResult(
            session_id=session_id,
            user_id=session.user_id,
            exam_type=session.exam_type,
            total_questions=session.total_questions,
            correct_answers=correct,
            wrong_answers=wrong,
            unanswered=unanswered,
            raw_score=raw_score,
            net_score=net_score,
            weighted_score=weighted_score,
            estimated_rank_percentile=estimated_percentile,
            time_used_seconds=min(time_used, time_limit),
            time_limit_seconds=time_limit,
            topic_results=topic_results,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )

        # Persist result
        self._results[session_id] = result
        user_key = f"{session.user_id}:{session.exam_type.value}"
        self._user_results.setdefault(user_key, []).append(result)

        logger.info(
            "Evaluated exam %s: %d/%d correct, net=%.2f, weighted=%.4f",
            session_id, correct, session.total_questions,
            net_score, weighted_score,
        )
        return result

    # ------------------------------------------------------------------
    # Session management helpers
    # ------------------------------------------------------------------

    def get_session(self, session_id: str) -> Optional[ExamSession]:
        """Retrieve an exam session by ID, updating expired status."""
        session = self._sessions.get(session_id)
        if session is not None and session.status == ExamSessionStatus.ACTIVE:
            if session.is_expired:
                session.status = ExamSessionStatus.EXPIRED
        return session

    def abandon_session(self, session_id: str) -> None:
        """Mark a session as abandoned by the student."""
        session = self._sessions.get(session_id)
        if session is not None and session.status == ExamSessionStatus.ACTIVE:
            session.status = ExamSessionStatus.ABANDONED
            session.completed_at = datetime.utcnow()

    def get_remaining_time(self, session_id: str) -> float:
        """Return remaining seconds for an active session, or 0.0."""
        session = self._sessions.get(session_id)
        if session is None:
            return 0.0
        return session.remaining_seconds

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_weighted_distribution(
        topic_weights: List[TopicWeight],
        total_questions: int,
    ) -> List[tuple]:
        """
        Distribute *total_questions* across topics proportional to weights.

        Returns a list of ``(TopicWeight, count)`` tuples whose counts sum
        to exactly *total_questions*.  Rounding residuals are distributed
        using the largest-remainder method.
        """
        raw_counts = [
            (tw, tw.weight * total_questions) for tw in topic_weights
        ]
        floor_counts = [
            (tw, int(math.floor(count))) for tw, count in raw_counts
        ]
        remainders = [
            (tw, count - int(math.floor(count)))
            for tw, count in raw_counts
        ]
        allocated = sum(c for _, c in floor_counts)
        deficit = total_questions - allocated

        # Largest-remainder allocation for rounding residuals
        remainders.sort(key=lambda x: x[1], reverse=True)
        extra_slugs = {r[0].topic_slug for r in remainders[:deficit]}

        distribution: List[tuple] = []
        for tw, count in floor_counts:
            final_count = count + (
                1 if tw.topic_slug in extra_slugs else 0
            )
            if final_count > 0:
                distribution.append((tw, final_count))

        return distribution

    @staticmethod
    def _build_single_topic_distribution(
        topic_slug: str,
        topic_weights: List[TopicWeight],
        total_questions: int,
    ) -> List[tuple]:
        """Build a distribution focused on a single topic."""
        matching = [
            tw for tw in topic_weights if tw.topic_slug == topic_slug
        ]
        if not matching:
            logger.warning(
                "Topic '%s' not found in exam weights; "
                "falling back to first topic",
                topic_slug,
            )
            matching = [topic_weights[0]]
        return [(matching[0], total_questions)]

    def _generate_questions(
        self,
        topic_distribution: List[tuple],
        exam_type: ExamType,
    ) -> List[ExamQuestion]:
        """
        Generate ExamQuestion instances for each topic in the distribution.

        Falls back gracefully when a specific generator is not registered.
        """
        questions: List[ExamQuestion] = []
        question_number = 1

        for topic_weight, count in topic_distribution:
            generator = registry.get(topic_weight.question_type)

            # Fallback: try ARITHMETIC if desired type is missing
            if generator is None:
                generator = registry.get(QuestionType.ARITHMETIC)
            if generator is None:
                logger.error(
                    "No generator available for %s (or fallback "
                    "ARITHMETIC); skipping",
                    topic_weight.question_type.value,
                )
                continue

            diff_min, diff_max = topic_weight.difficulty_range
            for _ in range(count):
                difficulty = random.uniform(diff_min, diff_max)
                grade_level = self._exam_type_to_grade(exam_type)

                try:
                    generated = generator.generate(
                        difficulty=difficulty,
                        grade_level=grade_level,
                    )
                except Exception:
                    logger.exception(
                        "Question generation failed for topic %s; "
                        "retrying with default difficulty",
                        topic_weight.topic_slug,
                    )
                    try:
                        generated = generator.generate(difficulty=0.5)
                    except Exception:
                        logger.exception(
                            "Retry also failed for topic %s; "
                            "skipping question",
                            topic_weight.topic_slug,
                        )
                        continue

                questions.append(ExamQuestion(
                    question_number=question_number,
                    generated_question=generated,
                    topic_slug=topic_weight.topic_slug,
                    topic_name_tr=topic_weight.topic_name_tr,
                ))
                question_number += 1

        # Shuffle so topics are interleaved (matches real exam feel)
        random.shuffle(questions)
        for idx, q in enumerate(questions, start=1):
            q.question_number = idx

        return questions

    @staticmethod
    def _exam_type_to_grade(exam_type: ExamType) -> int:
        """Map exam type to an approximate grade level for generators."""
        return {
            ExamType.LGS: 8,
            ExamType.TYT: 10,
            ExamType.AYT: 12,
        }.get(exam_type, 8)

    @staticmethod
    def _check_answer(
        question: GeneratedQuestion,
        user_answer: Any,
    ) -> bool:
        """
        Compare a user's answer to the correct answer.

        Handles numeric tolerance, string normalisation, and fraction
        formats.
        """
        correct = question.correct_answer

        # Normalise both to strings for comparison
        user_str = str(user_answer).strip().lower().replace(" ", "")
        correct_str = str(correct).strip().lower().replace(" ", "")

        # Exact string match
        if user_str == correct_str:
            return True

        # Numeric comparison with tolerance
        try:
            user_num = float(user_str.replace(",", "."))
            correct_num = float(correct_str.replace(",", "."))
            if abs(user_num - correct_num) < 1e-6:
                return True
            # Percentage-based tolerance for larger numbers
            if correct_num != 0 and abs(
                (user_num - correct_num) / correct_num
            ) < 0.005:
                return True
        except (ValueError, ZeroDivisionError):
            pass

        # Fraction comparison: e.g. "2/4" == "1/2"
        try:
            if "/" in user_str and "/" in correct_str:
                from fractions import Fraction as Frac
                if Frac(user_str) == Frac(correct_str):
                    return True
        except (ValueError, ZeroDivisionError):
            pass

        return False

    @staticmethod
    def _estimate_percentile(
        exam_type: ExamType,
        net_score: float,
        total_questions: int,
    ) -> Optional[float]:
        """
        Provide a rough percentile estimate based on historical averages.

        These are approximate benchmarks and NOT official OSYM/MEB data.
        They give students directional feedback only.
        """
        if total_questions == 0:
            return None

        max_possible = float(total_questions)
        if exam_type == ExamType.LGS:
            normalised = net_score  # already 0-1 for LGS
        else:
            normalised = max(0.0, net_score) / max_possible

        # Sigmoid-based rough percentile mapping
        z = (normalised - 0.5) * 6
        percentile = 100.0 / (1.0 + math.exp(-z))
        return min(max(percentile, 0.0), 99.9)

    @staticmethod
    def _generate_recommendations(
        exam_type: ExamType,
        topic_results: List[TopicResult],
        weaknesses: List[str],
    ) -> List[str]:
        """
        Generate actionable study recommendations in Turkish.

        Recommendations are tailored to the exam type and focus on
        the student's weakest topics.
        """
        recommendations: List[str] = []

        exam_labels = {
            ExamType.LGS: "LGS",
            ExamType.TYT: "TYT",
            ExamType.AYT: "AYT",
        }
        exam_label = exam_labels.get(
            exam_type, exam_type.value.upper()
        )

        if not weaknesses:
            recommendations.append(
                f"Tebrikler! {exam_label} konularinda genel "
                f"performansiniz iyi. Daha da ilerlemek icin "
                f"zorluk seviyesini artirmaya calisin."
            )
            return recommendations

        # Sort by accuracy ascending so worst topics come first
        sorted_topics = sorted(
            topic_results, key=lambda t: t.accuracy
        )

        for tr in sorted_topics:
            if tr.topic_slug not in weaknesses:
                continue

            pct = int(tr.accuracy * 100)
            name = tr.topic_name_tr

            if tr.accuracy < 0.25:
                recommendations.append(
                    f"{name} konusunda cok fazla calismaya "
                    f"ihtiyaciniz var (%{pct} basari). Temel "
                    f"kavramlari tekrar edin ve bol bol ornek "
                    f"soru cozun."
                )
            elif tr.accuracy < 0.50:
                recommendations.append(
                    f"{name} konusunu guclendirmelisiniz "
                    f"(%{pct} basari). Yanlis yaptiginiz "
                    f"sorularin cozumlerini inceleyin ve "
                    f"benzer sorularla pratik yapin."
                )

        # Time-management tip if applicable
        slow_topics = [
            tr for tr in topic_results
            if tr.average_time_seconds > 120.0
        ]
        if slow_topics:
            slow_names = ", ".join(
                tr.topic_name_tr for tr in slow_topics[:3]
            )
            recommendations.append(
                f"Zaman yonetimi: {slow_names} konularinda soru "
                f"basina cok zaman harciyorsunuz. Hizli cozum "
                f"teknikleri uzerinde calisin."
            )

        # Exam-specific tips
        if exam_type == ExamType.LGS:
            recommendations.append(
                "LGS'de her soru esit puana sahiptir. "
                "Emin olmadiginiz soruyu bos birakmak yerine "
                "eleme yontemiyle cevap vermeye calisin."
            )
        elif exam_type in (ExamType.TYT, ExamType.AYT):
            recommendations.append(
                f"{exam_label}'de her yanlis 1/4 dogru puani "
                f"goturur. Emin olmadiginiz sorulari bos "
                f"birakmak daha avantajli olabilir."
            )

        return recommendations


# ---------------------------------------------------------------------------
# Module-level convenience instance
# ---------------------------------------------------------------------------

exam_prep_service = ExamPrepService()
