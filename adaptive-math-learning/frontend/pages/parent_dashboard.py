"""
Veli Takip Paneli - Parent Dashboard Page.

Cocugun ogrenme ilerlemesini takip etme, haftalik raporlar,
konu bazli analiz, basarimlar, ekran suresi ve hedef belirleme
islevlerini sunan kapsamli veli paneli.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

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
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Veli Paneli - MathAI",
    page_icon="\U0001F468\u200D\U0001F467",
    layout="wide",
)

apply_theme()
render_sidebar(active_page="pages/parent_dashboard")


# ---------------------------------------------------------------------------
# Fallback / demo data generators
# ---------------------------------------------------------------------------

def _demo_child_overview() -> Dict[str, Any]:
    return {
        "child_id": "student_001",
        "name": "Ahmet Yilmaz",
        "level": 12,
        "xp": 3450,
        "xp_to_next_level": 4000,
        "streak": 7,
        "mastery": 0.72,
        "accuracy": 0.78,
        "total_questions": 842,
        "total_correct": 657,
        "badges": [
            {"name": "Ilk Adim", "icon": "🌟", "earned": True, "description": "Ilk soruyu coz"},
            {"name": "Hizli Baslangic", "icon": "🚀", "earned": True, "description": "Ilk 10 soruyu coz"},
            {"name": "Seri Avcisi", "icon": "🔥", "earned": True, "description": "5 ardisik dogru yap"},
            {"name": "Matematik Savascisi", "icon": "⚔️", "earned": True, "description": "100 soru coz"},
            {"name": "Konu Ustasi", "icon": "🏆", "earned": True, "description": "Bir konuda %90 hakimiyet"},
            {"name": "Haftalik Sampiyon", "icon": "🥇", "earned": False, "description": "Bir haftada 100 soru coz"},
            {"name": "Mukemmel Hafta", "icon": "💯", "earned": False, "description": "7 gun ust uste calis"},
            {"name": "Bilge", "icon": "🦉", "earned": False, "description": "Tum konularda %80 hakimiyet"},
        ],
        "joined_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
    }


def _demo_weekly_report() -> Dict[str, Any]:
    return {
        "week_start": (datetime.utcnow() - timedelta(days=7)).isoformat(),
        "week_end": datetime.utcnow().isoformat(),
        "days_active": 5,
        "total_questions": 67,
        "accuracy": 0.76,
        "study_minutes": 142,
        "topics_practiced": ["Cebir", "Kesirler", "Geometri", "Aritmetik"],
        "strongest_topic": "Aritmetik",
        "strongest_accuracy": 0.92,
        "weakest_topic": "Cebir",
        "weakest_accuracy": 0.58,
        "longest_streak": 12,
        "questions_change_pct": 15.0,
        "accuracy_change_pct": 3.2,
        "study_time_change_pct": 8.5,
        "improving_topics": ["Kesirler", "Geometri"],
        "declining_topics": [],
        "suggestions": [
            "Cebir konusunda daha fazla pratik yapilmasi onerilir.",
            "Haftalik calisma rutini harika! Ayni tempoda devam edin.",
            "Geometri konusunda guzel bir ilerleme var, tebrikler!",
        ],
    }


def _demo_topic_progress() -> List[Dict[str, Any]]:
    return [
        {"topic": "Aritmetik", "mastery": 0.88, "accuracy": 0.92, "questions_solved": 210, "level": "Uzman"},
        {"topic": "Kesirler", "mastery": 0.72, "accuracy": 0.78, "questions_solved": 145, "level": "Ileri"},
        {"topic": "Yuzdeler", "mastery": 0.68, "accuracy": 0.74, "questions_solved": 98, "level": "Ileri"},
        {"topic": "Cebir", "mastery": 0.55, "accuracy": 0.60, "questions_solved": 120, "level": "Orta"},
        {"topic": "Geometri", "mastery": 0.65, "accuracy": 0.70, "questions_solved": 87, "level": "Orta"},
        {"topic": "Oranlar", "mastery": 0.60, "accuracy": 0.66, "questions_solved": 72, "level": "Orta"},
        {"topic": "Uslu Sayilar", "mastery": 0.45, "accuracy": 0.52, "questions_solved": 54, "level": "Baslangic"},
        {"topic": "Istatistik", "mastery": 0.40, "accuracy": 0.48, "questions_solved": 38, "level": "Baslangic"},
        {"topic": "Trigonometri", "mastery": 0.30, "accuracy": 0.38, "questions_solved": 18, "level": "Baslangic"},
    ]


def _demo_achievements() -> List[Dict[str, Any]]:
    return [
        {"name": "Ilk Adim", "icon": "🌟", "earned": True, "earned_date": "2025-10-15", "description": "Ilk soruyu basariyla coz", "category": "Baslangic"},
        {"name": "Hizli Baslangic", "icon": "🚀", "earned": True, "earned_date": "2025-10-15", "description": "Ilk 10 soruyu coz", "category": "Baslangic"},
        {"name": "Seri Avcisi", "icon": "🔥", "earned": True, "earned_date": "2025-10-18", "description": "5 ardisik dogru yap", "category": "Seri"},
        {"name": "Yangin Serisi", "icon": "🔥🔥", "earned": True, "earned_date": "2025-11-02", "description": "10 ardisik dogru yap", "category": "Seri"},
        {"name": "Matematik Savascisi", "icon": "⚔️", "earned": True, "earned_date": "2025-11-10", "description": "100 soru coz", "category": "Miktar"},
        {"name": "Soru Makinesi", "icon": "⚙️", "earned": True, "earned_date": "2025-12-01", "description": "500 soru coz", "category": "Miktar"},
        {"name": "Konu Ustasi", "icon": "🏆", "earned": True, "earned_date": "2025-12-15", "description": "Bir konuda %90 hakimiyet", "category": "Hakimiyet"},
        {"name": "Haftalik Sampiyon", "icon": "🥇", "earned": False, "earned_date": None, "description": "Bir haftada 100 soru coz", "category": "Haftalik"},
        {"name": "Mukemmel Hafta", "icon": "💯", "earned": False, "earned_date": None, "description": "7 gun ust uste calis", "category": "Haftalik"},
        {"name": "Coklu Konu Ustasi", "icon": "🎓", "earned": False, "earned_date": None, "description": "3 konuda %80 hakimiyet", "category": "Hakimiyet"},
        {"name": "Bilge", "icon": "🦉", "earned": False, "earned_date": None, "description": "Tum konularda %80 hakimiyet", "category": "Hakimiyet"},
        {"name": "Efsane", "icon": "👑", "earned": False, "earned_date": None, "description": "Tum basarimlari topla", "category": "Ozel"},
    ]


def _demo_screen_time() -> Dict[str, Any]:
    return {
        "daily_minutes": [
            {"day": "Pazartesi", "minutes": 32},
            {"day": "Sali", "minutes": 28},
            {"day": "Carsamba", "minutes": 0},
            {"day": "Persembe", "minutes": 45},
            {"day": "Cuma", "minutes": 22},
            {"day": "Cumartesi", "minutes": 38},
            {"day": "Pazar", "minutes": 15},
        ],
        "weekly_total": 180,
        "daily_average": 25.7,
        "most_active_day": "Persembe",
        "least_active_day": "Carsamba",
        "peak_hour": "16:00-17:00",
        "weekly_change_pct": 12.5,
    }


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_hero():
    """Baslik alani."""
    st.markdown("""
    <div class="hero-card">
        <h2>Veli Takip Paneli</h2>
        <p>Cocugunuzun matematik yolculugunu yakindan takip edin, ilerlemesini goruntuleyin ve hedefler belirleyin.</p>
    </div>
    """, unsafe_allow_html=True)


def render_child_overview(data: Dict[str, Any]):
    """Cocugun genel durumu."""
    section_header("Cocuk Genel Durumu")

    name = data.get("name", "Ogrenci")
    level = data.get("level", 1)
    xp = data.get("xp", 0)
    xp_next = data.get("xp_to_next_level", 1000)
    streak = data.get("streak", 0)
    mastery = data.get("mastery", 0)
    accuracy = data.get("accuracy", 0)
    total_q = data.get("total_questions", 0)
    badges = data.get("badges", [])
    earned_badges = [b for b in badges if b.get("earned")]

    # Profile header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px; padding: 24px; color: white; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
            <div style="font-size: 3em;">👦</div>
            <div>
                <h3 style="color: white; margin: 0;">{name}</h3>
                <p style="color: rgba(255,255,255,0.85); margin: 4px 0 0 0;">
                    Seviye {level} &nbsp;|&nbsp; {xp:,} XP &nbsp;|&nbsp; {streak} gunluk seri
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # XP progress to next level
    xp_pct = min(xp / xp_next, 1.0) if xp_next > 0 else 0
    progress_bar(xp_pct, label=f"Sonraki Seviye (Seviye {level + 1}) - {xp:,}/{xp_next:,} XP")
    st.markdown("")

    # Stats grid
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        stat_card(level, "Seviye", icon="📈")
    with c2:
        stat_card(f"{xp:,}", "Toplam XP", icon="⭐")
    with c3:
        stat_card(f"%{mastery * 100:.0f}", "Hakimiyet", icon="🎯")
    with c4:
        stat_card(f"%{accuracy * 100:.0f}", "Dogruluk", icon="✅")
    with c5:
        stat_card(f"{total_q:,}", "Cozulen Soru", icon="📝")

    st.markdown("")

    # Quick badge showcase
    if earned_badges:
        badge_icons = " ".join(b.get("icon", "🏅") for b in earned_badges)
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 16px;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center;">
            <div style="font-size: 0.85em; color: #666; margin-bottom: 8px;">
                Kazanilan Rozetler ({len(earned_badges)}/{len(badges)})
            </div>
            <div style="font-size: 1.8em; letter-spacing: 8px;">{badge_icons}</div>
        </div>
        """, unsafe_allow_html=True)


def render_weekly_report(data: Dict[str, Any]):
    """Haftalik rapor."""
    section_header("Haftalik Rapor")

    if not data:
        st.info("Haftalik rapor verisi bulunamadi.")
        return

    days_active = data.get("days_active", 0)
    total_q = data.get("total_questions", 0)
    accuracy = data.get("accuracy", 0)
    study_min = data.get("study_minutes", 0)
    topics = data.get("topics_practiced", [])
    strongest = data.get("strongest_topic", "-")
    strongest_acc = data.get("strongest_accuracy", 0)
    weakest = data.get("weakest_topic", "-")
    weakest_acc = data.get("weakest_accuracy", 0)
    longest_streak = data.get("longest_streak", 0)

    q_change = data.get("questions_change_pct", 0)
    acc_change = data.get("accuracy_change_pct", 0)
    time_change = data.get("study_time_change_pct", 0)

    # Summary cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card(f"{days_active}/7", "Aktif Gun", icon="📅")
    with c2:
        stat_card(total_q, "Cozulen Soru", icon="📝")
    with c3:
        stat_card(f"%{accuracy * 100:.0f}", "Dogruluk", icon="✅")
    with c4:
        stat_card(f"{study_min} dk", "Calisma Suresi", icon="⏱️")

    st.markdown("")

    # Change indicators
    col1, col2, col3 = st.columns(3)
    with col1:
        delta_color = "normal" if q_change >= 0 else "inverse"
        st.metric("Soru Degisimi", f"%{q_change:+.1f}", delta=f"gecen haftaya gore", delta_color=delta_color)
    with col2:
        delta_color = "normal" if acc_change >= 0 else "inverse"
        st.metric("Dogruluk Degisimi", f"%{acc_change:+.1f}", delta=f"gecen haftaya gore", delta_color=delta_color)
    with col3:
        delta_color = "normal" if time_change >= 0 else "inverse"
        st.metric("Sure Degisimi", f"%{time_change:+.1f}", delta=f"gecen haftaya gore", delta_color=delta_color)

    st.markdown("")

    # Strongest / Weakest
    col_s, col_w = st.columns(2)
    with col_s:
        st.markdown(f"""
        <div class="success-box">
            <strong>En Guclu Konu:</strong> {strongest}<br>
            <strong>Dogruluk:</strong> %{strongest_acc * 100:.0f}
        </div>
        """, unsafe_allow_html=True)
    with col_w:
        st.markdown(f"""
        <div class="warning-box">
            <strong>En Zayif Konu:</strong> {weakest}<br>
            <strong>Dogruluk:</strong> %{weakest_acc * 100:.0f}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Topics practiced this week
    if topics:
        st.markdown(f"**Calisilan Konular:** {', '.join(topics)}")
    st.markdown(f"**En Uzun Seri:** {longest_streak} ardisik dogru")

    # Suggestions
    suggestions = data.get("suggestions", [])
    if suggestions:
        st.markdown("")
        with st.expander("Oneriler ve Degerlendirme", expanded=True):
            for s in suggestions:
                st.markdown(f"- {s}")

    # Improving / Declining topics
    improving = data.get("improving_topics", [])
    declining = data.get("declining_topics", [])
    if improving or declining:
        st.markdown("")
        ci, cd = st.columns(2)
        with ci:
            if improving:
                topics_str = ", ".join(improving)
                st.markdown(f"""
                <div class="success-box">
                    <strong>Gelisen Konular:</strong> {topics_str}
                </div>
                """, unsafe_allow_html=True)
        with cd:
            if declining:
                topics_str = ", ".join(declining)
                st.markdown(f"""
                <div class="warning-box">
                    <strong>Gerileyen Konular:</strong> {topics_str}
                </div>
                """, unsafe_allow_html=True)


def render_topic_progress(topics: List[Dict[str, Any]]):
    """Konu bazli ilerleme."""
    section_header("Konu Bazli Ilerleme")

    if not topics:
        st.info("Konu ilerleme verisi bulunamadi.")
        return

    # Sort by mastery descending
    sorted_topics = sorted(topics, key=lambda x: x.get("mastery", 0), reverse=True)

    for t in sorted_topics:
        topic_name = t.get("topic", "Bilinmiyor")
        mastery = t.get("mastery", 0)
        accuracy = t.get("accuracy", 0)
        solved = t.get("questions_solved", 0)
        level = t.get("level", "Baslangic")

        # Color coding
        if mastery >= 0.8:
            level_color = "#28a745"
            level_badge = "badge-green"
        elif mastery >= 0.6:
            level_color = "#667eea"
            level_badge = "badge-purple"
        elif mastery >= 0.4:
            level_color = "#fd7e14"
            level_badge = "badge-orange"
        else:
            level_color = "#dc3545"
            level_badge = "badge-red"

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                <strong style="color: #333;">{topic_name}</strong>
                <span class="badge {level_badge}">{level}</span>
            </div>
            """, unsafe_allow_html=True)
            progress_bar(mastery, label=f"Hakimiyet")

        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding-top: 8px;">
                <div style="font-size: 1.3em; font-weight: 700; color: {level_color};">
                    %{accuracy * 100:.0f}
                </div>
                <div style="font-size: 0.8em; color: #666;">Dogruluk</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding-top: 8px;">
                <div style="font-size: 1.3em; font-weight: 700; color: #667eea;">
                    {solved}
                </div>
                <div style="font-size: 0.8em; color: #666;">Soru</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")


def render_achievements(achievements: List[Dict[str, Any]]):
    """Basarimlar / rozetler."""
    section_header("Basarimlar ve Rozetler")

    if not achievements:
        st.info("Basarim verisi bulunamadi.")
        return

    earned = [a for a in achievements if a.get("earned")]
    not_earned = [a for a in achievements if not a.get("earned")]

    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 16px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center; margin-bottom: 20px;">
        <div style="font-size: 1.2em; font-weight: 600; color: #333;">
            Toplam Ilerleme: {len(earned)} / {len(achievements)} Basarim
        </div>
    </div>
    """, unsafe_allow_html=True)

    progress_bar(len(earned) / len(achievements) if achievements else 0,
                 label="Basarim Tamamlanma Orani")
    st.markdown("")

    # Earned achievements
    if earned:
        st.markdown("##### Kazanilan Basarimlar")
        cols = st.columns(min(len(earned), 4))
        for i, a in enumerate(earned):
            with cols[i % 4]:
                date_str = a.get("earned_date", "")
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                            border-radius: 12px; padding: 16px; text-align: center;
                            margin-bottom: 12px; min-height: 160px;">
                    <div style="font-size: 2.5em;">{a.get('icon', '🏅')}</div>
                    <div style="font-weight: 600; color: #155724; margin: 8px 0 4px 0;">
                        {a.get('name', '')}
                    </div>
                    <div style="font-size: 0.8em; color: #155724;">
                        {a.get('description', '')}
                    </div>
                    <div style="font-size: 0.75em; color: #666; margin-top: 6px;">
                        {date_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Not yet earned
    if not_earned:
        st.markdown("")
        st.markdown("##### Henuz Kazanilmamis")
        cols = st.columns(min(len(not_earned), 4))
        for i, a in enumerate(not_earned):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="background: #f8f9fa; border-radius: 12px; padding: 16px;
                            text-align: center; margin-bottom: 12px; min-height: 160px;
                            border: 2px dashed #dee2e6;">
                    <div style="font-size: 2.5em; filter: grayscale(100%); opacity: 0.5;">
                        {a.get('icon', '🏅')}
                    </div>
                    <div style="font-weight: 600; color: #999; margin: 8px 0 4px 0;">
                        {a.get('name', '')}
                    </div>
                    <div style="font-size: 0.8em; color: #aaa;">
                        {a.get('description', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)


def render_screen_time(data: Dict[str, Any]):
    """Ekran suresi / calisma suresi."""
    section_header("Calisma Suresi Analizi")

    if not data:
        st.info("Ekran suresi verisi bulunamadi.")
        return

    daily = data.get("daily_minutes", [])
    weekly_total = data.get("weekly_total", 0)
    daily_avg = data.get("daily_average", 0)
    most_active = data.get("most_active_day", "-")
    least_active = data.get("least_active_day", "-")
    peak_hour = data.get("peak_hour", "-")
    weekly_change = data.get("weekly_change_pct", 0)

    # Summary cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card(f"{weekly_total} dk", "Haftalik Toplam", icon="⏱️")
    with c2:
        stat_card(f"{daily_avg:.0f} dk", "Gunluk Ortalama", icon="📊")
    with c3:
        stat_card(most_active, "En Aktif Gun", icon="🟢")
    with c4:
        stat_card(peak_hour, "YoGun Saat", icon="🕐")

    st.markdown("")

    # Daily minutes chart
    if daily:
        chart_df = pd.DataFrame({
            "Gun": [d["day"] for d in daily],
            "Dakika": [d["minutes"] for d in daily],
        }).set_index("Gun")

        st.bar_chart(chart_df, height=300)

    # Additional details
    col1, col2 = st.columns(2)
    with col1:
        delta_color = "normal" if weekly_change >= 0 else "inverse"
        st.metric(
            "Haftalik Degisim",
            f"%{weekly_change:+.1f}",
            delta="gecen haftaya gore",
            delta_color=delta_color,
        )
    with col2:
        st.markdown(f"""
        <div class="info-box">
            <strong>En Az Aktif Gun:</strong> {least_active}<br>
            <em>Bu gunde daha fazla calisma tesvik edilebilir.</em>
        </div>
        """, unsafe_allow_html=True)


def render_set_goal(child_id: str, parent_id: str):
    """Hedef belirleme formu."""
    section_header("Hedef Belirle")

    st.markdown("""
    <div class="info-box" style="margin-bottom: 16px;">
        Cocugunuz icin ogrenme hedefleri belirleyin. Hedefler haftalik raporlarda takip edilecektir.
    </div>
    """, unsafe_allow_html=True)

    with st.form("set_goal_form", clear_on_submit=True):
        st.markdown("##### Yeni Ogrenme Hedefi")

        goal_type = st.selectbox("Hedef Turu", [
            "Haftalik Soru Sayisi",
            "Dogruluk Orani Hedefi (%)",
            "Ardisik Dogru Serisi",
            "Konu Hakimiyet Hedefi (%)",
            "Haftalik Calisma Suresi (dakika)",
        ], key="goal_type_select")

        # Map to API goal types
        goal_type_map = {
            "Haftalik Soru Sayisi": "questions_per_week",
            "Dogruluk Orani Hedefi (%)": "accuracy_target",
            "Ardisik Dogru Serisi": "streak_target",
            "Konu Hakimiyet Hedefi (%)": "mastery_target",
            "Haftalik Calisma Suresi (dakika)": "practice_minutes",
        }

        col_a, col_b = st.columns(2)
        with col_a:
            # Default values per goal type
            if "Soru" in goal_type:
                target_value = st.number_input("Hedef Deger", min_value=1, max_value=500, value=50, step=5)
            elif "Seri" in goal_type:
                target_value = st.number_input("Hedef Deger", min_value=1, max_value=100, value=10, step=1)
            elif "dakika" in goal_type:
                target_value = st.number_input("Hedef Deger", min_value=10, max_value=600, value=120, step=10)
            else:
                target_value = st.number_input("Hedef Deger (%)", min_value=10, max_value=100, value=80, step=5)

        with col_b:
            deadline_days = st.number_input(
                "Hedef Suresi (gun)", min_value=1, max_value=90, value=14, step=1,
            )

        motivation_msg = st.text_area(
            "Motivasyon Mesaji (Opsiyonel)",
            placeholder="Cocugunuza bir mesaj yazabilirsiniz...",
            help="Bu mesaj cocugunuzun panelinde goruntulenecektir.",
        )

        submitted = st.form_submit_button("Hedefi Kaydet", type="primary", use_container_width=True)

        if submitted:
            if target_value <= 0:
                st.error("Lutfen gecerli bir hedef degeri girin.")
            else:
                deadline = (datetime.utcnow() + timedelta(days=deadline_days)).isoformat()
                payload = {
                    "goal_type": goal_type_map.get(goal_type, "questions_per_week"),
                    "target_value": target_value,
                    "deadline": deadline,
                    "motivation_message": motivation_msg,
                }
                result = api_post(
                    f"/parent/child/{child_id}/goals?parent_id={parent_id}",
                    data=payload,
                )
                if result:
                    st.success("Hedef basariyla kaydedildi!")
                    st.balloons()
                else:
                    st.warning("API baglantisi kurulamadi. Demo modunda hedef olusturuldu.")
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>Hedef Olusturuldu (Demo)</strong><br>
                        <strong>Tur:</strong> {goal_type}<br>
                        <strong>Hedef:</strong> {target_value}<br>
                        <strong>Sure:</strong> {deadline_days} gun
                    </div>
                    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    render_hero()

    # Child ID + Parent ID inputs
    st.markdown("")
    col_id1, col_id2 = st.columns(2)
    with col_id1:
        child_id = st.text_input(
            "Cocuk Kimlik Numarasi",
            value="student_001",
            key="child_id_input",
            help="Cocugunuzun ogrenci ID'sini girin.",
        )
    with col_id2:
        parent_id = st.text_input(
            "Veli Kimlik Numarasi",
            value="parent_001",
            key="parent_id_input",
            help="Kendi veli ID'nizi girin.",
        )

    if not child_id.strip() or not parent_id.strip():
        st.warning("Lutfen gecerli Cocuk ID ve Veli ID girin.")
        return

    st.markdown("---")

    # ---- 1. Child Overview ----
    overview = api_get(f"/parent/child/{child_id}/overview", params={"parent_id": parent_id})
    if overview is None:
        overview = _demo_child_overview()
    render_child_overview(overview)

    st.markdown("---")

    # ---- 2. Weekly Report ----
    report = api_get(f"/parent/child/{child_id}/weekly-report", params={"parent_id": parent_id})
    if report is None:
        report = _demo_weekly_report()
    render_weekly_report(report)

    st.markdown("---")

    # ---- 3. Topic Progress ----
    topics = api_get(f"/parent/child/{child_id}/topics", params={"parent_id": parent_id})
    if topics is None:
        topics = _demo_topic_progress()
    render_topic_progress(topics)

    st.markdown("---")

    # ---- 4. Achievements ----
    achievements = api_get(f"/parent/child/{child_id}/achievements", params={"parent_id": parent_id})
    if achievements is None:
        achievements = _demo_achievements()
    render_achievements(achievements)

    st.markdown("---")

    # ---- 5. Screen Time ----
    screen_time = api_get(f"/parent/child/{child_id}/screen-time", params={"parent_id": parent_id})
    if screen_time is None:
        screen_time = _demo_screen_time()
    render_screen_time(screen_time)

    st.markdown("---")

    # ---- 6. Set Goal ----
    render_set_goal(child_id, parent_id)

    # Footer
    st.markdown("---")
    st.caption("MathAI Veli Paneli - Adaptif Matematik Ogrenme Platformu")


if __name__ == "__main__":
    main()
