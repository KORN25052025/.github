"""
Exponents & Roots Question Generator.

Generates questions about powers, square roots, cube roots, and scientific notation
with deterministic correct answers and pedagogically meaningful distractors.
"""

import random
import math
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
class ExponentsGenerator(QuestionGenerator):
    """
    Generator for exponents and roots questions.

    Supports:
    - Integer exponentiation (a^n)
    - Square roots
    - Cube roots
    - Scientific notation
    - Exponent rules (product, quotient, power of power)

    Difficulty is controlled through:
    - Base and exponent magnitude
    - Perfect vs non-perfect roots
    - Scientific notation digit count
    """

    GRADE_CONFIG = {
        6: {
            "max_base": 10,
            "max_exp": 3,
            "types": ["power", "square_root"],
        },
        7: {
            "max_base": 12,
            "max_exp": 4,
            "types": ["power", "square_root", "cube_root"],
        },
        8: {
            "max_base": 15,
            "max_exp": 5,
            "types": ["power", "square_root", "cube_root", "exponent_rules"],
        },
        9: {
            "max_base": 20,
            "max_exp": 6,
            "types": ["power", "square_root", "cube_root", "exponent_rules", "scientific_notation"],
        },
        10: {
            "max_base": 25,
            "max_exp": 8,
            "types": ["power", "square_root", "cube_root", "exponent_rules", "scientific_notation"],
        },
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.EXPONENTS

    @property
    def supported_operations(self) -> List[OperationType]:
        return [
            OperationType.EXPONENTIATION,
            OperationType.SQUARE_ROOT,
            OperationType.CUBE_ROOT,
            OperationType.SCIENTIFIC_NOTATION,
        ]

    def generate(
        self,
        difficulty: float = 0.5,
        operation: Optional[OperationType] = None,
        grade_level: Optional[int] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)

        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)

        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        if problem_type == "power":
            return self._generate_power(difficulty, config, grade_level)
        elif problem_type == "square_root":
            return self._generate_square_root(difficulty, config, grade_level)
        elif problem_type == "cube_root":
            return self._generate_cube_root(difficulty, config, grade_level)
        elif problem_type == "exponent_rules":
            return self._generate_exponent_rules(difficulty, config, grade_level)
        elif problem_type == "scientific_notation":
            return self._generate_scientific_notation(difficulty, config, grade_level)
        else:
            return self._generate_power(difficulty, config, grade_level)

    def _generate_power(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_base = max(2, int(config["max_base"] * (0.3 + 0.7 * difficulty)))
        base = random.randint(2, max_base)
        exp = random.randint(2, min(config["max_exp"], 2 + int(difficulty * 4)))
        answer = base ** exp

        expression = f"{base}^{exp} = ?"
        expression_latex = f"${base}^{{{exp}}}$"

        distractors = self._make_distractors(answer, [
            base * exp,
            base ** (exp - 1),
            base ** (exp + 1),
            (base + 1) ** exp,
            (base - 1) ** exp if base > 1 else base ** exp + 1,
        ])

        calc_difficulty = 0.2 + 0.15 * (base / config["max_base"]) + 0.15 * (exp / config["max_exp"])

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="exponents_power",
            question_type=self.question_type,
            operation=OperationType.EXPONENTIATION,
            expression=f"Calculate: {expression}",
            expression_latex=expression_latex,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"base": base, "exponent": exp, "answer": answer, "type": "power", "grade_level": grade_level},
        )

    def _generate_square_root(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_root = max(2, int(config["max_base"] * (0.3 + 0.7 * difficulty)))
        root = random.randint(2, max_root)
        radicand = root * root

        expression = f"√{radicand} = ?"
        expression_latex = f"$\\sqrt{{{radicand}}}$"

        distractors = self._make_distractors(root, [
            root + 1, root - 1, radicand // 2, root * 2, radicand // root + 1
        ])

        calc_difficulty = 0.25 + 0.2 * (root / config["max_base"])

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="exponents_square_root",
            question_type=self.question_type,
            operation=OperationType.SQUARE_ROOT,
            expression=f"Calculate: {expression}",
            expression_latex=expression_latex,
            correct_answer=str(root),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(root), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"radicand": radicand, "root": root, "type": "square_root", "grade_level": grade_level},
        )

    def _generate_cube_root(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_root = max(2, int(min(10, config["max_base"]) * (0.3 + 0.7 * difficulty)))
        root = random.randint(2, max_root)
        radicand = root ** 3

        expression = f"∛{radicand} = ?"
        expression_latex = f"$\\sqrt[3]{{{radicand}}}$"

        distractors = self._make_distractors(root, [
            root + 1, root - 1, root * 3, radicand // 3, root ** 2
        ])

        calc_difficulty = 0.4 + 0.2 * (root / 10)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="exponents_cube_root",
            question_type=self.question_type,
            operation=OperationType.CUBE_ROOT,
            expression=f"Calculate: {expression}",
            expression_latex=expression_latex,
            correct_answer=str(root),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(root), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"radicand": radicand, "root": root, "type": "cube_root", "grade_level": grade_level},
        )

    def _generate_exponent_rules(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        rule = random.choice(["product", "quotient", "power_of_power"])
        base = random.randint(2, min(8, config["max_base"]))

        if rule == "product":
            m = random.randint(2, 5)
            n = random.randint(2, 5)
            answer = m + n
            expression = f"{base}^{m} × {base}^{n} = {base}^?"
            expression_latex = f"${base}^{{{m}}} \\times {base}^{{{n}}} = {base}^{{?}}$"
            wrong = [m * n, abs(m - n), max(m, n), m + n + 1, m + n - 1]
        elif rule == "quotient":
            m = random.randint(4, 8)
            n = random.randint(2, m - 1)
            answer = m - n
            expression = f"{base}^{m} ÷ {base}^{n} = {base}^?"
            expression_latex = f"${base}^{{{m}}} \\div {base}^{{{n}}} = {base}^{{?}}$"
            wrong = [m + n, m * n, m // n if n != 0 else 1, m - n + 1, m - n - 1]
        else:  # power_of_power
            m = random.randint(2, 4)
            n = random.randint(2, 4)
            answer = m * n
            expression = f"({base}^{m})^{n} = {base}^?"
            expression_latex = f"$({base}^{{{m}}})^{{{n}}} = {base}^{{?}}$"
            wrong = [m + n, m ** n, abs(m - n), m * n + 1, m * n - 1]

        distractors = self._make_distractors(answer, wrong)
        calc_difficulty = 0.5 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id=f"exponents_rule_{rule}",
            question_type=self.question_type,
            operation=OperationType.EXPONENTIATION,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"base": base, "rule": rule, "answer": answer, "type": "exponent_rules", "grade_level": grade_level},
        )

    def _generate_scientific_notation(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        direction = random.choice(["to_scientific", "from_scientific"])
        exp = random.randint(2, 3 + int(difficulty * 6))
        coef = random.randint(1, 9)

        if random.random() < 0.5 and difficulty > 0.4:
            coef_decimal = coef + random.randint(1, 9) / 10
        else:
            coef_decimal = float(coef)

        number = coef_decimal * (10 ** exp)

        if direction == "to_scientific":
            expression = f"Write {int(number) if number == int(number) else number} in scientific notation"
            if coef_decimal == int(coef_decimal):
                answer = f"{int(coef_decimal)} × 10^{exp}"
            else:
                answer = f"{coef_decimal} × 10^{exp}"
            expression_latex = f"${int(number) if number == int(number) else number}$"
        else:
            if coef_decimal == int(coef_decimal):
                sci_str = f"{int(coef_decimal)} × 10^{exp}"
            else:
                sci_str = f"{coef_decimal} × 10^{exp}"
            expression = f"Convert {sci_str} to standard form"
            answer = str(int(number) if number == int(number) else number)
            expression_latex = f"${coef_decimal} \\times 10^{{{exp}}}$"

        distractors = [
            str(int(coef_decimal * 10 ** (exp + 1))),
            str(int(coef_decimal * 10 ** (exp - 1))) if exp > 1 else str(int(coef_decimal * 100)),
            str(int(number) + 10 ** (exp - 1)) if number == int(number) else str(number + 1),
        ]
        distractors = [d for d in distractors if d != answer][:3]
        while len(distractors) < 3:
            distractors.append(str(int(number) + random.randint(1, 100)))

        calc_difficulty = 0.45 + 0.25 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="exponents_scientific_notation",
            question_type=self.question_type,
            operation=OperationType.SCIENTIFIC_NOTATION,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"number": number, "coefficient": coef_decimal, "exponent": exp, "direction": direction, "type": "scientific_notation", "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        return parameters.get("answer", parameters.get("root", 0))

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return self._make_distractors(int(correct_answer) if str(correct_answer).isdigit() else 0, [])

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "power")
        base_diff = {"power": 0.3, "square_root": 0.3, "cube_root": 0.45, "exponent_rules": 0.55, "scientific_notation": 0.5}
        return base_diff.get(ptype, 0.4)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.2: return 6
        elif difficulty < 0.4: return 7
        elif difficulty < 0.6: return 8
        elif difficulty < 0.8: return 9
        else: return 10

    def _get_grade_config(self, grade_level: int) -> Dict:
        grade = max(6, min(10, grade_level))
        return self.GRADE_CONFIG[grade]

    def _make_distractors(self, answer: int, candidates: List) -> List[str]:
        distractors = set()
        for c in candidates:
            val = int(c) if isinstance(c, float) else c
            if val != answer and val > 0:
                distractors.add(str(val))
        while len(distractors) < 3:
            offset = random.choice([-3, -2, -1, 1, 2, 3])
            val = answer + offset
            if val > 0 and str(val) not in distractors:
                distractors.add(str(val))
        return list(distractors)[:3]
