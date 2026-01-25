"""
Story Themes for AI-Generated Word Problems.

Provides diverse, engaging themes for transforming abstract math
problems into contextual word problems. Themes are culturally
appropriate and age-relevant for K-12 students.

Features:
- 15+ theme categories
- Turkish cultural context
- Age-appropriate content
- Seasonal/holiday variations
- Gender-balanced names
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import random


class ThemeCategory(str, Enum):
    """Categories of story themes."""
    SPORTS = "sports"
    ANIMALS = "animals"
    FOOD = "food"
    SPACE = "space"
    NATURE = "nature"
    SCHOOL = "school"
    SHOPPING = "shopping"
    TRAVEL = "travel"
    GAMES = "games"
    TECHNOLOGY = "technology"
    MUSIC = "music"
    ART = "art"
    COOKING = "cooking"
    GARDENING = "gardening"
    CONSTRUCTION = "construction"
    TURKISH_CULTURE = "turkish_culture"


@dataclass
class StoryTheme:
    """A story theme with context and vocabulary."""
    category: ThemeCategory
    name: str
    name_tr: str
    description: str
    description_tr: str
    characters: List[str]
    characters_tr: List[str]
    settings: List[str]
    settings_tr: List[str]
    objects: List[str]
    objects_tr: List[str]
    verbs: List[str]
    verbs_tr: List[str]
    units: List[str]
    units_tr: List[str]
    grade_range: tuple  # (min_grade, max_grade)

    def get_random_character(self, gender: Optional[str] = None) -> tuple:
        """Get random character name (English, Turkish)."""
        idx = random.randint(0, len(self.characters) - 1)
        return self.characters[idx], self.characters_tr[idx]

    def get_random_setting(self) -> tuple:
        """Get random setting (English, Turkish)."""
        idx = random.randint(0, len(self.settings) - 1)
        return self.settings[idx], self.settings_tr[idx]

    def get_random_object(self) -> tuple:
        """Get random object (English, Turkish)."""
        idx = random.randint(0, len(self.objects) - 1)
        return self.objects[idx], self.objects_tr[idx]


# Turkish names (gender-balanced)
TURKISH_NAMES_MALE = ["Ali", "Mehmet", "Ahmet", "Mustafa", "Emre", "Burak", "Can", "Deniz", "Ege", "Kaan"]
TURKISH_NAMES_FEMALE = ["Ayse", "Fatma", "Zeynep", "Elif", "Seda", "Merve", "Ebru", "Ceren", "Defne", "Ela"]
TURKISH_NAMES_NEUTRAL = ["Deniz", "Ege", "Duru", "Evren", "Ilgaz", "Kutay"]

# All themes
STORY_THEMES: List[StoryTheme] = [
    # SPORTS
    StoryTheme(
        category=ThemeCategory.SPORTS,
        name="Soccer",
        name_tr="Futbol",
        description="Soccer matches and training",
        description_tr="Futbol maclari ve antrenmanlar",
        characters=["the goalkeeper", "the striker", "the coach", "the team captain"],
        characters_tr=["kaleci", "forvet", "antrenor", "takim kaptani"],
        settings=["the stadium", "the training field", "the locker room"],
        settings_tr=["stadyum", "antrenman sahasi", "soyunma odasi"],
        objects=["soccer balls", "goals", "jerseys", "water bottles", "cones"],
        objects_tr=["futbol toplari", "goller", "formalar", "su siseleri", "kulahlar"],
        verbs=["kicked", "scored", "passed", "saved", "trained"],
        verbs_tr=["vurdu", "atti", "pasladi", "kurtardi", "antreman yapti"],
        units=["goals", "points", "players", "minutes", "meters"],
        units_tr=["gol", "puan", "oyuncu", "dakika", "metre"],
        grade_range=(3, 12),
    ),
    StoryTheme(
        category=ThemeCategory.SPORTS,
        name="Basketball",
        name_tr="Basketbol",
        description="Basketball games and practice",
        description_tr="Basketbol maclari ve pratik",
        characters=["the point guard", "the center", "the coach"],
        characters_tr=["oyun kurucu", "pivot", "antrenor"],
        settings=["the basketball court", "the gym", "the sports hall"],
        settings_tr=["basketbol sahasi", "spor salonu", "spor salonu"],
        objects=["basketballs", "hoops", "sneakers", "scoreboards"],
        objects_tr=["basketbol toplari", "potalar", "spor ayakkabilar", "skor tablosu"],
        verbs=["shot", "dribbled", "blocked", "dunked", "passed"],
        verbs_tr=["atti", "dribling yapti", "blokladi", "smaç yapti", "pasladi"],
        units=["points", "baskets", "rebounds", "assists"],
        units_tr=["sayi", "basket", "ribaund", "asist"],
        grade_range=(3, 12),
    ),

    # ANIMALS
    StoryTheme(
        category=ThemeCategory.ANIMALS,
        name="Farm Animals",
        name_tr="Ciftlik Hayvanlari",
        description="Life on the farm",
        description_tr="Ciftlik hayati",
        characters=["the farmer", "the veterinarian"],
        characters_tr=["ciftci", "veteriner"],
        settings=["the farm", "the barn", "the pasture", "the chicken coop"],
        settings_tr=["ciftlik", "ahir", "mera", "tavuk kumesi"],
        objects=["cows", "chickens", "eggs", "sheep", "horses", "pigs"],
        objects_tr=["inekler", "tavuklar", "yumurtalar", "koyunlar", "atlar", "domuzlar"],
        verbs=["fed", "collected", "milked", "herded", "counted"],
        verbs_tr=["besledi", "topladi", "sagdi", "guduledi", "saydi"],
        units=["eggs", "liters of milk", "animals", "bales of hay"],
        units_tr=["yumurta", "litre sut", "hayvan", "saman balyasi"],
        grade_range=(1, 6),
    ),
    StoryTheme(
        category=ThemeCategory.ANIMALS,
        name="Zoo",
        name_tr="Hayvanat Bahcesi",
        description="Visiting the zoo",
        description_tr="Hayvanat bahcesi ziyareti",
        characters=["the zookeeper", "the visitor", "the guide"],
        characters_tr=["hayvanat bahcesi bakicisi", "ziyaretci", "rehber"],
        settings=["the zoo", "the aquarium", "the safari park"],
        settings_tr=["hayvanat bahcesi", "akvaryum", "safari parki"],
        objects=["lions", "elephants", "monkeys", "penguins", "giraffes"],
        objects_tr=["aslanlar", "filler", "maymunlar", "penguenler", "zurafalar"],
        verbs=["observed", "fed", "photographed", "counted"],
        verbs_tr=["gozlemledi", "besledi", "fotografladi", "saydi"],
        units=["animals", "enclosures", "visitors", "tickets"],
        units_tr=["hayvan", "kafes", "ziyaretci", "bilet"],
        grade_range=(1, 8),
    ),

    # FOOD & COOKING
    StoryTheme(
        category=ThemeCategory.COOKING,
        name="Bakery",
        name_tr="Pastane",
        description="Baking and pastry",
        description_tr="Firinci ve pastaci",
        characters=["the baker", "the pastry chef", "the customer"],
        characters_tr=["firinci", "pasta sefi", "musteri"],
        settings=["the bakery", "the kitchen", "the cafe"],
        settings_tr=["firina", "mutfak", "kafe"],
        objects=["cakes", "cookies", "bread loaves", "croissants", "muffins"],
        objects_tr=["pastalar", "kurabiyeler", "ekmekler", "kruvasanlar", "muffinler"],
        verbs=["baked", "decorated", "sold", "mixed", "measured"],
        verbs_tr=["pisirdi", "susledi", "satti", "karistirdi", "olctu"],
        units=["pieces", "kilograms", "grams", "dozens", "trays"],
        units_tr=["parca", "kilogram", "gram", "duzine", "tepsi"],
        grade_range=(2, 8),
    ),
    StoryTheme(
        category=ThemeCategory.FOOD,
        name="Restaurant",
        name_tr="Restoran",
        description="Dining and serving",
        description_tr="Yemek ve servis",
        characters=["the chef", "the waiter", "the customer"],
        characters_tr=["sef", "garson", "musteri"],
        settings=["the restaurant", "the kitchen", "the dining room"],
        settings_tr=["restoran", "mutfak", "yemek salonu"],
        objects=["plates", "meals", "drinks", "tables", "menus"],
        objects_tr=["tabaklar", "yemekler", "icecekler", "masalar", "menuler"],
        verbs=["served", "ordered", "cooked", "paid", "tipped"],
        verbs_tr=["servis etti", "siparis verdi", "pisirdi", "odedi", "bahsis verdi"],
        units=["plates", "lira", "customers", "tables"],
        units_tr=["porsiyon", "lira", "musteri", "masa"],
        grade_range=(3, 9),
    ),

    # SPACE
    StoryTheme(
        category=ThemeCategory.SPACE,
        name="Space Exploration",
        name_tr="Uzay Keşfi",
        description="Astronauts and space missions",
        description_tr="Astronotlar ve uzay gorevleri",
        characters=["the astronaut", "the mission controller", "the scientist"],
        characters_tr=["astronot", "gorev kontroloru", "bilim insani"],
        settings=["the space station", "the rocket", "mission control", "the moon"],
        settings_tr=["uzay istasyonu", "roket", "gorev kontrolu", "ay"],
        objects=["satellites", "rockets", "space suits", "planets", "stars"],
        objects_tr=["uydular", "roketler", "uzay kiyafetleri", "gezegenler", "yildizlar"],
        verbs=["launched", "orbited", "discovered", "transmitted", "landed"],
        verbs_tr=["firlatildi", "yorungeye girdi", "kesfetti", "iletti", "inis yapti"],
        units=["kilometers", "light-years", "days", "astronauts", "satellites"],
        units_tr=["kilometre", "isik yili", "gun", "astronot", "uydu"],
        grade_range=(4, 12),
    ),

    # NATURE
    StoryTheme(
        category=ThemeCategory.NATURE,
        name="Garden",
        name_tr="Bahce",
        description="Gardening and plants",
        description_tr="Bahcecilik ve bitkiler",
        characters=["the gardener", "the botanist"],
        characters_tr=["bahcivan", "botanikci"],
        settings=["the garden", "the greenhouse", "the park"],
        settings_tr=["bahce", "sera", "park"],
        objects=["flowers", "trees", "seeds", "vegetables", "fruits"],
        objects_tr=["cicekler", "agaclar", "tohumlar", "sebzeler", "meyveler"],
        verbs=["planted", "watered", "harvested", "grew", "picked"],
        verbs_tr=["dikti", "suladi", "hasat etti", "yetistirdi", "topladi"],
        units=["plants", "seeds", "rows", "kilograms", "liters"],
        units_tr=["bitki", "tohum", "sira", "kilogram", "litre"],
        grade_range=(1, 7),
    ),

    # SCHOOL
    StoryTheme(
        category=ThemeCategory.SCHOOL,
        name="Classroom",
        name_tr="Sinif",
        description="School activities",
        description_tr="Okul aktiviteleri",
        characters=["the teacher", "the student", "the principal"],
        characters_tr=["ogretmen", "ogrenci", "mudur"],
        settings=["the classroom", "the library", "the cafeteria", "the playground"],
        settings_tr=["sinif", "kutuphane", "yemekhane", "oyun alani"],
        objects=["books", "pencils", "notebooks", "desks", "computers"],
        objects_tr=["kitaplar", "kalemler", "defterler", "siralar", "bilgisayarlar"],
        verbs=["studied", "read", "wrote", "calculated", "presented"],
        verbs_tr=["calisti", "okudu", "yazdi", "hesapladi", "sundu"],
        units=["students", "books", "pages", "points", "minutes"],
        units_tr=["ogrenci", "kitap", "sayfa", "puan", "dakika"],
        grade_range=(1, 12),
    ),

    # SHOPPING
    StoryTheme(
        category=ThemeCategory.SHOPPING,
        name="Market",
        name_tr="Market",
        description="Shopping and buying",
        description_tr="Alisveris",
        characters=["the shopper", "the cashier", "the store manager"],
        characters_tr=["alici", "kasiyer", "magaza muduru"],
        settings=["the supermarket", "the mall", "the corner store"],
        settings_tr=["supermarket", "alisveris merkezi", "bakkal"],
        objects=["apples", "oranges", "bread", "milk", "chocolate"],
        objects_tr=["elmalar", "portakallar", "ekmek", "sut", "cikolata"],
        verbs=["bought", "paid", "counted", "weighed", "selected"],
        verbs_tr=["satin aldi", "odedi", "saydi", "tarti", "secti"],
        units=["lira", "items", "kilograms", "pieces", "bags"],
        units_tr=["lira", "urun", "kilogram", "adet", "poset"],
        grade_range=(1, 9),
    ),

    # GAMES
    StoryTheme(
        category=ThemeCategory.GAMES,
        name="Video Games",
        name_tr="Video Oyunlari",
        description="Gaming and points",
        description_tr="Oyun ve puanlar",
        characters=["the gamer", "the character", "the opponent"],
        characters_tr=["oyuncu", "karakter", "rakip"],
        settings=["the game world", "the arena", "the level"],
        settings_tr=["oyun dunyasi", "arena", "bolum"],
        objects=["coins", "gems", "power-ups", "lives", "treasures"],
        objects_tr=["altinlar", "taslar", "guc-uplari", "canlar", "hazineler"],
        verbs=["collected", "earned", "defeated", "completed", "unlocked"],
        verbs_tr=["topladi", "kazandi", "yendi", "tamamladi", "actı"],
        units=["points", "coins", "levels", "lives", "stars"],
        units_tr=["puan", "altin", "bolum", "can", "yildiz"],
        grade_range=(2, 10),
    ),

    # TURKISH CULTURE
    StoryTheme(
        category=ThemeCategory.TURKISH_CULTURE,
        name="Turkish Bazaar",
        name_tr="Turk Carsisi",
        description="Traditional Turkish marketplace",
        description_tr="Geleneksel Turk pazari",
        characters=["the merchant", "the customer", "the tea seller"],
        characters_tr=["esnaf", "musteri", "cayci"],
        settings=["the Grand Bazaar", "the spice market", "the carpet shop"],
        settings_tr=["Kapali Carsi", "Misir Carsisi", "hali dukkani"],
        objects=["Turkish delight", "carpets", "lamps", "spices", "tea glasses"],
        objects_tr=["lokum", "halilar", "lambalar", "baharatlar", "cay bardaklari"],
        verbs=["bargained", "sold", "displayed", "measured", "wrapped"],
        verbs_tr=["pazarlik yapti", "satti", "sergiledi", "olctu", "paketledi"],
        units=["lira", "kilograms", "pieces", "boxes", "glasses of tea"],
        units_tr=["lira", "kilogram", "adet", "kutu", "bardak cay"],
        grade_range=(3, 10),
    ),
    StoryTheme(
        category=ThemeCategory.TURKISH_CULTURE,
        name="Turkish Breakfast",
        name_tr="Turk Kahvaltisi",
        description="Traditional Turkish breakfast",
        description_tr="Geleneksel Turk kahvaltisi",
        characters=["the grandmother", "the family", "the host"],
        characters_tr=["babaanne/anneanne", "aile", "ev sahibi"],
        settings=["the breakfast table", "the village house", "the garden"],
        settings_tr=["kahvalti sofrasi", "koy evi", "bahce"],
        objects=["eggs", "cheese", "olives", "bread", "honey", "tomatoes", "cucumbers"],
        objects_tr=["yumurtalar", "peynir", "zeytinler", "ekmek", "bal", "domatesler", "salataliklar"],
        verbs=["prepared", "served", "ate", "shared", "enjoyed"],
        verbs_tr=["hazirladi", "servis etti", "yedi", "paylasti", "keyif aldi"],
        units=["eggs", "slices", "pieces", "glasses of tea", "plates"],
        units_tr=["yumurta", "dilim", "parca", "bardak cay", "tabak"],
        grade_range=(1, 8),
    ),

    # TECHNOLOGY
    StoryTheme(
        category=ThemeCategory.TECHNOLOGY,
        name="Coding",
        name_tr="Kodlama",
        description="Programming and computers",
        description_tr="Programlama ve bilgisayarlar",
        characters=["the programmer", "the developer", "the designer"],
        characters_tr=["programci", "gelistirici", "tasarimci"],
        settings=["the tech office", "the computer lab", "the startup"],
        settings_tr=["teknoloji ofisi", "bilgisayar laboratuvari", "startup"],
        objects=["lines of code", "apps", "websites", "bugs", "features"],
        objects_tr=["kod satirlari", "uygulamalar", "web siteleri", "hatalar", "ozellikler"],
        verbs=["coded", "debugged", "deployed", "tested", "created"],
        verbs_tr=["kodladi", "hata ayikladi", "yayinladi", "test etti", "olusturdu"],
        units=["lines", "bugs", "features", "users", "downloads"],
        units_tr=["satir", "hata", "ozellik", "kullanici", "indirme"],
        grade_range=(5, 12),
    ),

    # ART
    StoryTheme(
        category=ThemeCategory.ART,
        name="Art Class",
        name_tr="Resim Dersi",
        description="Drawing and painting",
        description_tr="Cizim ve boyama",
        characters=["the artist", "the art teacher", "the student"],
        characters_tr=["sanatci", "resim ogretmeni", "ogrenci"],
        settings=["the art studio", "the gallery", "the classroom"],
        settings_tr=["sanat studyosu", "galeri", "sinif"],
        objects=["paintings", "brushes", "colors", "canvases", "crayons"],
        objects_tr=["tablolar", "fircalar", "renkler", "tuvaller", "boyalar"],
        verbs=["painted", "drew", "colored", "exhibited", "created"],
        verbs_tr=["boyadi", "cizdi", "renklendirdi", "sergiledi", "yaratti"],
        units=["paintings", "colors", "brushes", "hours", "students"],
        units_tr=["tablo", "renk", "firca", "saat", "ogrenci"],
        grade_range=(1, 9),
    ),

    # MUSIC
    StoryTheme(
        category=ThemeCategory.MUSIC,
        name="Music Band",
        name_tr="Muzik Grubu",
        description="Making music together",
        description_tr="Birlikte muzik yapmak",
        characters=["the musician", "the singer", "the conductor"],
        characters_tr=["muzisyen", "sarkici", "orkestra sefi"],
        settings=["the concert hall", "the rehearsal room", "the stage"],
        settings_tr=["konser salonu", "prova odasi", "sahne"],
        objects=["instruments", "songs", "notes", "microphones", "speakers"],
        objects_tr=["enstrumanlar", "sarkilar", "notalar", "mikrofonlar", "hoparlörler"],
        verbs=["played", "sang", "composed", "performed", "practiced"],
        verbs_tr=["caldi", "soyledi", "besteledi", "sahneledi", "calistti"],
        units=["songs", "notes", "minutes", "concerts", "instruments"],
        units_tr=["sarki", "nota", "dakika", "konser", "enstruman"],
        grade_range=(2, 10),
    ),
]


class StoryThemeSelector:
    """
    Selects appropriate themes based on context.
    """

    def __init__(self, themes: List[StoryTheme] = None):
        self.themes = themes or STORY_THEMES

    def get_theme_for_grade(self, grade: int) -> StoryTheme:
        """Get a random theme appropriate for grade level."""
        appropriate = [t for t in self.themes if t.grade_range[0] <= grade <= t.grade_range[1]]
        if not appropriate:
            appropriate = self.themes
        return random.choice(appropriate)

    def get_theme_by_category(self, category: ThemeCategory) -> StoryTheme:
        """Get a random theme from a specific category."""
        matching = [t for t in self.themes if t.category == category]
        if not matching:
            return random.choice(self.themes)
        return random.choice(matching)

    def get_theme_by_name(self, name: str) -> Optional[StoryTheme]:
        """Get theme by name."""
        for theme in self.themes:
            if theme.name.lower() == name.lower() or theme.name_tr.lower() == name.lower():
                return theme
        return None

    def get_all_categories(self) -> List[str]:
        """Get all available categories."""
        return list(set(t.category.value for t in self.themes))

    def get_seasonal_theme(self, month: int) -> StoryTheme:
        """Get theme based on season/month."""
        # Winter (Dec-Feb): Indoor themes
        # Spring (Mar-May): Nature, garden
        # Summer (Jun-Aug): Sports, travel
        # Fall (Sep-Nov): School, harvest

        if month in [12, 1, 2]:  # Winter
            categories = [ThemeCategory.COOKING, ThemeCategory.GAMES, ThemeCategory.TECHNOLOGY]
        elif month in [3, 4, 5]:  # Spring
            categories = [ThemeCategory.NATURE, ThemeCategory.ANIMALS, ThemeCategory.GARDENING]
        elif month in [6, 7, 8]:  # Summer
            categories = [ThemeCategory.SPORTS, ThemeCategory.TRAVEL, ThemeCategory.SPACE]
        else:  # Fall
            categories = [ThemeCategory.SCHOOL, ThemeCategory.FOOD, ThemeCategory.ART]

        matching = [t for t in self.themes if t.category in categories]
        return random.choice(matching) if matching else random.choice(self.themes)


# Global selector instance
theme_selector = StoryThemeSelector()
