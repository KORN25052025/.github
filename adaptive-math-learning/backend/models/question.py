"""
Question model.
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class Question(Base):
    """A generated question record."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_key = Column(String(50), unique=True, nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    template_id = Column(String(100))
    question_type = Column(String(50), nullable=False)
    operation = Column(String(50))

    # Question content
    expression = Column(Text, nullable=False)
    expression_latex = Column(Text)
    correct_answer = Column(String(100), nullable=False)
    answer_format = Column(String(20), default="integer")
    distractors = Column(JSON)  # List of distractor values

    # Difficulty
    difficulty_score = Column(Float, nullable=False)
    difficulty_tier = Column(String(20))

    # Parameters used for generation
    parameters = Column(JSON)

    # AI enhancements
    story_text = Column(Text)
    visual_url = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("LearningSession", back_populates="questions")
    responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "question_id": self.question_key,
            "question_type": self.question_type,
            "operation": self.operation,
            "expression": self.expression,
            "expression_latex": self.expression_latex,
            "answer_format": self.answer_format,
            "difficulty_score": self.difficulty_score,
            "difficulty_tier": self.difficulty_tier,
            "options": self.distractors,
            "story_text": self.story_text,
            "visual_url": self.visual_url,
        }
