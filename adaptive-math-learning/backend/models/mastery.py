"""
Mastery tracking model.
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class Mastery(Base):
    """
    EMA-based mastery tracking per topic/subtopic.

    Stores persistent mastery scores that survive between sessions.
    """

    __tablename__ = "mastery"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"))

    # Mastery metrics
    mastery_score = Column(Float, default=0.5)  # 0.0 to 1.0
    attempts = Column(Integer, default=0)
    correct = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)

    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="mastery_records")
    subtopic = relationship("Subtopic", back_populates="mastery_records")

    # Unique constraint for topic+subtopic combination
    __table_args__ = (
        UniqueConstraint('topic_id', 'subtopic_id', name='unique_topic_subtopic'),
    )

    @property
    def accuracy(self) -> float:
        """Calculate overall accuracy."""
        if self.attempts == 0:
            return 0.0
        return self.correct / self.attempts

    @property
    def level(self) -> str:
        """Get human-readable mastery level."""
        if self.mastery_score < 0.15:
            return "Novice"
        elif self.mastery_score < 0.30:
            return "Beginner"
        elif self.mastery_score < 0.50:
            return "Developing"
        elif self.mastery_score < 0.70:
            return "Proficient"
        elif self.mastery_score < 0.85:
            return "Advanced"
        else:
            return "Expert"
