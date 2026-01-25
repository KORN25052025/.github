"""
DALL-E 3 Image Generation for Educational Illustrations.

Generates child-friendly educational images for math word problems
using OpenAI's DALL-E 3 API.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum
import os


class ImageSize(str, Enum):
    """Supported DALL-E 3 image sizes."""
    SQUARE = "1024x1024"
    LANDSCAPE = "1792x1024"
    PORTRAIT = "1024x1792"


class ImageQuality(str, Enum):
    """DALL-E 3 image quality levels."""
    STANDARD = "standard"
    HD = "hd"


@dataclass
class GeneratedImage:
    """Result of image generation."""
    url: str
    prompt_used: str
    revised_prompt: Optional[str] = None
    size: ImageSize = ImageSize.SQUARE
    success: bool = True
    error_message: Optional[str] = None


class ImageGenerator:
    """
    DALL-E 3 image generator for educational illustrations.

    Generates child-friendly, colorful images suitable for K-12 math education.
    All images are optimized for the Turkish educational context.
    """

    # Base style instructions for child-friendly educational images
    BASE_STYLE = """
    Style: Colorful, child-friendly, educational illustration.
    Art style: Warm, inviting, cartoon-like but not childish.
    Colors: Bright, cheerful palette suitable for children.
    Safety: No text, no numbers, no scary elements.
    Cultural context: Turkish/Mediterranean setting when applicable.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_size: ImageSize = ImageSize.SQUARE,
        default_quality: ImageQuality = ImageQuality.STANDARD
    ):
        """
        Initialize DALL-E 3 image generator.

        Args:
            api_key: OpenAI API key (or from OPENAI_API_KEY env)
            default_size: Default image size
            default_quality: Default image quality
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.default_size = default_size
        self.default_quality = default_quality
        self._client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                pass

    def is_available(self) -> bool:
        """Check if DALL-E 3 is available."""
        return self._client is not None and bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        size: Optional[ImageSize] = None,
        quality: Optional[ImageQuality] = None,
        grade_level: int = 5
    ) -> GeneratedImage:
        """
        Generate an educational illustration using DALL-E 3.

        Args:
            prompt: Base prompt describing the desired image
            size: Image size (defaults to square)
            quality: Image quality level
            grade_level: Target grade level (affects style)

        Returns:
            GeneratedImage with URL and metadata
        """
        if not self.is_available():
            return GeneratedImage(
                url="",
                prompt_used=prompt,
                success=False,
                error_message="DALL-E 3 not available - check OPENAI_API_KEY",
            )

        size = size or self.default_size
        quality = quality or self.default_quality

        # Enhance prompt for educational context
        enhanced_prompt = self._enhance_prompt(prompt, grade_level)

        try:
            response = self._client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=size.value,
                quality=quality.value,
                n=1,
            )

            return GeneratedImage(
                url=response.data[0].url,
                prompt_used=enhanced_prompt,
                revised_prompt=response.data[0].revised_prompt,
                size=size,
                success=True,
            )
        except Exception as e:
            return GeneratedImage(
                url="",
                prompt_used=enhanced_prompt,
                success=False,
                error_message=str(e),
            )

    def _enhance_prompt(self, prompt: str, grade_level: int) -> str:
        """Enhance prompt with educational and safety guidelines."""
        age_appropriate = "young children" if grade_level <= 3 else (
            "elementary school students" if grade_level <= 6 else
            "middle school students" if grade_level <= 8 else
            "high school students"
        )

        return f"""Create a colorful, educational illustration for {age_appropriate}:

{prompt}

{self.BASE_STYLE}

Important:
- NO text or numbers in the image
- Safe for children
- Encouraging and positive atmosphere
- Clear, simple composition
"""

    def generate_for_theme(
        self,
        theme: str,
        grade_level: int = 5,
        additional_context: Optional[str] = None
    ) -> GeneratedImage:
        """
        Generate image for a specific story theme.

        Args:
            theme: Theme name (e.g., "alisveris", "okul", "hayvanlar")
            grade_level: Target grade level
            additional_context: Extra context for the image

        Returns:
            GeneratedImage
        """
        theme_prompts = {
            "alisveris": "A colorful Turkish market scene with fruits, vegetables, and friendly vendors. Mediterranean atmosphere with bazaar elements.",
            "spor": "Children playing sports in a sunny school yard. Soccer, basketball, or running activities. Joyful and active.",
            "yemek": "A warm, inviting Turkish kitchen scene. Traditional cooking with pots, pans, and delicious food being prepared.",
            "seyahat": "A scenic Turkish landscape with a cheerful bus or train. Mountains, sea, or countryside in the background.",
            "doga": "Beautiful Turkish nature scene with flowers, trees, birds, and butterflies. Peaceful garden or park setting.",
            "hayvanlar": "Cute farm animals in a Turkish countryside. Chickens, cows, sheep, or rabbits in a barn setting.",
            "oyunlar": "Children playing traditional Turkish games outdoors. Jump rope, marbles, or group activities.",
            "okul": "A bright, cheerful Turkish classroom. Desks, chalkboard, books, and happy learning atmosphere.",
            "gunluk_hayat": "A typical sunny day in a Turkish neighborhood. Houses, gardens, and friendly community scene.",
        }

        base_prompt = theme_prompts.get(theme, theme_prompts["gunluk_hayat"])

        if additional_context:
            base_prompt = f"{base_prompt} Context: {additional_context}"

        return self.generate_sync(base_prompt, grade_level=grade_level)

    def generate_sync(
        self,
        prompt: str,
        size: Optional[ImageSize] = None,
        quality: Optional[ImageQuality] = None,
        grade_level: int = 5
    ) -> GeneratedImage:
        """Synchronous version of generate."""
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.generate(prompt, size, quality, grade_level)
            )
        finally:
            loop.close()


# Convenience function
def generate_image_sync(
    prompt: str,
    api_key: Optional[str] = None,
    grade_level: int = 5
) -> GeneratedImage:
    """
    Generate an educational image synchronously.

    Args:
        prompt: Image description
        api_key: OpenAI API key (optional, uses env var)
        grade_level: Target grade level

    Returns:
        GeneratedImage with URL
    """
    generator = ImageGenerator(api_key=api_key)
    return generator.generate_sync(prompt, grade_level=grade_level)
