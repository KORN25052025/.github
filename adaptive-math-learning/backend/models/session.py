"""
Learning Session model.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class LearningSession(Base):
    """A learning/practice session."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_key = Column(String(50), unique=True, nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"))
    session_type = Column(String(20), default="practice")  # practice, quiz, test
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)

    # Relationships
    topic = relationship("Topic", back_populates="sessions")
    subtopic = relationship("Subtopic", back_populates="sessions")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="session", cascade="all, delete-orphan")

    @property
    def accuracy(self) -> float:
        """Calculate session accuracy."""
        if self.questions_attempted == 0:
            return 0.0
        return self.questions_correct / self.questions_attempted

    @property
    def is_active(self) -> bool:
        """Check if session is still active."""
        return self.ended_at is None
