"""
Answer Validation and Explanation Service.

Provides comprehensive answer validation with step-by-step explanations.
"""

from typing import Any, Optional, List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
import re


class AnswerType(str, Enum):
    """Types of expected answers."""
    INTEGER = "integer"
    DECIMAL = "decimal"
    FRACTION = "fraction"
    RATIO = "ratio"
    EXPRESSION = "expression"
    PERCENTAGE = "percentage"


@dataclass
class ValidationResult:
    """Result of answer validation."""
    is_correct: bool
    user_answer: str
    correct_answer: str
    normalized_user: Any
    normalized_correct: Any
    feedback: str
    explanation: Optional[str] = None
    steps: Optional[List[str]] = None
    hint: Optional[str] = None
    partial_credit: float = 0.0


class AnswerValidator:
    """
    Validates user answers with tolerance and format handling.

    Supports multiple answer formats and provides detailed feedback.
    """

    # Tolerance for decimal comparison
    DECIMAL_TOLERANCE = 0.01

    def validate(
        self,
        user_input: str,
        correct_answer: Any,
        answer_type: AnswerType,
        question_params: Optional[Dict] = None
    ) -> ValidationResult:
        """
        Validate user input against correct answer.

        Args:
            user_input: Raw user input string
            correct_answer: Expected correct answer
            answer_type: Type of answer expected
            question_params: Optional question parameters for explanation

        Returns:
            ValidationResult with feedback and explanation
        """
        # Clean input
        user_input = user_input.strip()

        # Parse user answer
        try:
            parsed_user = self._parse_answer(user_input, answer_type)
        except ValueError as e:
            return ValidationResult(
                is_correct=False,
                user_answer=user_input,
                correct_answer=str(correct_answer),
                normalized_user=None,
                normalized_correct=correct_answer,
                feedback="Invalid answer format. Please check your input.",
                hint=f"Expected format: {self._get_format_hint(answer_type)}",
            )

        # Parse correct answer if string
        if isinstance(correct_answer, str):
            try:
                parsed_correct = self._parse_answer(correct_answer, answer_type)
            except:
                parsed_correct = correct_answer
        else:
            parsed_correct = correct_answer

        # Compare based on answer type
        is_correct, partial = self._compare_answers(
            parsed_user,
            parsed_correct,
            answer_type
        )

        # Generate feedback and explanation
        feedback = self._generate_feedback(is_correct, parsed_user, parsed_correct, answer_type)
        explanation = None
        steps = None
        hint = None

        if not is_correct and question_params:
            explanation, steps = self._generate_explanation(question_params)
            hint = self._generate_hint(parsed_user, parsed_correct, question_params)

        return ValidationResult(
            is_correct=is_correct,
            user_answer=user_input,
            correct_answer=str(correct_answer),
            normalized_user=parsed_user,
            normalized_correct=parsed_correct,
            feedback=feedback,
            explanation=explanation,
            steps=steps,
            hint=hint,
            partial_credit=partial,
        )

    def _parse_answer(self, answer: str, answer_type: AnswerType) -> Any:
        """Parse user answer to appropriate type."""
        answer = answer.strip().lower()

        # Remove common prefixes/suffixes
        answer = answer.replace('$', '').replace('units', '').replace('sq', '').strip()

        if answer_type == AnswerType.INTEGER:
            # Handle potential decimal input
            val = float(answer)
            if val == int(val):
                return int(val)
            return int(round(val))

        elif answer_type == AnswerType.DECIMAL:
            return float(answer)

        elif answer_type == AnswerType.FRACTION:
            if '/' in answer:
                parts = answer.split('/')
                return Fraction(int(parts[0].strip()), int(parts[1].strip()))
            else:
                return Fraction(answer)

        elif answer_type == AnswerType.RATIO:
            # Format: a:b
            if ':' in answer:
                parts = answer.split(':')
                return (int(parts[0].strip()), int(parts[1].strip()))
            return answer

        elif answer_type == AnswerType.PERCENTAGE:
            # Remove % sign if present
            answer = answer.replace('%', '').strip()
            return float(answer)

        elif answer_type == AnswerType.EXPRESSION:
            # Keep as string but normalize
            return answer.replace(' ', '')

        return answer

    def _compare_answers(
        self,
        user_answer: Any,
        correct_answer: Any,
        answer_type: AnswerType
    ) -> Tuple[bool, float]:
        """
        Compare user answer to correct answer.

        Returns: (is_correct, partial_credit)
        """
        try:
            if answer_type == AnswerType.INTEGER:
                is_correct = int(user_answer) == int(correct_answer)
                partial = 0.5 if abs(int(user_answer) - int(correct_answer)) == 1 else 0.0
                return is_correct, partial

            elif answer_type == AnswerType.DECIMAL:
                is_correct = abs(float(user_answer) - float(correct_answer)) < self.DECIMAL_TOLERANCE
                return is_correct, 0.0

            elif answer_type == AnswerType.FRACTION:
                user_frac = Fraction(user_answer) if not isinstance(user_answer, Fraction) else user_answer
                correct_frac = Fraction(correct_answer) if not isinstance(correct_answer, Fraction) else correct_answer
                is_correct = user_frac == correct_frac
                return is_correct, 0.0

            elif answer_type == AnswerType.RATIO:
                # Normalize ratios
                if isinstance(user_answer, tuple) and isinstance(correct_answer, tuple):
                    # Simplify both
                    import math
                    u_gcd = math.gcd(user_answer[0], user_answer[1])
                    c_gcd = math.gcd(correct_answer[0], correct_answer[1])
                    user_norm = (user_answer[0] // u_gcd, user_answer[1] // u_gcd)
                    correct_norm = (correct_answer[0] // c_gcd, correct_answer[1] // c_gcd)
                    return user_norm == correct_norm, 0.0
                return str(user_answer) == str(correct_answer), 0.0

            elif answer_type == AnswerType.PERCENTAGE:
                is_correct = abs(float(user_answer) - float(str(correct_answer).replace('%', ''))) < 0.1
                return is_correct, 0.0

            else:
                # String comparison
                return str(user_answer).lower() == str(correct_answer).lower(), 0.0

        except Exception:
            return False, 0.0

    def _generate_feedback(
        self,
        is_correct: bool,
        user_answer: Any,
        correct_answer: Any,
        answer_type: AnswerType
    ) -> str:
        """Generate appropriate feedback message."""
        if is_correct:
            messages = [
                "Correct! Well done!",
                "Excellent work!",
                "That's right! Great job!",
                "Perfect!",
                "Correct! You've got it!",
            ]
            import random
            return random.choice(messages)
        else:
            # Analyze the error type
            error_type = self._identify_error(user_answer, correct_answer, answer_type)

            if error_type == "sign":
                return f"Almost! Check your sign. The correct answer is {correct_answer}."
            elif error_type == "off_by_one":
                return f"So close! You were off by one. The correct answer is {correct_answer}."
            elif error_type == "magnitude":
                return f"Check your decimal place. The correct answer is {correct_answer}."
            elif error_type == "not_simplified":
                return f"Your answer needs to be simplified. The correct answer is {correct_answer}."
            else:
                return f"Not quite. The correct answer is {correct_answer}."

    def _identify_error(
        self,
        user_answer: Any,
        correct_answer: Any,
        answer_type: AnswerType
    ) -> str:
        """Identify the type of error made."""
        try:
            if answer_type in [AnswerType.INTEGER, AnswerType.DECIMAL]:
                user_val = float(user_answer) if user_answer else 0
                correct_val = float(str(correct_answer).replace('%', '').replace('$', '')) if correct_answer else 0

                if user_val == -correct_val:
                    return "sign"
                if abs(user_val - correct_val) == 1:
                    return "off_by_one"
                if user_val != 0 and (abs(user_val / 10 - correct_val) < 0.01 or abs(user_val * 10 - correct_val) < 0.01):
                    return "magnitude"

            elif answer_type == AnswerType.FRACTION:
                # Check if not simplified
                if isinstance(user_answer, Fraction) and isinstance(correct_answer, Fraction):
                    if user_answer.limit_denominator(1000) == correct_answer:
                        return "not_simplified"

            elif answer_type == AnswerType.RATIO:
                if isinstance(user_answer, tuple) and isinstance(correct_answer, tuple):
                    if user_answer == (correct_answer[1], correct_answer[0]):
                        return "reversed"

        except:
            pass

        return "general"

    def _generate_explanation(
        self,
        params: Dict
    ) -> Tuple[Optional[str], Optional[List[str]]]:
        """Generate explanation and steps for the problem."""
        operation = params.get("operation", "")
        equation_type = params.get("equation_type", "")

        steps = []
        explanation = None

        # Linear algebra
        if equation_type == "one_step":
            expression = params.get("expression", "")
            solution = params.get("solution", 0)
            steps.append(f"Given: {expression}")
            steps.append("Isolate x by performing the inverse operation")
            steps.append(f"Solution: x = {solution}")
            explanation = "One-step equations require one operation to isolate the variable."

        elif equation_type == "two_step":
            a = params.get("a", 1)
            b = params.get("b", 0)
            c = params.get("c", 0)
            x = params.get("solution", 0)

            steps.append(f"Given: {a}x + {b} = {c}")
            steps.append(f"Step 1: Subtract {b} from both sides → {a}x = {c - b}")
            steps.append(f"Step 2: Divide both sides by {a} → x = {x}")
            explanation = "Two-step equations require two operations: first handle the constant, then the coefficient."

        # Percentages
        elif operation == "find_percentage":
            percent = params.get("percent", 0)
            value = params.get("value", 0)
            steps.append(f"To find {percent}% of {value}:")
            steps.append(f"Step 1: Convert {percent}% to decimal: {percent}/100 = {percent/100}")
            steps.append(f"Step 2: Multiply: {percent/100} × {value} = {percent * value / 100}")
            explanation = "To find a percentage of a number, convert the percentage to a decimal and multiply."

        # Geometry
        elif operation == "area":
            shape = params.get("shape", "")
            if shape == "rectangle":
                l = params.get("length", 0)
                w = params.get("width", 0)
                steps.append(f"Area of rectangle = length × width")
                steps.append(f"Area = {l} × {w} = {l * w}")
            elif shape == "triangle":
                b = params.get("base", 0)
                h = params.get("height", 0)
                steps.append(f"Area of triangle = ½ × base × height")
                steps.append(f"Area = ½ × {b} × {h} = {b * h / 2}")
            explanation = "Use the appropriate area formula for each shape."

        # Fractions
        elif operation == "addition" and params.get("fraction1"):
            steps.append("To add fractions:")
            steps.append("Step 1: Find a common denominator")
            steps.append("Step 2: Convert both fractions")
            steps.append("Step 3: Add the numerators")
            steps.append("Step 4: Simplify if needed")
            explanation = "When adding fractions with different denominators, first find a common denominator."

        return explanation, steps if steps else None

    def _generate_hint(
        self,
        user_answer: Any,
        correct_answer: Any,
        params: Dict
    ) -> Optional[str]:
        """Generate a helpful hint based on the error."""
        operation = params.get("operation", "")
        equation_type = params.get("equation_type", "")

        if equation_type in ["one_step", "two_step", "multi_step"]:
            return "Remember: what you do to one side of the equation, you must do to the other side."

        if operation == "find_percentage":
            return "Remember: to find a percentage, divide the percentage by 100 and multiply by the number."

        if operation == "area":
            shape = params.get("shape", "")
            if shape == "triangle":
                return "Don't forget to divide by 2 for triangle area!"
            elif shape == "rectangle":
                return "Area = length × width"

        if operation in ["simplify", "equivalent"]:
            return "Try dividing both parts of the ratio by their greatest common factor."

        return None

    def _get_format_hint(self, answer_type: AnswerType) -> str:
        """Get format hint for answer type."""
        hints = {
            AnswerType.INTEGER: "a whole number (e.g., 42)",
            AnswerType.DECIMAL: "a decimal number (e.g., 3.14)",
            AnswerType.FRACTION: "a fraction (e.g., 3/4)",
            AnswerType.RATIO: "a ratio (e.g., 2:3)",
            AnswerType.PERCENTAGE: "a percentage (e.g., 25 or 25%)",
            AnswerType.EXPRESSION: "a mathematical expression",
        }
        return hints.get(answer_type, "a number")


# Service class for API integration
class AnswerService:
    """Service for answer validation in the API."""

    def __init__(self, db=None):
        self.db = db
        self.validator = AnswerValidator()

    def validate_answer(
        self,
        question_id: str,
        user_answer: str,
        correct_answer: Any,
        answer_type: str,
        question_params: Optional[Dict] = None
    ) -> ValidationResult:
        """Validate an answer."""
        return self.validator.validate(
            user_input=user_answer,
            correct_answer=correct_answer,
            answer_type=AnswerType(answer_type),
            question_params=question_params
        )
