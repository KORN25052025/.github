"""
A/B Testing Manager using PostHog Feature Flags.

Manages experiments for:
- Story vs No-Story presentation
- Visual vs No-Visual questions
- Difficulty progression strategies
- Gamification features
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
from .posthog_client import analytics_client


class ABTestVariant(str, Enum):
    """Standard A/B test variants."""
    CONTROL = "control"
    TREATMENT = "treatment"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"
    VARIANT_C = "variant_c"


@dataclass
class ABTest:
    """A/B test configuration."""
    key: str
    name: str
    description: str
    variants: List[ABTestVariant]
    default_variant: ABTestVariant = ABTestVariant.CONTROL


class ABTestManager:
    """
    Manager for A/B testing experiments.

    Pre-defined experiments:
    - story_presentation: Test story vs no-story question presentation
    - visual_generation: Test visual vs no-visual questions
    - difficulty_algorithm: Test BKT vs other algorithms
    - gamification_level: Test different gamification intensities
    - feedback_style: Test different feedback styles
    """

    # Pre-defined experiments
    EXPERIMENTS = {
        "story_presentation": ABTest(
            key="story_presentation",
            name="Story Presentation Test",
            description="Compare learning outcomes between story and abstract problems",
            variants=[ABTestVariant.CONTROL, ABTestVariant.TREATMENT],
        ),
        "visual_generation": ABTest(
            key="visual_generation",
            name="Visual Generation Test",
            description="Test impact of AI-generated visuals on engagement",
            variants=[ABTestVariant.CONTROL, ABTestVariant.TREATMENT],
        ),
        "difficulty_progression": ABTest(
            key="difficulty_progression",
            name="Difficulty Progression Test",
            description="Compare different difficulty progression strategies",
            variants=[ABTestVariant.VARIANT_A, ABTestVariant.VARIANT_B, ABTestVariant.VARIANT_C],
            default_variant=ABTestVariant.VARIANT_A,
        ),
        "gamification_level": ABTest(
            key="gamification_level",
            name="Gamification Level Test",
            description="Test different levels of gamification features",
            variants=[ABTestVariant.CONTROL, ABTestVariant.VARIANT_A, ABTestVariant.VARIANT_B],
        ),
        "feedback_style": ABTest(
            key="feedback_style",
            name="Feedback Style Test",
            description="Compare different feedback presentation styles",
            variants=[ABTestVariant.VARIANT_A, ABTestVariant.VARIANT_B],
            default_variant=ABTestVariant.VARIANT_A,
        ),
    }

    def __init__(self, client=None):
        """
        Initialize A/B test manager.

        Args:
            client: PostHog client (uses singleton if not provided)
        """
        self.client = client or analytics_client

    def get_variant(
        self,
        user_id: str,
        experiment_key: str
    ) -> ABTestVariant:
        """
        Get user's variant for an experiment.

        Args:
            user_id: User identifier
            experiment_key: Experiment key

        Returns:
            User's assigned variant
        """
        experiment = self.EXPERIMENTS.get(experiment_key)
        if not experiment:
            return ABTestVariant.CONTROL

        if not self.client.is_available():
            return experiment.default_variant

        # Get variant from PostHog feature flag
        flag_value = self.client.get_feature_flag_payload(user_id, experiment_key)

        if flag_value and isinstance(flag_value, dict):
            variant_str = flag_value.get("variant", experiment.default_variant.value)
            try:
                return ABTestVariant(variant_str)
            except ValueError:
                return experiment.default_variant

        # Fall back to boolean flag
        is_enabled = self.client.get_feature_flag(user_id, experiment_key)
        return ABTestVariant.TREATMENT if is_enabled else ABTestVariant.CONTROL

    def should_show_story(self, user_id: str) -> bool:
        """Check if user should see story problems."""
        variant = self.get_variant(user_id, "story_presentation")
        return variant == ABTestVariant.TREATMENT

    def should_generate_visual(self, user_id: str) -> bool:
        """Check if user should see AI-generated visuals."""
        variant = self.get_variant(user_id, "visual_generation")
        return variant == ABTestVariant.TREATMENT

    def get_difficulty_strategy(self, user_id: str) -> str:
        """
        Get difficulty progression strategy for user.

        Returns:
            Strategy name: "conservative", "moderate", or "aggressive"
        """
        variant = self.get_variant(user_id, "difficulty_progression")
        strategies = {
            ABTestVariant.VARIANT_A: "conservative",
            ABTestVariant.VARIANT_B: "moderate",
            ABTestVariant.VARIANT_C: "aggressive",
        }
        return strategies.get(variant, "moderate")

    def get_gamification_config(self, user_id: str) -> Dict[str, Any]:
        """
        Get gamification configuration for user.

        Returns:
            Gamification settings based on variant
        """
        variant = self.get_variant(user_id, "gamification_level")

        configs = {
            ABTestVariant.CONTROL: {
                "xp_enabled": False,
                "badges_enabled": False,
                "streaks_enabled": True,
                "leaderboard_enabled": False,
            },
            ABTestVariant.VARIANT_A: {
                "xp_enabled": True,
                "badges_enabled": True,
                "streaks_enabled": True,
                "leaderboard_enabled": False,
            },
            ABTestVariant.VARIANT_B: {
                "xp_enabled": True,
                "badges_enabled": True,
                "streaks_enabled": True,
                "leaderboard_enabled": True,
            },
        }
        return configs.get(variant, configs[ABTestVariant.CONTROL])

    def get_feedback_style(self, user_id: str) -> str:
        """
        Get feedback style for user.

        Returns:
            Feedback style: "encouraging" or "informative"
        """
        variant = self.get_variant(user_id, "feedback_style")
        styles = {
            ABTestVariant.VARIANT_A: "encouraging",
            ABTestVariant.VARIANT_B: "informative",
        }
        return styles.get(variant, "encouraging")

    def track_experiment_exposure(
        self,
        user_id: str,
        experiment_key: str
    ) -> None:
        """
        Track that user was exposed to an experiment.

        Args:
            user_id: User identifier
            experiment_key: Experiment key
        """
        variant = self.get_variant(user_id, experiment_key)
        self.client.capture(user_id, "$experiment_started", {
            "experiment": experiment_key,
            "variant": variant.value,
        })

    def get_all_variants(self, user_id: str) -> Dict[str, str]:
        """
        Get all experiment variants for a user.

        Args:
            user_id: User identifier

        Returns:
            Dict mapping experiment keys to variant values
        """
        return {
            key: self.get_variant(user_id, key).value
            for key in self.EXPERIMENTS.keys()
        }


# Singleton instance
ab_test_manager = ABTestManager()
