"""
Systems of Equations Question Generator.

Generates systems of linear equations with two or three variables,
ensuring integer solutions for clean answers.
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
class SystemsOfEquationsGenerator(QuestionGenerator):
    """
    Generator for systems of equations questions.

    Supports:
    - Two-variable systems (2x2)
    - Three-variable systems (3x3)
    - Word problems that reduce to systems

    All systems are designed to have integer solutions.
    """

    GRADE_CONFIG = {
        7: {"max_coef": 10, "max_sol": 10, "types": ["two_variable_easy"]},
        8: {"max_coef": 15, "max_sol": 15, "types": ["two_variable_easy", "two_variable"]},
        9: {"max_coef": 20, "max_sol": 20, "types": ["two_variable", "two_variable_word"]},
        10: {"max_coef": 25, "max_sol": 25, "types": ["two_variable", "two_variable_word", "three_variable"]},
        11: {"max_coef": 30, "max_sol": 30, "types": ["two_variable", "three_variable"]},
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.SYSTEMS_OF_EQUATIONS

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.TWO_VARIABLE, OperationType.THREE_VARIABLE]

    def generate(self, difficulty: float = 0.5, operation: Optional[OperationType] = None,
                 grade_level: Optional[int] = None, seed: Optional[int] = None, **kwargs) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)
        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        if problem_type == "two_variable_easy":
            return self._generate_two_var_easy(difficulty, config, grade_level)
        elif problem_type == "two_variable":
            return self._generate_two_var(difficulty, config, grade_level)
        elif problem_type == "two_variable_word":
            return self._generate_two_var_word(difficulty, config, grade_level)
        elif problem_type == "three_variable":
            return self._generate_three_var(difficulty, config, grade_level)
        return self._generate_two_var_easy(difficulty, config, grade_level)

    def _generate_two_var_easy(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        """x + y = a, x - y = b pattern"""
        x = random.randint(1, max(3, int(config["max_sol"] * difficulty)))
        y = random.randint(1, max(3, int(config["max_sol"] * difficulty)))

        s = x + y
        d = x - y

        eq1 = f"x + y = {s}"
        eq2 = f"x - y = {d}"
        expression = f"Solve the system:\n{eq1}\n{eq2}"
        answer = f"x = {x}, y = {y}"

        distractors = [
            f"x = {y}, y = {x}",
            f"x = {x + 1}, y = {y - 1}",
            f"x = {x - 1}, y = {y + 1}",
        ]
        distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.25 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="systems_two_var_easy",
            question_type=self.question_type,
            operation=OperationType.TWO_VARIABLE,
            expression=expression,
            expression_latex=f"$\\begin{{cases}} x + y = {s} \\\\ x - y = {d} \\end{{cases}}$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"x": x, "y": y, "type": "two_variable_easy", "grade_level": grade_level},
        )

    def _generate_two_var(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        """ax + by = c, dx + ey = f pattern"""
        x = random.randint(1, max(2, int(config["max_sol"] * 0.5 * (0.3 + 0.7 * difficulty))))
        y = random.randint(1, max(2, int(config["max_sol"] * 0.5 * (0.3 + 0.7 * difficulty))))

        a = random.randint(1, min(8, config["max_coef"]))
        b = random.randint(1, min(8, config["max_coef"]))
        d = random.randint(1, min(8, config["max_coef"]))
        e = random.randint(1, min(8, config["max_coef"]))

        # Ensure system has unique solution (det != 0)
        while a * e - b * d == 0:
            e = random.randint(1, min(8, config["max_coef"]))

        c = a * x + b * y
        f = d * x + e * y

        eq1 = f"{a}x + {b}y = {c}"
        eq2 = f"{d}x + {e}y = {f}"
        expression = f"Solve the system:\n{eq1}\n{eq2}"
        answer = f"x = {x}, y = {y}"

        distractors = [
            f"x = {y}, y = {x}",
            f"x = {x + 1}, y = {y}",
            f"x = {x}, y = {y + 1}",
        ]
        distractors = [dd for dd in distractors if dd != answer][:3]

        calc_difficulty = 0.45 + 0.25 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="systems_two_var",
            question_type=self.question_type,
            operation=OperationType.TWO_VARIABLE,
            expression=expression,
            expression_latex=f"$\\begin{{cases}} {a}x + {b}y = {c} \\\\ {d}x + {e}y = {f} \\end{{cases}}$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"x": x, "y": y, "a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "type": "two_variable", "grade_level": grade_level},
        )

    def _generate_two_var_word(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        """Word problem that reduces to a 2x2 system"""
        templates = [
            {
                "text": "The sum of two numbers is {s}. Their difference is {d}. Find the two numbers.",
                "gen": lambda: self._word_sum_diff(config, difficulty),
            },
            {
                "text": "A store sells apples for {pa} TL each and oranges for {po} TL each. You buy {ta} total fruits and pay {total} TL. How many apples did you buy?",
                "gen": lambda: self._word_shopping(config, difficulty),
            },
        ]

        template = random.choice(templates)
        data = template["gen"]()
        expression = template["text"].format(**data["format_args"])
        answer = data["answer"]
        distractors = data["distractors"]

        calc_difficulty = 0.5 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="systems_word_problem",
            question_type=self.question_type,
            operation=OperationType.TWO_VARIABLE,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors[:3],
            all_options=self._shuffle_options(answer, distractors[:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"type": "two_variable_word", "grade_level": grade_level, **data.get("params", {})},
        )

    def _word_sum_diff(self, config, difficulty):
        x = random.randint(3, max(5, int(config["max_sol"] * 0.5 * difficulty)))
        y = random.randint(1, x - 1)
        return {
            "format_args": {"s": x + y, "d": x - y},
            "answer": f"{x} and {y}",
            "distractors": [f"{x+1} and {y-1}", f"{y} and {x}", f"{x+y} and {x-y}"],
            "params": {"x": x, "y": y},
        }

    def _word_shopping(self, config, difficulty):
        apple_price = random.randint(2, 5)
        orange_price = random.randint(1, apple_price - 1) if apple_price > 1 else 1
        apples = random.randint(2, 8)
        oranges = random.randint(2, 8)
        total_fruits = apples + oranges
        total_cost = apples * apple_price + oranges * orange_price
        return {
            "format_args": {"pa": apple_price, "po": orange_price, "ta": total_fruits, "total": total_cost},
            "answer": str(apples),
            "distractors": [str(oranges), str(apples + 1), str(max(1, apples - 1))],
            "params": {"apples": apples, "oranges": oranges},
        }

    def _generate_three_var(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        """3x3 system with integer solutions"""
        x = random.randint(1, max(2, int(config["max_sol"] * 0.3 * (0.3 + 0.7 * difficulty))))
        y = random.randint(1, max(2, int(config["max_sol"] * 0.3 * (0.3 + 0.7 * difficulty))))
        z = random.randint(1, max(2, int(config["max_sol"] * 0.3 * (0.3 + 0.7 * difficulty))))

        # Generate 3 equations from solutions
        coeffs = []
        for _ in range(3):
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            c = random.randint(1, 5)
            r = a * x + b * y + c * z
            coeffs.append((a, b, c, r))

        eq_strs = []
        for a, b, c, r in coeffs:
            eq_strs.append(f"{a}x + {b}y + {c}z = {r}")

        expression = "Solve the system:\n" + "\n".join(eq_strs)
        latex_eqs = " \\\\ ".join(f"{a}x + {b}y + {c}z = {r}" for a, b, c, r in coeffs)
        answer = f"x = {x}, y = {y}, z = {z}"

        distractors = [
            f"x = {y}, y = {x}, z = {z}",
            f"x = {x+1}, y = {y}, z = {z}",
            f"x = {x}, y = {y+1}, z = {z-1}" if z > 1 else f"x = {x}, y = {y}, z = {z+1}",
        ]
        distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.7 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="systems_three_var",
            question_type=self.question_type,
            operation=OperationType.THREE_VARIABLE,
            expression=expression,
            expression_latex=f"$\\begin{{cases}} {latex_eqs} \\end{{cases}}$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"x": x, "y": y, "z": z, "type": "three_variable", "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        t = parameters.get("type", "two_variable")
        if "z" in parameters:
            return f"x = {parameters['x']}, y = {parameters['y']}, z = {parameters['z']}"
        return f"x = {parameters.get('x', 0)}, y = {parameters.get('y', 0)}"

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return []

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "two_variable")
        return {"two_variable_easy": 0.3, "two_variable": 0.5, "two_variable_word": 0.6, "three_variable": 0.8}.get(ptype, 0.5)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.2: return 7
        elif difficulty < 0.4: return 8
        elif difficulty < 0.6: return 9
        elif difficulty < 0.8: return 10
        else: return 11

    def _get_grade_config(self, grade_level: int) -> Dict:
        return self.GRADE_CONFIG[max(7, min(11, grade_level))]
