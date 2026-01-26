"""
Spaced Repetition Service (Aralikli Tekrar Servisi)

A wrong-answer notebook and SM-2 based spaced repetition system
for the Turkish adaptive math learning platform.

This module provides:
  - Wrong answer tracking and notebook management
  - SM-2 (SuperMemo 2) algorithm for optimal review scheduling
  - Review queue generation and statistics

SM-2 Algorithm Summary:
  - Quality response scale: 0-5
      0: Complete blackout
      1: Incorrect, but remembered upon seeing the answer
      2: Incorrect, but the correct answer seemed easy to recall
      3: Correct, but with significant difficulty
      4: Correct, after some hesitation
      5: Perfect response
  - Ease factor (EF) >= 1.3, starts at 2.5
  - Intervals: 1 day -> 6 days -> previous_interval * EF
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_EASE_FACTOR: float = 2.5
_MINIMUM_EASE_FACTOR: float = 1.3
_INITIAL_INTERVAL_DAYS: int = 1
_SECOND_INTERVAL_DAYS: int = 6
_MASTERED_REPETITION_THRESHOLD: int = 5
_MASTERED_EASE_THRESHOLD: float = 2.4
_DEFAULT_PAGE_SIZE: int = 20
_MAX_PAGE_SIZE: int = 100


class ResponseQuality(IntEnum):
    """SM-2 response quality scale (0-5)."""

    BLACKOUT = 0
    INCORRECT_REMEMBERED = 1
    INCORRECT_EASY_RECALL = 2
    CORRECT_DIFFICULT = 3
    CORRECT_HESITATION = 4
    PERFECT = 5


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ReviewItem:
    """Represents a single item in the spaced repetition system.

    Attributes:
        id: Unique identifier for this review item.
        user_id: The owner of this review item.
        question_data: Full question payload (text, choices, topic, etc.).
        ease_factor: SM-2 ease factor, starts at 2.5.
        interval: Current review interval in days.
        repetitions: Number of consecutive correct reviews.
        next_review_date: When this item is next due for review.
        last_reviewed: Timestamp of the most recent review.
        created_at: When this item was first created.
    """

    id: str
    user_id: str
    question_data: Dict[str, Any]
    ease_factor: float = _DEFAULT_EASE_FACTOR
    interval: float = 0.0
    repetitions: int = 0
    next_review_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_reviewed: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_due(self, now: Optional[datetime] = None) -> bool:
        """Return True if this item is due for review."""
        now = now or datetime.now(timezone.utc)
        return self.next_review_date <= now

    def is_mastered(self) -> bool:
        """Return True if this item is considered fully mastered."""
        return (
            self.repetitions >= _MASTERED_REPETITION_THRESHOLD
            and self.ease_factor >= _MASTERED_EASE_THRESHOLD
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary (JSON-safe)."""
        data = asdict(self)
        for key in ("next_review_date", "last_reviewed", "created_at"):
            value = data.get(key)
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


@dataclass
class WrongAnswerEntry:
    """A single entry in the wrong-answer notebook (Hata Defteri).

    Attributes:
        id: Unique identifier for this notebook entry.
        user_id: The owner of this entry.
        original_question: The full question that was answered incorrectly.
        user_answer: What the user submitted.
        correct_answer: The expected correct answer.
        topic: Math topic / category (e.g. kesirler, denklemler).
        subtopic: Optional narrower subtopic.
        difficulty: Question difficulty level if available.
        timestamp: When the wrong answer was recorded.
        review_count: How many times this entry has been reviewed.
        review_item_id: Link to the corresponding ReviewItem (if any).
        notes: Optional user or system notes.
    """

    id: str
    user_id: str
    original_question: Dict[str, Any]
    user_answer: Any
    correct_answer: Any
    topic: str = ""
    subtopic: str = ""
    difficulty: Optional[int] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    review_count: int = 0
    review_item_id: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary (JSON-safe)."""
        data = asdict(self)
        if isinstance(data.get("timestamp"), datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        return data


@dataclass
class SRSStatistics:
    """Aggregated spaced-repetition statistics for a user.

    Attributes:
        total_cards: Total number of review items.
        due_today: Items due for review today.
        overdue: Items past their review date by more than one day.
        mastered: Items considered fully mastered.
        learning: Items still in the learning phase (repetitions < threshold).
        average_ease_factor: Mean ease factor across all items.
        total_reviews_done: Lifetime count of reviews submitted.
        wrong_answers_total: Total entries in the wrong-answer notebook.
        topics_breakdown: Per-topic counts of wrong answers.
    """

    total_cards: int = 0
    due_today: int = 0
    overdue: int = 0
    mastered: int = 0
    learning: int = 0
    average_ease_factor: float = 0.0
    total_reviews_done: int = 0
    wrong_answers_total: int = 0
    topics_breakdown: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# SM-2 Algorithm
# ---------------------------------------------------------------------------


class SM2Algorithm:
    """Pure implementation of the SuperMemo SM-2 algorithm.

    This class is stateless; every method is a pure function that takes
    current scheduling parameters and returns updated ones.
    """

    @staticmethod
    def calculate_quality(is_correct: bool, difficulty_hint: Optional[int] = None) -> int:
        """Derive a 0-5 quality score from a boolean correct/incorrect flag.

        When only a boolean is available we map:
          - correct  -> 4 (correct with some hesitation)
          - incorrect -> 1 (incorrect, remembered upon seeing answer)

        If difficulty_hint (1-5 scale, 5 = hardest) is supplied and the
        answer is correct, we refine the quality:
          - difficulty 1-2 -> quality 5
          - difficulty 3   -> quality 4
          - difficulty 4-5 -> quality 3
        """
        if not is_correct:
            return ResponseQuality.INCORRECT_REMEMBERED

        if difficulty_hint is not None:
            if difficulty_hint <= 2:
                return ResponseQuality.PERFECT
            if difficulty_hint <= 3:
                return ResponseQuality.CORRECT_HESITATION
            return ResponseQuality.CORRECT_DIFFICULT

        return ResponseQuality.CORRECT_HESITATION

    @staticmethod
    def update_ease_factor(current_ef: float, quality: int) -> float:
        """Compute a new ease factor based on response quality.

        Formula (SM-2):
            EF_new = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))

        The result is clamped to a minimum of 1.3.
        """
        new_ef = current_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        return max(new_ef, _MINIMUM_EASE_FACTOR)

    @staticmethod
    def next_interval(repetitions: int, current_interval: float, ease_factor: float) -> float:
        """Return the next review interval in days.

        Rules:
          - repetitions == 0 -> 1 day   (first review)
          - repetitions == 1 -> 6 days  (second review)
          - repetitions >= 2 -> previous_interval * ease_factor
        """
        if repetitions == 0:
            return float(_INITIAL_INTERVAL_DAYS)
        if repetitions == 1:
            return float(_SECOND_INTERVAL_DAYS)
        return round(current_interval * ease_factor, 2)

    @classmethod
    def process_review(
        cls,
        item: ReviewItem,
        quality: int,
        now: Optional[datetime] = None,
    ) -> ReviewItem:
        """Apply one review to a ReviewItem in-place and return it.

        If quality < 3 the item is reset (repetitions back to 0, interval
        back to 1 day) but the ease factor is still updated so that the
        item becomes harder over repeated failures.
        """
        now = now or datetime.now(timezone.utc)

        quality = max(0, min(5, quality))

        # Update ease factor regardless of correctness.
        item.ease_factor = cls.update_ease_factor(item.ease_factor, quality)

        if quality >= 3:
            # Correct response -- advance the schedule.
            item.interval = cls.next_interval(item.repetitions, item.interval, item.ease_factor)
            item.repetitions += 1
        else:
            # Incorrect -- reset the schedule but keep the (now lower) EF.
            item.repetitions = 0
            item.interval = float(_INITIAL_INTERVAL_DAYS)

        item.next_review_date = now + timedelta(days=item.interval)
        item.last_reviewed = now

        return item


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class SpacedRepetitionService:
    """High-level service that ties together the wrong-answer notebook and
    the SM-2 spaced repetition scheduler.

    Storage is handled via simple in-memory dictionaries keyed by user ID.
    In production, swap the _wrong_answers and _review_items dictionaries
    for a proper database repository / ORM layer.
    """

    def __init__(self) -> None:
        # user_id -> list of WrongAnswerEntry
        self._wrong_answers: Dict[str, List[WrongAnswerEntry]] = {}
        # user_id -> dict of (review_item_id -> ReviewItem)
        self._review_items: Dict[str, Dict[str, ReviewItem]] = {}
        # user_id -> cumulative review count
        self._review_counts: Dict[str, int] = {}

        self._algorithm = SM2Algorithm()

    # ------------------------------------------------------------------
    # Wrong-answer notebook
    # ------------------------------------------------------------------

    def record_wrong_answer(
        self,
        user_id: str,
        question_data: Dict[str, Any],
        user_answer: Any,
        correct_answer: Any,
    ) -> WrongAnswerEntry:
        """Save a wrong answer to the notebook and create a review item.

        Args:
            user_id: Unique identifier of the student.
            question_data: Full question payload including text, choices, etc.
            user_answer: The answer the student submitted.
            correct_answer: The expected correct answer.

        Returns:
            The newly created WrongAnswerEntry.
        """
        entry_id = self._generate_id()
        topic = question_data.get("topic", question_data.get("konu", ""))
        subtopic = question_data.get("subtopic", question_data.get("alt_konu", ""))
        difficulty = question_data.get("difficulty", question_data.get("zorluk"))

        entry = WrongAnswerEntry(
            id=entry_id,
            user_id=user_id,
            original_question=question_data,
            user_answer=user_answer,
            correct_answer=correct_answer,
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            timestamp=datetime.now(timezone.utc),
        )

        self._wrong_answers.setdefault(user_id, []).append(entry)

        # Create a corresponding review item for SRS scheduling.
        review_item = self._create_review_item(user_id, question_data)
        entry.review_item_id = review_item.id

        return entry

    def get_wrong_answer_notebook(
        self,
        user_id: str,
        topic: Optional[str] = None,
        page: int = 1,
        per_page: int = _DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        """Return a paginated view of the wrong-answer notebook.

        Args:
            user_id: Student identifier.
            topic: Optional topic filter (case-insensitive substring match).
            page: 1-based page number.
            per_page: Items per page (clamped to _MAX_PAGE_SIZE).

        Returns:
            Dictionary with keys: items, page, per_page, total_items, total_pages.
        """
        per_page = max(1, min(per_page, _MAX_PAGE_SIZE))
        page = max(1, page)

        entries = self._wrong_answers.get(user_id, [])

        if topic:
            topic_lower = topic.lower()
            entries = [
                e for e in entries
                if topic_lower in e.topic.lower() or topic_lower in e.subtopic.lower()
            ]

        # Sort by timestamp descending (most recent first).
        entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)

        total_items = len(entries)
        total_pages = max(1, math.ceil(total_items / per_page))
        start = (page - 1) * per_page
        end = start + per_page

        return {
            "items": [e.to_dict() for e in entries[start:end]],
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
        }

    # ------------------------------------------------------------------
    # Review queue
    # ------------------------------------------------------------------

    def get_review_queue(
        self,
        user_id: str,
        max_count: int = 10,
    ) -> List[Dict[str, Any]]:
        """Return up to max_count review items that are currently due.

        Items are sorted by urgency: overdue items first (oldest
        next_review_date), then items due today.

        Args:
            user_id: Student identifier.
            max_count: Maximum number of items to return.

        Returns:
            List of review-item dictionaries ready for the front end.
        """
        max_count = max(1, min(max_count, _MAX_PAGE_SIZE))
        now = datetime.now(timezone.utc)

        items = self._review_items.get(user_id, {})
        due_items = [item for item in items.values() if item.is_due(now)]

        # Sort so the most overdue items come first.
        due_items.sort(key=lambda item: item.next_review_date)

        return [item.to_dict() for item in due_items[:max_count]]

    # ------------------------------------------------------------------
    # Review submission
    # ------------------------------------------------------------------

    def submit_review(
        self,
        user_id: str,
        question_id: str,
        is_correct: bool,
        quality: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Process a review response and update the SRS schedule.

        Args:
            user_id: Student identifier.
            question_id: The ReviewItem.id being reviewed.
            is_correct: Whether the student answered correctly.
            quality: Explicit 0-5 quality score. If None, a quality
                     score is derived from is_correct using
                     SM2Algorithm.calculate_quality.

        Returns:
            Updated review-item dictionary, or None if question_id
            was not found.
        """
        items = self._review_items.get(user_id)
        if items is None or question_id not in items:
            return None

        item = items[question_id]

        if quality is None:
            difficulty_hint = item.question_data.get(
                "difficulty", item.question_data.get("zorluk")
            )
            quality = self._algorithm.calculate_quality(is_correct, difficulty_hint)

        self._algorithm.process_review(item, quality)

        # Increment lifetime review counter.
        self._review_counts[user_id] = self._review_counts.get(user_id, 0) + 1

        # Update corresponding wrong-answer entry review count.
        self._increment_wrong_answer_review_count(user_id, question_id)

        return item.to_dict()

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_srs_statistics(self, user_id: str) -> Dict[str, Any]:
        """Compute and return aggregated SRS statistics for a user.

        Returns:
            A dictionary conforming to SRSStatistics.
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        items = list(self._review_items.get(user_id, {}).values())
        wrong_entries = self._wrong_answers.get(user_id, [])

        total = len(items)
        due_today = 0
        overdue = 0
        mastered = 0
        learning = 0
        ease_sum = 0.0

        for item in items:
            ease_sum += item.ease_factor

            if item.is_mastered():
                mastered += 1
            else:
                learning += 1

            if item.next_review_date <= now:
                if item.next_review_date < today_start:
                    overdue += 1
                else:
                    due_today += 1
            elif item.next_review_date < today_end:
                due_today += 1

        # Topic breakdown from wrong-answer notebook.
        topics: Dict[str, int] = {}
        for entry in wrong_entries:
            t = entry.topic or "Diger"
            topics[t] = topics.get(t, 0) + 1

        stats = SRSStatistics(
            total_cards=total,
            due_today=due_today,
            overdue=overdue,
            mastered=mastered,
            learning=learning,
            average_ease_factor=round(ease_sum / total, 3) if total else 0.0,
            total_reviews_done=self._review_counts.get(user_id, 0),
            wrong_answers_total=len(wrong_entries),
            topics_breakdown=topics,
        )

        return stats.to_dict()

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def clear_mastered(self, user_id: str) -> int:
        """Remove all fully mastered review items for a user.

        Mastered items are those with enough consecutive correct reviews
        and a sufficiently high ease factor (see ReviewItem.is_mastered).

        The corresponding wrong-answer notebook entries are NOT deleted
        so that the student can still look back at past mistakes.

        Args:
            user_id: Student identifier.

        Returns:
            Number of items removed.
        """
        items = self._review_items.get(user_id)
        if not items:
            return 0

        mastered_ids = [rid for rid, item in items.items() if item.is_mastered()]
        for rid in mastered_ids:
            del items[rid]

        return len(mastered_ids)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_review_item(
        self,
        user_id: str,
        question_data: Dict[str, Any],
    ) -> ReviewItem:
        """Create a new ReviewItem and store it."""
        item_id = self._generate_id()
        item = ReviewItem(
            id=item_id,
            user_id=user_id,
            question_data=question_data,
        )
        self._review_items.setdefault(user_id, {})[item_id] = item
        return item

    def _increment_wrong_answer_review_count(
        self,
        user_id: str,
        review_item_id: str,
    ) -> None:
        """Bump the review_count on the wrong-answer entry linked to a review item."""
        entries = self._wrong_answers.get(user_id, [])
        for entry in entries:
            if entry.review_item_id == review_item_id:
                entry.review_count += 1
                break

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique identifier string."""
        return uuid.uuid4().hex


# Module-level singleton
spaced_repetition_service = SpacedRepetitionService()
