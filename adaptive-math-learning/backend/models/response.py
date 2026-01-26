"""
User Response model.
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class Response(Base):
    """A user's response to a question."""

    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    # Response data
    user_answer = Column(String(255), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    partial_credit = Column(Float, default=0.0)
    response_time_ms = Column(Integer)  # Time to answer in milliseconds

    # Feedback given
    feedback = Column(String(500))

    # Metadata
    answered_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    question = relationship("Question", back_populates="responses")
    session = relationship("LearningSession", back_populates="responses")
