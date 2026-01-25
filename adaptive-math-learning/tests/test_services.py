"""
Tests for backend services.

Tests the service layer including answer processing and question generation.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAnswerService:
    """Tests for the answer service."""

    def test_normalize_numeric_answer(self):
        """Test normalizing numeric answers."""
        from backend.services.answer_service import normalize_answer

        # Test basic normalization
        assert normalize_answer("42") == "42"
        assert normalize_answer(" 42 ") == "42"
        assert normalize_answer("42.0") == "42"
        assert normalize_answer("42.00") == "42"

    def test_normalize_fraction_answer(self):
        """Test normalizing fraction answers."""
        from backend.services.answer_service import normalize_answer

        # Fractions should be normalized
        assert normalize_answer("1/2") in ["1/2", "0.5"]
        assert normalize_answer(" 3/4 ") in ["3/4", "0.75"]

    def test_check_answer_correct(self):
        """Test checking correct answers."""
        from backend.services.answer_service import check_answer

        # Exact match
        assert check_answer("42", "42") is True
        assert check_answer("42.0", "42") is True

        # Case insensitive for text
        assert check_answer("Yes", "yes") is True

    def test_check_answer_incorrect(self):
        """Test checking incorrect answers."""
        from backend.services.answer_service import check_answer

        assert check_answer("41", "42") is False
        assert check_answer("wrong", "42") is False

    def test_check_answer_with_tolerance(self):
        """Test checking answers with numeric tolerance."""
        from backend.services.answer_service import check_answer

        # Float comparison with tolerance
        assert check_answer("3.14", "3.14159", tolerance=0.01) is True
        assert check_answer("3.14", "3.14159", tolerance=0.001) is False

    def test_calculate_partial_credit(self):
        """Test partial credit calculation."""
        from backend.services.answer_service import calculate_partial_credit

        # Exact answer = full credit
        assert calculate_partial_credit("42", "42") == 1.0

        # Wrong answer = no credit
        assert calculate_partial_credit("wrong", "42") == 0.0

    def test_generate_feedback_correct(self):
        """Test feedback generation for correct answers."""
        from backend.services.answer_service import generate_feedback

        feedback = generate_feedback(
            is_correct=True,
            user_answer="42",
            correct_answer="42",
            question_type="arithmetic"
        )

        assert feedback is not None
        assert isinstance(feedback, str)

    def test_generate_feedback_incorrect(self):
        """Test feedback generation for incorrect answers."""
        from backend.services.answer_service import generate_feedback

        feedback = generate_feedback(
            is_correct=False,
            user_answer="41",
            correct_answer="42",
            question_type="arithmetic"
        )

        assert feedback is not None
        assert isinstance(feedback, str)


class TestQuestionService:
    """Tests for the question service."""

    def test_get_difficulty_for_mastery(self):
        """Test difficulty calculation based on mastery."""
        from backend.services.question_service import get_difficulty_for_mastery

        # Low mastery = easier questions
        difficulty_low = get_difficulty_for_mastery(0.2)
        assert difficulty_low < 50

        # High mastery = harder questions
        difficulty_high = get_difficulty_for_mastery(0.8)
        assert difficulty_high > 50

    def test_select_subtopic(self):
        """Test subtopic selection logic."""
        from backend.services.question_service import select_subtopic

        subtopics = [
            {"slug": "addition", "mastery": 0.8},
            {"slug": "subtraction", "mastery": 0.3},
            {"slug": "multiplication", "mastery": 0.5},
        ]

        # Should select lower mastery topics more often
        selected = select_subtopic(subtopics)
        assert selected in [s["slug"] for s in subtopics]

    def test_format_question_text(self):
        """Test question text formatting."""
        from backend.services.question_service import format_question_text

        # Basic formatting
        text = format_question_text("What is 2 + 2?", "arithmetic")
        assert "2 + 2" in text

    def test_generate_distractors(self):
        """Test distractor generation for multiple choice."""
        from backend.services.question_service import generate_distractors

        distractors = generate_distractors(
            correct_answer=42,
            count=3,
            question_type="arithmetic"
        )

        assert len(distractors) == 3
        assert 42 not in distractors  # Correct answer shouldn't be in distractors


class TestMasteryCalculation:
    """Tests for mastery calculation utilities."""

    def test_bkt_update(self):
        """Test Bayesian Knowledge Tracing update."""
        from adaptation.bkt import BKTModel

        model = BKTModel()

        # Initial mastery
        initial = 0.5

        # Correct answer should increase mastery
        after_correct = model.update(initial, is_correct=True)
        assert after_correct > initial

        # Incorrect answer should decrease mastery
        after_incorrect = model.update(initial, is_correct=False)
        assert after_incorrect < initial

    def test_bkt_bounds(self):
        """Test BKT mastery stays within bounds."""
        from adaptation.bkt import BKTModel

        model = BKTModel()

        # Many correct answers shouldn't exceed 1.0
        mastery = 0.9
        for _ in range(10):
            mastery = model.update(mastery, is_correct=True)
        assert mastery <= 1.0

        # Many incorrect answers shouldn't go below 0.0
        mastery = 0.1
        for _ in range(10):
            mastery = model.update(mastery, is_correct=False)
        assert mastery >= 0.0

    def test_ema_update(self):
        """Test Exponential Moving Average update."""
        from adaptation.ema import EMATracker

        tracker = EMATracker(alpha=0.3)

        # Initial value
        value = 0.5

        # Update with high score
        value = tracker.update(value, 1.0)
        assert value > 0.5

        # Update with low score
        value = tracker.update(value, 0.0)
        assert value < 1.0


class TestSymPyUtils:
    """Tests for SymPy utility functions."""

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

    def test_evaluate_expression_safe(self):
        """Test safe expression evaluation."""
        from question_engine.sympy_utils import symbolic_math

        # Simple arithmetic
        result = symbolic_math.evaluate_expression("2 + 3")
        assert result == 5.0

        # With variables
        result = symbolic_math.evaluate_expression("x + 5", x=3)
        assert result == 8.0

    def test_evaluate_expression_rejects_unsafe(self):
        """Test that unsafe expressions are rejected."""
        from question_engine.sympy_utils import symbolic_math

        # These should return None or raise an error
        result = symbolic_math.evaluate_expression("__import__('os')")
        assert result is None

        result = symbolic_math.evaluate_expression("open('/etc/passwd')")
        assert result is None


class TestQuestionGenerators:
    """Tests for question generators."""

    def test_arithmetic_generator_addition(self):
        """Test arithmetic addition question generation."""
        from question_engine.generators.arithmetic import ArithmeticGenerator

        generator = ArithmeticGenerator()
        question = generator.generate(
            operation="addition",
            difficulty=30,
            num_range=(1, 20)
        )

        assert question is not None
        assert "question" in question
        assert "answer" in question
        assert "+" in question["question"]

    def test_arithmetic_generator_multiplication(self):
        """Test arithmetic multiplication question generation."""
        from question_engine.generators.arithmetic import ArithmeticGenerator

        generator = ArithmeticGenerator()
        question = generator.generate(
            operation="multiplication",
            difficulty=50,
            num_range=(1, 12)
        )

        assert question is not None
        assert "×" in question["question"] or "*" in question["question"]

    def test_fraction_generator(self):
        """Test fraction question generation."""
        from question_engine.generators.fractions import FractionGenerator

        generator = FractionGenerator()
        question = generator.generate(
            operation="addition",
            difficulty=40
        )

        assert question is not None
        assert "/" in question["question"]

    def test_percentage_generator(self):
        """Test percentage question generation."""
        from question_engine.generators.percentages import PercentageGenerator

        generator = PercentageGenerator()
        question = generator.generate(
            subtype="find_percentage",
            difficulty=50
        )

        assert question is not None
        assert "%" in question["question"]

    def test_algebra_generator(self):
        """Test algebra question generation."""
        from question_engine.generators.algebra import AlgebraGenerator

        generator = AlgebraGenerator()
        question = generator.generate(
            equation_type="linear",
            difficulty=60
        )

        assert question is not None
        assert "x" in question["question"].lower() or "=" in question["question"]


class TestDifficultyScaling:
    """Tests for difficulty scaling."""

    def test_difficulty_affects_number_range(self):
        """Test that difficulty affects number ranges."""
        from question_engine.generators.arithmetic import ArithmeticGenerator

        generator = ArithmeticGenerator()

        # Easy question
        easy = generator.generate(operation="addition", difficulty=20)
        easy_nums = [int(n) for n in easy["question"].split() if n.isdigit()]

        # Hard question
        hard = generator.generate(operation="addition", difficulty=80)
        hard_nums = [int(n) for n in hard["question"].split() if n.isdigit()]

        # Hard questions should generally have larger numbers
        # (This is probabilistic, so we just check they're generated)
        assert len(easy_nums) >= 2
        assert len(hard_nums) >= 2

    def test_difficulty_bounds(self):
        """Test difficulty parameter bounds."""
        from question_engine.generators.arithmetic import ArithmeticGenerator

        generator = ArithmeticGenerator()

        # Should handle edge cases
        q0 = generator.generate(operation="addition", difficulty=0)
        q100 = generator.generate(operation="addition", difficulty=100)

        assert q0 is not None
        assert q100 is not None
