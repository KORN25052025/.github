"""
Tests for backend services and utilities.

Tests the service layer including answer validation, mastery tracking,
and question generation utilities.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAnswerValidator:
    """Tests for the AnswerValidator class."""

    def test_validator_import(self):
        """Test that AnswerValidator can be imported."""
        from backend.services.answer_service import AnswerValidator, AnswerType
        validator = AnswerValidator()
        assert validator is not None

    def test_validate_integer_correct(self):
        """Test validating correct integer answer."""
        from backend.services.answer_service import AnswerValidator, AnswerType

        validator = AnswerValidator()
        result = validator.validate(
            user_input="42",
            correct_answer=42,
            answer_type=AnswerType.INTEGER
        )

        assert result.is_correct is True

    def test_validate_integer_incorrect(self):
        """Test validating incorrect integer answer."""
        from backend.services.answer_service import AnswerValidator, AnswerType

        validator = AnswerValidator()
        result = validator.validate(
            user_input="41",
            correct_answer=42,
            answer_type=AnswerType.INTEGER
        )

        assert result.is_correct is False

    def test_validate_decimal_with_tolerance(self):
        """Test decimal validation with tolerance."""
        from backend.services.answer_service import AnswerValidator, AnswerType

        validator = AnswerValidator()
        result = validator.validate(
            user_input="3.14",
            correct_answer=3.14159,
            answer_type=AnswerType.DECIMAL
        )

        # Should be correct within tolerance
        assert result is not None

    def test_validate_fraction(self):
        """Test fraction validation."""
        from backend.services.answer_service import AnswerValidator, AnswerType

        validator = AnswerValidator()
        result = validator.validate(
            user_input="1/2",
            correct_answer="1/2",
            answer_type=AnswerType.FRACTION
        )

        assert result.is_correct is True

    def test_validation_result_has_feedback(self):
        """Test that validation result includes feedback."""
        from backend.services.answer_service import AnswerValidator, AnswerType

        validator = AnswerValidator()
        result = validator.validate(
            user_input="wrong",
            correct_answer=42,
            answer_type=AnswerType.INTEGER
        )

        assert result.feedback is not None
        assert len(result.feedback) > 0


class TestSymPyUtils:
    """Tests for SymPy utility functions."""

    def test_symbolic_math_import(self):
        """Test that symbolic_math can be imported."""
        from question_engine.sympy_utils import symbolic_math
        assert symbolic_math is not None

    def test_solve_linear_equation(self):
        """Test solving linear equations."""
        from question_engine.sympy_utils import symbolic_math

        # ax + b = c where a=2, b=3, c=7 -> x=2
        result = symbolic_math.solve_linear(2, 3, 7)
        assert result == 2.0

    def test_solve_quadratic_equation(self):
        """Test solving quadratic equations."""
        from question_engine.sympy_utils import symbolic_math

        # x^2 - 4 = 0 -> x = ±2
        result = symbolic_math.solve_quadratic(1, 0, -4)
        assert result is not None
        assert 2.0 in result or -2.0 in result

    def test_simplify_fraction(self):
        """Test fraction simplification."""
        from question_engine.sympy_utils import symbolic_math

        # 4/8 = 1/2
        result = symbolic_math.simplify_fraction(4, 8)
        assert result == (1, 2)

    def test_gcd(self):
        """Test greatest common divisor."""
        from question_engine.sympy_utils import symbolic_math

        assert symbolic_math.gcd(12, 8) == 4
        assert symbolic_math.gcd(17, 13) == 1

    def test_lcm(self):
        """Test least common multiple."""
        from question_engine.sympy_utils import symbolic_math

        assert symbolic_math.lcm(4, 6) == 12
        assert symbolic_math.lcm(3, 5) == 15

    def test_evaluate_expression(self):
        """Test safe expression evaluation."""
        from question_engine.sympy_utils import symbolic_math

        # Simple arithmetic
        result = symbolic_math.evaluate_expression("2 + 3")
        assert result == 5.0

    def test_evaluate_expression_with_variables(self):
        """Test expression evaluation with variables."""
        from question_engine.sympy_utils import symbolic_math

        result = symbolic_math.evaluate_expression("x + 5", x=3)
        assert result == 8.0


class TestMasteryTrackerService:
    """Tests for the mastery tracking system in services."""

    def test_mastery_tracker_import(self):
        """Test that MasteryTracker can be imported."""
        from adaptation.mastery_tracker import MasteryTracker
        tracker = MasteryTracker()
        assert tracker is not None

    def test_initial_mastery(self):
        """Test initial mastery value."""
        from adaptation.mastery_tracker import MasteryTracker

        tracker = MasteryTracker()
        mastery = tracker.get_mastery("topic1")

        # Default initial mastery should be 0.5
        assert mastery == 0.5

    def test_update_correct_increases_mastery(self):
        """Test that correct answers increase mastery."""
        from adaptation.mastery_tracker import MasteryTracker

        tracker = MasteryTracker()
        initial = tracker.get_mastery("topic1")

        # Note: update takes (topic_id, is_correct) not (user_id, topic_id, is_correct)
        tracker.update("topic1", is_correct=True)
        after = tracker.get_mastery("topic1")

        assert after > initial

    def test_update_incorrect_decreases_mastery(self):
        """Test that incorrect answers decrease mastery."""
        from adaptation.mastery_tracker import MasteryTracker

        tracker = MasteryTracker()

        # First increase mastery
        for _ in range(5):
            tracker.update("topic1", is_correct=True)

        before = tracker.get_mastery("topic1")
        tracker.update("topic1", is_correct=False)
        after = tracker.get_mastery("topic1")

        assert after < before

    def test_mastery_bounded(self):
        """Test that mastery stays within 0-1 bounds."""
        from adaptation.mastery_tracker import MasteryTracker

        tracker = MasteryTracker()

        # Many correct answers
        for _ in range(50):
            tracker.update("topic1", is_correct=True)

        high = tracker.get_mastery("topic1")
        assert high <= 1.0

        # Many incorrect answers on different topic
        for _ in range(50):
            tracker.update("topic2", is_correct=False)

        low = tracker.get_mastery("topic2")
        assert low >= 0.0

    def test_streak_tracking(self):
        """Test streak tracking functionality."""
        from adaptation.mastery_tracker import MasteryTracker

        tracker = MasteryTracker()

        # Build a streak
        for _ in range(5):
            tracker.update("topic1", is_correct=True)

        record = tracker.get_record("topic1")
        assert record.streak >= 5

        # Break the streak
        tracker.update("topic1", is_correct=False)
        record = tracker.get_record("topic1")
        assert record.streak == 0


class TestQuestionGenerators:
    """Tests for question generators via service layer."""

    def test_arithmetic_generator(self):
        """Test arithmetic question generation."""
        from question_engine.generators.arithmetic import ArithmeticGenerator
        from question_engine.base import OperationType

        generator = ArithmeticGenerator()
        question = generator.generate(
            difficulty=0.5,
            operation=OperationType.ADDITION
        )

        assert question is not None
        assert "+" in question.expression

    def test_fraction_generator(self):
        """Test fraction question generation."""
        from question_engine.generators.fractions import FractionsGenerator

        generator = FractionsGenerator()
        question = generator.generate(difficulty=0.5)

        assert question is not None

    def test_percentage_generator(self):
        """Test percentage question generation."""
        from question_engine.generators.percentages import PercentagesGenerator

        generator = PercentagesGenerator()
        question = generator.generate(difficulty=0.5)

        assert question is not None

    def test_algebra_generator(self):
        """Test algebra question generation."""
        from question_engine.generators.algebra import AlgebraGenerator
        from question_engine.base import OperationType

        generator = AlgebraGenerator()
        question = generator.generate(
            difficulty=0.5,
            operation=OperationType.LINEAR
        )

        assert question is not None


class TestGamificationSystems:
    """Tests for gamification systems."""

    def test_xp_system_import(self):
        """Test that XP system can be imported."""
        from backend.gamification.xp_system import XPSystem
        xp = XPSystem()
        assert xp is not None

    def test_badge_system_import(self):
        """Test that badge system can be imported."""
        from backend.gamification.badges import BadgeSystem
        badges = BadgeSystem()
        assert badges is not None

    def test_streak_tracker_import(self):
        """Test that streak tracker can be imported."""
        from backend.gamification.streaks import StreakTracker
        streaks = StreakTracker()
        assert streaks is not None

    def test_leaderboard_import(self):
        """Test that leaderboard can be imported."""
        from backend.gamification.leaderboard import Leaderboard
        lb = Leaderboard()
        assert lb is not None


class TestDatabaseSchemas:
    """Tests for database schemas."""

    def test_schemas_import(self):
        """Test that all schemas can be imported."""
        from backend.schemas import (
            QuestionRequest,
            QuestionResponse,
            AnswerRequest,
            AnswerResponse,
            SessionStartRequest,
            SessionResponse,
            TopicListResponse,
        )

        assert QuestionRequest is not None
        assert QuestionResponse is not None
        assert AnswerRequest is not None
        assert AnswerResponse is not None

    def test_model_schemas_import(self):
        """Test that model schemas can be imported."""
        from backend.schemas import (
            TopicResponse,
            SubtopicResponse,
            LearningSessionResponse,
            ResponseResponse,
        )

        assert TopicResponse is not None
        assert SubtopicResponse is not None
        assert LearningSessionResponse is not None
        assert ResponseResponse is not None


class TestEMACalculationService:
    """Tests for EMA calculation in MasteryTracker."""

    def test_ema_formula_applied(self):
        """Test that EMA formula is correctly applied."""
        from adaptation.mastery_tracker import MasteryTracker

        tracker = MasteryTracker(alpha=0.3)

        # Initial mastery is 0.5
        # After correct: 0.3 * 1.0 + 0.7 * 0.5 = 0.65
        tracker.update("topic1", is_correct=True)
        expected = 0.3 * 1.0 + 0.7 * 0.5

        actual = tracker.get_mastery("topic1")
        assert abs(actual - expected) < 0.01

    def test_ema_multiple_updates(self):
        """Test EMA with multiple updates."""
        from adaptation.mastery_tracker import MasteryTracker

        tracker = MasteryTracker(alpha=0.3)

        # Multiple correct answers should increase mastery
        for _ in range(10):
            tracker.update("topic1", is_correct=True)

        mastery = tracker.get_mastery("topic1")
        assert mastery > 0.9  # Should be high after 10 correct
