"""
Adaptif Matematik Ogrenme Platformu - Ana Sayfa

TOBB ETU - BIL495/YAP495 Bahar 2025
Streamlit ana giris noktasi. Modern, gorsel acidan etkileyici bir kontrol paneli.
"""

import streamlit as st
from frontend.theme import (
    apply_theme,
    render_sidebar,
    api_get,
    stat_card,
    feature_card,
    section_header,
    progress_bar,
    get_topic_color,
    TOPIC_COLORS,
)

# ---------------------------------------------------------------------------
# Sayfa Yapilandirmasi
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Adaptif Matematik Ogrenme Platformu",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000/api/v1"

# ---------------------------------------------------------------------------
# Tema & Kenar Cubugu
# ---------------------------------------------------------------------------
apply_theme()
render_sidebar(active_page="app")

# ---------------------------------------------------------------------------
# Ek CSS - Sayfa icin ozel stiller
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Hero icerigi */
.hero-title {
    font-size: 2.4em;
    font-weight: 700;
    color: white;
    margin: 0 0 8px 0;
    line-height: 1.15;
}
.hero-subtitle {
    font-size: 1.1em;
    color: rgba(255,255,255,0.92);
    margin: 0 0 20px 0;
    line-height: 1.6;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 24px;
    padding: 6px 16px;
    font-size: 0.82em;
    font-weight: 600;
    color: white;
    margin-bottom: 14px;
    letter-spacing: 0.5px;
}
/* Hero gorsel bolumu */
.hero-visual {
    text-align: center;
    padding: 24px 0;
}
.hero-visual-icon {
    font-size: 6em;
    line-height: 1;
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.2));
}
.hero-visual-text {
    color: rgba(255,255,255,0.75);
    font-size: 0.9em;
    margin-top: 12px;
}

/* Oneri karti */
.recommendation-card {
    background: white;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 3px 15px rgba(0,0,0,0.07);
    border: 1px solid #f0f0f0;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 8px;
}
.recommendation-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 24px rgba(0,0,0,0.12);
}
.rec-topic-name {
    font-size: 1.15em;
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
}
.rec-reason {
    font-size: 0.85em;
    color: #888;
    margin-bottom: 12px;
}

/* Konu kartlari (grid) */
.topic-grid-card {
    border-radius: 14px;
    padding: 20px;
    color: white;
    margin-bottom: 14px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.18);
    transition: transform 0.25s, box-shadow 0.25s;
    cursor: default;
    min-height: 120px;
}
.topic-grid-card:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 8px 30px rgba(0,0,0,0.22);
}
.topic-grid-name {
    font-size: 1.1em;
    font-weight: 700;
    margin-bottom: 6px;
}
.topic-grid-desc {
    font-size: 0.82em;
    color: rgba(255,255,255,0.85);
    line-height: 1.4;
}
.topic-grid-grade {
    display: inline-block;
    margin-top: 10px;
    background: rgba(255,255,255,0.22);
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.75em;
    font-weight: 600;
}

/* Alt bilgi */
.app-footer {
    text-align: center;
    padding: 32px 0 16px 0;
    color: #aaa;
    font-size: 0.85em;
    border-top: 1px solid #eee;
    margin-top: 48px;
}
.app-footer strong {
    color: #667eea;
}
</style>
""", unsafe_allow_html=True)


# ===================================================================
# YARDIMCI FONKSIYONLAR
# ===================================================================

def get_statistics() -> dict:
    """Ilerleme istatistiklerini API'den al."""
    data = api_get("/progress/statistics")
    if data:
        return data
    return {
        "total_questions": 0,
        "overall_accuracy": 0,
        "best_streak": 0,
        "average_mastery": 0.0,
        "topics_practiced": 0,
    }


def get_recommendations() -> list:
    """Konu onerilerini API'den al."""
    data = api_get("/progress/recommendations")
    if data:
        return data[:3]
    return [
        {"topic": "arithmetic", "topic_name": "Aritmetik", "current_mastery": 0.45, "reason": "Temel islemlerle baslayarak gucllu bir temel olusuturun"},
        {"topic": "fractions", "topic_name": "Kesirler", "current_mastery": 0.30, "reason": "Aritmetik becerilerinizi kesirlerle gelistirin"},
        {"topic": "algebra", "topic_name": "Cebir", "current_mastery": 0.20, "reason": "Ileri matematik icin vazgecilmez bir konu"},
    ]


def get_topics() -> list:
    """Mevcut konulari API'den al."""
    data = api_get("/topics")
    if data:
        # API bir liste veya dict dondurebilir
        if isinstance(data, dict):
            return data.get("topics", [])
        return data
    # Varsayilan konu listesi
    return [
        {"name": "Aritmetik", "slug": "arithmetic", "description": "Temel islemler: toplama, cikarma, carpma, bolme", "grade_range_start": 1, "grade_range_end": 6},
        {"name": "Kesirler", "slug": "fractions", "description": "Kesir islemleri", "grade_range_start": 3, "grade_range_end": 8},
        {"name": "Yuzdeler", "slug": "percentages", "description": "Yuzde hesaplamalari", "grade_range_start": 5, "grade_range_end": 9},
        {"name": "Cebir", "slug": "algebra", "description": "Denklemler ve ifadeler", "grade_range_start": 6, "grade_range_end": 12},
        {"name": "Geometri", "slug": "geometry", "description": "Alan, cevre, hacim hesaplamalari", "grade_range_start": 3, "grade_range_end": 12},
        {"name": "Oranlar", "slug": "ratios", "description": "Oran ve orantilar", "grade_range_start": 5, "grade_range_end": 9},
        {"name": "Uslu Sayilar", "slug": "exponents", "description": "Kuvvetler, kokler, us kurallari", "grade_range_start": 6, "grade_range_end": 10},
        {"name": "Istatistik", "slug": "statistics", "description": "Ortalama, medyan, mod, olasilik", "grade_range_start": 5, "grade_range_end": 9},
        {"name": "Sayi Teorisi", "slug": "number_theory", "description": "Asal sayilar, EBOB, EKOK", "grade_range_start": 4, "grade_range_end": 8},
        {"name": "Denklem Sistemleri", "slug": "systems_of_equations", "description": "Cok bilinmeyenli denklemler", "grade_range_start": 7, "grade_range_end": 11},
        {"name": "Esitsizlikler", "slug": "inequalities", "description": "Dogrusal ve birlesik esitsizlikler", "grade_range_start": 7, "grade_range_end": 11},
        {"name": "Fonksiyonlar", "slug": "functions", "description": "Dogrusal, ikinci derece fonksiyonlar", "grade_range_start": 8, "grade_range_end": 12},
        {"name": "Trigonometri", "slug": "trigonometry", "description": "Sinus, kosinus, tanjant", "grade_range_start": 9, "grade_range_end": 12},
        {"name": "Polinomlar", "slug": "polynomials", "description": "Polinom islemleri ve carpanlara ayirma", "grade_range_start": 8, "grade_range_end": 11},
        {"name": "Kumeler ve Mantik", "slug": "sets_and_logic", "description": "Kume islemleri, Venn semalari", "grade_range_start": 6, "grade_range_end": 10},
        {"name": "Analitik Geometri", "slug": "coordinate_geometry", "description": "Uzaklik, egim, dogru denklemleri", "grade_range_start": 7, "grade_range_end": 11},
    ]


# Turkce konu isimleri eslestirmesi
TOPIC_NAME_TR = {
    "arithmetic": "Aritmetik",
    "fractions": "Kesirler",
    "percentages": "Yuzdeler",
    "algebra": "Cebir",
    "geometry": "Geometri",
    "ratios": "Oranlar",
    "exponents": "Uslu Sayilar",
    "statistics": "Istatistik",
    "number_theory": "Sayi Teorisi",
    "systems_of_equations": "Denklem Sistemleri",
    "inequalities": "Esitsizlikler",
    "functions": "Fonksiyonlar",
    "trigonometry": "Trigonometri",
    "polynomials": "Polinomlar",
    "sets_and_logic": "Kumeler ve Mantik",
    "coordinate_geometry": "Analitik Geometri",
}


# ===================================================================
# 1) HERO BOLUMU
# ===================================================================
st.markdown("""
<div class="hero-card" style="display:flex; align-items:center; flex-wrap:wrap; padding:32px 36px;">
    <div style="flex:2; min-width:300px;">
        <div class="hero-badge">🚀 Yapay Zeka Destekli Ogrenme</div>
        <div class="hero-title">Adaptif Matematik<br>Ogrenme Platformu</div>
        <p class="hero-subtitle">
            Hibrit yapay zeka ve deterministik soru uretim motoru ile
            kisisellestirilmis matematik egitimi. Seviyenize uygun sorularla
            pratik yapin, aninda geri bildirim alin ve ilerlemenizi takip edin.
        </p>
    </div>
    <div style="flex:1; min-width:200px;" class="hero-visual">
        <div class="hero-visual-icon">🧮</div>
        <div class="hero-visual-text">16 Konu &bull; 80+ Alt Konu &bull; Sinirsiz Soru</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hizli eylem butonlari
btn_col1, btn_col2, btn_col3, btn_spacer = st.columns([1, 1, 1, 2])
with btn_col1:
    if st.button("📝  Pratik Baslat", type="primary", use_container_width=True):
        st.switch_page("pages/practice.py")
with btn_col2:
    if st.button("📚  Konulari Gor", use_container_width=True):
        st.switch_page("pages/topics.py")
with btn_col3:
    if st.button("📊  Ilerlemeni Takip Et", use_container_width=True):
        st.switch_page("pages/progress.py")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ===================================================================
# 2) ISTATISTIK SATIRLARI
# ===================================================================
section_header("📈 Ogrenme Istatistiklerin")

stats = get_statistics()

s1, s2, s3, s4, s5 = st.columns(5)
with s1:
    stat_card(
        value=stats.get("total_questions", 0),
        label="Cozulen Soru",
        icon="✏️",
    )
with s2:
    accuracy = stats.get("overall_accuracy", 0)
    accuracy_display = f"%{accuracy * 100:.0f}" if isinstance(accuracy, float) and accuracy <= 1 else f"%{accuracy:.0f}"
    stat_card(
        value=accuracy_display,
        label="Dogruluk Orani",
        icon="🎯",
    )
with s3:
    stat_card(
        value=stats.get("best_streak", 0),
        label="En Iyi Seri",
        icon="🔥",
    )
with s4:
    mastery = stats.get("average_mastery", 0)
    mastery_display = f"%{mastery * 100:.0f}" if isinstance(mastery, float) and mastery <= 1 else f"%{mastery:.0f}"
    stat_card(
        value=mastery_display,
        label="Genel Hakimiyet",
        icon="🏆",
    )
with s5:
    stat_card(
        value=stats.get("topics_practiced", 0),
        label="Calisilan Konu",
        icon="📚",
    )

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ===================================================================
# 3) ONERILEN KONULAR
# ===================================================================
section_header("💡 Senin Icin Oneriler")

recommendations = get_recommendations()

if recommendations:
    rec_cols = st.columns(3)
    for idx, rec in enumerate(recommendations[:3]):
        with rec_cols[idx]:
            topic_slug = rec.get("topic", rec.get("topic_slug", "arithmetic"))
            topic_name = rec.get("topic_name", TOPIC_NAME_TR.get(topic_slug, topic_slug.replace("_", " ").title()))
            mastery_val = rec.get("current_mastery", 0.5)
            reason = rec.get("reason", "Pratik yapmaniz onerilir")
            color = get_topic_color(topic_slug)

            st.markdown(f"""
            <div class="recommendation-card">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    <div style="width:10px; height:10px; border-radius:50%; background:{color};"></div>
                    <div class="rec-topic-name">{topic_name}</div>
                </div>
                <div class="rec-reason">{reason}</div>
            </div>
            """, unsafe_allow_html=True)

            progress_bar(mastery_val, f"Hakimiyet")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if st.button(f"🎯 Pratik Yap", key=f"rec_practice_{idx}", use_container_width=True):
                st.session_state.selected_topic = topic_slug
                st.switch_page("pages/practice.py")
else:
    st.info("Kisisellestirilmis oneriler almak icin birkac pratik oturumu tamamlayin!")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ===================================================================
# 4) PLATFORM OZELLIKLERI (3x3 Grid)
# ===================================================================
section_header("🚀 Platform Ozellikleri")

features = [
    ("🎯", "Adaptif Zorluk",
     "Bayesian Bilgi Takibi (BKT) ile seviyenize gore dinamik olarak ayarlanan zorluk sistemi."),
    ("⚡", "Aninda Geri Bildirim",
     "Her cevabinizdan sonra detayli aciklama ve adim adim cozum rehberi."),
    ("📊", "BKT ile Hakimiyet Takibi",
     "Bayesian Knowledge Tracing algoritmasi ile konu bazli hakimiyet analizi."),
    ("🤖", "AI Hikaye Sorulari",
     "Yapay zeka ile uretilen hikaye tabanli sorularla gercek hayat uygulamalari."),
    ("🏆", "Oyunlastirma",
     "Rozetler, liderlik tablosu, gunluk gorevler ve seri takibi ile motivasyon."),
    ("🔄", "Aralikli Tekrar",
     "Bilimsel aralikli tekrar algoritmasi ile uzun sureli hafiza olusturma."),
    ("📋", "Sinav Hazirlik",
     "LGS ve YKS formatinda deneme sinavlari ve detayli performans analizi."),
    ("👥", "Sosyal Yarisma",
     "Arkadaslarinizla yarisma, takim kurun ve birlikte ogrenin."),
    ("🌍", "Coklu Dil Destegi",
     "Turkce ve Ingilizce dil destegiyle tum ogrenciler icin erisebilir platform."),
]

# 3 satir x 3 sutun
for row_start in range(0, 9, 3):
    cols = st.columns(3)
    for col_idx, col in enumerate(cols):
        feat_idx = row_start + col_idx
        if feat_idx < len(features):
            icon, title, desc = features[feat_idx]
            with col:
                feature_card(icon, title, desc)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ===================================================================
# 5) MEVCUT KONULAR
# ===================================================================
section_header("📚 Mevcut Konular")

st.markdown("""
<p style="color:#666; margin-bottom:18px; font-size:0.95em;">
    Platformda 16 ana konu ve 80'den fazla alt konu bulunmaktadir.
    Bir konuya tiklayarak pratik yapmaya baslayabilirsiniz.
</p>
""", unsafe_allow_html=True)

topics = get_topics()

# 4 sutunluk grid
COLS_PER_ROW = 4
for row_start in range(0, len(topics), COLS_PER_ROW):
    row_topics = topics[row_start:row_start + COLS_PER_ROW]
    cols = st.columns(COLS_PER_ROW)
    for col_idx, col in enumerate(cols):
        if col_idx < len(row_topics):
            t = row_topics[col_idx]
            slug = t.get("slug", "")
            name = TOPIC_NAME_TR.get(slug, t.get("name", slug))
            desc = t.get("description", "")
            grade_start = t.get("grade_range_start", "?")
            grade_end = t.get("grade_range_end", "?")
            color = get_topic_color(slug)

            with col:
                st.markdown(f"""
                <div class="topic-grid-card" style="background: linear-gradient(135deg, {color} 0%, {color}CC 100%);">
                    <div class="topic-grid-name">{name}</div>
                    <div class="topic-grid-desc">{desc}</div>
                    <div class="topic-grid-grade">Sinif {grade_start}-{grade_end}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Pratik Yap", key=f"topic_{slug}", use_container_width=True):
                    st.session_state.selected_topic = slug
                    st.switch_page("pages/practice.py")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ===================================================================
# 6) ALT BILGI (FOOTER)
# ===================================================================
st.markdown("""
<div class="app-footer">
    <strong>TOBB ETU</strong> &mdash; BIL495 / YAP495 Bahar 2025<br>
    <span style="font-size:0.8em; color:#ccc;">Adaptif Matematik Ogrenme Platformu v1.0</span>
</div>
""", unsafe_allow_html=True)
