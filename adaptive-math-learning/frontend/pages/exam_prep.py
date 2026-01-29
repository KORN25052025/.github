"""
Sinav Hazirlik ve Seviye Testi Sayfasi.

LGS/YKS sinav hazirligi ve adaptif seviye belirleme testi.
Turkiye ulusal matematik sinavlarina yonelik kapsamli hazirlik platformu.
"""

import streamlit as st
import time
import html as html_module
from typing import Optional, Dict, Any, List

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
    page_title="Sinav Hazirlik - MathAI",
    page_icon="\U0001f4cb",
    layout="wide",
)

apply_theme()
render_sidebar("exam_prep")

# ---------------------------------------------------------------------------
# Additional page-specific CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
/* Exam hero gradient */
.exam-hero {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    border-radius: 20px;
    padding: 40px 36px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 16px 48px rgba(48, 43, 99, 0.4);
    position: relative;
    overflow: hidden;
}
.exam-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(102,126,234,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.exam-hero h1 {
    color: white !important;
    font-size: 2.2em;
    font-weight: 700;
    margin: 0 0 8px 0;
}
.exam-hero p {
    color: rgba(255,255,255,0.8);
    font-size: 1.05em;
    line-height: 1.6;
    margin: 0;
    max-width: 700px;
}
.exam-hero .exam-badges {
    margin-top: 16px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.exam-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 24px;
    font-size: 0.85em;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.25);
    background: rgba(255,255,255,0.1);
    color: white;
    backdrop-filter: blur(4px);
}

/* Exam type selector cards */
.exam-type-card {
    background: white;
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 3px 16px rgba(0,0,0,0.08);
    border: 2px solid transparent;
    transition: all 0.25s ease;
    cursor: pointer;
}
.exam-type-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(0,0,0,0.12);
    border-color: #667eea;
}
.exam-type-card.active {
    border-color: #667eea;
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
}
.exam-type-icon {
    font-size: 2.4em;
    margin-bottom: 8px;
}
.exam-type-title {
    font-size: 1.15em;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 4px;
}
.exam-type-desc {
    font-size: 0.8em;
    color: #666;
    line-height: 1.4;
}

/* Topic weight bar */
.topic-weight-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #f0f0f0;
}
.topic-weight-row:last-child {
    border-bottom: none;
}
.topic-weight-name {
    font-weight: 600;
    color: #333;
    width: 160px;
    flex-shrink: 0;
    font-size: 0.92em;
}
.topic-weight-bar-bg {
    flex: 1;
    background: #e9ecef;
    border-radius: 8px;
    height: 12px;
    overflow: hidden;
}
.topic-weight-bar-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 0.6s ease;
}
.topic-weight-pct {
    font-weight: 700;
    color: #667eea;
    width: 50px;
    text-align: right;
    font-size: 0.92em;
}

/* Question card */
.exam-question-card {
    background: white;
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-left: 5px solid #667eea;
    margin: 16px 0;
}
.exam-question-number {
    font-size: 0.85em;
    font-weight: 600;
    color: #667eea;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.exam-question-topic {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75em;
    font-weight: 600;
    background: #ede9fe;
    color: #5b21b6;
    margin-bottom: 12px;
}
.exam-question-text {
    font-size: 1.15em;
    color: #1a1a2e;
    line-height: 1.6;
    margin-bottom: 4px;
}

/* Result card */
.result-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    text-align: center;
}
.result-score {
    font-size: 3em;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}
.result-label {
    font-size: 0.9em;
    color: #666;
    margin-top: 4px;
}

/* Diagnostic flow */
.diag-progress-container {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}
.diag-progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.diag-progress-title {
    font-weight: 600;
    color: #333;
    font-size: 0.95em;
}
.diag-progress-count {
    font-weight: 700;
    color: #667eea;
    font-size: 0.95em;
}

/* Strength/weakness chip */
.mastery-chip {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82em;
    font-weight: 600;
    margin: 4px;
}
.mastery-chip-strong {
    background: #d1fae5;
    color: #065f46;
}
.mastery-chip-weak {
    background: #fee2e2;
    color: #991b1b;
}
.mastery-chip-mid {
    background: #fef3c7;
    color: #92400e;
}

/* Timer display */
.timer-display {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: #f8fafc;
    border-radius: 12px;
    padding: 12px 20px;
    text-align: center;
    font-family: 'Courier New', monospace;
    font-size: 1.6em;
    font-weight: 700;
    letter-spacing: 2px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.timer-label {
    font-size: 0.45em;
    font-weight: 400;
    letter-spacing: 1px;
    color: rgba(248,250,252,0.7);
    display: block;
    margin-bottom: 2px;
    font-family: 'Inter', sans-serif;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

def init_session_state():
    """Initialize all session state keys used by this page."""
    defaults = {
        "exam_type": "LGS",
        "mock_session": None,
        "mock_questions": [],
        "mock_current_idx": 0,
        "mock_answers": {},
        "mock_completed": False,
        "mock_result": None,
        "mock_start_time": None,
        "diag_session_id": None,
        "diag_current_question": None,
        "diag_questions_answered": 0,
        "diag_progress": 0.0,
        "diag_completed": False,
        "diag_result": None,
        "diag_last_feedback": None,
        "diag_grade_level": 8,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ---------------------------------------------------------------------------
# Exam type metadata
# ---------------------------------------------------------------------------

EXAM_TYPE_META = {
    "LGS": {
        "icon": "\U0001f3eb",
        "title": "LGS",
        "full_name": "Liselere Gecis Sinavi",
        "desc": "8. sinif - Liseye gecis sinavi",
        "questions": 20,
        "duration": "40 dk",
        "api_key": "lgs",
    },
    "YKS-TYT": {
        "icon": "\U0001f393",
        "title": "YKS-TYT",
        "full_name": "Temel Yeterlilik Testi",
        "desc": "Universite giris - Temel matematik",
        "questions": 40,
        "duration": "75 dk",
        "api_key": "tyt",
    },
    "YKS-AYT": {
        "icon": "\U0001f3af",
        "title": "YKS-AYT",
        "full_name": "Alan Yeterlilik Testi",
        "desc": "Universite giris - Ileri matematik",
        "questions": 40,
        "duration": "75 dk",
        "api_key": "ayt",
    },
}

TOPIC_BAR_COLORS = [
    "#667eea", "#764ba2", "#f093fb", "#4facfe",
    "#43e97b", "#fa709a", "#fee140", "#a18cd1",
]

# Turkish translations for MasteryLevel enum values
MASTERY_LEVEL_TR = {
    "not_assessed": "Degerlendirilmedi",
    "novice": "Baslangic",
    "beginner": "Temel",
    "intermediate": "Orta",
    "advanced": "Ileri",
    "expert": "Uzman",
}

# Turkish translations for topic slugs
TOPIC_NAME_TR = {
    "arithmetic": "Aritmetik",
    "fractions": "Kesirler",
    "percentages": "Yuzdelik",
    "ratios": "Oranlar",
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
    "sayilar": "Sayilar",
    "cebir": "Cebir",
    "geometri": "Geometri",
    "veri_olasilik": "Veri-Olasilik",
    "olcme": "Olcme",
    "kesirler": "Kesirler",
    "temel_matematik": "Temel Matematik",
    "veri": "Veri Analizi",
    "fonksiyonlar": "Fonksiyonlar",
    "trigonometri": "Trigonometri",
    "analitik_geometri": "Analitik Geometri",
    "diziler": "Diziler",
    "limit_turev_integral": "Limit-Turev-Integral",
}


# ---------------------------------------------------------------------------
# Fallback data (used when API is unreachable)
# ---------------------------------------------------------------------------

FALLBACK_TOPIC_WEIGHTS = {
    "lgs": [
        {"topic_slug": "sayilar", "topic_name_tr": "Sayilar", "weight": 0.15},
        {"topic_slug": "cebir", "topic_name_tr": "Cebir", "weight": 0.20},
        {"topic_slug": "geometri", "topic_name_tr": "Geometri", "weight": 0.25},
        {"topic_slug": "veri_olasilik", "topic_name_tr": "Veri-Olasilik", "weight": 0.15},
        {"topic_slug": "olcme", "topic_name_tr": "Olcme", "weight": 0.15},
        {"topic_slug": "kesirler", "topic_name_tr": "Kesirler", "weight": 0.10},
    ],
    "tyt": [
        {"topic_slug": "temel_matematik", "topic_name_tr": "Temel Matematik", "weight": 0.30},
        {"topic_slug": "geometri", "topic_name_tr": "Geometri", "weight": 0.25},
        {"topic_slug": "sayilar", "topic_name_tr": "Sayilar", "weight": 0.20},
        {"topic_slug": "cebir", "topic_name_tr": "Cebir", "weight": 0.15},
        {"topic_slug": "veri", "topic_name_tr": "Veri Analizi", "weight": 0.10},
    ],
    "ayt": [
        {"topic_slug": "fonksiyonlar", "topic_name_tr": "Fonksiyonlar", "weight": 0.20},
        {"topic_slug": "trigonometri", "topic_name_tr": "Trigonometri", "weight": 0.15},
        {"topic_slug": "analitik_geometri", "topic_name_tr": "Analitik Geometri", "weight": 0.15},
        {"topic_slug": "diziler", "topic_name_tr": "Diziler", "weight": 0.10},
        {"topic_slug": "limit_turev_integral", "topic_name_tr": "Limit-Turev-Integral", "weight": 0.25},
        {"topic_slug": "sayilar", "topic_name_tr": "Sayilar", "weight": 0.15},
    ],
}

FALLBACK_STATS = {
    "total_sessions": 0,
    "total_questions_answered": 0,
    "overall_accuracy": 0.0,
    "average_net_score": 0.0,
    "best_net_score": 0.0,
    "average_time_per_question_seconds": 0.0,
    "topic_accuracy": {},
    "score_trend": [],
    "last_session_at": None,
}


# ---------------------------------------------------------------------------
# Helper: render topic weight bars
# ---------------------------------------------------------------------------

def render_topic_weights(weights: List[Dict]):
    """Render a visually appealing topic-weight bar chart."""
    if not weights:
        st.info("Konu agirliklari yuklenemedi.")
        return

    # Sort by weight descending
    sorted_weights = sorted(weights, key=lambda w: w.get("weight", 0), reverse=True)
    max_weight = max(w.get("weight", 0) for w in sorted_weights) if sorted_weights else 1

    rows_html = ""
    for i, tw in enumerate(sorted_weights):
        name = tw.get("topic_name_tr", tw.get("topic_slug", ""))
        weight = tw.get("weight", 0)
        pct = int(weight * 100)
        bar_width = int((weight / max_weight) * 100) if max_weight > 0 else 0
        color = TOPIC_BAR_COLORS[i % len(TOPIC_BAR_COLORS)]

        rows_html += f"""
        <div class="topic-weight-row">
            <div class="topic-weight-name">{name}</div>
            <div class="topic-weight-bar-bg">
                <div class="topic-weight-bar-fill" style="width:{bar_width}%; background:{color};"></div>
            </div>
            <div class="topic-weight-pct">%{pct}</div>
        </div>
        """

    st.markdown(f"""
    <div style="background:white; border-radius:14px; padding:20px 24px;
                box-shadow:0 2px 12px rgba(0,0,0,0.06); margin-top:12px;">
        <div style="font-weight:600; color:#333; font-size:1em; margin-bottom:12px;">
            Konu Dagilimi (MEB Mufredat Agirliklari)
        </div>
        {rows_html}
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper: format timer
# ---------------------------------------------------------------------------

def format_timer(seconds: float) -> str:
    """Format seconds into MM:SS display."""
    if seconds <= 0:
        return "00:00"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


# ---------------------------------------------------------------------------
# TAB 1: Sinav Hazirlik
# ---------------------------------------------------------------------------

def render_exam_prep_tab():
    """Render the exam preparation tab content."""

    # --- Exam type selector ---
    section_header("Sinav Turu Secin")

    exam_type_display = st.selectbox(
        "Sinav Turu",
        list(EXAM_TYPE_META.keys()),
        index=list(EXAM_TYPE_META.keys()).index(st.session_state.exam_type),
        key="exam_type_selector",
        label_visibility="collapsed",
    )
    st.session_state.exam_type = exam_type_display
    meta = EXAM_TYPE_META[exam_type_display]

    # Exam info card
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        stat_card(meta["icon"], meta["full_name"], "")
    with col_info2:
        stat_card(f"{meta['questions']}", "Soru Sayisi", "\u2753")
    with col_info3:
        stat_card(meta["duration"], "Sure", "\u23f0")

    st.markdown("")

    # --- Topic weights ---
    section_header("Konu Agirliklari")

    api_key = meta["api_key"]
    weights_data = api_get(f"/exam/topics/{api_key}")
    if weights_data is None:
        weights_data = FALLBACK_TOPIC_WEIGHTS.get(api_key, [])
        if not isinstance(weights_data, list):
            weights_data = weights_data.get("topics", []) if isinstance(weights_data, dict) else []
    elif isinstance(weights_data, dict):
        weights_data = weights_data.get("topics", weights_data.get("weights", []))

    render_topic_weights(weights_data if isinstance(weights_data, list) else [])

    st.markdown("")
    st.markdown("---")

    # --- Mock exam section ---
    section_header("Deneme Sinavi")

    if not st.session_state.mock_session or st.session_state.mock_completed:
        st.markdown(f"""
        <div class="info-box">
            <strong>{meta['full_name']}</strong> formatinda tam bir deneme sinavi olusturun.
            Sinav <strong>{meta['questions']} soru</strong> ve <strong>{meta['duration']}</strong> sureden
            olusmaktadir. Sorular MEB mufredat agirliklarini yansitir.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        if st.button(
            f"{meta['icon']}  Deneme Sinavi Olustur ({meta['title']})",
            type="primary",
            use_container_width=True,
            key="generate_mock",
        ):
            with st.spinner("Deneme sinavi hazirlaniyor..."):
                result = api_post(f"/exam/mock/{api_key}")

            if result:
                st.session_state.mock_session = result
                questions = result.get("questions", [])
                st.session_state.mock_questions = questions
                st.session_state.mock_current_idx = 0
                st.session_state.mock_answers = {}
                st.session_state.mock_completed = False
                st.session_state.mock_result = None
                st.session_state.mock_start_time = time.time()
                st.rerun()
            else:
                st.error(
                    "Deneme sinavi olusturulamadi. Lutfen API sunucusunun "
                    "calistigindan emin olun."
                )

        # Show previous result if exists
        if st.session_state.mock_result:
            render_mock_result(st.session_state.mock_result)

    else:
        # Active mock exam
        render_active_mock_exam()

    st.markdown("")
    st.markdown("---")

    # --- Statistics section ---
    section_header("Sinav Istatistikleri")

    user_id = "current_user"
    stats = api_get(f"/exam/stats/{user_id}/{api_key}")
    if stats is None:
        stats = FALLBACK_STATS

    render_exam_stats(stats, api_key)


def render_active_mock_exam():
    """Render the active mock exam question flow."""
    session = st.session_state.mock_session
    questions = st.session_state.mock_questions
    current_idx = st.session_state.mock_current_idx
    total = len(questions)

    if total == 0:
        st.warning("Sinav sorulari yuklenemedi.")
        if st.button("Geri Don", key="mock_back_empty"):
            st.session_state.mock_session = None
            st.rerun()
        return

    # Timer
    time_limit = session.get("time_limit_minutes", 40) * 60
    elapsed = time.time() - (st.session_state.mock_start_time or time.time())
    remaining = max(0, time_limit - elapsed)

    col_timer, col_progress = st.columns([1, 3])

    with col_timer:
        timer_color = "#ef4444" if remaining < 300 else "#f8fafc"
        st.markdown(f"""
        <div class="timer-display" style="{'background: linear-gradient(135deg, #dc2626, #b91c1c) !important;' if remaining < 300 else ''}">
            <span class="timer-label">KALAN SURE</span>
            {format_timer(remaining)}
        </div>
        """, unsafe_allow_html=True)

    with col_progress:
        answered_count = len(st.session_state.mock_answers)
        progress_bar(answered_count / max(total, 1), f"Ilerleme: {answered_count}/{total} soru cevaplandi")
        st.markdown("")

    # Navigation
    col_nav_prev, col_nav_info, col_nav_next = st.columns([1, 2, 1])

    with col_nav_prev:
        if st.button("Onceki Soru", disabled=current_idx == 0, use_container_width=True, key="prev_q"):
            st.session_state.mock_current_idx = max(0, current_idx - 1)
            st.rerun()

    with col_nav_info:
        st.markdown(
            f"<div style='text-align:center; padding:8px; font-weight:600; color:#333;'>"
            f"Soru {current_idx + 1} / {total}</div>",
            unsafe_allow_html=True,
        )

    with col_nav_next:
        if current_idx < total - 1:
            if st.button("Sonraki Soru", use_container_width=True, key="next_q"):
                st.session_state.mock_current_idx = min(total - 1, current_idx + 1)
                st.rerun()
        else:
            if st.button("Sinavi Bitir", type="primary", use_container_width=True, key="finish_exam"):
                finish_mock_exam()
                st.rerun()

    # Current question
    if current_idx < total:
        question = questions[current_idx]
        render_exam_question(question, current_idx, total)

    # Question navigator (mini grid)
    st.markdown("")
    section_header("Soru Navigasyonu")
    cols_per_row = 10
    for row_start in range(0, total, cols_per_row):
        cols = st.columns(min(cols_per_row, total - row_start))
        for j, col in enumerate(cols):
            q_idx = row_start + j
            with col:
                is_answered = (q_idx + 1) in st.session_state.mock_answers or q_idx in st.session_state.mock_answers
                is_current = q_idx == current_idx
                btn_type = "primary" if is_current else "secondary"
                label = f"{'*' if is_answered else ''}{q_idx + 1}"
                if st.button(label, key=f"nav_{q_idx}", use_container_width=True, type=btn_type):
                    st.session_state.mock_current_idx = q_idx
                    st.rerun()

    # Emergency finish button
    st.markdown("")
    col_abandon, col_finish = st.columns(2)
    with col_abandon:
        if st.button("Sinavi Iptal Et", key="abandon_exam", use_container_width=True):
            st.session_state.mock_session = None
            st.session_state.mock_completed = False
            st.session_state.mock_result = None
            st.rerun()
    with col_finish:
        if st.button("Sinavi Bitir ve Degerlendır", type="primary", key="finish_exam_bottom", use_container_width=True):
            finish_mock_exam()
            st.rerun()


def render_exam_question(question: Dict, idx: int, total: int):
    """Render a single exam question with answer input."""
    q_data = question.get("question", question)
    q_num = question.get("question_number", idx + 1)
    topic_tr = question.get("topic_name_tr", "")
    topic_slug = question.get("topic_slug", "")

    expression = q_data.get("expression", "")
    question_text = q_data.get("question_text", "")
    story_text = q_data.get("story_text", "")

    topic_display = topic_tr or TOPIC_NAME_TR.get(topic_slug, topic_slug)

    st.markdown(f"""
    <div class="exam-question-card">
        <div class="exam-question-number">Soru {q_num}</div>
        <span class="exam-question-topic">{html_module.escape(str(topic_display))}</span>
        {f'<div style="color:#555; font-size:0.95em; margin-bottom:10px; line-height:1.5;">{html_module.escape(str(story_text))}</div>' if story_text else ''}
        {f'<div class="exam-question-text">{html_module.escape(str(question_text))}</div>' if question_text else ''}
    </div>
    """, unsafe_allow_html=True)

    if expression:
        expr_display = expression.replace("*", " x ").replace("/", " / ")
        st.latex(expr_display)

    # Answer input
    current_answer = st.session_state.mock_answers.get(q_num, "")
    answer = st.text_input(
        "Cevabin:",
        value=str(current_answer) if current_answer else "",
        key=f"answer_{idx}",
        placeholder="Cevabin buraya yaz...",
    )

    if answer:
        st.session_state.mock_answers[q_num] = answer


def finish_mock_exam():
    """Submit all answers and get exam results."""
    session = st.session_state.mock_session
    if not session:
        return

    session_id = session.get("session_id", "")
    answers = st.session_state.mock_answers

    # Try to submit to API
    result = api_post(f"/exam/evaluate/{session_id}", {"answers": answers})

    if result:
        st.session_state.mock_result = result
    else:
        # Build a local approximation of results
        questions = st.session_state.mock_questions
        total = len(questions)
        correct = 0
        topic_results_map = {}

        for q in questions:
            q_data = q.get("question", q)
            q_num = q.get("question_number", 0)
            correct_answer = q_data.get("correct_answer", "")
            user_answer = str(answers.get(q_num, "")).strip()
            topic = q.get("topic_name_tr", q.get("topic_slug", ""))

            is_correct = user_answer.lower() == str(correct_answer).strip().lower()
            if is_correct:
                correct += 1

            if topic not in topic_results_map:
                topic_results_map[topic] = {"total": 0, "correct": 0, "topic_name_tr": topic}
            topic_results_map[topic]["total"] += 1
            if is_correct:
                topic_results_map[topic]["correct"] += 1

        unanswered = total - len(answers)
        wrong = len(answers) - correct

        st.session_state.mock_result = {
            "total_questions": total,
            "correct_answers": correct,
            "wrong_answers": wrong,
            "unanswered": unanswered,
            "raw_score": correct / max(total, 1),
            "net_score": correct - (wrong / 4.0) if st.session_state.exam_type != "LGS" else correct / max(total, 1),
            "topic_results": [
                {
                    "topic_name_tr": v["topic_name_tr"],
                    "total_questions": v["total"],
                    "correct_answers": v["correct"],
                    "accuracy": v["correct"] / max(v["total"], 1),
                }
                for v in topic_results_map.values()
            ],
            "strengths": [
                k for k, v in topic_results_map.items()
                if v["total"] > 0 and v["correct"] / v["total"] >= 0.7
            ],
            "weaknesses": [
                k for k, v in topic_results_map.items()
                if v["total"] > 0 and v["correct"] / v["total"] < 0.5
            ],
            "recommendations": [
                "Zayif konularinizda daha fazla pratik yapin.",
                "Yanlis yaptiginiz sorularin cozumlerini dikkatli inceleyin.",
            ],
        }

    st.session_state.mock_completed = True
    st.session_state.mock_session = None


def render_mock_result(result: Dict):
    """Render exam result with detailed analysis."""
    st.markdown("")
    section_header("Sinav Sonuclari")

    total = result.get("total_questions", 0)
    correct = result.get("correct_answers", 0)
    wrong = result.get("wrong_answers", 0)
    unanswered = result.get("unanswered", 0)
    raw_score = result.get("raw_score", 0)
    net_score = result.get("net_score", 0)

    # Score cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-score">{correct}/{total}</div>
            <div class="result-label">Dogru Cevap</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        stat_card(f"%{int(raw_score * 100)}", "Basari Orani", "\U0001f4ca")
    with col3:
        stat_card(str(wrong), "Yanlis Cevap", "\u274c")
    with col4:
        stat_card(str(unanswered), "Bos", "\u2796")

    # Net score (for YKS exams)
    if st.session_state.exam_type != "LGS":
        st.markdown("")
        col_net1, col_net2 = st.columns(2)
        with col_net1:
            stat_card(f"{net_score:.1f}", "Net Puan (Dogru - Yanlis/4)", "\U0001f4af")
        with col_net2:
            percentile = result.get("estimated_rank_percentile")
            if percentile is not None:
                stat_card(f"%{percentile:.0f}", "Tahmini Yuzdelik Dilim", "\U0001f3c6")

    # Topic-wise results
    st.markdown("")
    topic_results = result.get("topic_results", [])
    if topic_results:
        section_header("Konu Bazli Performans")
        for tr in topic_results:
            name = tr.get("topic_name_tr", tr.get("topic_slug", ""))
            t_total = tr.get("total_questions", 0)
            t_correct = tr.get("correct_answers", 0)
            accuracy = tr.get("accuracy", 0)

            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                progress_bar(accuracy, f"{name}: {t_correct}/{t_total} dogru")
            with col_t2:
                if accuracy >= 0.7:
                    st.markdown('<span class="mastery-chip mastery-chip-strong">Guclu</span>', unsafe_allow_html=True)
                elif accuracy < 0.5:
                    st.markdown('<span class="mastery-chip mastery-chip-weak">Gelistirilmeli</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="mastery-chip mastery-chip-mid">Orta</span>', unsafe_allow_html=True)

    # Strengths and weaknesses
    strengths = result.get("strengths", [])
    weaknesses = result.get("weaknesses", [])

    if strengths or weaknesses:
        st.markdown("")
        col_sw1, col_sw2 = st.columns(2)
        with col_sw1:
            section_header("Guclu Yonler")
            if strengths:
                chips_html = "".join(
                    f'<span class="mastery-chip mastery-chip-strong">{TOPIC_NAME_TR.get(s, s)}</span>'
                    for s in strengths
                )
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#666;">Henuz yeterli veri yok</span>', unsafe_allow_html=True)

        with col_sw2:
            section_header("Gelistirilecek Alanlar")
            if weaknesses:
                chips_html = "".join(
                    f'<span class="mastery-chip mastery-chip-weak">{TOPIC_NAME_TR.get(w, w)}</span>'
                    for w in weaknesses
                )
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.markdown(
                    '<span class="mastery-chip mastery-chip-strong">Tum konularda basarili!</span>',
                    unsafe_allow_html=True,
                )

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        st.markdown("")
        section_header("Oneriler")
        for rec in recommendations:
            st.markdown(f"""
            <div class="info-box" style="margin-bottom:10px;">
                {rec}
            </div>
            """, unsafe_allow_html=True)

    # New exam button
    st.markdown("")
    if st.button("Yeni Deneme Sinavi", type="primary", use_container_width=True, key="new_mock"):
        st.session_state.mock_completed = False
        st.session_state.mock_result = None
        st.session_state.mock_session = None
        st.rerun()


def render_exam_stats(stats: Dict, exam_type_api: str):
    """Render exam statistics section."""
    total_sessions = stats.get("total_sessions", 0)

    if total_sessions == 0:
        st.markdown("""
        <div class="info-box">
            <strong>Henuz sinav istatistiginiz bulunmuyor.</strong><br>
            Ilk deneme sinavinizi olusturarak istatistiklerinizi takip etmeye baslayin.
        </div>
        """, unsafe_allow_html=True)
        return

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stat_card(str(total_sessions), "Sinav Sayisi", "\U0001f4dd")
    with col2:
        accuracy = stats.get("overall_accuracy", 0)
        stat_card(f"%{int(accuracy * 100)}", "Ortalama Basari", "\U0001f4ca")
    with col3:
        best = stats.get("best_net_score", 0)
        stat_card(f"{best:.1f}", "En Iyi Net", "\U0001f31f")
    with col4:
        avg_time = stats.get("average_time_per_question_seconds", 0)
        stat_card(f"{avg_time:.0f}sn", "Ort. Sure/Soru", "\u23f1")

    # Topic accuracy breakdown
    topic_accuracy = stats.get("topic_accuracy", {})
    if topic_accuracy:
        st.markdown("")
        section_header("Konu Bazli Basari Orani")

        sorted_topics = sorted(topic_accuracy.items(), key=lambda x: x[1], reverse=True)
        for slug, acc in sorted_topics:
            name = TOPIC_NAME_TR.get(slug, slug)
            progress_bar(acc, f"{name}")

    # Score trend
    score_trend = stats.get("score_trend", [])
    if score_trend and len(score_trend) > 1:
        st.markdown("")
        section_header("Puan Trendi")
        st.line_chart(
            {"Net Puan": score_trend},
            use_container_width=True,
        )


# ---------------------------------------------------------------------------
# TAB 2: Seviye Testi (Diagnostic)
# ---------------------------------------------------------------------------

def render_diagnostic_tab():
    """Render the diagnostic placement test tab."""

    if not st.session_state.diag_session_id and not st.session_state.diag_completed:
        # Start screen
        render_diagnostic_start()
    elif st.session_state.diag_completed:
        # Show results
        render_diagnostic_result()
    else:
        # Active diagnostic
        render_active_diagnostic()


def render_diagnostic_start():
    """Render the diagnostic start screen."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%);
                border-radius: 18px; padding: 36px; color: white;
                box-shadow: 0 12px 40px rgba(5, 150, 105, 0.3); margin-bottom: 24px;">
        <h2 style="color: white !important; margin: 0 0 8px 0;">Seviye Belirleme Testi</h2>
        <p style="color: rgba(255,255,255,0.9); font-size: 1em; line-height: 1.6; margin: 0;">
            Matematik seviyenizi belirleyin. Adaptif algoritma, guclendirmeniz gereken
            alanlari ve mevcut seviyenizi tespit eder. Test 15-40 soru arasinda degisir
            ve performansiniza gore otomatik olarak zorluk ayari yapar.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        stat_card("15-40", "Soru Araligi", "\u2753")
    with col_info2:
        stat_card("16", "Matematik Konusu", "\U0001f4da")
    with col_info3:
        stat_card("Adaptif", "Zorluk Ayari", "\U0001f9e0")

    st.markdown("")

    # Grade level selector
    col_grade, col_start = st.columns([2, 1])
    with col_grade:
        grade = st.selectbox(
            "Sinif Seviyeniz",
            list(range(1, 13)),
            index=st.session_state.diag_grade_level - 1,
            format_func=lambda x: f"{x}. Sinif",
            key="diag_grade_select",
        )
        st.session_state.diag_grade_level = grade

    with col_start:
        st.markdown("")
        st.markdown("")
        if st.button(
            "Teste Basla",
            type="primary",
            use_container_width=True,
            key="start_diagnostic",
        ):
            with st.spinner("Seviye testi hazirlaniyor..."):
                result = api_post("/diagnostic/start", {
                    "user_id": "current_user",
                    "grade_level": grade,
                })

            if result:
                st.session_state.diag_session_id = result.get("session_id")
                st.session_state.diag_questions_answered = 0
                st.session_state.diag_progress = 0.0
                st.session_state.diag_completed = False
                st.session_state.diag_result = None
                st.session_state.diag_last_feedback = None
                st.session_state.diag_current_question = None
                st.rerun()
            else:
                st.error(
                    "Seviye testi baslatilamadi. Lutfen API sunucusunun "
                    "calistigindan emin olun."
                )

    # Show previous result if exists
    if st.session_state.diag_result:
        st.markdown("---")
        section_header("Son Test Sonucunuz")
        render_placement_result_display(st.session_state.diag_result)


def render_active_diagnostic():
    """Render the active diagnostic question flow."""
    session_id = st.session_state.diag_session_id

    # Fetch next question if we don't have one
    if st.session_state.diag_current_question is None:
        question_data = api_get(f"/diagnostic/next/{session_id}")

        if question_data is None:
            # Diagnostic might be complete
            complete_diagnostic()
            st.rerun()
            return

        st.session_state.diag_current_question = question_data

    question = st.session_state.diag_current_question

    if question is None:
        complete_diagnostic()
        st.rerun()
        return

    # Progress display
    progress = st.session_state.diag_progress
    answered = st.session_state.diag_questions_answered

    st.markdown(f"""
    <div class="diag-progress-container">
        <div class="diag-progress-header">
            <span class="diag-progress-title">Seviye Testi Ilerlemeniz</span>
            <span class="diag-progress-count">{answered} soru cevaplandi</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    progress_bar(progress, f"Ilerleme: %{int(progress * 100)}")

    # Show last feedback
    if st.session_state.diag_last_feedback:
        fb = st.session_state.diag_last_feedback
        if fb.get("is_correct"):
            st.success("Dogru cevap!")
        else:
            correct_answer = fb.get("correct_answer", "")
            st.error(f"Yanlis. Dogru cevap: {correct_answer}")

    st.markdown("")

    # Render question
    question_id = question.get("question_id", "")
    expression = question.get("expression", "")
    question_text = question.get("question_text", "")
    story_text = question.get("story_text", "")
    topic = question.get("topic", "")

    topic_display = TOPIC_NAME_TR.get(topic, topic)

    st.markdown(f"""
    <div class="exam-question-card">
        <div class="exam-question-number">Soru {answered + 1}</div>
        {f'<span class="exam-question-topic">{html_module.escape(str(topic_display))}</span>' if topic_display else ''}
        {f'<div style="color:#555; font-size:0.95em; margin-bottom:10px; line-height:1.5;">{html_module.escape(str(story_text))}</div>' if story_text else ''}
        {f'<div class="exam-question-text">{html_module.escape(str(question_text))}</div>' if question_text else ''}
    </div>
    """, unsafe_allow_html=True)

    if expression:
        expr_display = expression.replace("*", " \\times ").replace("/", " \\div ")
        st.latex(expr_display)

    # Answer input
    with st.form("diag_answer_form", clear_on_submit=True):
        answer = st.text_input(
            "Cevabin",
            placeholder="Cevabin buraya yaz...",
            key="diag_answer_input",
        )
        col_submit, col_skip = st.columns([3, 1])
        with col_submit:
            submitted = st.form_submit_button(
                "Cevabi Gonder",
                type="primary",
                use_container_width=True,
            )
        with col_skip:
            skipped = st.form_submit_button(
                "Atla",
                use_container_width=True,
            )

    if submitted and answer:
        # Submit answer
        response = api_post(f"/diagnostic/answer/{session_id}", {"answer": answer})

        if response:
            st.session_state.diag_last_feedback = response
            st.session_state.diag_questions_answered = response.get(
                "total_questions_asked", answered + 1
            )
            st.session_state.diag_progress = response.get("progress", progress)
            st.session_state.diag_current_question = None
            st.rerun()
        else:
            # Fallback: just move to next
            st.session_state.diag_questions_answered = answered + 1
            st.session_state.diag_progress = min(1.0, (answered + 1) / 40.0)
            st.session_state.diag_current_question = None
            st.session_state.diag_last_feedback = None
            st.rerun()

    elif skipped:
        # Skip this question
        st.session_state.diag_questions_answered = answered + 1
        st.session_state.diag_progress = min(1.0, (answered + 1) / 40.0)
        st.session_state.diag_current_question = None
        st.session_state.diag_last_feedback = None
        st.rerun()

    # Finish early button
    st.markdown("")
    if answered >= 15:
        if st.button("Testi Bitir", key="finish_diag_early", use_container_width=True):
            complete_diagnostic()
            st.rerun()

    if st.button("Testi Iptal Et", key="cancel_diag", use_container_width=True):
        st.session_state.diag_session_id = None
        st.session_state.diag_current_question = None
        st.session_state.diag_completed = False
        st.session_state.diag_last_feedback = None
        st.rerun()


def complete_diagnostic():
    """Complete the diagnostic and fetch results."""
    session_id = st.session_state.diag_session_id

    # Complete the diagnostic
    complete_result = api_post(f"/diagnostic/complete/{session_id}")

    # Get placement result
    placement = api_get(f"/diagnostic/result/{session_id}")

    if placement:
        st.session_state.diag_result = placement
    elif complete_result:
        st.session_state.diag_result = complete_result
    else:
        # Fallback result
        st.session_state.diag_result = {
            "overall_mastery": 0.5,
            "overall_accuracy": 0.5,
            "total_questions": st.session_state.diag_questions_answered,
            "total_correct": int(st.session_state.diag_questions_answered * 0.5),
            "topic_results": {},
            "focus_topics": [],
            "recommended_difficulties": {},
        }

    st.session_state.diag_completed = True
    st.session_state.diag_session_id = None
    st.session_state.diag_current_question = None


def render_diagnostic_result():
    """Render the diagnostic result screen."""
    result = st.session_state.diag_result
    if not result:
        st.info("Sonuc bulunamadi.")
        return

    render_placement_result_display(result)

    st.markdown("")
    if st.button(
        "Yeni Seviye Testi Baslat",
        type="primary",
        use_container_width=True,
        key="new_diag",
    ):
        st.session_state.diag_completed = False
        st.session_state.diag_result = None
        st.session_state.diag_session_id = None
        st.session_state.diag_current_question = None
        st.rerun()


def render_placement_result_display(result: Dict):
    """Render a detailed placement result with visual representation."""
    overall_mastery = result.get("overall_mastery", 0)
    overall_accuracy = result.get("overall_accuracy", 0)
    total_q = result.get("total_questions", 0)
    total_c = result.get("total_correct", 0)

    # Determine recommended level label
    if overall_mastery < 0.20:
        level_label = "Baslangic"
        level_color = "#ef4444"
        level_icon = "\U0001f331"
    elif overall_mastery < 0.40:
        level_label = "Temel"
        level_color = "#f97316"
        level_icon = "\U0001f33f"
    elif overall_mastery < 0.60:
        level_label = "Orta"
        level_color = "#eab308"
        level_icon = "\U0001f333"
    elif overall_mastery < 0.80:
        level_label = "Ileri"
        level_color = "#22c55e"
        level_icon = "\u2b50"
    else:
        level_label = "Uzman"
        level_color = "#667eea"
        level_icon = "\U0001f48e"

    # Hero result
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {level_color}22 0%, {level_color}11 100%);
                border-radius: 18px; padding: 32px; border: 2px solid {level_color};
                text-align: center; margin-bottom: 24px;">
        <div style="font-size: 3em; margin-bottom: 8px;">{level_icon}</div>
        <div style="font-size: 1.8em; font-weight: 800; color: {level_color};">
            {level_label} Seviye
        </div>
        <div style="font-size: 0.95em; color: #666; margin-top: 6px;">
            Genel Hakimiyet: %{int(overall_mastery * 100)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card(f"%{int(overall_mastery * 100)}", "Genel Hakimiyet", "\U0001f4ca")
    with col2:
        stat_card(f"%{int(overall_accuracy * 100)}", "Dogru Orani", "\U0001f3af")
    with col3:
        stat_card(f"{total_c}/{total_q}", "Dogru/Toplam", "\u2705")

    # Topic results
    topic_results = result.get("topic_results", {})
    if topic_results:
        st.markdown("")
        section_header("Konu Bazli Seviye Analizi")

        # Sort topics by mastery score
        sorted_topics = []
        for topic_key, topic_data in topic_results.items():
            if isinstance(topic_data, dict):
                mastery = topic_data.get("mastery_score", 0)
                level = topic_data.get("mastery_level", "not_assessed")
                questions = topic_data.get("questions_asked", 0)
                accuracy = topic_data.get("accuracy", 0)
                topic_name = TOPIC_NAME_TR.get(topic_key, topic_key)
                sorted_topics.append({
                    "name": topic_name,
                    "mastery": mastery,
                    "level": level,
                    "questions": questions,
                    "accuracy": accuracy,
                })

        sorted_topics.sort(key=lambda x: x["mastery"], reverse=True)

        for t in sorted_topics:
            if t["questions"] == 0:
                continue

            level_tr = MASTERY_LEVEL_TR.get(t["level"], t["level"])

            col_t1, col_t2, col_t3 = st.columns([3, 1, 1])
            with col_t1:
                progress_bar(t["mastery"], f"{t['name']}")
            with col_t2:
                if t["mastery"] >= 0.7:
                    st.markdown(
                        f'<span class="mastery-chip mastery-chip-strong">{level_tr}</span>',
                        unsafe_allow_html=True,
                    )
                elif t["mastery"] < 0.4:
                    st.markdown(
                        f'<span class="mastery-chip mastery-chip-weak">{level_tr}</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<span class="mastery-chip mastery-chip-mid">{level_tr}</span>',
                        unsafe_allow_html=True,
                    )
            with col_t3:
                st.markdown(
                    f"<div style='text-align:center; color:#666; font-size:0.85em; padding-top:6px;'>"
                    f"%{int(t['accuracy'] * 100)} dogru</div>",
                    unsafe_allow_html=True,
                )

    # Visual strength map
    if topic_results:
        st.markdown("")
        section_header("Guc Haritasi")

        strong_topics = [
            t for t in sorted_topics if t.get("mastery", 0) >= 0.6 and t.get("questions", 0) > 0
        ]
        mid_topics = [
            t for t in sorted_topics
            if 0.4 <= t.get("mastery", 0) < 0.6 and t.get("questions", 0) > 0
        ]
        weak_topics = [
            t for t in sorted_topics if t.get("mastery", 0) < 0.4 and t.get("questions", 0) > 0
        ]

        col_s, col_m, col_w = st.columns(3)

        with col_s:
            st.markdown("""
            <div style="background:#d1fae5; border-radius:12px; padding:16px; min-height:120px;">
                <div style="font-weight:700; color:#065f46; margin-bottom:8px;">
                    Guclu Alanlar
                </div>
            """, unsafe_allow_html=True)
            if strong_topics:
                chips = "".join(
                    f'<span class="mastery-chip mastery-chip-strong">{t["name"]}</span>'
                    for t in strong_topics
                )
                st.markdown(chips + "</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    '<span style="color:#065f46; font-size:0.85em;">Henuz belirlenmedi</span></div>',
                    unsafe_allow_html=True,
                )

        with col_m:
            st.markdown("""
            <div style="background:#fef3c7; border-radius:12px; padding:16px; min-height:120px;">
                <div style="font-weight:700; color:#92400e; margin-bottom:8px;">
                    Gelistirilebilir
                </div>
            """, unsafe_allow_html=True)
            if mid_topics:
                chips = "".join(
                    f'<span class="mastery-chip mastery-chip-mid">{t["name"]}</span>'
                    for t in mid_topics
                )
                st.markdown(chips + "</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    '<span style="color:#92400e; font-size:0.85em;">Henuz belirlenmedi</span></div>',
                    unsafe_allow_html=True,
                )

        with col_w:
            st.markdown("""
            <div style="background:#fee2e2; border-radius:12px; padding:16px; min-height:120px;">
                <div style="font-weight:700; color:#991b1b; margin-bottom:8px;">
                    Odak Alanlari
                </div>
            """, unsafe_allow_html=True)
            if weak_topics:
                chips = "".join(
                    f'<span class="mastery-chip mastery-chip-weak">{t["name"]}</span>'
                    for t in weak_topics
                )
                st.markdown(chips + "</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    '<span style="color:#991b1b; font-size:0.85em;">Henuz belirlenmedi</span></div>',
                    unsafe_allow_html=True,
                )

    # Focus topics
    focus_topics = result.get("focus_topics", [])
    if focus_topics:
        st.markdown("")
        section_header("Onerilen Calisma Plani")
        for i, topic_slug in enumerate(focus_topics, 1):
            name = TOPIC_NAME_TR.get(topic_slug, topic_slug)
            st.markdown(f"""
            <div class="info-box" style="margin-bottom:8px;">
                <strong>{i}.</strong> <strong>{name}</strong> konusuna oncelik verin.
                Bu alanda daha fazla pratik yapmaniz oneriliyor.
            </div>
            """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main page layout
# ---------------------------------------------------------------------------

def main():
    """Main page entry point."""

    # Hero section
    st.markdown("""
    <div class="exam-hero">
        <h1>Sinav Hazirlik Merkezi</h1>
        <p>
            LGS ve YKS sinavlarina kapsamli hazirlik. MEB mufredat agirliklarina uygun
            deneme sinavlari cozun, adaptif seviye testi ile guclu ve zayif yonlerinizi
            kesfedın. Kisisellestirilmis calisma planlariyla hedefinize ulasin.
        </p>
        <div class="exam-badges">
            <span class="exam-badge">LGS Hazirlik</span>
            <span class="exam-badge">YKS-TYT</span>
            <span class="exam-badge">YKS-AYT</span>
            <span class="exam-badge">Adaptif Seviye Testi</span>
            <span class="exam-badge">MEB Mufredat Uyumlu</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main tabs
    tab_exam, tab_diag = st.tabs([
        "Sinav Hazirlik",
        "Seviye Testi",
    ])

    with tab_exam:
        render_exam_prep_tab()

    with tab_diag:
        render_diagnostic_tab()

    # Footer
    st.markdown("---")
    st.caption("MathAI Sinav Hazirlik Merkezi - MEB mufredat agirliklarina uygun adaptif sinav platformu")


if __name__ == "__main__":
    main()
