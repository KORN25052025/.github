"""
Pydantic schemas for answer validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AnswerRequest(BaseModel):
    """Request for validating an answer."""
    question_id: str
    user_answer: str
    response_time_ms: Optional[int] = Field(None, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "abc123",
                "user_answer": "23",
                "response_time_ms": 5000
            }
        }


class AnswerResponse(BaseModel):
    """Response after validating an answer."""
    is_correct: bool
    user_answer: str
    correct_answer: str
    feedback: str
    explanation: Optional[str] = None

    # Updated mastery info
    new_mastery_score: Optional[float] = None
    mastery_change: Optional[float] = None
    streak: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "is_correct": True,
                "user_answer": "23",
                "correct_answer": "23",
                "feedback": "Correct! Great job!",
                "new_mastery_score": 0.65,
                "mastery_change": 0.05,
                "streak": 3
            }
        }


class ExplanationResponse(BaseModel):
    """Detailed explanation for a question."""
    question_id: str
    expression: str
    correct_answer: str
    steps: list[str]
    tip: Optional[str] = None
