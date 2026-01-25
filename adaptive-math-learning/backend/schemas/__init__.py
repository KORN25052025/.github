"""
Pydantic schemas for API request/response validation.
"""

from .question import (
    QuestionRequest,
    QuestionResponse,
    QuestionListResponse,
    QuestionTypeEnum,
    OperationEnum,
)
from .answer import AnswerRequest, AnswerResponse, ExplanationResponse
from .session import SessionStartRequest, SessionResponse, SessionSummaryResponse
from .progress import (
    MasteryResponse,
    TopicMasteryResponse,
    ProgressHistoryResponse,
    StatisticsResponse,
    TopicListResponse,
)
from .models import (
    # Topic schemas
    SubtopicBase,
    SubtopicCreate,
    SubtopicResponse,
    TopicBase,
    TopicCreate,
    TopicResponse,
    TopicWithSubtopics,
    # LearningSession schemas
    LearningSessionBase,
    LearningSessionCreate,
    LearningSessionResponse,
    LearningSessionSummary,
    # Response schemas
    ResponseBase,
    ResponseCreate,
    ResponseResponse,
    ResponseSummary,
    # Aggregated schemas
    SessionWithResponses,
    TopicStats,
)

__all__ = [
    # Question schemas
    "QuestionRequest",
    "QuestionResponse",
    "QuestionListResponse",
    "QuestionTypeEnum",
    "OperationEnum",
    # Answer schemas
    "AnswerRequest",
    "AnswerResponse",
    "ExplanationResponse",
    # Session schemas
    "SessionStartRequest",
    "SessionResponse",
    "SessionSummaryResponse",
    # Progress schemas
    "MasteryResponse",
    "TopicMasteryResponse",
    "ProgressHistoryResponse",
    "StatisticsResponse",
    "TopicListResponse",
    # Model schemas
    "SubtopicBase",
    "SubtopicCreate",
    "SubtopicResponse",
    "TopicBase",
    "TopicCreate",
    "TopicResponse",
    "TopicWithSubtopics",
    "LearningSessionBase",
    "LearningSessionCreate",
    "LearningSessionResponse",
    "LearningSessionSummary",
    "ResponseBase",
    "ResponseCreate",
    "ResponseResponse",
    "ResponseSummary",
    "SessionWithResponses",
    "TopicStats",
]
