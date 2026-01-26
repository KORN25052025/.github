"""
Polynomials Question Generator.

Generates questions about polynomial addition, multiplication,
factoring, and polynomial division.
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
class PolynomialsGenerator(QuestionGenerator):
    """
    Generator for polynomial questions.

    Supports:
    - Polynomial addition/subtraction
    - Polynomial multiplication
    - Factoring (common factor, difference of squares, trinomials)
    - Polynomial long division (simple cases)
    """

    GRADE_CONFIG = {
        8: {"max_coef": 10, "max_degree": 2, "types": ["add_subtract", "multiply_binomial"]},
        9: {"max_coef": 15, "max_degree": 3, "types": ["add_subtract", "multiply_binomial", "factor_common"]},
        10: {"max_coef": 20, "max_degree": 3, "types": ["add_subtract", "multiply_binomial", "factor_common", "factor_trinomial"]},
        11: {"max_coef": 25, "max_degree": 4, "types": ["multiply_binomial", "factor_common", "factor_trinomial", "factor_diff_squares"]},
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.POLYNOMIALS

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.POLYNOMIAL_ADD, OperationType.POLYNOMIAL_MULTIPLY,
                OperationType.FACTORING, OperationType.POLYNOMIAL_DIVISION]

    def generate(self, difficulty: float = 0.5, operation: Optional[OperationType] = None,
                 grade_level: Optional[int] = None, seed: Optional[int] = None, **kwargs) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)
        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        generators = {
            "add_subtract": self._generate_add_subtract,
            "multiply_binomial": self._generate_multiply_binomial,
            "factor_common": self._generate_factor_common,
            "factor_trinomial": self._generate_factor_trinomial,
            "factor_diff_squares": self._generate_factor_diff_squares,
        }
        return generators.get(problem_type, self._generate_add_subtract)(difficulty, config, grade_level)

    def _format_poly(self, coeffs: Dict[int, int], var: str = "x") -> str:
        """Format polynomial from {degree: coefficient} dict."""
        if not coeffs:
            return "0"
        terms = []
        for deg in sorted(coeffs.keys(), reverse=True):
            c = coeffs[deg]
            if c == 0:
                continue
            if deg == 0:
                terms.append(f"{c}" if c > 0 else f"({c})")
            elif deg == 1:
                if c == 1:
                    terms.append(var)
                elif c == -1:
                    terms.append(f"-{var}")
                else:
                    terms.append(f"{c}{var}")
            else:
                if c == 1:
                    terms.append(f"{var}²" if deg == 2 else f"{var}^{deg}")
                elif c == -1:
                    terms.append(f"-{var}²" if deg == 2 else f"-{var}^{deg}")
                else:
                    terms.append(f"{c}{var}²" if deg == 2 else f"{c}{var}^{deg}")

        if not terms:
            return "0"

        result = terms[0]
        for t in terms[1:]:
            if t.startswith("-") or t.startswith("("):
                result += f" - {t.lstrip('-').strip('()')}"
            else:
                result += f" + {t}"
        return result

    def _generate_add_subtract(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_c = max(3, int(config["max_coef"] * (0.3 + 0.7 * difficulty)))
        max_deg = min(config["max_degree"], 2 + int(difficulty * 2))
        op = random.choice(["+", "-"])

        # Generate two polynomials
        p1 = {d: random.randint(-max_c, max_c) for d in range(max_deg + 1)}
        p2 = {d: random.randint(-max_c, max_c) for d in range(max_deg + 1)}

        # Make sure highest degree has non-zero coefficient
        p1[max_deg] = random.randint(1, max_c)
        p2[max_deg] = random.randint(1, max_c)

        # Compute result
        result = {}
        for d in range(max_deg + 1):
            if op == "+":
                result[d] = p1.get(d, 0) + p2.get(d, 0)
            else:
                result[d] = p1.get(d, 0) - p2.get(d, 0)

        p1_str = self._format_poly(p1)
        p2_str = self._format_poly(p2)
        answer = self._format_poly(result)

        expression = f"Simplify: ({p1_str}) {op} ({p2_str})"

        # Distractors: common errors
        wrong1 = result.copy()
        if max_deg in wrong1:
            wrong1[max_deg] = wrong1.get(max_deg, 0) + 1
        wrong2 = result.copy()
        if 0 in wrong2:
            wrong2[0] = wrong2.get(0, 0) - 1

        distractors = [
            self._format_poly(wrong1),
            self._format_poly(wrong2),
            self._format_poly(p1),  # Forgot p2
        ]
        distractors = [d for d in distractors if d != answer][:3]
        while len(distractors) < 3:
            distractors.append(self._format_poly({max_deg: result.get(max_deg, 1) + random.randint(1, 3)}))

        calc_difficulty = 0.25 + 0.15 * difficulty + 0.05 * max_deg

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="polynomials_add_subtract",
            question_type=self.question_type,
            operation=OperationType.POLYNOMIAL_ADD,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors[:3],
            all_options=self._shuffle_options(answer, distractors[:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"p1": p1, "p2": p2, "op": op, "result": result, "type": "add_subtract", "grade_level": grade_level},
        )

    def _generate_multiply_binomial(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_c = max(2, int(config["max_coef"] * (0.3 + 0.7 * difficulty)))

        # (ax + b)(cx + d)
        a = random.randint(1, min(5, max_c))
        b = random.randint(-max_c, max_c)
        c = random.randint(1, min(5, max_c))
        d = random.randint(-max_c, max_c)

        # Result: ac*x² + (ad+bc)*x + bd
        r2 = a * c
        r1 = a * d + b * c
        r0 = b * d
        result = {2: r2, 1: r1, 0: r0}
        answer = self._format_poly(result)

        b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
        d_str = f"+ {d}" if d >= 0 else f"- {abs(d)}"
        expression = f"Expand: ({a}x {b_str})({c}x {d_str})"

        # FOIL errors
        wrong_inner = {2: r2, 1: a * d, 0: r0}  # Forgot outer term
        wrong_sign = {2: r2, 1: -r1, 0: r0}

        distractors = [
            self._format_poly(wrong_inner),
            self._format_poly(wrong_sign),
            self._format_poly({2: r2, 1: r1 + 1, 0: r0}),
        ]
        distractors = [dd for dd in distractors if dd != answer][:3]
        while len(distractors) < 3:
            distractors.append(self._format_poly({2: r2 + 1, 1: r1, 0: r0}))

        calc_difficulty = 0.35 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="polynomials_multiply",
            question_type=self.question_type,
            operation=OperationType.POLYNOMIAL_MULTIPLY,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors[:3],
            all_options=self._shuffle_options(answer, distractors[:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"a": a, "b": b, "c": c, "d": d, "result": result, "type": "multiply_binomial", "grade_level": grade_level},
        )

    def _generate_factor_common(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_c = max(2, int(config["max_coef"] * (0.3 + 0.7 * difficulty)))
        gcf = random.randint(2, min(8, max_c))

        # Generate inner terms
        inner_a = random.randint(1, max_c)
        inner_b = random.randint(1, max_c)

        # Expanded: gcf*inner_a*x + gcf*inner_b
        term1 = gcf * inner_a
        term2 = gcf * inner_b

        expression = f"Factor: {term1}x + {term2}"
        answer = f"{gcf}({inner_a}x + {inner_b})"

        distractors = [
            f"{gcf + 1}({inner_a}x + {inner_b})",
            f"{gcf}({inner_a + 1}x + {inner_b})",
            f"{term1}(x + {term2 // term1})" if term1 != 0 else f"{gcf}({inner_a}x)",
        ]
        distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.3 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="polynomials_factor_common",
            question_type=self.question_type,
            operation=OperationType.FACTORING,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"gcf": gcf, "inner_a": inner_a, "inner_b": inner_b, "type": "factor_common", "grade_level": grade_level},
        )

    def _generate_factor_trinomial(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        # x² + (p+q)x + pq = (x + p)(x + q)
        p = random.randint(-8, 8)
        q = random.randint(-8, 8)
        if p == 0:
            p = 1
        if q == 0:
            q = -1

        b = p + q
        c = p * q

        b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
        c_str = f"+ {c}" if c >= 0 else f"- {abs(c)}"
        expression = f"Factor: x² {b_str}x {c_str}"

        p_str = f"+ {p}" if p >= 0 else f"- {abs(p)}"
        q_str = f"+ {q}" if q >= 0 else f"- {abs(q)}"
        answer = f"(x {p_str})(x {q_str})"

        # Distractors: sign errors
        distractors = [
            f"(x {'+' if -p >= 0 else '-'} {abs(p)})(x {'+' if -q >= 0 else '-'} {abs(q)})",
            f"(x {'+' if p >= 0 else '-'} {abs(p)})(x {'+' if -q >= 0 else '-'} {abs(q)})",
            f"(x {'+' if p+1 >= 0 else '-'} {abs(p+1)})(x {'+' if q-1 >= 0 else '-'} {abs(q-1)})",
        ]
        distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.5 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="polynomials_factor_trinomial",
            question_type=self.question_type,
            operation=OperationType.FACTORING,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"p": p, "q": q, "b": b, "c": c, "type": "factor_trinomial", "grade_level": grade_level},
        )

    def _generate_factor_diff_squares(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        # a²x² - b² = (ax - b)(ax + b)
        a = random.randint(1, min(5, config["max_coef"]))
        b = random.randint(1, min(10, config["max_coef"]))

        a_sq = a * a
        b_sq = b * b

        if a == 1:
            expression = f"Factor: x² - {b_sq}"
            answer = f"(x - {b})(x + {b})"
        else:
            expression = f"Factor: {a_sq}x² - {b_sq}"
            answer = f"({a}x - {b})({a}x + {b})"

        distractors = [
            f"({a}x - {b})²" if a > 1 else f"(x - {b})²",
            f"({a}x + {b})²" if a > 1 else f"(x + {b})²",
            f"({a}x - {b+1})({a}x + {b-1})" if a > 1 else f"(x - {b+1})(x + {b-1})",
        ]
        distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.45 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="polynomials_factor_diff_squares",
            question_type=self.question_type,
            operation=OperationType.FACTORING,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"a": a, "b": b, "type": "factor_diff_squares", "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        return parameters.get("answer", parameters.get("result", "0"))

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return []

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "add_subtract")
        return {"add_subtract": 0.3, "multiply_binomial": 0.45, "factor_common": 0.35, "factor_trinomial": 0.6, "factor_diff_squares": 0.5}.get(ptype, 0.4)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.25: return 8
        elif difficulty < 0.5: return 9
        elif difficulty < 0.75: return 10
        else: return 11

    def _get_grade_config(self, grade_level: int) -> Dict:
        return self.GRADE_CONFIG[max(8, min(11, grade_level))]
