"""
Number Theory Question Generator.

Generates questions about prime numbers, GCD, LCM, divisibility rules,
and prime factorization with deterministic correct answers.
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
class NumberTheoryGenerator(QuestionGenerator):
    """
    Generator for number theory questions.

    Supports:
    - Prime number identification
    - Greatest Common Divisor (GCD / EBOB)
    - Least Common Multiple (LCM / EKOK)
    - Divisibility rules
    - Prime factorization
    """

    GRADE_CONFIG = {
        4: {"max_value": 50, "types": ["prime_check", "divisibility"]},
        5: {"max_value": 100, "types": ["prime_check", "divisibility", "gcd"]},
        6: {"max_value": 200, "types": ["prime_check", "divisibility", "gcd", "lcm"]},
        7: {"max_value": 500, "types": ["prime_check", "gcd", "lcm", "factorization"]},
        8: {"max_value": 1000, "types": ["prime_check", "gcd", "lcm", "factorization", "divisibility"]},
    }

    PRIMES_UNDER_100 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                         53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.NUMBER_THEORY

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.PRIME, OperationType.GCD, OperationType.LCM,
                OperationType.DIVISIBILITY, OperationType.FACTORIZATION]

    def generate(self, difficulty: float = 0.5, operation: Optional[OperationType] = None,
                 grade_level: Optional[int] = None, seed: Optional[int] = None, **kwargs) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)
        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        generators = {
            "prime_check": self._generate_prime_check,
            "gcd": self._generate_gcd,
            "lcm": self._generate_lcm,
            "divisibility": self._generate_divisibility,
            "factorization": self._generate_factorization,
        }
        return generators.get(problem_type, self._generate_prime_check)(difficulty, config, grade_level)

    def _is_prime(self, n: int) -> bool:
        if n < 2:
            return False
        if n < 4:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    def _prime_factors(self, n: int) -> List[int]:
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors

    def _generate_prime_check(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_val = max(20, int(config["max_value"] * (0.3 + 0.7 * difficulty)))

        if random.random() < 0.5:
            # Ask to identify if a number is prime
            is_prime = random.random() < 0.5
            if is_prime:
                candidates = [p for p in self.PRIMES_UNDER_100 if p <= max_val]
                if not candidates:
                    candidates = [2, 3, 5, 7]
                number = random.choice(candidates)
            else:
                number = random.randint(4, max_val)
                while self._is_prime(number):
                    number = random.randint(4, max_val)

            answer = "Yes" if self._is_prime(number) else "No"
            expression = f"Is {number} a prime number?"
            distractors = ["No", "Yes"]
            distractors = [d for d in distractors if d != answer]
            distractors.append("Cannot determine")
            distractors = distractors[:3]
        else:
            # Find the next prime after a number
            start = random.randint(10, max(20, max_val // 2))
            n = start + 1
            while not self._is_prime(n):
                n += 1
            answer_val = n
            expression = f"What is the smallest prime number greater than {start}?"
            answer = str(answer_val)
            distractors = self._make_num_distractors(answer_val, [
                answer_val + 1, answer_val - 1, start, answer_val + 2,
            ])

        calc_difficulty = 0.2 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="number_theory_prime",
            question_type=self.question_type,
            operation=OperationType.PRIME,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION if answer in ("Yes", "No") else AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"answer": answer, "type": "prime_check", "grade_level": grade_level},
        )

    def _generate_gcd(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_val = max(20, int(config["max_value"] * (0.3 + 0.7 * difficulty)))

        # Generate two numbers with a known GCD
        gcd_val = random.randint(2, min(20, max_val // 4))
        mult_a = random.randint(2, max(3, max_val // gcd_val))
        mult_b = random.randint(2, max(3, max_val // gcd_val))
        while math.gcd(mult_a, mult_b) != 1:
            mult_b = random.randint(2, max(3, max_val // gcd_val))

        a = gcd_val * mult_a
        b = gcd_val * mult_b
        answer = gcd_val

        expression = f"Find the GCD (EBOB) of {a} and {b}"
        expression_latex = f"$\\gcd({a}, {b})$"

        distractors = self._make_num_distractors(answer, [
            a * b // answer,  # LCM instead
            answer * 2,
            answer + 1, answer - 1 if answer > 1 else 3,
            min(a, b),
        ])

        calc_difficulty = 0.35 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="number_theory_gcd",
            question_type=self.question_type,
            operation=OperationType.GCD,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"a": a, "b": b, "answer": answer, "type": "gcd", "grade_level": grade_level},
        )

    def _generate_lcm(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_val = max(20, int(config["max_value"] * (0.3 + 0.7 * difficulty)))

        a = random.randint(2, min(30, max_val))
        b = random.randint(2, min(30, max_val))
        answer = (a * b) // math.gcd(a, b)

        expression = f"Find the LCM (EKOK) of {a} and {b}"
        expression_latex = f"$\\text{{lcm}}({a}, {b})$"

        gcd_val = math.gcd(a, b)
        distractors = self._make_num_distractors(answer, [
            a * b,  # Not simplifying by GCD
            gcd_val,  # GCD instead of LCM
            answer + a, answer - b if answer > b else answer + b,
            max(a, b),
        ])

        calc_difficulty = 0.4 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="number_theory_lcm",
            question_type=self.question_type,
            operation=OperationType.LCM,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"a": a, "b": b, "answer": answer, "type": "lcm", "grade_level": grade_level},
        )

    def _generate_divisibility(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        divisors = [2, 3, 4, 5, 6, 9, 10]
        divisor = random.choice(divisors)
        max_val = max(50, int(config["max_value"] * (0.3 + 0.7 * difficulty)))

        is_divisible = random.random() < 0.5
        if is_divisible:
            mult = random.randint(2, max_val // divisor)
            number = divisor * mult
        else:
            number = random.randint(10, max_val)
            while number % divisor == 0:
                number = random.randint(10, max_val)

        answer = "Yes" if number % divisor == 0 else "No"
        expression = f"Is {number} divisible by {divisor}?"

        distractors = ["No" if answer == "Yes" else "Yes", "Cannot determine", f"Only if divided by {divisor + 1}"]
        distractors = distractors[:3]

        calc_difficulty = 0.2 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="number_theory_divisibility",
            question_type=self.question_type,
            operation=OperationType.DIVISIBILITY,
            expression=expression,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors,
            all_options=self._shuffle_options(answer, distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"number": number, "divisor": divisor, "answer": answer, "type": "divisibility", "grade_level": grade_level},
        )

    def _generate_factorization(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_val = max(20, int(min(200, config["max_value"]) * (0.3 + 0.7 * difficulty)))

        # Generate a composite number
        small_primes = [2, 3, 5, 7, 11, 13]
        num_factors = random.randint(2, 3 + int(difficulty * 2))
        number = 1
        used_primes = []
        for _ in range(num_factors):
            p = random.choice(small_primes[:3 + int(difficulty * 3)])
            number *= p
            used_primes.append(p)
            if number > max_val:
                break

        if number < 4:
            number = 12
            used_primes = [2, 2, 3]

        factors = self._prime_factors(number)
        factors_str = " × ".join(str(f) for f in sorted(factors))
        answer = factors_str

        expression = f"Find the prime factorization of {number}"
        expression_latex = f"${number} = {factors_str}$"

        # Generate wrong factorizations
        distractors = []
        wrong1 = sorted(factors)
        if len(wrong1) > 1:
            w = wrong1.copy()
            w[0] = w[0] + 1
            distractors.append(" × ".join(str(f) for f in w))
        distractors.append(f"1 × {number}")
        if number % 2 == 0:
            distractors.append(f"2 × {number // 2}")
        else:
            distractors.append(f"3 × {number}")
        distractors = [d for d in distractors if d != answer][:3]
        while len(distractors) < 3:
            distractors.append(f"{random.choice([2,3,5])} × {number // random.choice([2,3,5]) if number > 5 else number}")

        calc_difficulty = 0.4 + 0.25 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="number_theory_factorization",
            question_type=self.question_type,
            operation=OperationType.FACTORIZATION,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors[:3],
            all_options=self._shuffle_options(answer, distractors[:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"number": number, "factors": factors, "answer": answer, "type": "factorization", "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        return parameters.get("answer", 0)

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return []

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "prime_check")
        return {"prime_check": 0.25, "gcd": 0.4, "lcm": 0.45, "divisibility": 0.2, "factorization": 0.5}.get(ptype, 0.3)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.2: return 4
        elif difficulty < 0.4: return 5
        elif difficulty < 0.6: return 6
        elif difficulty < 0.8: return 7
        else: return 8

    def _get_grade_config(self, grade_level: int) -> Dict:
        return self.GRADE_CONFIG[max(4, min(8, grade_level))]

    def _make_num_distractors(self, answer: int, candidates: List) -> List[str]:
        distractors = set()
        for c in candidates:
            v = int(c) if isinstance(c, float) else c
            if v != answer and v > 0:
                distractors.add(str(v))
        while len(distractors) < 3:
            offset = random.choice([-2, -1, 1, 2, 3])
            v = answer + offset
            if v > 0 and str(v) not in distractors:
                distractors.add(str(v))
        return list(distractors)[:3]
