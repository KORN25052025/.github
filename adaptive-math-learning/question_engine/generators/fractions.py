"""
Fractions Question Generator.

Generates fraction arithmetic questions with deterministic correct answers.
Supports addition, subtraction, multiplication, and division of fractions.
"""

import random
from typing import List, Optional, Dict, Any, Tuple
from fractions import Fraction
import math

from ..base import (
    QuestionGenerator,
    QuestionType,
    OperationType,
    AnswerFormat,
    GeneratedQuestion,
    DifficultyTier,
)
from ..registry import register_generator
from ..difficulty import difficulty_calculator
from ..distractor import DistractorGenerator


@register_generator
class FractionsGenerator(QuestionGenerator):
    """
    Generator for fraction arithmetic questions.

    Supports:
    - Addition of fractions (like and unlike denominators)
    - Subtraction of fractions
    - Multiplication of fractions
    - Division of fractions

    Difficulty is controlled through:
    - Denominator size
    - Unlike vs like denominators
    - Need for simplification
    - Mixed numbers vs proper fractions
    """

    # Grade-based configuration
    GRADE_CONFIG = {
        3: {"max_denom": 6, "allow_unlike": False, "allow_mixed": False, "ops": [OperationType.ADDITION]},
        4: {"max_denom": 10, "allow_unlike": True, "allow_mixed": False, "ops": [OperationType.ADDITION, OperationType.SUBTRACTION]},
        5: {"max_denom": 12, "allow_unlike": True, "allow_mixed": True, "ops": [OperationType.ADDITION, OperationType.SUBTRACTION, OperationType.MULTIPLICATION]},
        6: {"max_denom": 20, "allow_unlike": True, "allow_mixed": True, "ops": [OperationType.ADDITION, OperationType.SUBTRACTION, OperationType.MULTIPLICATION, OperationType.DIVISION]},
    }

    # Common denominators for easier problems
    EASY_DENOMINATORS = [2, 3, 4, 5, 6, 8, 10, 12]

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.FRACTIONS

    @property
    def supported_operations(self) -> List[OperationType]:
        return [
            OperationType.ADDITION,
            OperationType.SUBTRACTION,
            OperationType.MULTIPLICATION,
            OperationType.DIVISION,
        ]

    def generate(
        self,
        difficulty: float = 0.5,
        operation: Optional[OperationType] = None,
        grade_level: Optional[int] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> GeneratedQuestion:
        """Generate a fraction arithmetic question."""

        if seed is not None:
            random.seed(seed)

        # Determine grade level from difficulty
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)

        # Get grade configuration
        config = self._get_grade_config(grade_level)

        # Select operation
        if operation is None or operation not in config["ops"]:
            operation = random.choice(config["ops"])

        # Generate fractions based on operation
        if operation == OperationType.ADDITION:
            return self._generate_addition(difficulty, config, grade_level)
        elif operation == OperationType.SUBTRACTION:
            return self._generate_subtraction(difficulty, config, grade_level)
        elif operation == OperationType.MULTIPLICATION:
            return self._generate_multiplication(difficulty, config, grade_level)
        elif operation == OperationType.DIVISION:
            return self._generate_division(difficulty, config, grade_level)

    def _generate_addition(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate fraction addition question."""
        # Generate two fractions
        f1, f2 = self._generate_fraction_pair(difficulty, config, for_subtraction=False)

        # Calculate answer
        answer = f1 + f2
        answer_simplified = self._simplify_fraction(answer)

        # Create expression
        expression = f"{self._format_fraction(f1)} + {self._format_fraction(f2)}"

        # Generate distractors
        distractors = self._generate_fraction_distractors(answer_simplified, f1, f2, "add")

        # Calculate difficulty
        calc_difficulty = self._calculate_fraction_difficulty(f1, f2, config)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="fractions_addition",
            question_type=self.question_type,
            operation=OperationType.ADDITION,
            expression=f"{expression} = ?",
            expression_latex=self._to_latex(expression),
            correct_answer=self._format_fraction(answer_simplified),
            answer_format=AnswerFormat.FRACTION,
            distractors=distractors,
            all_options=self._shuffle_options(self._format_fraction(answer_simplified), distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "fraction1": str(f1),
                "fraction2": str(f2),
                "operation": "addition",
                "grade_level": grade_level,
            },
        )

    def _generate_subtraction(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate fraction subtraction question."""
        # Generate two fractions (ensure f1 >= f2 for positive result)
        f1, f2 = self._generate_fraction_pair(difficulty, config, for_subtraction=True)

        # Ensure positive result
        if f1 < f2:
            f1, f2 = f2, f1

        # Calculate answer
        answer = f1 - f2
        answer_simplified = self._simplify_fraction(answer)

        # Create expression
        expression = f"{self._format_fraction(f1)} - {self._format_fraction(f2)}"

        # Generate distractors
        distractors = self._generate_fraction_distractors(answer_simplified, f1, f2, "sub")

        # Calculate difficulty
        calc_difficulty = self._calculate_fraction_difficulty(f1, f2, config)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="fractions_subtraction",
            question_type=self.question_type,
            operation=OperationType.SUBTRACTION,
            expression=f"{expression} = ?",
            expression_latex=self._to_latex(expression),
            correct_answer=self._format_fraction(answer_simplified),
            answer_format=AnswerFormat.FRACTION,
            distractors=distractors,
            all_options=self._shuffle_options(self._format_fraction(answer_simplified), distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "fraction1": str(f1),
                "fraction2": str(f2),
                "operation": "subtraction",
                "grade_level": grade_level,
            },
        )

    def _generate_multiplication(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate fraction multiplication question."""
        # Generate two fractions
        f1, f2 = self._generate_fraction_pair(difficulty, config, for_multiplication=True)

        # Calculate answer
        answer = f1 * f2
        answer_simplified = self._simplify_fraction(answer)

        # Create expression
        expression = f"{self._format_fraction(f1)} × {self._format_fraction(f2)}"

        # Generate distractors
        distractors = self._generate_fraction_distractors(answer_simplified, f1, f2, "mul")

        # Calculate difficulty
        calc_difficulty = self._calculate_fraction_difficulty(f1, f2, config) + 0.1

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="fractions_multiplication",
            question_type=self.question_type,
            operation=OperationType.MULTIPLICATION,
            expression=f"{expression} = ?",
            expression_latex=self._to_latex(expression),
            correct_answer=self._format_fraction(answer_simplified),
            answer_format=AnswerFormat.FRACTION,
            distractors=distractors,
            all_options=self._shuffle_options(self._format_fraction(answer_simplified), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "fraction1": str(f1),
                "fraction2": str(f2),
                "operation": "multiplication",
                "grade_level": grade_level,
            },
        )

    def _generate_division(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate fraction division question."""
        # Generate two fractions
        f1, f2 = self._generate_fraction_pair(difficulty, config, for_division=True)

        # Ensure f2 is not zero
        if f2 == 0:
            f2 = Fraction(1, 2)

        # Calculate answer
        answer = f1 / f2
        answer_simplified = self._simplify_fraction(answer)

        # Create expression
        expression = f"{self._format_fraction(f1)} ÷ {self._format_fraction(f2)}"

        # Generate distractors
        distractors = self._generate_fraction_distractors(answer_simplified, f1, f2, "div")

        # Calculate difficulty
        calc_difficulty = self._calculate_fraction_difficulty(f1, f2, config) + 0.15

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="fractions_division",
            question_type=self.question_type,
            operation=OperationType.DIVISION,
            expression=f"{expression} = ?",
            expression_latex=self._to_latex(expression),
            correct_answer=self._format_fraction(answer_simplified),
            answer_format=AnswerFormat.FRACTION,
            distractors=distractors,
            all_options=self._shuffle_options(self._format_fraction(answer_simplified), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "fraction1": str(f1),
                "fraction2": str(f2),
                "operation": "division",
                "grade_level": grade_level,
            },
        )

    def compute_answer(self, **parameters) -> Any:
        """Compute the correct answer deterministically."""
        operation = parameters.get("operation")
        f1 = Fraction(parameters.get("fraction1", "1/2"))
        f2 = Fraction(parameters.get("fraction2", "1/3"))

        if operation == "addition":
            return self._simplify_fraction(f1 + f2)
        elif operation == "subtraction":
            return self._simplify_fraction(f1 - f2)
        elif operation == "multiplication":
            return self._simplify_fraction(f1 * f2)
        elif operation == "division":
            return self._simplify_fraction(f1 / f2) if f2 != 0 else Fraction(0)
        return Fraction(0)

    def generate_distractors(
        self,
        correct_answer: Any,
        parameters: Dict[str, Any],
        count: int = 3
    ) -> List[Any]:
        """Generate fraction distractors."""
        return self._generate_fraction_distractors(
            correct_answer,
            Fraction(parameters.get("fraction1", "1/2")),
            Fraction(parameters.get("fraction2", "1/3")),
            parameters.get("operation", "add")[:3]
        )

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        """Calculate difficulty for fractions."""
        f1 = Fraction(parameters.get("fraction1", "1/2"))
        f2 = Fraction(parameters.get("fraction2", "1/3"))

        config = self._get_grade_config(parameters.get("grade_level", 5))
        return self._calculate_fraction_difficulty(f1, f2, config)

    # Helper methods

    def _difficulty_to_grade(self, difficulty: float) -> int:
        """Map difficulty to grade level."""
        if difficulty < 0.25:
            return 3
        elif difficulty < 0.5:
            return 4
        elif difficulty < 0.75:
            return 5
        else:
            return 6

    def _get_grade_config(self, grade_level: int) -> Dict[str, Any]:
        """Get configuration for grade level."""
        grade = max(3, min(6, grade_level))
        return self.GRADE_CONFIG[grade]

    def _generate_fraction_pair(
        self,
        difficulty: float,
        config: Dict[str, Any],
        for_subtraction: bool = False,
        for_multiplication: bool = False,
        for_division: bool = False
    ) -> Tuple[Fraction, Fraction]:
        """Generate a pair of fractions appropriate for the operation."""
        max_denom = config["max_denom"]
        allow_unlike = config["allow_unlike"]

        # Scale denominator based on difficulty
        scaled_max = max(2, int(max_denom * (0.3 + 0.7 * difficulty)))

        if allow_unlike and difficulty > 0.3:
            # Unlike denominators
            d1 = random.choice([d for d in self.EASY_DENOMINATORS if d <= scaled_max])
            d2 = random.choice([d for d in self.EASY_DENOMINATORS if d <= scaled_max])
        else:
            # Like denominators (easier)
            d1 = d2 = random.choice([d for d in self.EASY_DENOMINATORS if d <= scaled_max])

        # Generate numerators
        n1 = random.randint(1, d1 - 1)
        n2 = random.randint(1, d2 - 1)

        # For multiplication/division, keep fractions simpler
        if for_multiplication or for_division:
            d1 = random.choice([2, 3, 4, 5, 6])
            d2 = random.choice([2, 3, 4, 5, 6])
            n1 = random.randint(1, min(d1, 5))
            n2 = random.randint(1, min(d2, 5))

        f1 = Fraction(n1, d1)
        f2 = Fraction(n2, d2)

        return f1, f2

    def _simplify_fraction(self, f: Fraction) -> Fraction:
        """Return fraction in lowest terms."""
        return Fraction(f.numerator, f.denominator)

    def _format_fraction(self, f: Fraction) -> str:
        """Format fraction for display."""
        if f.denominator == 1:
            return str(f.numerator)
        return f"{f.numerator}/{f.denominator}"

    def _to_latex(self, expression: str) -> str:
        """Convert fraction expression to LaTeX."""
        import re
        # Convert a/b to \frac{a}{b}
        result = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', expression)
        result = result.replace("×", r"\times").replace("÷", r"\div")
        return f"${result}$"

    def _calculate_fraction_difficulty(
        self,
        f1: Fraction,
        f2: Fraction,
        config: Dict[str, Any]
    ) -> float:
        """Calculate difficulty score for fraction problem."""
        difficulty = 0.2

        # Unlike denominators are harder
        if f1.denominator != f2.denominator:
            difficulty += 0.2

        # Larger denominators are harder
        max_denom = max(f1.denominator, f2.denominator)
        difficulty += min(0.3, max_denom / 30)

        # Need for simplification adds difficulty
        lcm = (f1.denominator * f2.denominator) // math.gcd(f1.denominator, f2.denominator)
        if lcm > max_denom:
            difficulty += 0.1

        return min(1.0, difficulty)

    def _generate_fraction_distractors(
        self,
        correct: Fraction,
        f1: Fraction,
        f2: Fraction,
        operation: str
    ) -> List[str]:
        """Generate plausible wrong fraction answers."""
        distractors = set()

        # Common errors:

        # 1. Adding/subtracting numerators AND denominators separately (common mistake)
        if operation in ["add", "sub"]:
            wrong = Fraction(
                f1.numerator + f2.numerator if operation == "add" else abs(f1.numerator - f2.numerator),
                f1.denominator + f2.denominator
            )
            if wrong != correct and wrong.denominator > 0:
                distractors.add(self._format_fraction(wrong))

        # 2. Forgetting to find common denominator
        if f1.denominator != f2.denominator:
            wrong = Fraction(f1.numerator + f2.numerator, max(f1.denominator, f2.denominator))
            if wrong != correct:
                distractors.add(self._format_fraction(wrong))

        # 3. Not simplifying
        unsimplified = Fraction(correct.numerator * 2, correct.denominator * 2)
        if unsimplified != correct:
            distractors.add(self._format_fraction(unsimplified))

        # 4. Off by one in numerator
        if correct.numerator > 1:
            wrong = Fraction(correct.numerator - 1, correct.denominator)
            distractors.add(self._format_fraction(wrong))

        wrong = Fraction(correct.numerator + 1, correct.denominator)
        distractors.add(self._format_fraction(wrong))

        # 5. Inverted fraction (for division)
        if operation == "div" and correct.numerator != 0:
            wrong = Fraction(correct.denominator, correct.numerator)
            if wrong != correct:
                distractors.add(self._format_fraction(wrong))

        # Remove correct answer if accidentally included
        correct_str = self._format_fraction(correct)
        distractors.discard(correct_str)

        return list(distractors)[:3]
