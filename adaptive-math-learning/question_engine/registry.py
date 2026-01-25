"""
Question Generator Registry.

Provides a central registry for all question generators, allowing
dynamic discovery and instantiation of generators by type.
"""

from typing import Dict, Type, Optional, List
from .base import QuestionGenerator, QuestionType, OperationType, GeneratedQuestion


class GeneratorRegistry:
    """
    Central registry for question generators.

    Usage:
        registry = GeneratorRegistry()
        registry.register(ArithmeticGenerator)
        generator = registry.get(QuestionType.ARITHMETIC)
        question = generator.generate(difficulty=0.5)
    """

    _instance: Optional["GeneratorRegistry"] = None
    _generators: Dict[QuestionType, QuestionGenerator] = {}

    def __new__(cls) -> "GeneratorRegistry":
        """Singleton pattern for registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._generators = {}
        return cls._instance

    def register(self, generator_class: Type[QuestionGenerator]) -> None:
        """
        Register a generator class.

        Args:
            generator_class: The generator class to register
        """
        instance = generator_class()
        self._generators[instance.question_type] = instance

    def get(self, question_type: QuestionType) -> Optional[QuestionGenerator]:
        """
        Get a generator instance by question type.

        Args:
            question_type: The type of questions to generate

        Returns:
            The generator instance, or None if not found
        """
        return self._generators.get(question_type)

    def get_all(self) -> Dict[QuestionType, QuestionGenerator]:
        """Get all registered generators."""
        return self._generators.copy()

    def list_types(self) -> List[QuestionType]:
        """List all registered question types."""
        return list(self._generators.keys())

    def is_registered(self, question_type: QuestionType) -> bool:
        """Check if a generator is registered for the given type."""
        return question_type in self._generators

    def generate(
        self,
        question_type: QuestionType,
        difficulty: float = 0.5,
        operation: Optional[OperationType] = None,
        **kwargs
    ) -> GeneratedQuestion:
        """
        Generate a question using the appropriate generator.

        Args:
            question_type: Type of question to generate
            difficulty: Target difficulty (0.0 to 1.0)
            operation: Specific operation (optional)
            **kwargs: Additional parameters

        Returns:
            Generated question

        Raises:
            ValueError: If no generator is registered for the type
        """
        generator = self.get(question_type)
        if generator is None:
            raise ValueError(f"No generator registered for type: {question_type}")
        return generator.generate(difficulty=difficulty, operation=operation, **kwargs)


# Global registry instance
registry = GeneratorRegistry()


def register_generator(generator_class: Type[QuestionGenerator]) -> Type[QuestionGenerator]:
    """
    Decorator to register a generator class.

    Usage:
        @register_generator
        class MyGenerator(QuestionGenerator):
            ...
    """
    registry.register(generator_class)
    return generator_class
