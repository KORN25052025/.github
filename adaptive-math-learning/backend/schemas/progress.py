"""
Pydantic schemas for progress tracking.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MasteryResponse(BaseModel):
    """Mastery information for a topic/subtopic."""
    topic_id: int
    topic_name: str
    subtopic_id: Optional[int] = None
    subtopic_name: Optional[str] = None
    mastery_score: float
    level: str
    attempts: int
    correct: int
    accuracy: float
    streak: int
    best_streak: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class TopicMasteryResponse(BaseModel):
    """Mastery overview for a topic including subtopics."""
    topic_id: int
    topic_name: str
    average_mastery: float
    total_attempts: int
    total_correct: int
    accuracy: float
    subtopics: List[MasteryResponse]


class ProgressHistoryResponse(BaseModel):
    """Historical progress data."""
    date: str
    questions_attempted: int
    questions_correct: int
    accuracy: float
    mastery_score: float


class StatisticsResponse(BaseModel):
    """Overall statistics for the user."""
    total_questions: int
    total_correct: int
    overall_accuracy: float
    total_sessions: int
    total_time_minutes: int
    current_streak: int
    best_streak: int
    topics_practiced: int
    average_mastery: float


class TopicListResponse(BaseModel):
    """List of available topics."""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    grade_range: str
    subtopic_count: int
    mastery_score: Optional[float] = None

    class Config:
        from_attributes = True
