"""
Odev Yonetim Sayfasi - Homework Management Page.

Ogrenciler odevlerini gorur ve gonderir, ogretmenler odev olusturur,
veliler hedef belirler. Kapsamli odev takip ve yonetim platformu.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from theme import (
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
    page_title="Odevler - MathAI",
    page_icon="📓",
    layout="wide",
)

apply_theme()
render_sidebar("pages/homework")

# ---------------------------------------------------------------------------
# Additional page-specific CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.homework-hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    border-radius: 20px; padding: 40px 36px; color: white;
    margin-bottom: 28px; box-shadow: 0 16px 48px rgba(102,126,234,0.35);
    position: relative; overflow: hidden;
}
.homework-hero::before {
    content: ''; position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.homework-hero h1 { color: white !important; font-size: 2.2em; font-weight: 700; margin: 0 0 8px 0; position: relative; }
.homework-hero p { color: rgba(255,255,255,0.88); font-size: 1.05em; line-height: 1.6; margin: 0; max-width: 700px; position: relative; }
.hw-card {
    background: white; border-radius: 14px; padding: 22px 24px;
    box-shadow: 0 3px 16px rgba(0,0,0,0.08); border-left: 5px solid #667eea;
    margin-bottom: 14px; transition: transform 0.2s, box-shadow 0.2s;
}
.hw-card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.12); }
.hw-card-title { font-size: 1.15em; font-weight: 700; color: #1a1a2e; margin-bottom: 6px; }
.hw-card-meta { font-size: 0.85em; color: #666; margin-bottom: 10px; line-height: 1.6; }
.hw-card-topics { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.hw-topic-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: 600; background: #ede9fe; color: #5b21b6; }
.hw-status { display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.8em; font-weight: 600; }
.hw-status-pending { background: #fff3cd; color: #856404; }
.hw-status-submitted { background: #cce5ff; color: #004085; }
.hw-status-graded { background: #d4edda; color: #155724; }
.hw-status-overdue { background: #f8d7da; color: #721c24; }
.hw-grade { display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 50%; font-weight: 800; font-size: 1.2em; color: white; }
.hw-grade-high { background: linear-gradient(135deg, #28a745, #20c997); }
.hw-grade-mid { background: linear-gradient(135deg, #ffc107, #fd7e14); }
.hw-grade-low { background: linear-gradient(135deg, #dc3545, #e83e8c); }
.goal-card { background: white; border-radius: 14px; padding: 20px 24px; box-shadow: 0 3px 16px rgba(0,0,0,0.08); border-left: 5px solid #28a745; margin-bottom: 14px; transition: transform 0.2s; }
.goal-card:hover { transform: translateY(-2px); }
.goal-card-title { font-size: 1.05em; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
.goal-card-meta { font-size: 0.85em; color: #666; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KONU_LISTESI = [
    "Aritmetik", "Kesirler", "Yuzdelik", "Cebir",
    "Geometri", "Oran-Oranti", "Uslu Sayilar", "Istatistik",
    "Sayi Teorisi", "Denklem Sistemleri", "Esitsizlikler", "Fonksiyonlar",
    "Trigonometri", "Polinomlar", "Kumeler ve Mantik", "Koordinat Geometrisi",
]

KONU_SLUG_MAP = {
    "Aritmetik": "arithmetic", "Kesirler": "fractions",
    "Yuzdelik": "percentages", "Cebir": "algebra",
    "Geometri": "geometry", "Oran-Oranti": "ratios",
    "Uslu Sayilar": "exponents", "Istatistik": "statistics",
    "Sayi Teorisi": "number_theory", "Denklem Sistemleri": "systems_of_equations",
    "Esitsizlikler": "inequalities", "Fonksiyonlar": "functions",
    "Trigonometri": "trigonometry", "Polinomlar": "polynomials",
    "Kumeler ve Mantik": "sets_and_logic", "Koordinat Geometrisi": "coordinate_geometry",
}

HEDEF_TURLERI = {
    "Haftalik Soru Sayisi": "questions_per_week",
    "Dogruluk Orani Hedefi (%)": "accuracy_target",
    "Ardisik Dogru Serisi": "streak_target",
    "Konu Hakimiyet Hedefi (%)": "mastery_target",
    "Haftalik Calisma Suresi (dakika)": "practice_minutes",
}

HEDEF_TURU_TR = {
    "questions_per_week": "Haftalik Soru Sayisi",
    "accuracy_target": "Dogruluk Orani Hedefi",
    "streak_target": "Ardisik Dogru Serisi",
    "mastery_target": "Konu Hakimiyet Hedefi",
    "practice_minutes": "Haftalik Calisma Suresi",
}

STATUS_TR = {
    "pending": ("Bekliyor", "hw-status-pending"),
    "submitted": ("Gonderildi", "hw-status-submitted"),
    "graded": ("Notlandirildi", "hw-status-graded"),
    "overdue": ("Suresi Gecti", "hw-status-overdue"),
}

# ---------------------------------------------------------------------------
# Fallback / demo data
# ---------------------------------------------------------------------------

def _demo_student_homework():
    now = datetime.utcnow()
    return [
        {"homework_id": "hw_001", "title": "Kesirler - Haftalik Odev",
         "topics": ["Kesirler"], "question_count": 15,
         "due_date": (now + timedelta(days=3)).isoformat(),
         "status": "pending", "grade": None,
         "created_at": (now - timedelta(days=2)).isoformat(),
         "teacher_name": "Ayse Ogretmen", "class_name": "8-A"},
        {"homework_id": "hw_002", "title": "Cebir ve Denklemler Pratigi",
         "topics": ["Cebir", "Denklem Sistemleri"], "question_count": 20,
         "due_date": (now + timedelta(days=5)).isoformat(),
         "status": "pending", "grade": None,
         "created_at": (now - timedelta(days=1)).isoformat(),
         "teacher_name": "Mehmet Ogretmen", "class_name": "8-A"},
        {"homework_id": "hw_003", "title": "Geometri Alistirmasi",
         "topics": ["Geometri", "Koordinat Geometrisi"], "question_count": 10,
         "due_date": (now - timedelta(days=1)).isoformat(),
         "status": "submitted", "grade": None,
         "created_at": (now - timedelta(days=7)).isoformat(),
         "teacher_name": "Ayse Ogretmen", "class_name": "8-A"},
        {"homework_id": "hw_004", "title": "Aritmetik Temel Islemler",
         "topics": ["Aritmetik"], "question_count": 25,
         "due_date": (now - timedelta(days=5)).isoformat(),
         "status": "graded", "grade": 88,
         "created_at": (now - timedelta(days=12)).isoformat(),
         "teacher_name": "Mehmet Ogretmen", "class_name": "8-A"},
        {"homework_id": "hw_005", "title": "Istatistik ve Olasilik",
         "topics": ["Istatistik"], "question_count": 12,
         "due_date": (now - timedelta(days=3)).isoformat(),
         "status": "graded", "grade": 72,
         "created_at": (now - timedelta(days=10)).isoformat(),
         "teacher_name": "Ayse Ogretmen", "class_name": "8-A"},
        {"homework_id": "hw_006", "title": "Uslu Sayilar ve Kokler",
         "topics": ["Uslu Sayilar"], "question_count": 18,
         "due_date": (now - timedelta(days=8)).isoformat(),
         "status": "overdue", "grade": None,
         "created_at": (now - timedelta(days=15)).isoformat(),
         "teacher_name": "Mehmet Ogretmen", "class_name": "8-A"},
    ]


def _demo_homework_detail():
    return {
        "homework_id": "hw_001", "title": "Kesirler - Haftalik Odev",
        "topics": ["Kesirler"], "question_count": 15,
        "due_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
        "status": "pending",
        "questions": [
            {"question_id": f"q_{i+1}",
             "question_text": f"Soru {i+1}: Ornek kesir sorusu",
             "expression": f"{i+1}/4 + {i+2}/8",
             "correct_answer": str(round((i + 1) / 4 + (i + 2) / 8, 2))}
            for i in range(5)
        ],
    }


def _demo_child_goals():
    now = datetime.utcnow()
    return [
        {"goal_id": "goal_001", "goal_type": "questions_per_week",
         "target_value": 50, "current_value": 32, "progress": 0.64,
         "deadline": (now + timedelta(days=5)).isoformat(),
         "status": "active", "created_at": (now - timedelta(days=9)).isoformat()},
        {"goal_id": "goal_002", "goal_type": "accuracy_target",
         "target_value": 85, "current_value": 78, "progress": 0.92,
         "deadline": (now + timedelta(days=12)).isoformat(),
         "status": "active", "created_at": (now - timedelta(days=14)).isoformat()},
        {"goal_id": "goal_003", "goal_type": "streak_target",
         "target_value": 15, "current_value": 15, "progress": 1.0,
         "deadline": (now + timedelta(days=2)).isoformat(),
         "status": "completed", "created_at": (now - timedelta(days=20)).isoformat()},
        {"goal_id": "goal_004", "goal_type": "mastery_target",
         "target_value": 80, "current_value": 55, "progress": 0.69,
         "deadline": (now + timedelta(days=20)).isoformat(),
         "status": "active", "created_at": (now - timedelta(days=5)).isoformat()},
        {"goal_id": "goal_005", "goal_type": "practice_minutes",
         "target_value": 120, "current_value": 90, "progress": 0.75,
         "deadline": (now + timedelta(days=3)).isoformat(),
         "status": "active", "created_at": (now - timedelta(days=11)).isoformat()},
    ]


def _demo_goal_progress():
    return {
        "goal_id": "goal_001", "goal_type": "questions_per_week",
        "target_value": 50, "current_value": 32, "progress": 0.64,
        "remaining_days": 5, "daily_target": 4, "on_track": True,
        "history": [
            {"date": "2026-01-21", "value": 5},
            {"date": "2026-01-22", "value": 7},
            {"date": "2026-01-23", "value": 4},
            {"date": "2026-01-24", "value": 8},
            {"date": "2026-01-25", "value": 6},
            {"date": "2026-01-26", "value": 2},
        ],
    }

# ---------------------------------------------------------------------------
# Helper renderers
# ---------------------------------------------------------------------------

def _format_date(iso_str):
    """Format ISO date string to Turkish-friendly display."""
    if not iso_str:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return iso_str


def _days_remaining(iso_str):
    """Calculate days remaining from ISO date string."""
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            from datetime import timezone
            now = datetime.now(timezone.utc)
        else:
            now = datetime.utcnow()
        delta = dt - now
        return delta.days
    except Exception:
        return None


def _render_status_badge(status):
    """Return HTML for a status badge."""
    label, css_class = STATUS_TR.get(status, (status, "hw-status-pending"))
    return f'<span class="hw-status {css_class}">{label}</span>'


def _render_grade_circle(grade):
    """Return HTML for a grade circle."""
    if grade is None:
        return ""
    if grade >= 80:
        grade_class = "hw-grade-high"
    elif grade >= 60:
        grade_class = "hw-grade-mid"
    else:
        grade_class = "hw-grade-low"
    return f'<span class="hw-grade {grade_class}">{grade}</span>'


def _render_homework_card(hw):
    """Render a single homework card."""
    title = hw.get("title", "Isimsiz Odev")
    status = hw.get("status", "pending")
    grade = hw.get("grade")
    topics = hw.get("topics", [])
    question_count = hw.get("question_count", 0)
    due_date = hw.get("due_date")
    teacher_name = hw.get("teacher_name", "")
    class_name = hw.get("class_name", "")

    due_display = _format_date(due_date)
    days_left = _days_remaining(due_date)

    topics_html = ""
    if topics:
        chips = "".join(f'<span class="hw-topic-chip">{t}</span>' for t in topics)
        topics_html = f'<div class="hw-card-topics">{chips}</div>'

    days_text = ""
    if days_left is not None:
        if days_left > 0:
            days_text = f" ({days_left} gun kaldi)"
        elif days_left == 0:
            days_text = " (Bugun son gun!)"
        else:
            days_text = f" ({abs(days_left)} gun gecti)"

    grade_html = ""
    if grade is not None:
        grade_html = f'<div style="float:right;margin-top:-60px;">{_render_grade_circle(grade)}</div>'

    border_colors = {"pending": "#ffc107", "submitted": "#007bff", "graded": "#28a745", "overdue": "#dc3545"}
    border_color = border_colors.get(status, "#667eea")

    st.markdown(f"""
    <div class="hw-card" style="border-left-color: {border_color};">
        <div class="hw-card-title">{title}</div>
        <div class="hw-card-meta">
            {_render_status_badge(status)}
            &nbsp;&middot;&nbsp; {question_count} soru
            &nbsp;&middot;&nbsp; Son teslim: {due_display}{days_text}
            {f'&nbsp;&middot;&nbsp; {teacher_name}' if teacher_name else ''}
            {f'&nbsp;&middot;&nbsp; {class_name}' if class_name else ''}
        </div>
        {topics_html}
        {grade_html}
    </div>
    """, unsafe_allow_html=True)


def _render_goal_card(goal):
    """Render a single goal card."""
    goal_type = goal.get("goal_type", "questions_per_week")
    target = goal.get("target_value", 0)
    current = goal.get("current_value", 0)
    progress_val = goal.get("progress", 0)
    deadline = goal.get("deadline")
    status = goal.get("status", "active")

    type_label = HEDEF_TURU_TR.get(goal_type, goal_type)
    days_left = _days_remaining(deadline)

    unit = ""
    if goal_type in ("accuracy_target", "mastery_target"):
        unit = "%"
    elif goal_type == "practice_minutes":
        unit = " dk"

    if status == "completed":
        status_icon, status_text, border_color = "✅", "Tamamlandi", "#28a745"
    elif days_left is not None and days_left < 0:
        status_icon, status_text, border_color = "⏰", "Suresi Doldu", "#dc3545"
    else:
        status_icon, status_text, border_color = "🎯", "Aktif", "#667eea"

    days_text = ""
    if days_left is not None:
        if days_left > 0:
            days_text = f"{days_left} gun kaldi"
        elif days_left == 0:
            days_text = "Bugun son gun!"
        else:
            days_text = f"{abs(days_left)} gun gecti"

    st.markdown(f"""
    <div class="goal-card" style="border-left-color: {border_color};">
        <div class="goal-card-title">{status_icon} {type_label}</div>
        <div class="goal-card-meta">
            Hedef: <strong>{target}{unit}</strong>
            &nbsp;&middot;&nbsp; Mevcut: <strong>{current}{unit}</strong>
            &nbsp;&middot;&nbsp; {status_text}
            {f'&nbsp;&middot;&nbsp; {days_text}' if days_text else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)
    progress_bar(progress_val, label=f"Ilerleme: {current}{unit} / {target}{unit}")
    st.markdown("")


# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
st.markdown("""
<div class="homework-hero">
    <h1>📓 Odev Merkezi</h1>
    <p>
        Odevlerini takip et, zamaninda teslim et ve ogrenme hedeflerine ulas.
        Ogretmenler yeni odevler olusturabilir, veliler hedef belirleyebilir.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------
tab_my_hw, tab_create, tab_goals = st.tabs([
    "📚 Odevlerim",
    "📝 Odev Olustur",
    "🎯 Hedefler",
])

# =========================================================================
# TAB 1 - ODEVLERIM (My Homework)
# =========================================================================
with tab_my_hw:
    section_header("Odev Listem")

    st.markdown("""
    <div class="info-box" style="margin-bottom: 16px;">
        Tum odevlerinizi burada gorebilir, detaylarini inceleyebilir ve
        cevaplarini gonderebilirsiniz.
    </div>
    """, unsafe_allow_html=True)

    student_id = st.text_input(
        "Ogrenci Kimlik Numarasi", value="student_001",
        key="hw_student_id",
        help="Odev listenizi gormek icin ogrenci ID nizi girin.",
    )

    if not student_id.strip():
        st.warning("Lutfen gecerli bir Ogrenci ID girin.")
    else:
        homework_list = api_get(f"/homework/student/{student_id}")
        if homework_list is None:
            homework_list = _demo_student_homework()
        elif isinstance(homework_list, dict):
            homework_list = homework_list.get("homework", homework_list.get("assignments", []))

        if not homework_list:
            st.info("Henuz atanmis odeviniz bulunmuyor.")
        else:
            total_hw = len(homework_list)
            pending_count = sum(1 for h in homework_list if h.get("status") == "pending")
            submitted_count = sum(1 for h in homework_list if h.get("status") == "submitted")
            graded_count = sum(1 for h in homework_list if h.get("status") == "graded")
            overdue_count = sum(1 for h in homework_list if h.get("status") == "overdue")
            graded_items = [h for h in homework_list if h.get("grade") is not None]
            avg_grade = sum(h["grade"] for h in graded_items) / len(graded_items) if graded_items else 0

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                stat_card(total_hw, "Toplam Odev", icon="U0001F4DA")
            with c2:
                stat_card(pending_count, "Bekleyen", icon="⏳")
            with c3:
                stat_card(submitted_count, "Gonderilen", icon="U0001F4E8")
            with c4:
                stat_card(graded_count, "Notlanan", icon="✅")
            with c5:
                stat_card(f"%{avg_grade:.0f}" if graded_items else "-", "Ortalama Not", icon="U0001F4CA")

            st.markdown("")

            filter_status = st.selectbox(
                "Duruma Gore Filtrele",
                ["Tumu", "Bekleyen", "Gonderilen", "Notlanan", "Suresi Gecen"],
                key="hw_filter",
            )
            status_filter_map = {
                "Tumu": None, "Bekleyen": "pending", "Gonderilen": "submitted",
                "Notlanan": "graded", "Suresi Gecen": "overdue",
            }
            active_filter = status_filter_map.get(filter_status)
            filtered = (homework_list if active_filter is None
                        else [h for h in homework_list if h.get("status") == active_filter])

            if not filtered:
                st.info("Secilen durumda odev bulunamadi.")
            else:
                for hw in filtered:
                    _render_homework_card(hw)

            st.markdown("---")
            section_header("Odev Detayi ve Gonderim")

            hw_id_input = st.text_input(
                "Odev ID (detay gormek icin)", placeholder="ornek: hw_001", key="hw_detail_id",
            )

            if hw_id_input.strip():
                if st.button("U0001F50D Odev Detayini Getir", key="fetch_hw_detail"):
                    detail = api_get(f"/homework/{hw_id_input.strip()}")
                    if detail is None:
                        detail = _demo_homework_detail()
                        st.info("API baglantisi kurulamadi. Demo verisi gosteriliyor.")
                    st.session_state["hw_detail_data"] = detail

            if "hw_detail_data" in st.session_state and st.session_state["hw_detail_data"]:
                detail = st.session_state["hw_detail_data"]
                d_title = detail.get("title", "Odev")
                d_status = detail.get("status", "pending")
                d_questions = detail.get("questions", [])

                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:20px 24px;
                            box-shadow:0 2px 12px rgba(0,0,0,0.06);margin:16px 0;">
                    <h4 style="color:#333;margin:0 0 8px 0;">{d_title}</h4>
                    <div>{_render_status_badge(d_status)} &nbsp;&middot;&nbsp; {len(d_questions)} soru</div>
                </div>
                """, unsafe_allow_html=True)

                if d_questions and d_status in ("pending", "overdue"):
                    st.markdown("")
                    st.markdown("##### Cevaplarin")
                    with st.form("hw_submit_form", clear_on_submit=False):
                        answers = []
                        for i, q in enumerate(d_questions):
                            q_text = q.get("question_text", f"Soru {i + 1}")
                            expression = q.get("expression", "")
                            display = q_text + (f"  ({expression})" if expression else "")
                            answer = st.text_input(display, key=f"hw_answer_{i}", placeholder="Cevabin...")
                            answers.append({"question_id": q.get("question_id", f"q_{i+1}"), "answer": answer})

                        submit_hw = st.form_submit_button(
                            "U0001F4E8 Odevi Gonder", type="primary", use_container_width=True,
                        )

                    if submit_hw:
                        empty_answers = [a for a in answers if not a["answer"].strip()]
                        if empty_answers:
                            st.warning(f"{len(empty_answers)} soru cevaplanmadi.")
                        filled_answers = [a for a in answers if a["answer"].strip()]
                        if filled_answers:
                            payload = {"student_id": student_id, "answers": filled_answers}
                            result = api_post(f"/homework/{hw_id_input.strip()}/submit", payload)
                            if result:
                                st.success("Odeviniz basariyla gonderildi!")
                                st.balloons()
                            else:
                                st.warning("API baglantisi kurulamadi. Demo modunda gonderim simulasyonu yapildi.")
                                st.markdown("""
                                <div class="success-box">
                                    <strong>Odev Gonderildi (Demo)</strong><br>
                                    Gercek API baglantisi kuruldugunda odeviniz sunucuya gonderilecektir.
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error("Lutfen en az bir soruyu cevaplayin.")

                elif d_status == "submitted":
                    st.info("Bu odev gonderilmis durumda. Ogretmeninizin degerlendirmesini bekleyin.")
                elif d_status == "graded":
                    grade = detail.get("grade")
                    if grade is not None:
                        st.markdown(f"""
                        <div style="text-align:center;padding:20px;">
                            {_render_grade_circle(grade)}
                            <div style="margin-top:10px;font-weight:600;color:#333;">Notunuz: {grade}/100</div>
                        </div>
                        """, unsafe_allow_html=True)


# =========================================================================
# TAB 2 - ODEV OLUSTUR (Create Homework - for Teachers)
# =========================================================================
with tab_create:
    section_header("Yeni Odev Olustur")

    st.markdown("""
    <div class="info-box" style="margin-bottom: 16px;">
        Siniflariniz icin yeni matematik odevi olusturun. Konu, soru sayisi ve
        teslim tarihini belirleyin. Odevler otomatik olarak ogrencilere atanir.
    </div>
    """, unsafe_allow_html=True)

    with st.form("create_hw_form", clear_on_submit=True):
        st.markdown("##### Odev Bilgileri")

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            teacher_id = st.text_input(
                "Ogretmen Kimlik Numarasi",
                placeholder="ornek: teacher_001",
                key="hw_teacher_id",
                help="Kendi ogretmen ID nizi girin.",
            )
        with col_t2:
            class_id = st.text_input(
                "Sinif Kimlik Numarasi",
                placeholder="ornek: class_8a",
                key="hw_class_id",
                help="Odevi atayacaginiz sinifin ID sini girin.",
            )

        hw_title = st.text_input(
            "Odev Basligi",
            placeholder="ornek: Kesirler - Haftalik Odev",
            key="hw_create_title",
        )

        selected_topics = st.multiselect(
            "Konular",
            KONU_LISTESI,
            default=None,
            key="hw_topics",
            help="Odevde yer almasini istediginiz konulari secin.",
        )

        col_q, col_d = st.columns(2)
        with col_q:
            question_count = st.number_input(
                "Soru Sayisi",
                min_value=1, max_value=100, value=15, step=1,
                key="hw_q_count",
            )
        with col_d:
            due_date = st.date_input(
                "Son Teslim Tarihi",
                value=datetime.utcnow().date() + timedelta(days=7),
                key="hw_due_date",
                help="Ogrencilerin odevi teslim etmesi gereken son tarih.",
            )

        st.markdown("")
        create_submitted = st.form_submit_button(
            "U0001F4DD Odevi Olustur",
            type="primary",
            use_container_width=True,
        )

    if create_submitted:
        errors = []
        if not teacher_id.strip():
            errors.append("Ogretmen ID bos olamaz.")
        if not class_id.strip():
            errors.append("Sinif ID bos olamaz.")
        if not hw_title.strip():
            errors.append("Odev basligi bos olamaz.")
        if not selected_topics:
            errors.append("En az bir konu secmelisiniz.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            topic_slugs = [
                KONU_SLUG_MAP.get(t, t.lower().replace(" ", "_"))
                for t in selected_topics
            ]

            payload = {
                "teacher_id": teacher_id.strip(),
                "class_id": class_id.strip(),
                "title": hw_title.strip(),
                "topics": topic_slugs,
                "question_count": question_count,
                "due_date": due_date.isoformat(),
            }

            result = api_post("/homework/create", payload)

            if result:
                hw_id = result.get("homework_id", "")
                st.success(f"Odev basariyla olusturuldu! Odev ID: {hw_id}")
                st.balloons()
                st.markdown(f"""
                <div class="success-box">
                    <strong>Odev Olusturuldu</strong><br>
                    <strong>Baslik:</strong> {hw_title}<br>
                    <strong>Konular:</strong> {', '.join(selected_topics)}<br>
                    <strong>Soru Sayisi:</strong> {question_count}<br>
                    <strong>Son Teslim:</strong> {due_date.strftime('%d.%m.%Y')}<br>
                    <strong>Sinif:</strong> {class_id}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("API baglantisi kurulamadi. Demo modunda odev olusturuldu.")
                st.markdown(f"""
                <div class="success-box">
                    <strong>Odev Olusturuldu (Demo)</strong><br>
                    <strong>Baslik:</strong> {hw_title}<br>
                    <strong>Konular:</strong> {', '.join(selected_topics)}<br>
                    <strong>Soru Sayisi:</strong> {question_count}<br>
                    <strong>Son Teslim:</strong> {due_date.strftime('%d.%m.%Y')}<br>
                    <strong>Sinif:</strong> {class_id}<br>
                    <em>Gercek API baglantisi kuruldugunda odev sunucuya kaydedilecektir.</em>
                </div>
                """, unsafe_allow_html=True)

    # --- Grade homework section ---
    st.markdown("---")
    section_header("Odev Notlandirma")

    st.markdown("""
    <div class="info-box" style="margin-bottom: 16px;">
        Gonderilmis odevleri otomatik olarak notlandirin. Sistem sorulan sorulara
        gore otomatik degerlendirme yapacaktir.
    </div>
    """, unsafe_allow_html=True)

    col_g1, col_g2 = st.columns([3, 1])
    with col_g1:
        grade_hw_id = st.text_input(
            "Notlandirilacak Odev ID",
            placeholder="ornek: hw_003",
            key="grade_hw_id",
        )
    with col_g2:
        st.markdown("")
        st.markdown("")
        grade_btn = st.button(
            "✅ Notlandir",
            type="primary",
            use_container_width=True,
            key="grade_hw_btn",
        )

    if grade_btn:
        if not grade_hw_id.strip():
            st.error("Lutfen notlandirilacak Odev ID girin.")
        else:
            result = api_post(f"/homework/{grade_hw_id.strip()}/grade")
            if result:
                avg = result.get("average_grade", 0)
                count = result.get("submissions_graded", 0)
                st.success(f"Notlandirma tamamlandi! {count} gonderim degerlendirildi. Ortalama not: {avg:.0f}")
            else:
                st.warning("API baglantisi kurulamadi. Demo modunda notlandirma simulasyonu:")
                st.markdown("""
                <div class="success-box">
                    <strong>Notlandirma Tamamlandi (Demo)</strong><br>
                    <strong>Degerlendirilen:</strong> 24 gonderim<br>
                    <strong>Ortalama Not:</strong> 76<br>
                    <strong>En Yuksek:</strong> 100 &nbsp;&middot;&nbsp;
                    <strong>En Dusuk:</strong> 45
                </div>
                """, unsafe_allow_html=True)


# =============================================================================
# TAB 3 - HEDEFLER (Goals)
# =============================================================================
with tab_goals:
    section_header("Ogrenme Hedefleri")

    st.markdown("""
    <div class="info-box" style="margin-bottom: 16px;">
        Cocugunuz icin ogrenme hedefleri belirleyin, ilerlemelerini takip edin
        ve motivasyonlarini artirin.
    </div>
    """, unsafe_allow_html=True)

    gcol1, gcol2 = st.columns(2)
    with gcol1:
        parent_id = st.text_input(
            "Veli Kimlik Numarasi", value="parent_001",
            key="goal_parent_id",
            help="Hedef yonetimi icin veli ID nizi girin.",
        )
    with gcol2:
        child_id = st.text_input(
            "Ogrenci Kimlik Numarasi", value="student_001",
            key="goal_child_id",
            help="Hedef belirlenecek ogrencinin ID sini girin.",
        )

    # ---- Mevcut Hedefler ----
    st.markdown("### Mevcut Hedefler")

    goals_data = api_get(f"/homework/goals/{child_id}")
    if goals_data is None:
        goals_data = _demo_child_goals()

    goals_list = goals_data if isinstance(goals_data, list) else goals_data.get("goals", [])

    if goals_list:
        active_goals = [g for g in goals_list if g.get("status") == "active"]
        completed_goals = [g for g in goals_list if g.get("status") == "completed"]
        avg_prog = sum(g.get("progress", 0) for g in goals_list) / len(goals_list) if goals_list else 0

        sg1, sg2, sg3, sg4 = st.columns(4)
        with sg1:
            stat_card(str(len(goals_list)), "Toplam Hedef", "U0001f3af")
        with sg2:
            stat_card(str(len(active_goals)), "Aktif Hedef", "U0001f525")
        with sg3:
            stat_card(str(len(completed_goals)), "Tamamlanan", "✅")
        with sg4:
            stat_card(f"{avg_prog:.0f}%", "Ort. Ilerleme", "U0001f4c8")

        for goal in goals_list:
            _render_goal_card(goal)

        # ---- Hedef Detay ----
        st.markdown("### Hedef Ilerleme Detayi")

        goal_ids = [str(g.get("goal_id", g.get("id", ""))) for g in goals_list]
        selected_goal_id = st.selectbox(
            "Detayini gormek istediginiz hedefi secin",
            options=goal_ids,
            key="goal_detail_select",
        )

        if selected_goal_id:
            progress_data = api_get(f"/homework/goals/{selected_goal_id}/progress")
            if progress_data is None:
                progress_data = _demo_goal_progress()

            pcol1, pcol2, pcol3 = st.columns(3)
            with pcol1:
                cur = progress_data.get("current_value", 0)
                tgt = progress_data.get("target_value", 1)
                stat_card(f"{cur}/{tgt}", "Mevcut / Hedef", "U0001f4ca")
            with pcol2:
                pct = progress_data.get("progress_pct", 0)
                stat_card(f"{pct:.0f}%", "Ilerleme Yuzdesi", "U0001f4c8")
            with pcol3:
                on_track = progress_data.get("on_track", False)
                track_icon = "✅" if on_track else "⚠️"
                track_text = "Hedefte" if on_track else "Geride"
                stat_card(track_text, "Durum", track_icon)

            prog_pct = progress_data.get("progress_pct", 0)
            progress_bar(prog_pct / 100.0, f"Hedef Ilerlemesi: {prog_pct:.0f}%")

            history = progress_data.get("history", [])
            if history:
                st.markdown("#### Haftalik Ilerleme")
                import pandas as pd
                df = pd.DataFrame(history)
                if "week" in df.columns and "value" in df.columns:
                    st.bar_chart(df.set_index("week")["value"])
                else:
                    st.dataframe(df)
    else:
        st.info("Henuz hedef belirlenmemis. Asagidaki formu kullanarak yeni bir hedef olusturabilirsiniz.")

    # ---- Yeni Hedef Olustur ----
    st.markdown("### Yeni Hedef Olustur")

    with st.form("create_goal_form", clear_on_submit=True):
        st.markdown("**Hedef Bilgileri**")

        goal_type_label = st.selectbox(
            "Hedef Turu",
            options=list(HEDEF_TURU_TR.values()),
            key="goal_type_select",
        )
        goal_type_key = None
        for k, v in HEDEF_TURU_TR.items():
            if v == goal_type_label:
                goal_type_key = k
                break

        if goal_type_key == "questions_per_week":
            target_val = st.number_input("Haftalik Soru Sayisi", min_value=1, max_value=500, value=50, step=5)
        elif goal_type_key == "accuracy_target":
            target_val = st.number_input("Hedef Dogruluk Orani (%%)", min_value=1, max_value=100, value=80, step=5)
        elif goal_type_key == "streak_target":
            target_val = st.number_input("Hedef Seri Sayisi (gun)", min_value=1, max_value=365, value=30, step=5)
        elif goal_type_key == "mastery_target":
            target_val = st.number_input("Hedef Ustalasma Konusu Sayisi", min_value=1, max_value=16, value=5, step=1)
        elif goal_type_key == "practice_minutes":
            target_val = st.number_input("Gunluk Calisma Suresi (dk)", min_value=5, max_value=240, value=30, step=5)
        else:
            target_val = st.number_input("Hedef Deger", min_value=1, value=50, step=5)

        deadline = st.date_input("Son Tarih", key="goal_deadline")

        goal_submit = st.form_submit_button("Hedef Olustur", use_container_width=True)

    if goal_submit:
        if goal_type_key is None:
            st.error("Lutfen bir hedef turu secin.")
        else:
            deadline_str = deadline.strftime("%d.%m.%Y")
            payload = {
                "parent_id": parent_id,
                "child_id": child_id,
                "goal_type": goal_type_key,
                "target_value": target_val,
                "deadline": deadline_str,
            }
            result = api_post("/homework/goals/set", data=payload)
            if result:
                st.success(f"Hedef basariyla olusturuldu! Hedef ID: {result.get('goal_id', 'N/A')}")
            else:
                st.warning("API baglantisi kurulamadi. Demo modunda hedef olusturma simulasyonu:")
                st.markdown(f"""
                <div class="success-box">
                    <strong>Hedef Olusturuldu (Demo)</strong><br>
                    <strong>Tur:</strong> {goal_type_label}<br>
                    <strong>Hedef:</strong> {target_val}<br>
                    <strong>Son Tarih:</strong> {deadline_str}<br>
                    <strong>Durum:</strong> Aktif
                </div>
                """, unsafe_allow_html=True)


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.caption("MathAI Odev Merkezi - Adaptif Matematik Ogrenme Platformu")
