"""
Percentages Question Generator.

Generates percentage-related questions with deterministic correct answers.
Supports finding percentage, finding whole, and percentage change.
"""

import random
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP

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


class PercentageOperation(str):
    """Specific percentage operations."""
    FIND_PERCENTAGE = "find_percentage"      # What is X% of Y?
    FIND_WHOLE = "find_whole"                # X is Y% of what number?
    FIND_PERCENT = "find_percent"            # X is what percent of Y?
    PERCENTAGE_CHANGE = "percentage_change"  # Increase/decrease by X%
    DISCOUNT = "discount"                    # Price after X% discount
    TAX = "tax"                              # Price after X% tax


@register_generator
class PercentagesGenerator(QuestionGenerator):
    """
    Generator for percentage questions.

    Supports:
    - Finding a percentage of a number (What is 25% of 80?)
    - Finding the whole from percentage (15 is 30% of what?)
    - Finding what percent one number is of another
    - Percentage increase/decrease
    - Discount and tax calculations

    Difficulty is controlled through:
    - Percentage values (easy: 10,25,50 vs hard: 17,33,68)
    - Base number magnitude
    - Decimal results vs whole numbers
    - Multi-step calculations
    """

    # Common easy percentages
    EASY_PERCENTAGES = [10, 20, 25, 50, 75, 100]
    MEDIUM_PERCENTAGES = [5, 15, 30, 40, 60, 80, 90]
    HARD_PERCENTAGES = [12, 17, 23, 33, 37, 45, 55, 67, 78, 83]

    # Grade-based configuration
    GRADE_CONFIG = {
        5: {"max_value": 100, "percentages": "easy", "ops": ["find_percentage"]},
        6: {"max_value": 200, "percentages": "easy", "ops": ["find_percentage", "find_whole"]},
        7: {"max_value": 500, "percentages": "medium", "ops": ["find_percentage", "find_whole", "find_percent"]},
        8: {"max_value": 1000, "percentages": "medium", "ops": ["find_percentage", "find_whole", "find_percent", "percentage_change"]},
        9: {"max_value": 2000, "percentages": "hard", "ops": ["find_percentage", "find_whole", "find_percent", "percentage_change", "discount", "tax"]},
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.PERCENTAGES

    @property
    def supported_operations(self) -> List[OperationType]:
        # Using MIXED for various percentage operations
        return [OperationType.MIXED]

    def generate(
        self,
        difficulty: float = 0.5,
        operation: Optional[OperationType] = None,
        grade_level: Optional[int] = None,
        seed: Optional[int] = None,
        percentage_operation: Optional[str] = None,
        **kwargs
    ) -> GeneratedQuestion:
        """Generate a percentage question."""

        if seed is not None:
            random.seed(seed)

        # Determine grade level from difficulty
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)

        # Get grade configuration
        config = self._get_grade_config(grade_level)

        # Select percentage operation
        if percentage_operation is None:
            percentage_operation = random.choice(config["ops"])

        # Generate based on operation type
        if percentage_operation == "find_percentage":
            return self._generate_find_percentage(difficulty, config, grade_level)
        elif percentage_operation == "find_whole":
            return self._generate_find_whole(difficulty, config, grade_level)
        elif percentage_operation == "find_percent":
            return self._generate_find_percent(difficulty, config, grade_level)
        elif percentage_operation == "percentage_change":
            return self._generate_percentage_change(difficulty, config, grade_level)
        elif percentage_operation == "discount":
            return self._generate_discount(difficulty, config, grade_level)
        elif percentage_operation == "tax":
            return self._generate_tax(difficulty, config, grade_level)
        else:
            return self._generate_find_percentage(difficulty, config, grade_level)

    def _generate_find_percentage(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate 'What is X% of Y?' question."""
        # Get appropriate percentage and value
        percent = self._select_percentage(difficulty, config)
        value = self._select_value(difficulty, config)

        # Ensure clean answer for lower difficulties
        if difficulty < 0.5:
            # Adjust value to give whole number result
            result = value * percent // 100
            value = result * 100 // percent if percent > 0 else value

        # Calculate answer
        answer = value * percent / 100

        # Format answer
        if answer == int(answer):
            answer_str = str(int(answer))
            answer_format = AnswerFormat.INTEGER
        else:
            answer_str = f"{answer:.2f}".rstrip('0').rstrip('.')
            answer_format = AnswerFormat.DECIMAL

        expression = f"What is {percent}% of {value}?"

        # Generate distractors
        distractors = self._generate_percentage_distractors(answer, percent, value, "find_pct")

        # Calculate difficulty
        calc_difficulty = self._calculate_percentage_difficulty(percent, value, answer)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="percentages_find_percentage",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            expression_latex=f"${percent}\\% \\times {value} = ?$",
            correct_answer=answer_str,
            answer_format=answer_format,
            distractors=distractors,
            all_options=self._shuffle_options(answer_str, distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "percent": percent,
                "value": value,
                "operation": "find_percentage",
                "grade_level": grade_level,
            },
        )

    def _generate_find_whole(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate 'X is Y% of what number?' question."""
        # Get appropriate percentage
        percent = self._select_percentage(difficulty, config)

        # Generate the whole number first, then calculate the part
        whole = self._select_value(difficulty, config)

        # Ensure clean part value
        part = whole * percent / 100
        if difficulty < 0.5:
            part = int(part)
            whole = int(part * 100 / percent) if percent > 0 else whole

        # The answer is the whole
        answer = whole

        expression = f"{int(part) if part == int(part) else part} is {percent}% of what number?"

        # Generate distractors
        distractors = self._generate_percentage_distractors(answer, percent, part, "find_whole")

        # Calculate difficulty
        calc_difficulty = self._calculate_percentage_difficulty(percent, answer, part) + 0.1

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="percentages_find_whole",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            expression_latex=f"${part} = {percent}\\% \\times ? $",
            correct_answer=str(int(answer) if answer == int(answer) else answer),
            answer_format=AnswerFormat.INTEGER if answer == int(answer) else AnswerFormat.DECIMAL,
            distractors=distractors,
            all_options=self._shuffle_options(str(int(answer) if answer == int(answer) else answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "part": part,
                "percent": percent,
                "whole": whole,
                "operation": "find_whole",
                "grade_level": grade_level,
            },
        )

    def _generate_find_percent(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate 'X is what percent of Y?' question."""
        # Generate whole and part that give clean percentage
        percent = self._select_percentage(difficulty, config)
        whole = self._select_value(difficulty, config)
        part = whole * percent / 100

        # Ensure clean values
        if difficulty < 0.5:
            part = int(part)
            if part == 0:
                part = 1
                whole = int(part * 100 / percent)

        expression = f"{int(part) if part == int(part) else part} is what percent of {whole}?"

        # Generate distractors
        distractors = self._generate_percent_distractors(percent, part, whole)

        # Calculate difficulty
        calc_difficulty = self._calculate_percentage_difficulty(percent, whole, part) + 0.05

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="percentages_find_percent",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            expression_latex=f"$\\frac{{{part}}}{{{whole}}} \\times 100 = ?\\%$",
            correct_answer=f"{percent}%",
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(f"{percent}%", distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "part": part,
                "whole": whole,
                "percent": percent,
                "operation": "find_percent",
                "grade_level": grade_level,
            },
        )

    def _generate_percentage_change(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate percentage increase/decrease question."""
        percent = self._select_percentage(difficulty, config)
        original = self._select_value(difficulty, config)
        is_increase = random.choice([True, False])

        if is_increase:
            new_value = original * (100 + percent) / 100
            change_word = "increased"
        else:
            new_value = original * (100 - percent) / 100
            change_word = "decreased"

        # Round for cleaner answers
        if difficulty < 0.6:
            new_value = round(new_value)

        answer = new_value
        answer_str = str(int(answer)) if answer == int(answer) else f"{answer:.2f}"

        expression = f"A number {original} is {change_word} by {percent}%. What is the new value?"

        # Generate distractors
        distractors = self._generate_change_distractors(answer, original, percent, is_increase)

        calc_difficulty = self._calculate_percentage_difficulty(percent, original, answer) + 0.15

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="percentages_change",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            correct_answer=answer_str,
            answer_format=AnswerFormat.INTEGER if answer == int(answer) else AnswerFormat.DECIMAL,
            distractors=distractors,
            all_options=self._shuffle_options(answer_str, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "original": original,
                "percent": percent,
                "is_increase": is_increase,
                "operation": "percentage_change",
                "grade_level": grade_level,
            },
        )

    def _generate_discount(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate discount calculation question."""
        percent = self._select_percentage(difficulty, config)
        # Use round prices
        original_price = random.choice([20, 25, 30, 40, 50, 60, 75, 80, 100, 120, 150, 200])

        discount_amount = original_price * percent / 100
        final_price = original_price - discount_amount

        if difficulty < 0.5:
            final_price = round(final_price)

        answer_str = f"${final_price:.2f}".rstrip('0').rstrip('.')
        if answer_str.endswith('$'):
            answer_str = f"${int(final_price)}"

        expression = f"A shirt costs ${original_price}. It is on sale for {percent}% off. What is the sale price?"

        distractors = self._generate_price_distractors(final_price, original_price, discount_amount)

        calc_difficulty = self._calculate_percentage_difficulty(percent, original_price, final_price) + 0.1

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="percentages_discount",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            correct_answer=answer_str,
            answer_format=AnswerFormat.DECIMAL,
            distractors=distractors,
            all_options=self._shuffle_options(answer_str, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "original_price": original_price,
                "percent": percent,
                "final_price": final_price,
                "operation": "discount",
                "grade_level": grade_level,
            },
        )

    def _generate_tax(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate tax calculation question."""
        tax_rate = random.choice([5, 6, 7, 8, 10, 15, 20])
        original_price = random.choice([10, 15, 20, 25, 30, 40, 50, 60, 80, 100])

        tax_amount = original_price * tax_rate / 100
        final_price = original_price + tax_amount

        if difficulty < 0.5:
            final_price = round(final_price, 2)

        answer_str = f"${final_price:.2f}"

        expression = f"An item costs ${original_price}. With {tax_rate}% tax, what is the total price?"

        distractors = self._generate_price_distractors(final_price, original_price, tax_amount)

        calc_difficulty = self._calculate_percentage_difficulty(tax_rate, original_price, final_price) + 0.1

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="percentages_tax",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            correct_answer=answer_str,
            answer_format=AnswerFormat.DECIMAL,
            distractors=distractors,
            all_options=self._shuffle_options(answer_str, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "original_price": original_price,
                "tax_rate": tax_rate,
                "final_price": final_price,
                "operation": "tax",
                "grade_level": grade_level,
            },
        )

    def compute_answer(self, **parameters) -> Any:
        """Compute the correct answer deterministically."""
        operation = parameters.get("operation")

        if operation == "find_percentage":
            return parameters["value"] * parameters["percent"] / 100
        elif operation == "find_whole":
            return parameters["whole"]
        elif operation == "find_percent":
            return parameters["percent"]
        elif operation in ["discount", "tax", "percentage_change"]:
            return parameters.get("final_price", parameters.get("new_value", 0))

        return 0

    def generate_distractors(
        self,
        correct_answer: Any,
        parameters: Dict[str, Any],
        count: int = 3
    ) -> List[Any]:
        """Generate percentage distractors."""
        operation = parameters.get("operation", "find_percentage")
        percent = parameters.get("percent", 10)
        value = parameters.get("value", 100)

        return self._generate_percentage_distractors(correct_answer, percent, value, operation)

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        """Calculate difficulty for percentage problem."""
        percent = parameters.get("percent", 10)
        value = parameters.get("value", 100)
        answer = parameters.get("answer", 10)

        return self._calculate_percentage_difficulty(percent, value, answer)

    # Helper methods

    def _difficulty_to_grade(self, difficulty: float) -> int:
        """Map difficulty to grade level."""
        if difficulty < 0.2:
            return 5
        elif difficulty < 0.4:
            return 6
        elif difficulty < 0.6:
            return 7
        elif difficulty < 0.8:
            return 8
        else:
            return 9

    def _get_grade_config(self, grade_level: int) -> Dict[str, Any]:
        """Get configuration for grade level."""
        grade = max(5, min(9, grade_level))
        return self.GRADE_CONFIG[grade]

    def _select_percentage(self, difficulty: float, config: Dict[str, Any]) -> int:
        """Select appropriate percentage based on difficulty."""
        pct_type = config["percentages"]

        if pct_type == "easy" or difficulty < 0.3:
            return random.choice(self.EASY_PERCENTAGES)
        elif pct_type == "medium" or difficulty < 0.7:
            return random.choice(self.EASY_PERCENTAGES + self.MEDIUM_PERCENTAGES)
        else:
            return random.choice(self.EASY_PERCENTAGES + self.MEDIUM_PERCENTAGES + self.HARD_PERCENTAGES)

    def _select_value(self, difficulty: float, config: Dict[str, Any]) -> int:
        """Select appropriate base value based on difficulty."""
        max_val = config["max_value"]
        scaled_max = max(20, int(max_val * (0.2 + 0.8 * difficulty)))

        # Prefer round numbers
        round_values = [v for v in [10, 20, 25, 40, 50, 60, 75, 80, 100, 120, 150, 200, 250, 300, 400, 500]
                       if v <= scaled_max]

        if round_values and difficulty < 0.7:
            return random.choice(round_values)
        else:
            return random.randint(10, scaled_max)

    def _calculate_percentage_difficulty(
        self,
        percent: int,
        value: float,
        answer: float
    ) -> float:
        """Calculate difficulty score for percentage problem."""
        difficulty = 0.2

        # Non-easy percentages are harder
        if percent not in self.EASY_PERCENTAGES:
            difficulty += 0.2
        if percent in self.HARD_PERCENTAGES:
            difficulty += 0.1

        # Larger values are harder
        difficulty += min(0.2, value / 1000)

        # Non-integer answers are harder
        if answer != int(answer):
            difficulty += 0.15

        return min(1.0, difficulty)

    def _generate_percentage_distractors(
        self,
        answer: float,
        percent: int,
        value: float,
        operation: str
    ) -> List[str]:
        """Generate plausible wrong answers for percentage questions."""
        distractors = set()
        answer_num = float(str(answer).replace('$', '').replace('%', ''))

        # Common errors:

        # 1. Using percentage as decimal incorrectly (divide by 10 instead of 100)
        wrong = value * percent / 10
        if wrong != answer_num:
            distractors.add(str(int(wrong)) if wrong == int(wrong) else f"{wrong:.2f}")

        # 2. Just the percentage of the value as integer
        wrong = percent
        if wrong != answer_num:
            distractors.add(str(wrong))

        # 3. Off by factor of 10
        if answer_num != 0:
            wrong = answer_num * 10
            distractors.add(str(int(wrong)) if wrong == int(wrong) else f"{wrong:.2f}")

            wrong = answer_num / 10
            if wrong > 0:
                distractors.add(str(int(wrong)) if wrong == int(wrong) else f"{wrong:.2f}")

        # 4. Close values
        wrong = answer_num + random.randint(1, 5)
        distractors.add(str(int(wrong)) if wrong == int(wrong) else f"{wrong:.2f}")

        if answer_num > 5:
            wrong = answer_num - random.randint(1, 5)
            distractors.add(str(int(wrong)) if wrong == int(wrong) else f"{wrong:.2f}")

        # Remove correct answer
        answer_str = str(int(answer_num)) if answer_num == int(answer_num) else f"{answer_num:.2f}"
        distractors.discard(answer_str)

        return list(distractors)[:3]

    def _generate_percent_distractors(
        self,
        percent: int,
        part: float,
        whole: float
    ) -> List[str]:
        """Generate distractors for 'what percent' questions."""
        distractors = set()

        # Common errors
        if percent != 100 - percent:
            distractors.add(f"{100 - percent}%")

        distractors.add(f"{percent + 10}%")
        distractors.add(f"{max(1, percent - 10)}%")

        # Inverted calculation
        if whole != 0:
            wrong = int(whole / part * 100) if part != 0 else 0
            if wrong != percent and wrong > 0:
                distractors.add(f"{wrong}%")

        distractors.discard(f"{percent}%")
        return list(distractors)[:3]

    def _generate_change_distractors(
        self,
        answer: float,
        original: float,
        percent: int,
        is_increase: bool
    ) -> List[str]:
        """Generate distractors for percentage change questions."""
        distractors = set()

        # Just the change amount
        change = original * percent / 100
        if change != answer:
            distractors.add(str(int(change)) if change == int(change) else f"{change:.2f}")

        # Wrong direction
        if is_increase:
            wrong = original - change
        else:
            wrong = original + change
        if wrong != answer and wrong > 0:
            distractors.add(str(int(wrong)) if wrong == int(wrong) else f"{wrong:.2f}")

        # Original value
        if original != answer:
            distractors.add(str(original))

        # Close values
        distractors.add(str(int(answer + 5)))
        if answer > 5:
            distractors.add(str(int(answer - 5)))

        answer_str = str(int(answer)) if answer == int(answer) else f"{answer:.2f}"
        distractors.discard(answer_str)
        return list(distractors)[:3]

    def _generate_price_distractors(
        self,
        final: float,
        original: float,
        change: float
    ) -> List[str]:
        """Generate distractors for price questions."""
        distractors = set()

        # Just the discount/tax amount
        distractors.add(f"${change:.2f}")

        # Original price
        distractors.add(f"${original}")

        # Close values
        distractors.add(f"${final + 5:.2f}")
        if final > 5:
            distractors.add(f"${final - 5:.2f}")

        answer_str = f"${final:.2f}".rstrip('0').rstrip('.')
        distractors.discard(answer_str)
        return list(distractors)[:3]
