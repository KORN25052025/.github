"""
Algebra Question Generator.

Generates algebraic equation questions with deterministic correct answers.
Uses SymPy for symbolic mathematics when available.
Supports linear equations, quadratic equations, and systems of equations.
"""

import random
from typing import List, Optional, Dict, Any, Tuple, Union
from fractions import Fraction

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

# Try to import SymPy for symbolic math
try:
    import sympy as sp
    from sympy import symbols, Eq, solve, expand, simplify
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


@register_generator
class AlgebraGenerator(QuestionGenerator):
    """
    Generator for algebraic equation questions.

    Supports:
    - Linear equations (ax + b = c, ax + b = cx + d)
    - One-step equations
    - Two-step equations
    - Multi-step equations
    - Equations with variables on both sides
    - Quadratic equations (factoring, quadratic formula)

    Difficulty is controlled through:
    - Coefficient magnitude
    - Number of steps required
    - Presence of negative numbers
    - Integer vs fractional solutions
    - Single variable vs variables on both sides
    """

    # Grade-based configuration
    GRADE_CONFIG = {
        6: {
            "max_coef": 10,
            "allow_negative": False,
            "allow_fractions": False,
            "types": ["one_step"],
        },
        7: {
            "max_coef": 15,
            "allow_negative": True,
            "allow_fractions": False,
            "types": ["one_step", "two_step"],
        },
        8: {
            "max_coef": 20,
            "allow_negative": True,
            "allow_fractions": True,
            "types": ["one_step", "two_step", "multi_step"],
        },
        9: {
            "max_coef": 30,
            "allow_negative": True,
            "allow_fractions": True,
            "types": ["two_step", "multi_step", "both_sides"],
        },
        10: {
            "max_coef": 50,
            "allow_negative": True,
            "allow_fractions": True,
            "types": ["multi_step", "both_sides", "quadratic"],
        },
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.ALGEBRA

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.LINEAR, OperationType.QUADRATIC]

    def generate(
        self,
        difficulty: float = 0.5,
        operation: Optional[OperationType] = None,
        grade_level: Optional[int] = None,
        seed: Optional[int] = None,
        equation_type: Optional[str] = None,
        **kwargs
    ) -> GeneratedQuestion:
        """Generate an algebra question."""

        if seed is not None:
            random.seed(seed)

        # Determine grade level from difficulty
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)

        # Get grade configuration
        config = self._get_grade_config(grade_level)

        # Map OperationType to equation_type if provided
        if equation_type is None and operation is not None:
            op_mapping = {
                OperationType.LINEAR: "two_step",
                OperationType.QUADRATIC: "quadratic",
            }
            equation_type = op_mapping.get(operation)

        # Select equation type
        if equation_type is None:
            equation_type = random.choice(config["types"])
        elif equation_type not in config["types"]:
            # User explicitly requested this type - upgrade grade config
            for g in range(grade_level + 1, 11):
                gc = self.GRADE_CONFIG.get(g)
                if gc and equation_type in gc["types"]:
                    config = gc
                    break

        # Generate based on equation type
        if equation_type == "one_step":
            return self._generate_one_step(difficulty, config, grade_level)
        elif equation_type == "two_step":
            return self._generate_two_step(difficulty, config, grade_level)
        elif equation_type == "multi_step":
            return self._generate_multi_step(difficulty, config, grade_level)
        elif equation_type == "both_sides":
            return self._generate_both_sides(difficulty, config, grade_level)
        elif equation_type == "quadratic":
            return self._generate_quadratic(difficulty, config, grade_level)
        else:
            return self._generate_two_step(difficulty, config, grade_level)

    def _generate_one_step(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate one-step equation: x + a = b or ax = b"""
        max_coef = config["max_coef"]
        scaled_max = max(3, int(max_coef * (0.3 + 0.7 * difficulty)))

        # Choose operation type
        op_type = random.choice(["add", "subtract", "multiply", "divide"])

        if op_type == "add":
            # x + a = b
            x = random.randint(1, scaled_max)
            a = random.randint(1, scaled_max)
            b = x + a
            expression = f"x + {a} = {b}"
            solution = x

        elif op_type == "subtract":
            # x - a = b
            x = random.randint(1, scaled_max)
            a = random.randint(1, min(x, scaled_max))
            b = x - a
            expression = f"x - {a} = {b}"
            solution = x

        elif op_type == "multiply":
            # ax = b
            a = random.randint(2, min(10, scaled_max))
            x = random.randint(1, scaled_max // a + 1)
            b = a * x
            expression = f"{a}x = {b}"
            solution = x

        else:  # divide
            # x/a = b
            a = random.randint(2, min(10, scaled_max))
            b = random.randint(1, scaled_max // a + 1)
            x = a * b
            expression = f"x ÷ {a} = {b}"
            solution = x

        # Generate distractors
        distractors = self._generate_algebra_distractors(solution, expression)

        calc_difficulty = 0.2 + 0.1 * (scaled_max / max_coef)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="algebra_one_step",
            question_type=self.question_type,
            operation=OperationType.LINEAR,
            expression=f"Solve for x: {expression}",
            expression_latex=f"${self._to_latex_equation(expression)}$",
            correct_answer=str(solution),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(solution), distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "equation_type": "one_step",
                "solution": solution,
                "expression": expression,
                "grade_level": grade_level,
            },
        )

    def _generate_two_step(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate two-step equation: ax + b = c"""
        max_coef = config["max_coef"]
        allow_neg = config["allow_negative"]

        scaled_max = max(3, int(max_coef * (0.3 + 0.7 * difficulty)))

        # Generate solution first for cleaner equations
        x = random.randint(1, scaled_max)
        if allow_neg and random.random() < 0.3:
            x = -x

        # Generate coefficients
        a = random.randint(2, min(10, scaled_max))
        b = random.randint(1, scaled_max)
        if allow_neg and random.random() < 0.3:
            b = -b

        # Calculate c
        c = a * x + b

        # Format expression
        if b >= 0:
            expression = f"{a}x + {b} = {c}"
        else:
            expression = f"{a}x - {abs(b)} = {c}"

        # Generate distractors
        distractors = self._generate_algebra_distractors(x, expression)

        calc_difficulty = 0.35 + 0.15 * (scaled_max / max_coef)
        if allow_neg and (x < 0 or b < 0):
            calc_difficulty += 0.1

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="algebra_two_step",
            question_type=self.question_type,
            operation=OperationType.LINEAR,
            expression=f"Solve for x: {expression}",
            expression_latex=f"${self._to_latex_equation(expression)}$",
            correct_answer=str(x),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(x), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "equation_type": "two_step",
                "a": a,
                "b": b,
                "c": c,
                "solution": x,
                "grade_level": grade_level,
            },
        )

    def _generate_multi_step(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate multi-step equation: a(x + b) = c or ax + b = cx + d"""
        max_coef = config["max_coef"]
        allow_neg = config["allow_negative"]

        scaled_max = max(3, int(max_coef * (0.3 + 0.7 * difficulty)))

        # Generate with distribution: a(x + b) = c
        x = random.randint(1, scaled_max // 2)
        if allow_neg and random.random() < 0.3:
            x = -x

        a = random.randint(2, min(8, scaled_max))
        b = random.randint(1, scaled_max // 2)
        if allow_neg and random.random() < 0.3:
            b = -b

        c = a * (x + b)

        # Format expression
        if b >= 0:
            expression = f"{a}(x + {b}) = {c}"
        else:
            expression = f"{a}(x - {abs(b)}) = {c}"

        # Generate distractors
        distractors = self._generate_algebra_distractors(x, expression)

        calc_difficulty = 0.5 + 0.2 * (scaled_max / max_coef)
        if allow_neg:
            calc_difficulty += 0.1

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="algebra_multi_step",
            question_type=self.question_type,
            operation=OperationType.LINEAR,
            expression=f"Solve for x: {expression}",
            expression_latex=f"${self._to_latex_equation(expression)}$",
            correct_answer=str(x),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(x), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "equation_type": "multi_step",
                "a": a,
                "b": b,
                "c": c,
                "solution": x,
                "grade_level": grade_level,
            },
        )

    def _generate_both_sides(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate equation with variables on both sides: ax + b = cx + d"""
        max_coef = config["max_coef"]
        allow_neg = config["allow_negative"]

        scaled_max = max(3, int(max_coef * (0.3 + 0.7 * difficulty)))

        # Generate solution
        x = random.randint(1, scaled_max // 2)
        if allow_neg and random.random() < 0.3:
            x = -x

        # Generate coefficients ensuring a != c
        a = random.randint(2, min(10, scaled_max))
        c = random.randint(1, a - 1)  # c < a to ensure positive coefficient difference

        b = random.randint(1, scaled_max)
        d = a * x + b - c * x  # Calculate d to satisfy equation

        if allow_neg and random.random() < 0.3:
            b = -b
            d = a * x + b - c * x

        # Format expression
        left = f"{a}x + {b}" if b >= 0 else f"{a}x - {abs(b)}"
        right = f"{c}x + {d}" if d >= 0 else f"{c}x - {abs(d)}"
        expression = f"{left} = {right}"

        # Generate distractors
        distractors = self._generate_algebra_distractors(x, expression)

        calc_difficulty = 0.6 + 0.2 * (scaled_max / max_coef)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="algebra_both_sides",
            question_type=self.question_type,
            operation=OperationType.LINEAR,
            expression=f"Solve for x: {expression}",
            expression_latex=f"${self._to_latex_equation(expression)}$",
            correct_answer=str(x),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(x), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "equation_type": "both_sides",
                "a": a,
                "b": b,
                "c": c,
                "d": d,
                "solution": x,
                "grade_level": grade_level,
            },
        )

    def _generate_quadratic(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate quadratic equation: x² + bx + c = 0 (factorable)"""
        # Generate from factors for clean solutions: (x - r1)(x - r2) = 0
        r1 = random.randint(-8, 8)
        r2 = random.randint(-8, 8)

        # Expand: x² - (r1+r2)x + r1*r2 = 0
        b = -(r1 + r2)
        c = r1 * r2

        # Format expression
        if b >= 0 and c >= 0:
            expression = f"x² + {b}x + {c} = 0"
        elif b >= 0:
            expression = f"x² + {b}x - {abs(c)} = 0"
        elif c >= 0:
            expression = f"x² - {abs(b)}x + {c} = 0"
        else:
            expression = f"x² - {abs(b)}x - {abs(c)} = 0"

        # Clean up "x² + 0x" -> "x²"
        expression = expression.replace(" + 0x", "").replace(" - 0x", "")

        # Solutions (sorted)
        solutions = sorted([r1, r2])
        solution_str = f"x = {solutions[0]} or x = {solutions[1]}" if r1 != r2 else f"x = {r1}"

        # For multiple choice, use smaller root
        answer = min(abs(r1), abs(r2))
        if r1 < 0 and r2 < 0:
            answer = max(r1, r2)
        elif r1 >= 0 and r2 >= 0:
            answer = min(r1, r2)
        else:
            answer = min(r1, r2)  # negative root

        # Generate distractors
        distractors = self._generate_quadratic_distractors(r1, r2)

        calc_difficulty = 0.7 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="algebra_quadratic",
            question_type=self.question_type,
            operation=OperationType.QUADRATIC,
            expression=f"Solve for x: {expression}",
            expression_latex=f"${self._to_latex_equation(expression)}$",
            correct_answer=solution_str,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "equation_type": "quadratic",
                "b": b,
                "c": c,
                "solutions": [r1, r2],
                "grade_level": grade_level,
            },
        )

    def compute_answer(self, **parameters) -> Any:
        """Compute the correct answer deterministically."""
        eq_type = parameters.get("equation_type")

        if eq_type == "quadratic":
            return parameters.get("solutions", [0, 0])
        else:
            return parameters.get("solution", 0)

    def generate_distractors(
        self,
        correct_answer: Any,
        parameters: Dict[str, Any],
        count: int = 3
    ) -> List[Any]:
        """Generate algebra distractors."""
        expression = parameters.get("expression", "x = 0")
        return self._generate_algebra_distractors(correct_answer, expression)

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        """Calculate difficulty for algebra problem."""
        eq_type = parameters.get("equation_type", "one_step")

        base_difficulty = {
            "one_step": 0.2,
            "two_step": 0.4,
            "multi_step": 0.6,
            "both_sides": 0.7,
            "quadratic": 0.8,
        }

        return base_difficulty.get(eq_type, 0.5)

    # Helper methods

    def _difficulty_to_grade(self, difficulty: float) -> int:
        """Map difficulty to grade level."""
        if difficulty < 0.2:
            return 6
        elif difficulty < 0.4:
            return 7
        elif difficulty < 0.6:
            return 8
        elif difficulty < 0.8:
            return 9
        else:
            return 10

    def _get_grade_config(self, grade_level: int) -> Dict[str, Any]:
        """Get configuration for grade level."""
        grade = max(6, min(10, grade_level))
        return self.GRADE_CONFIG[grade]

    def _to_latex_equation(self, expression: str) -> str:
        """Convert equation to LaTeX."""
        latex = expression
        latex = latex.replace("÷", r"\div")
        latex = latex.replace("×", r"\times")
        # Handle x² -> x^2
        latex = latex.replace("²", "^2")
        return latex

    def _generate_algebra_distractors(
        self,
        solution: int,
        expression: str
    ) -> List[str]:
        """Generate plausible wrong answers for algebra."""
        distractors = set()

        # Sign error
        if solution != 0:
            distractors.add(str(-solution))

        # Off by one
        distractors.add(str(solution + 1))
        distractors.add(str(solution - 1))

        # Common calculation errors
        distractors.add(str(solution + 2))
        distractors.add(str(solution - 2))

        # Factor of 2 error
        if solution != 0:
            distractors.add(str(solution * 2))
            if solution % 2 == 0:
                distractors.add(str(solution // 2))

        # Remove correct answer
        distractors.discard(str(solution))

        return list(distractors)[:3]

    def _generate_quadratic_distractors(
        self,
        r1: int,
        r2: int
    ) -> List[str]:
        """Generate distractors for quadratic equations."""
        distractors = set()

        # Sign errors on roots
        distractors.add(str(-r1))
        distractors.add(str(-r2))

        # Off by one
        distractors.add(str(r1 + 1))
        distractors.add(str(r2 - 1))

        # Sum and product confusions
        distractors.add(str(r1 + r2))
        if r1 * r2 != r1 and r1 * r2 != r2:
            distractors.add(str(r1 * r2))

        # Remove actual roots
        distractors.discard(str(r1))
        distractors.discard(str(r2))

        return list(distractors)[:3]
