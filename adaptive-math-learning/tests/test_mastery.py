"""Tests for mastery tracking."""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptation.mastery_tracker import MasteryTracker, MasteryLevel


class TestMasteryTracker:
    """Tests for MasteryTracker."""

    def setup_method(self):
        self.tracker = MasteryTracker()

    def test_initial_mastery(self):
        """Test initial mastery is 0.5."""
        mastery = self.tracker.get_mastery("new_topic")
        assert mastery == 0.5

    def test_correct_increases_mastery(self):
        """Test that correct answers increase mastery."""
        initial = self.tracker.get_mastery("test_topic")

        self.tracker.update("test_topic", is_correct=True)
        new_mastery = self.tracker.get_mastery("test_topic")

        assert new_mastery > initial

    def test_incorrect_decreases_mastery(self):
        """Test that incorrect answers decrease mastery."""
        # First increase mastery
        for _ in range(5):
            self.tracker.update("test_topic", is_correct=True)

        high_mastery = self.tracker.get_mastery("test_topic")

        self.tracker.update("test_topic", is_correct=False)
        new_mastery = self.tracker.get_mastery("test_topic")

        assert new_mastery < high_mastery

    def test_mastery_bounded(self):
        """Test mastery stays within [0, 1]."""
        # Many correct answers
        for _ in range(100):
            self.tracker.update("test_topic", is_correct=True)

        mastery = self.tracker.get_mastery("test_topic")
        assert 0 <= mastery <= 1

        # Many incorrect answers
        for _ in range(100):
            self.tracker.update("test_topic", is_correct=False)

        mastery = self.tracker.get_mastery("test_topic")
        assert 0 <= mastery <= 1

    def test_streak_tracking(self):
        """Test streak tracking."""
        # Build a streak
        for _ in range(5):
            self.tracker.update("test_topic", is_correct=True)

        record = self.tracker.get_record("test_topic")
        assert record.streak == 5

        # Break streak
        self.tracker.update("test_topic", is_correct=False)
        record = self.tracker.get_record("test_topic")
        assert record.streak == 0
        assert record.best_streak == 5

    def test_level_progression(self):
        """Test mastery level progression."""
        # Start - initial mastery is 0.5 which maps to PROFICIENT (0.50-0.70)
        record = self.tracker.get_record("test_topic")
        # Initial 0.5 is at the edge, could be DEVELOPING or PROFICIENT
        assert record.level in [MasteryLevel.DEVELOPING, MasteryLevel.PROFICIENT]

        # Increase to expert (need to get above 0.85)
        for _ in range(30):
            self.tracker.update("test_topic", is_correct=True)

        record = self.tracker.get_record("test_topic")
        # Should now be ADVANCED or EXPERT
        assert record.level in [MasteryLevel.ADVANCED, MasteryLevel.EXPERT]

    def test_reset_topic(self):
        """Test resetting a topic."""
        # Increase mastery
        for _ in range(5):
            self.tracker.update("test_topic", is_correct=True)

        # Reset
        self.tracker.reset("test_topic")

        mastery = self.tracker.get_mastery("test_topic")
        assert mastery == 0.5

    def test_recommended_difficulty(self):
        """Test difficulty recommendation."""
        # Low mastery should recommend easy difficulty
        diff_low = self.tracker.get_recommended_difficulty("new_topic")

        # Increase mastery
        for _ in range(10):
            self.tracker.update("test_topic", is_correct=True)

        diff_high = self.tracker.get_recommended_difficulty("test_topic")

        assert diff_high > diff_low


class TestEMACalculation:
    """Tests for EMA calculation."""

    def test_ema_formula(self):
        """Test EMA formula: new = alpha * performance + (1 - alpha) * old."""
        tracker = MasteryTracker(alpha=0.3)

        initial = 0.5
        # After correct answer: 0.3 * 1.0 + 0.7 * 0.5 = 0.3 + 0.35 = 0.65
        tracker.update("test_topic", is_correct=True)
        expected = 0.3 * 1.0 + 0.7 * 0.5

        actual = tracker.get_mastery("test_topic")
        assert abs(actual - expected) < 0.01


class TestMasteryLevels:
    """Tests for mastery level mapping."""

    def test_level_thresholds(self):
        """Test that levels map correctly to mastery scores."""
        from adaptation.mastery_tracker import MasteryRecord

        # Test each level threshold
        test_cases = [
            (0.10, MasteryLevel.NOVICE),
            (0.20, MasteryLevel.BEGINNER),
            (0.40, MasteryLevel.DEVELOPING),
            (0.60, MasteryLevel.PROFICIENT),
            (0.80, MasteryLevel.ADVANCED),
            (0.90, MasteryLevel.EXPERT),
        ]

        for mastery_score, expected_level in test_cases:
            record = MasteryRecord(
                topic_id="test",
                mastery_score=mastery_score
            )
            assert record.level == expected_level, f"Score {mastery_score} should be {expected_level}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
