"""Tests for new question generators (10 generators added in content expansion)."""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_engine.generators.exponents import ExponentsGenerator
from question_engine.generators.statistics import StatisticsGenerator
from question_engine.generators.number_theory import NumberTheoryGenerator
from question_engine.generators.systems_of_equations import SystemsOfEquationsGenerator
from question_engine.generators.inequalities import InequalitiesGenerator
from question_engine.generators.functions import FunctionsGenerator
from question_engine.generators.trigonometry import TrigonometryGenerator
from question_engine.generators.polynomials import PolynomialsGenerator
from question_engine.generators.sets_and_logic import SetsAndLogicGenerator
from question_engine.generators.coordinate_geometry import CoordinateGeometryGenerator


def _validate_question(question):
    """Validate that a generated question has all required fields."""
    assert question is not None, "Question should not be None"
    assert question.question_id is not None, "question_id should not be None"
    assert question.expression is not None, "expression should not be None"
    assert question.correct_answer is not None, "correct_answer should not be None"
    assert question.distractors is not None, "distractors should not be None"
    assert len(question.distractors) >= 2, "Should have at least 2 distractors"


class TestExponentsGenerator:
    """Tests for ExponentsGenerator."""

    def setup_method(self):
        self.generator = ExponentsGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestStatisticsGenerator:
    """Tests for StatisticsGenerator."""

    def setup_method(self):
        self.generator = StatisticsGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestNumberTheoryGenerator:
    """Tests for NumberTheoryGenerator."""

    def setup_method(self):
        self.generator = NumberTheoryGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestSystemsOfEquationsGenerator:
    """Tests for SystemsOfEquationsGenerator."""

    def setup_method(self):
        self.generator = SystemsOfEquationsGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestInequalitiesGenerator:
    """Tests for InequalitiesGenerator."""

    def setup_method(self):
        self.generator = InequalitiesGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestFunctionsGenerator:
    """Tests for FunctionsGenerator."""

    def setup_method(self):
        self.generator = FunctionsGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestTrigonometryGenerator:
    """Tests for TrigonometryGenerator."""

    def setup_method(self):
        self.generator = TrigonometryGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestPolynomialsGenerator:
    """Tests for PolynomialsGenerator."""

    def setup_method(self):
        self.generator = PolynomialsGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestSetsAndLogicGenerator:
    """Tests for SetsAndLogicGenerator."""

    def setup_method(self):
        self.generator = SetsAndLogicGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestCoordinateGeometryGenerator:
    """Tests for CoordinateGeometryGenerator."""

    def setup_method(self):
        self.generator = CoordinateGeometryGenerator()

    def test_generate_default(self):
        question = self.generator.generate(difficulty=0.3)
        _validate_question(question)

    def test_generate_medium_difficulty(self):
        question = self.generator.generate(difficulty=0.5)
        _validate_question(question)

    def test_generate_hard_difficulty(self):
        question = self.generator.generate(difficulty=0.8)
        _validate_question(question)


class TestNewServices:
    """Verify new service modules import correctly and singletons exist."""

    def test_motivation_service_imports(self):
        from backend.services.motivation_service import (
            math_history_service,
            math_puzzle_service,
            certificate_service,
            seasonal_content_service,
        )
        assert math_history_service is not None
        assert math_puzzle_service is not None
        assert certificate_service is not None
        assert seasonal_content_service is not None

    def test_motivation_daily_fact(self):
        from backend.services.motivation_service import math_history_service
        fact = math_history_service.get_daily_fact()
        assert fact is not None
        d = fact.to_dict()
        assert "id" in d
        assert "title" in d
        assert "content" in d

    def test_motivation_puzzle(self):
        from backend.services.motivation_service import math_puzzle_service
        puzzle = math_puzzle_service.get_daily_puzzle()
        assert puzzle is not None
        d = puzzle.to_dict()
        assert "id" in d
        assert "title" in d

    def test_enhanced_parent_teacher_imports(self):
        from backend.services.enhanced_parent_teacher_service import (
            homework_service,
            weekly_report_service,
            goal_setting_service,
            class_analytics_service,
        )
        assert homework_service is not None
        assert weekly_report_service is not None
        assert goal_setting_service is not None
        assert class_analytics_service is not None

    def test_accessibility_service_imports(self):
        from backend.services.accessibility_service import (
            tts_service,
            accessibility_settings_service,
            multi_language_service,
            special_education_service,
        )
        assert tts_service is not None
        assert accessibility_settings_service is not None
        assert multi_language_service is not None
        assert special_education_service is not None

    def test_accessibility_glossary(self):
        from backend.services.accessibility_service import multi_language_service
        entry = multi_language_service.get_math_glossary("addition", "tr")
        assert entry is not None
        assert entry["term"] == "Toplama"

    def test_tts_service(self):
        from backend.services.accessibility_service import tts_service
        result = tts_service.generate_speech("Merhaba", "tr")
        assert result is not None
        d = result.to_dict()
        assert "audio_url" in d
        assert d["language"] == "tr"

    def test_accessibility_settings(self):
        from backend.services.accessibility_service import accessibility_settings_service
        prefs = accessibility_settings_service.get_settings("test_user")
        assert prefs is not None
        assert prefs.user_id == "test_user"
        assert prefs.font_size == 16

    def test_celebration_feedback(self):
        from backend.services.accessibility_service import special_education_service
        msg = special_education_service.celebration_feedback()
        assert msg is not None
        assert isinstance(msg, str)
        assert len(msg) > 0
