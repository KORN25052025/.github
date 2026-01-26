"""
Functions Question Generator.

Generates questions about linear functions, quadratic functions,
domain/range, composition, and inverse functions.
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
class FunctionsGenerator(QuestionGenerator):
    """
    Generator for function questions.

    Supports:
    - Evaluating linear functions f(x) = ax + b
    - Evaluating quadratic functions f(x) = ax² + bx + c
    - Finding domain and range
    - Function composition f(g(x))
    - Inverse functions f⁻¹(x)
    """

    GRADE_CONFIG = {
        8: {"max_coef": 10, "types": ["linear_eval"]},
        9: {"max_coef": 15, "types": ["linear_eval", "quadratic_eval", "domain_range"]},
        10: {"max_coef": 20, "types": ["linear_eval", "quadratic_eval", "domain_range", "composition"]},
        11: {"max_coef": 25, "types": ["quadratic_eval", "domain_range", "composition", "inverse"]},
        12: {"max_coef": 30, "types": ["quadratic_eval", "composition", "inverse"]},
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.FUNCTIONS

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.LINEAR_FUNCTION, OperationType.QUADRATIC_FUNCTION,
                OperationType.DOMAIN_RANGE, OperationType.COMPOSITION,
                OperationType.INVERSE_FUNCTION]

    def generate(self, difficulty: float = 0.5, operation: Optional[OperationType] = None,
                 grade_level: Optional[int] = None, seed: Optional[int] = None, **kwargs) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)
        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        generators = {
            "linear_eval": self._generate_linear_eval,
            "quadratic_eval": self._generate_quadratic_eval,
            "domain_range": self._generate_domain_range,
            "composition": self._generate_composition,
            "inverse": self._generate_inverse,
        }
        return generators.get(problem_type, self._generate_linear_eval)(difficulty, config, grade_level)

    def _generate_linear_eval(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_c = max(3, int(config["max_coef"] * (0.3 + 0.7 * difficulty)))
        a = random.randint(1, max_c)
        b = random.randint(-max_c, max_c)
        x_val = random.randint(-5, 10)
        answer = a * x_val + b

        b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
        func_str = f"f(x) = {a}x {b_str}"
        expression = f"If {func_str}, find f({x_val})"

        distractors = self._make_distractors(answer, [
            a * x_val - b, a + b, x_val * b + a, answer + 1, answer - 1,
        ])
        calc_difficulty = 0.2 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="functions_linear_eval",
            question_type=self.question_type,
            operation=OperationType.LINEAR_FUNCTION,
            expression=expression,
            expression_latex=f"$f(x) = {a}x {b_str}$, $f({x_val}) = ?$",
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"a": a, "b": b, "x": x_val, "answer": answer, "type": "linear_eval", "grade_level": grade_level},
        )

    def _generate_quadratic_eval(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        a = random.randint(1, min(5, config["max_coef"]))
        b = random.randint(-5, 5)
        c = random.randint(-10, 10)
        x_val = random.randint(-4, 4)
        answer = a * x_val * x_val + b * x_val + c

        parts = [f"{a}x²"]
        if b > 0:
            parts.append(f"+ {b}x")
        elif b < 0:
            parts.append(f"- {abs(b)}x")
        if c > 0:
            parts.append(f"+ {c}")
        elif c < 0:
            parts.append(f"- {abs(c)}")

        func_str = f"f(x) = {' '.join(parts)}"
        expression = f"If {func_str}, find f({x_val})"

        distractors = self._make_distractors(answer, [
            a * x_val + b * x_val + c,  # Forgot to square
            a * x_val * x_val - b * x_val + c,  # Sign error on b
            answer + a, answer - c, abs(answer),
        ])
        calc_difficulty = 0.4 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="functions_quadratic_eval",
            question_type=self.question_type,
            operation=OperationType.QUADRATIC_FUNCTION,
            expression=expression,
            expression_latex=f"$f(x) = {a}x^2 {'+' if b >= 0 else '-'} {abs(b)}x {'+' if c >= 0 else '-'} {abs(c)}$",
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"a": a, "b": b, "c": c, "x": x_val, "answer": answer, "type": "quadratic_eval", "grade_level": grade_level},
        )

    def _generate_domain_range(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        func_type = random.choice(["sqrt", "fraction", "linear"])

        if func_type == "sqrt":
            a = random.randint(1, 5)
            b = random.randint(-10, 10)
            expression = f"Find the domain of f(x) = √({a}x + {b})" if b >= 0 else f"Find the domain of f(x) = √({a}x - {abs(b)})"
            # ax + b >= 0 => x >= -b/a
            boundary = -b / a
            if boundary == int(boundary):
                boundary = int(boundary)
                answer = f"x ≥ {boundary}"
            else:
                from fractions import Fraction
                frac = Fraction(-b, a)
                answer = f"x ≥ {frac}"

            distractors = [
                f"x > {boundary}" if isinstance(boundary, int) else f"x > 0",
                "All real numbers",
                f"x ≤ {boundary}" if isinstance(boundary, int) else f"x ≥ 0",
            ]
        elif func_type == "fraction":
            a = random.randint(1, 5)
            b = random.randint(-10, 10)
            expression = f"Find the domain of f(x) = 1/({a}x + {b})" if b >= 0 else f"Find the domain of f(x) = 1/({a}x - {abs(b)})"
            excluded = -b / a
            if excluded == int(excluded):
                excluded = int(excluded)
            answer = f"x ≠ {excluded}"
            distractors = [
                "All real numbers",
                f"x > {excluded}",
                f"x ≥ {excluded}",
            ]
        else:
            a = random.randint(1, 5)
            b = random.randint(-10, 10)
            expression = f"Find the domain of f(x) = {a}x + {b}" if b >= 0 else f"Find the domain of f(x) = {a}x - {abs(b)}"
            answer = "All real numbers"
            distractors = [
                "x > 0",
                "x ≥ 0",
                f"x ≠ {-b}",
            ]

        distractors = [d for d in distractors if d != answer][:3]
        calc_difficulty = 0.4 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="functions_domain_range",
            question_type=self.question_type,
            operation=OperationType.DOMAIN_RANGE,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"func_type": func_type, "answer": answer, "type": "domain_range", "grade_level": grade_level},
        )

    def _generate_composition(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        # f(x) = ax + b, g(x) = cx + d
        a = random.randint(1, min(5, config["max_coef"]))
        b = random.randint(-5, 5)
        c = random.randint(1, min(5, config["max_coef"]))
        d = random.randint(-5, 5)
        x_val = random.randint(-3, 5)

        g_of_x = c * x_val + d
        answer = a * g_of_x + b

        b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
        d_str = f"+ {d}" if d >= 0 else f"- {abs(d)}"
        expression = f"If f(x) = {a}x {b_str} and g(x) = {c}x {d_str}, find f(g({x_val}))"

        distractors = self._make_distractors(answer, [
            c * (a * x_val + b) + d,  # g(f(x)) instead
            a * x_val + b + c * x_val + d,  # f(x) + g(x)
            a * c * x_val + b + d,
            answer + 1, answer - 1,
        ])
        calc_difficulty = 0.55 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="functions_composition",
            question_type=self.question_type,
            operation=OperationType.COMPOSITION,
            expression=expression,
            expression_latex=f"$f(g({x_val}))$",
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"a": a, "b": b, "c": c, "d": d, "x": x_val, "answer": answer, "type": "composition", "grade_level": grade_level},
        )

    def _generate_inverse(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        # f(x) = ax + b => f⁻¹(x) = (x - b) / a
        a = random.randint(1, min(8, config["max_coef"]))
        b = random.randint(-10, 10)
        # Choose x_val so answer is integer: (x_val - b) must be divisible by a
        answer = random.randint(-5, 10)
        x_val = a * answer + b

        b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
        expression = f"If f(x) = {a}x {b_str}, find f⁻¹({x_val})"

        distractors = self._make_distractors(answer, [
            a * x_val + b,  # f(x) instead of f⁻¹(x)
            x_val - b,  # Forgot to divide
            (x_val + b) // a if a != 0 else 0,  # Added b instead of subtracting
            answer + 1, answer - 1,
        ])
        calc_difficulty = 0.6 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="functions_inverse",
            question_type=self.question_type,
            operation=OperationType.INVERSE_FUNCTION,
            expression=expression,
            expression_latex=f"$f^{{-1}}({x_val})$",
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"a": a, "b": b, "x_val": x_val, "answer": answer, "type": "inverse", "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        return parameters.get("answer", 0)

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return []

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "linear_eval")
        return {"linear_eval": 0.25, "quadratic_eval": 0.45, "domain_range": 0.5, "composition": 0.6, "inverse": 0.65}.get(ptype, 0.4)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.2: return 8
        elif difficulty < 0.4: return 9
        elif difficulty < 0.6: return 10
        elif difficulty < 0.8: return 11
        else: return 12

    def _get_grade_config(self, grade_level: int) -> Dict:
        return self.GRADE_CONFIG[max(8, min(12, grade_level))]

    def _make_distractors(self, answer: int, candidates: List) -> List[str]:
        distractors = set()
        for c in candidates:
            v = int(c) if isinstance(c, float) and c == int(c) else c
            if isinstance(v, (int, float)) and str(int(v)) != str(answer):
                distractors.add(str(int(v)))
        while len(distractors) < 3:
            offset = random.choice([-3, -2, -1, 1, 2, 3])
            v = answer + offset
            if str(v) not in distractors:
                distractors.add(str(v))
        return list(distractors)[:3]
