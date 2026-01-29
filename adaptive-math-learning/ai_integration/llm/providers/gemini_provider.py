"""
Google Gemini API Provider.

Provides integration with Google's Gemini models for Turkish story generation.
Free tier available, making it the most accessible provider option.
"""

from typing import Optional
import os


class GeminiProvider:
    """
    Google Gemini provider for story generation.

    Supports Gemini 2.0 Flash and other Gemini models.
    Uses the Google Generative AI Python SDK.
    """

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL
    ):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google AI API key (or from GEMINI_API_KEY env)
            model: Model to use (default: gemini-2.0-flash)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self._client = None

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                pass

    def is_available(self) -> bool:
        """Check if provider is available."""
        return self._client is not None and bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        if not self.is_available():
            raise RuntimeError("Gemini provider not available - check GEMINI_API_KEY")

        # Build full prompt with system instruction
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": min(2.0, max(0.0, temperature)),
        }

        response = self._client.generate_content(
            full_prompt,
            generation_config=generation_config,
        )

        if response and response.text:
            return response.text

        return ""

    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Synchronous version of generate."""
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.generate(prompt, system_prompt, max_tokens, temperature)
            )
        finally:
            loop.close()
