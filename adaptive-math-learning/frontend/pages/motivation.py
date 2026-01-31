"""
Motivasyon Sayfasi - Kesfet ve Ogren.

Gunluk matematik bilgileri, bulmacalar, matematikci hikayeleri,
sertifikalar ve mevsimsel icerikler sunan motivasyon merkezi.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any

from theme import apply_theme, render_sidebar, api_get, api_post, stat_card, section_header

# ---------------------------------------------------------------------------
# Sayfa yapilandirmasi
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Motivasyon - MathAI",
    page_icon="\U0001f4a1",
    layout="wide",
)

apply_theme()
render_sidebar("motivation")

# ---------------------------------------------------------------------------
# Ek CSS -- motivasyon sayfasina ozel goersel zenginlik
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Motivasyon hero */
.motivation-hero {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%);
    border-radius: 20px;
    padding: 40px 36px;
    color: white;
    text-align: center;
    margin-bottom: 28px;
    box-shadow: 0 12px 40px rgba(240, 147, 251, 0.35);
    position: relative;
    overflow: hidden;
}
.motivation-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
    animation: shimmer 6s ease-in-out infinite;
}
@keyframes shimmer {
    0%, 100% { transform: translateX(-30%) translateY(-30%); }
    50% { transform: translateX(10%) translateY(10%); }
}
.motivation-hero h1 {
    color: white !important;
    font-size: 2.4em;
    font-weight: 700;
    margin: 0 0 8px 0;
    position: relative;
}
.motivation-hero p {
    color: rgba(255,255,255,0.92);
    font-size: 1.15em;
    margin: 0;
    position: relative;
}

/* Bilgi karti */
.fact-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 28px;
    color: white;
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
    margin-bottom: 16px;
}
.fact-card h3 {
    color: white !important;
    margin: 0 0 12px 0;
    font-size: 1.3em;
}
.fact-card p {
    color: rgba(255,255,255,0.92);
    line-height: 1.7;
    margin: 0 0 8px 0;
    font-size: 1.02em;
}
.fact-meta {
    display: flex;
    gap: 16px;
    margin-top: 14px;
    flex-wrap: wrap;
}
.fact-meta span {
    background: rgba(255,255,255,0.18);
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.82em;
    color: rgba(255,255,255,0.9);
}

/* Bulmaca karti */
.puzzle-card {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    border-radius: 16px;
    padding: 28px;
    color: #1a3a2a;
    box-shadow: 0 8px 30px rgba(67, 233, 123, 0.25);
    margin-bottom: 16px;
}
.puzzle-card h3 {
    color: #1a3a2a !important;
    margin: 0 0 8px 0;
}
.puzzle-card p {
    color: #1a3a2a;
    line-height: 1.6;
}
.difficulty-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.82em;
    font-weight: 600;
}
.diff-easy { background: #d4edda; color: #155724; }
.diff-medium { background: #fff3cd; color: #856404; }
.diff-hard { background: #f8d7da; color: #721c24; }

/* Matematikci karti */
.mathematician-card {
    background: white;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border: 1px solid #f0f0f0;
    transition: transform 0.25s, box-shadow 0.25s;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.mathematician-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2);
}
.mathematician-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.14);
}
.mathematician-name {
    font-size: 1.12em;
    font-weight: 700;
    color: #333;
    margin-bottom: 4px;
}
.mathematician-era {
    font-size: 0.82em;
    color: #888;
    margin-bottom: 8px;
}
.mathematician-contrib {
    font-size: 0.88em;
    color: #555;
    line-height: 1.5;
}
.mathematician-nationality {
    display: inline-block;
    background: #667eea;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75em;
    margin-bottom: 8px;
}

/* Sertifika karti */
.certificate-card {
    background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
    border: 3px solid #c9a96e;
    border-radius: 16px;
    padding: 32px;
    text-align: center;
    box-shadow: 0 8px 30px rgba(201, 169, 110, 0.25);
    position: relative;
    margin-bottom: 16px;
}
.certificate-card::before {
    content: '';
    position: absolute;
    top: 8px; left: 8px; right: 8px; bottom: 8px;
    border: 1px solid rgba(201, 169, 110, 0.4);
    border-radius: 12px;
    pointer-events: none;
}
.cert-title {
    font-size: 1.3em;
    font-weight: 700;
    color: #5a3e1b;
    margin-bottom: 8px;
}
.cert-description {
    font-size: 0.95em;
    color: #6b5a3e;
    line-height: 1.6;
    margin-bottom: 12px;
}
.cert-code {
    font-family: 'Courier New', monospace;
    background: rgba(201, 169, 110, 0.2);
    padding: 6px 18px;
    border-radius: 8px;
    font-size: 0.9em;
    color: #5a3e1b;
    letter-spacing: 2px;
}
.cert-date {
    font-size: 0.8em;
    color: #8a7a5a;
    margin-top: 10px;
}
.cert-level {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85em;
    margin-bottom: 10px;
}
.level-master { background: #ffd700; color: #5a3e1b; }
.level-advanced { background: #c0c0c0; color: #333; }
.level-intermediate { background: #cd7f32; color: white; }
.level-beginner { background: #a8d8ea; color: #333; }

/* Mevsimsel kart */
.seasonal-card {
    border-radius: 16px;
    padding: 28px;
    color: white;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.seasonal-card h3 {
    color: white !important;
    margin: 0 0 8px 0;
}
.seasonal-card p {
    color: rgba(255,255,255,0.9);
    line-height: 1.6;
}

/* Mevsimsel gorev karti */
.challenge-item {
    background: rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 10px;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255,255,255,0.2);
}
.challenge-item h4 {
    color: white !important;
    margin: 0 0 4px 0;
    font-size: 1em;
}
.challenge-item p {
    margin: 0;
    font-size: 0.9em;
}
.xp-badge {
    display: inline-block;
    background: rgba(255,255,255,0.25);
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
    margin-top: 6px;
}

/* Sonuc kutulari */
.result-correct {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    border-radius: 12px;
    padding: 20px;
    border-left: 5px solid #28a745;
    color: #155724;
    margin: 12px 0;
}
.result-incorrect {
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    border-radius: 12px;
    padding: 20px;
    border-left: 5px solid #dc3545;
    color: #721c24;
    margin: 12px 0;
}
.hint-box {
    background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
    border-radius: 12px;
    padding: 16px;
    border-left: 5px solid #ffc107;
    color: #856404;
    margin: 12px 0;
}

/* Detay modal */
.detail-overlay {
    background: white;
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    border: 1px solid #e0e0e0;
    margin-bottom: 16px;
}
.detail-overlay h3 {
    color: #333 !important;
    margin-bottom: 12px;
}
.quote-box {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 12px;
    padding: 18px;
    border-left: 4px solid #667eea;
    font-style: italic;
    color: #555;
    margin: 12px 0;
}
.fun-fact-item {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    font-size: 0.92em;
    color: #444;
    border-left: 3px solid #43e97b;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults (moved to top for safe initialization)
# ---------------------------------------------------------------------------
_SESSION_DEFAULTS = {
    "puzzle_answer": "",
    "puzzle_result": None,
    "puzzle_hint_index": 0,
    "puzzle_hints_shown": [],
}
for _k, _v in _SESSION_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ---------------------------------------------------------------------------
# Yardimci fonksiyonlar ve yedek veriler
# ---------------------------------------------------------------------------

FALLBACK_DAILY_FACT: Dict[str, Any] = {
    "id": "fallback-fact",
    "title": "Cebirin Babasi: El-Harizmi",
    "content": (
        "Harizmi (Muhammed bin Musa el-Harizmi), 9. yuzyilda yazdigi "
        "Kitabul-Muhtasar fi Hisabil-Cebr vel-Mukabele adli eseriyle "
        "cebir biliminin temellerini atti. 'Cebir' kelimesi bu kitabin "
        "adindan, 'algoritma' kelimesi ise Harizminin Latinceye cevrilen "
        "adindan turemistir."
    ),
    "source": "Matematik Tarihi Ansiklopedisi",
    "mathematician": "El-Harizmi",
    "year": "820",
    "fun_rating": 5,
    "date": datetime.now().strftime("%d.%m.%Y"),
}

FALLBACK_PUZZLE: Dict[str, Any] = {
    "id": "fallback-puz",
    "title": "Sayi Dizisi Bulmacasi",
    "description": "Bu dizinin bir sonraki sayisini bulun: 2, 6, 12, 20, 30, ?",
    "difficulty": "easy",
    "category": "sequence",
    "points": 10,
    "hints": ["Her adimda fark artmaktadir.", "Farklar: 4, 6, 8, 10, ..."],
}

FALLBACK_MATHEMATICIANS: List[Dict[str, Any]] = [
    {
        "id": "cahit_arf",
        "name": "Cahit Arf",
        "birth_year": "1910",
        "death_year": "1997",
        "nationality": "Turk",
        "contributions": ["Arf degismezi", "Arf halkalari", "Hasse-Arf teoremi"],
        "biography": "Turkiyenin en buyuk matematikcisi. Portresi 10 TL banknotundadir.",
        "famous_quote": "Matematikte gercek anlama, formullerin otesindedir.",
        "fun_facts": [
            "Portresi Turk 10 lira banknotunun arkasinda yer almaktadir.",
            "Gottingen Universitesinde Helmut Hasse ile calismistir.",
        ],
        "related_topics": ["cebir", "topoloji", "sayi_teorisi"],
    },
    {
        "id": "ali_kuscu",
        "name": "Ali Kuscu",
        "birth_year": "1403",
        "death_year": "1474",
        "nationality": "Osmanli",
        "contributions": ["Trigonometrik fonksiyonlarin sistematik incelenmesi", "Astronomi hesaplari"],
        "biography": "Ulug Beyin ogrencisi, Fatih Sultan Mehmetin davetlisi olarak Istanbula gelmistir.",
        "famous_quote": None,
        "fun_facts": [
            "Fatih Sultan Mehmet gunluk 200 akce maas baglamistir.",
            "Aydaki bir krater onun adini tasir.",
        ],
        "related_topics": ["trigonometri", "astronomi"],
    },
    {
        "id": "harizmi",
        "name": "El-Harizmi",
        "birth_year": "780",
        "death_year": "850",
        "nationality": "Harezmli",
        "contributions": ["Cebir biliminin temeli", "Hindu-Arap rakamlari", "Algoritma kavrami"],
        "biography": "Islam Altin Caginin en onemli matematikcisi. Beytul Hikmede calismistir.",
        "famous_quote": "Bilgi, insanin en degerli hazinesidir.",
        "fun_facts": [
            "Cebir ve algoritma kelimeleri onun adindan gelir.",
            "Beytul Hikme doneminin en buyuk arastirma merkeziydi.",
        ],
        "related_topics": ["cebir", "denklemler", "aritmetik"],
    },
    {
        "id": "omer_hayyam",
        "name": "Omer Hayyam",
        "birth_year": "1048",
        "death_year": "1131",
        "nationality": "Selcuklu",
        "contributions": ["Kup denklemlerin geometrik cozumu", "Hayyam takvimi", "Pascal ucgeninin kesfedicisi"],
        "biography": "Matematikci, astronom, filozof ve sair. Rubailer ile edebiyat dunyasinda da unludur.",
        "famous_quote": "Bir kadeh sarap, bir kitap ve sen - cennet budur.",
        "fun_facts": [
            "Hayyam takvimi 5000 yilda sadece 1 gun sapar.",
            "Rubailer Edward FitzGerald cevirisiyle Batida meshur oldu.",
        ],
        "related_topics": ["cebir", "geometri", "denklemler"],
    },
    {
        "id": "tusi",
        "name": "Nasireddin Tusi",
        "birth_year": "1201",
        "death_year": "1274",
        "nationality": "Selcuklu",
        "contributions": ["Trigonometriyi bagimsiz dal olarak kurmasi", "Tusi cifti", "Meraga Rasathanesi"],
        "biography": "Meraga Rasathanesinin kurucusu. Doneminin en etkili bilgini.",
        "famous_quote": "Bilim, karanligi aydinlatan isiktir.",
        "fun_facts": [
            "Meraga Rasathanesinde 400.000 ciltlik kutuphane kurmustur.",
            "Tusi cifti Kopernike ilham vermis olabilir.",
        ],
        "related_topics": ["trigonometri", "astronomi"],
    },
    {
        "id": "euler",
        "name": "Leonhard Euler",
        "birth_year": "1707",
        "death_year": "1783",
        "nationality": "Isvicre",
        "contributions": ["Euler formulu", "Graf teorisi", "Modern matematik notasyonu"],
        "biography": "Tarihin en verimli matematikcisi. 800den fazla eser yazmistir.",
        "famous_quote": "Matematikte okumak, yazmak kadar onemlidir.",
        "fun_facts": [
            "Son 17 yilini kor olarak gecirdi ama uretkenligini kaybetmedi.",
            "Bir gunun buyuk bolumunu matematik yaparak gecirirdi.",
        ],
        "related_topics": ["analiz", "graf_teorisi", "sayi_teorisi"],
    },
    {
        "id": "gauss",
        "name": "Carl Friedrich Gauss",
        "birth_year": "1777",
        "death_year": "1855",
        "nationality": "Alman",
        "contributions": ["Asal Sayilar Teoremi", "Gauss eleminasyonu", "Normal dagilim"],
        "biography": "Matematik Prensi olarak bilinir. Sayi teorisi, istatistik ve analiz alanlarinda dev.",
        "famous_quote": "Matematik bilimlerin kralicesidir.",
        "fun_facts": [
            "10 yasinda 1den 100e toplami saniyeler icinde buldu: 5050.",
            "Kesiflerini yayinlamakta cok yavas davranirdi.",
        ],
        "related_topics": ["sayi_teorisi", "istatistik", "cebir"],
    },
    {
        "id": "ramanujan",
        "name": "Srinivasa Ramanujan",
        "birth_year": "1887",
        "death_year": "1920",
        "nationality": "Hint",
        "contributions": ["Sonsuz seriler", "Surekli kesirler", "Bolum fonksiyonu"],
        "biography": "Resmi egitim almadan dahi seviyesinde eserler uretmis nadir matematikci.",
        "famous_quote": "Bir formul bana bir sey anlatmiyorsa, benim icin degersizdir.",
        "fun_facts": [
            "1729 sayisi 'Ramanujan sayisi' olarak anilir.",
            "Defterlerinde binlerce ispatsiz teorem vardi.",
        ],
        "related_topics": ["sayi_teorisi", "diziler", "analiz"],
    },
    {
        "id": "pisagor",
        "name": "Pisagor (Pythagoras)",
        "birth_year": "M.O. 570",
        "death_year": "M.O. 495",
        "nationality": "Antik Yunan",
        "contributions": ["Pisagor teoremi", "Muzik-matematik iliskisi", "Sayi mistisizmi"],
        "biography": "Antik Yunanin en meshur matematikci ve filozoflarindan. Pisagorculuk okulunu kurmustur.",
        "famous_quote": "Her sey sayidir.",
        "fun_facts": [
            "Fasulye yemeyi reddederdi - nedenini kimse bilmiyor.",
            "Pisagorculuk okulu gizli bir topluluktu.",
        ],
        "related_topics": ["geometri", "ucgenler", "sayilar"],
    },
]

FALLBACK_SEASONAL: Dict[str, Any] = {
    "season": "winter",
    "theme": "Kis Tatili Calisma Kampi",
    "color_primary": "#2196F3",
    "color_secondary": "#64B5F6",
    "icon": "kar",
}

FALLBACK_SEASONAL_CHALLENGES: List[Dict[str, Any]] = [
    {
        "challenge_id": "season_winter",
        "title": "Kis Donemi Matematik Maratonu",
        "description": "Her gun en az 5 soru cozerek kis tatilini verimli gecir!",
        "season": "winter",
        "xp_reward": 100,
    },
    {
        "challenge_id": "holiday_general",
        "title": "Tatil Ozel Bulmaca Serisi",
        "description": "Tatil gunlerine ozel zorlu bulmacalari coz ve odul kazan!",
        "xp_reward": 150,
    },
]

SEASON_ICONS = {
    "spring": "\U0001f338",   # cherry blossom
    "summer": "\u2600\ufe0f", # sun
    "autumn": "\U0001f342",   # fallen leaf
    "winter": "\u2744\ufe0f", # snowflake
}

SEASON_NAMES_TR = {
    "spring": "Ilkbahar",
    "summer": "Yaz",
    "autumn": "Sonbahar",
    "winter": "Kis",
}


def _difficulty_badge(level: str) -> str:
    """Zorluk seviyesine gore HTML rozet uretir."""
    mapping = {
        "easy": ("Kolay", "diff-easy"),
        "medium": ("Orta", "diff-medium"),
        "hard": ("Zor", "diff-hard"),
    }
    label, css = mapping.get(level, ("Bilinmiyor", "diff-easy"))
    return f'<span class="difficulty-badge {css}">{label}</span>'


def _mastery_level_css(level: str) -> str:
    mapping = {
        "master": "level-master",
        "advanced": "level-advanced",
        "intermediate": "level-intermediate",
        "beginner": "level-beginner",
    }
    return mapping.get(level, "level-beginner")


def _mastery_level_tr(level: str) -> str:
    mapping = {
        "master": "Usta",
        "advanced": "Ileri",
        "intermediate": "Orta",
        "beginner": "Baslangic",
    }
    return mapping.get(level, level.title())


# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
st.markdown("""
<div class="motivation-hero">
    <h1>\U0001f4a1 Kesfet ve Ogren</h1>
    <p>Matematik dunyanin en guzel dili. Her gun yeni bir sey kesfet, bulmacalarla zihnini gelistir ve basarilarini belgele!</p>
</div>
""", unsafe_allow_html=True)

# Ust istatistik kartlari
col1, col2, col3, col4 = st.columns(4)
with col1:
    stat_card("\U0001f4d6", "Gunun Bilgisi", "Her gun yeni bir bilgi")
with col2:
    stat_card("\U0001f9e9", "Bulmaca", "Zihnini test et")
with col3:
    stat_card("\U0001f3c6", "Matematikci", "Ilham veren hikayeler")
with col4:
    stat_card("\U0001f4dc", "Sertifika", "Basarini belgele")

st.markdown("")

# ---------------------------------------------------------------------------
# ANA SEKMELER
# ---------------------------------------------------------------------------
tab_fact, tab_puzzle, tab_mathematicians, tab_certificates = st.tabs(
    ["\U0001f4d6 Gunun Bilgisi", "\U0001f9e9 Bulmaca", "\U0001f3eb Matematikciler", "\U0001f3c5 Sertifikalar"]
)

# ===== SEKME 1 - GUNUN BILGISI ============================================
with tab_fact:
    section_header("Gunun Matematik Bilgisi")

    data = api_get("/motivation/daily-fact")
    if data is None:
        data = FALLBACK_DAILY_FACT

    title = data.get("title", "Matematik Bilgisi")
    content = data.get("content", "")
    source = data.get("source", "")
    mathematician = data.get("mathematician", "")
    year = data.get("year", "")
    fun_rating = data.get("fun_rating", 3)

    today_str = datetime.now().strftime("%d.%m.%Y")

    # Rating yildizlari
    stars = "\u2b50" * min(fun_rating, 5)

    meta_parts = []
    if year:
        meta_parts.append(f"<span>\U0001f4c5 {year}</span>")
    if mathematician:
        meta_parts.append(f"<span>\U0001f464 {mathematician}</span>")
    if source:
        meta_parts.append(f"<span>\U0001f4da {source}</span>")
    meta_parts.append(f"<span>\U0001f4c6 {today_str}</span>")
    meta_parts.append(f"<span>{stars}</span>")
    meta_html = "\n".join(meta_parts)

    st.markdown(f"""
    <div class="fact-card">
        <h3>\U0001f4a1 {title}</h3>
        <p>{content}</p>
        <div class="fact-meta">
            {meta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Rastgele baska bir bilgi
    st.markdown("")
    if st.button("\U0001f504 Baska Bir Bilgi Goster", key="random_fact"):
        random_data = api_get("/motivation/random-fact")
        if random_data:
            st.markdown(f"""
            <div class="fact-card" style="background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);">
                <h3>\U0001f31f {random_data.get('title', '')}</h3>
                <p>{random_data.get('content', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Ek bilgi yuklenemedi. Yarin yeni bir bilgi seni bekliyor!")


# ===== SEKME 2 - BULMACA ===================================================
with tab_puzzle:
    section_header("Gunluk Matematik Bulmacasi")

    puzzle_data = api_get("/motivation/puzzle")
    if puzzle_data is None:
        puzzle_data = FALLBACK_PUZZLE

    puzzle_id = puzzle_data.get("id", "unknown")
    puzzle_title = puzzle_data.get("title", "Bulmaca")
    puzzle_desc = puzzle_data.get("description", "")
    puzzle_diff = puzzle_data.get("difficulty", "easy")
    puzzle_points = puzzle_data.get("points", 10)
    puzzle_category = puzzle_data.get("category", "mantik")

    diff_html = _difficulty_badge(puzzle_diff)

    st.markdown(f"""
    <div class="puzzle-card">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <h3>\U0001f9e9 {puzzle_title}</h3>
            <div>{diff_html} <span class="difficulty-badge diff-easy" style="margin-left:6px;">\U0001f3af {puzzle_points} Puan</span></div>
        </div>
        <p style="font-size:1.1em; margin-top:12px; font-weight:500;">{puzzle_desc}</p>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_actions = st.columns([3, 2])

    with col_input:
        answer = st.text_input(
            "Cevabin:",
            key="puzzle_answer_input",
            placeholder="Cevabini buraya yaz...",
        )

    with col_actions:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            if st.button("\u2705 Kontrol Et", key="check_puzzle", use_container_width=True, type="primary"):
                if answer.strip():
                    result = api_post(
                        f"/motivation/puzzle/{puzzle_id}/check",
                        {"answer": answer.strip()},
                    )
                    if result is None:
                        # Yedek: yerel kontrol
                        fallback_answer = "42"
                        is_correct = answer.strip().lower() == fallback_answer.lower()
                        result = {
                            "correct": is_correct,
                            "message": "Tebrikler! Dogru cevap!" if is_correct else "Yanlis cevap. Tekrar dene!",
                            "explanation": "Farklar 4, 6, 8, 10, 12. Yani 30 + 12 = 42." if is_correct else None,
                        }
                    st.session_state.puzzle_result = result
                else:
                    st.warning("Lutfen bir cevap girin.")

        with btn_col2:
            if st.button("\U0001f4a1 Ipucu", key="hint_puzzle", use_container_width=True):
                hint_resp = api_get(f"/motivation/puzzle/{puzzle_id}/hint", params={"hint_index": getattr(st.session_state, "puzzle_hint_index", 0)})
                if hint_resp and isinstance(hint_resp, dict):
                    hint_text = hint_resp.get("hint", "")
                elif hint_resp and isinstance(hint_resp, str):
                    hint_text = hint_resp
                else:
                    # Yedek ipucu
                    hints = puzzle_data.get("hints", [])
                    idx = min(getattr(st.session_state, "puzzle_hint_index", 0), len(hints) - 1) if hints else -1
                    hint_text = hints[idx] if idx >= 0 else "Ipucu bulunamadi."
                if hint_text and hint_text not in getattr(st.session_state, "puzzle_hints_shown", []):
                    st.session_state.puzzle_hints_shown.append(hint_text)
                st.session_state.puzzle_hint_index = getattr(st.session_state, "puzzle_hint_index", 0) + 1

    # Gosterilen ipuclari
    for i, hint in enumerate(getattr(st.session_state, "puzzle_hints_shown", [])):
        st.markdown(f"""
        <div class="hint-box">
            <strong>\U0001f4a1 Ipucu {i + 1}:</strong> {hint}
        </div>
        """, unsafe_allow_html=True)

    # Sonuc goster
    if getattr(st.session_state, "puzzle_result", None):
        result = getattr(st.session_state, "puzzle_result", {})
        is_correct = result.get("correct", False)
        message = result.get("message", "")
        explanation = result.get("explanation", "")

        if is_correct:
            st.markdown(f"""
            <div class="result-correct">
                <strong>\U0001f389 {message}</strong>
                {f'<br><br><em>{explanation}</em>' if explanation else ''}
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
        else:
            st.markdown(f"""
            <div class="result-incorrect">
                <strong>\u274c {message}</strong>
            </div>
            """, unsafe_allow_html=True)


# ===== SEKME 3 - MATEMATIKCILER ============================================
with tab_mathematicians:
    section_header("Unlu Matematikciler")
    st.markdown("Matematik tarihine yon vermis buyuk zihinleri taniyin.")
    st.markdown("")

    mathematicians_data = api_get("/motivation/mathematicians")
    if mathematicians_data is None:
        mathematicians_data = FALLBACK_MATHEMATICIANS

    if isinstance(mathematicians_data, dict):
        mathematicians_data = mathematicians_data.get("mathematicians", [])

    # Izgara duzeni: satir basi 3 kart
    num_cols = 3
    rows = [mathematicians_data[i:i + num_cols] for i in range(0, len(mathematicians_data), num_cols)]

    for row in rows:
        cols = st.columns(num_cols)
        for idx, m in enumerate(row):
            with cols[idx]:
                m_id = m.get("id", "")
                name = m.get("name", "Bilinmiyor")
                birth = m.get("birth_year", "?")
                death = m.get("death_year", "?")
                nationality = m.get("nationality", "")
                contribs = m.get("contributions", [])
                contrib_text = ", ".join(contribs[:2]) if contribs else "Bilgi yok"

                st.markdown(f"""
                <div class="mathematician-card">
                    <div class="mathematician-nationality">{nationality}</div>
                    <div class="mathematician-name">{name}</div>
                    <div class="mathematician-era">{birth} - {death}</div>
                    <div class="mathematician-contrib">{contrib_text}</div>
                </div>
                """, unsafe_allow_html=True)

                # Detay butonu
                if st.button(f"Detay Gor", key=f"detail_{m_id}_{idx}", use_container_width=True):
                    st.session_state[f"show_detail_{m_id}"] = True

                # Detay goruntuleme
                if st.session_state.get(f"show_detail_{m_id}", False):
                    detail = api_get(f"/motivation/mathematician/{m_id}")
                    if detail is None:
                        detail = m  # Yedek olarak mevcut veriyi kullan

                    bio = detail.get("biography", "Biyografi bilgisi mevcut degil.")
                    quote = detail.get("famous_quote", "")
                    fun_facts = detail.get("fun_facts", [])
                    all_contribs = detail.get("contributions", contribs)
                    topics = detail.get("related_topics", [])

                    st.markdown(f"""
                    <div class="detail-overlay">
                        <h3>\U0001f393 {detail.get('name', name)}</h3>
                        <p style="color:#555; line-height:1.7;">{bio}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    if quote:
                        st.markdown(f"""
                        <div class="quote-box">
                            "{quote}"
                        </div>
                        """, unsafe_allow_html=True)

                    if all_contribs:
                        st.markdown("**Onemli Katkilari:**")
                        for c in all_contribs:
                            st.markdown(f"- {c}")

                    if fun_facts:
                        st.markdown("**Ilginc Bilgiler:**")
                        for ff in fun_facts:
                            st.markdown(f"""
                            <div class="fun-fact-item">\U0001f31f {ff}</div>
                            """, unsafe_allow_html=True)

                    if topics:
                        topics_str = ", ".join([t.replace("_", " ").title() for t in topics])
                        st.markdown(f"**Ilgili Konular:** {topics_str}")

                    if st.button("Kapat", key=f"close_{m_id}_{idx}"):
                        st.session_state[f"show_detail_{m_id}"] = False
                        st.rerun()

        st.markdown("")


# ===== SEKME 4 - SERTIFIKALAR ==============================================
with tab_certificates:
    section_header("Basari Sertifikalari")
    st.markdown("Matematik yolculugundaki basarilarini belgele ve sertifikalarini gor.")
    st.markdown("")

    cert_col1, cert_col2 = st.columns([1, 1])

    with cert_col1:
        st.markdown("##### \U0001f50d Sertifikalarimi Gor")
        user_id = st.text_input(
            "Kullanici ID",
            key="cert_user_id",
            placeholder="Kullanici ID giriniz...",
        )

        if st.button("\U0001f4c4 Sertifikalari Getir", key="fetch_certs", use_container_width=True):
            if user_id.strip():
                certs = api_get(f"/motivation/certificates/{user_id.strip()}")
                if certs is None:
                    certs = []
                if isinstance(certs, dict):
                    certs = certs.get("certificates", [])
                st.session_state.user_certificates = certs
                st.session_state.cert_user = user_id.strip()
            else:
                st.warning("Lutfen bir Kullanici ID girin.")

    with cert_col2:
        st.markdown("##### \U0001f3c6 Yeni Sertifika Olustur")

        gen_user = st.text_input(
            "Kullanici ID",
            key="gen_user_id",
            placeholder="Kullanici ID giriniz...",
        )
        gen_topic = st.selectbox(
            "Konu",
            options=[
                "arithmetic", "fractions", "percentages", "algebra",
                "geometry", "ratios", "exponents", "statistics",
                "number_theory", "trigonometry", "polynomials",
                "functions", "inequalities", "sets_and_logic",
                "coordinate_geometry", "systems_of_equations",
            ],
            format_func=lambda x: x.replace("_", " ").title(),
            key="gen_topic",
        )
        gen_mastery = st.slider(
            "Hakimiyet Seviyesi (%)",
            min_value=0,
            max_value=100,
            value=75,
            step=5,
            key="gen_mastery",
        )

        if st.button("\U0001f4dc Sertifika Olustur", key="gen_cert", use_container_width=True, type="primary"):
            if gen_user.strip():
                result = api_post("/motivation/certificates/generate", {
                    "user_id": gen_user.strip(),
                    "topic": gen_topic,
                    "mastery": gen_mastery / 100.0,
                })
                if result:
                    st.session_state.generated_cert = result
                    st.success("Sertifika basariyla olusturuldu!")
                else:
                    # Yedek sertifika
                    mastery_val = gen_mastery / 100.0
                    if mastery_val >= 0.9:
                        level, level_text = "master", "Usta"
                    elif mastery_val >= 0.7:
                        level, level_text = "advanced", "Ileri"
                    elif mastery_val >= 0.5:
                        level, level_text = "intermediate", "Orta"
                    else:
                        level, level_text = "beginner", "Baslangic"

                    topic_display = gen_topic.replace("_", " ").title()
                    st.session_state.generated_cert = {
                        "id": "local-cert-001",
                        "user_id": gen_user.strip(),
                        "title": f"{topic_display} - {level_text} Seviye Sertifikasi",
                        "description": f"Bu sertifika, {topic_display} konusunda %{gen_mastery} basari oranina ulastiginizi belgeler.",
                        "topic_slug": gen_topic,
                        "mastery_level": level,
                        "issued_at": datetime.now().isoformat(),
                        "certificate_code": "DEMO12345X",
                    }
                    st.success("Sertifika olusturuldu (yerel mod).")
            else:
                st.warning("Lutfen bir Kullanici ID girin.")

    st.markdown("---")

    # Olusturulan sertifika goster
    if st.session_state.get("generated_cert"):
        cert = st.session_state.generated_cert

        level = cert.get("mastery_level", "beginner")
        level_css = _mastery_level_css(level)
        level_tr = _mastery_level_tr(level)
        issued = cert.get("issued_at", "")
        if issued:
            try:
                dt = datetime.fromisoformat(issued.replace("Z", "+00:00"))
                issued_str = dt.strftime("%d.%m.%Y %H:%M")
            except Exception:
                issued_str = issued
        else:
            issued_str = datetime.now().strftime("%d.%m.%Y %H:%M")

        st.markdown(f"""
        <div class="certificate-card">
            <div style="font-size:2em; margin-bottom:8px;">\U0001f3c6</div>
            <div class="cert-level {level_css}">{level_tr} Seviye</div>
            <div class="cert-title">{cert.get('title', 'Sertifika')}</div>
            <div class="cert-description">{cert.get('description', '')}</div>
            <div class="cert-code">Kod: {cert.get('certificate_code', '---')}</div>
            <div class="cert-date">Tarih: {issued_str}</div>
        </div>
        """, unsafe_allow_html=True)

    # Kullanici sertifikalari
    user_certs = st.session_state.get("user_certificates", None)
    if user_certs is not None:
        cert_user = st.session_state.get("cert_user", "")
        if user_certs:
            st.markdown(f"##### \U0001f4cb {cert_user} Kullanicisinin Sertifikalari")
            for cert in user_certs:
                level = cert.get("mastery_level", "beginner")
                level_css = _mastery_level_css(level)
                level_tr = _mastery_level_tr(level)
                issued = cert.get("issued_at", "")
                if issued:
                    try:
                        dt = datetime.fromisoformat(issued.replace("Z", "+00:00"))
                        issued_str = dt.strftime("%d.%m.%Y %H:%M")
                    except Exception:
                        issued_str = issued
                else:
                    issued_str = "-"

                st.markdown(f"""
                <div class="certificate-card">
                    <div style="font-size:1.6em; margin-bottom:6px;">\U0001f4dc</div>
                    <div class="cert-level {level_css}">{level_tr} Seviye</div>
                    <div class="cert-title">{cert.get('title', 'Sertifika')}</div>
                    <div class="cert-description">{cert.get('description', '')}</div>
                    <div class="cert-code">Kod: {cert.get('certificate_code', '---')}</div>
                    <div class="cert-date">Tarih: {issued_str}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"{cert_user} kullanicisina ait sertifika bulunamadi. Yeni bir sertifika olusturmak icin sag taraftaki formu kullanin.")


# ---------------------------------------------------------------------------
# MEVSIMSEL ICERIK BOLUMU
# ---------------------------------------------------------------------------
st.markdown("")
st.markdown("---")
section_header("Mevsimsel Icerikler")

seasonal_data = api_get("/motivation/seasonal")
if seasonal_data is None:
    seasonal_data = FALLBACK_SEASONAL

season_key = seasonal_data.get("season", "winter")
season_theme = seasonal_data.get("theme", "Genel Calisma Donemi")
color_primary = seasonal_data.get("color_primary", "#2196F3")
color_secondary = seasonal_data.get("color_secondary", "#64B5F6")
season_icon_key = seasonal_data.get("icon", "")
season_icon = SEASON_ICONS.get(season_key, "\U0001f30d")
season_name_tr = SEASON_NAMES_TR.get(season_key, "Bilinmiyor")

st.markdown(f"""
<div class="seasonal-card" style="background: linear-gradient(135deg, {color_primary} 0%, {color_secondary} 100%);">
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:2.4em;">{season_icon}</span>
        <div>
            <h3>{season_name_tr} Donemi: {season_theme}</h3>
            <p>Bu donem icin ozel matematik gorevleri ve etkinlikler seni bekliyor!</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Mevsimsel gorevler
challenges_data = api_get("/motivation/seasonal/challenges")
if challenges_data is None:
    challenges_data = FALLBACK_SEASONAL_CHALLENGES

if isinstance(challenges_data, dict):
    challenges_data = challenges_data.get("challenges", [])

if challenges_data:
    ch_cols = st.columns(min(len(challenges_data), 3))
    for i, ch in enumerate(challenges_data):
        with ch_cols[i % 3]:
            xp = ch.get("xp_reward", 0)
            ch_title = ch.get("title", "Gorev")
            ch_desc = ch.get("description", "")
            holiday_name = ch.get("holiday", "")

            holiday_line = f'<span style="font-size:0.8em; opacity:0.85;">\U0001f389 {holiday_name}</span><br>' if holiday_name else ""

            st.markdown(f"""
            <div class="seasonal-card" style="background: linear-gradient(135deg, {color_primary}cc 0%, {color_secondary}cc 100%); padding:20px;">
                {holiday_line}
                <h4 style="color:white !important; margin:0 0 6px 0;">{ch_title}</h4>
                <p style="color:rgba(255,255,255,0.9); font-size:0.92em; margin:0 0 8px 0;">{ch_desc}</p>
                <div class="xp-badge">\u2b50 {xp} XP</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Bu donem icin aktif gorev bulunmuyor. Yakinda yeni gorevler eklenecek!")

# ---------------------------------------------------------------------------
# Altbilgi
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    '<div style="text-align:center; color:#999; font-size:0.85em; padding:12px 0;">'
    'MathAI Motivasyon Merkezi | Adaptif Matematik Ogrenme Platformu'
    '</div>',
    unsafe_allow_html=True,
)
