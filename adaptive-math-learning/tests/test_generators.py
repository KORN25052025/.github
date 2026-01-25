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
    
    def test_generate_one_step(self):
        """Test one-step equation generation."""
        question = self.generator.generate(
            difficulty=0.3,
            operation=OperationType.ONE_STEP
        )
        
        assert question is not None
        assert "x" in question.expression.lower()
    
    def test_generate_two_step(self):
        """Test two-step equation generation."""
        question = self.generator.generate(
            difficulty=0.5,
            operation=OperationType.TWO_STEP
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
    
    def test_generate_simplify(self):
        """Test ratio simplification."""
        question = self.generator.generate(
            difficulty=0.3,
            operation=OperationType.SIMPLIFY
        )
        
        assert question is not None
    
    def test_generate_proportion(self):
        """Test proportion solving."""
        question = self.generator.generate(
            difficulty=0.5,
            operation=OperationType.SOLVE_PROPORTION
        )
        
        assert question is not None


class TestMathematicalCorrectness:
    """Tests to verify mathematical correctness of generated questions."""
    
    def test_arithmetic_correctness(self):
        """Verify arithmetic answers are correct."""
        generator = ArithmeticGenerator()
        
        for _ in range(10):
            question = generator.generate(difficulty=0.5)
            
            # Re-compute answer
            params = question.parameters
            a, b = params.get("a", 0), params.get("b", 0)
            op = params.get("operation", "")
            
            if op == "addition":
                expected = a + b
            elif op == "subtraction":
                expected = a - b
            elif op == "multiplication":
                expected = a * b
            elif op == "division":
                expected = a // b if b != 0 else a
            else:
                continue
            
            assert question.correct_answer == expected, \
                f"Expected {expected}, got {question.correct_answer}"
    
    def test_no_division_by_zero(self):
        """Verify no division by zero occurs."""
        generator = ArithmeticGenerator()
        
        for _ in range(20):
            question = generator.generate(
                difficulty=0.7,
                operation=OperationType.DIVISION
            )
            
            params = question.parameters
            divisor = params.get("b", 1)
            
            assert divisor != 0, "Division by zero should not occur"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
