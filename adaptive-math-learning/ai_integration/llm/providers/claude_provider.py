"""
Anthropic Claude API Provider.

Provides integration with Anthropic's Claude models for Turkish story generation.
This is the primary LLM provider for the adaptive math learning system.
"""

from typing import Optional
import os


class ClaudeProvider:
    """
    Anthropic Claude provider for Turkish story generation.

    Supports Claude 3.5 Sonnet and other Claude models.
    Uses the Anthropic Python SDK.
    """

    # Default model as per specifications
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL
    ):
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key (or from ANTHROPIC_API_KEY env)
            model: Model to use (default: claude-3-5-sonnet-20241022)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None

        if self.api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
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
            raise RuntimeError("Claude provider not available - check ANTHROPIC_API_KEY")

        # Build message request
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Add system prompt if provided
        if system_prompt:
            kwargs["system"] = system_prompt

        # Claude API uses temperature 0-1
        if temperature is not None:
            kwargs["temperature"] = min(1.0, max(0.0, temperature))

        # Create message (synchronous call)
        message = self._client.messages.create(**kwargs)

        # Extract text from response
        if message.content and len(message.content) > 0:
            return message.content[0].text

        return ""

    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Synchronous version of generate.

        Claude's Python SDK is synchronous by default,
        so this directly calls the API.
        """
        if not self.is_available():
            raise RuntimeError("Claude provider not available - check ANTHROPIC_API_KEY")

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        if temperature is not None:
            kwargs["temperature"] = min(1.0, max(0.0, temperature))

        message = self._client.messages.create(**kwargs)

        if message.content and len(message.content) > 0:
            return message.content[0].text

        return ""

    async def generate_turkish_story(
        self,
        expression: str,
        answer: any,
        grade_level: int = 5,
        theme: str = "gunluk_hayat"
    ) -> dict:
        """
        Generate a Turkish math word problem.

        Args:
            expression: Mathematical expression (e.g., "15 + 8 = ?")
            answer: Correct answer
            grade_level: Target grade level (1-12)
            theme: Story theme in Turkish

        Returns:
            dict with 'story_text' and 'visual_prompt'
        """
        system_prompt = """Sen K-12 öğrencileri için Türkçe matematik kelime problemleri oluşturan bir eğitim asistanısın.

Kurallar:
1. Hikaye yaşa uygun ve ilgi çekici olmalı
2. Tüm sayılar orijinal ifadeyle AYNI olmalı
3. Soru açık ve cevaplanabilir olmalı
4. Sınıf seviyesine uygun kelime hazinesi kullan
5. Hikaye 2-3 cümle ile sınırlı olsun
6. Cevabı hikayede verme
7. Net bir soru ile bitir"""

        prompt = f"""Aşağıdaki matematiksel ifadeyi eğlenceli bir Türkçe kelime problemine dönüştür:

MATEMATİKSEL İFADE: {expression}
DOĞRU CEVAP: {answer}
SINIF SEVİYESİ: {grade_level}. sınıf
TEMA: {theme}

Sadece hikaye problemini yaz, başka bir şey yazma."""

        try:
            story_text = await self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=300,
                temperature=0.7
            )

            # Generate visual prompt for DALL-E
            visual_prompt = f"A colorful, child-friendly educational illustration for a Turkish math problem about {theme}, suitable for grade {grade_level} students"

            return {
                "story_text": story_text.strip(),
                "visual_prompt": visual_prompt,
                "success": True,
            }
        except Exception as e:
            return {
                "story_text": "",
                "visual_prompt": "",
                "success": False,
                "error": str(e),
            }

    def generate_turkish_story_sync(
        self,
        expression: str,
        answer: any,
        grade_level: int = 5,
        theme: str = "gunluk_hayat"
    ) -> dict:
        """Synchronous version of generate_turkish_story."""
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.generate_turkish_story(expression, answer, grade_level, theme)
            )
        finally:
            loop.close()
