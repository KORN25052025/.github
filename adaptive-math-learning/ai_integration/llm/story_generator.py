"""
Turkish Story Generation using Anthropic Claude API.

Transforms abstract mathematical expressions into engaging Turkish word problems
while preserving mathematical correctness.

Primary LLM: Claude 3.5 Sonnet (Anthropic)
Fallback: Template-based generation
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
import random


class StoryTheme(str, Enum):
    """Themes for Turkish story generation."""
    ALISVERIS = "alisveris"        # Shopping
    SPOR = "spor"                   # Sports
    YEMEK = "yemek"                 # Cooking/Food
    SEYAHAT = "seyahat"            # Travel
    DOGA = "doga"                   # Nature
    HAYVANLAR = "hayvanlar"        # Animals
    OYUNLAR = "oyunlar"            # Games
    OKUL = "okul"                   # School
    GUNLUK_HAYAT = "gunluk_hayat"  # Daily life


@dataclass
class StoryContext:
    """Context for story generation."""
    theme: StoryTheme
    character_name: Optional[str] = None
    grade_level: int = 5
    language: str = "tr"  # Turkish by default


@dataclass
class GeneratedStory:
    """Result of story generation."""
    story_text: str
    visual_prompt: Optional[str] = None
    theme_used: StoryTheme = StoryTheme.GUNLUK_HAYAT
    success: bool = True
    error_message: Optional[str] = None


# Turkish character name pools
TURKISH_NAMES = [
    "Ali", "Ayse", "Mehmet", "Fatma", "Ahmet", "Zeynep",
    "Mustafa", "Elif", "Emre", "Selin", "Burak", "Deniz",
    "Cem", "Ece", "Kerem", "Defne", "Mert", "Yagmur",
]


class StoryGenerator:
    """
    Transforms abstract math expressions into engaging Turkish word problems.

    Uses Anthropic Claude API for story generation with fallback to templates.
    """

    TURKISH_STORY_PROMPT = """Sen {grade_level}. sinif ogrencisi icin Turkce matematik problemi olusturuyorsun.

Bu matematiksel ifadeyi eglenceli bir hikaye problemine donustur:

IFADE: {expression}
DOGRU CEVAP: {answer}
TEMA: {theme}
KARAKTER: {character}

Gereksinimler:
1. Hikaye yasa uygun ve ilgi cekici olmali
2. Tum sayilar orijinal ifadeyle AYNI olmali
3. Soru acik ve cevaplanabilir olmali
4. {grade_level}. sinif icin uygun kelime hazinesi kullan
5. Hikaye 2-3 cumle ile sinirli olsun
6. Cevabi hikayede verme
7. Net bir soru ile bitir

Sadece hikaye problemini yaz, baska bir sey yazma."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "gemini"):
        """
        Initialize story generator.

        Args:
            api_key: API key for the selected provider
            provider: LLM provider to use ("gemini", "claude", or "openai")
        """
        self.api_key = api_key
        self.provider = provider
        self._client = None

        if api_key:
            try:
                if provider == "gemini":
                    from .providers.gemini_provider import GeminiProvider
                    self._client = GeminiProvider(api_key=api_key)
                elif provider == "claude":
                    from .providers.claude_provider import ClaudeProvider
                    self._client = ClaudeProvider(api_key=api_key)
                else:
                    from .providers.openai_provider import OpenAIProvider
                    self._client = OpenAIProvider(api_key=api_key)
            except ImportError:
                pass

    async def generate(
        self,
        expression: str,
        answer: any,
        context: Optional[StoryContext] = None
    ) -> GeneratedStory:
        """
        Generate a Turkish story problem from a mathematical expression.

        Args:
            expression: The math expression (e.g., "15 + 8 = ?")
            answer: The correct answer
            context: Optional story context

        Returns:
            GeneratedStory with the Turkish word problem
        """
        context = context or StoryContext(
            theme=random.choice(list(StoryTheme)),
            character_name=random.choice(TURKISH_NAMES),
            grade_level=5,
            language="tr",
        )

        # Try LLM if available
        if self._client and self._client.is_available():
            try:
                return await self._generate_with_llm(expression, answer, context)
            except Exception as e:
                # Fall back to templates
                return self._generate_from_template(expression, answer, context, str(e))

        # Use templates if no API key
        return self._generate_from_template(expression, answer, context)

    async def _generate_with_llm(
        self,
        expression: str,
        answer: any,
        context: StoryContext
    ) -> GeneratedStory:
        """Generate story using Claude or OpenAI API."""
        prompt = self.TURKISH_STORY_PROMPT.format(
            grade_level=context.grade_level,
            expression=expression,
            answer=answer,
            theme=context.theme.value,
            character=context.character_name or random.choice(TURKISH_NAMES),
        )

        system_prompt = "Sen K-12 ogrencileri icin Turkce matematik kelime problemleri olusturan bir egitim asistanisin."

        story_text = await self._client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=300,
            temperature=0.7,
        )

        # Generate visual prompt for DALL-E 3
        visual_prompt = self._generate_visual_prompt(context)

        return GeneratedStory(
            story_text=story_text.strip(),
            visual_prompt=visual_prompt,
            theme_used=context.theme,
            success=True,
        )

    def _generate_visual_prompt(self, context: StoryContext) -> str:
        """Generate DALL-E 3 visual prompt."""
        theme_descriptions = {
            StoryTheme.ALISVERIS: "a colorful Turkish market scene with fruits and vegetables",
            StoryTheme.SPOR: "children playing sports in a sunny Turkish school yard",
            StoryTheme.YEMEK: "a warm Turkish kitchen with traditional food",
            StoryTheme.SEYAHAT: "a scenic Turkish landscape with a bus or train",
            StoryTheme.DOGA: "beautiful Turkish nature with flowers and trees",
            StoryTheme.HAYVANLAR: "cute farm animals in a Turkish countryside",
            StoryTheme.OYUNLAR: "children playing traditional Turkish games",
            StoryTheme.OKUL: "a bright and cheerful Turkish classroom",
            StoryTheme.GUNLUK_HAYAT: "a typical day in a Turkish neighborhood",
        }

        theme_desc = theme_descriptions.get(context.theme, "a friendly educational scene")

        return f"A colorful, child-friendly educational illustration showing {theme_desc}. The style should be warm, inviting, and suitable for grade {context.grade_level} students. No text in the image."

    def _generate_from_template(
        self,
        expression: str,
        answer: any,
        context: StoryContext,
        error: Optional[str] = None
    ) -> GeneratedStory:
        """Generate Turkish story using templates (fallback)."""
        name = context.character_name or random.choice(TURKISH_NAMES)
        theme = context.theme

        # Parse expression to get operation and operands
        story = self._template_story(expression, name, theme)

        return GeneratedStory(
            story_text=story,
            visual_prompt=self._generate_visual_prompt(context),
            theme_used=theme,
            success=error is None,
            error_message=error,
        )

    def _template_story(self, expression: str, name: str, theme: StoryTheme) -> str:
        """Generate Turkish story from template based on operation."""
        # Simple parsing
        expr = expression.replace("= ?", "").strip()

        if "+" in expr:
            parts = expr.split("+")
            a, b = parts[0].strip(), parts[1].strip()
            return self._addition_story(a, b, name, theme)

        elif "-" in expr:
            parts = expr.split("-")
            a, b = parts[0].strip(), parts[1].strip()
            return self._subtraction_story(a, b, name, theme)

        elif "x" in expr.lower() or "*" in expr:
            parts = expr.replace("x", "*").replace("X", "*").split("*")
            a, b = parts[0].strip(), parts[1].strip()
            return self._multiplication_story(a, b, name, theme)

        elif "/" in expr or ":" in expr:
            parts = expr.replace(":", "/").split("/")
            a, b = parts[0].strip(), parts[1].strip()
            return self._division_story(a, b, name, theme)

        # Fallback
        return f"Bu problemi coz: {expression}"

    def _addition_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate Turkish addition story."""
        templates = {
            StoryTheme.ALISVERIS: f"{name} marketten {a} elma aldi, sonra {b} elma daha aldi. {name}'in toplam kac elmasi var?",
            StoryTheme.SPOR: f"{name} ilk yarisinda {a} sayi yapti, ikinci yarisinda {b} sayi daha yapti. Toplam kac sayi yapti?",
            StoryTheme.YEMEK: f"{name}'in {a} kurabiyesi vardi, {b} tane daha pisirdi. Simdi toplam kac kurabiyesi var?",
            StoryTheme.HAYVANLAR: f"Agacta {a} kus vardi. {b} kus daha geldi. Simdi agacta kac kus var?",
            StoryTheme.OYUNLAR: f"{name} birinci bolumde {a} puan topladi, ikinci bolumde {b} puan daha topladi. Toplam kac puan topladi?",
            StoryTheme.OKUL: f"{name} dun {a} sayfa okudu, bugun {b} sayfa daha okudu. Toplam kac sayfa okudu?",
            StoryTheme.GUNLUK_HAYAT: f"{name}'in {a} tane kalem var. Annesi {b} kalem daha aldi. Simdi toplam kac kalemi var?",
        }
        return templates.get(theme, templates[StoryTheme.GUNLUK_HAYAT])

    def _subtraction_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate Turkish subtraction story."""
        templates = {
            StoryTheme.ALISVERIS: f"{name}'in {a} lirasi vardi, {b} lira harcadi. Kac lirasi kaldi?",
            StoryTheme.SPOR: f"A takimi {a} gol atti, B takimi {b} gol atti. A takimi kac gol farkla kazandi?",
            StoryTheme.YEMEK: f"{name} {a} tane borek yapti, {b} tanesini arkadaslarina verdi. Kac borek kaldi?",
            StoryTheme.HAYVANLAR: f"Havuzda {a} balik vardi. {b} balik yuzup gitti. Havuzda kac balik kaldi?",
            StoryTheme.OYUNLAR: f"{name}'in oyunda {a} cani vardi, {b} can kaybetti. Kac cani kaldi?",
            StoryTheme.OKUL: f"{name}'in {a} cikartmasi vardi, arkadasina {b} tane verdi. Kac cikartmasi kaldi?",
            StoryTheme.GUNLUK_HAYAT: f"Kutuda {a} top vardi. {b} tanesi kayboldu. Kutuda kac top kaldi?",
        }
        return templates.get(theme, templates[StoryTheme.GUNLUK_HAYAT])

    def _multiplication_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate Turkish multiplication story."""
        templates = {
            StoryTheme.ALISVERIS: f"{name} {a} paket kalem aldi. Her pakette {b} kalem var. Toplam kac kalem aldi?",
            StoryTheme.SPOR: f"{a} takim var. Her takimda {b} oyuncu var. Toplam kac oyuncu var?",
            StoryTheme.YEMEK: f"{name} {a} tepsi kurabiye yapti. Her tepside {b} kurabiye var. Toplam kac kurabiye var?",
            StoryTheme.HAYVANLAR: f"{a} kus yuvasi var. Her yuvada {b} yumurta var. Toplam kac yumurta var?",
            StoryTheme.OYUNLAR: f"{name} {a} bolum tamamladi. Her bolum {b} yildiz veriyor. Toplam kac yildiz kazandi?",
            StoryTheme.OKUL: f"Sinifta {a} sira var. Her sirada {b} ogrenci oturuyor. Sinifta toplam kac ogrenci var?",
            StoryTheme.GUNLUK_HAYAT: f"{name}'in {a} arkadasi var. Her arkadasina {b} sekerleme verdi. Toplam kac sekerleme verdi?",
        }
        return templates.get(theme, templates[StoryTheme.GUNLUK_HAYAT])

    def _division_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate Turkish division story."""
        templates = {
            StoryTheme.ALISVERIS: f"{name}'in {a} sekeri var. {b} arkadasina esit paylastirmak istiyor. Her arkadasa kac seker duser?",
            StoryTheme.SPOR: f"Antrenor {a} formasi {b} takima esit dagitmak istiyor. Her takima kac forma duser?",
            StoryTheme.YEMEK: f"{name}'in {a} dilim pizzasi var. {b} kisiyle esit paylasacak. Her kisiye kac dilim duser?",
            StoryTheme.HAYVANLAR: f"Ciftci {a} havcucu {b} tavsana esit dagitacak. Her tavsana kac havuc duser?",
            StoryTheme.OYUNLAR: f"{name} {a} altin madeni {b} sandiga esit dagitiyor. Her sandikta kac altin olur?",
            StoryTheme.OKUL: f"Ogretmen {a} kitabi {b} ogrenciye esit dagitacak. Her ogrenciye kac kitap duser?",
            StoryTheme.GUNLUK_HAYAT: f"{name}'in {a} bilye var. {b} torbaya esit dagitmak istiyor. Her torbaya kac bilye koyar?",
        }
        return templates.get(theme, templates[StoryTheme.GUNLUK_HAYAT])


# Synchronous wrapper for non-async contexts
def generate_story_sync(
    expression: str,
    answer: any,
    api_key: Optional[str] = None,
    theme: Optional[StoryTheme] = None,
    provider: Optional[str] = None,
) -> GeneratedStory:
    """Synchronous Turkish story generation.

    Tries providers in order: Gemini (free) > Claude > OpenAI.
    Uses the first provider that has an API key available.
    """
    import asyncio
    import os

    # Auto-detect provider based on available API keys
    if not api_key and not provider:
        provider_keys = [
            ("gemini", "GEMINI_API_KEY"),
            ("claude", "ANTHROPIC_API_KEY"),
            ("openai", "OPENAI_API_KEY"),
        ]
        for prov, env_var in provider_keys:
            key = os.getenv(env_var)
            if key:
                api_key = key
                provider = prov
                break
        if not provider:
            provider = "gemini"
    elif not api_key:
        env_map = {
            "gemini": "GEMINI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
        }
        api_key = os.getenv(env_map.get(provider, ""), "")

    generator = StoryGenerator(api_key, provider=provider or "gemini")
    context = StoryContext(
        theme=theme or random.choice(list(StoryTheme)),
        character_name=random.choice(TURKISH_NAMES),
        language="tr",
    )

    # Run async function synchronously
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(generator.generate(expression, answer, context))
    finally:
        loop.close()
