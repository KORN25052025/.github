"""
Pydantic schemas for questions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum
from datetime import datetime


class QuestionTypeEnum(str, Enum):
    ARITHMETIC = "arithmetic"
    FRACTIONS = "fractions"
    PERCENTAGES = "percentages"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    RATIOS = "ratios"


class OperationEnum(str, Enum):
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"
    MIXED = "mixed"


class AnswerFormatEnum(str, Enum):
    INTEGER = "integer"
    DECIMAL = "decimal"
    FRACTION = "fraction"
    EXPRESSION = "expression"


class DifficultyTierEnum(str, Enum):
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class QuestionRequest(BaseModel):
    """Request for generating a new question."""
    topic_id: Optional[int] = None
    topic_slug: Optional[str] = None
    subtopic_id: Optional[int] = None
    difficulty: Optional[float] = Field(None, ge=0.0, le=1.0)
    question_type: Optional[QuestionTypeEnum] = None
    operation: Optional[OperationEnum] = None
    with_story: bool = False
    multiple_choice: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "topic_slug": "arithmetic",
                "difficulty": 0.5,
                "operation": "addition",
                "multiple_choice": True
            }
        }


class QuestionResponse(BaseModel):
    """Response containing a generated question."""
    question_id: str
    session_id: Optional[int] = None
    question_type: str
    operation: Optional[str] = None

    # Display content
    expression: str
    expression_latex: Optional[str] = None
    story_text: Optional[str] = None
    visual_url: Optional[str] = None

    # Answer format
    answer_format: str
    multiple_choice: bool = True
    options: Optional[List[Any]] = None

    # Metadata
    difficulty_score: float
    difficulty_tier: str
    topic_name: Optional[str] = None
    subtopic_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "question_id": "abc123",
                "question_type": "arithmetic",
                "operation": "addition",
                "expression": "15 + 8 = ?",
                "answer_format": "integer",
                "multiple_choice": True,
                "options": [23, 22, 24, 28],
                "difficulty_score": 0.35,
                "difficulty_tier": "beginner"
            }
        }


class QuestionListResponse(BaseModel):
    """Response containing multiple questions."""
    questions: List[QuestionResponse]
    total: int
