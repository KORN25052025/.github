"""
User model.
"""

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from ..database import Base


class User(Base):
    """Application user (student, parent, or teacher)."""

    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    display_name = Column(String(100), default="Student")
    grade_level = Column(Integer, default=6)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    ab_group = Column(String(20), default="control")
    created_at = Column(DateTime, default=datetime.utcnow)
