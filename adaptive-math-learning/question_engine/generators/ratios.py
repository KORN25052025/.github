"""
Ratios Question Generator.

Generates ratio and proportion questions with deterministic correct answers.
Supports simplifying ratios, solving proportions, direct/inverse variation.
"""

import random
import math
from typing import List, Optional, Dict, Any, Tuple
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


class RatioOperation(str):
    """Types of ratio operations."""
    SIMPLIFY = "simplify"
    EQUIVALENT = "equivalent"
    SOLVE_PROPORTION = "solve_proportion"
    WORD_PROBLEM = "word_problem"
    PART_TO_WHOLE = "part_to_whole"
    SCALE = "scale"


@register_generator
class RatiosGenerator(QuestionGenerator):
    """
    Generator for ratio and proportion questions.

    Supports:
    - Simplifying ratios to lowest terms
    - Finding equivalent ratios
    - Solving proportions (cross multiplication)
    - Ratio word problems
    - Part-to-whole relationships
    - Scale problems (maps, models)

    Difficulty is controlled through:
    - Ratio magnitude
    - GCD complexity
    - Multi-step problems
    - Real-world context complexity
    """

    # Grade-based configuration
    GRADE_CONFIG = {
        5: {
            "max_value": 50,
            "operations": ["simplify", "equivalent"],
            "allow_decimals": False,
        },
        6: {
            "max_value": 100,
            "operations": ["simplify", "equivalent", "solve_proportion"],
            "allow_decimals": False,
        },
        7: {
            "max_value": 200,
            "operations": ["simplify", "equivalent", "solve_proportion", "word_problem"],
            "allow_decimals": True,
        },
        8: {
            "max_value": 500,
            "operations": ["simplify", "equivalent", "solve_proportion", "word_problem", "part_to_whole", "scale"],
            "allow_decimals": True,
        },
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.RATIOS

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.MIXED]

    def generate(
        self,
        difficulty: float = 0.5,
        operation: Optional[OperationType] = None,
        grade_level: Optional[int] = None,
        seed: Optional[int] = None,
        ratio_operation: Optional[str] = None,
        **kwargs
    ) -> GeneratedQuestion:
        """Generate a ratio question."""

        if seed is not None:
            random.seed(seed)

        # Determine grade level
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)

        # Get configuration
        config = self._get_grade_config(grade_level)

        # Select operation
        if ratio_operation is None:
            ratio_operation = random.choice(config["operations"])

        # Generate based on operation
        if ratio_operation == "simplify":
            return self._generate_simplify(difficulty, config, grade_level)
        elif ratio_operation == "equivalent":
            return self._generate_equivalent(difficulty, config, grade_level)
        elif ratio_operation == "solve_proportion":
            return self._generate_solve_proportion(difficulty, config, grade_level)
        elif ratio_operation == "word_problem":
            return self._generate_word_problem(difficulty, config, grade_level)
        elif ratio_operation == "part_to_whole":
            return self._generate_part_to_whole(difficulty, config, grade_level)
        elif ratio_operation == "scale":
            return self._generate_scale(difficulty, config, grade_level)
        else:
            return self._generate_simplify(difficulty, config, grade_level)

    def _generate_simplify(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate 'simplify this ratio' question."""
        max_val = config["max_value"]
        scaled_max = max(10, int(max_val * (0.3 + 0.7 * difficulty)))

        # Generate a simplified ratio first
        simple_a = random.randint(1, 10)
        simple_b = random.randint(1, 10)

        # Ensure coprime
        gcd = math.gcd(simple_a, simple_b)
        simple_a //= gcd
        simple_b //= gcd

        # Multiply by a factor
        factor = random.randint(2, min(10, scaled_max // max(simple_a, simple_b)))
        a = simple_a * factor
        b = simple_b * factor

        expression = f"Simplify the ratio {a}:{b}"
        answer = f"{simple_a}:{simple_b}"

        # Generate distractors
        distractors = self._generate_ratio_distractors(simple_a, simple_b, a, b, "simplify")

        calc_difficulty = 0.2 + 0.1 * (factor / 10) + 0.1 * (max(a, b) / max_val)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="ratios_simplify",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            expression_latex=f"${a}:{b}$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "original_a": a,
                "original_b": b,
                "simplified_a": simple_a,
                "simplified_b": simple_b,
                "factor": factor,
                "operation": "simplify",
                "grade_level": grade_level,
            },
        )

    def _generate_equivalent(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate 'find equivalent ratio' question."""
        max_val = config["max_value"]
        scaled_max = max(10, int(max_val * (0.3 + 0.7 * difficulty)))

        # Generate base ratio
        a = random.randint(2, 10)
        b = random.randint(2, 10)

        # Scale factor
        factor = random.randint(2, min(8, scaled_max // max(a, b)))

        # What to find
        find_second = random.choice([True, False])

        if find_second:
            # a:b = (a*factor):?
            given = a * factor
            answer = b * factor
            expression = f"Find the missing value: {a}:{b} = {given}:?"
            formula_latex = f"{a}:{b} = {given}:x"
        else:
            # a:b = ?:(b*factor)
            given = b * factor
            answer = a * factor
            expression = f"Find the missing value: {a}:{b} = ?:{given}"
            formula_latex = f"{a}:{b} = x:{given}"

        distractors = self._generate_missing_distractors(answer, a, b, factor)

        calc_difficulty = 0.25 + 0.15 * (factor / 10)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="ratios_equivalent",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            expression_latex=f"${formula_latex}$",
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "a": a,
                "b": b,
                "factor": factor,
                "answer": answer,
                "operation": "equivalent",
                "grade_level": grade_level,
            },
        )

    def _generate_solve_proportion(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate 'solve the proportion' question using cross multiplication."""
        max_val = config["max_value"]
        scaled_max = max(10, int(max_val * (0.3 + 0.7 * difficulty)))

        # Generate values that give integer solution
        a = random.randint(2, min(15, scaled_max))
        b = random.randint(2, min(15, scaled_max))
        c = random.randint(2, min(15, scaled_max))

        # x/b = c/d where x = bc/d -> ensure divisibility
        # a/b = c/x -> x = bc/a
        # Ensure bc is divisible by a
        bc = b * c
        if bc % a != 0:
            # Adjust c to make divisible
            c = (bc // a + 1) * a // b
            if c <= 0:
                c = a

        x = (b * c) // a

        expression = f"Solve for x: {a}/{b} = {c}/x"
        formula_latex = f"\\frac{{{a}}}{{{b}}} = \\frac{{{c}}}{{x}}"

        distractors = self._generate_proportion_distractors(x, a, b, c)

        calc_difficulty = 0.4 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="ratios_solve_proportion",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            expression_latex=f"${formula_latex}$",
            correct_answer=str(x),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(x), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "a": a,
                "b": b,
                "c": c,
                "x": x,
                "operation": "solve_proportion",
                "grade_level": grade_level,
            },
        )

    def _generate_word_problem(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate ratio word problem."""
        max_val = config["max_value"]
        scaled_max = max(20, int(max_val * (0.3 + 0.7 * difficulty)))

        # Problem templates
        templates = [
            {
                "context": "recipe",
                "text": "A recipe uses {a} cups of flour for every {b} cups of sugar. If you use {c} cups of flour, how many cups of sugar do you need?",
                "find": "second",
            },
            {
                "context": "distance",
                "text": "A car travels {a} miles in {b} hours. At this rate, how far will it travel in {c} hours?",
                "find": "first",
            },
            {
                "context": "students",
                "text": "The ratio of boys to girls in a class is {a}:{b}. If there are {c} boys, how many girls are there?",
                "find": "second",
            },
            {
                "context": "money",
                "text": "If {a} items cost ${b}, how much would {c} items cost?",
                "find": "second",
            },
        ]

        template = random.choice(templates)

        # Generate values
        a = random.randint(2, min(10, scaled_max // 5))
        b = random.randint(2, min(10, scaled_max // 5))

        # Generate c as multiple of a for clean answer
        multiplier = random.randint(2, min(8, scaled_max // max(a, b)))
        c = a * multiplier
        answer = b * multiplier

        expression = template["text"].format(a=a, b=b, c=c)

        distractors = self._generate_missing_distractors(answer, a, b, multiplier)

        calc_difficulty = 0.45 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id=f"ratios_word_{template['context']}",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "a": a,
                "b": b,
                "c": c,
                "answer": answer,
                "context": template["context"],
                "operation": "word_problem",
                "grade_level": grade_level,
            },
        )

    def _generate_part_to_whole(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate part-to-whole ratio problem."""
        max_val = config["max_value"]
        scaled_max = max(20, int(max_val * (0.3 + 0.7 * difficulty)))

        # Ratio parts
        part_a = random.randint(1, 5)
        part_b = random.randint(1, 5)
        total_parts = part_a + part_b

        # Total amount (multiple of total_parts for clean answer)
        multiplier = random.randint(3, min(20, scaled_max // total_parts))
        total = total_parts * multiplier

        # What to find
        find_a = random.choice([True, False])

        if find_a:
            answer = part_a * multiplier
            expression = f"A sum of ${total} is divided in the ratio {part_a}:{part_b}. What is the larger/smaller share?"
            if part_a > part_b:
                expression = f"A sum of ${total} is divided in the ratio {part_a}:{part_b}. What is the larger share?"
            else:
                expression = f"A sum of ${total} is divided in the ratio {part_a}:{part_b}. What is the first share?"
        else:
            answer = part_b * multiplier
            expression = f"A sum of ${total} is divided in the ratio {part_a}:{part_b}. What is the second share?"

        distractors = self._generate_part_whole_distractors(answer, part_a, part_b, total)

        calc_difficulty = 0.5 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="ratios_part_to_whole",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "part_a": part_a,
                "part_b": part_b,
                "total": total,
                "answer": answer,
                "operation": "part_to_whole",
                "grade_level": grade_level,
            },
        )

    def _generate_scale(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate scale/map problem."""
        # Common scales
        scales = [(1, 100), (1, 50), (1, 200), (1, 1000), (2, 100), (1, 500)]
        scale = random.choice(scales)

        map_dist = random.randint(2, 20)
        actual_dist = map_dist * scale[1] // scale[0]

        find_actual = random.choice([True, False])

        if find_actual:
            expression = f"On a map with scale {scale[0]}:{scale[1]}, a distance of {map_dist} cm represents how many cm in real life?"
            answer = actual_dist
        else:
            expression = f"On a map with scale {scale[0]}:{scale[1]}, what map distance represents {actual_dist} cm in real life?"
            answer = map_dist

        distractors = self._generate_scale_distractors(answer, scale, map_dist, actual_dist)

        calc_difficulty = 0.5 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="ratios_scale",
            question_type=self.question_type,
            operation=OperationType.MIXED,
            expression=expression,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={
                "scale": scale,
                "map_dist": map_dist,
                "actual_dist": actual_dist,
                "answer": answer,
                "operation": "scale",
                "grade_level": grade_level,
            },
        )

    def compute_answer(self, **parameters) -> Any:
        """Compute the correct answer deterministically."""
        return parameters.get("answer", 0)

    def generate_distractors(
        self,
        correct_answer: Any,
        parameters: Dict[str, Any],
        count: int = 3
    ) -> List[Any]:
        """Generate ratio distractors."""
        operation = parameters.get("operation", "simplify")
        if operation == "simplify":
            return self._generate_ratio_distractors(
                parameters.get("simplified_a", 1),
                parameters.get("simplified_b", 1),
                parameters.get("original_a", 2),
                parameters.get("original_b", 2),
                operation
            )
        else:
            return self._generate_missing_distractors(
                correct_answer,
                parameters.get("a", 2),
                parameters.get("b", 3),
                parameters.get("factor", 2)
            )

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        """Calculate difficulty for ratio problem."""
        operation = parameters.get("operation", "simplify")
        base_difficulty = {
            "simplify": 0.25,
            "equivalent": 0.35,
            "solve_proportion": 0.5,
            "word_problem": 0.55,
            "part_to_whole": 0.6,
            "scale": 0.6,
        }
        return base_difficulty.get(operation, 0.4)

    # Helper methods

    def _difficulty_to_grade(self, difficulty: float) -> int:
        """Map difficulty to grade level."""
        if difficulty < 0.25:
            return 5
        elif difficulty < 0.5:
            return 6
        elif difficulty < 0.75:
            return 7
        else:
            return 8

    def _get_grade_config(self, grade_level: int) -> Dict[str, Any]:
        """Get configuration for grade level."""
        grade = max(5, min(8, grade_level))
        return self.GRADE_CONFIG[grade]

    def _generate_ratio_distractors(
        self,
        simple_a: int,
        simple_b: int,
        orig_a: int,
        orig_b: int,
        operation: str
    ) -> List[str]:
        """Generate distractors for simplify ratio problems."""
        distractors = set()

        # Not fully simplified
        if orig_a != simple_a:
            factor = 2
            distractors.add(f"{simple_a * factor}:{simple_b * factor}")

        # Reversed ratio
        distractors.add(f"{simple_b}:{simple_a}")

        # Off by one
        distractors.add(f"{simple_a + 1}:{simple_b}")
        distractors.add(f"{simple_a}:{simple_b + 1}")

        # Original ratio
        if f"{orig_a}:{orig_b}" != f"{simple_a}:{simple_b}":
            distractors.add(f"{orig_a}:{orig_b}")

        distractors.discard(f"{simple_a}:{simple_b}")
        return list(distractors)[:3]

    def _generate_missing_distractors(
        self,
        answer: int,
        a: int,
        b: int,
        factor: int
    ) -> List[str]:
        """Generate distractors for missing value problems."""
        distractors = set()

        # Common errors
        distractors.add(str(answer + a))
        distractors.add(str(answer - b))
        distractors.add(str(answer + factor))

        # Wrong operation
        distractors.add(str(a * b))
        distractors.add(str(abs(a - b) * factor))

        # Close values
        distractors.add(str(answer + 1))
        distractors.add(str(max(1, answer - 1)))

        distractors.discard(str(answer))
        return list(distractors)[:3]

    def _generate_proportion_distractors(
        self,
        x: int,
        a: int,
        b: int,
        c: int
    ) -> List[str]:
        """Generate distractors for proportion problems."""
        distractors = set()

        # Cross multiplication errors
        distractors.add(str(a * c))  # Forgot to divide
        distractors.add(str(b * c // a) if a != 0 else str(b * c))

        # Other common errors
        distractors.add(str(x + 1))
        distractors.add(str(max(1, x - 1)))
        distractors.add(str(a + b + c))

        distractors.discard(str(x))
        return list(distractors)[:3]

    def _generate_part_whole_distractors(
        self,
        answer: int,
        part_a: int,
        part_b: int,
        total: int
    ) -> List[str]:
        """Generate distractors for part-to-whole problems."""
        distractors = set()

        # Other part
        other = total - answer
        if other != answer:
            distractors.add(str(other))

        # Just the ratio part
        distractors.add(str(part_a))
        distractors.add(str(part_b))

        # Total divided by one part
        distractors.add(str(total // (part_a + part_b)))

        # Close values
        distractors.add(str(answer + 5))
        distractors.add(str(max(1, answer - 5)))

        distractors.discard(str(answer))
        return list(distractors)[:3]

    def _generate_scale_distractors(
        self,
        answer: int,
        scale: Tuple[int, int],
        map_dist: int,
        actual_dist: int
    ) -> List[str]:
        """Generate distractors for scale problems."""
        distractors = set()

        # Wrong direction
        if answer == actual_dist:
            distractors.add(str(map_dist))
        else:
            distractors.add(str(actual_dist))

        # Using scale incorrectly
        distractors.add(str(answer * scale[0]))
        distractors.add(str(answer // scale[0]) if scale[0] != 0 else str(answer))

        # Close values
        distractors.add(str(answer + 10))
        distractors.add(str(max(1, answer - 10)))

        distractors.discard(str(answer))
        return list(distractors)[:3]
