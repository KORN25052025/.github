"""
Shared dependencies for API routes.
"""

from typing import Generator
from sqlalchemy.orm import Session

from ..database import SessionLocal, get_db
from ..services.question_service import QuestionService
from ..services.answer_service import AnswerService
from ..services.question_service import SessionService, MasteryService


def get_question_service(db: Session = None) -> QuestionService:
    """Get question service instance."""
    return QuestionService(db)


def get_answer_service(db: Session = None) -> AnswerService:
    """Get answer service instance."""
    return AnswerService(db)


def get_session_service(db: Session = None) -> SessionService:
    """Get session service instance."""
    return SessionService(db)


def get_mastery_service(db: Session = None) -> MasteryService:
    """Get mastery service instance."""
    return MasteryService(db)
