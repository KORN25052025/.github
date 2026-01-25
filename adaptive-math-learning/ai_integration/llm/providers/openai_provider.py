"""
OpenAI LLM Provider.

Provides integration with OpenAI's GPT models for story generation.
"""

from typing import Optional
import os


class OpenAIProvider:
    """
    OpenAI GPT provider for story generation.

    Supports GPT-3.5-turbo and GPT-4 models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo"
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (or from OPENAI_API_KEY env)
            model: Model to use (default: gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
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
            raise RuntimeError("OpenAI provider not available")

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content

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
