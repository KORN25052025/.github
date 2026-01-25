"""
Pydantic schemas for database models.

Provides schema definitions for Response, LearningSession, Topic, and Subtopic models.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# =============================================================================
# Topic Schemas
# =============================================================================

class SubtopicBase(BaseModel):
    """Base schema for Subtopic."""
    name: str
    slug: str
    description: Optional[str] = None
    difficulty_base: int = 50
    display_order: int = 0
    is_active: bool = True


class SubtopicCreate(SubtopicBase):
    """Schema for creating a Subtopic."""
    topic_id: int


class SubtopicResponse(SubtopicBase):
    """Schema for Subtopic response."""
    id: int
    topic_id: int

    model_config = ConfigDict(from_attributes=True)


class TopicBase(BaseModel):
    """Base schema for Topic."""
    name: str
    slug: str
    description: Optional[str] = None
    grade_range_start: int = 1
    grade_range_end: int = 12
    display_order: int = 0
    is_active: bool = True


class TopicCreate(TopicBase):
    """Schema for creating a Topic."""
    pass


class TopicResponse(TopicBase):
    """Schema for Topic response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class TopicWithSubtopics(TopicResponse):
    """Schema for Topic with its subtopics."""
    subtopics: List[SubtopicResponse] = []


# =============================================================================
# Learning Session Schemas
# =============================================================================

class LearningSessionBase(BaseModel):
    """Base schema for LearningSession."""
    session_key: str
    topic_id: Optional[int] = None
    subtopic_id: Optional[int] = None
    session_type: str = "practice"


class LearningSessionCreate(LearningSessionBase):
    """Schema for creating a LearningSession."""
    pass


class LearningSessionResponse(LearningSessionBase):
    """Schema for LearningSession response."""
    id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    questions_attempted: int = 0
    questions_correct: int = 0

    model_config = ConfigDict(from_attributes=True)

    @property
    def accuracy(self) -> float:
        """Calculate session accuracy."""
        if self.questions_attempted == 0:
            return 0.0
        return self.questions_correct / self.questions_attempted


class LearningSessionSummary(BaseModel):
    """Summary of a learning session."""
    id: int
    session_key: str
    topic_name: Optional[str] = None
    subtopic_name: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    questions_attempted: int
    questions_correct: int
    accuracy: float
    duration_minutes: Optional[float] = None


# =============================================================================
# Response Schemas
# =============================================================================

class ResponseBase(BaseModel):
    """Base schema for Response."""
    question_id: int
    session_id: int
    user_answer: str
    is_correct: bool
    partial_credit: float = 0.0
    response_time_ms: Optional[int] = None
    feedback: Optional[str] = None


class ResponseCreate(ResponseBase):
    """Schema for creating a Response."""
    pass


class ResponseResponse(ResponseBase):
    """Schema for Response response."""
    id: int
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResponseSummary(BaseModel):
    """Summary of a response for reporting."""
    id: int
    question_id: int
    user_answer: str
    is_correct: bool
    response_time_ms: Optional[int] = None
    answered_at: datetime


# =============================================================================
# Aggregated Schemas
# =============================================================================

class SessionWithResponses(LearningSessionResponse):
    """Learning session with all responses."""
    responses: List[ResponseResponse] = []


class TopicStats(BaseModel):
    """Statistics for a topic."""
    topic_id: int
    topic_name: str
    total_sessions: int
    total_questions: int
    correct_answers: int
    average_accuracy: float
    average_response_time_ms: Optional[float] = None
