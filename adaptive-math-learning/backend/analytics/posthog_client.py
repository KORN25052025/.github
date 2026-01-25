"""
PostHog Analytics Client.

Provides integration with PostHog for:
- Event tracking
- User analytics
- A/B testing feature flags
- Session recording configuration
"""

from typing import Optional, Dict, Any
from datetime import datetime
import os


class PostHogClient:
    """
    PostHog analytics client for the adaptive math learning system.

    Tracks:
    - Question generation events
    - Answer submission events
    - Mastery progression
    - Session metrics
    - A/B test variants
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: str = "https://app.posthog.com"
    ):
        """
        Initialize PostHog client.

        Args:
            api_key: PostHog project API key (or from POSTHOG_API_KEY env)
            host: PostHog host URL
        """
        self.api_key = api_key or os.getenv("POSTHOG_API_KEY")
        self.host = host
        self._client = None

        if self.api_key:
            try:
                import posthog
                posthog.project_api_key = self.api_key
                posthog.host = self.host
                self._client = posthog
            except ImportError:
                pass

    def is_available(self) -> bool:
        """Check if PostHog is available."""
        return self._client is not None and bool(self.api_key)

    def identify(
        self,
        user_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Identify a user with properties.

        Args:
            user_id: Unique user identifier
            properties: User properties (grade_level, school, etc.)
        """
        if not self.is_available():
            return

        self._client.identify(user_id, properties or {})

    def capture(
        self,
        user_id: str,
        event: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Capture an event.

        Args:
            user_id: User who triggered the event
            event: Event name
            properties: Event properties
        """
        if not self.is_available():
            return

        props = properties or {}
        props["timestamp"] = datetime.utcnow().isoformat()

        self._client.capture(user_id, event, props)

    def track_question_generated(
        self,
        user_id: str,
        question_id: str,
        question_type: str,
        difficulty: float,
        has_story: bool = False,
        has_visual: bool = False
    ) -> None:
        """Track question generation event."""
        self.capture(user_id, "question_generated", {
            "question_id": question_id,
            "question_type": question_type,
            "difficulty": difficulty,
            "has_story": has_story,
            "has_visual": has_visual,
        })

    def track_answer_submitted(
        self,
        user_id: str,
        question_id: str,
        is_correct: bool,
        response_time_ms: int,
        mastery_before: float,
        mastery_after: float
    ) -> None:
        """Track answer submission event."""
        self.capture(user_id, "answer_submitted", {
            "question_id": question_id,
            "is_correct": is_correct,
            "response_time_ms": response_time_ms,
            "mastery_before": mastery_before,
            "mastery_after": mastery_after,
            "mastery_change": mastery_after - mastery_before,
        })

    def track_mastery_milestone(
        self,
        user_id: str,
        topic: str,
        milestone: str,
        mastery_score: float
    ) -> None:
        """Track mastery milestone achievement."""
        self.capture(user_id, "mastery_milestone", {
            "topic": topic,
            "milestone": milestone,
            "mastery_score": mastery_score,
        })

    def track_session_started(
        self,
        user_id: str,
        session_id: str,
        topic: Optional[str] = None
    ) -> None:
        """Track session start."""
        self.capture(user_id, "session_started", {
            "session_id": session_id,
            "topic": topic,
        })

    def track_session_ended(
        self,
        user_id: str,
        session_id: str,
        questions_attempted: int,
        questions_correct: int,
        duration_seconds: int
    ) -> None:
        """Track session end."""
        accuracy = questions_correct / questions_attempted if questions_attempted > 0 else 0
        self.capture(user_id, "session_ended", {
            "session_id": session_id,
            "questions_attempted": questions_attempted,
            "questions_correct": questions_correct,
            "accuracy": accuracy,
            "duration_seconds": duration_seconds,
        })

    def track_xp_earned(
        self,
        user_id: str,
        amount: int,
        source: str,
        total_xp: int
    ) -> None:
        """Track XP earning for gamification."""
        self.capture(user_id, "xp_earned", {
            "amount": amount,
            "source": source,
            "total_xp": total_xp,
        })

    def track_badge_earned(
        self,
        user_id: str,
        badge_id: str,
        badge_name: str
    ) -> None:
        """Track badge achievement."""
        self.capture(user_id, "badge_earned", {
            "badge_id": badge_id,
            "badge_name": badge_name,
        })

    def track_streak_milestone(
        self,
        user_id: str,
        streak_count: int,
        streak_type: str = "daily"
    ) -> None:
        """Track streak milestones."""
        self.capture(user_id, "streak_milestone", {
            "streak_count": streak_count,
            "streak_type": streak_type,
        })

    def get_feature_flag(
        self,
        user_id: str,
        flag_key: str,
        default: bool = False
    ) -> bool:
        """
        Get feature flag value for A/B testing.

        Args:
            user_id: User identifier
            flag_key: Feature flag key
            default: Default value if flag not found

        Returns:
            Feature flag value
        """
        if not self.is_available():
            return default

        try:
            return self._client.feature_enabled(flag_key, user_id) or default
        except Exception:
            return default

    def get_feature_flag_payload(
        self,
        user_id: str,
        flag_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get feature flag payload for complex A/B tests.

        Args:
            user_id: User identifier
            flag_key: Feature flag key

        Returns:
            Feature flag payload or None
        """
        if not self.is_available():
            return None

        try:
            return self._client.get_feature_flag_payload(flag_key, user_id)
        except Exception:
            return None

    def flush(self) -> None:
        """Flush any pending events."""
        if self.is_available():
            self._client.flush()

    def shutdown(self) -> None:
        """Shutdown the client."""
        if self.is_available():
            self._client.shutdown()


# Singleton instance
analytics_client = PostHogClient()
