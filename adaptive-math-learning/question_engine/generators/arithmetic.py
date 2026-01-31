"""
Arithmetic Question Generator.

Generates basic arithmetic questions (+, -, ×, ÷) with deterministic
correct answers and pedagogically meaningful distractors.
"""

import random
from typing import List, Optional, Dict, Any, Tuple

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
from ..distractor import distractor_generator


@register_generator
class ArithmeticGenerator(QuestionGenerator):
    """
    Generator for basic arithmetic questions.

    Supports:
    - Addition
    - Subtraction
    - Multiplication
    - Division
    - Mixed operations (order of operations)

    Difficulty is controlled through:
    - Operand magnitude (larger numbers = harder)
    - Operation type (division > multiplication > subtraction > addition)
    - Presence of negative numbers
    - Number of operations (for mixed)
    """

    # Grade-based configuration
    GRADE_CONFIG = {
        1: {"max_operand": 10, "allow_negative": False, "ops": [OperationType.ADDITION]},
        2: {"max_operand": 20, "allow_negative": False, "ops": [OperationType.ADDITION, OperationType.SUBTRACTION]},
        3: {"max_operand": 100, "allow_negative": False, "ops": [OperationType.ADDITION, OperationType.SUBTRACTION, OperationType.MULTIPLICATION]},
        4: {"max_operand": 1000, "allow_negative": False, "ops": [OperationType.ADDITION, OperationType.SUBTRACTION, OperationType.MULTIPLICATION, OperationType.DIVISION]},
        5: {"max_operand": 10000, "allow_negative": True, "ops": [OperationType.ADDITION, OperationType.SUBTRACTION, OperationType.MULTIPLICATION, OperationType.DIVISION, OperationType.MIXED]},
    }

    # Operation symbols for display
    OP_SYMBOLS = {
        OperationType.ADDITION: "+",
        OperationType.SUBTRACTION: "-",
        OperationType.MULTIPLICATION: "×",
        OperationType.DIVISION: "÷",
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.ARITHMETIC

    @property
    def supported_operations(self) -> List[OperationType]:
        return [
            OperationType.ADDITION,
            OperationType.SUBTRACTION,
            OperationType.MULTIPLICATION,
            OperationType.DIVISION,
            OperationType.MIXED,
        ]

    def generate(
        self,
        difficulty: float = 0.5,
        operation: Optional[OperationType] = None,
        grade_level: Optional[int] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> GeneratedQuestion:
        """Generate an arithmetic question."""

        if seed is not None:
            random.seed(seed)

        # Determine grade level from difficulty if not provided
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)

        # Get grade configuration
        config = self._get_grade_config(grade_level)

        # Select operation
        if operation is None:
            operation = random.choice(config["ops"])
        elif operation not in config["ops"]:
            # User explicitly requested this operation - upgrade grade config
            # to support it rather than ignoring the request
            for g in range(grade_level + 1, 6):
                if operation in self.GRADE_CONFIG[g]["ops"]:
                    config = self._get_grade_config(g)
                    break

        # Generate based on operation type
        if operation == OperationType.MIXED:
            return self._generate_mixed(difficulty, config, grade_level)
        else:
            return self._generate_single_operation(
                difficulty, operation, config, grade_level
            )

    def _generate_single_operation(
        self,
        difficulty: float,
        operation: OperationType,
        config: Dict[str, Any],
        grade_level: int,
    ) -> GeneratedQuestion:
        """Generate a single operation question."""

        # Adjust operand range based on difficulty
        max_val = self._scale_by_difficulty(config["max_operand"], difficulty)
        min_val = max(1, int(max_val * 0.1))

        # Generate operands based on operation
        if operation == OperationType.ADDITION:
            a, b = self._generate_addition_operands(min_val, max_val)
            answer = a + b
            expression = f"{a} + {b}"

        elif operation == OperationType.SUBTRACTION:
            a, b = self._generate_subtraction_operands(min_val, max_val, config["allow_negative"])
            answer = a - b
            expression = f"{a} - {b}"

        elif operation == OperationType.MULTIPLICATION:
            a, b = self._generate_multiplication_operands(min_val, max_val)
            answer = a * b
            expression = f"{a} × {b}"

        elif operation == OperationType.DIVISION:
            a, b, answer = self._generate_division_operands(min_val, max_val)
            expression = f"{a} ÷ {b}"

        else:
            raise ValueError(f"Unsupported operation: {operation}")

        # Generate distractors
        distractors = self.generate_distractors(
            answer,
            {"operation": operation, "a": a, "b": b},
            count=3
        )

        # Calculate difficulty
        calc_difficulty = self.calculate_difficulty({
            "operation": operation,
            "operands": [a, b],
            "answer": answer,
            "has_negatives": config["allow_negative"] and (a < 0 or b < 0 or answer < 0),
        })

        # Build question
        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id=f"arithmetic_{operation.value}",
            question_type=self.question_type,
            operation=operation,
            expression=f"{expression} = ?",
            expression_latex=self._to_latex(expression),
            correct_answer=answer,
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "a": a,
                "b": b,
                "operation": operation.value,
                "grade_level": grade_level,
            },
        )

    def _generate_mixed(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int,
    ) -> GeneratedQuestion:
        """Generate a mixed operations question (order of operations)."""

        # Scale operand range
        max_val = self._scale_by_difficulty(min(config["max_operand"], 50), difficulty)
        min_val = max(1, int(max_val * 0.2))

        # Generate 3 operands and 2 operations
        a = random.randint(min_val, max_val)
        b = random.randint(2, min(12, max_val))  # Keep smaller for multiplication
        c = random.randint(min_val, max_val)

        # Choose operations (ensure order of operations matters)
        ops = [OperationType.ADDITION, OperationType.SUBTRACTION,
               OperationType.MULTIPLICATION, OperationType.DIVISION]

        # First operation with lower precedence
        op1 = random.choice([OperationType.ADDITION, OperationType.SUBTRACTION])
        # Second operation with higher precedence
        op2 = random.choice([OperationType.MULTIPLICATION, OperationType.DIVISION])

        # Arrange to require order of operations
        if random.random() < 0.5:
            # a + b × c or a - b × c
            if op2 == OperationType.MULTIPLICATION:
                answer = (a + b * c) if op1 == OperationType.ADDITION else (a - b * c)
                expression = f"{a} {self.OP_SYMBOLS[op1]} {b} × {c}"
            else:
                # Division: ensure clean division
                c = random.randint(2, 10)
                b = c * random.randint(1, max_val // c if c > 0 else 5)
                answer = (a + b // c) if op1 == OperationType.ADDITION else (a - b // c)
                expression = f"{a} {self.OP_SYMBOLS[op1]} {b} ÷ {c}"
        else:
            # b × c + a or b × c - a
            if op2 == OperationType.MULTIPLICATION:
                answer = (b * c + a) if op1 == OperationType.ADDITION else (b * c - a)
                expression = f"{b} × {c} {self.OP_SYMBOLS[op1]} {a}"
            else:
                c = random.randint(2, 10)
                b = c * random.randint(1, max_val // c if c > 0 else 5)
                answer = (b // c + a) if op1 == OperationType.ADDITION else (b // c - a)
                expression = f"{b} ÷ {c} {self.OP_SYMBOLS[op1]} {a}"

        # Generate distractors including order-of-operations errors
        distractors = self._generate_mixed_distractors(answer, a, b, c, op1, op2)

        # Calculate difficulty
        calc_difficulty = self.calculate_difficulty({
            "operation": OperationType.MIXED,
            "operands": [a, b, c],
            "answer": answer,
            "step_count": 2,
        })

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="arithmetic_mixed",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=f"{expression} = ?",
            expression_latex=self._to_latex(expression),
            correct_answer=answer,
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "a": a,
                "b": b,
                "c": c,
                "op1": op1.value,
                "op2": op2.value,
                "grade_level": grade_level,
            },
        )

    def compute_answer(self, **parameters) -> Any:
        """Compute the correct answer deterministically."""
        operation = parameters.get("operation")
        a = parameters.get("a", 0)
        b = parameters.get("b", 1)

        if operation == "addition" or operation == OperationType.ADDITION:
            return a + b
        elif operation == "subtraction" or operation == OperationType.SUBTRACTION:
            return a - b
        elif operation == "multiplication" or operation == OperationType.MULTIPLICATION:
            return a * b
        elif operation == "division" or operation == OperationType.DIVISION:
            return a // b if b != 0 else 0
        else:
            return 0

    def generate_distractors(
        self,
        correct_answer: Any,
        parameters: Dict[str, Any],
        count: int = 3
    ) -> List[Any]:
        """Generate pedagogically meaningful wrong answers."""
        operation = parameters.get("operation")
        a = parameters.get("a", 10)
        b = parameters.get("b", 5)

        return distractor_generator.generate(
            correct_answer=correct_answer,
            count=count,
            operation=operation if isinstance(operation, OperationType) else None,
            operands=[a, b],
        )

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        """Calculate objective difficulty score."""
        operation = parameters.get("operation", OperationType.ADDITION)
        operands = parameters.get("operands", [10, 5])
        step_count = parameters.get("step_count", 1)
        has_negatives = parameters.get("has_negatives", False)

        return difficulty_calculator.calculate(
            operation=operation,
            operands=operands,
            step_count=step_count,
            has_negatives=has_negatives,
        )

    # Helper methods

    def _difficulty_to_grade(self, difficulty: float) -> int:
        """Map difficulty to appropriate grade level."""
        if difficulty < 0.2:
            return 1
        elif difficulty < 0.4:
            return 2
        elif difficulty < 0.6:
            return 3
        elif difficulty < 0.8:
            return 4
        else:
            return 5

    def _get_grade_config(self, grade_level: int) -> Dict[str, Any]:
        """Get configuration for a grade level."""
        # Clamp to available grades
        grade = max(1, min(5, grade_level))
        return self.GRADE_CONFIG[grade]

    def _scale_by_difficulty(self, max_value: int, difficulty: float) -> int:
        """Scale a max value based on difficulty."""
        # Lower difficulty = smaller portion of max
        # Higher difficulty = larger portion of max
        min_scale = 0.2
        scale = min_scale + (1 - min_scale) * difficulty
        return max(2, int(max_value * scale))

    def _generate_addition_operands(
        self,
        min_val: int,
        max_val: int
    ) -> Tuple[int, int]:
        """Generate operands for addition."""
        a = random.randint(min_val, max_val)
        b = random.randint(min_val, max_val)
        return a, b

    def _generate_subtraction_operands(
        self,
        min_val: int,
        max_val: int,
        allow_negative: bool
    ) -> Tuple[int, int]:
        """Generate operands for subtraction."""
        a = random.randint(min_val, max_val)
        if allow_negative:
            b = random.randint(min_val, max_val)
        else:
            # Ensure non-negative result
            b = random.randint(min_val, min(a, max_val))
        return a, b

    def _generate_multiplication_operands(
        self,
        min_val: int,
        max_val: int
    ) -> Tuple[int, int]:
        """Generate operands for multiplication."""
        # Keep factors smaller to avoid huge products
        mult_max = int(max_val ** 0.5) + 1
        mult_max = max(2, min(mult_max, 12))  # Cap at 12 for reasonable products
        a = random.randint(2, mult_max)
        b = random.randint(2, mult_max)
        return a, b

    def _generate_division_operands(
        self,
        min_val: int,
        max_val: int
    ) -> Tuple[int, int, int]:
        """Generate operands for division (ensures clean division)."""
        # Generate divisor and quotient, then compute dividend
        divisor = random.randint(2, min(12, max_val))
        quotient = random.randint(1, max(1, max_val // divisor))
        dividend = divisor * quotient
        return dividend, divisor, quotient

    def _generate_mixed_distractors(
        self,
        correct_answer: int,
        a: int,
        b: int,
        c: int,
        op1: OperationType,
        op2: OperationType
    ) -> List[int]:
        """Generate distractors for mixed operations including order-of-operations errors."""
        distractors = set()

        # Common error: applying operations left-to-right ignoring precedence
        if op1 == OperationType.ADDITION:
            left_to_right = (a + b) * c if op2 == OperationType.MULTIPLICATION else (a + b) // c
        else:
            left_to_right = (a - b) * c if op2 == OperationType.MULTIPLICATION else (a - b) // c

        if left_to_right != correct_answer:
            distractors.add(left_to_right)

        # Add standard distractors
        for d in distractor_generator.generate(correct_answer, count=4):
            if d != correct_answer and d not in distractors:
                distractors.add(d)

        return list(distractors)[:3]

    def _to_latex(self, expression: str) -> str:
        """Convert expression to LaTeX format."""
        # Simple conversion for basic arithmetic
        latex = expression.replace("×", r"\times").replace("÷", r"\div")
        return f"${latex}$"
