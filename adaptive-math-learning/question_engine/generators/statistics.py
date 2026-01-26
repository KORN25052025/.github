"""
Statistics & Probability Question Generator.

Generates questions about mean, median, mode, range, basic probability,
combinations, and permutations with deterministic correct answers.
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
class StatisticsGenerator(QuestionGenerator):
    """
    Generator for statistics and probability questions.

    Supports:
    - Mean (average)
    - Median
    - Mode
    - Range
    - Basic probability
    - Combinations and permutations
    """

    GRADE_CONFIG = {
        5: {"max_value": 50, "set_size": 5, "types": ["mean", "range"]},
        6: {"max_value": 100, "set_size": 7, "types": ["mean", "median", "mode", "range"]},
        7: {"max_value": 200, "set_size": 9, "types": ["mean", "median", "mode", "range", "probability"]},
        8: {"max_value": 500, "set_size": 10, "types": ["mean", "median", "mode", "range", "probability"]},
        9: {"max_value": 500, "set_size": 10, "types": ["mean", "median", "mode", "range", "probability", "combination", "permutation"]},
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.STATISTICS

    @property
    def supported_operations(self) -> List[OperationType]:
        return [
            OperationType.MEAN, OperationType.MEDIAN, OperationType.MODE,
            OperationType.RANGE, OperationType.PROBABILITY,
            OperationType.COMBINATION, OperationType.PERMUTATION,
        ]

    def generate(self, difficulty: float = 0.5, operation: Optional[OperationType] = None,
                 grade_level: Optional[int] = None, seed: Optional[int] = None, **kwargs) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)
        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        generators = {
            "mean": self._generate_mean,
            "median": self._generate_median,
            "mode": self._generate_mode,
            "range": self._generate_range,
            "probability": self._generate_probability,
            "combination": self._generate_combination,
            "permutation": self._generate_permutation,
        }
        return generators.get(problem_type, self._generate_mean)(difficulty, config, grade_level)

    def _generate_mean(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        size = max(3, int(config["set_size"] * (0.4 + 0.6 * difficulty)))
        max_val = max(10, int(config["max_value"] * (0.3 + 0.7 * difficulty)))

        # Generate numbers whose sum is divisible by count for clean answer
        target_mean = random.randint(5, max_val // 2)
        total = target_mean * size
        numbers = []
        remaining = total
        for i in range(size - 1):
            val = random.randint(max(1, target_mean - 20), min(max_val, target_mean + 20))
            numbers.append(val)
            remaining -= val
        numbers.append(remaining)
        random.shuffle(numbers)

        answer = target_mean
        nums_str = ", ".join(str(n) for n in numbers)
        expression = f"Find the mean of: {nums_str}"

        distractors = self._make_distractors(answer, [
            answer + 1, answer - 1, max(numbers), min(numbers),
            sum(numbers) // (size + 1) if size + 1 > 0 else answer + 2,
            sorted(numbers)[size // 2],
        ])

        calc_difficulty = 0.2 + 0.15 * (size / 10) + 0.1 * (max_val / config["max_value"])

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="statistics_mean",
            question_type=self.question_type,
            operation=OperationType.MEAN,
            expression=expression,
            expression_latex=f"$\\bar{{x}} = \\frac{{{'+'.join(str(n) for n in numbers)}}}{{{size}}}$",
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"numbers": numbers, "answer": answer, "type": "mean", "grade_level": grade_level},
        )

    def _generate_median(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        size = random.choice([5, 7, 9]) if random.random() < 0.6 else random.choice([4, 6, 8])
        max_val = max(10, int(config["max_value"] * (0.3 + 0.7 * difficulty)))
        numbers = sorted([random.randint(1, max_val) for _ in range(size)])

        if size % 2 == 1:
            answer = numbers[size // 2]
            answer_format = AnswerFormat.INTEGER
        else:
            mid1 = numbers[size // 2 - 1]
            mid2 = numbers[size // 2]
            answer = (mid1 + mid2) / 2
            answer_format = AnswerFormat.DECIMAL if answer != int(answer) else AnswerFormat.INTEGER
            if answer == int(answer):
                answer = int(answer)

        random.shuffle(numbers)
        nums_str = ", ".join(str(n) for n in numbers)
        expression = f"Find the median of: {nums_str}"

        distractors = self._make_distractors(answer, [
            int(answer) + 1, int(answer) - 1,
            sum(numbers) // size,
            max(numbers), min(numbers),
        ])

        calc_difficulty = 0.3 + 0.1 * (size / 10)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="statistics_median",
            question_type=self.question_type,
            operation=OperationType.MEDIAN,
            expression=expression,
            correct_answer=str(answer),
            answer_format=answer_format,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"numbers": sorted(numbers), "answer": answer, "type": "median", "grade_level": grade_level},
        )

    def _generate_mode(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_val = max(10, int(config["max_value"] * (0.3 + 0.7 * difficulty)))
        size = max(5, int(config["set_size"] * (0.5 + 0.5 * difficulty)))

        mode_val = random.randint(1, max_val)
        mode_count = random.randint(2, min(4, size - 2))
        numbers = [mode_val] * mode_count

        while len(numbers) < size:
            val = random.randint(1, max_val)
            if val != mode_val:
                numbers.append(val)

        random.shuffle(numbers)
        nums_str = ", ".join(str(n) for n in numbers)
        expression = f"Find the mode of: {nums_str}"

        unique_others = [n for n in set(numbers) if n != mode_val]
        distractors = self._make_distractors(mode_val, [
            mode_val + 1, mode_val - 1,
            sum(numbers) // size,
        ] + unique_others[:2])

        calc_difficulty = 0.25 + 0.1 * (size / 10)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="statistics_mode",
            question_type=self.question_type,
            operation=OperationType.MODE,
            expression=expression,
            correct_answer=str(mode_val),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(mode_val), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"numbers": numbers, "mode": mode_val, "answer": mode_val, "type": "mode", "grade_level": grade_level},
        )

    def _generate_range(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        max_val = max(10, int(config["max_value"] * (0.3 + 0.7 * difficulty)))
        size = max(4, int(config["set_size"] * (0.4 + 0.6 * difficulty)))
        numbers = [random.randint(1, max_val) for _ in range(size)]
        answer = max(numbers) - min(numbers)

        nums_str = ", ".join(str(n) for n in numbers)
        expression = f"Find the range of: {nums_str}"

        distractors = self._make_distractors(answer, [
            answer + 1, answer - 1, max(numbers), min(numbers), sum(numbers) // size,
        ])

        calc_difficulty = 0.15 + 0.1 * (size / 10)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="statistics_range",
            question_type=self.question_type,
            operation=OperationType.RANGE,
            expression=expression,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"numbers": numbers, "answer": answer, "type": "range", "grade_level": grade_level},
        )

    def _generate_probability(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        scenarios = [
            {"context": "dice", "total": 6, "text": "A standard die is rolled. What is the probability of rolling {event}?"},
            {"context": "coin", "total": 2, "text": "A fair coin is tossed. What is the probability of getting {event}?"},
            {"context": "cards", "total": 52, "text": "A card is drawn from a standard deck. What is the probability of drawing {event}?"},
            {"context": "marbles", "total": None, "text": "A bag contains {details}. What is the probability of drawing {event}?"},
        ]

        if difficulty < 0.4:
            scenario = scenarios[random.randint(0, 1)]
        else:
            scenario = random.choice(scenarios)

        if scenario["context"] == "dice":
            event_type = random.choice(["even", "odd", "greater_than_4", "less_than_3", "specific"])
            if event_type == "even":
                favorable = 3
                event_desc = "an even number"
            elif event_type == "odd":
                favorable = 3
                event_desc = "an odd number"
            elif event_type == "greater_than_4":
                favorable = 2
                event_desc = "a number greater than 4"
            elif event_type == "less_than_3":
                favorable = 2
                event_desc = "a number less than 3"
            else:
                favorable = 1
                event_desc = f"a {random.randint(1, 6)}"
            total = 6
            expression = scenario["text"].format(event=event_desc)

        elif scenario["context"] == "coin":
            favorable = 1
            total = 2
            event_desc = random.choice(["heads", "tails"])
            expression = scenario["text"].format(event=event_desc)

        elif scenario["context"] == "cards":
            event_type = random.choice(["suit", "color", "face", "specific"])
            if event_type == "suit":
                favorable = 13
                event_desc = f"a {random.choice(['heart', 'diamond', 'club', 'spade'])}"
            elif event_type == "color":
                favorable = 26
                event_desc = f"a {random.choice(['red', 'black'])} card"
            elif event_type == "face":
                favorable = 12
                event_desc = "a face card (J, Q, K)"
            else:
                favorable = 4
                event_desc = f"a {random.choice(['King', 'Queen', 'Ace', '7'])}"
            total = 52
            expression = scenario["text"].format(event=event_desc)

        else:  # marbles
            colors = {"red": random.randint(2, 8), "blue": random.randint(2, 8), "green": random.randint(1, 5)}
            total = sum(colors.values())
            chosen_color = random.choice(list(colors.keys()))
            favorable = colors[chosen_color]
            details = ", ".join(f"{v} {k}" for k, v in colors.items()) + " marbles"
            event_desc = f"a {chosen_color} marble"
            expression = scenario["text"].format(details=details, event=event_desc)

        frac = Fraction(favorable, total)
        answer = f"{frac.numerator}/{frac.denominator}"

        distractors = []
        wrong_fracs = [
            Fraction(total - favorable, total),
            Fraction(favorable, total - favorable) if total - favorable > 0 else Fraction(1, 2),
            Fraction(favorable + 1, total),
        ]
        for wf in wrong_fracs:
            d = f"{wf.numerator}/{wf.denominator}"
            if d != answer:
                distractors.append(d)
        while len(distractors) < 3:
            n = random.randint(1, total - 1)
            f = Fraction(n, total)
            d = f"{f.numerator}/{f.denominator}"
            if d != answer and d not in distractors:
                distractors.append(d)

        calc_difficulty = 0.3 + 0.2 * difficulty + (0.1 if total > 10 else 0)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="statistics_probability",
            question_type=self.question_type,
            operation=OperationType.PROBABILITY,
            expression=expression,
            expression_latex=f"$P = \\frac{{{frac.numerator}}}{{{frac.denominator}}}$",
            correct_answer=answer,
            answer_format=AnswerFormat.FRACTION,
            distractors=distractors[:3],
            all_options=self._shuffle_options(answer, distractors[:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"favorable": favorable, "total": total, "answer": answer, "type": "probability", "grade_level": grade_level},
        )

    def _generate_combination(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        n = random.randint(4, 5 + int(difficulty * 7))
        r = random.randint(2, n - 1)
        answer = math.comb(n, r)

        expression = f"How many ways can you choose {r} items from {n} items? (C({n},{r}))"
        expression_latex = f"$C({n},{r}) = \\binom{{{n}}}{{{r}}}$"

        distractors = self._make_distractors(answer, [
            math.perm(n, r),
            math.comb(n, r - 1) if r > 1 else answer + 5,
            math.comb(n - 1, r),
            n * r,
            answer + random.randint(1, 5),
        ])

        calc_difficulty = 0.6 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="statistics_combination",
            question_type=self.question_type,
            operation=OperationType.COMBINATION,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"n": n, "r": r, "answer": answer, "type": "combination", "grade_level": grade_level},
        )

    def _generate_permutation(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        n = random.randint(4, 4 + int(difficulty * 5))
        r = random.randint(2, min(n, 4))
        answer = math.perm(n, r)

        expression = f"How many ways can you arrange {r} items from {n} items? (P({n},{r}))"
        expression_latex = f"$P({n},{r}) = \\frac{{{n}!}}{{({n}-{r})!}}$"

        distractors = self._make_distractors(answer, [
            math.comb(n, r),
            n * r,
            math.perm(n, r - 1) if r > 1 else answer + 10,
            n ** r,
            answer + random.randint(1, 10),
        ])

        calc_difficulty = 0.65 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="statistics_permutation",
            question_type=self.question_type,
            operation=OperationType.PERMUTATION,
            expression=expression,
            expression_latex=expression_latex,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"n": n, "r": r, "answer": answer, "type": "permutation", "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        return parameters.get("answer", 0)

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return self._make_distractors(int(correct_answer) if str(correct_answer).isdigit() else 0, [])

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "mean")
        base_diff = {"mean": 0.3, "median": 0.35, "mode": 0.25, "range": 0.2, "probability": 0.4, "combination": 0.65, "permutation": 0.7}
        return base_diff.get(ptype, 0.3)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.2: return 5
        elif difficulty < 0.4: return 6
        elif difficulty < 0.6: return 7
        elif difficulty < 0.8: return 8
        else: return 9

    def _get_grade_config(self, grade_level: int) -> Dict:
        return self.GRADE_CONFIG[max(5, min(9, grade_level))]

    def _make_distractors(self, answer, candidates: List) -> List[str]:
        distractors = set()
        for c in candidates:
            val = int(c) if isinstance(c, float) and c == int(c) else c
            if str(val) != str(answer) and (isinstance(val, (int, float)) and val > 0):
                distractors.add(str(val))
        while len(distractors) < 3:
            offset = random.choice([-3, -2, -1, 1, 2, 3])
            val = int(answer) + offset if str(answer).isdigit() else offset + 5
            if val > 0 and str(val) not in distractors:
                distractors.add(str(val))
        return list(distractors)[:3]
