"""
Inequalities Question Generator.

Generates linear inequality, compound inequality, and absolute value
inequality questions with deterministic correct answers.
"""

import random
from typing import List, Optional, Dict, Any

from ..base import (
    QuestionGenerator,
    QuestionType,
    OperationType,
    AnswerFormat,
    GeneratedQuestion,
)
from ..registry import register_generator


@register_generator
class InequalitiesGenerator(QuestionGenerator):
    """
    Generator for inequality questions.

    Supports:
    - One-step linear inequalities
    - Two-step linear inequalities
    - Compound inequalities (AND / OR)
    - Absolute value inequalities
    """

    GRADE_CONFIG = {
        7: {"max_coef": 10, "types": ["one_step"]},
        8: {"max_coef": 15, "types": ["one_step", "two_step"]},
        9: {"max_coef": 20, "types": ["one_step", "two_step", "compound"]},
        10: {"max_coef": 25, "types": ["two_step", "compound", "absolute_value"]},
        11: {"max_coef": 30, "types": ["two_step", "compound", "absolute_value"]},
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.INEQUALITIES

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.LINEAR_INEQUALITY, OperationType.COMPOUND_INEQUALITY,
                OperationType.ABSOLUTE_VALUE_INEQUALITY]

    def generate(self, difficulty: float = 0.5, operation: Optional[OperationType] = None,
                 grade_level: Optional[int] = None, seed: Optional[int] = None, **kwargs) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)
        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        generators = {
            "one_step": self._generate_one_step,
            "two_step": self._generate_two_step,
            "compound": self._generate_compound,
            "absolute_value": self._generate_absolute_value,
        }
        return generators.get(problem_type, self._generate_one_step)(difficulty, config, grade_level)

    def _generate_one_step(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        op = random.choice(["add", "subtract", "multiply", "divide"])
        max_c = max(3, int(config["max_coef"] * (0.3 + 0.7 * difficulty)))
        ineq_symbol = random.choice(["<", ">", "≤", "≥"])

        if op == "add":
            a = random.randint(1, max_c)
            b = random.randint(a + 1, max_c + a)
            answer_val = b - a
            expression = f"x + {a} {ineq_symbol} {b}"
            answer = f"x {ineq_symbol} {answer_val}"
        elif op == "subtract":
            a = random.randint(1, max_c)
            b = random.randint(1, max_c)
            answer_val = b + a
            expression = f"x - {a} {ineq_symbol} {b}"
            answer = f"x {ineq_symbol} {answer_val}"
        elif op == "multiply":
            a = random.randint(2, min(10, max_c))
            result = random.randint(2, max_c)
            b = a * result
            expression = f"{a}x {ineq_symbol} {b}"
            answer = f"x {ineq_symbol} {result}"
        else:
            a = random.randint(2, min(10, max_c))
            result = random.randint(1, max_c // 2)
            b = result
            expression = f"x/{a} {ineq_symbol} {b}"
            answer_val = a * b
            answer = f"x {ineq_symbol} {answer_val}"

        distractors = self._make_ineq_distractors(answer, ineq_symbol)
        calc_difficulty = 0.2 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="inequalities_one_step",
            question_type=self.question_type,
            operation=OperationType.LINEAR_INEQUALITY,
            expression=f"Solve: {expression}",
            expression_latex=f"${expression}$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"type": "one_step", "answer": answer, "grade_level": grade_level},
        )

    def _generate_two_step(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_c = max(3, int(config["max_coef"] * (0.3 + 0.7 * difficulty)))
        ineq_symbol = random.choice(["<", ">", "≤", "≥"])

        a = random.randint(2, min(8, max_c))
        b = random.randint(1, max_c)
        x_val = random.randint(1, max_c // a + 1)
        c = a * x_val + b

        neg_coef = random.random() < 0.3 and difficulty > 0.5
        if neg_coef:
            a = -a
            c = a * x_val + b
            # Flip inequality when dividing by negative
            flip = {"<": ">", ">": "<", "≤": "≥", "≥": "≤"}
            answer_symbol = flip[ineq_symbol]
        else:
            answer_symbol = ineq_symbol

        if b >= 0:
            expression = f"{a}x + {b} {ineq_symbol} {c}"
        else:
            expression = f"{a}x - {abs(b)} {ineq_symbol} {c}"

        answer = f"x {answer_symbol} {x_val}"

        distractors = self._make_ineq_distractors(answer, answer_symbol)
        calc_difficulty = 0.35 + 0.2 * difficulty
        if neg_coef:
            calc_difficulty += 0.1

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="inequalities_two_step",
            question_type=self.question_type,
            operation=OperationType.LINEAR_INEQUALITY,
            expression=f"Solve: {expression}",
            expression_latex=f"${expression}$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"type": "two_step", "answer": answer, "neg_coef": neg_coef, "grade_level": grade_level},
        )

    def _generate_compound(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_c = max(5, int(config["max_coef"] * (0.3 + 0.7 * difficulty)))
        compound_type = random.choice(["and", "or"])

        a = random.randint(1, max_c // 2)
        b = random.randint(a + 2, max_c)

        if compound_type == "and":
            expression = f"{a} < x < {b}"
            answer = f"{a} < x < {b}"
            alt_expression = f"x > {a} AND x < {b}"
            distractors = [
                f"{a} ≤ x ≤ {b}",
                f"x < {a} or x > {b}",
                f"{a-1} < x < {b+1}",
            ]
        else:
            expression = f"x < {a} or x > {b}"
            answer = f"x < {a} or x > {b}"
            alt_expression = expression
            distractors = [
                f"x ≤ {a} or x ≥ {b}",
                f"{a} < x < {b}",
                f"x < {a+1} or x > {b-1}",
            ]

        distractors = [d for d in distractors if d != answer][:3]
        calc_difficulty = 0.5 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="inequalities_compound",
            question_type=self.question_type,
            operation=OperationType.COMPOUND_INEQUALITY,
            expression=f"Express the solution: {alt_expression}",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"type": "compound", "compound_type": compound_type, "answer": answer, "grade_level": grade_level},
        )

    def _generate_absolute_value(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_c = max(3, int(config["max_coef"] * (0.3 + 0.7 * difficulty)))
        ineq_type = random.choice(["less", "greater"])

        a = random.randint(0, max_c // 2)
        b = random.randint(1, max_c)

        if ineq_type == "less":
            expression = f"|x - {a}| < {b}"
            low = a - b
            high = a + b
            answer = f"{low} < x < {high}"
            distractors = [
                f"x < {high}",
                f"x < {low} or x > {high}",
                f"{low-1} < x < {high+1}",
            ]
        else:
            expression = f"|x - {a}| > {b}"
            low = a - b
            high = a + b
            answer = f"x < {low} or x > {high}"
            distractors = [
                f"{low} < x < {high}",
                f"x > {high}",
                f"x < {low-1} or x > {high+1}",
            ]

        distractors = [d for d in distractors if d != answer][:3]
        calc_difficulty = 0.6 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="inequalities_absolute_value",
            question_type=self.question_type,
            operation=OperationType.ABSOLUTE_VALUE_INEQUALITY,
            expression=f"Solve: {expression}",
            expression_latex=f"${expression}$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"type": "absolute_value", "answer": answer, "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        return parameters.get("answer", "")

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return []

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "one_step")
        return {"one_step": 0.25, "two_step": 0.45, "compound": 0.6, "absolute_value": 0.7}.get(ptype, 0.4)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.2: return 7
        elif difficulty < 0.4: return 8
        elif difficulty < 0.6: return 9
        elif difficulty < 0.8: return 10
        else: return 11

    def _get_grade_config(self, grade_level: int) -> Dict:
        return self.GRADE_CONFIG[max(7, min(11, grade_level))]

    def _make_ineq_distractors(self, answer: str, symbol: str) -> List[str]:
        """Generate distractors by flipping symbol or changing value."""
        flip = {"<": ">", ">": "<", "≤": "≥", "≥": "≤"}
        distractors = []
        # Flip the inequality
        flipped = answer.replace(symbol, flip.get(symbol, symbol), 1)
        if flipped != answer:
            distractors.append(flipped)
        # Change value
        parts = answer.split(symbol)
        if len(parts) == 2:
            try:
                val = int(parts[1].strip())
                distractors.append(f"x {symbol} {val + 1}")
                distractors.append(f"x {symbol} {val - 1}")
            except ValueError:
                distractors.append(answer + " (wrong)")
                distractors.append("No solution")
        while len(distractors) < 3:
            distractors.append("No solution")
        return [d for d in distractors if d != answer][:3]
