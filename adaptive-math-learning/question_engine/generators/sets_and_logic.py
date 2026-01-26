"""
Sets & Logic Question Generator.

Generates questions about set operations (union, intersection, difference),
Venn diagrams, and basic logic.
"""

import random
from typing import List, Optional, Dict, Any, Set, FrozenSet

from ..base import (
    QuestionGenerator,
    QuestionType,
    OperationType,
    AnswerFormat,
    GeneratedQuestion,
)
from ..registry import register_generator


@register_generator
class SetsAndLogicGenerator(QuestionGenerator):
    """
    Generator for set theory and logic questions.

    Supports:
    - Set union (A ∪ B)
    - Set intersection (A ∩ B)
    - Set difference (A \\ B)
    - Venn diagram problems (element counting)
    - Cardinality problems
    """

    GRADE_CONFIG = {
        6: {"max_element": 20, "set_size": 5, "types": ["union", "intersection"]},
        7: {"max_element": 30, "set_size": 7, "types": ["union", "intersection", "difference"]},
        8: {"max_element": 50, "set_size": 8, "types": ["union", "intersection", "difference", "venn_two"]},
        9: {"max_element": 50, "set_size": 10, "types": ["union", "intersection", "difference", "venn_two", "venn_three"]},
        10: {"max_element": 100, "set_size": 10, "types": ["union", "intersection", "difference", "venn_two", "venn_three"]},
    }

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.SETS_AND_LOGIC

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.SET_UNION, OperationType.SET_INTERSECTION,
                OperationType.SET_DIFFERENCE, OperationType.VENN_DIAGRAM]

    def generate(self, difficulty: float = 0.5, operation: Optional[OperationType] = None,
                 grade_level: Optional[int] = None, seed: Optional[int] = None, **kwargs) -> GeneratedQuestion:
        if seed is not None:
            random.seed(seed)
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)
        config = self._get_grade_config(grade_level)
        problem_type = random.choice(config["types"])

        generators = {
            "union": self._generate_union,
            "intersection": self._generate_intersection,
            "difference": self._generate_difference,
            "venn_two": self._generate_venn_two,
            "venn_three": self._generate_venn_three,
        }
        return generators.get(problem_type, self._generate_union)(difficulty, config, grade_level)

    def _make_sets(self, config: Dict, difficulty: float, overlap: int = 2):
        """Generate two sets with controlled overlap."""
        max_el = max(10, int(config["max_element"] * (0.3 + 0.7 * difficulty)))
        size_a = max(3, int(config["set_size"] * (0.4 + 0.6 * difficulty)))
        size_b = max(3, int(config["set_size"] * (0.4 + 0.6 * difficulty)))

        pool = list(range(1, max_el + 1))
        random.shuffle(pool)

        # Create overlap first
        overlap_count = min(overlap, size_a, size_b, len(pool))
        common = set(pool[:overlap_count])
        remaining = pool[overlap_count:]

        only_a_count = size_a - overlap_count
        only_b_count = size_b - overlap_count

        only_a = set(remaining[:only_a_count])
        only_b = set(remaining[only_a_count:only_a_count + only_b_count])

        set_a = sorted(common | only_a)
        set_b = sorted(common | only_b)
        return set_a, set_b

    def _format_set(self, s) -> str:
        return "{" + ", ".join(str(x) for x in sorted(s)) + "}"

    def _generate_union(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        set_a, set_b = self._make_sets(config, difficulty)
        result = sorted(set(set_a) | set(set_b))
        answer = self._format_set(result)

        expression = f"Find A ∪ B where A = {self._format_set(set_a)} and B = {self._format_set(set_b)}"

        intersection = sorted(set(set_a) & set(set_b))
        diff = sorted(set(set_a) - set(set_b))
        distractors = [
            self._format_set(intersection),
            self._format_set(diff),
            self._format_set(sorted(set(set_a) | set(set_b))[:-1]) if result else "{0}",
        ]
        distractors = [d for d in distractors if d != answer][:3]
        while len(distractors) < 3:
            distractors.append(self._format_set(set_a))

        calc_difficulty = 0.2 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="sets_union",
            question_type=self.question_type,
            operation=OperationType.SET_UNION,
            expression=expression,
            expression_latex=f"$A \\cup B$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors[:3],
            all_options=self._shuffle_options(answer, distractors[:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"set_a": set_a, "set_b": set_b, "answer": answer, "type": "union", "grade_level": grade_level},
        )

    def _generate_intersection(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        overlap = random.randint(2, 4)
        set_a, set_b = self._make_sets(config, difficulty, overlap=overlap)
        result = sorted(set(set_a) & set(set_b))
        answer = self._format_set(result) if result else "∅"

        expression = f"Find A ∩ B where A = {self._format_set(set_a)} and B = {self._format_set(set_b)}"

        union = sorted(set(set_a) | set(set_b))
        distractors = [
            self._format_set(union),
            self._format_set(sorted(set(set_a) - set(set_b))),
            "∅" if result else self._format_set(set_a),
        ]
        distractors = [d for d in distractors if d != answer][:3]
        while len(distractors) < 3:
            distractors.append(self._format_set(set_b))

        calc_difficulty = 0.25 + 0.15 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="sets_intersection",
            question_type=self.question_type,
            operation=OperationType.SET_INTERSECTION,
            expression=expression,
            expression_latex=f"$A \\cap B$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors[:3],
            all_options=self._shuffle_options(answer, distractors[:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"set_a": set_a, "set_b": set_b, "answer": answer, "type": "intersection", "grade_level": grade_level},
        )

    def _generate_difference(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        overlap = random.randint(1, 3)
        set_a, set_b = self._make_sets(config, difficulty, overlap=overlap)
        result = sorted(set(set_a) - set(set_b))
        answer = self._format_set(result) if result else "∅"

        expression = f"Find A \\ B (A minus B) where A = {self._format_set(set_a)} and B = {self._format_set(set_b)}"

        distractors = [
            self._format_set(sorted(set(set_b) - set(set_a))),
            self._format_set(sorted(set(set_a) & set(set_b))),
            self._format_set(sorted(set(set_a) | set(set_b))),
        ]
        distractors = [d for d in distractors if d != answer][:3]

        calc_difficulty = 0.3 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="sets_difference",
            question_type=self.question_type,
            operation=OperationType.SET_DIFFERENCE,
            expression=expression,
            expression_latex=f"$A \\setminus B$",
            correct_answer=answer,
            answer_format=AnswerFormat.EXPRESSION,
            distractors=distractors[:3],
            all_options=self._shuffle_options(answer, distractors[:3]),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"set_a": set_a, "set_b": set_b, "answer": answer, "type": "difference", "grade_level": grade_level},
        )

    def _generate_venn_two(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        """Venn diagram counting problem with 2 sets."""
        only_a = random.randint(3, 15)
        only_b = random.randint(3, 15)
        both = random.randint(1, 8)
        neither = random.randint(0, 5) if difficulty > 0.4 else 0
        total = only_a + only_b + both + neither

        n_a = only_a + both
        n_b = only_b + both

        question_type = random.choice(["total", "only_a", "only_b", "union", "neither"])

        if question_type == "total":
            expression = f"In a class of {total} students, {n_a} study Math and {n_b} study Science. {both} study both. How many study neither?"
            answer = neither
        elif question_type == "only_a":
            expression = f"{n_a} students study Math, {n_b} study Science, and {both} study both. How many study ONLY Math?"
            answer = only_a
        elif question_type == "only_b":
            expression = f"{n_a} students study Math, {n_b} study Science, and {both} study both. How many study ONLY Science?"
            answer = only_b
        elif question_type == "union":
            expression = f"{n_a} students study Math, {n_b} study Science, and {both} study both. How many study at least one subject?"
            answer = n_a + n_b - both
        else:
            expression = f"In a group of {total}, {n_a} like football, {n_b} like basketball, and {both} like both. How many like neither?"
            answer = neither

        distractors = self._make_num_distractors(answer, [
            n_a, n_b, both, total, n_a + n_b, only_a, only_b,
        ])

        calc_difficulty = 0.4 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="sets_venn_two",
            question_type=self.question_type,
            operation=OperationType.VENN_DIAGRAM,
            expression=expression,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"only_a": only_a, "only_b": only_b, "both": both, "neither": neither,
                        "total": total, "answer": answer, "type": "venn_two", "grade_level": grade_level},
        )

    def _generate_venn_three(self, difficulty: float, config: Dict, grade_level: int) -> GeneratedQuestion:
        """Venn diagram counting problem with 3 sets."""
        only_a = random.randint(2, 10)
        only_b = random.randint(2, 10)
        only_c = random.randint(2, 10)
        ab = random.randint(1, 5)
        bc = random.randint(1, 5)
        ac = random.randint(1, 5)
        abc = random.randint(1, 3)

        n_a = only_a + ab + ac + abc
        n_b = only_b + ab + bc + abc
        n_c = only_c + ac + bc + abc
        total_in_sets = only_a + only_b + only_c + ab + bc + ac + abc

        expression = (
            f"In a survey: {n_a} like Math, {n_b} like Science, {n_c} like Art. "
            f"{ab + abc} like Math & Science, {bc + abc} like Science & Art, {ac + abc} like Math & Art, "
            f"and {abc} like all three. How many like at least one subject?"
        )
        answer = total_in_sets

        distractors = self._make_num_distractors(answer, [
            n_a + n_b + n_c,
            n_a + n_b + n_c - ab - bc - ac,
            total_in_sets + random.randint(1, 5),
            total_in_sets - abc,
        ])

        calc_difficulty = 0.65 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="sets_venn_three",
            question_type=self.question_type,
            operation=OperationType.VENN_DIAGRAM,
            expression=expression,
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=min(1.0, calc_difficulty),
            difficulty_tier=self._get_difficulty_tier(min(1.0, calc_difficulty)),
            parameters={"answer": answer, "type": "venn_three", "grade_level": grade_level},
        )

    def compute_answer(self, **parameters) -> Any:
        return parameters.get("answer", 0)

    def generate_distractors(self, correct_answer: Any, parameters: Dict[str, Any], count: int = 3) -> List[Any]:
        return []

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        ptype = parameters.get("type", "union")
        return {"union": 0.25, "intersection": 0.3, "difference": 0.4, "venn_two": 0.5, "venn_three": 0.7}.get(ptype, 0.3)

    def _difficulty_to_grade(self, difficulty: float) -> int:
        if difficulty < 0.2: return 6
        elif difficulty < 0.4: return 7
        elif difficulty < 0.6: return 8
        elif difficulty < 0.8: return 9
        else: return 10

    def _get_grade_config(self, grade_level: int) -> Dict:
        return self.GRADE_CONFIG[max(6, min(10, grade_level))]

    def _make_num_distractors(self, answer: int, candidates: List) -> List[str]:
        distractors = set()
        for c in candidates:
            v = int(c) if isinstance(c, float) else c
            if v != answer and v >= 0:
                distractors.add(str(v))
        while len(distractors) < 3:
            offset = random.choice([-2, -1, 1, 2, 3])
            v = answer + offset
            if v >= 0 and str(v) not in distractors:
                distractors.add(str(v))
        return list(distractors)[:3]
