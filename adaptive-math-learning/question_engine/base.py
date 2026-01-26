"""
Base classes for the deterministic question generation engine.

The Question Engine is responsible for generating mathematically correct
questions with guaranteed accurate answers. It separates the mathematical
correctness concern from the presentation concern.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import uuid
from datetime import datetime


class QuestionType(str, Enum):
    """Types of mathematical questions supported by the system."""
    ARITHMETIC = "arithmetic"
    FRACTIONS = "fractions"
    PERCENTAGES = "percentages"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    RATIOS = "ratios"
    EXPONENTS = "exponents"
    STATISTICS = "statistics"
    NUMBER_THEORY = "number_theory"
    SYSTEMS_OF_EQUATIONS = "systems_of_equations"
    INEQUALITIES = "inequalities"
    FUNCTIONS = "functions"
    TRIGONOMETRY = "trigonometry"
    POLYNOMIALS = "polynomials"
    SETS_AND_LOGIC = "sets_and_logic"
    COORDINATE_GEOMETRY = "coordinate_geometry"


class OperationType(str, Enum):
    """Mathematical operations supported within question types."""
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"
    MIXED = "mixed"
    # Algebra operations
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    # Geometry operations
    AREA = "area"
    PERIMETER = "perimeter"
    VOLUME = "volume"
    # Exponents & Roots
    EXPONENTIATION = "exponentiation"
    SQUARE_ROOT = "square_root"
    CUBE_ROOT = "cube_root"
    SCIENTIFIC_NOTATION = "scientific_notation"
    # Statistics & Probability
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    RANGE = "range"
    PROBABILITY = "probability"
    COMBINATION = "combination"
    PERMUTATION = "permutation"
    # Number Theory
    PRIME = "prime"
    GCD = "gcd"
    LCM = "lcm"
    DIVISIBILITY = "divisibility"
    FACTORIZATION = "factorization"
    # Systems of Equations
    TWO_VARIABLE = "two_variable"
    THREE_VARIABLE = "three_variable"
    # Inequalities
    LINEAR_INEQUALITY = "linear_inequality"
    COMPOUND_INEQUALITY = "compound_inequality"
    ABSOLUTE_VALUE_INEQUALITY = "absolute_value_inequality"
    # Functions
    LINEAR_FUNCTION = "linear_function"
    QUADRATIC_FUNCTION = "quadratic_function"
    DOMAIN_RANGE = "domain_range"
    COMPOSITION = "composition"
    INVERSE_FUNCTION = "inverse_function"
    # Trigonometry
    SINE = "sine"
    COSINE = "cosine"
    TANGENT = "tangent"
    TRIG_EQUATION = "trig_equation"
    # Polynomials
    POLYNOMIAL_ADD = "polynomial_add"
    POLYNOMIAL_MULTIPLY = "polynomial_multiply"
    FACTORING = "factoring"
    POLYNOMIAL_DIVISION = "polynomial_division"
    # Sets & Logic
    SET_UNION = "set_union"
    SET_INTERSECTION = "set_intersection"
    SET_DIFFERENCE = "set_difference"
    VENN_DIAGRAM = "venn_diagram"
    # Coordinate Geometry
    DISTANCE = "distance"
    MIDPOINT = "midpoint"
    SLOPE = "slope"
    LINE_EQUATION = "line_equation"


class AnswerFormat(str, Enum):
    """Format of the expected answer."""
    INTEGER = "integer"
    DECIMAL = "decimal"
    FRACTION = "fraction"
    EXPRESSION = "expression"


class DifficultyTier(str, Enum):
    """Difficulty tiers for adaptive learning."""
    NOVICE = "novice"          # 0.0 - 0.2
    BEGINNER = "beginner"      # 0.2 - 0.4
    INTERMEDIATE = "intermediate"  # 0.4 - 0.6
    ADVANCED = "advanced"      # 0.6 - 0.8
    EXPERT = "expert"          # 0.8 - 1.0


@dataclass
class ParameterRange:
    """Defines valid ranges for question parameters."""
    min_value: int
    max_value: int
    decimal_places: int = 0
    allow_negative: bool = False

    def is_valid(self, value: Union[int, float]) -> bool:
        """Check if a value falls within the valid range."""
        if not self.allow_negative and value < 0:
            return False
        return self.min_value <= value <= self.max_value


@dataclass
class DistractorRule:
    """Rule for generating a distractor (wrong answer option)."""
    name: str  # e.g., "sign_error", "off_by_one"
    description: str
    transform: str  # e.g., "negate", "add_1", "subtract_1"
    probability: float = 0.25  # Probability of using this rule


@dataclass
class QuestionTemplate:
    """Template defining how to generate a specific type of question."""
    template_id: str
    question_type: QuestionType
    operation: Optional[OperationType]
    parameter_ranges: Dict[str, ParameterRange]
    difficulty_base: float  # 0.0 to 1.0
    grade_level_min: int = 1
    grade_level_max: int = 12
    distractor_rules: List[DistractorRule] = field(default_factory=list)
    description: str = ""


@dataclass
class GeneratedQuestion:
    """A fully generated question with all components."""

    # Identifiers (required)
    question_id: str
    template_id: str
    question_type: QuestionType
    expression: str  # Human-readable expression, e.g., "15 + 8 = ?"
    correct_answer: Any
    answer_format: AnswerFormat

    # Optional fields with defaults
    operation: Optional[OperationType] = None
    expression_latex: Optional[str] = None  # LaTeX format for rendering

    # Multiple choice options (if applicable)
    distractors: List[Any] = field(default_factory=list)
    all_options: List[Any] = field(default_factory=list)  # Shuffled correct + distractors

    # Difficulty metrics
    difficulty_score: float = 0.5  # 0.0 to 1.0
    difficulty_tier: DifficultyTier = DifficultyTier.INTERMEDIATE

    # Parameters used for generation (for logging/analysis)
    parameters: Dict[str, Any] = field(default_factory=dict)

    # AI enhancement fields (populated later by AI layer)
    story_text: Optional[str] = None
    visual_prompt: Optional[str] = None
    visual_url: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "question_id": self.question_id,
            "question_type": self.question_type.value,
            "operation": self.operation.value if self.operation else None,
            "expression": self.expression,
            "expression_latex": self.expression_latex,
            "answer_format": self.answer_format.value,
            "difficulty_score": self.difficulty_score,
            "difficulty_tier": self.difficulty_tier.value,
            "options": self.all_options if self.all_options else None,
            "story_text": self.story_text,
            "visual_url": self.visual_url,
        }


class QuestionGenerator(ABC):
    """
    Abstract base class for all question generators.

    Each generator is responsible for:
    1. Generating mathematically correct expressions
    2. Computing the exact correct answer
    3. Generating pedagogically meaningful distractors
    4. Calculating objective difficulty scores
    """

    @property
    @abstractmethod
    def question_type(self) -> QuestionType:
        """Return the type of questions this generator produces."""
        pass

    @property
    @abstractmethod
    def supported_operations(self) -> List[OperationType]:
        """Return list of operations this generator supports."""
        pass

    @abstractmethod
    def generate(
        self,
        difficulty: float = 0.5,
        operation: Optional[OperationType] = None,
        grade_level: Optional[int] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> GeneratedQuestion:
        """
        Generate a question based on the given parameters.

        Args:
            difficulty: Target difficulty from 0.0 (easiest) to 1.0 (hardest)
            operation: Specific operation to use, or None for random
            grade_level: Target grade level (1-12), affects parameter ranges
            seed: Random seed for reproducibility
            **kwargs: Additional generator-specific parameters

        Returns:
            A fully constructed GeneratedQuestion instance
        """
        pass

    @abstractmethod
    def compute_answer(self, **parameters) -> Any:
        """
        Compute the correct answer given the question parameters.

        This must be a pure, deterministic function that guarantees
        mathematical correctness.
        """
        pass

    @abstractmethod
    def generate_distractors(
        self,
        correct_answer: Any,
        parameters: Dict[str, Any],
        count: int = 3
    ) -> List[Any]:
        """
        Generate plausible wrong answers based on common student errors.

        Args:
            correct_answer: The correct answer to generate alternatives for
            parameters: The parameters used to generate the question
            count: Number of distractors to generate

        Returns:
            List of plausible but incorrect answers
        """
        pass

    @abstractmethod
    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        """
        Calculate objective difficulty score based on question parameters.

        The difficulty calculation should consider:
        - Magnitude of numbers involved
        - Number of operations/steps
        - Type of operation (e.g., division is harder than addition)
        - Presence of negative numbers or fractions

        Returns:
            Float from 0.0 (easiest) to 1.0 (hardest)
        """
        pass

    def _generate_id(self) -> str:
        """Generate a unique question ID."""
        return str(uuid.uuid4())[:8]

    def _get_difficulty_tier(self, difficulty: float) -> DifficultyTier:
        """Map difficulty score to tier."""
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

    def _shuffle_options(
        self,
        correct_answer: Any,
        distractors: List[Any]
    ) -> List[Any]:
        """Shuffle correct answer with distractors."""
        import random
        options = [correct_answer] + distractors
        random.shuffle(options)
        return options


class DistractorStrategy:
    """
    Strategies for generating pedagogically meaningful wrong answers.

    Each strategy corresponds to a common student misconception or error pattern.
    """

    @staticmethod
    def sign_error(answer: Union[int, float]) -> Union[int, float]:
        """Student makes a sign error (negates the answer)."""
        return -answer

    @staticmethod
    def off_by_one(answer: Union[int, float], direction: int = 1) -> Union[int, float]:
        """Student makes an off-by-one error."""
        return answer + direction

    @staticmethod
    def magnitude_error(answer: Union[int, float], factor: int = 10) -> Union[int, float]:
        """Student makes a decimal place/magnitude error."""
        return answer * factor

    @staticmethod
    def operation_confusion(
        a: Union[int, float],
        b: Union[int, float],
        intended_op: str,
        confused_op: str
    ) -> Union[int, float]:
        """Student uses the wrong operation."""
        ops = {
            "add": lambda x, y: x + y,
            "sub": lambda x, y: x - y,
            "mul": lambda x, y: x * y,
            "div": lambda x, y: x / y if y != 0 else x,
        }
        return ops.get(confused_op, ops["add"])(a, b)

    @staticmethod
    def partial_solution(intermediate_values: List[Any]) -> Any:
        """Student stops at an intermediate step."""
        if intermediate_values:
            return intermediate_values[0]
        return None

    @staticmethod
    def random_close(answer: Union[int, float], range_pct: float = 0.2) -> Union[int, float]:
        """Generate a random value close to the correct answer."""
        import random
        delta = abs(answer * range_pct) if answer != 0 else 5
        offset = random.uniform(-delta, delta)
        result = answer + offset
        if isinstance(answer, int):
            result = int(round(result))
            if result == answer:
                result += random.choice([-1, 1])
        return result
