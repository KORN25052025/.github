"""
Coordinate Geometry Question Generator.

Generates questions about distance, midpoint, slope,
and line equations in the coordinate plane.
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
class CoordinateGeometryGenerator(QuestionGenerator):
    """
    Generator for coordinate geometry questions.

    Supports:
    - Distance between two points
    - Midpoint of two points
    - Slope of a line through two points
    - Equation of a line (slope-intercept and point-slope)
    """

    GRADE_CONFIG = {
        7: {"max_coord": 10, "types": ["midpoint", "distance_simple"]},
        8: {"max_coord": 15, "types": ["midpoint", "distance", "slope"]},
        9: {"max_coord": 20, "types": ["midpoint", "distance", "slope", "line_equation"]},
        10: {"max_coord": 25, "types": ["distance", "slope", "line_equation"]},
        11: {"max_coord": 30, "types": ["distance", "slope", "line_equation", "parallel_perpendicular"]},
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.COORDINATE_GEOMETRY

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.DISTANCE, OperationType.MIDPOINT,
                OperationType.SLOPE, OperationType.LINE_EQUATION]

    def generate(self, difficulty: float = 0.5, operation: Optional[OperationType] = None,
                 grade_level: Optional[int] = None, seed: Optional[int] = None, **kwargs) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)
        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        generators = {
            "distance_simple": self._generate_distance_simple,
            "distance": self._generate_distance,
            "midpoint": self._generate_midpoint,
            "slope": self._generate_slope,
            "line_equation": self._generate_line_equation,
            "parallel_perpendicular": self._generate_parallel_perpendicular,
        }
        return generators.get(problem_type, self._generate_midpoint)(difficulty, config, grade_level)

    def _generate_distance_simple(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        """Generate distance with Pythagorean triple for integer answers."""
        triples = [(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17)]
        dx, dy, dist = random.choice(triples[:2] if difficulty < 0.5 else triples)

        x1 = random.randint(0, 5)
        y1 = random.randint(0, 5)
        x2 = x1 + dx
        y2 = y1 + dy

        expression = f"Find the distance between ({x1}, {y1}) and ({x2}, {y2})"
        expression_latex = f"$d = \\sqrt{{({x2}-{x1})^2 + ({y2}-{y1})^2}}$"
        answer = dist

        distractors = self._make_distractors(answer, [dx, dy, dx + dy, abs(dist - 1), dist + 1])
        calc_difficulty = 0.25 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="coord_distance_simple",
            question_type=self.question_type,
            operation=OperationType.DISTANCE,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"x1": x1, "y1": y1, "x2": x2, "y2": y2, "answer": answer, "type": "distance_simple", "grade_level": grade_level},
        )

    def _generate_distance(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        """General distance formula (may result in irrational answers)."""
        max_c = max(5, int(config["max_coord"] * (0.3 + 0.7 * difficulty)))
        x1 = random.randint(-max_c, max_c)
        y1 = random.randint(-max_c, max_c)
        x2 = random.randint(-max_c, max_c)
        y2 = random.randint(-max_c, max_c)

        while x1 == x2 and y1 == y2:
            x2 = random.randint(-max_c, max_c)

        dist_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        dist_exact = math.sqrt(dist_sq)

        # Check if perfect square
        if dist_exact == int(dist_exact):
            answer = str(int(dist_exact))
            answer_format = AnswerFormat.INTEGER
        else:
            answer = f"√{dist_sq}"
            answer_format = AnswerFormat.EXPRESSION

        expression = f"Find the distance between ({x1}, {y1}) and ({x2}, {y2})"
        expression_latex = f"$d = \\sqrt{{({x2}-{x1})^2 + ({y2}-{y1})^2}}$"

        distractors = [
            f"√{dist_sq + 1}",
            f"√{max(1, dist_sq - 1)}",
            str(abs(x2 - x1) + abs(y2 - y1)),
        ]
        distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.35 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="coord_distance",
            question_type=self.question_type,
            operation=OperationType.DISTANCE,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=answer,
            answer_format=answer_format,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"x1": x1, "y1": y1, "x2": x2, "y2": y2, "dist_sq": dist_sq, "answer": answer, "type": "distance", "grade_level": grade_level},
        )

    def _generate_midpoint(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_c = max(5, int(config["max_coord"] * (0.3 + 0.7 * difficulty)))

        # Generate even sums for integer midpoints
        x1 = random.randint(-max_c, max_c)
        y1 = random.randint(-max_c, max_c)
        # Make sure midpoint is integer
        x2 = x1 + 2 * random.randint(-max_c // 2, max_c // 2)
        y2 = y1 + 2 * random.randint(-max_c // 2, max_c // 2)

        while x1 == x2 and y1 == y2:
            x2 = x1 + 2 * random.randint(1, max_c // 2)

        mx = (x1 + x2) // 2
        my = (y1 + y2) // 2
        answer = f"({mx}, {my})"

        expression = f"Find the midpoint of ({x1}, {y1}) and ({x2}, {y2})"
        expression_latex = f"$M = \\left(\\frac{{{x1}+{x2}}}{{2}}, \\frac{{{y1}+{y2}}}{{2}}\\right)$"

        distractors = [
            f"({mx + 1}, {my})",
            f"({mx}, {my + 1})",
            f"({x1 + x2}, {y1 + y2})",  # Forgot to divide by 2
        ]
        distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.2 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="coord_midpoint",
            question_type=self.question_type,
            operation=OperationType.MIDPOINT,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"x1": x1, "y1": y1, "x2": x2, "y2": y2, "mx": mx, "my": my, "answer": answer, "type": "midpoint", "grade_level": grade_level},
        )

    def _generate_slope(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_c = max(5, int(config["max_coord"] * (0.3 + 0.7 * difficulty)))
        x1 = random.randint(-max_c, max_c)
        y1 = random.randint(-max_c, max_c)
        x2 = random.randint(-max_c, max_c)
        y2 = random.randint(-max_c, max_c)

        while x1 == x2:
            x2 = random.randint(-max_c, max_c)

        dy = y2 - y1
        dx = x2 - x1
        frac = Fraction(dy, dx)

        if frac.denominator == 1:
            answer = str(frac.numerator)
            answer_format = AnswerFormat.INTEGER
        else:
            answer = f"{frac.numerator}/{frac.denominator}"
            answer_format = AnswerFormat.FRACTION

        expression = f"Find the slope of the line through ({x1}, {y1}) and ({x2}, {y2})"
        expression_latex = f"$m = \\frac{{{y2}-{y1}}}{{{x2}-{x1}}} = \\frac{{{dy}}}{{{dx}}}$"

        if frac.denominator == 1:
            distractors = self._make_distractors(frac.numerator, [
                -frac.numerator,
                frac.numerator + 1,
                frac.numerator - 1,
                dx,
            ])
        else:
            distractors = [
                f"{-frac.numerator}/{frac.denominator}",
                f"{frac.denominator}/{frac.numerator}" if frac.numerator != 0 else "0",
                f"{frac.numerator + 1}/{frac.denominator}",
            ]
            distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.3 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="coord_slope",
            question_type=self.question_type,
            operation=OperationType.SLOPE,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=answer,
            answer_format=answer_format,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"x1": x1, "y1": y1, "x2": x2, "y2": y2, "slope": str(frac), "answer": answer, "type": "slope", "grade_level": grade_level},
        )

    def _generate_line_equation(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        # y = mx + b
        m = random.randint(-5, 5)
        b = random.randint(-10, 10)

        question_variant = random.choice(["from_slope_intercept", "from_two_points", "from_point_slope"])

        if question_variant == "from_slope_intercept":
            expression = f"Write the equation of a line with slope {m} and y-intercept {b}"
            b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
            answer = f"y = {m}x {b_str}"
        elif question_variant == "from_two_points":
            x1 = random.randint(-5, 5)
            y1 = m * x1 + b
            x2 = x1 + random.randint(1, 3)
            y2 = m * x2 + b
            expression = f"Find the equation of the line through ({x1}, {y1}) and ({x2}, {y2})"
            b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
            answer = f"y = {m}x {b_str}"
        else:
            x1 = random.randint(-5, 5)
            y1 = m * x1 + b
            expression = f"Find the equation of the line with slope {m} passing through ({x1}, {y1})"
            b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
            answer = f"y = {m}x {b_str}"

        # Clean up: y = 0x + b => y = b, y = 1x => y = x
        if m == 0:
            answer = f"y = {b}"
        elif m == 1:
            answer = f"y = x {'+' if b >= 0 else '-'} {abs(b)}" if b != 0 else "y = x"
        elif m == -1:
            answer = f"y = -x {'+' if b >= 0 else '-'} {abs(b)}" if b != 0 else "y = -x"
        elif b == 0:
            answer = f"y = {m}x"

        distractors = [
            f"y = {-m}x {'+' if b >= 0 else '-'} {abs(b)}",
            f"y = {m}x {'+' if -b >= 0 else '-'} {abs(b)}",
            f"y = {m + 1}x {'+' if b >= 0 else '-'} {abs(b)}",
        ]
        distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.4 + 0.25 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="coord_line_equation",
            question_type=self.question_type,
            operation=OperationType.LINE_EQUATION,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"m": m, "b": b, "variant": question_variant, "answer": answer, "type": "line_equation", "grade_level": grade_level},
        )

    def _generate_parallel_perpendicular(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        m1 = random.randint(-5, 5)
        while m1 == 0:
            m1 = random.randint(-5, 5)
        b1 = random.randint(-10, 10)

        rel = random.choice(["parallel", "perpendicular"])

        if rel == "parallel":
            m2 = m1
            expression = f"Find the slope of a line parallel to y = {m1}x + {b1}"
            answer = str(m2)
            distractors = [str(-m1), str(m1 + 1), f"-1/{m1}" if m1 != 0 else "0"]
        else:
            frac = Fraction(-1, m1)
            if frac.denominator == 1:
                m2_str = str(frac.numerator)
            else:
                m2_str = f"{frac.numerator}/{frac.denominator}"
            expression = f"Find the slope of a line perpendicular to y = {m1}x + {b1}"
            answer = m2_str
            distractors = [str(m1), str(-m1), str(m1 + 1)]

        distractors = [d for d in distractors if d != answer][:3]
        calc_difficulty = 0.45 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="coord_parallel_perpendicular",
            question_type=self.question_type,
            operation=OperationType.SLOPE,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION if "/" in answer else AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"m1": m1, "relation": rel, "answer": answer, "type": "parallel_perpendicular", "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        return parameters.get("answer", 0)

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return []

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "midpoint")
        return {"distance_simple": 0.3, "distance": 0.4, "midpoint": 0.25, "slope": 0.4,
                "line_equation": 0.55, "parallel_perpendicular": 0.5}.get(ptype, 0.35)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.2: return 7
        elif difficulty < 0.4: return 8
        elif difficulty < 0.6: return 9
        elif difficulty < 0.8: return 10
        else: return 11

    def _get_grade_config(self, grade_level: int) -> Dict:
        return self.GRADE_CONFIG[max(7, min(11, grade_level))]

    def _make_distractors(self, answer: int, candidates: List) -> List[str]:
        distractors = set()
        for c in candidates:
            v = int(c) if isinstance(c, float) else c
            if v != answer:
                distractors.add(str(v))
        while len(distractors) < 3:
            offset = random.choice([-2, -1, 1, 2, 3])
            distractors.add(str(answer + offset))
        return [d for d in distractors if d != str(answer)][:3]
