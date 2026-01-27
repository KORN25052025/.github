"""
Shared dependencies for API routes.

Provides FastAPI dependency injection functions for core services.
"""

from sqlalchemy.orm import Session

from ..database import get_db
from ..services.question_service import QuestionService, SessionService, MasteryService
from ..services.answer_service import AnswerService
