"""
Motivation and Enrichment Content Service
==========================================
Turkce matematik ogrenme platformu icin motivasyon ve zenginlestirme servisi.

Includes:
- MathHistoryService: Matematik tarihi bilgileri ve matematikci hikayeleri
- MathPuzzleService: Gunluk bulmacalar ve mantik sorulari
- CertificateService: Basari sertifikalari olusturma ve yonetim
- SeasonalContentService: Mevsimsel ve tatil icerikleri
"""

from __future__ import annotations

import hashlib
import random
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MasteryLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"


class Season(Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class MathFact:
    """Bir matematik tarihi bilgisi."""
    id: str
    title: str
    content: str
    mathematician: Optional[str] = None
    year: Optional[str] = None
    topic_slugs: List[str] = field(default_factory=list)
    source: Optional[str] = None
    fun_rating: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "mathematician": self.mathematician,
            "year": self.year,
            "topic_slugs": self.topic_slugs,
            "source": self.source,
            "fun_rating": self.fun_rating,
        }


@dataclass
class Mathematician:
    """Bir matematikcinin biyografi karti."""
    id: str
    name: str
    birth_year: Optional[str] = None
    death_year: Optional[str] = None
    nationality: str = ""
    biography: str = ""
    contributions: List[str] = field(default_factory=list)
    famous_quote: Optional[str] = None
    image_url: Optional[str] = None
    related_topics: List[str] = field(default_factory=list)
    fun_facts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "nationality": self.nationality,
            "biography": self.biography,
            "contributions": self.contributions,
            "famous_quote": self.famous_quote,
            "image_url": self.image_url,
            "related_topics": self.related_topics,
            "fun_facts": self.fun_facts,
        }


@dataclass
class Puzzle:
    """Bir matematik/mantik bulmacasi."""
    id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    answer: str
    hints: List[str] = field(default_factory=list)
    explanation: str = ""
    category: str = "logic"
    points: int = 10
    time_limit_seconds: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty.value,
            "category": self.category,
            "points": self.points,
            "time_limit_seconds": self.time_limit_seconds,
            "hints": self.hints,
        }


@dataclass
class Certificate:
    """Bir basari sertifikasi."""
    id: str
    user_id: str
    title: str
    description: str
    topic_slug: str
    mastery_level: MasteryLevel
    issued_at: datetime = field(default_factory=datetime.utcnow)
    certificate_code: str = ""
    template: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "topic_slug": self.topic_slug,
            "mastery_level": self.mastery_level.value,
            "issued_at": self.issued_at.isoformat(),
            "certificate_code": self.certificate_code,
            "template": self.template,
        }


@dataclass
class SeasonalTheme:
    """Mevsimsel tema bilgisi."""
    id: str
    name: str
    season: Season
    description: str
    color_primary: str
    color_secondary: str
    icon: str
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=date.today)
    challenges: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "season": self.season.value,
            "description": self.description,
            "color_primary": self.color_primary,
            "color_secondary": self.color_secondary,
            "icon": self.icon,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "challenges": self.challenges,
        }


@dataclass
class HolidayContent:
    """Tatil gunu ozel icerigi."""
    id: str
    holiday_name: str
    description: str
    date_month: int
    date_day: int
    is_variable_date: bool = False
    challenges: List[Dict[str, Any]] = field(default_factory=list)
    fun_facts: List[str] = field(default_factory=list)
    greeting: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "holiday_name": self.holiday_name,
            "description": self.description,
            "date_month": self.date_month,
            "date_day": self.date_day,
            "is_variable_date": self.is_variable_date,
            "challenges": self.challenges,
            "fun_facts": self.fun_facts,
            "greeting": self.greeting,
        }


@dataclass
class PuzzleAttempt:
    """Bulmaca deneme kaydi."""
    puzzle_id: str
    user_id: str
    answer: str
    is_correct: bool
    attempted_at: datetime = field(default_factory=datetime.utcnow)
    hints_used: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "puzzle_id": self.puzzle_id,
            "user_id": self.user_id,
            "answer": self.answer,
            "is_correct": self.is_correct,
            "attempted_at": self.attempted_at.isoformat(),
            "hints_used": self.hints_used,
        }


# ---------------------------------------------------------------------------
# MathHistoryService
# ---------------------------------------------------------------------------

class MathHistoryService:
    """Matematik tarihi bilgileri ve matematikci hikayeleri servisi."""

    def __init__(self) -> None:
        self._facts: List[MathFact] = self._load_facts()
        self._mathematicians: Dict[str, Mathematician] = self._load_mathematicians()
        self._topic_history: Dict[str, List[MathFact]] = self._build_topic_index()

    # -- Public API ----------------------------------------------------------

    def get_daily_fact(self, reference_date: Optional[date] = None) -> MathFact:
        """Gunun matematik tarihi bilgisini dondurur."""
        today = reference_date or date.today()
        day_of_year = today.timetuple().tm_yday
        index = day_of_year % len(self._facts)
        return self._facts[index]

    def get_mathematician_story(self, mathematician_id: str) -> Optional[Mathematician]:
        """Belirtilen matematikcinin biyografi kartini dondurur."""
        return self._mathematicians.get(mathematician_id)

    def get_all_mathematicians(self) -> List[Mathematician]:
        """Tum matematikcilerin listesini dondurur."""
        return list(self._mathematicians.values())

    def get_topic_history(self, topic_slug: str) -> List[MathFact]:
        """Bir matematik konusunun tarihsel baglamini dondurur."""
        return self._topic_history.get(topic_slug, [])

    def search_facts(self, query: str) -> List[MathFact]:
        """Bilgiler arasinda arama yapar."""
        query_lower = query.lower()
        results: List[MathFact] = []
        for fact in self._facts:
            if (query_lower in fact.title.lower()
                    or query_lower in fact.content.lower()
                    or (fact.mathematician and query_lower in fact.mathematician.lower())):
                results.append(fact)
        return results

    def get_random_fact(self, exclude_ids: Optional[List[str]] = None) -> MathFact:
        """Rastgele bir bilgi dondurur (belirli idler haric)."""
        exclude = set(exclude_ids or [])
        candidates = [f for f in self._facts if f.id not in exclude]
        if not candidates:
            candidates = self._facts
        return random.choice(candidates)

    # -- Private helpers -----------------------------------------------------

    def _build_topic_index(self) -> Dict[str, List[MathFact]]:
        index: Dict[str, List[MathFact]] = {}
        for fact in self._facts:
            for slug in fact.topic_slugs:
                index.setdefault(slug, []).append(fact)
        return index

    @staticmethod
    def _load_facts() -> List[MathFact]:
        return [
            MathFact(
                id="fact-01", title="Cebirin Babasi",
                content=(
                    "Harizmi (Muhammed bin Musa el-Harizmi), 9. yuzyilda yazdigi "
                    "Kitabul-Muhtasar fi Hisabil-Cebr vel-Mukabele adli eseriyle "
                    "cebir biliminin temellerini atti. Cebir kelimesi bu kitabin "
                    "adindan gelir. Algoritma kelimesi de onun Latinceye cevrilen "
                    "adindan turemistir."
                ),
                mathematician="harizmi", year="820",
                topic_slugs=["cebir", "denklemler"], fun_rating=5,
            ),
            MathFact(
                id="fact-02", title="Pisagor Teoremi Aslinda Daha Eski",
                content=(
                    "Pisagor teoremi (a^2 + b^2 = c^2) Pisagordan yaklasik 1000 yil "
                    "once Babilliler tarafindan biliniyordu. Ancak ilk matematiksel "
                    "ispat Pisagora atfedilir."
                ),
                mathematician="pisagor", year="M.O. 570-495",
                topic_slugs=["geometri", "ucgenler", "pisagor"], fun_rating=5,
            ),
            MathFact(
                id="fact-03", title="Pi Sayisini Hesaplayan Dahi",
                content=(
                    "Arsimet, pi sayisinin degerini hesaplamak icin 96 kenarli "
                    "cokgenler cizip 3.1408 ile 3.1429 arasinda oldugunu bulmustur. "
                    "Bu yaklasim 2000 yil boyunca en iyi tahmin olarak kalmistir."
                ),
                mathematician="arsimed", year="M.O. 250",
                topic_slugs=["geometri", "daire", "pi"], fun_rating=4,
            ),
            MathFact(
                id="fact-04", title="Cahit Arf ve Arf Degismezleri",
                content=(
                    "Turk matematikci Cahit Arf (1910-1997), kuadratik formlar "
                    "teorisinde 'Arf degismezi' kavramini gelistirmistir. Bu kavram "
                    "modern cebirsel topolojide hala kullanilmaktadir. Portresi "
                    "Turk 10 lira banknotunun arkasinda yer almaktadir."
                ),
                mathematician="cahit_arf", year="1941",
                topic_slugs=["cebir", "sayi_teorisi"], fun_rating=5,
            ),
            MathFact(
                id="fact-05", title="Omer Hayyam ve Kup Denklemler",
                content=(
                    "Omer Hayyam (1048-1131) sadece siir yazmamis, ayni zamanda kup "
                    "denklemlerin sistematik geometrik cozumlerini bulan buyuk bir "
                    "matematikcidir. Hayyam takvimi Gregory takviminden daha dogrudur."
                ),
                mathematician="omer_hayyam", year="1077",
                topic_slugs=["cebir", "denklemler", "geometri"], fun_rating=5,
            ),
            MathFact(
                id="fact-06", title="Euler ve Koenigsberg Kopru Problemi",
                content=(
                    "Leonhard Euler, 1736 yilinda Koenigsbergin 7 koprusunun "
                    "hepsinden birer kez gecerek dolasilamayacagini ispatlamis ve "
                    "boylece graf teorisinin temelini atmistir."
                ),
                mathematician="euler", year="1736",
                topic_slugs=["graf_teorisi", "mantik"], fun_rating=4,
            ),
            MathFact(
                id="fact-07", title="Gauss - Matematik Prensi",
                content=(
                    "Carl Friedrich Gauss, 10 yasindayken 1den 100e kadar olan "
                    "sayilarin toplamini saniyeler icinde bulmustur: n(n+1)/2 "
                    "formulu ile 5050. Ogretmeni cok sasirmistir."
                ),
                mathematician="gauss", year="1787",
                topic_slugs=["aritmetik", "sayilar"], fun_rating=5,
            ),
            MathFact(
                id="fact-08", title="Fibonacci Dizisi Dogada",
                content=(
                    "Fibonacci dizisi (1, 1, 2, 3, 5, 8, 13...) dogada her yerde "
                    "karsimiza cikar: ayciegi tohumlarinin spirali, deniz kabuklarinin "
                    "sekli, cicelerin yaprak dizilisi ve tavsan populasyonu gibi."
                ),
                mathematician="fibonacci", year="1202",
                topic_slugs=["diziler", "sayilar", "doga"], fun_rating=5,
            ),
            MathFact(
                id="fact-09", title="Ali Kuscu ve Astronomi Matematigi",
                content=(
                    "Ali Kuscu (1403-1474), Semerkant ve Istanbulda matematik ve "
                    "astronomi egitimi vermis, trigonometrik hesaplamalara onemli "
                    "katkilar yapmis bir Turk bilginidir. Fatih Sultan Mehmetin "
                    "davetlisi olarak Istanbula gelmistir."
                ),
                mathematician="ali_kuscu", year="1450",
                topic_slugs=["trigonometri", "astronomi"], fun_rating=4,
            ),
            MathFact(
                id="fact-10", title="Sonsuzluk Paradokslari",
                content=(
                    "Georg Cantor, 1874te farkli boyutlarda sonsuzluklarin var "
                    "oldugunu ispatlamistir. Reel sayilar kumesi dogal sayilar "
                    "kumesinden 'daha buyuk' bir sonsuzdur."
                ),
                mathematician="cantor", year="1874",
                topic_slugs=["kumeler", "sonsuzluk"], fun_rating=4,
            ),
            MathFact(
                id="fact-11", title="Emmy Noether ve Modern Cebir",
                content=(
                    "Emmy Noether (1882-1935), soyut cebirin kurucusu olarak kabul "
                    "edilir. Einstein, onu 'matematige en onemli katki yapan kadin' "
                    "olarak tanimlamistir."
                ),
                mathematician="noether", year="1920",
                topic_slugs=["cebir", "fizik"], fun_rating=4,
            ),
            MathFact(
                id="fact-12", title="Altin Oran",
                content=(
                    "Altin oran (phi = 1.618...) antik Yunandan beri estetik ve "
                    "dogada gorulur. Parthenon tapinagi, Da Vincinin Vitruvius Adami "
                    "ve DNA sarmalinda bu oran bulunur."
                ),
                mathematician=None, year="M.O. 5. yuzyil",
                topic_slugs=["oranlar", "geometri", "doga"], fun_rating=5,
            ),
            MathFact(
                id="fact-13", title="Ramanujannin Dehasi",
                content=(
                    "Srinivasa Ramanujan, resmi egitim almadan 3000den fazla "
                    "matematiksel formul ve teorem uretmistir. Hardynin taxi "
                    "numarasi hikayesi meshurdur: 1729 = 1^3 + 12^3 = 9^3 + 10^3."
                ),
                mathematician="ramanujan", year="1913",
                topic_slugs=["sayi_teorisi", "diziler"], fun_rating=5,
            ),
            MathFact(
                id="fact-14", title="Fermatin Son Teoremi",
                content=(
                    "Pierre de Fermat 1637de 'n>2 icin x^n + y^n = z^n denkleminin "
                    "tam sayili cozumu yoktur' demis ve 358 yil boyunca kimse "
                    "ispatlayamamistir. Andrew Wiles 1995te basarmistir."
                ),
                mathematician="fermat", year="1637",
                topic_slugs=["sayi_teorisi", "cebir"], fun_rating=5,
            ),
            MathFact(
                id="fact-15", title="Turk Ucgeni (Pascal Ucgeni)",
                content=(
                    "Pascal ucgeni olarak bilinen sayi ucgeni, aslinda Omer Hayyam "
                    "ve Cinli matematikci Yang Hui tarafindan Pascaldan yuzlerce "
                    "yil once kesfedilmistir."
                ),
                mathematician="omer_hayyam", year="11. yuzyil",
                topic_slugs=["kombinatorik", "sayilar"], fun_rating=4,
            ),
            MathFact(
                id="fact-16", title="El-Biruni ve Dunyanin Capini Olcme",
                content=(
                    "El-Biruni (973-1048), bir dagin tepesinden bakis acisini "
                    "olcerek Dunyanin capini hesaplamistir. Sonucu modern "
                    "olcumlerden sadece %1 sapmistir."
                ),
                mathematician="biruni", year="1020",
                topic_slugs=["geometri", "trigonometri"], fun_rating=5,
            ),
            MathFact(
                id="fact-17", title="Sifirin Icadi",
                content=(
                    "Sifir sayisi ilk kez Hintli matematikci Brahmagupta tarafindan "
                    "628 yilinda bir sayi olarak tanimlanmistir. Roma rakamlari "
                    "sisteminde sifir yoktu, bu yuzden karmasik hesaplamalar cok zordu."
                ),
                mathematician="brahmagupta", year="628",
                topic_slugs=["aritmetik", "sayilar"], fun_rating=4,
            ),
            MathFact(
                id="fact-18", title="Maryam Mirzakhani",
                content=(
                    "Iranli matematikci Maryam Mirzakhani, 2014te Fields Madalyasi "
                    "kazanan ilk kadin olmustur. Riemann yuzeylerinin dinamigi "
                    "uzerine calismalariyla tanilir."
                ),
                mathematician="mirzakhani", year="2014",
                topic_slugs=["geometri", "topoloji"], fun_rating=4,
            ),
            MathFact(
                id="fact-19", title="Pi Gunu",
                content=(
                    "Her yil 14 Mart (3/14) Pi Gunu olarak kutlanir. Pi sayisi "
                    "(3.14159...) bir dairenin cevresinin capina orandir ve "
                    "irrasyonel bir sayidir - ondalik acilimi sonsuza kadar "
                    "devam eder, hic tekrar etmez."
                ),
                mathematician=None, year="Modern",
                topic_slugs=["geometri", "daire", "pi"], fun_rating=3,
            ),
            MathFact(
                id="fact-20", title="Nasireddin Tusi ve Trigonometri",
                content=(
                    "Nasireddin Tusi (1201-1274), trigonometriyi astronomiden "
                    "bagimsiz bir matematik dali olarak ilk kez ele alan bilgindir. "
                    "Sinusler kanununu da formule etmistir."
                ),
                mathematician="tusi", year="1260",
                topic_slugs=["trigonometri", "astronomi"], fun_rating=4,
            ),
            MathFact(
                id="fact-21", title="Negatif Sayilarin Kabulu",
                content=(
                    "Negatif sayilar ilk kez Cinde M.O. 200 yilinda kullanilmistir, "
                    "ancak Avrupada 17. yuzyila kadar 'sacma sayilar' olarak "
                    "gorulmusterdir."
                ),
                mathematician=None, year="M.O. 200",
                topic_slugs=["sayilar", "aritmetik"], fun_rating=3,
            ),
            MathFact(
                id="fact-22", title="Satranc Tahtasindaki Bugday",
                content=(
                    "Efsaneye gore satranci icat eden bilge, kraldan odul olarak "
                    "her kareye ikiyle katlanan bugday tanesi istemistir: "
                    "1+2+4+8+... = 2^64 - 1 = 18 kentilyon tane. Bu, ustel "
                    "buyumenin gucunu gosteren meshur ornektir."
                ),
                mathematician=None, year="6. yuzyil",
                topic_slugs=["uslu_sayilar", "diziler"], fun_rating=5,
            ),
        ]

    @staticmethod
    def _load_mathematicians() -> Dict[str, Mathematician]:
        mathematicians = [
            Mathematician(
                id="harizmi", name="El-Harizmi (Muhammed bin Musa)",
                birth_year="780", death_year="850",
                nationality="Harezmli (Ozbekistan)",
                biography=(
                    "Islam Altin Caginin en onemli matematikci ve astronomlarindan "
                    "biridir. Bagdattaki Beytul Hikmede calismistir."
                ),
                contributions=[
                    "Cebir biliminin temeli: Kitabul-Cebr vel-Mukabele",
                    "Hindu-Arap rakam sistemini Avrupaya tanitti",
                    "Algoritma kavraminin isim babasi",
                ],
                famous_quote="Bilgi, insanin en degerli hazinesidir.",
                related_topics=["cebir", "denklemler", "aritmetik"],
                fun_facts=[
                    "Cebir ve algoritma kelimelerinin her ikisi de onun adindan gelir.",
                    "Beytul Hikme (Bilgelik Evi) doneminin en buyuk arastirma merkeziydi.",
                ],
            ),
            Mathematician(
                id="pisagor", name="Pisagor (Pythagoras)",
                birth_year="M.O. 570", death_year="M.O. 495",
                nationality="Antik Yunan (Sisam Adasi)",
                biography=(
                    "Antik Yunanin en meshur matematikci ve filozoflarindan biridir. "
                    "Pisagorculuk okulunu kurmustur."
                ),
                contributions=[
                    "Pisagor teoremi: a^2 + b^2 = c^2",
                    "Muzik ve matematik arasindaki iliski",
                    "Sayi mistisizmi",
                ],
                famous_quote="Her sey sayidir.",
                related_topics=["geometri", "ucgenler", "sayilar"],
                fun_facts=[
                    "Pisagor, fasulye yemeyi reddederdi - nedenini kimse bilmiyor.",
                    "Pisagorculuk okulu gizli bir topluluktu.",
                ],
            ),
            Mathematician(
                id="cahit_arf", name="Cahit Arf",
                birth_year="1910", death_year="1997",
                nationality="Turk",
                biography=(
                    "Turkiyenin en buyuk matematikcisi olarak kabul edilir. "
                    "Selanik'te dogmus, Istanbul ve Gottingende egitim almistir."
                ),
                contributions=[
                    "Arf degismezi (kuadratik formlar)",
                    "Arf halkalari",
                    "Hasse-Arf teoremi",
                ],
                famous_quote="Matematikte gercek anlama, formullerin otesindedir.",
                related_topics=["cebir", "topoloji", "sayi_teorisi"],
                fun_facts=[
                    "Portresi Turk 10 lira banknotunun arkasinda yer almaktadir.",
                    "Gottingen Universitesinde Helmut Hasse ile calismistir.",
                ],
            ),
            Mathematician(
                id="omer_hayyam", name="Omer Hayyam",
                birth_year="1048", death_year="1131",
                nationality="Selcuklu (Iran)",
                biography=(
                    "Matematikci, astronom, filozof ve sair. Rubailer ile edebiyat "
                    "dunyasinda da cok unludur."
                ),
                contributions=[
                    "Kup denklemlerin geometrik cozumu",
                    "Hayyam takvimi (Gregory'den daha dogru)",
                    "Pascal ucgeninin erken kesfedicisi",
                ],
                famous_quote="Bir kadeh sarap, bir kitap ve sen - cennet budur.",
                related_topics=["cebir", "geometri", "denklemler"],
                fun_facts=[
                    "Hayyam takvimi 5000 yilda sadece 1 gun sapar.",
                    "Rubailer 19. yuzyilda Bati'da Edward FitzGerald cevirisiyle unlu oldu.",
                ],
            ),
            Mathematician(
                id="euler", name="Leonhard Euler",
                birth_year="1707", death_year="1783",
                nationality="Isvicre",
                biography=(
                    "Tarihte en verimli matematikci olarak kabul edilir. "
                    "800den fazla makale ve kitap yazmistir."
                ),
                contributions=[
                    "Euler formulu: e^(ix) = cos(x) + i*sin(x)",
                    "Graf teorisinin temeli",
                    "Modern matematik notasyonu (f(x), e, pi, i, sigma)",
                ],
                famous_quote="Matematikte okumak, yazmak kadar onemlidir.",
                related_topics=["analiz", "graf_teorisi", "sayi_teorisi"],
                fun_facts=[
                    "Hayatinin son 17 yilini kor olarak gecirmis ama uretkenligini kaybetmemistir.",
                    "Bir gunun buyuk bolumunu matematik yaparak gecirirdi.",
                ],
            ),
            Mathematician(
                id="gauss", name="Carl Friedrich Gauss",
                birth_year="1777", death_year="1855",
                nationality="Alman",
                biography=(
                    "Matematik Prensi olarak bilinir. Sayi teorisi, istatistik, "
                    "analiz ve geometriye muazzam katkilar yapmistir."
                ),
                contributions=[
                    "Asal Sayilar Teoremi",
                    "Gauss eleminasyonu",
                    "Normal dagilim (can egrisi)",
                    "Disquisitiones Arithmeticae",
                ],
                famous_quote="Matematik bilimlerin kralicesidir.",
                related_topics=["sayi_teorisi", "istatistik", "cebir"],
                fun_facts=[
                    "10 yasinda 1den 100e toplam soruldu, saniyeler icinde 5050 dedi.",
                    "Kesiflerini yayinlamakta cok yavas davranirdi.",
                ],
            ),
            Mathematician(
                id="arsimed", name="Arsimet (Archimedes)",
                birth_year="M.O. 287", death_year="M.O. 212",
                nationality="Antik Yunan (Sirakuza)",
                biography=(
                    "Antik cagin en buyuk bilim insanlarindan biridir. Matematik, "
                    "fizik ve muhendislikte devrimci buluslar yapmistir."
                ),
                contributions=[
                    "Pi sayisinin hesaplanmasi",
                    "Kurenin hacim ve alan formulleri",
                    "Kaldirma kuvveti (Arsimet prensibi)",
                ],
                famous_quote="Bana bir kaldungac noktasi verin, dunyayi yerinden oynatayim.",
                related_topics=["geometri", "fizik", "pi"],
                fun_facts=[
                    "Eureka! diye bagirarak cirilciplak sokaga firdigi soylenir.",
                    "Roma askerinin kilicindan bile matematik problemini birakamadi.",
                ],
            ),
            Mathematician(
                id="tusi", name="Nasireddin Tusi",
                birth_year="1201", death_year="1274",
                nationality="Selcuklu (Iran)",
                biography=(
                    "Meraga Rasathanesinin kurucusu ve muduru. Matematik ve "
                    "astronomide doneminin en etkili bilginidir."
                ),
                contributions=[
                    "Trigonometriyi bagimsiz bir dal olarak kurmasi",
                    "Tusi cifti kavrami",
                    "Meraga Rasathanesi ve kutuphane",
                ],
                famous_quote="Bilim, karanligi aydinlatan isiktir.",
                related_topics=["trigonometri", "astronomi"],
                fun_facts=[
                    "Meraga Rasathanesinde 400.000 ciltlik kutuphane kurmustur.",
                    "Tusi cifti, Kopernike ilham vermis olabilir.",
                ],
            ),
            Mathematician(
                id="ali_kuscu", name="Ali Kuscu",
                birth_year="1403", death_year="1474",
                nationality="Osmanli (Semerkant dogumlu)",
                biography=(
                    "Ulug Beyin ogrencisi olan Ali Kuscu, Istanbulun fethinden "
                    "sonra Fatih Sultan Mehmetin davetlisi olarak Istanbula gelmistir."
                ),
                contributions=[
                    "Trigonometrik fonksiyonlarin sistematik incelenmesi",
                    "Astronomi hesaplari ve gozlemleri",
                ],
                famous_quote=None,
                related_topics=["trigonometri", "astronomi"],
                fun_facts=[
                    "Fatih Sultan Mehmet gunluk 200 akce maas baglamistir.",
                    "Ay kraterleri arasinda onun adini tasiyan bir krater vardir.",
                ],
            ),
            Mathematician(
                id="ramanujan", name="Srinivasa Ramanujan",
                birth_year="1887", death_year="1920",
                nationality="Hint",
                biography=(
                    "Resmi matematik egitimi almadan dahi seviyesinde eserler "
                    "uretmis nadir matematikcilardan biridir."
                ),
                contributions=[
                    "Sonsuz serilere katkilar",
                    "Surekli kesirler",
                    "Sayi teorisi (bolum fonksiyonu)",
                ],
                famous_quote="Bir formul bana bir sey anlatmiyorsa, benim icin degersizdir.",
                related_topics=["sayi_teorisi", "diziler", "analiz"],
                fun_facts=[
                    "1729 sayisi 'Ramanujan sayisi' olarak anilir.",
                    "Cambridge'e goturulen defterlerinde binlerce ispatsiz teorem vardi.",
                ],
            ),
        ]
        return {m.id: m for m in mathematicians}


# ---------------------------------------------------------------------------
# MathPuzzleService
# ---------------------------------------------------------------------------

class MathPuzzleService:
    """Gunluk matematik bulmacalari ve mantik sorulari servisi."""

    def __init__(self) -> None:
        self._puzzles: List[Puzzle] = self._load_puzzles()
        self._attempts: Dict[str, List[PuzzleAttempt]] = {}  # user_id -> attempts

    def get_daily_puzzle(self, reference_date: Optional[date] = None) -> Puzzle:
        """Gunun bulmacasini dondurur (tarih bazli deterministik)."""
        today = reference_date or date.today()
        index = today.toordinal() % len(self._puzzles)
        return self._puzzles[index]

    def get_puzzle_by_id(self, puzzle_id: str) -> Optional[Puzzle]:
        """ID ile bulmaca getirir."""
        for p in self._puzzles:
            if p.id == puzzle_id:
                return p
        return None

    def check_puzzle_answer(self, puzzle_id: str, answer: str) -> Dict[str, Any]:
        """Bulmaca cevabini kontrol eder."""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if puzzle is None:
            return {"found": False, "correct": False, "message": "Bulmaca bulunamadi."}
        is_correct = answer.strip().lower() == puzzle.answer.strip().lower()
        return {
            "found": True,
            "correct": is_correct,
            "message": "Tebrikler! Dogru cevap!" if is_correct else "Yanlis cevap. Tekrar dene!",
            "explanation": puzzle.explanation if is_correct else None,
        }

    def get_puzzle_hint(self, puzzle_id: str, hint_index: int = 0) -> Optional[str]:
        """Bulmaca ipucu dondurur."""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if puzzle is None or not puzzle.hints:
            return None
        idx = min(hint_index, len(puzzle.hints) - 1)
        return puzzle.hints[idx]

    def get_all_puzzles(self) -> List[Puzzle]:
        """Tum bulmacalari dondurur."""
        return list(self._puzzles)

    @staticmethod
    def _load_puzzles() -> List[Puzzle]:
        return [
            Puzzle(id="puz-01", title="Sayi Dizisi",
                   description="Bu dizinin bir sonraki sayisini bulun: 2, 6, 12, 20, 30, ?",
                   difficulty=DifficultyLevel.EASY, answer="42",
                   hints=["Her adimda fark artmaktadir.", "Farklar: 4, 6, 8, 10, ..."],
                   explanation="Farklar 4, 6, 8, 10, 12. Yani 30 + 12 = 42.",
                   category="sequence", points=10),
            Puzzle(id="puz-02", title="Fibonacci Devam",
                   description="Bu dizinin sonraki sayisi: 1, 1, 2, 3, 5, 8, 13, ?",
                   difficulty=DifficultyLevel.EASY, answer="21",
                   hints=["Her sayi onceki iki sayinin toplamidir."],
                   explanation="8 + 13 = 21 (Fibonacci dizisi).",
                   category="sequence", points=10),
            Puzzle(id="puz-03", title="Geometrik Dizi",
                   description="Sonraki sayiyi bulun: 3, 9, 27, 81, ?",
                   difficulty=DifficultyLevel.EASY, answer="243",
                   hints=["Her sayi bir oncekinin kac kati?"],
                   explanation="Geometrik dizi, oran = 3. 81 x 3 = 243.",
                   category="sequence", points=10),
            Puzzle(id="puz-04", title="Saat Bulmacasi",
                   description="Bir saat 12:00 icin 12 kez vuruyor. 6 vurus arasi 5 saniye ise 6:00 icin toplam kac saniye surer?",
                   difficulty=DifficultyLevel.MEDIUM, answer="25",
                   hints=["Vurus sayisi ile aralik sayisini karistirmayin."],
                   explanation="6 vurus = 5 aralik. 5 x 5 = 25 saniye.",
                   category="logic", points=20),
            Puzzle(id="puz-05", title="Satranc Kareleri",
                   description="8x8 satranc tahtasinda (1x1, 2x2, ... 8x8) toplam kac kare var?",
                   difficulty=DifficultyLevel.HARD, answer="204",
                   hints=["Sadece 1x1 degil, buyuk kareleri de sayin.", "n^2 lerin toplami."],
                   explanation="64+49+36+25+16+9+4+1 = 204.",
                   category="pattern", points=30),
            Puzzle(id="puz-06", title="Havuz Problemi",
                   description="A muslugu havuzu 6 saatte, B muslugu 3 saatte dolduruyor. Ikisi birlikte kac saatte doldurur?",
                   difficulty=DifficultyLevel.MEDIUM, answer="2",
                   hints=["Her muslugun saatlik is oranini hesaplayin."],
                   explanation="1/6 + 1/3 = 1/6 + 2/6 = 3/6 = 1/2. Yani 2 saat.",
                   category="logic", points=20),
            Puzzle(id="puz-07", title="Asal Sayilar",
                   description="2 ile 20 arasinda kac tane asal sayi vardir?",
                   difficulty=DifficultyLevel.EASY, answer="8",
                   hints=["Asal sayi: sadece 1e ve kendisine bolunen."],
                   explanation="2, 3, 5, 7, 11, 13, 17, 19 = 8 asal sayi.",
                   category="pattern", points=10),
            Puzzle(id="puz-08", title="Otobus Tuzagi",
                   description="Bos otobus: 1. durak +7, 2. durak -3 +5, 3. durak -2. Kac duraktan gecti?",
                   difficulty=DifficultyLevel.EASY, answer="3",
                   hints=["Soruyu tekrar oku - ne soruluyor?"],
                   explanation="Soru kisi degil durak sayisini soruyor: 3.",
                   category="trick", points=15),
            Puzzle(id="puz-09", title="Kibrit Ucgenleri",
                   description="6 kibritle 4 eskenar ucgen yapabilir misiniz?",
                   difficulty=DifficultyLevel.HARD, answer="Evet, ucgen piramit (tetrahedron)",
                   hints=["2 boyutta dusunmeyin.", "3 boyutu deneyin."],
                   explanation="Tetrahedron: 6 kenar, 4 eskenar ucgen yuz.",
                   category="logic", points=30),
            Puzzle(id="puz-10", title="Tam Kareler",
                   description="1'den 100'e kadar (dahil) kac tam kare sayi var?",
                   difficulty=DifficultyLevel.EASY, answer="10",
                   hints=["1, 4, 9, 16, ... seklinde sayin."],
                   explanation="1^2=1, 2^2=4, ..., 10^2=100. Toplam 10.",
                   category="pattern", points=10),
            Puzzle(id="puz-11", title="Carpim Sifirlari",
                   description="10! (10 faktoriyel) kac sifirla biter?",
                   difficulty=DifficultyLevel.MEDIUM, answer="2",
                   hints=["Sifir = 2 x 5 carpimi."],
                   explanation="10! = 3628800. 5 ve 10 birer 5 faktoru verir: 2 sifir.",
                   category="pattern", points=20),
            Puzzle(id="puz-12", title="Hiz Problemi",
                   description="60 km/s hizla giden tren 300 km yolu kac saatte alir?",
                   difficulty=DifficultyLevel.EASY, answer="5",
                   hints=["Yol = Hiz x Zaman."],
                   explanation="300 / 60 = 5 saat.",
                   category="logic", points=10),
            Puzzle(id="puz-13", title="Yas Bulmacasi",
                   description="Annesi ogrenciden 24 yas buyuk. 6 yil sonra annesi ogrencinin 3 kati yasinda olacak. Ogrenci kac yasinda?",
                   difficulty=DifficultyLevel.MEDIUM, answer="6",
                   hints=["Ogrencinin yasi x olsun.", "6 yil sonra: x+24+6 = 3(x+6)"],
                   explanation="x+30 = 3x+18 -> 2x=12 -> x=6.",
                   category="logic", points=20),
            Puzzle(id="puz-14", title="Para Paylasimi",
                   description="120 TL 3 kisiye 1:2:3 oraninda paylasilacak. En az pay kac TL?",
                   difficulty=DifficultyLevel.EASY, answer="20",
                   hints=["1+2+3 = 6 pay."],
                   explanation="120/6 = 20 TL (en kucuk pay).",
                   category="logic", points=10),
            Puzzle(id="puz-15", title="Kup Ozellikleri",
                   description="Bir kupun kac yuzeyi, kenari ve kosesi vardir? (yuz-kenar-kose)",
                   difficulty=DifficultyLevel.EASY, answer="6-12-8",
                   hints=["Bir zarla dusunun.", "Euler: Y - K + Ko = 2"],
                   explanation="6 yuz, 12 kenar, 8 kose. Euler: 6-12+8=2.",
                   category="pattern", points=10),
            Puzzle(id="puz-16", title="Sayisal Tuzak",
                   description="0.1 + 0.2 tam olarak 0.3 eder mi?",
                   difficulty=DifficultyLevel.HARD, answer="Hayir",
                   hints=["Bilgisayarlarda ondalik sayilarin gosterimi sinirlidir."],
                   explanation="IEEE 754 floating point: 0.1+0.2 = 0.30000000000000004. Kayan noktali aritmetik.",
                   category="trick", points=25),
        ]


# ---------------------------------------------------------------------------
# CertificateService
# ---------------------------------------------------------------------------

class CertificateService:
    """Basari sertifikalari olusturma ve yonetim servisi."""

    def __init__(self) -> None:
        self._certificates: Dict[str, List[Certificate]] = {}  # user_id -> certs

    def generate_certificate(
        self,
        user_id: str,
        topic: str,
        mastery: float,
    ) -> Certificate:
        """Konu hakimiyetine gore sertifika olusturur."""
        if mastery >= 0.9:
            level = MasteryLevel.MASTER
            level_text = "Usta"
        elif mastery >= 0.7:
            level = MasteryLevel.ADVANCED
            level_text = "Ileri"
        elif mastery >= 0.5:
            level = MasteryLevel.INTERMEDIATE
            level_text = "Orta"
        else:
            level = MasteryLevel.BEGINNER
            level_text = "Baslangic"

        topic_display = topic.replace("_", " ").title()
        code = hashlib.md5(f"{user_id}:{topic}:{mastery}".encode()).hexdigest()[:10].upper()

        cert = Certificate(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=f"{topic_display} - {level_text} Seviye Sertifikasi",
            description=(
                f"Bu sertifika, {topic_display} konusunda "
                f"%{int(mastery * 100)} basari oranina ulastiginizi belgeler."
            ),
            topic_slug=topic,
            mastery_level=level,
            certificate_code=code,
        )
        self._certificates.setdefault(user_id, []).append(cert)
        return cert

    def get_user_certificates(self, user_id: str) -> List[Certificate]:
        """Kullanicinin tum sertifikalarini dondurur."""
        return self._certificates.get(user_id, [])


# ---------------------------------------------------------------------------
# SeasonalContentService
# ---------------------------------------------------------------------------

class SeasonalContentService:
    """Mevsimsel ve tatil icerik servisi."""

    _SEASONS = {
        Season.SPRING: {"months": [3, 4, 5], "theme": "Sinav Hazirlik Donemi",
                        "primary": "#4CAF50", "secondary": "#81C784", "icon": "cicek"},
        Season.SUMMER: {"months": [6, 7, 8], "theme": "Yaz Okulu",
                        "primary": "#FF9800", "secondary": "#FFB74D", "icon": "gunes"},
        Season.AUTUMN: {"months": [9, 10, 11], "theme": "Okul Baslangici",
                        "primary": "#FF5722", "secondary": "#FF8A65", "icon": "yaprak"},
        Season.WINTER: {"months": [12, 1, 2], "theme": "Kis Tatili Calisma Kampi",
                        "primary": "#2196F3", "secondary": "#64B5F6", "icon": "kar"},
    }

    _HOLIDAYS: List[HolidayContent] = [
        HolidayContent(
            id="h-23nisan", holiday_name="23 Nisan Ulusal Egemenlik ve Cocuk Bayrami",
            description="TBMM'nin acilisi ve cocuklara armagan edilen bayram.",
            date_month=4, date_day=23,
            challenges=[
                {"title": "Cocuk Sampiyonu", "description": "23 soru coz, ozel rozet kazan!", "xp": 230},
                {"title": "Egemenlik Sayilari", "description": "1920 ile 2024 arasi asal sayilari bul.", "xp": 150},
            ],
            fun_facts=["TBMM 23 Nisan 1920de acildi.", "Ataturk bu gunu cocuklara armagan etti."],
            greeting="23 Nisan Ulusal Egemenlik ve Cocuk Bayraminiz kutlu olsun!",
        ),
        HolidayContent(
            id="h-19mayis", holiday_name="19 Mayis Ataturku Anma, Genclik ve Spor Bayrami",
            description="Ataturkun Samsuna cikisi ve genclere armagan.",
            date_month=5, date_day=19,
            challenges=[
                {"title": "Genclik Maratonu", "description": "19 dakikada en cok soru coz!", "xp": 190},
                {"title": "1919 Bolen Bulmacasi", "description": "1919 sayisinin tum bolenlerini bul.", "xp": 100},
            ],
            fun_facts=["Ataturk 19 Mayis 1919da Samsuna cikti.", "1919 = 19 x 101 (iki asal carpimi)."],
            greeting="19 Mayis Genclik ve Spor Bayraminiz kutlu olsun!",
        ),
        HolidayContent(
            id="h-29ekim", holiday_name="29 Ekim Cumhuriyet Bayrami",
            description="Turkiye Cumhuriyetinin ilani.",
            date_month=10, date_day=29,
            challenges=[
                {"title": "Cumhuriyet Sinavi", "description": "29 soruluk ozel sinav!", "xp": 290},
                {"title": "100. Yil Matematik", "description": "Cumhuriyetin 100. yili matematik problemleri.", "xp": 200},
            ],
            fun_facts=["Cumhuriyet 29 Ekim 1923te ilan edildi.", "29 bir asal sayidir."],
            greeting="Cumhuriyet Bayraminiz kutlu olsun!",
        ),
        HolidayContent(
            id="h-ramazan", holiday_name="Ramazan Bayrami",
            description="Ramazan ayinin bitisini kutlayan bayram.",
            date_month=0, date_day=0, is_variable_date=True,
            challenges=[
                {"title": "Bayram Hediyesi", "description": "3 gun 10 soru coz, sertifika kazan!", "xp": 300},
            ],
            fun_facts=["Ramazan Bayrami 3 gun surer."],
            greeting="Ramazan Bayraminiz mubarek olsun!",
        ),
        HolidayContent(
            id="h-kurban", holiday_name="Kurban Bayrami",
            description="Islamin en onemli bayramlarindan biri.",
            date_month=0, date_day=0, is_variable_date=True,
            challenges=[
                {"title": "Paylasim Matematigi", "description": "Oran-oranli paylasim problemleri coz!", "xp": 250},
            ],
            fun_facts=["Kurban Bayrami 4 gun surer."],
            greeting="Kurban Bayraminiz mubarek olsun!",
        ),
    ]

    def get_current_season(self) -> Dict[str, Any]:
        """Mevcut mevsimi ve temasini dondurur."""
        month = date.today().month
        for season, info in self._SEASONS.items():
            if month in info["months"]:
                return {
                    "season": season.value,
                    "theme": info["theme"],
                    "color_primary": info["primary"],
                    "color_secondary": info["secondary"],
                    "icon": info["icon"],
                    "month": month,
                }
        return {"season": "unknown", "theme": "Genel", "icon": "", "month": month}

    def get_seasonal_challenges(self) -> List[Dict[str, Any]]:
        """Mevcut mevsim ve tatillere ozel gorevleri dondurur."""
        month = date.today().month
        day = date.today().day
        challenges: List[Dict[str, Any]] = []

        # Mevsimsel gorev
        for season, info in self._SEASONS.items():
            if month in info["months"]:
                challenges.append({
                    "challenge_id": f"season_{season.value}",
                    "title": f"{info['theme']} Gorevi",
                    "description": f"Bu donem icin ozel matematik gorevleri.",
                    "season": season.value,
                    "xp_reward": 100,
                })

        # Tatil gorevleri
        for holiday in self._HOLIDAYS:
            if holiday.date_month == month and (holiday.date_day == day or abs(holiday.date_day - day) <= 3):
                for ch in holiday.challenges:
                    challenges.append({
                        "challenge_id": f"holiday_{holiday.id}",
                        "title": ch["title"],
                        "description": ch["description"],
                        "holiday": holiday.holiday_name,
                        "xp_reward": ch["xp"],
                    })

        return challenges

    def get_holiday_content(self, holiday_id: str) -> Optional[Dict[str, Any]]:
        """Belirli bir tatil icerigini dondurur."""
        for h in self._HOLIDAYS:
            if h.id == holiday_id:
                return h.to_dict()
        return None

    def get_all_holidays(self) -> List[Dict[str, Any]]:
        """Tum tatil iceriklerini dondurur."""
        return [h.to_dict() for h in self._HOLIDAYS]


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

math_history_service = MathHistoryService()
math_puzzle_service = MathPuzzleService()
certificate_service = CertificateService()
seasonal_content_service = SeasonalContentService()
