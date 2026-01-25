"""
Topic and Subtopic models.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Topic(Base):
    """Mathematical topic (e.g., Arithmetic, Algebra)."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    grade_range_start = Column(Integer, default=1)
    grade_range_end = Column(Integer, default=12)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Relationships
    subtopics = relationship("Subtopic", back_populates="topic", cascade="all, delete-orphan")
    sessions = relationship("LearningSession", back_populates="topic")
    mastery_records = relationship("Mastery", back_populates="topic")


class Subtopic(Base):
    """Subtopic within a topic (e.g., Addition, Multiplication)."""

    __tablename__ = "subtopics"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    difficulty_base = Column(Integer, default=50)  # 0-100 scale
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Relationships
    topic = relationship("Topic", back_populates="subtopics")
    sessions = relationship("LearningSession", back_populates="subtopic")
    mastery_records = relationship("Mastery", back_populates="subtopic")
