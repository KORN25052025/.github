"""
Pydantic schemas for learning sessions.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionStartRequest(BaseModel):
    """Request to start a new learning session."""
    topic_id: Optional[int] = None
    topic_slug: Optional[str] = None
    subtopic_id: Optional[int] = None
    session_type: str = "practice"  # practice, quiz, test

    class Config:
        json_schema_extra = {
            "example": {
                "topic_slug": "arithmetic",
                "session_type": "practice"
            }
        }


class SessionResponse(BaseModel):
    """Response containing session information."""
    session_id: int
    session_key: str
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    subtopic_id: Optional[int] = None
    subtopic_name: Optional[str] = None
    session_type: str
    started_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class SessionSummaryResponse(BaseModel):
    """Summary of a completed session."""
    session_id: int
    session_key: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    questions_attempted: int
    questions_correct: int
    accuracy: float
    mastery_before: Optional[float] = None
    mastery_after: Optional[float] = None

    class Config:
        from_attributes = True
