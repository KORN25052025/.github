"""
Accessibility and Inclusivity Service for the Adaptive Math Learning Platform.

Provides text-to-speech, multi-language support, accessibility settings,
and special education accommodations for a Turkish math learning platform.
Supports Turkish (tr), English (en), Kurdish (ku), and Arabic (ar).
"""

from __future__ import annotations

import hashlib
import random
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ColorBlindMode(Enum):
    """Supported colour-blindness simulation / accommodation modes."""
    NONE = "none"
    PROTANOPIA = "protanopia"
    DEUTERANOPIA = "deuteranopia"
    TRITANOPIA = "tritanopia"


class DyslexiaFont(Enum):
    """Font options optimised for readers with dyslexia."""
    DEFAULT = "default"
    OPENDYSLEXIC = "OpenDyslexic"
    LEXIE_READABLE = "LexieReadable"
    COMIC_SANS = "ComicSans"


class SimplificationLevel(Enum):
    """How aggressively a question is simplified."""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    MAXIMUM = "maximum"


# ---------------------------------------------------------------------------
# Data-classes
# ---------------------------------------------------------------------------

@dataclass
class AccessibilityPreferences:
    """Full set of per-user accessibility preferences."""
    user_id: str
    font_size: int = 16
    high_contrast: bool = False
    dyslexia_font: DyslexiaFont = DyslexiaFont.DEFAULT
    color_blind_mode: ColorBlindMode = ColorBlindMode.NONE
    screen_reader_mode: bool = False
    reduced_motion: bool = False
    language: str = "tr"
    auto_read_questions: bool = False
    extra_time_multiplier: float = 1.0
    simplified_ui: bool = False
    text_spacing: float = 1.0
    cursor_size: str = "normal"
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        self.extra_time_multiplier = max(1.0, min(3.0, self.extra_time_multiplier))
        self.font_size = max(12, min(32, self.font_size))
        self.text_spacing = max(1.0, min(3.0, self.text_spacing))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "font_size": self.font_size,
            "high_contrast": self.high_contrast,
            "dyslexia_font": self.dyslexia_font.value,
            "color_blind_mode": self.color_blind_mode.value,
            "screen_reader_mode": self.screen_reader_mode,
            "reduced_motion": self.reduced_motion,
            "language": self.language,
            "auto_read_questions": self.auto_read_questions,
            "extra_time_multiplier": self.extra_time_multiplier,
            "simplified_ui": self.simplified_ui,
            "text_spacing": self.text_spacing,
            "cursor_size": self.cursor_size,
            "updated_at": self.updated_at,
        }


@dataclass
class GlossaryEntry:
    """A single maths-term entry with translations and definitions."""
    term_id: str
    term_tr: str
    term_en: str
    term_ku: str
    term_ar: str
    definition_tr: str
    definition_en: str
    definition_ku: str
    definition_ar: str
    example: Optional[str] = None
    related_terms: List[str] = field(default_factory=list)
    difficulty_level: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "term_id": self.term_id,
            "term_tr": self.term_tr,
            "term_en": self.term_en,
            "term_ku": self.term_ku,
            "term_ar": self.term_ar,
            "definition_tr": self.definition_tr,
            "definition_en": self.definition_en,
            "definition_ku": self.definition_ku,
            "definition_ar": self.definition_ar,
            "example": self.example,
            "related_terms": self.related_terms,
            "difficulty_level": self.difficulty_level,
        }


@dataclass
class SimplifiedQuestion:
    """A question rewritten / restructured for special-needs learners."""
    original_question_id: str
    simplified_text: str
    visual_aids: List[str]
    step_by_step_breakdown: List[str]
    vocabulary_hints: Dict[str, str]
    estimated_extra_time_seconds: int
    simplification_level: SimplificationLevel = SimplificationLevel.MODERATE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_question_id": self.original_question_id,
            "simplified_text": self.simplified_text,
            "visual_aids": self.visual_aids,
            "step_by_step_breakdown": self.step_by_step_breakdown,
            "vocabulary_hints": self.vocabulary_hints,
            "estimated_extra_time_seconds": self.estimated_extra_time_seconds,
            "simplification_level": self.simplification_level.value,
        }


@dataclass
class SpeechResult:
    """Result of a text-to-speech synthesis request."""
    audio_url: str
    duration_seconds: float
    language: str
    text_hash: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audio_url": self.audio_url,
            "duration_seconds": self.duration_seconds,
            "language": self.language,
            "text_hash": self.text_hash,
            "created_at": self.created_at,
        }


@dataclass
class ScaffoldingSupport:
    """Additional scaffolding for a question."""
    question_id: str
    visual_aids: List[str]
    verbal_prompts: List[str]
    manipulative_suggestions: List[str]
    real_world_connections: List[str]
    prerequisite_skills: List[str]
    simplification_level: SimplificationLevel

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "visual_aids": self.visual_aids,
            "verbal_prompts": self.verbal_prompts,
            "manipulative_suggestions": self.manipulative_suggestions,
            "real_world_connections": self.real_world_connections,
            "prerequisite_skills": self.prerequisite_skills,
            "simplification_level": self.simplification_level.value,
        }


# ---------------------------------------------------------------------------
# Glossary data - 35 mathematical terms in four languages
# ---------------------------------------------------------------------------

_MATH_GLOSSARY: List[GlossaryEntry] = [
    GlossaryEntry(
        term_id="addition", term_tr="Toplama", term_en="Addition",
        term_ku="Lekdan", term_ar="جمع",
        definition_tr="Iki veya daha fazla sayiyi birlestirerek toplami bulma islemi.",
        definition_en="The process of combining two or more numbers to find their total.",
        definition_ku="Pevajoya kombuuna du an ji zetir jimaran ji bo ditina berhevoka wan.",
        definition_ar="عملية دمج عددين أو أكثر لإيجاد مجموعهما.",
        example="3 + 5 = 8", related_terms=["subtraction", "sum"], difficulty_level=1,
    ),
    GlossaryEntry(
        term_id="subtraction", term_tr="Cikarma", term_en="Subtraction",
        term_ku="Derxistin", term_ar="طرح",
        definition_tr="Bir sayidan digerini cikararak farki bulma islemi.",
        definition_en="The process of removing one number from another to find the difference.",
        definition_ku="Pevajoya rakirina jimareyeke ji ya din ji bo ditina cudahiye.",
        definition_ar="عملية إزالة عدد من عدد آخر لإيجاد الفرق.",
        example="9 - 4 = 5", related_terms=["addition", "difference"], difficulty_level=1,
    ),
    GlossaryEntry(
        term_id="multiplication", term_tr="Carpma", term_en="Multiplication",
        term_ku="Pirjimar", term_ar="ضرب",
        definition_tr="Bir sayiyi belirli bir sayida tekrarlayarak carpimi bulma islemi.",
        definition_en="The process of repeated addition of a number a certain number of times.",
        definition_ku="Pevajoya dubare kirina lekdana jimareyeke cend caran.",
        definition_ar="عملية تكرار جمع عدد عدة مرات.",
        example="4 x 3 = 12", related_terms=["division", "product"], difficulty_level=1,
    ),
    GlossaryEntry(
        term_id="division", term_tr="Bolme", term_en="Division",
        term_ku="Dabeskirn", term_ar="قسمة",
        definition_tr="Bir sayiyi esit gruplara ayirma islemi.",
        definition_en="The process of splitting a number into equal groups.",
        definition_ku="Pevajoya dabeskirina jimareyeke li komen wekhev.",
        definition_ar="عملية تقسيم عدد إلى مجموعات متساوية.",
        example="12 / 3 = 4", related_terms=["multiplication", "quotient"], difficulty_level=1,
    ),
    GlossaryEntry(
        term_id="fraction", term_tr="Kesir", term_en="Fraction",
        term_ku="Perce", term_ar="كسر",
        definition_tr="Bir butunun esit parcalarindan birini veya birkacini gosteren sayi.",
        definition_en="A number that represents one or more equal parts of a whole.",
        definition_ku="Jimareyek ku yek an ji cend besen wekhev en tevayiyeke nisan dide.",
        definition_ar="عدد يمثل جزءاً واحداً أو أكثر من أجزاء متساوية لكل.",
        example="1/2, 3/4", related_terms=["numerator", "denominator", "decimal"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="percentage", term_tr="Yuzde", term_en="Percentage",
        term_ku="Ji sede", term_ar="نسبة مئوية",
        definition_tr="Bir miktarin yuzdeki oranidir. 100 uzerinden ifade edilir.",
        definition_en="A fraction or ratio expressed as a number out of 100.",
        definition_ku="Pariyeke an rewsenek weke jimareke ji 100 te hatiye vegotin.",
        definition_ar="كسر أو نسبة معبر عنها كرقم من 100.",
        example="%25 = 25/100 = 0.25", related_terms=["fraction", "ratio"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="equation", term_tr="Denklem", term_en="Equation",
        term_ku="Hevkesi", term_ar="معادلة",
        definition_tr="Iki matematiksel ifadenin esitligini gosteren ifade.",
        definition_en="A mathematical statement showing that two expressions are equal.",
        definition_ku="Daxuyaniyek matematiki ku nisan dide du ibare wekhev in.",
        definition_ar="عبارة رياضية توضح أن تعبيرين متساويان.",
        example="2x + 3 = 7", related_terms=["variable", "algebra"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="variable", term_tr="Degisken", term_en="Variable",
        term_ku="Guherbar", term_ar="متغير",
        definition_tr="Bilinmeyen bir degeri temsil eden harf veya sembol.",
        definition_en="A letter or symbol representing an unknown value.",
        definition_ku="Tipen an sembolek ku nirxeke nenas temsil dike.",
        definition_ar="حرف أو رمز يمثل قيمة مجهولة.",
        example="x, y, z", related_terms=["equation", "constant"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="area", term_tr="Alan", term_en="Area",
        term_ku="Rober", term_ar="مساحة",
        definition_tr="Bir seklin yuzeyinin buyuklugu, kare birim cinsinden olculur.",
        definition_en="The size of a surface, measured in square units.",
        definition_ku="Mezinbuna ruye sekilek, bi yekinen caregosey te dipimin.",
        definition_ar="حجم سطح ما، يُقاس بالوحدات المربعة.",
        example="Dikdortgen alani = uzunluk x genislik", related_terms=["perimeter", "volume"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="perimeter", term_tr="Cevre", term_en="Perimeter",
        term_ku="Dorber", term_ar="محيط",
        definition_tr="Bir seklin dis kenarlarinin toplam uzunlugu.",
        definition_en="The total distance around the outside of a shape.",
        definition_ku="Civata gistayi ya li dora derveyiya sekileke.",
        definition_ar="المسافة الإجمالية حول الجزء الخارجي من الشكل.",
        example="Kare cevresi = 4 x kenar", related_terms=["area", "length"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="angle", term_tr="Aci", term_en="Angle",
        term_ku="Goce", term_ar="زاوية",
        definition_tr="Iki dogrukun veya isininin ortak noktada olusturdugu sekil.",
        definition_en="The figure formed by two rays sharing a common endpoint.",
        definition_ku="Sekilek ku ji du tirisan an tisan ku xala hevpar parvedikin pedite.",
        definition_ar="الشكل المتكون من شعاعين يشتركان في نقطة نهاية.",
        example="Dik aci = 90 derece", related_terms=["triangle", "degree"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="triangle", term_tr="Ucgen", term_en="Triangle",
        term_ku="Sego", term_ar="مثلث",
        definition_tr="Uc kenari ve uc acisi olan duz geometrik sekil.",
        definition_en="A flat shape with three sides and three angles.",
        definition_ku="Sekilek tevik bi se aliyan u se goceyan.",
        definition_ar="شكل مسطح بثلاثة أضلاع وثلاث زوايا.",
        example="Eskenar ucgen: 3 kenari esit", related_terms=["angle", "area"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="circle", term_tr="Daire", term_en="Circle",
        term_ku="Bazne", term_ar="دائرة",
        definition_tr="Merkezden esit uzaklikta olan noktalarin olusturdugu kapalı egri.",
        definition_en="A round plane figure whose boundary consists of points equidistant from a fixed center.",
        definition_ku="Sekilek gilover ku sinure we ji xalan pedite ku ji navendeke sabit wekhev dur in.",
        definition_ar="شكل مسطح مستدير حدوده يتكون من نقاط متساوية البعد عن مركز ثابت.",
        example="Daire alani = pi x r^2", related_terms=["radius", "diameter", "pi"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="ratio", term_tr="Oran", term_en="Ratio",
        term_ku="Rew", term_ar="نسبة",
        definition_tr="Iki miktarin birbirine oranini gosteren ifade.",
        definition_en="A comparison of two quantities by division.",
        definition_ku="Berawirdkirina du miqdarean bi dabesekirine.",
        definition_ar="مقارنة بين كميتين بالقسمة.",
        example="3:5 veya 3/5", related_terms=["proportion", "fraction"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="exponent", term_tr="Us", term_en="Exponent",
        term_ku="Hejmara jor", term_ar="أس",
        definition_tr="Bir sayinin kendisiyle kac kez carpilacagini belirten sayi.",
        definition_en="A number that indicates how many times a base is multiplied by itself.",
        definition_ku="Jimareyek ku nisan dide ku bngehek cend caran bi xwe te pircimar dibe.",
        definition_ar="رقم يشير إلى عدد المرات التي يُضرب فيها الأساس بنفسه.",
        example="2^3 = 8", related_terms=["base", "power"], difficulty_level=3,
    ),
    GlossaryEntry(
        term_id="square_root", term_tr="Karekoku", term_en="Square Root",
        term_ku="Reha caregoce", term_ar="جذر تربيعي",
        definition_tr="Kendisiyle carpildiginda verilen sayiyi veren sayi.",
        definition_en="A value that, when multiplied by itself, gives the number.",
        definition_ku="Nirxek ku dema bi xwe te bicimire jimara diyarikiri dide.",
        definition_ar="قيمة عند ضربها بنفسها تعطي العدد.",
        example="Karekoku(9) = 3", related_terms=["exponent", "radical"], difficulty_level=3,
    ),
    GlossaryEntry(
        term_id="prime_number", term_tr="Asal Sayi", term_en="Prime Number",
        term_ku="Jimara seretayi", term_ar="عدد أولي",
        definition_tr="Yalnizca 1'e ve kendisine tam bolunen 1'den buyuk dogal sayi.",
        definition_en="A natural number greater than 1 that has no positive divisors other than 1 and itself.",
        definition_ku="Jimara xwezayi ya ji 1 mezintir ku ji 1 u xwe pe ve dabeserek eron ninin.",
        definition_ar="عدد طبيعي أكبر من 1 ليس له قواسم موجبة غير 1 ونفسه.",
        example="2, 3, 5, 7, 11, 13", related_terms=["composite_number", "factor"], difficulty_level=3,
    ),
    GlossaryEntry(
        term_id="probability", term_tr="Olasilik", term_en="Probability",
        term_ku="Ihtimal", term_ar="احتمال",
        definition_tr="Bir olayin gerceklesme ihtimalinin sayisal olarak ifadesi.",
        definition_en="A measure of the likelihood that an event will occur.",
        definition_ku="Pivana ihtimala ku buwariyek biqewime.",
        definition_ar="مقياس لاحتمال حدوث حدث ما.",
        example="P(yazi) = 1/2", related_terms=["statistics", "event"], difficulty_level=3,
    ),
    GlossaryEntry(
        term_id="mean", term_tr="Ortalama", term_en="Mean (Average)",
        term_ku="Navinci", term_ar="المتوسط",
        definition_tr="Sayilarin toplaminin sayi adedine bolunmesiyle bulunan deger.",
        definition_en="The sum of all values divided by the number of values.",
        definition_ku="Civata hemu nirxan li ser jimara nirxan dabeskiri.",
        definition_ar="مجموع جميع القيم مقسوماً على عددها.",
        example="(3+5+7)/3 = 5", related_terms=["median", "mode"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="function", term_tr="Fonksiyon", term_en="Function",
        term_ku="Fonksiyon", term_ar="دالة",
        definition_tr="Her girdiye tam olarak bir cikti eslestiren kural.",
        definition_en="A rule that assigns exactly one output to each input.",
        definition_ku="Rewilek ku ji her ketiyek rast yek derkevtiyek diyar dike.",
        definition_ar="قاعدة تعين مخرجاً واحداً بالضبط لكل مدخل.",
        example="f(x) = 2x + 1", related_terms=["domain", "range"], difficulty_level=3,
    ),
    GlossaryEntry(
        term_id="polynomial", term_tr="Polinom", term_en="Polynomial",
        term_ku="Polinom", term_ar="كثير حدود",
        definition_tr="Degiskenlerin ve katsayilarin toplam, cikarma ve carpim islemleriyle olusturdugu ifade.",
        definition_en="An expression with variables and coefficients using addition, subtraction, and multiplication.",
        definition_ku="Ibareyeke bi guherbar u hevjimaran ku bi lekdan, derxistin u pirjimaran pedite.",
        definition_ar="تعبير بمتغيرات ومعاملات باستخدام الجمع والطرح والضرب.",
        example="3x^2 + 2x - 5", related_terms=["coefficient", "degree"], difficulty_level=3,
    ),
    GlossaryEntry(
        term_id="sine", term_tr="Sinus", term_en="Sine",
        term_ku="Sinus", term_ar="جيب",
        definition_tr="Dik ucgende karsi kenarin hipotenuese orani.",
        definition_en="In a right triangle, the ratio of the opposite side to the hypotenuse.",
        definition_ku="Di segoyek rast de, rewa aliya beridir li ser hipotenuze.",
        definition_ar="في المثلث القائم، نسبة الضلع المقابل إلى الوتر.",
        example="sin(30) = 0.5", related_terms=["cosine", "tangent"], difficulty_level=4,
    ),
    GlossaryEntry(
        term_id="cosine", term_tr="Kosinus", term_en="Cosine",
        term_ku="Kosinus", term_ar="جيب التمام",
        definition_tr="Dik ucgende komsu kenarin hipotenuese orani.",
        definition_en="In a right triangle, the ratio of the adjacent side to the hypotenuse.",
        definition_ku="Di segoyek rast de, rewa aliya nik li ser hipotenuze.",
        definition_ar="في المثلث القائم، نسبة الضلع المجاور إلى الوتر.",
        example="cos(60) = 0.5", related_terms=["sine", "tangent"], difficulty_level=4,
    ),
    GlossaryEntry(
        term_id="set", term_tr="Kume", term_en="Set",
        term_ku="Kom", term_ar="مجموعة",
        definition_tr="Belirli bir kurala gore bir araya getirilen nesneler toplulugu.",
        definition_en="A collection of distinct objects grouped by a rule.",
        definition_ku="Kombuna tisteyen cuda ku li gor rewelek kom kirine.",
        definition_ar="مجموعة من العناصر المميزة المجمعة وفقاً لقاعدة.",
        example="A = {1, 2, 3}", related_terms=["element", "subset"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="inequality", term_tr="Esitsizlik", term_en="Inequality",
        term_ku="Newekhevi", term_ar="متباينة",
        definition_tr="Iki ifadenin esit olmadigini gosteren matematiksel ifade.",
        definition_en="A mathematical statement showing two expressions are not equal.",
        definition_ku="Daxuyaniyeke matematiki ku du ibare wekhev ninin nisan dide.",
        definition_ar="عبارة رياضية توضح أن تعبيرين غير متساويين.",
        example="x > 5, 2x + 1 < 10", related_terms=["equation", "interval"], difficulty_level=3,
    ),
    GlossaryEntry(
        term_id="coordinate", term_tr="Koordinat", term_en="Coordinate",
        term_ku="Koordinat", term_ar="إحداثي",
        definition_tr="Bir noktanin duzlemdeki konumunu belirleyen sayi cifti.",
        definition_en="A pair of numbers that defines the position of a point on a plane.",
        definition_ku="Cot jimareyan ku ciya xaleke li ser rewsene diyar dike.",
        definition_ar="زوج من الأرقام يحدد موضع نقطة على المستوى.",
        example="(3, 5)", related_terms=["axis", "graph"], difficulty_level=3,
    ),
    GlossaryEntry(
        term_id="logarithm", term_tr="Logaritma", term_en="Logarithm",
        term_ku="Logaritma", term_ar="لوغاريتم",
        definition_tr="Bir tabanin hangi kuvvetine yukselince verilen sayiyi verdigi deger.",
        definition_en="The power to which a base must be raised to produce a given number.",
        definition_ku="Heza ku divit bne bi we heze bilind bibe da ku jimareya diyarkiri bide.",
        definition_ar="القوة التي يجب رفع الأساس إليها لإنتاج عدد معين.",
        example="log2(8) = 3", related_terms=["exponent", "base"], difficulty_level=4,
    ),
    GlossaryEntry(
        term_id="median", term_tr="Medyan (Ortanca)", term_en="Median",
        term_ku="Navin", term_ar="الوسيط",
        definition_tr="Siralanan verilerin tam ortasindaki deger.",
        definition_en="The middle value in a sorted list of numbers.",
        definition_ku="Nirxa navinci ya di listeya jimaran a rexistikiri de.",
        definition_ar="القيمة الوسطى في قائمة مرتبة من الأعداد.",
        example="1,3,5,7,9 -> medyan = 5", related_terms=["mean", "mode"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="parallel", term_tr="Paralel", term_en="Parallel",
        term_ku="Hevhevu", term_ar="متوازي",
        definition_tr="Ayni duzlemde olup hic kesismeyen iki dogru.",
        definition_en="Two lines in the same plane that never intersect.",
        definition_ku="Du xeten di heman ruwere de ku qet nahevdu dibirin.",
        definition_ar="خطان في نفس المستوى لا يتقاطعان أبداً.",
        example="AB // CD", related_terms=["perpendicular", "line"], difficulty_level=2,
    ),
    GlossaryEntry(
        term_id="symmetry", term_tr="Simetri", term_en="Symmetry",
        term_ku="Simetri", term_ar="تناظر",
        definition_tr="Bir seklin bir eksen etrafinda aynalanan esitlik ozelligi.",
        definition_en="The property of a shape being identical on both sides of a dividing line.",
        definition_ku="Taybetmendia sekileke ku li her du aliyan xeteke dabeskiri yek be.",
        definition_ar="خاصية الشكل بأن يكون متطابقاً على جانبي خط فاصل.",
        example="Kare 4 simetri eksenine sahiptir", related_terms=["reflection", "rotation"], difficulty_level=2,
    ),
]

# Available languages
_AVAILABLE_LANGUAGES = [
    {"code": "tr", "name": "Turkce", "native_name": "Turkce", "direction": "ltr"},
    {"code": "en", "name": "English", "native_name": "English", "direction": "ltr"},
    {"code": "ku", "name": "Kurdish", "native_name": "Kurdi", "direction": "ltr"},
    {"code": "ar", "name": "Arabic", "native_name": "العربية", "direction": "rtl"},
]

# Celebration messages for special education
_CELEBRATION_MESSAGES_TR = [
    "Harika! Dogru cevap! Sen cok zekasin!",
    "Tebrikler! Muhtesem bir is cikardin!",
    "Supersin! Her seferinde daha iyi oluyorsun!",
    "Bravoo! Bu cok zor bir soruydu ama basardin!",
    "Aferin! Matematik senin icin cok kolay olacak!",
    "Inanilmaz! Bir dahaki soru daha da eglenceli olacak!",
    "Cok iyi! Ogretmenin seninle gurur duyacak!",
    "Sasirtttin! Bu tempoda devam et!",
    "Muhteeem! Matematik yildizi olma yolundasin!",
    "Helal olsun! Her yeni soru seni daha guclu yapiyor!",
]


# ---------------------------------------------------------------------------
# TextToSpeechService
# ---------------------------------------------------------------------------

class TextToSpeechService:
    """
    Simulates text-to-speech synthesis.
    In production this would call a TTS API (e.g., Google TTS, Azure TTS).
    """

    def generate_speech(self, text: str, lang: str = "tr") -> SpeechResult:
        """Generate speech from text (simulated)."""
        text_hash = hashlib.md5(f"{text}:{lang}".encode()).hexdigest()
        # Estimate duration: ~150 words per minute
        word_count = len(text.split())
        duration = max(1.0, word_count / 2.5)

        return SpeechResult(
            audio_url=f"/api/v1/tts/audio/{text_hash}.mp3",
            duration_seconds=round(duration, 1),
            language=lang,
            text_hash=text_hash,
        )

    def read_question(self, question_data: Dict[str, Any], lang: str = "tr") -> SpeechResult:
        """Generate speech for a question's expression and story text."""
        parts = []
        if question_data.get("story_text"):
            parts.append(question_data["story_text"])
        if question_data.get("expression"):
            # Convert math expression to speakable text
            expr = self._math_to_speech(question_data["expression"], lang)
            parts.append(expr)

        text = ". ".join(parts) if parts else "Soru metni bulunamadi."
        return self.generate_speech(text, lang)

    @staticmethod
    def _math_to_speech(expression: str, lang: str = "tr") -> str:
        """Convert math expression to speakable text in Turkish."""
        if lang != "tr":
            return expression

        replacements = [
            ("+", " arti "),
            ("-", " eksi "),
            ("*", " carpi "),
            ("/", " bolu "),
            ("=", " esittir "),
            ("^2", " kare"),
            ("^3", " kup"),
            ("x", " x "),
            ("(", " parantez ac "),
            (")", " parantez kapa "),
        ]
        result = expression
        for old, new in replacements:
            result = result.replace(old, new)
        # Clean up extra spaces
        result = re.sub(r'\s+', ' ', result).strip()
        return result


# ---------------------------------------------------------------------------
# AccessibilitySettingsService
# ---------------------------------------------------------------------------

class AccessibilitySettingsService:
    """Manages per-user accessibility preferences."""

    def __init__(self) -> None:
        self._settings: Dict[str, AccessibilityPreferences] = {}

    def get_settings(self, user_id: str) -> AccessibilityPreferences:
        """Get accessibility settings for a user, creating defaults if needed."""
        if user_id not in self._settings:
            self._settings[user_id] = AccessibilityPreferences(user_id=user_id)
        return self._settings[user_id]

    def update_settings(self, user_id: str, updates: Dict[str, Any]) -> AccessibilityPreferences:
        """Update accessibility settings for a user."""
        prefs = self.get_settings(user_id)

        if "font_size" in updates:
            prefs.font_size = max(12, min(32, int(updates["font_size"])))
        if "high_contrast" in updates:
            prefs.high_contrast = bool(updates["high_contrast"])
        if "dyslexia_font" in updates:
            prefs.dyslexia_font = DyslexiaFont(updates["dyslexia_font"])
        if "color_blind_mode" in updates:
            prefs.color_blind_mode = ColorBlindMode(updates["color_blind_mode"])
        if "screen_reader_mode" in updates:
            prefs.screen_reader_mode = bool(updates["screen_reader_mode"])
        if "reduced_motion" in updates:
            prefs.reduced_motion = bool(updates["reduced_motion"])
        if "language" in updates:
            prefs.language = str(updates["language"])
        if "auto_read_questions" in updates:
            prefs.auto_read_questions = bool(updates["auto_read_questions"])
        if "extra_time_multiplier" in updates:
            prefs.extra_time_multiplier = max(1.0, min(3.0, float(updates["extra_time_multiplier"])))
        if "simplified_ui" in updates:
            prefs.simplified_ui = bool(updates["simplified_ui"])
        if "text_spacing" in updates:
            prefs.text_spacing = max(1.0, min(3.0, float(updates["text_spacing"])))
        if "cursor_size" in updates:
            prefs.cursor_size = str(updates["cursor_size"])

        prefs.updated_at = datetime.utcnow().isoformat()
        return prefs


# ---------------------------------------------------------------------------
# MultiLanguageService
# ---------------------------------------------------------------------------

class MultiLanguageService:
    """Multi-language support for math terms and glossary."""

    def __init__(self) -> None:
        self._glossary = {entry.term_id: entry for entry in _MATH_GLOSSARY}

    def get_math_glossary(self, term: str, lang: str = "tr") -> Optional[Dict[str, Any]]:
        """Get a math term definition in the requested language."""
        # Try exact match
        entry = self._glossary.get(term.lower().replace(" ", "_"))
        if entry is None:
            # Try searching by Turkish term
            for e in _MATH_GLOSSARY:
                if (e.term_tr.lower() == term.lower()
                        or e.term_en.lower() == term.lower()
                        or e.term_ku.lower() == term.lower()):
                    entry = e
                    break
        if entry is None:
            return None

        lang_map = {
            "tr": {"term": entry.term_tr, "definition": entry.definition_tr},
            "en": {"term": entry.term_en, "definition": entry.definition_en},
            "ku": {"term": entry.term_ku, "definition": entry.definition_ku},
            "ar": {"term": entry.term_ar, "definition": entry.definition_ar},
        }
        translation = lang_map.get(lang, lang_map["tr"])

        return {
            "term_id": entry.term_id,
            "term": translation["term"],
            "definition": translation["definition"],
            "example": entry.example,
            "related_terms": entry.related_terms,
            "difficulty_level": entry.difficulty_level,
            "all_translations": {
                "tr": entry.term_tr,
                "en": entry.term_en,
                "ku": entry.term_ku,
                "ar": entry.term_ar,
            },
        }

    def search_glossary(self, query: str, lang: str = "tr") -> List[Dict[str, Any]]:
        """Search glossary entries by query string."""
        results: List[Dict[str, Any]] = []
        query_lower = query.lower()
        for entry in _MATH_GLOSSARY:
            if (query_lower in entry.term_tr.lower()
                    or query_lower in entry.term_en.lower()
                    or query_lower in entry.definition_tr.lower()
                    or query_lower in entry.definition_en.lower()):
                result = self.get_math_glossary(entry.term_id, lang)
                if result:
                    results.append(result)
        return results

    @staticmethod
    def get_available_languages() -> List[Dict[str, str]]:
        """Return all supported languages."""
        return list(_AVAILABLE_LANGUAGES)

    def translate_question(self, question_data: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """Translate a question's expression to the target language (basic term replacement)."""
        if target_lang == "tr":
            return question_data

        translated = dict(question_data)
        expression = question_data.get("expression", "")

        # Replace known Turkish math terms with target language equivalents
        for entry in _MATH_GLOSSARY:
            lang_terms = {"en": entry.term_en, "ku": entry.term_ku, "ar": entry.term_ar}
            target_term = lang_terms.get(target_lang, entry.term_tr)
            if entry.term_tr.lower() in expression.lower():
                expression = re.sub(
                    re.escape(entry.term_tr), target_term, expression, flags=re.IGNORECASE
                )

        translated["expression"] = expression
        translated["language"] = target_lang
        return translated


# ---------------------------------------------------------------------------
# SpecialEducationService
# ---------------------------------------------------------------------------

class SpecialEducationService:
    """
    Provides accommodations for students with special educational needs:
    - Simplified question versions
    - Extra scaffolding (visual aids, verbal prompts)
    - Positive reinforcement in Turkish
    """

    def get_simplified_question(
        self,
        question_data: Dict[str, Any],
        level: SimplificationLevel = SimplificationLevel.MODERATE,
    ) -> SimplifiedQuestion:
        """Create a simplified version of a question."""
        expression = question_data.get("expression", "")
        question_type = question_data.get("question_type", "arithmetic")

        # Generate simplified text
        simplified_text = self._simplify_text(expression, question_type, level)

        # Visual aids
        visual_aids = self._get_visual_aids(question_type, level)

        # Step-by-step breakdown
        steps = self._get_step_breakdown(expression, question_type, level)

        # Vocabulary hints
        vocab = self._get_vocabulary_hints(expression, question_type)

        # Extra time estimate
        extra_time_map = {
            SimplificationLevel.MINIMAL: 30,
            SimplificationLevel.MODERATE: 60,
            SimplificationLevel.MAXIMUM: 120,
        }

        return SimplifiedQuestion(
            original_question_id=question_data.get("question_id", ""),
            simplified_text=simplified_text,
            visual_aids=visual_aids,
            step_by_step_breakdown=steps,
            vocabulary_hints=vocab,
            estimated_extra_time_seconds=extra_time_map.get(level, 60),
            simplification_level=level,
        )

    def get_extra_scaffolding(
        self,
        question_data: Dict[str, Any],
        level: SimplificationLevel = SimplificationLevel.MODERATE,
    ) -> ScaffoldingSupport:
        """Provide extra learning scaffolding for a question."""
        question_type = question_data.get("question_type", "arithmetic")

        return ScaffoldingSupport(
            question_id=question_data.get("question_id", ""),
            visual_aids=self._get_visual_aids(question_type, level),
            verbal_prompts=self._get_verbal_prompts(question_type),
            manipulative_suggestions=self._get_manipulative_suggestions(question_type),
            real_world_connections=self._get_real_world_connections(question_type),
            prerequisite_skills=self._get_prerequisites(question_type),
            simplification_level=level,
        )

    @staticmethod
    def celebration_feedback() -> str:
        """Return a random Turkish celebration message."""
        return random.choice(_CELEBRATION_MESSAGES_TR)

    # -- Private helpers -------------------------------------------------------

    @staticmethod
    def _simplify_text(expression: str, question_type: str, level: SimplificationLevel) -> str:
        """Simplify the question text based on level."""
        if level == SimplificationLevel.MINIMAL:
            return f"Bu soruyu cozelim: {expression}"
        elif level == SimplificationLevel.MODERATE:
            return (
                f"Su islemi birlikte yapalim: {expression}. "
                f"Adim adim dusunelim."
            )
        else:  # MAXIMUM
            return (
                f"Kolay bir soru: {expression}. "
                f"Hadi birlikte cozum yolunu bulalim! "
                f"Yardim icin ipuclarina bakabilirsin."
            )

    @staticmethod
    def _get_visual_aids(question_type: str, level: SimplificationLevel) -> List[str]:
        """Get appropriate visual aids for the question type."""
        aids: Dict[str, List[str]] = {
            "arithmetic": ["Sayi dogrusu", "Parmak sayma", "Sayma tablolari"],
            "fractions": ["Pasta dilimi gorseli", "Kesir seritlari", "Renkli bloklar"],
            "geometry": ["Sekil cizimi", "Aci olcer gorseli", "Kare kagidi"],
            "algebra": ["Terazi gorseli", "Kutu-ok diyagrami"],
            "percentages": ["100luk grid", "Pasta grafigi"],
            "statistics": ["Cubuk grafik", "Sira tablosu"],
        }
        result = aids.get(question_type, ["Genel gorsel yardim"])
        if level == SimplificationLevel.MAXIMUM:
            result.append("Canli ornek animasyonu")
        return result

    @staticmethod
    def _get_step_breakdown(expression: str, question_type: str, level: SimplificationLevel) -> List[str]:
        """Break question into manageable steps."""
        if level == SimplificationLevel.MINIMAL:
            return [f"Coz: {expression}"]
        elif level == SimplificationLevel.MODERATE:
            return [
                "Soruyu dikkatlice oku.",
                f"Ne yapman gerektigini bul: {expression}",
                "Islemi yap.",
                "Sonucu kontrol et.",
            ]
        else:
            return [
                "Once soruyu birlikte okuyalim.",
                "Ne bildigimizi yazalim.",
                "Ne bulmamiz gerektigini yazalim.",
                f"Islemi yapalim: {expression}",
                "Sonucu yazdik mi?",
                "Birlikte kontrol edelim.",
            ]

    @staticmethod
    def _get_vocabulary_hints(expression: str, question_type: str) -> Dict[str, str]:
        """Get vocabulary hints relevant to the question."""
        hints: Dict[str, Dict[str, str]] = {
            "arithmetic": {"toplama": "Sayilari birlestirme", "cikarma": "Bir sayidan digerin alma"},
            "fractions": {"pay": "Kesirin ust kismi", "payda": "Kesirin alt kismi"},
            "geometry": {"alan": "Seklin icindeki buyukluk", "cevre": "Seklin etrafindaki uzunluk"},
            "algebra": {"degisken": "Bilinmeyen sayi (x, y)", "denklem": "Iki tarafi esit olan ifade"},
            "percentages": {"yuzde": "100 uzerinden oran"},
        }
        return hints.get(question_type, {"soru": "Cevabi bulman gereken problem"})

    @staticmethod
    def _get_verbal_prompts(question_type: str) -> List[str]:
        """Get verbal prompts to guide the student."""
        prompts: Dict[str, List[str]] = {
            "arithmetic": [
                "Hangi islemi yapman gerekiyor?",
                "Sayilari parmaginla sayabilirsin.",
                "Birler basamagindan basla.",
            ],
            "fractions": [
                "Kesirin pay ve paydasina bak.",
                "Bir pizza dilimi gibi dusun.",
                "Paydalari esitle.",
            ],
            "geometry": [
                "Sekli cizerek basla.",
                "Kenarlari ve acilari isle.",
                "Formulu hatirla.",
            ],
        }
        return prompts.get(question_type, ["Soruyu dikkatlice oku.", "Ne isteniyor?"])

    @staticmethod
    def _get_manipulative_suggestions(question_type: str) -> List[str]:
        """Suggest hands-on learning materials."""
        suggestions: Dict[str, List[str]] = {
            "arithmetic": ["Lego bloklari ile say", "Boncuk veya fasulye kullan"],
            "fractions": ["Kagit katlama ile kesir", "Oyun hamuru ile paylasim"],
            "geometry": ["Cetvel ve pergel kullan", "Karton sekiller kes"],
        }
        return suggestions.get(question_type, ["Kagit kalem kullan"])

    @staticmethod
    def _get_real_world_connections(question_type: str) -> List[str]:
        """Connect math to real-world scenarios."""
        connections: Dict[str, List[str]] = {
            "arithmetic": ["Markette para hesabi", "Yemek tarifinde olculer"],
            "fractions": ["Pizza dilimlemek", "Bir siseyi esit paylasma"],
            "geometry": ["Odanin alani", "Bahce citi uzunlugu"],
            "percentages": ["Indirimli fiyat hesabi", "Sinav notu yuzdesi"],
            "statistics": ["Sinif boy ortalaması", "Hava durumu tahminleri"],
        }
        return connections.get(question_type, ["Gunluk hayatta matematik"])

    @staticmethod
    def _get_prerequisites(question_type: str) -> List[str]:
        """Identify prerequisite skills for a question type."""
        prereqs: Dict[str, List[str]] = {
            "arithmetic": ["Sayma", "Basamak degeri"],
            "fractions": ["Toplama/cikarma", "Bolme kavrami"],
            "geometry": ["Sekil tanima", "Olcme"],
            "algebra": ["Aritmetik islemler", "Ters islem kavrami"],
            "percentages": ["Kesir", "Oran"],
        }
        return prereqs.get(question_type, [])


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

tts_service = TextToSpeechService()
accessibility_settings_service = AccessibilitySettingsService()
multi_language_service = MultiLanguageService()
special_education_service = SpecialEducationService()
