"""
Difficulty calculation utilities for the question engine.

Provides objective difficulty scoring based on mathematical complexity factors.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from .base import OperationType, DifficultyTier


@dataclass
class DifficultyFactors:
    """Factors that contribute to question difficulty."""
    operation_weight: float = 0.0
    magnitude_weight: float = 0.0
    step_count_weight: float = 0.0
    negative_numbers_weight: float = 0.0
    fraction_weight: float = 0.0
    decimal_weight: float = 0.0


class DifficultyCalculator:
    """
    Calculates objective difficulty scores for math questions.

    The difficulty score is a weighted combination of multiple factors:
    - Operation complexity (e.g., division > multiplication > addition)
    - Number magnitude (larger numbers are harder)
    - Number of steps required
    - Presence of negative numbers
    - Presence of fractions or decimals
    """

    # Operation difficulty weights (0.0 to 1.0)
    OPERATION_WEIGHTS = {
        OperationType.ADDITION: 0.1,
        OperationType.SUBTRACTION: 0.2,
        OperationType.MULTIPLICATION: 0.4,
        OperationType.DIVISION: 0.5,
        OperationType.MIXED: 0.6,
        OperationType.LINEAR: 0.5,
        OperationType.QUADRATIC: 0.8,
        OperationType.AREA: 0.3,
        OperationType.PERIMETER: 0.2,
        OperationType.VOLUME: 0.5,
    }

    # Magnitude thresholds for difficulty scaling
    MAGNITUDE_THRESHOLDS = [
        (10, 0.1),      # Single digit: very easy
        (100, 0.2),     # Two digits: easy
        (1000, 0.4),    # Three digits: medium
        (10000, 0.6),   # Four digits: hard
        (100000, 0.8),  # Five+ digits: very hard
    ]

    def __init__(self):
        self.weights = {
            "operation": 0.3,
            "magnitude": 0.25,
            "steps": 0.2,
            "negative": 0.1,
            "fraction": 0.1,
            "decimal": 0.05,
        }

    def calculate(
        self,
        operation: OperationType,
        operands: List[float],
        step_count: int = 1,
        has_negatives: bool = False,
        has_fractions: bool = False,
        has_decimals: bool = False,
    ) -> float:
        """
        Calculate difficulty score for a question.

        Args:
            operation: The mathematical operation used
            operands: List of operand values
            step_count: Number of steps to solve
            has_negatives: Whether negative numbers are involved
            has_fractions: Whether fractions are involved
            has_decimals: Whether decimal numbers are involved

        Returns:
            Difficulty score from 0.0 to 1.0
        """
        # Operation difficulty
        op_diff = self.OPERATION_WEIGHTS.get(operation, 0.3)

        # Magnitude difficulty (based on largest operand)
        max_operand = max(abs(x) for x in operands) if operands else 10
        mag_diff = self._calculate_magnitude_difficulty(max_operand)

        # Step count difficulty
        step_diff = min(1.0, (step_count - 1) * 0.15)

        # Negative numbers add difficulty
        neg_diff = 0.3 if has_negatives else 0.0

        # Fractions add significant difficulty
        frac_diff = 0.4 if has_fractions else 0.0

        # Decimals add some difficulty
        dec_diff = 0.2 if has_decimals else 0.0

        # Weighted combination
        total = (
            self.weights["operation"] * op_diff +
            self.weights["magnitude"] * mag_diff +
            self.weights["steps"] * step_diff +
            self.weights["negative"] * neg_diff +
            self.weights["fraction"] * frac_diff +
            self.weights["decimal"] * dec_diff
        )

        return min(1.0, max(0.0, total))

    def _calculate_magnitude_difficulty(self, value: float) -> float:
        """Calculate difficulty contribution from number magnitude."""
        abs_value = abs(value)
        for threshold, difficulty in self.MAGNITUDE_THRESHOLDS:
            if abs_value < threshold:
                return difficulty
        return 1.0

    def get_tier(self, difficulty: float) -> DifficultyTier:
        """Map difficulty score to difficulty tier."""
        if difficulty < 0.2:
            return DifficultyTier.NOVICE
        elif difficulty < 0.4:
            return DifficultyTier.BEGINNER
        elif difficulty < 0.6:
            return DifficultyTier.INTERMEDIATE
        elif difficulty < 0.8:
            return DifficultyTier.ADVANCED
        else:
            return DifficultyTier.EXPERT

    def adjust_parameters_for_difficulty(
        self,
        target_difficulty: float,
        base_range: tuple,
    ) -> tuple:
        """
        Adjust parameter range based on target difficulty.

        Args:
            target_difficulty: Target difficulty (0.0 to 1.0)
            base_range: Base (min, max) range for parameters

        Returns:
            Adjusted (min, max) range
        """
        min_val, max_val = base_range
        range_size = max_val - min_val

        # Scale range based on difficulty
        # Lower difficulty = smaller portion of range
        # Higher difficulty = larger portion of range
        scale_factor = 0.2 + (0.8 * target_difficulty)

        adjusted_max = min_val + int(range_size * scale_factor)
        adjusted_min = min_val + int((adjusted_max - min_val) * (target_difficulty * 0.3))

        return (max(min_val, adjusted_min), max(adjusted_min + 1, adjusted_max))


# Global calculator instance
difficulty_calculator = DifficultyCalculator()
