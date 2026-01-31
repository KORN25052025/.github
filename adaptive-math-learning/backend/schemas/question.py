"""
Pydantic schemas for questions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum
from datetime import datetime


class QuestionTypeEnum(str, Enum):
    ARITHMETIC = "arithmetic"
    FRACTIONS = "fractions"
    PERCENTAGES = "percentages"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    RATIOS = "ratios"


class OperationEnum(str, Enum):
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


class AnswerFormatEnum(str, Enum):
    INTEGER = "integer"
    DECIMAL = "decimal"
    FRACTION = "fraction"
    EXPRESSION = "expression"


class DifficultyTierEnum(str, Enum):
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class QuestionRequest(BaseModel):
    """Request for generating a new question."""
    topic_id: Optional[int] = None
    topic_slug: Optional[str] = None
    subtopic_id: Optional[int] = None
    difficulty: Optional[float] = Field(None, ge=0.0, le=1.0)
    question_type: Optional[QuestionTypeEnum] = None
    operation: Optional[OperationEnum] = None
    with_story: bool = False
    multiple_choice: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "topic_slug": "arithmetic",
                "difficulty": 0.5,
                "operation": "addition",
                "multiple_choice": True
            }
        }


class QuestionResponse(BaseModel):
    """Response containing a generated question."""
    question_id: str
    session_id: Optional[int] = None
    question_type: str
    operation: Optional[str] = None

    # Display content
    expression: str
    expression_latex: Optional[str] = None
    story_text: Optional[str] = None
    visual_url: Optional[str] = None

    # Answer format
    answer_format: str
    multiple_choice: bool = True
    options: Optional[List[Any]] = None

    # Metadata
    difficulty_score: float
    difficulty_tier: str
    topic_name: Optional[str] = None
    subtopic_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "question_id": "abc123",
                "question_type": "arithmetic",
                "operation": "addition",
                "expression": "15 + 8 = ?",
                "answer_format": "integer",
                "multiple_choice": True,
                "options": [23, 22, 24, 28],
                "difficulty_score": 0.35,
                "difficulty_tier": "beginner"
            }
        }


class QuestionListResponse(BaseModel):
    """Response containing multiple questions."""
    questions: List[QuestionResponse]
    total: int
