"""
Trigonometry Question Generator.

Generates questions about sine, cosine, tangent, and basic
trigonometric equations using special angle values.
"""

import random
import math
from typing import List, Optional, Dict, Any
from fractions import Fraction

from ..base import (
    QuestionGenerator,
    QuestionType,
    OperationType,
    AnswerFormat,
    GeneratedQuestion,
)
from ..registry import register_generator


@register_generator
class TrigonometryGenerator(QuestionGenerator):
    """
    Generator for trigonometry questions.

    Supports:
    - Evaluating sin, cos, tan at special angles
    - Finding missing sides using trig ratios
    - Basic trig identities
    - Solving simple trig equations
    """

    # Special angles and their exact trig values
    SPECIAL_ANGLES = {
        0: {"sin": "0", "cos": "1", "tan": "0"},
        30: {"sin": "1/2", "cos": "√3/2", "tan": "√3/3"},
        45: {"sin": "√2/2", "cos": "√2/2", "tan": "1"},
        60: {"sin": "√3/2", "cos": "1/2", "tan": "√3"},
        90: {"sin": "1", "cos": "0", "tan": "undefined"},
        120: {"sin": "√3/2", "cos": "-1/2", "tan": "-√3"},
        135: {"sin": "√2/2", "cos": "-√2/2", "tan": "-1"},
        150: {"sin": "1/2", "cos": "-√3/2", "tan": "-√3/3"},
        180: {"sin": "0", "cos": "-1", "tan": "0"},
        270: {"sin": "-1", "cos": "0", "tan": "undefined"},
        360: {"sin": "0", "cos": "1", "tan": "0"},
    }

    GRADE_CONFIG = {
        9: {"types": ["special_angle", "right_triangle"]},
        10: {"types": ["special_angle", "right_triangle", "identity"]},
        11: {"types": ["special_angle", "right_triangle", "identity", "trig_equation"]},
        12: {"types": ["special_angle", "identity", "trig_equation"]},
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.TRIGONOMETRY

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.SINE, OperationType.COSINE,
                OperationType.TANGENT, OperationType.TRIG_EQUATION]

    def generate(self, difficulty: float = 0.5, operation: Optional[OperationType] = None,
                 grade_level: Optional[int] = None, seed: Optional[int] = None, **kwargs) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)
        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        generators = {
            "special_angle": self._generate_special_angle,
            "right_triangle": self._generate_right_triangle,
            "identity": self._generate_identity,
            "trig_equation": self._generate_trig_equation,
        }
        return generators.get(problem_type, self._generate_special_angle)(difficulty, config, grade_level)

    def _generate_special_angle(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        func = random.choice(["sin", "cos", "tan"])
        if difficulty < 0.4:
            angles = [0, 30, 45, 60, 90]
        else:
            angles = list(self.SPECIAL_ANGLES.keys())

        # Avoid tan(90) and tan(270)
        if func == "tan":
            angles = [a for a in angles if a not in (90, 270)]

        angle = random.choice(angles)
        answer = self.SPECIAL_ANGLES[angle][func]

        expression = f"Find {func}({angle}°)"
        expression_latex = f"$\\{func}({angle}°)$"

        # Generate distractors from other trig values at same or nearby angles
        distractors = set()
        other_funcs = [f for f in ["sin", "cos", "tan"] if f != func]
        for of in other_funcs:
            val = self.SPECIAL_ANGLES[angle].get(of, "0")
            if val != answer and val != "undefined":
                distractors.add(val)
        nearby_angles = [a for a in self.SPECIAL_ANGLES if a != angle and a not in (90, 270)][:3]
        for na in nearby_angles:
            val = self.SPECIAL_ANGLES[na][func]
            if val != answer and val != "undefined":
                distractors.add(val)

        distractors = list(distractors)[:3]
        while len(distractors) < 3:
            distractors.append(str(random.choice(["-1", "2", "-1/2", "√2", "0"])))
            distractors = list(set(d for d in distractors if d != answer))[:3]

        calc_difficulty = 0.3 + 0.1 * (1 if angle > 90 else 0) + 0.1 * difficulty

        op_map = {"sin": OperationType.SINE, "cos": OperationType.COSINE, "tan": OperationType.TANGENT}

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id=f"trig_{func}_special",
            question_type=self.question_type,
            operation=op_map[func],
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"func": func, "angle": angle, "answer": answer, "type": "special_angle", "grade_level": grade_level},
        )

    def _generate_right_triangle(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        """Use trig to find missing side of right triangle"""
        # Use Pythagorean triples for clean answers
        triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (6, 8, 10)]
        if difficulty < 0.5:
            triple = random.choice(triples[:2])
        else:
            triple = random.choice(triples)

        a, b, c = triple
        scale = random.randint(1, max(1, int(3 * difficulty)))
        a, b, c = a * scale, b * scale, c * scale

        func = random.choice(["sin", "cos", "tan"])
        # angle opposite to side a
        if func == "sin":
            expression = f"In a right triangle, the hypotenuse is {c} and sin(θ) = {a}/{c}. Find the opposite side."
            answer = a
        elif func == "cos":
            expression = f"In a right triangle, the hypotenuse is {c} and cos(θ) = {b}/{c}. Find the adjacent side."
            answer = b
        else:
            expression = f"In a right triangle, the adjacent side is {b} and tan(θ) = {a}/{b}. Find the opposite side."
            answer = a

        distractors = self._make_distractors(answer, [b, c, a + b, abs(c - a), abs(c - b)])
        calc_difficulty = 0.35 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="trig_right_triangle",
            question_type=self.question_type,
            operation=OperationType.SINE,
            expression=expression,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"triple": (a, b, c), "func": func, "answer": answer, "type": "right_triangle", "grade_level": grade_level},
        )

    def _generate_identity(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        identities = [
            {
                "expression": "sin²(θ) + cos²(θ) = ?",
                "answer": "1",
                "distractors": ["0", "2", "sin(2θ)"],
                "latex": "$\\sin^2(\\theta) + \\cos^2(\\theta)$",
            },
            {
                "expression": "If sin(θ) = 3/5, find cos(θ) (0° < θ < 90°)",
                "answer": "4/5",
                "distractors": ["3/5", "5/3", "2/5"],
                "latex": "$\\cos(\\theta) = ?$",
            },
            {
                "expression": "tan(θ) = sin(θ) / ?",
                "answer": "cos(θ)",
                "distractors": ["sin(θ)", "tan(θ)", "1"],
                "latex": "$\\tan(\\theta) = \\frac{\\sin(\\theta)}{?}$",
            },
            {
                "expression": "sin(2θ) = ?",
                "answer": "2sin(θ)cos(θ)",
                "distractors": ["sin²(θ)", "2sin(θ)", "sin(θ) + cos(θ)"],
                "latex": "$\\sin(2\\theta) = ?$",
            },
        ]
        identity = random.choice(identities[:2] if difficulty < 0.5 else identities)

        calc_difficulty = 0.4 + 0.25 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="trig_identity",
            question_type=self.question_type,
            operation=OperationType.TRIG_EQUATION,
            expression=identity["expression"],
            expression_latex=identity["latex"],
            correct_answer=identity["answer"],
            answer_format=AnswerFormat.EXPRESSION,
            distractors=identity["distractors"][:3],
            all_options=self._shuffle_options(identity["answer"], identity["distractors"][:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"answer": identity["answer"], "type": "identity", "grade_level": grade_level},
        )

    def _generate_trig_equation(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        equations = [
            {"eq": "sin(x) = 1/2", "answer": "30° and 150°", "distractors": ["60° and 120°", "45° and 135°", "30° and 330°"]},
            {"eq": "cos(x) = 1/2", "answer": "60° and 300°", "distractors": ["30° and 330°", "120° and 240°", "60° and 120°"]},
            {"eq": "tan(x) = 1", "answer": "45° and 225°", "distractors": ["30° and 210°", "60° and 240°", "90° and 270°"]},
            {"eq": "sin(x) = √3/2", "answer": "60° and 120°", "distractors": ["30° and 150°", "45° and 135°", "60° and 300°"]},
            {"eq": "cos(x) = 0", "answer": "90° and 270°", "distractors": ["0° and 180°", "45° and 225°", "60° and 300°"]},
            {"eq": "sin(x) = 0", "answer": "0° and 180°", "distractors": ["90° and 270°", "45° and 225°", "30° and 150°"]},
        ]
        eq = random.choice(equations[:3] if difficulty < 0.5 else equations)

        expression = f"Solve for x (0° ≤ x < 360°): {eq['eq']}"
        calc_difficulty = 0.6 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="trig_equation",
            question_type=self.question_type,
            operation=OperationType.TRIG_EQUATION,
            expression=expression,
            correct_answer=eq["answer"],
            answer_format=AnswerFormat.EXPRESSION,
            distractors=eq["distractors"][:3],
            all_options=self._shuffle_options(eq["answer"], eq["distractors"][:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"equation": eq["eq"], "answer": eq["answer"], "type": "trig_equation", "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        return parameters.get("answer", "0")

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return []

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "special_angle")
        return {"special_angle": 0.35, "right_triangle": 0.45, "identity": 0.55, "trig_equation": 0.7}.get(ptype, 0.4)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.3: return 9
        elif difficulty < 0.5: return 10
        elif difficulty < 0.7: return 11
        else: return 12

    def _get_grade_config(self, grade_level: int) -> Dict:
        return self.GRADE_CONFIG[max(9, min(12, grade_level))]

    def _make_distractors(self, answer: int, candidates: List) -> List[str]:
        distractors = set()
        for c in candidates:
            v = int(c) if isinstance(c, float) else c
            if v != answer and v > 0:
                distractors.add(str(v))
        while len(distractors) < 3:
            distractors.add(str(answer + random.choice([-2, -1, 1, 2, 3])))
        return [d for d in distractors if d != str(answer)][:3]
