"""
TYT Yeni Nesil Soru Üretici (Turkish New-Generation Question Generator).

Transforms abstract mathematical expressions into TYT-style "yeni nesil"
(new generation) questions — real-life scenario-based, analytical thinking
problems modeled after ÖSYM university entrance exam format.

Primary LLM: Gemini (Google)
Fallback: Template-based generation
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
import random


class StoryTheme(str, Enum):
    """Themes for TYT yeni nesil story generation."""
    ALISVERIS = "alisveris"        # Shopping / Economy
    SPOR = "spor"                   # Sports / Statistics
    YEMEK = "yemek"                 # Cooking / Ratios
    SEYAHAT = "seyahat"            # Travel / Distance-Time
    DOGA = "doga"                   # Nature / Environment
    HAYVANLAR = "hayvanlar"        # Animals / Biology data
    OYUNLAR = "oyunlar"            # Games / Probability
    OKUL = "okul"                   # School / Education stats
    GUNLUK_HAYAT = "gunluk_hayat"  # Daily life / Practical math
    EKONOMI = "ekonomi"            # Finance / Percentages
    BILIM = "bilim"                # Science / Measurement
    TEKNOLOJI = "teknoloji"        # Technology / Data


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

    TURKISH_STORY_PROMPT = """Sen ÖSYM tarzında TYT "yeni nesil" matematik sorusu hazırlayan bir eğitim uzmanısın.

Aşağıdaki matematiksel ifadeyi gerçek hayat senaryosuna dayalı, analitik düşünme gerektiren bir TYT yeni nesil sorusuna dönüştür.

İFADE: {expression}
DOĞRU CEVAP: {answer}
TEMA: {theme}
KARAKTER: {character}

TYT YENİ NESİL SORU KURALLARI:
1. Gerçek hayattan bir senaryo kur (alışveriş, iş, bilim, spor, seyahat, üretim, veri analizi vb.)
2. Soruyu bir bağlam/durum içinde sun — düz "hesapla" deme
3. Öğrencinin bilgiyi yorumlaması, analiz etmesi veya çıkarım yapması gereksin
4. Mümkünse tablo, liste veya karşılaştırma formatı kullan (metin içinde)
5. Tüm sayısal değerler orijinal ifadeyle BİREBİR AYNI olmalı — sayıları değiştirme
6. Cevabı kesinlikle verme veya ima etme
7. Soru net ve tek doğru cevaplı olmalı
8. 3-5 cümle uzunluğunda, akıcı Türkçe ile yaz
9. Soru "Buna göre..." veya "Bu durumda..." gibi analitik bir soru cümlesiyle bitsin
10. {grade_level}. sınıf seviyesine uygun olsun

ÖRNEK FORMAT:
"{character}, hafta sonu markete gidip her biri 3 TL olan 5 paket süt almıştır. Kasada indirim kuponu kullanarak toplam tutardan 2 TL indirim almıştır. Buna göre, {character}'in kasada ödediği tutar kaç TL'dir?"

Sadece soruyu yaz, başka açıklama ekleme."""

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

        system_prompt = "Sen ÖSYM tarzında TYT yeni nesil matematik soruları hazırlayan deneyimli bir Türk matematik eğitimcisisin. Soruların gerçek hayat senaryolarına dayalı, analitik düşünme gerektiren ve çok adımlı çözüm içeren sorular olmalı."

        story_text = await self._client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=500,
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
            StoryTheme.ALISVERIS: "a modern Turkish shopping scene with price tags and receipts",
            StoryTheme.SPOR: "a Turkish sports stadium with scoreboards and statistics",
            StoryTheme.YEMEK: "a Turkish kitchen with recipe cards and measuring tools",
            StoryTheme.SEYAHAT: "a Turkish travel scene with maps, distances, and timetables",
            StoryTheme.DOGA: "Turkish nature scene with scientific measurement tools",
            StoryTheme.HAYVANLAR: "animals in a Turkish setting with data charts",
            StoryTheme.OYUNLAR: "a game board with scores and probability elements",
            StoryTheme.OKUL: "a Turkish classroom with graphs and charts on the board",
            StoryTheme.GUNLUK_HAYAT: "a typical Turkish daily scene with practical math elements",
            StoryTheme.EKONOMI: "a Turkish bank or finance scene with charts and percentages",
            StoryTheme.BILIM: "a Turkish science lab with measurement instruments",
            StoryTheme.TEKNOLOJI: "a modern Turkish tech workspace with data on screens",
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

        elif "×" in expr or "x" in expr.lower() or "*" in expr:
            parts = expr.replace("×", "*").replace("x", "*").replace("X", "*").split("*")
            a, b = parts[0].strip(), parts[1].strip()
            return self._multiplication_story(a, b, name, theme)

        elif "÷" in expr or "/" in expr or ":" in expr:
            parts = expr.replace("÷", "/").replace(":", "/").split("/")
            a, b = parts[0].strip(), parts[1].strip()
            return self._division_story(a, b, name, theme)

        # Fallback for fraction and other expressions
        name2 = random.choice([n for n in TURKISH_NAMES if n != name])
        return f"{name} ve {name2}, bir proje için şu matematiksel ifadeyi hesaplamaları gerekmektedir: {expression}. Buna göre, bu işlemin sonucu kaçtır?"

    def _addition_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate TYT yeni nesil addition story."""
        templates = {
            StoryTheme.ALISVERIS: f"{name}, bir kırtasiyeden {a} TL'lik defter ve {b} TL'lik kalem almıştır. Kasada nakit ödeme yapmıştır. Buna göre, {name}'in kasada ödediği toplam tutar kaç TL'dir?",
            StoryTheme.SPOR: f"Bir basketbol turnuvasında {name}'in takımı ilk yarıda {a}, ikinci yarıda {b} sayı atmıştır. Buna göre, takımın maç sonunda toplam attığı sayı kaçtır?",
            StoryTheme.YEMEK: f"{name}, bir tarife göre pasta yaparken ilk malzeme için {a} gram, ikinci malzeme için {b} gram şeker kullanmıştır. Buna göre, tarifin tamamı için kullanılan toplam şeker miktarı kaç gramdır?",
            StoryTheme.SEYAHAT: f"{name}, sabah evden işe giderken {a} km, akşam işten eve dönerken farklı bir yoldan {b} km yol gitmiştir. Buna göre, {name}'in gün içinde toplam gittiği yol kaç km'dir?",
            StoryTheme.OKUL: f"Bir sınıfta yapılan ankete göre {a} öğrenci fen bilimleri, {b} öğrenci matematik dersini en sevdiği ders olarak belirtmiştir. Bu iki dersi seçen öğrenci sayılarının toplamı kaçtır?",
            StoryTheme.GUNLUK_HAYAT: f"{name}, kütüphaneden bu hafta {a} kitap, geçen hafta {b} kitap ödünç almıştır. Buna göre, {name}'in iki haftada ödünç aldığı toplam kitap sayısı kaçtır?",
        }
        return templates.get(theme, templates[StoryTheme.GUNLUK_HAYAT])

    def _subtraction_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate TYT yeni nesil subtraction story."""
        templates = {
            StoryTheme.ALISVERIS: f"{name}'in bütçesinde {a} TL bulunmaktadır. Bir alışveriş merkezinde {b} TL tutarında harcama yapmıştır. Buna göre, {name}'in kalan bütçesi kaç TL'dir?",
            StoryTheme.SPOR: f"Bir yüzme yarışmasında {name} {a} saniyede, rakibi ise {b} saniyede bitirmiştir. Buna göre, {name} rakibinden kaç saniye önce bitirmiştir?",
            StoryTheme.YEMEK: f"Bir fırında sabah {a} adet ekmek üretilmiştir. Öğlene kadar {b} adedi satılmıştır. Buna göre, öğleden sonra fırında kalan ekmek sayısı kaçtır?",
            StoryTheme.SEYAHAT: f"{name}, toplam {a} km uzunluğundaki bir yolculuğa çıkmıştır. Şu ana kadar {b} km yol almıştır. Buna göre, {name}'in kalan yol mesafesi kaç km'dir?",
            StoryTheme.OKUL: f"Bir okul kütüphanesinde {a} kitap bulunmaktadır. Dönem başında öğrencilere {b} kitap dağıtılmıştır. Buna göre, kütüphanede kalan kitap sayısı kaçtır?",
            StoryTheme.GUNLUK_HAYAT: f"Bir depoda {a} adet ürün stoklanmıştır. Gün içinde {b} adet ürün sevk edilmiştir. Buna göre, depoda kalan ürün sayısı kaçtır?",
        }
        return templates.get(theme, templates[StoryTheme.GUNLUK_HAYAT])

    def _multiplication_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate TYT yeni nesil multiplication story."""
        templates = {
            StoryTheme.ALISVERIS: f"{name}, bir mağazadan tanesi {b} TL olan üründen {a} adet satın almıştır. Buna göre, {name}'in bu alışveriş için ödediği toplam tutar kaç TL'dir?",
            StoryTheme.SPOR: f"Bir okulda {a} sınıf bulunmaktadır ve her sınıftan {b} öğrenci okul spor takımına seçilmiştir. Buna göre, spor takımındaki toplam öğrenci sayısı kaçtır?",
            StoryTheme.YEMEK: f"{name}, bir organizasyon için {a} tepsi baklava sipariş etmiştir. Her tepside {b} dilim bulunmaktadır. Buna göre, organizasyon için hazırlanan toplam baklava dilimi sayısı kaçtır?",
            StoryTheme.SEYAHAT: f"Bir tur otobüsü günde {a} sefer yapmaktadır. Her seferde {b} yolcu taşımaktadır. Buna göre, otobüsün bir günde taşıdığı toplam yolcu sayısı kaçtır?",
            StoryTheme.OKUL: f"Bir okulda {a} şube vardır ve her şubede {b} öğrenci bulunmaktadır. Buna göre, okulun toplam öğrenci sayısı kaçtır?",
            StoryTheme.GUNLUK_HAYAT: f"Bir apartmanda {a} kat bulunmakta olup her katta {b} daire vardır. Buna göre, apartmandaki toplam daire sayısı kaçtır?",
        }
        return templates.get(theme, templates[StoryTheme.GUNLUK_HAYAT])

    def _division_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate TYT yeni nesil division story."""
        templates = {
            StoryTheme.ALISVERIS: f"Bir mağaza, toplam {a} TL tutarındaki ürünleri {b} eşit taksitle satışa sunmuştur. Buna göre, her bir taksitin tutarı kaç TL'dir?",
            StoryTheme.SPOR: f"Bir atletizm antrenörü, {a} metrelik koşu parkurunu {b} eşit etaba bölmüştür. Buna göre, her bir etabın uzunluğu kaç metredir?",
            StoryTheme.YEMEK: f"{name}, {a} adet kurabiyeyi {b} kişiye eşit olarak dağıtacaktır. Buna göre, her kişiye kaç kurabiye düşmektedir?",
            StoryTheme.SEYAHAT: f"Bir otobüs şirketi, {a} km'lik güzergâhı {b} eşit durağa bölmüştür. Buna göre, ardışık iki durak arasındaki mesafe kaç km'dir?",
            StoryTheme.OKUL: f"Bir okul müdürü, {a} adet kitabı {b} sınıfa eşit olarak dağıtacaktır. Buna göre, her sınıfa kaç kitap düşmektedir?",
            StoryTheme.GUNLUK_HAYAT: f"Bir çiftçi, {a} kg ürünü {b} eşit çuvala paylaştırmak istemektedir. Buna göre, her çuvala kaç kg ürün konulmalıdır?",
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
