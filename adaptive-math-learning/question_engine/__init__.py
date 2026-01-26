"""
Question Engine - Deterministic mathematical question generation.

This package provides mathematically correct question generators for various
math topics with adaptive difficulty and pedagogical distractors.
"""

# Import all generators to trigger registration via @register_generator decorator
from .generators import arithmetic  # noqa: F401
from .generators import fractions  # noqa: F401
from .generators import percentages  # noqa: F401
from .generators import algebra  # noqa: F401
from .generators import geometry  # noqa: F401
from .generators import ratios  # noqa: F401
from .generators import exponents  # noqa: F401
from .generators import statistics  # noqa: F401
from .generators import number_theory  # noqa: F401
from .generators import systems_of_equations  # noqa: F401
from .generators import inequalities  # noqa: F401
from .generators import functions  # noqa: F401
from .generators import trigonometry  # noqa: F401
from .generators import polynomials  # noqa: F401
from .generators import sets_and_logic  # noqa: F401
from .generators import coordinate_geometry  # noqa: F401

from .registry import registry, GeneratorRegistry
from .base import (
    QuestionType,
    OperationType,
    AnswerFormat,
    DifficultyTier,
    GeneratedQuestion,
    QuestionGenerator,
)
