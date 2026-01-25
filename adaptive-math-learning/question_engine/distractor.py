"""
Distractor generation for multiple choice questions.

Generates pedagogically meaningful wrong answers based on
common student misconceptions and error patterns.
"""

from typing import List, Union, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import random

from .base import OperationType


class DistractorType(str, Enum):
    """Types of distractors based on common student errors."""
    SIGN_ERROR = "sign_error"           # Negating the answer
    OFF_BY_ONE = "off_by_one"           # Adding/subtracting 1
    MAGNITUDE_ERROR = "magnitude_error"  # Decimal place error
    OPERATION_CONFUSION = "op_confusion" # Using wrong operation
    PARTIAL_SOLUTION = "partial"         # Stopping at intermediate step
    RANDOM_CLOSE = "random_close"        # Random value near answer


@dataclass
class Distractor:
    """A distractor with its value and type."""
    value: Any
    distractor_type: DistractorType
    explanation: str = ""


class DistractorGenerator:
    """
    Generates plausible wrong answers for multiple choice questions.

    Each distractor is designed to catch common student errors:
    - Sign errors (forgetting to negate)
    - Off-by-one errors (common in counting)
    - Magnitude errors (decimal place mistakes)
    - Operation confusion (adding instead of multiplying)
    - Partial solutions (stopping before final step)
    """

    def generate(
        self,
        correct_answer: Union[int, float],
        count: int = 3,
        operation: Optional[OperationType] = None,
        operands: Optional[List[Union[int, float]]] = None,
        exclude: Optional[Set[Any]] = None,
    ) -> List[Any]:
        """
        Generate distractors for a given correct answer.

        Args:
            correct_answer: The correct answer to generate alternatives for
            count: Number of distractors to generate
            operation: The operation used (helps generate operation confusion errors)
            operands: The operands used (helps generate partial solutions)
            exclude: Values to exclude from distractors

        Returns:
            List of distractor values
        """
        exclude = exclude or set()
        exclude.add(correct_answer)

        distractors: List[Distractor] = []
        attempts = 0
        max_attempts = count * 10

        # Generate using different strategies
        strategies = [
            self._sign_error,
            self._off_by_one_plus,
            self._off_by_one_minus,
            self._magnitude_error,
            self._random_close,
        ]

        # Add operation confusion if operands provided
        if operands and len(operands) >= 2 and operation:
            strategies.append(
                lambda ans, op=operation, ops=operands: self._operation_confusion(ans, op, ops)
            )

        # Try each strategy
        for strategy in strategies:
            if len(distractors) >= count:
                break

            result = strategy(correct_answer)
            if result is not None and result not in exclude:
                # Ensure it's a valid number
                if isinstance(correct_answer, int):
                    result = int(round(result))
                if result != correct_answer and result not in exclude:
                    distractors.append(Distractor(value=result, distractor_type=DistractorType.RANDOM_CLOSE))
                    exclude.add(result)

        # Fill remaining with random close values
        while len(distractors) < count and attempts < max_attempts:
            attempts += 1
            result = self._random_close(correct_answer)
            if isinstance(correct_answer, int):
                result = int(round(result))
            if result not in exclude and result != correct_answer:
                distractors.append(Distractor(value=result, distractor_type=DistractorType.RANDOM_CLOSE))
                exclude.add(result)

        return [d.value for d in distractors[:count]]

    def _sign_error(self, answer: Union[int, float]) -> Optional[Union[int, float]]:
        """Generate sign error distractor."""
        if answer == 0:
            return None
        return -answer

    def _off_by_one_plus(self, answer: Union[int, float]) -> Union[int, float]:
        """Generate off-by-one (plus) distractor."""
        return answer + 1

    def _off_by_one_minus(self, answer: Union[int, float]) -> Optional[Union[int, float]]:
        """Generate off-by-one (minus) distractor."""
        result = answer - 1
        # Avoid negative results for simple problems
        if result < 0 and answer > 0:
            return answer + 2
        return result

    def _magnitude_error(self, answer: Union[int, float]) -> Optional[Union[int, float]]:
        """Generate magnitude error distractor (decimal place error)."""
        if answer == 0:
            return None
        if abs(answer) < 10:
            return answer * 10
        return answer // 10 if isinstance(answer, int) else answer / 10

    def _operation_confusion(
        self,
        answer: Union[int, float],
        operation: OperationType,
        operands: List[Union[int, float]]
    ) -> Optional[Union[int, float]]:
        """Generate distractor based on using wrong operation."""
        if len(operands) < 2:
            return None

        a, b = operands[0], operands[1]

        # Map to confused operations
        confusion_map = {
            OperationType.ADDITION: lambda x, y: x - y,
            OperationType.SUBTRACTION: lambda x, y: x + y,
            OperationType.MULTIPLICATION: lambda x, y: x + y,
            OperationType.DIVISION: lambda x, y: x * y if y < 20 else x - y,
        }

        confused_op = confusion_map.get(operation)
        if confused_op:
            try:
                return confused_op(a, b)
            except:
                return None
        return None

    def _random_close(self, answer: Union[int, float]) -> Union[int, float]:
        """Generate random value close to the answer."""
        if answer == 0:
            return random.choice([-2, -1, 1, 2, 3])

        # Determine range based on answer magnitude
        magnitude = abs(answer)
        if magnitude < 10:
            delta = random.randint(2, 5)
        elif magnitude < 100:
            delta = random.randint(5, 15)
        elif magnitude < 1000:
            delta = random.randint(10, 50)
        else:
            delta = int(magnitude * random.uniform(0.05, 0.15))

        offset = random.choice([-1, 1]) * delta
        result = answer + offset

        # Ensure positive for simple problems
        if answer > 0 and result <= 0:
            result = answer + abs(delta)

        return result


# Global distractor generator instance
distractor_generator = DistractorGenerator()
