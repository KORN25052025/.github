"""
Hint and Step-by-Step Solution Service.

Provides progressive hints and detailed solution explanations
for math questions to support learning without giving away answers.

Features:
- 3-level progressive hint system
- Step-by-step solution breakdowns
- LaTeX formatting for math expressions
- Turkish and English support
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class HintLevel(int, Enum):
    """Hint progression levels."""
    GENTLE = 1    # General strategy hint
    MODERATE = 2  # More specific guidance
    STRONG = 3    # Nearly gives the approach


@dataclass
class Hint:
    """A single hint."""
    level: HintLevel
    text: str
    text_tr: str  # Turkish translation
    xp_cost: int  # XP penalty for using hint


@dataclass
class SolutionStep:
    """A single step in the solution."""
    step_number: int
    description: str
    description_tr: str
    expression: str  # Math expression
    expression_latex: str  # LaTeX version
    explanation: str
    explanation_tr: str


@dataclass
class FullSolution:
    """Complete step-by-step solution."""
    question_id: str
    steps: List[SolutionStep]
    final_answer: str
    final_answer_latex: str
    total_steps: int


class HintService:
    """
    Generates hints and solutions for math questions.
    """

    # XP costs for hints
    HINT_COSTS = {
        HintLevel.GENTLE: 5,
        HintLevel.MODERATE: 10,
        HintLevel.STRONG: 20,
    }

    def get_hints(
        self,
        question_type: str,
        operation: Optional[str],
        expression: str,
        difficulty_tier: int,
    ) -> List[Hint]:
        """
        Generate progressive hints for a question.

        Args:
            question_type: Type of question (arithmetic, algebra, etc.)
            operation: Specific operation (add, subtract, etc.)
            expression: The math expression
            difficulty_tier: 1-5 difficulty level

        Returns:
            List of 3 hints from gentle to strong
        """
        hints = []

        if question_type == "arithmetic":
            hints = self._arithmetic_hints(operation, expression)
        elif question_type == "algebra":
            hints = self._algebra_hints(expression)
        elif question_type == "fractions":
            hints = self._fraction_hints(operation, expression)
        elif question_type == "percentages":
            hints = self._percentage_hints(expression)
        elif question_type == "geometry":
            hints = self._geometry_hints(operation, expression)
        elif question_type == "ratios":
            hints = self._ratio_hints(expression)
        else:
            hints = self._generic_hints()

        return hints

    def get_solution_steps(
        self,
        question_type: str,
        operation: Optional[str],
        expression: str,
        correct_answer: str,
        params: Optional[Dict] = None,
    ) -> FullSolution:
        """
        Generate step-by-step solution for a question.

        Args:
            question_type: Type of question
            operation: Specific operation
            expression: The math expression
            correct_answer: The correct answer
            params: Original question parameters

        Returns:
            FullSolution with all steps
        """
        steps = []

        if question_type == "arithmetic":
            steps = self._arithmetic_steps(operation, expression, correct_answer, params)
        elif question_type == "algebra":
            steps = self._algebra_steps(expression, correct_answer, params)
        elif question_type == "fractions":
            steps = self._fraction_steps(operation, expression, correct_answer, params)
        elif question_type == "percentages":
            steps = self._percentage_steps(expression, correct_answer, params)
        elif question_type == "geometry":
            steps = self._geometry_steps(operation, expression, correct_answer, params)
        elif question_type == "ratios":
            steps = self._ratio_steps(expression, correct_answer, params)
        else:
            steps = self._generic_steps(expression, correct_answer)

        return FullSolution(
            question_id="",
            steps=steps,
            final_answer=correct_answer,
            final_answer_latex=self._to_latex(correct_answer),
            total_steps=len(steps),
        )

    # ==================== ARITHMETIC ====================

    def _arithmetic_hints(self, operation: str, expression: str) -> List[Hint]:
        """Generate hints for arithmetic questions."""
        if operation == "add":
            return [
                Hint(HintLevel.GENTLE,
                     "Think about combining quantities together.",
                     "Miktarlari birlestirmeyi dusun.",
                     self.HINT_COSTS[HintLevel.GENTLE]),
                Hint(HintLevel.MODERATE,
                     "Start from the ones place and work left. Carry over if needed.",
                     "Birler basamagindan basla ve sola dogru ilerle. Gerekirse elde var.",
                     self.HINT_COSTS[HintLevel.MODERATE]),
                Hint(HintLevel.STRONG,
                     "Add each column: ones, tens, hundreds. Remember to carry!",
                     "Her sutunu topla: birler, onlar, yuzler. Eldeyi unutma!",
                     self.HINT_COSTS[HintLevel.STRONG]),
            ]
        elif operation == "subtract":
            return [
                Hint(HintLevel.GENTLE,
                     "Think about taking away or finding the difference.",
                     "Cikartmayi veya farki bulmavi dusun.",
                     self.HINT_COSTS[HintLevel.GENTLE]),
                Hint(HintLevel.MODERATE,
                     "Start from the right. If the top digit is smaller, borrow from the left.",
                     "Sagdan basla. Ustteki rakam kucukse, soldan odunc al.",
                     self.HINT_COSTS[HintLevel.MODERATE]),
                Hint(HintLevel.STRONG,
                     "Borrow from the tens place when needed. Subtract each column.",
                     "Gerektiginde onlar basamagindan odunc al. Her sutunu cikar.",
                     self.HINT_COSTS[HintLevel.STRONG]),
            ]
        elif operation == "multiply":
            return [
                Hint(HintLevel.GENTLE,
                     "Think about repeated addition or groups of numbers.",
                     "Tekrarli toplama veya sayi gruplarini dusun.",
                     self.HINT_COSTS[HintLevel.GENTLE]),
                Hint(HintLevel.MODERATE,
                     "Multiply each digit separately, then add the partial products.",
                     "Her rakami ayri ayri carp, sonra kismi carpimlari topla.",
                     self.HINT_COSTS[HintLevel.MODERATE]),
                Hint(HintLevel.STRONG,
                     "Use the standard algorithm: multiply, carry, then add rows.",
                     "Standart algoritmavi kullan: carp, elde, sonra satirlari topla.",
                     self.HINT_COSTS[HintLevel.STRONG]),
            ]
        elif operation == "divide":
            return [
                Hint(HintLevel.GENTLE,
                     "Think about splitting into equal groups.",
                     "Esit gruplara bolmeyi dusun.",
                     self.HINT_COSTS[HintLevel.GENTLE]),
                Hint(HintLevel.MODERATE,
                     "How many times does the divisor fit into the dividend?",
                     "Bolen, bolunenin icine kac kez sigar?",
                     self.HINT_COSTS[HintLevel.MODERATE]),
                Hint(HintLevel.STRONG,
                     "Use long division: divide, multiply, subtract, bring down.",
                     "Uzun bolme kullan: bol, carp, cikar, asagi indir.",
                     self.HINT_COSTS[HintLevel.STRONG]),
            ]
        else:
            return self._generic_hints()

    def _arithmetic_steps(
        self,
        operation: str,
        expression: str,
        answer: str,
        params: Optional[Dict]
    ) -> List[SolutionStep]:
        """Generate solution steps for arithmetic."""
        steps = []

        # Parse expression to get numbers
        numbers = re.findall(r'-?\d+\.?\d*', expression)
        if len(numbers) < 2:
            return self._generic_steps(expression, answer)

        a, b = float(numbers[0]), float(numbers[1])

        if operation == "add":
            steps = [
                SolutionStep(
                    step_number=1,
                    description="Write down both numbers",
                    description_tr="Iki sayiyi yaz",
                    expression=f"{a} + {b}",
                    expression_latex=f"{a} + {b}",
                    explanation="We need to add these two numbers together.",
                    explanation_tr="Bu iki sayiyi toplamamiz gerekiyor.",
                ),
                SolutionStep(
                    step_number=2,
                    description="Add the numbers",
                    description_tr="Sayilari topla",
                    expression=f"{a} + {b} = {a + b}",
                    expression_latex=f"{a} + {b} = {a + b}",
                    explanation=f"Adding {a} and {b} gives us {a + b}.",
                    explanation_tr=f"{a} ve {b} toplaninca {a + b} olur.",
                ),
            ]
        elif operation == "subtract":
            steps = [
                SolutionStep(
                    step_number=1,
                    description="Write down the subtraction",
                    description_tr="Cikarma islemini yaz",
                    expression=f"{a} - {b}",
                    expression_latex=f"{a} - {b}",
                    explanation="We need to subtract the second number from the first.",
                    explanation_tr="Ikinci sayiyi birinciden cikarmamiz gerekiyor.",
                ),
                SolutionStep(
                    step_number=2,
                    description="Perform the subtraction",
                    description_tr="Cikarma islemini yap",
                    expression=f"{a} - {b} = {a - b}",
                    expression_latex=f"{a} - {b} = {a - b}",
                    explanation=f"Subtracting {b} from {a} gives us {a - b}.",
                    explanation_tr=f"{a}'dan {b} cikarilinca {a - b} olur.",
                ),
            ]
        elif operation == "multiply":
            steps = [
                SolutionStep(
                    step_number=1,
                    description="Write down the multiplication",
                    description_tr="Carpma islemini yaz",
                    expression=f"{a} × {b}",
                    expression_latex=f"{a} \\times {b}",
                    explanation="We need to multiply these two numbers.",
                    explanation_tr="Bu iki sayiyi carpmamiz gerekiyor.",
                ),
                SolutionStep(
                    step_number=2,
                    description="Perform the multiplication",
                    description_tr="Carpma islemini yap",
                    expression=f"{a} × {b} = {a * b}",
                    expression_latex=f"{a} \\times {b} = {a * b}",
                    explanation=f"Multiplying {a} by {b} gives us {a * b}.",
                    explanation_tr=f"{a} ile {b} carpilinca {a * b} olur.",
                ),
            ]
        elif operation == "divide":
            result = a / b if b != 0 else 0
            steps = [
                SolutionStep(
                    step_number=1,
                    description="Write down the division",
                    description_tr="Bolme islemini yaz",
                    expression=f"{a} ÷ {b}",
                    expression_latex=f"{a} \\div {b}",
                    explanation="We need to divide the first number by the second.",
                    explanation_tr="Birinci sayiyi ikinciye bolmemiz gerekiyor.",
                ),
                SolutionStep(
                    step_number=2,
                    description="Perform the division",
                    description_tr="Bolme islemini yap",
                    expression=f"{a} ÷ {b} = {result}",
                    expression_latex=f"{a} \\div {b} = {result}",
                    explanation=f"Dividing {a} by {b} gives us {result}.",
                    explanation_tr=f"{a}, {b}'ye bolununce {result} olur.",
                ),
            ]

        return steps

    # ==================== ALGEBRA ====================

    def _algebra_hints(self, expression: str) -> List[Hint]:
        """Generate hints for algebra questions."""
        return [
            Hint(HintLevel.GENTLE,
                 "Isolate the variable on one side of the equation.",
                 "Degiskeni denklemin bir tarafinda yalniz birak.",
                 self.HINT_COSTS[HintLevel.GENTLE]),
            Hint(HintLevel.MODERATE,
                 "Do the same operation to both sides to keep the equation balanced.",
                 "Denklemi dengede tutmak icin her iki tarafa ayni islemi yap.",
                 self.HINT_COSTS[HintLevel.MODERATE]),
            Hint(HintLevel.STRONG,
                 "First add/subtract to move constants, then divide by the coefficient.",
                 "Once sabitleri tasimak icin topla/cikar, sonra katsayiya bol.",
                 self.HINT_COSTS[HintLevel.STRONG]),
        ]

    def _algebra_steps(
        self,
        expression: str,
        answer: str,
        params: Optional[Dict]
    ) -> List[SolutionStep]:
        """Generate solution steps for algebra."""
        # Parse a simple linear equation like "3x + 5 = 14"
        steps = []

        # Try to parse ax + b = c format
        match = re.match(r'(-?\d*)x\s*([+-])\s*(\d+)\s*=\s*(-?\d+)', expression.replace(' ', ''))
        if match:
            a = int(match.group(1)) if match.group(1) and match.group(1) != '-' else (
                -1 if match.group(1) == '-' else 1)
            sign = match.group(2)
            b = int(match.group(3))
            c = int(match.group(4))

            if sign == '-':
                b = -b

            steps = [
                SolutionStep(
                    step_number=1,
                    description="Start with the equation",
                    description_tr="Denklemle basla",
                    expression=expression,
                    expression_latex=f"{a}x + {b} = {c}" if b >= 0 else f"{a}x - {-b} = {c}",
                    explanation="This is a linear equation. We need to find x.",
                    explanation_tr="Bu bir dogrusal denklem. x'i bulmamiz gerekiyor.",
                ),
                SolutionStep(
                    step_number=2,
                    description=f"{'Subtract' if b > 0 else 'Add'} {abs(b)} from both sides",
                    description_tr=f"Her iki taraftan {abs(b)} {'cikar' if b > 0 else 'ekle'}",
                    expression=f"{a}x = {c} - {b}" if b > 0 else f"{a}x = {c} + {-b}",
                    expression_latex=f"{a}x = {c - b}",
                    explanation=f"Move the constant to the right side.",
                    explanation_tr=f"Sabiti sag tarafa tasi.",
                ),
                SolutionStep(
                    step_number=3,
                    description=f"Divide both sides by {a}",
                    description_tr=f"Her iki tarafi {a}'e bol",
                    expression=f"x = {c - b} ÷ {a}",
                    expression_latex=f"x = \\frac{{{c - b}}}{{{a}}}",
                    explanation=f"Divide to isolate x.",
                    explanation_tr=f"x'i yalniz birakmak icin bol.",
                ),
                SolutionStep(
                    step_number=4,
                    description="Calculate the final answer",
                    description_tr="Sonucu hesapla",
                    expression=f"x = {(c - b) // a}",
                    expression_latex=f"x = {(c - b) // a}",
                    explanation=f"The answer is x = {(c - b) // a}.",
                    explanation_tr=f"Cevap x = {(c - b) // a}.",
                ),
            ]

        return steps if steps else self._generic_steps(expression, answer)

    # ==================== FRACTIONS ====================

    def _fraction_hints(self, operation: str, expression: str) -> List[Hint]:
        """Generate hints for fraction questions."""
        return [
            Hint(HintLevel.GENTLE,
                 "Remember: a fraction has a numerator (top) and denominator (bottom).",
                 "Unutma: Kesirin pavi (ust) ve paydasi (alt) vardir.",
                 self.HINT_COSTS[HintLevel.GENTLE]),
            Hint(HintLevel.MODERATE,
                 "For addition/subtraction, find a common denominator first.",
                 "Toplama/cikarma icin once ortak payda bul.",
                 self.HINT_COSTS[HintLevel.MODERATE]),
            Hint(HintLevel.STRONG,
                 "Multiply numerator × numerator and denominator × denominator for multiplication.",
                 "Carpma icin pay × pay ve payda × payda carp.",
                 self.HINT_COSTS[HintLevel.STRONG]),
        ]

    def _fraction_steps(
        self,
        operation: str,
        expression: str,
        answer: str,
        params: Optional[Dict]
    ) -> List[SolutionStep]:
        """Generate solution steps for fractions."""
        return self._generic_steps(expression, answer)

    # ==================== PERCENTAGES ====================

    def _percentage_hints(self, expression: str) -> List[Hint]:
        """Generate hints for percentage questions."""
        return [
            Hint(HintLevel.GENTLE,
                 "Percent means 'per hundred' or 'out of 100'.",
                 "Yuzde 'yuz ustunden' veya '100'de' demektir.",
                 self.HINT_COSTS[HintLevel.GENTLE]),
            Hint(HintLevel.MODERATE,
                 "To find X% of a number, multiply by X/100.",
                 "Bir sayinin %X'ini bulmak icin X/100 ile carp.",
                 self.HINT_COSTS[HintLevel.MODERATE]),
            Hint(HintLevel.STRONG,
                 "Convert percentage to decimal (divide by 100), then multiply.",
                 "Yuzdeyi ondaliga cevir (100'e bol), sonra carp.",
                 self.HINT_COSTS[HintLevel.STRONG]),
        ]

    def _percentage_steps(
        self,
        expression: str,
        answer: str,
        params: Optional[Dict]
    ) -> List[SolutionStep]:
        """Generate solution steps for percentages."""
        return self._generic_steps(expression, answer)

    # ==================== GEOMETRY ====================

    def _geometry_hints(self, operation: str, expression: str) -> List[Hint]:
        """Generate hints for geometry questions."""
        if "area" in operation.lower() or "alan" in expression.lower():
            return [
                Hint(HintLevel.GENTLE,
                     "Area is the space inside a shape, measured in square units.",
                     "Alan, seklin icindeki bosluktur, kare birimlerle olculur.",
                     self.HINT_COSTS[HintLevel.GENTLE]),
                Hint(HintLevel.MODERATE,
                     "Rectangle area = length × width. Circle area = π × r².",
                     "Dikdortgen alani = uzunluk × genislik. Daire alani = π × r².",
                     self.HINT_COSTS[HintLevel.MODERATE]),
                Hint(HintLevel.STRONG,
                     "Plug the given measurements into the area formula.",
                     "Verilen olculeri alan formulune yerlestir.",
                     self.HINT_COSTS[HintLevel.STRONG]),
            ]
        else:  # perimeter
            return [
                Hint(HintLevel.GENTLE,
                     "Perimeter is the distance around the outside of a shape.",
                     "Cevre, seklin dis kenarlarinin toplam uzunlugudur.",
                     self.HINT_COSTS[HintLevel.GENTLE]),
                Hint(HintLevel.MODERATE,
                     "Add up all the sides of the shape.",
                     "Seklin tum kenarlarini topla.",
                     self.HINT_COSTS[HintLevel.MODERATE]),
                Hint(HintLevel.STRONG,
                     "Rectangle perimeter = 2 × (length + width).",
                     "Dikdortgen cevresi = 2 × (uzunluk + genislik).",
                     self.HINT_COSTS[HintLevel.STRONG]),
            ]

    def _geometry_steps(
        self,
        operation: str,
        expression: str,
        answer: str,
        params: Optional[Dict]
    ) -> List[SolutionStep]:
        """Generate solution steps for geometry."""
        return self._generic_steps(expression, answer)

    # ==================== RATIOS ====================

    def _ratio_hints(self, expression: str) -> List[Hint]:
        """Generate hints for ratio questions."""
        return [
            Hint(HintLevel.GENTLE,
                 "A ratio compares two quantities. Think about the relationship.",
                 "Oran iki miktari karsilastirir. Iliskiyi dusun.",
                 self.HINT_COSTS[HintLevel.GENTLE]),
            Hint(HintLevel.MODERATE,
                 "Set up a proportion: a/b = c/d, then cross-multiply.",
                 "Oranli kurulum yap: a/b = c/d, sonra capraz carp.",
                 self.HINT_COSTS[HintLevel.MODERATE]),
            Hint(HintLevel.STRONG,
                 "Cross-multiply and solve: a × d = b × c.",
                 "Capraz carp ve coz: a × d = b × c.",
                 self.HINT_COSTS[HintLevel.STRONG]),
        ]

    def _ratio_steps(
        self,
        expression: str,
        answer: str,
        params: Optional[Dict]
    ) -> List[SolutionStep]:
        """Generate solution steps for ratios."""
        return self._generic_steps(expression, answer)

    # ==================== GENERIC ====================

    def _generic_hints(self) -> List[Hint]:
        """Generic hints for any question type."""
        return [
            Hint(HintLevel.GENTLE,
                 "Read the problem carefully and identify what you need to find.",
                 "Problemi dikkatli oku ve ne bulman gerektigini belirle.",
                 self.HINT_COSTS[HintLevel.GENTLE]),
            Hint(HintLevel.MODERATE,
                 "Write down the given information and the formula you need.",
                 "Verilen bilgileri ve gereken formulu yaz.",
                 self.HINT_COSTS[HintLevel.MODERATE]),
            Hint(HintLevel.STRONG,
                 "Substitute the values into the formula and calculate step by step.",
                 "Degerleri formule yerlestir ve adim adim hesapla.",
                 self.HINT_COSTS[HintLevel.STRONG]),
        ]

    def _generic_steps(self, expression: str, answer: str) -> List[SolutionStep]:
        """Generic solution steps."""
        return [
            SolutionStep(
                step_number=1,
                description="Understand the problem",
                description_tr="Problemi anla",
                expression=expression,
                expression_latex=self._to_latex(expression),
                explanation="Read the problem and identify what needs to be calculated.",
                explanation_tr="Problemi oku ve neyin hesaplanmasi gerektigini belirle.",
            ),
            SolutionStep(
                step_number=2,
                description="Calculate the answer",
                description_tr="Cevabi hesapla",
                expression=f"= {answer}",
                expression_latex=f"= {answer}",
                explanation=f"The final answer is {answer}.",
                explanation_tr=f"Sonuc {answer}.",
            ),
        ]

    def _to_latex(self, text: str) -> str:
        """Convert expression to LaTeX format."""
        return (text
                .replace('×', '\\times')
                .replace('÷', '\\div')
                .replace('*', '\\times')
                .replace('/', '\\div'))


# Global instance
hint_service = HintService()
