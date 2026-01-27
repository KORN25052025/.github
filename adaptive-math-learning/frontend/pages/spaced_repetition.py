"""
Aralikli Tekrar (Spaced Repetition) Sayfasi.

SM-2 algoritmasina dayali aralikli tekrar sistemi ile matematik konularini
kalici olarak ogren. Hata defteri, tekrar kuyrugu ve istatistikler.
"""

import streamlit as st
from datetime import datetime, timedelta

from frontend.theme import (
    apply_theme,
    render_sidebar,
    api_get,
    api_post,
    stat_card,
    section_header,
    progress_bar,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Aralikli Tekrar - MathAI",
    page_icon="🔄",
    layout="wide",
)

apply_theme()
render_sidebar("pages/spaced_repetition")

# ---------------------------------------------------------------------------
# Page-specific CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.srs-hero {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 40%, #2c5364 100%);
    border-radius: 20px;
    padding: 40px 36px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 16px 48px rgba(44, 83, 100, 0.45);
    position: relative;
    overflow: hidden;
}
.srs-hero::before {
    content: '';
    position: absolute;
    top: -40%; right: -15%;
    width: 380px; height: 380px;
    background: radial-gradient(circle, rgba(0,210,255,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.srs-hero::after {
    content: '';
    position: absolute;
    bottom: -30%; left: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(118,75,162,0.10) 0%, transparent 70%);
    border-radius: 50%;
}
.srs-hero h1 { color: white !important; font-size: 2.2em; font-weight: 700; margin: 0 0 8px 0; }
.srs-hero p { color: rgba(255,255,255,0.82); font-size: 1.05em; line-height: 1.6; margin: 0; max-width: 700px; }
.srs-hero .srs-badges { margin-top: 16px; display: flex; gap: 10px; flex-wrap: wrap; }
.srs-badge {
    display: inline-block; padding: 6px 16px; border-radius: 24px;
    font-size: 0.85em; font-weight: 600;
    border: 1px solid rgba(255,255,255,0.25);
    background: rgba(255,255,255,0.1); color: white;
    backdrop-filter: blur(4px);
}

.review-item {
    background: white; border-radius: 14px; padding: 20px 24px;
    margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 5px solid #667eea;
    display: flex; align-items: center; gap: 16px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.review-item:hover { transform: translateX(4px); box-shadow: 0 4px 20px rgba(0,0,0,0.10); }
.review-item-overdue { border-left-color: #dc3545; }
.review-item-today { border-left-color: #fd7e14; }
.review-item-upcoming { border-left-color: #28a745; }
.review-item-icon { font-size: 2em; flex-shrink: 0; }
.review-item-content { flex: 1; }
.review-item-topic { font-size: 1.1em; font-weight: 600; color: #333; margin-bottom: 2px; }
.review-item-detail { font-size: 0.85em; color: #666; }
.review-item-urgency { padding: 4px 14px; border-radius: 20px; font-size: 0.8em; font-weight: 600; flex-shrink: 0; }
.urgency-overdue { background: #fee2e2; color: #991b1b; }
.urgency-today { background: #fff3cd; color: #92400e; }
.urgency-upcoming { background: #d1fae5; color: #065f46; }

.quality-card {
    background: white; border-radius: 14px; padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-top: 4px solid #667eea; margin: 16px 0;
}
.quality-title { font-size: 1.15em; font-weight: 600; color: #333; margin-bottom: 12px; }
.quality-desc { font-size: 0.9em; color: #666; margin-bottom: 16px; }

.mastered-chip {
    display: inline-block; padding: 8px 18px; border-radius: 24px;
    font-size: 0.88em; font-weight: 600; margin: 4px;
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    color: #065f46; border: 1px solid #6ee7b7;
}

.error-card {
    background: white; border-radius: 14px; padding: 20px 24px;
    margin-bottom: 14px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 5px solid #dc3545; transition: transform 0.2s;
}
.error-card:hover { transform: translateX(4px); }
.error-card-topic { font-size: 0.8em; font-weight: 600; color: #667eea; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.error-card-question { font-size: 1.05em; font-weight: 500; color: #333; margin-bottom: 10px; line-height: 1.5; }
.error-card-answers { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 8px; }
.error-answer-wrong { padding: 6px 14px; border-radius: 8px; background: #fee2e2; color: #991b1b; font-size: 0.9em; font-weight: 500; }
.error-answer-correct { padding: 6px 14px; border-radius: 8px; background: #d1fae5; color: #065f46; font-size: 0.9em; font-weight: 500; }
.error-card-date { font-size: 0.8em; color: #999; }

.srs-stats-panel {
    background: white; border-radius: 14px; padding: 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #f0f0f0; margin-bottom: 16px;
}
.srs-stats-title { font-size: 1.1em; font-weight: 600; color: #333; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #f0f0f0; }

.srs-footer {
    text-align: center; padding: 32px 0 16px 0;
    color: #999; font-size: 0.85em;
    border-top: 1px solid #f0f0f0; margin-top: 48px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "srs_user_id": "demo_user",
    "srs_active_review_topic": None,
    "srs_review_submitted": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ---------------------------------------------------------------------------
# Quality rating labels (SM-2 algorithm: 0-5)
# ---------------------------------------------------------------------------
QUALITY_LABELS = {
    0: "Tamamen unuttum",
    1: "Yanlis",
    2: "Zor hatirladi",
    3: "Dogru ama zor",
    4: "Dogru",
    5: "Cok kolay",
}

QUALITY_ICONS = {
    0: "❌",
    1: "🚫",
    2: "🤔",
    3: "😌",
    4: "✅",
    5: "🌟",
}

# ---------------------------------------------------------------------------
# Topic Turkish names
# ---------------------------------------------------------------------------
TOPIC_NAME_TR = {
    "arithmetic": "Aritmetik",
    "fractions": "Kesirler",
    "percentages": "Yuzdelik",
    "ratios": "Oran-Oranti",
    "exponents": "Uslu Sayilar",
    "number_theory": "Sayi Teorisi",
    "algebra": "Cebir",
    "inequalities": "Esitsizlikler",
    "systems_of_equations": "Denklem Sistemleri",
    "polynomials": "Polinomlar",
    "functions": "Fonksiyonlar",
    "geometry": "Geometri",
    "coordinate_geometry": "Analitik Geometri",
    "trigonometry": "Trigonometri",
    "statistics": "Istatistik",
    "sets_and_logic": "Kumeler ve Mantik",
}

# ---------------------------------------------------------------------------
# Fallback / demo data
# ---------------------------------------------------------------------------
FALLBACK_REVIEW_QUEUE = [
    {
        "topic": "fractions",
        "subtopic": "Kesir Islemleri",
        "due_date": (datetime.now() - timedelta(days=2)).isoformat(),
        "interval_days": 3,
        "easiness_factor": 2.1,
        "repetitions": 2,
        "last_quality": 3,
        "urgency": "overdue",
    },
    {
        "topic": "algebra",
        "subtopic": "Birinci Derece Denklemler",
        "due_date": datetime.now().isoformat(),
        "interval_days": 1,
        "easiness_factor": 2.5,
        "repetitions": 0,
        "last_quality": None,
        "urgency": "today",
    },
    {
        "topic": "geometry",
        "subtopic": "Ucgen Alani",
        "due_date": datetime.now().isoformat(),
        "interval_days": 1,
        "easiness_factor": 2.3,
        "repetitions": 1,
        "last_quality": 2,
        "urgency": "today",
    },
    {
        "topic": "percentages",
        "subtopic": "Yuzde Problemleri",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "interval_days": 7,
        "easiness_factor": 2.8,
        "repetitions": 5,
        "last_quality": 4,
        "urgency": "upcoming",
    },
    {
        "topic": "statistics",
        "subtopic": "Ortalama ve Medyan",
        "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
        "interval_days": 14,
        "easiness_factor": 2.9,
        "repetitions": 7,
        "last_quality": 5,
        "urgency": "upcoming",
    },
    {
        "topic": "exponents",
        "subtopic": "Us Kurallari",
        "due_date": (datetime.now() - timedelta(days=1)).isoformat(),
        "interval_days": 2,
        "easiness_factor": 1.8,
        "repetitions": 1,
        "last_quality": 1,
        "urgency": "overdue",
    },
    {
        "topic": "ratios",
        "subtopic": "Dogrudan Oranti",
        "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
        "interval_days": 21,
        "easiness_factor": 2.7,
        "repetitions": 8,
        "last_quality": 5,
        "urgency": "upcoming",
    },
]
FALLBACK_STATS = {
    "total_items": 24,
    "mastered_count": 8,
    "learning_count": 12,
    "due_count": 4,
    "total_reviews": 156,
    "streak_days": 7,
    "average_quality": 3.6,
    "retention_rate": 0.78,
    "reviews_today": 3,
    "reviews_this_week": 21,
    "topic_stats": [
        {"topic": "fractions", "reviews": 28, "mastery": 0.85, "avg_quality": 4.1},
        {"topic": "algebra", "reviews": 22, "mastery": 0.72, "avg_quality": 3.5},
        {"topic": "geometry", "reviews": 19, "mastery": 0.65, "avg_quality": 3.2},
        {"topic": "percentages", "reviews": 15, "mastery": 0.90, "avg_quality": 4.4},
        {"topic": "statistics", "reviews": 12, "mastery": 0.92, "avg_quality": 4.6},
        {"topic": "exponents", "reviews": 18, "mastery": 0.55, "avg_quality": 2.8},
        {"topic": "ratios", "reviews": 14, "mastery": 0.88, "avg_quality": 4.2},
        {"topic": "number_theory", "reviews": 10, "mastery": 0.60, "avg_quality": 3.0},
        {"topic": "inequalities", "reviews": 8, "mastery": 0.45, "avg_quality": 2.5},
        {"topic": "trigonometry", "reviews": 6, "mastery": 0.40, "avg_quality": 2.3},
        {"topic": "polynomials", "reviews": 4, "mastery": 0.35, "avg_quality": 2.1},
    ],
    "review_history": [
        {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), "count": max(2, 8 - i)}
        for i in range(7)
    ],
}

FALLBACK_MASTERED = [
    {"topic": "percentages", "mastery_pct": 95, "mastered_date": "2025-12-15", "total_reviews": 32},
    {"topic": "statistics", "mastery_pct": 93, "mastered_date": "2025-12-20", "total_reviews": 28},
    {"topic": "ratios", "mastery_pct": 91, "mastered_date": "2026-01-05", "total_reviews": 25},
    {"topic": "fractions", "mastery_pct": 88, "mastered_date": "2026-01-10", "total_reviews": 40},
    {"topic": "arithmetic", "mastery_pct": 96, "mastered_date": "2025-11-28", "total_reviews": 45},
    {"topic": "sets_and_logic", "mastery_pct": 87, "mastered_date": "2026-01-18", "total_reviews": 20},
    {"topic": "coordinate_geometry", "mastery_pct": 85, "mastered_date": "2026-01-22", "total_reviews": 18},
    {"topic": "functions", "mastery_pct": 82, "mastered_date": "2026-01-25", "total_reviews": 15},
]
FALLBACK_NOTEBOOK = [
    {
        "id": "err_001",
        "topic": "fractions",
        "subtopic": "Kesir Bolmesi",
        "question": "3/4 bolum 2/5 isleminin sonucu kactir?",
        "wrong_answer": "6/20",
        "correct_answer": "15/8",
        "date": "2026-01-25",
        "difficulty": 3,
        "notes": "Bolme isleminde ikinci kesri ters cevirip carpmayi unuttum.",
    },
    {
        "id": "err_002",
        "topic": "algebra",
        "subtopic": "Denklem Cozme",
        "question": "3x + 7 = 22 denkleminde x degeri kactir?",
        "wrong_answer": "3",
        "correct_answer": "5",
        "date": "2026-01-24",
        "difficulty": 2,
        "notes": "Islem sirasinda hata yaptim.",
    },
    {
        "id": "err_003",
        "topic": "geometry",
        "subtopic": "Ucgen Alani",
        "question": "Tabani 12 cm, yuksekligi 8 cm olan ucgenin alani kac cm2?",
        "wrong_answer": "96",
        "correct_answer": "48",
        "date": "2026-01-23",
        "difficulty": 2,
        "notes": "2'ye bolmeyi unuttum. Alan = (taban * yukseklik) / 2",
    },
    {
        "id": "err_004",
        "topic": "exponents",
        "subtopic": "Us Kurallari",
        "question": "2^3 * 2^4 isleminin sonucu kactir?",
        "wrong_answer": "2^12",
        "correct_answer": "2^7 = 128",
        "date": "2026-01-22",
        "difficulty": 3,
        "notes": "Carpimda usler toplanir, carpilmaz.",
    },
    {
        "id": "err_005",
        "topic": "percentages",
        "subtopic": "Yuzde Hesaplama",
        "question": "240 TL'nin %35'i kac TL'dir?",
        "wrong_answer": "72",
        "correct_answer": "84",
        "date": "2026-01-21",
        "difficulty": 2,
        "notes": "240 * 0.35 = 84, 240 * 0.30 = 72 ile karistirdim.",
    },
    {
        "id": "err_006",
        "topic": "number_theory",
        "subtopic": "EBOB-EKOK",
        "question": "12 ve 18 sayilarinin EKOK'u kactir?",
        "wrong_answer": "6",
        "correct_answer": "36",
        "date": "2026-01-20",
        "difficulty": 3,
        "notes": "EBOB ile EKOK karistirildi. EBOB=6, EKOK=36.",
    },
    {
        "id": "err_007",
        "topic": "inequalities",
        "subtopic": "Esitsizlik Cozumu",
        "question": "-2x > 6 esitsizliginin cozum kumesi nedir?",
        "wrong_answer": "x > -3",
        "correct_answer": "x < -3",
        "date": "2026-01-19",
        "difficulty": 4,
        "notes": "Negatif sayiyla bolunce esitsizlik yonu degisir.",
    },
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def get_topic_display_name(slug: str) -> str:
    """Return Turkish display name for a topic slug."""
    return TOPIC_NAME_TR.get(slug, slug.replace("_", " ").title())


def get_urgency_info(urgency: str):
    """Return CSS class, label, and icon for a given urgency level."""
    mapping = {
        "overdue": ("review-item-overdue", "urgency-overdue", "Gecikti", "🔴"),
        "today": ("review-item-today", "urgency-today", "Bugun", "🟠"),
        "upcoming": ("review-item-upcoming", "urgency-upcoming", "Yaklasan", "🟢"),
    }
    return mapping.get(urgency, ("review-item-upcoming", "urgency-upcoming", urgency, "⭕"))


def determine_urgency(due_date_str: str) -> str:
    """Determine urgency from a due date ISO string."""
    try:
        due = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        now = datetime.now()
        if hasattr(due, "tzinfo") and due.tzinfo is not None:
            from datetime import timezone
            now = datetime.now(timezone.utc)
        diff = (due - now).total_seconds()
        if diff < 0:
            return "overdue"
        elif diff < 86400:
            return "today"
        else:
            return "upcoming"
    except Exception:
        return "upcoming"


def format_due_date(due_date_str: str) -> str:
    """Format a due date string for display."""
    try:
        due = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        now = datetime.now()
        diff = due - now
        if diff.total_seconds() < -86400:
            days_ago = abs(diff.days)
            return f"{days_ago} gun gecikti"
        elif diff.total_seconds() < 0:
            return "Bugun (gecikti)"
        elif diff.total_seconds() < 86400:
            return "Bugun"
        elif diff.days == 1:
            return "Yarin"
        else:
            return f"{diff.days} gun sonra"
    except Exception:
        return due_date_str


def render_review_item(item: dict, index: int):
    """Render a single review queue item."""
    topic = item.get("topic", "")
    subtopic = item.get("subtopic", "")
    due_date = item.get("due_date", "")
    interval = item.get("interval_days", 0)
    ef = item.get("easiness_factor", 2.5)
    reps = item.get("repetitions", 0)
    urgency = item.get("urgency", determine_urgency(due_date))

    topic_name = get_topic_display_name(topic)
    item_cls, urg_cls, urg_label, urg_icon = get_urgency_info(urgency)
    due_display = format_due_date(due_date) if due_date else ""

    detail_parts = []
    if subtopic:
        detail_parts.append(subtopic)
    if due_display:
        detail_parts.append(f"Tekrar: {due_display}")
    if interval:
        detail_parts.append(f"Aralik: {interval} gun")
    if reps > 0:
        detail_parts.append(f"Tekrar sayisi: {reps}")

    detail_text = " &middot; ".join(detail_parts)
    icon = "📐"

    st.markdown(f"""
    <div class="review-item {item_cls}">
        <div class="review-item-icon">{icon}</div>
        <div class="review-item-content">
            <div class="review-item-topic">{topic_name}</div>
            <div class="review-item-detail">{detail_text}</div>
        </div>
        <div class="review-item-urgency {urg_cls}">{urg_icon} {urg_label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_error_card(error: dict):
    """Render a single error notebook entry."""
    topic = error.get("topic", "")
    subtopic = error.get("subtopic", "")
    question = error.get("question", "")
    wrong = error.get("wrong_answer", "")
    correct = error.get("correct_answer", "")
    date = error.get("date", "")
    notes = error.get("notes", "")

    topic_name = get_topic_display_name(topic)
    header = topic_name
    if subtopic:
        header += f" - {subtopic}"

    notes_html = ""
    if notes:
        notes_html = f"""
        <div style="margin-top:8px; padding:8px 12px; background:#f8f9fa; border-radius:8px;
                    font-size:0.85em; color:#555; border-left:3px solid #667eea;">
            📝 {notes}
        </div>
        """

    st.markdown(f"""
    <div class="error-card">
        <div class="error-card-topic">{header}</div>
        <div class="error-card-question">{question}</div>
        <div class="error-card-answers">
            <div class="error-answer-wrong">❌ Senin cevabin: {wrong}</div>
            <div class="error-answer-correct">✅ Dogru cevap: {correct}</div>
        </div>
        {notes_html}
        <div class="error-card-date">📅 {date}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================================
# HERO SECTION
# =========================================================================
st.markdown("""
<div class="srs-hero">
    <h1>🔄 Aralikli Tekrar Sistemi</h1>
    <p>
        SM-2 algoritmasina dayali akilli tekrar sistemi ile matematik konularini
        kalici olarak hafizana yerlestir. Unutma egrisini yen, her gun biraz
        daha guclenen bilgiyle sinavlara hazirlan!
    </p>
    <div class="srs-badges">
        <span class="srs-badge">🧠 SM-2 Algoritmasi</span>
        <span class="srs-badge">📈 Adaptif Araliklar</span>
        <span class="srs-badge">📓 Hata Defteri</span>
        <span class="srs-badge">🎯 Kisisel Tekrar Plani</span>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================================
# USER ID INPUT
# =========================================================================
user_id = st.text_input(
    "👤 Kullanici ID",
    value=st.session_state.srs_user_id,
    placeholder="Kullanici ID'nizi girin...",
    key="srs_user_input",
)
st.session_state.srs_user_id = user_id if user_id else "demo_user"
user_id = st.session_state.srs_user_id


# =========================================================================
# FETCH DATA
# =========================================================================
stats_data = api_get(f"/srs/stats/{user_id}")
if stats_data is None:
    stats_data = FALLBACK_STATS

review_queue = api_get(f"/srs/review/{user_id}")
if review_queue is None:
    review_queue = FALLBACK_REVIEW_QUEUE
elif isinstance(review_queue, dict):
    review_queue = review_queue.get("items", review_queue.get("reviews", FALLBACK_REVIEW_QUEUE))

mastered_data = api_get(f"/srs/mastered/{user_id}")
if mastered_data is None:
    mastered_data = FALLBACK_MASTERED
elif isinstance(mastered_data, dict):
    mastered_data = mastered_data.get("topics", mastered_data.get("mastered", FALLBACK_MASTERED))

notebook_data = api_get(f"/srs/notebook/{user_id}")
if notebook_data is None:
    notebook_data = FALLBACK_NOTEBOOK
elif isinstance(notebook_data, dict):
    notebook_data = notebook_data.get("errors", notebook_data.get("entries", FALLBACK_NOTEBOOK))


# =========================================================================
# STATS ROW
# =========================================================================
st.markdown("")
c1, c2, c3, c4 = st.columns(4)

total_reviews = stats_data.get("total_reviews", 0)
mastered_count = stats_data.get("mastered_count", 0)
due_count = stats_data.get("due_count", 0)
streak = stats_data.get("streak_days", 0)

with c1:
    stat_card(str(total_reviews), "Toplam Tekrar", "🔄")
with c2:
    stat_card(str(mastered_count), "Ustalasilmis Konu", "🏆")
with c3:
    stat_card(str(due_count), "Bugun Bekleyen", "📅")
with c4:
    stat_card(f"{streak} gun", "Seri", "🔥")

st.markdown("")


# =========================================================================
# TABS
# =========================================================================
tab_queue, tab_stats, tab_notebook = st.tabs([
    "🔄 Tekrar Kuyrugu",
    "📊 Istatistikler",
    "📓 Hata Defteri",
])

# -------------------------------------------------------------------------
# TAB 1: TEKRAR KUYRUGU (Review Queue)
# -------------------------------------------------------------------------
with tab_queue:

    section_header("Tekrar Kuyrugu")

    if not review_queue:
        st.markdown("""
        <div class="success-box">
            🎉 Tebrikler! Simdilik tekrar edilecek konu bulunmuyor.
            Yeni konular ogrendikce tekrar kuyruguna otomatik olarak eklenecek.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Sort: overdue first, then today, then upcoming
        urgency_order = {"overdue": 0, "today": 1, "upcoming": 2}
        sorted_queue = sorted(
            review_queue,
            key=lambda x: urgency_order.get(
                x.get("urgency", determine_urgency(x.get("due_date", ""))),
                3,
            ),
        )

        # Summary counts
        overdue_count = sum(
            1 for item in sorted_queue
            if item.get("urgency", determine_urgency(item.get("due_date", ""))) == "overdue"
        )
        today_count = sum(
            1 for item in sorted_queue
            if item.get("urgency", determine_urgency(item.get("due_date", ""))) == "today"
        )
        upcoming_count = sum(
            1 for item in sorted_queue
            if item.get("urgency", determine_urgency(item.get("due_date", ""))) == "upcoming"
        )

        sum_c1, sum_c2, sum_c3 = st.columns(3)
        with sum_c1:
            st.markdown(f"""
            <div style="text-align:center; padding:12px; background:#fee2e2; border-radius:10px;">
                <div style="font-size:1.5em; font-weight:700; color:#991b1b;">{overdue_count}</div>
                <div style="font-size:0.85em; color:#991b1b;">Gecikti</div>
            </div>
            """, unsafe_allow_html=True)
        with sum_c2:
            st.markdown(f"""
            <div style="text-align:center; padding:12px; background:#fff3cd; border-radius:10px;">
                <div style="font-size:1.5em; font-weight:700; color:#92400e;">{today_count}</div>
                <div style="font-size:0.85em; color:#92400e;">Bugun</div>
            </div>
            """, unsafe_allow_html=True)
        with sum_c3:
            st.markdown(f"""
            <div style="text-align:center; padding:12px; background:#d1fae5; border-radius:10px;">
                <div style="font-size:1.5em; font-weight:700; color:#065f46;">{upcoming_count}</div>
                <div style="font-size:0.85em; color:#065f46;">Yaklasan</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Render each review item with a review button
        for idx, item in enumerate(sorted_queue):
            render_review_item(item, idx)

            topic = item.get("topic", "")
            topic_name = get_topic_display_name(topic)
            urgency = item.get("urgency", determine_urgency(item.get("due_date", "")))

            # Only show review button for overdue and today items
            if urgency in ("overdue", "today"):
                btn_key = f"review_btn_{idx}_{topic}"
                if st.button(
                    f"🔄 {topic_name} Tekrar Et",
                    key=btn_key,
                    use_container_width=False,
                ):
                    st.session_state.srs_active_review_topic = topic
                    st.session_state.srs_review_submitted = False

            st.markdown("")
    # --- Quality rating section ---
    st.markdown("")
    st.markdown("---")
    section_header("Tekrar Degerlendirmesi")

    active_topic = st.session_state.get("srs_active_review_topic")

    if active_topic:
        active_topic_name = get_topic_display_name(active_topic)

        st.markdown(f"""
        <div class="quality-card">
            <div class="quality-title">🔄 {active_topic_name} - Tekrar Degerlendirmesi</div>
            <div class="quality-desc">
                Bu konuyu tekrar ettikten sonra asagidaki olcekten performansinizi
                degerlendirin. Bu deger SM-2 algoritmasina beslenerek bir sonraki
                tekrar zamaninizi belirler.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quality rating selection
        st.markdown("**Kalite Degerlendirmesi (0-5):**")

        quality_options = [f"{q} - {QUALITY_ICONS[q]} {QUALITY_LABELS[q]}" for q in range(6)]
        selected_quality_str = st.radio(
            "Tekrar kalitenizi secin",
            options=quality_options,
            index=4,
            key="srs_quality_radio",
            label_visibility="collapsed",
        )
        selected_quality = int(selected_quality_str.split(" - ")[0])

        col_submit, col_cancel = st.columns(2)
        with col_submit:
            if st.button(
                "✅ Degerlendirmeyi Gonder",
                type="primary",
                use_container_width=True,
                key="submit_quality",
            ):
                payload = {
                    "user_id": user_id,
                    "topic": active_topic,
                    "quality": selected_quality,
                }
                result = api_post("/srs/review", payload)

                if result:
                    next_review = result.get("next_review_date", "")
                    new_interval = result.get("interval_days", "")
                    st.success(
                        f"Degerlendirme kaydedildi! "
                        f"Sonraki tekrar: {next_review if next_review else 'hesaplaniyor...'}"
                        f"{f' (Aralik: {new_interval} gun)' if new_interval else ''}"
                    )
                else:
                    # Demo mode feedback
                    demo_intervals = {0: 1, 1: 1, 2: 1, 3: 3, 4: 7, 5: 14}
                    demo_interval = demo_intervals.get(selected_quality, 1)
                    st.success(
                        f"Degerlendirme kaydedildi (demo modu)! "
                        f"Sonraki tekrar: {demo_interval} gun sonra."
                    )

                st.session_state.srs_active_review_topic = None
                st.session_state.srs_review_submitted = True

        with col_cancel:
            if st.button(
                "❌ Iptal",
                use_container_width=True,
                key="cancel_quality",
            ):
                st.session_state.srs_active_review_topic = None

    else:
        if st.session_state.srs_review_submitted:
            st.markdown("""
            <div class="success-box">
                ✅ Degerlendirmeniz basariyla kaydedildi! Bir sonraki konuyu secebilirsiniz.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                💡 Tekrar etmek istediginiz konunun yanindaki
                <strong>"Tekrar Et"</strong> butonuna tiklayin.
                Tekrar sonrasi performansinizi degerlendirerek SM-2 algoritmasi
                bir sonraki tekrar zamaninizi otomatik olarak belirleyecektir.
            </div>
            """, unsafe_allow_html=True)
    # --- Manual review recording ---
    st.markdown("")
    with st.expander("📝 Manuel Tekrar Kaydi", expanded=False):
        st.markdown(
            "Kendi basina tekrar yaptiginiz bir konuyu manuel olarak kaydedin."
        )

        with st.form("manual_review_form", clear_on_submit=True):
            topic_options = list(TOPIC_NAME_TR.values())
            topic_slugs = list(TOPIC_NAME_TR.keys())

            manual_topic_display = st.selectbox(
                "Konu",
                options=topic_options,
                key="manual_topic",
            )
            manual_topic_idx = topic_options.index(manual_topic_display)
            manual_topic_slug = topic_slugs[manual_topic_idx]

            manual_subtopic = st.text_input(
                "Alt Konu (opsiyonel)",
                placeholder="ornek: Kesir Islemleri",
                key="manual_subtopic",
            )

            manual_correct = st.checkbox(
                "Dogru cevapladim",
                value=True,
                key="manual_correct",
            )

            manual_difficulty = st.slider(
                "Zorluk (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                key="manual_difficulty",
            )

            manual_time = st.number_input(
                "Cevap suresi (milisaniye, opsiyonel)",
                min_value=0,
                max_value=600000,
                value=0,
                step=1000,
                key="manual_time",
            )

            manual_submit = st.form_submit_button(
                "💾 Kaydet",
                type="primary",
                use_container_width=True,
            )

        if manual_submit:
            payload = {
                "user_id": user_id,
                "topic": manual_topic_slug,
                "is_correct": manual_correct,
                "difficulty": manual_difficulty,
            }
            if manual_subtopic:
                payload["subtopic"] = manual_subtopic
            if manual_time > 0:
                payload["response_time_ms"] = manual_time

            result = api_post("/srs/record", payload)
            if result:
                st.success("Tekrar basariyla kaydedildi!")
            else:
                st.success("Tekrar kaydedildi (demo modu).")

# -------------------------------------------------------------------------
# TAB 2: ISTATISTIKLER (Statistics)
# -------------------------------------------------------------------------
with tab_stats:

    section_header("Genel Bakis")

    # Main stats
    s_c1, s_c2, s_c3, s_c4 = st.columns(4)
    with s_c1:
        stat_card(
            str(stats_data.get("total_items", 0)),
            "Toplam Konu",
            "📚",
        )
    with s_c2:
        stat_card(
            str(stats_data.get("mastered_count", 0)),
            "Ustalasilmis",
            "🏆",
        )
    with s_c3:
        stat_card(
            str(stats_data.get("learning_count", 0)),
            "Ogreniyor",
            "📖",
        )
    with s_c4:
        stat_card(
            str(stats_data.get("due_count", 0)),
            "Bekleyen Tekrar",
            "⏰",
        )

    st.markdown("")

    # Secondary stats row
    s2_c1, s2_c2, s2_c3, s2_c4 = st.columns(4)
    with s2_c1:
        avg_q = stats_data.get("average_quality", 0)
        stat_card(f"{avg_q:.1f}", "Ort. Kalite (0-5)", "⭐")
    with s2_c2:
        retention = stats_data.get("retention_rate", 0)
        stat_card(f"%{int(retention * 100)}", "Hatirlama Orani", "🧠")
    with s2_c3:
        today_rev = stats_data.get("reviews_today", 0)
        stat_card(str(today_rev), "Bugunun Tekrarlari", "📅")
    with s2_c4:
        week_rev = stats_data.get("reviews_this_week", 0)
        stat_card(str(week_rev), "Bu Haftanin Tekrarlari", "🗓️")

    st.markdown("")
    st.markdown("---")

    # --- Mastered topics ---
    section_header("Ustalasilmis Konular")

    if mastered_data:
        mastered_html_items = []
        for m in mastered_data:
            topic = m.get("topic", "")
            pct = m.get("mastery_pct", 0)
            topic_name = get_topic_display_name(topic)
            mastered_html_items.append(
                f'<span class="mastered-chip">🏆 {topic_name} (%{pct})</span>'
            )

        st.markdown(
            '<div style="margin-bottom:16px;">' + " ".join(mastered_html_items) + "</div>",
            unsafe_allow_html=True,
        )

        # Detailed mastery table
        st.markdown("")
        for m in mastered_data:
            topic = m.get("topic", "")
            pct = m.get("mastery_pct", 0)
            topic_name = get_topic_display_name(topic)
            reviews = m.get("total_reviews", 0)
            mastered_date = m.get("mastered_date", "")

            col_m1, col_m2 = st.columns([3, 1])
            with col_m1:
                progress_bar(pct / 100, f"{topic_name}: {reviews} tekrar")
            with col_m2:
                st.markdown(
                    f'<div style="text-align:right; padding-top:4px; '
                    f'font-size:0.85em; color:#666;">'
                    f'📅 {mastered_date}</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.markdown("""
        <div class="info-box">
            💡 Henuz ustalasilmis konu bulunmuyor.
            Duzenli tekrar yaparak konularda ustalik seviyesine ulasin!
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("---")
    # --- Topic-level statistics ---
    section_header("Konu Bazli Istatistikler")

    topic_stats = stats_data.get("topic_stats", [])
    if topic_stats:
        # Sort by mastery descending
        sorted_topics = sorted(topic_stats, key=lambda x: x.get("mastery", 0), reverse=True)

        for ts in sorted_topics:
            topic = ts.get("topic", "")
            topic_name = get_topic_display_name(topic)
            reviews = ts.get("reviews", 0)
            mastery = ts.get("mastery", 0)
            avg_q = ts.get("avg_quality", 0)

            col_t1, col_t2, col_t3 = st.columns([3, 1, 1])
            with col_t1:
                progress_bar(mastery, f"{topic_name}")
            with col_t2:
                st.markdown(
                    f'<div style="text-align:center; font-size:0.85em; color:#666;">'
                    f'{reviews} tekrar</div>',
                    unsafe_allow_html=True,
                )
            with col_t3:
                # Color-code average quality
                q_color = "#28a745" if avg_q >= 4 else ("#fd7e14" if avg_q >= 3 else "#dc3545")
                st.markdown(
                    f'<div style="text-align:center; font-size:0.85em; '
                    f'color:{q_color}; font-weight:600;">'
                    f'Ort: {avg_q:.1f}</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.info("Henuz konu bazli istatistik bulunmuyor.")

    st.markdown("")
    st.markdown("---")

    # --- Review history ---
    section_header("Tekrar Gecmisi")

    review_history = stats_data.get("review_history", [])
    if review_history:
        st.markdown("""
        <div class="srs-stats-panel">
            <div class="srs-stats-title">📈 Son 7 Gunluk Tekrar Aktivitesi</div>
        """, unsafe_allow_html=True)

        # Simple bar chart representation
        max_count = max(h.get("count", 0) for h in review_history) if review_history else 1
        for h in review_history:
            date_str = h.get("date", "")
            count = h.get("count", 0)
            bar_width = int((count / max(max_count, 1)) * 100)

            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                day_names_tr = {
                    0: "Pzt", 1: "Sal", 2: "Car",
                    3: "Per", 4: "Cum", 5: "Cmt", 6: "Paz",
                }
                day_label = day_names_tr.get(dt.weekday(), date_str)
                date_display = f"{day_label} ({dt.strftime('%d/%m')})"
            except Exception:
                date_display = date_str

            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:12px; padding:6px 0;">
                <div style="width:100px; font-size:0.85em; color:#666; text-align:right;">{date_display}</div>
                <div style="flex:1; background:#e9ecef; border-radius:6px; height:20px; overflow:hidden;">
                    <div style="width:{bar_width}%; height:100%; border-radius:6px;
                                background:linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                                transition:width 0.5s ease;"></div>
                </div>
                <div style="width:40px; font-size:0.85em; font-weight:600; color:#667eea;">{count}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Henuz tekrar gecmisi bulunmuyor. Tekrar yapmaya baslayin!")

# -------------------------------------------------------------------------
# TAB 3: HATA DEFTERI (Error Notebook)
# -------------------------------------------------------------------------
with tab_notebook:

    section_header("Hata Defteri")

    st.markdown("""
    <div class="info-box" style="margin-bottom:20px;">
        📓 Hata defteriniz, yanlis yaptiginiz sorulari otomatik olarak kaydeder.
        Bu hatalari tekrar ederek ayni hatalari tekrarlamamayi ogrenir,
        zayif noktalarinizi guclendirebilirsiniz.
    </div>
    """, unsafe_allow_html=True)

    if not notebook_data:
        st.markdown("""
        <div class="success-box">
            🎉 Hata defteriniz bos! Henuz hata kaydedilmemis veya
            tum hatalari basariyla tekrar ettiniz.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Filters
        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            all_topics_in_notebook = sorted(set(
                e.get("topic", "") for e in notebook_data if e.get("topic")
            ))
            topic_filter_options = ["Tumu"] + [
                get_topic_display_name(t) for t in all_topics_in_notebook
            ]
            selected_filter = st.selectbox(
                "Konuya Gore Filtrele",
                options=topic_filter_options,
                key="notebook_topic_filter",
            )

        with filter_col2:
            sort_options = ["Tarihe Gore (Yeni)", "Tarihe Gore (Eski)", "Konuya Gore"]
            selected_sort = st.selectbox(
                "Siralama",
                options=sort_options,
                key="notebook_sort",
            )

        # Apply filter
        filtered_notebook = notebook_data
        if selected_filter != "Tumu":
            # Reverse lookup: display name to slug
            filter_slug = None
            for slug, name in TOPIC_NAME_TR.items():
                if name == selected_filter:
                    filter_slug = slug
                    break
            if filter_slug:
                filtered_notebook = [
                    e for e in filtered_notebook if e.get("topic") == filter_slug
                ]

        # Apply sort
        if selected_sort == "Tarihe Gore (Yeni)":
            filtered_notebook = sorted(
                filtered_notebook,
                key=lambda x: x.get("date", ""),
                reverse=True,
            )
        elif selected_sort == "Tarihe Gore (Eski)":
            filtered_notebook = sorted(
                filtered_notebook,
                key=lambda x: x.get("date", ""),
            )
        elif selected_sort == "Konuya Gore":
            filtered_notebook = sorted(
                filtered_notebook,
                key=lambda x: get_topic_display_name(x.get("topic", "")),
            )

        # Summary
        st.markdown(
            f"**{len(filtered_notebook)}** hata kaydi bulundu.",
        )
        st.markdown("")

        # Render each error with a repeat button
        for err_idx, error in enumerate(filtered_notebook):
            render_error_card(error)

            error_topic = error.get("topic", "")
            error_id = error.get("id", f"err_{err_idx}")

            if st.button(
                f"🔄 Tekrar Et - {get_topic_display_name(error_topic)}",
                key=f"repeat_error_{error_id}_{err_idx}",
            ):
                # Record the repeat attempt via API
                payload = {
                    "user_id": user_id,
                    "topic": error_topic,
                    "quality": 0,  # Start with quality 0, user will re-evaluate
                }
                if error.get("subtopic"):
                    payload["subtopic"] = error["subtopic"]

                result = api_post("/srs/review", payload)

                if result:
                    st.success(
                        f"'{get_topic_display_name(error_topic)}' konusu tekrar kuyrugunuza eklendi!"
                    )
                else:
                    st.success(
                        f"'{get_topic_display_name(error_topic)}' konusu tekrar kuyrugunuza eklendi (demo modu)."
                    )

                # Also set as active review topic
                st.session_state.srs_active_review_topic = error_topic
                st.info(
                    "Tekrar Kuyrugu sekmesinden degerlendirmenizi yapabilirsiniz."
                )

            st.markdown("")

# =========================================================================
# FOOTER
# =========================================================================
st.markdown("""
<div class="srs-footer">
    <p>
        🔄 <strong>Aralikli Tekrar Sistemi</strong> &middot;
        SM-2 algoritmasiyla desteklenen kisisellestirilmis tekrar plani &middot;
        MathAI Adaptif Matematik Platformu
    </p>
    <p style="margin-top:4px;">
        💡 Ipucu: Duzenli tekrar yaparak unutma egrisini yenin.
        Her gun en az 5 dakika tekrar yapmak, uzun vadeli basarinin anahtaridir.
    </p>
</div>
""", unsafe_allow_html=True)