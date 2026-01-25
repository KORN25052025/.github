"""Tests for question generators."""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_engine.generators.arithmetic import ArithmeticGenerator
from question_engine.generators.fractions import FractionsGenerator
from question_engine.generators.percentages import PercentagesGenerator
from question_engine.generators.algebra import AlgebraGenerator
from question_engine.generators.geometry import GeometryGenerator
from question_engine.generators.ratios import RatiosGenerator
from question_engine.base import OperationType


class TestArithmeticGenerator:
    """Tests for ArithmeticGenerator."""

    def setup_method(self):
        self.generator = ArithmeticGenerator()

    def test_generate_addition(self):
        """Test addition question generation."""
        question = self.generator.generate(
            difficulty=0.3,
            operation=OperationType.ADDITION
        )

        assert question is not None
        assert question.correct_answer is not None
        assert "+" in question.expression

    def test_generate_subtraction(self):
        """Test subtraction question generation."""
        question = self.generator.generate(
            difficulty=0.3,
            operation=OperationType.SUBTRACTION
        )

        assert question is not None
        assert question.correct_answer is not None
        assert "-" in question.expression

    def test_generate_multiplication(self):
        """Test multiplication question generation."""
        question = self.generator.generate(
            difficulty=0.5,
            operation=OperationType.MULTIPLICATION
        )

        assert question is not None
        assert question.correct_answer is not None

    def test_generate_division(self):
        """Test division question generation."""
        question = self.generator.generate(
            difficulty=0.6,
            operation=OperationType.DIVISION
        )

        assert question is not None
        assert question.correct_answer is not None

    def test_distractors_generated(self):
        """Test that distractors are generated."""
        question = self.generator.generate(difficulty=0.5)

        assert len(question.distractors) > 0
        assert question.correct_answer not in question.distractors


class TestFractionsGenerator:
    """Tests for FractionsGenerator."""

    def setup_method(self):
        self.generator = FractionsGenerator()

    def test_generate_fraction_addition(self):
        """Test fraction addition."""
        question = self.generator.generate(
            difficulty=0.4,
            operation=OperationType.ADDITION
        )

        assert question is not None
        assert question.correct_answer is not None

    def test_generate_fraction_division(self):
        """Test fraction division."""
        question = self.generator.generate(
            difficulty=0.6,
            operation=OperationType.DIVISION
        )

        assert question is not None


class TestAlgebraGenerator:
    """Tests for AlgebraGenerator."""

    def setup_method(self):
        self.generator = AlgebraGenerator()

    def test_generate_linear(self):
        """Test linear equation generation."""
        question = self.generator.generate(
            difficulty=0.3,
            operation=OperationType.LINEAR
        )

        assert question is not None
        # Check that the equation contains x or similar variable
        expr_lower = question.expression.lower()
        assert "x" in expr_lower or "=" in question.expression

    def test_generate_quadratic(self):
        """Test quadratic equation generation."""
        question = self.generator.generate(
            difficulty=0.7,
            operation=OperationType.QUADRATIC
        )

        assert question is not None


class TestGeometryGenerator:
    """Tests for GeometryGenerator."""

    def setup_method(self):
        self.generator = GeometryGenerator()

    def test_generate_area(self):
        """Test area calculation question."""
        question = self.generator.generate(
            difficulty=0.4,
            operation=OperationType.AREA
        )

        assert question is not None

    def test_generate_perimeter(self):
        """Test perimeter calculation question."""
        question = self.generator.generate(
            difficulty=0.3,
            operation=OperationType.PERIMETER
        )

        assert question is not None


class TestRatiosGenerator:
    """Tests for RatiosGenerator."""

    def setup_method(self):
        self.generator = RatiosGenerator()

    def test_generate_ratio_question(self):
        """Test ratio question generation."""
        question = self.generator.generate(
            difficulty=0.4
        )

        assert question is not None
        assert question.correct_answer is not None

    def test_generate_with_division(self):
        """Test ratio with division operation."""
        question = self.generator.generate(
            difficulty=0.5,
            operation=OperationType.DIVISION
        )

        assert question is not None


class TestPercentagesGenerator:
    """Tests for PercentagesGenerator."""

    def setup_method(self):
        self.generator = PercentagesGenerator()

    def test_generate_percentage(self):
        """Test percentage question generation."""
        question = self.generator.generate(
            difficulty=0.4
        )

        assert question is not None
        assert question.correct_answer is not None


class TestMathematicalCorrectness:
    """Tests for mathematical correctness of generated questions."""

    def test_arithmetic_correctness(self):
        """Verify arithmetic answers are mathematically correct."""
        generator = ArithmeticGenerator()

        for _ in range(10):
            question = generator.generate(
                difficulty=0.5,
                operation=OperationType.ADDITION
            )

            # Parse expression like "5 + 3 = ?"
            expr = question.expression.replace("= ?", "").strip()
            parts = expr.split("+")
            if len(parts) == 2:
                a, b = int(parts[0].strip()), int(parts[1].strip())
                assert question.correct_answer == a + b

    def test_no_division_by_zero(self):
        """Ensure division questions never divide by zero."""
        generator = ArithmeticGenerator()

        for _ in range(20):
            question = generator.generate(
                difficulty=0.5,
                operation=OperationType.DIVISION
            )

            # The generator should never produce division by zero
            expr = question.expression.replace("= ?", "").strip()
            if "÷" in expr:
                parts = expr.split("÷")
                divisor = parts[1].strip() if len(parts) > 1 else "1"
                try:
                    assert int(divisor) != 0
                except ValueError:
                    pass  # Non-integer divisor is fine


class TestDifficultyScaling:
    """Tests for difficulty-based question scaling."""

    def test_difficulty_parameter_accepted(self):
        """Test that generators accept difficulty parameter."""
        generator = ArithmeticGenerator()

        # Low difficulty
        q_easy = generator.generate(difficulty=0.1)
        assert q_easy is not None

        # High difficulty
        q_hard = generator.generate(difficulty=0.9)
        assert q_hard is not None

    def test_difficulty_bounds(self):
        """Test generators handle edge difficulty values."""
        generator = ArithmeticGenerator()

        # Minimum difficulty
        q_min = generator.generate(difficulty=0.0)
        assert q_min is not None

        # Maximum difficulty
        q_max = generator.generate(difficulty=1.0)
        assert q_max is not None
