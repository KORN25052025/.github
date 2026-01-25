"""
Fallback handling for AI service failures.

Provides graceful degradation when AI services are unavailable.
"""

from typing import Tuple, Optional, Any

from .llm.story_generator import StoryGenerator, GeneratedStory


class AIFallbackManager:
    """
    Manages graceful degradation when AI services fail.

    Ensures the learning experience continues even without AI enhancement.
    """

    def __init__(self, story_generator: Optional[StoryGenerator] = None):
        """Initialize fallback manager."""
        self.story_generator = story_generator or StoryGenerator()

    async def get_story_with_fallback(
        self,
        expression: str,
        answer: Any,
    ) -> Tuple[str, Optional[str]]:
        """
        Try AI story generation, fall back to expression-only.

        Args:
            expression: The mathematical expression
            answer: The correct answer

        Returns:
            Tuple of (display_text, visual_prompt or None)
        """
        try:
            story = await self.story_generator.generate(expression, answer)
            if story.success:
                return story.story_text, story.visual_prompt
        except Exception:
            pass

        # Fallback: return raw expression
        return f"Solve: {expression}", None

    def get_fallback_story(self, expression: str) -> str:
        """Get a simple fallback when AI fails."""
        return f"Solve this problem: {expression}"

    def get_fallback_explanation(
        self,
        expression: str,
        answer: Any,
        user_answer: Any,
        is_correct: bool
    ) -> str:
        """Generate basic explanation without AI."""
        if is_correct:
            return f"Correct! {expression.replace('?', str(answer))}"
        else:
            return f"The answer to {expression} is {answer}, not {user_answer}. Try again!"

    def get_simple_feedback(self, is_correct: bool, streak: int = 0) -> str:
        """Get simple feedback message."""
        if is_correct:
            if streak >= 5:
                return f"Excellent! You're on a {streak}-question streak!"
            elif streak >= 3:
                return "Great job! Keep it up!"
            else:
                return "Correct! Well done!"
        else:
            return "Not quite. Let's try another one!"


# Global fallback manager
fallback_manager = AIFallbackManager()
