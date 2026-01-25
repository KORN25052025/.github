"""
Question Generation Service.

Orchestrates question generation with AI enhancement and caching.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import uuid

from question_engine.base import QuestionType, OperationType, GeneratedQuestion
from question_engine.registry import registry
from adaptation.bkt_tracker import BKTTracker
from adaptation.difficulty_mapper import DifficultyMapper, difficulty_mapper


@dataclass
class QuestionServiceConfig:
    """Configuration for question service."""
    enable_story_generation: bool = False
    enable_visual_generation: bool = False
    cache_questions: bool = True
    default_difficulty: float = 0.5


class QuestionService:
    """
    Service for generating and managing questions.

    Handles:
    - Question generation orchestration
    - Difficulty adjustment based on mastery
    - AI story generation (when enabled)
    - Question caching for validation
    """

    # In-memory cache for question data (for answer validation)
    _question_cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self, db=None, config: Optional[QuestionServiceConfig] = None):
        self.db = db
        self.config = config or QuestionServiceConfig()
        self.mastery_tracker = BKTTracker()
        self.difficulty_mapper = difficulty_mapper

    def generate_question(
        self,
        topic: str,
        subtopic: Optional[str] = None,
        difficulty: Optional[float] = None,
        operation: Optional[str] = None,
        with_story: bool = False,
        grade_level: Optional[int] = None,
    ) -> GeneratedQuestion:
        """
        Generate a question based on parameters.

        Args:
            topic: Topic slug (e.g., "arithmetic", "algebra")
            subtopic: Optional subtopic slug
            difficulty: Target difficulty (0-1), None for adaptive
            operation: Specific operation to use
            with_story: Whether to generate AI story
            grade_level: Target grade level

        Returns:
            GeneratedQuestion instance
        """
        # Map topic to question type
        question_type = self._topic_to_type(topic)

        # Get generator
        generator = registry.get(question_type)
        if not generator:
            # Fallback to arithmetic
            generator = registry.get(QuestionType.ARITHMETIC)

        # Determine difficulty
        if difficulty is None:
            topic_key = f"{topic}:{subtopic}" if subtopic else topic
            difficulty = self.mastery_tracker.get_recommended_difficulty(topic_key)

        # Parse operation
        operation_enum = None
        if operation:
            try:
                operation_enum = OperationType(operation)
            except ValueError:
                pass

        # Generate question
        question = generator.generate(
            difficulty=difficulty,
            operation=operation_enum,
            grade_level=grade_level,
        )

        # Generate story if requested
        if with_story and self.config.enable_story_generation:
            question = self._add_story(question)

        # Cache for validation
        self._cache_question(question, topic)

        return question

    def get_cached_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Get cached question data."""
        return self._question_cache.get(question_id)

    def update_mastery(
        self,
        topic: str,
        is_correct: bool,
        subtopic: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ) -> float:
        """
        Update mastery after answering a question.

        Returns new mastery score.
        """
        topic_key = f"{topic}:{subtopic}" if subtopic else topic
        return self.mastery_tracker.update(
            topic_key,
            is_correct,
            response_time_ms=response_time_ms
        )

    def get_mastery(self, topic: str, subtopic: Optional[str] = None) -> float:
        """Get current mastery for a topic."""
        topic_key = f"{topic}:{subtopic}" if subtopic else topic
        return self.mastery_tracker.get_mastery(topic_key)

    def get_recommended_topics(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recommended topics based on mastery."""
        all_topics = [
            "arithmetic", "fractions", "percentages",
            "algebra", "geometry", "ratios"
        ]

        recommendations = []
        for topic in all_topics:
            mastery = self.mastery_tracker.get_mastery(topic)
            record = self.mastery_tracker.get_record(topic)

            # Recommend topics that need practice
            if mastery < 0.8 or record.attempts < 10:
                priority = 1 if mastery < 0.4 else (2 if mastery < 0.6 else 3)
                recommendations.append({
                    "topic": topic,
                    "mastery": mastery,
                    "attempts": record.attempts,
                    "priority": priority,
                })

        # Sort by priority and mastery
        recommendations.sort(key=lambda x: (x["priority"], x["mastery"]))
        return recommendations[:count]

    def _topic_to_type(self, topic: str) -> QuestionType:
        """Map topic slug to QuestionType."""
        mapping = {
            "arithmetic": QuestionType.ARITHMETIC,
            "fractions": QuestionType.FRACTIONS,
            "percentages": QuestionType.PERCENTAGES,
            "algebra": QuestionType.ALGEBRA,
            "geometry": QuestionType.GEOMETRY,
            "ratios": QuestionType.RATIOS,
        }
        return mapping.get(topic.lower(), QuestionType.ARITHMETIC)

    def _cache_question(self, question: GeneratedQuestion, topic: str) -> None:
        """Cache question data for later validation."""
        self._question_cache[question.question_id] = {
            "question_id": question.question_id,
            "correct_answer": question.correct_answer,
            "answer_format": question.answer_format.value,
            "topic": topic,
            "parameters": question.parameters,
            "difficulty": question.difficulty_score,
        }

    def _add_story(self, question: GeneratedQuestion) -> GeneratedQuestion:
        """Add AI-generated story to question."""
        try:
            from ai_integration.llm.story_generator import generate_story_sync

            story = generate_story_sync(
                expression=question.expression,
                answer=question.correct_answer,
            )

            if story.success:
                question.story_text = story.story_text
                question.visual_prompt = story.visual_prompt

        except Exception:
            # Story generation failed, continue without story
            pass

        return question


class SessionService:
    """Service for managing learning sessions."""

    def __init__(self, db=None):
        self.db = db

    def create_session(
        self,
        topic_id: Optional[int] = None,
        subtopic_id: Optional[int] = None,
        session_type: str = "practice"
    ) -> Dict[str, Any]:
        """Create a new learning session."""
        session_key = str(uuid.uuid4())[:8]

        return {
            "session_key": session_key,
            "topic_id": topic_id,
            "subtopic_id": subtopic_id,
            "session_type": session_type,
            "questions_attempted": 0,
            "questions_correct": 0,
        }

    def end_session(self, session_key: str) -> Dict[str, Any]:
        """End a learning session."""
        # In a full implementation, this would update the database
        return {
            "session_key": session_key,
            "ended": True,
        }


class MasteryService:
    """Service for mastery tracking operations using BKT algorithm."""

    def __init__(self, db=None):
        self.db = db
        self.tracker = BKTTracker()

    def get_all_mastery(self) -> Dict[str, Any]:
        """Get mastery for all topics."""
        return self.tracker.to_dict()

    def get_topic_mastery(self, topic: str) -> Dict[str, Any]:
        """Get mastery for a specific topic."""
        record = self.tracker.get_record(topic)
        return {
            "topic": topic,
            "mastery_score": record.mastery,  # BKT uses 'mastery'
            "level": record.difficulty_tier.name,  # BKT uses 'difficulty_tier'
            "attempts": record.attempts,
            "correct": record.correct,
            "accuracy": record.accuracy,
            "streak": record.streak,
        }

    def reset_topic(self, topic: str) -> None:
        """Reset mastery for a topic."""
        self.tracker.reset(topic)

    def reset_all(self) -> None:
        """Reset all mastery data."""
        self.tracker.reset_all()
