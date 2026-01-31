"""
Gunluk Gorevler Sayfasi - Daily Challenges.

Gunluk ve haftalik matematik gorevleri ile ogrencilerin duzenli calismasini
tesvik eden oyunlastirilmis gorev merkezi. Turkce arayuz.
"""

import streamlit as st
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
# Sayfa yapilandirmasi
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Gunluk Gorevler - MathAI",
    page_icon="🎯",
    layout="wide",
)

apply_theme()
render_sidebar("pages/daily_challenges")

# ---------------------------------------------------------------------------
# Ek CSS - gunluk gorevler sayfasina ozel stiller
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Gorev hero gradient */
.challenge-hero {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #ffd200 100%);
    border-radius: 20px;
    padding: 40px 36px;
    color: white;
    text-align: center;
    margin-bottom: 28px;
    box-shadow: 0 12px 40px rgba(240, 147, 251, 0.35);
    position: relative;
    overflow: hidden;
}
.challenge-hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
    animation: hero-shimmer 6s ease-in-out infinite;
}
@keyframes hero-shimmer {
    0%, 100% { transform: translateX(-30%) translateY(-30%); }
    50% { transform: translateX(10%) translateY(10%); }
}
.challenge-hero h1 {
    color: white !important;
    font-size: 2.4em;
    font-weight: 700;
    margin: 0 0 8px 0;
    position: relative;
}
.challenge-hero p {
    color: rgba(255,255,255,0.92);
    font-size: 1.15em;
    margin: 0;
    position: relative;
}

/* Gorev karti */
.challenge-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 1px solid #f0f0f0;
    margin-bottom: 16px;
    transition: transform 0.25s, box-shadow 0.25s;
    position: relative;
    overflow: hidden;
}
.challenge-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.14);
}
.challenge-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}
.challenge-card.diff-easy::before { background: linear-gradient(90deg, #28a745, #6fcf97); }
.challenge-card.diff-medium::before { background: linear-gradient(90deg, #007bff, #6cb4ee); }
.challenge-card.diff-hard::before { background: linear-gradient(90deg, #fd7e14, #fdb97e); }
.challenge-card.diff-legendary::before { background: linear-gradient(90deg, #dc3545, #ff6b81); }

.challenge-card-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
}
.challenge-icon {
    font-size: 2.2em;
    flex-shrink: 0;
    width: 54px; height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    background: #f8f9fa;
}
.challenge-title {
    font-size: 1.15em;
    font-weight: 700;
    color: #333;
    margin: 0;
    line-height: 1.3;
}
.challenge-desc {
    font-size: 0.9em;
    color: #666;
    line-height: 1.6;
    margin: 0 0 14px 0;
}

/* Gorev ilerleme cubugu */
.challenge-progress-outer {
    background: #e9ecef;
    border-radius: 10px;
    height: 14px;
    overflow: hidden;
    position: relative;
    margin-bottom: 8px;
}
.challenge-progress-inner {
    height: 100%;
    border-radius: 10px;
    transition: width 0.6s ease;
}
.challenge-progress-inner.pg-easy { background: linear-gradient(90deg, #28a745, #6fcf97); }
.challenge-progress-inner.pg-medium { background: linear-gradient(90deg, #007bff, #6cb4ee); }
.challenge-progress-inner.pg-hard { background: linear-gradient(90deg, #fd7e14, #fdb97e); }
.challenge-progress-inner.pg-legendary { background: linear-gradient(90deg, #dc3545, #ff6b81); }

.challenge-progress-text {
    display: flex;
    justify-content: space-between;
    font-size: 0.82em;
    color: #888;
}

/* Zorluk rozetleri */
.diff-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 16px;
    font-size: 0.78em;
    font-weight: 600;
    margin-right: 6px;
}
.diff-badge-easy { background: #d4edda; color: #155724; }
.diff-badge-medium { background: #cce5ff; color: #004085; }
.diff-badge-hard { background: #fff3cd; color: #856404; }
.diff-badge-legendary { background: #f8d7da; color: #721c24; }

/* XP rozeti */
.xp-reward-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 12px;
    border-radius: 16px;
    font-size: 0.78em;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

/* Tamamlandi rozeti */
.completed-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 5px 16px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 700;
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    color: white;
    box-shadow: 0 3px 12px rgba(40, 167, 69, 0.3);
}

/* Zaman siniri */
.time-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 12px;
    border-radius: 16px;
    font-size: 0.78em;
    font-weight: 600;
    background: #f8f9fa;
    color: #555;
    border: 1px solid #e9ecef;
}

/* Ozet karti */
.summary-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 24px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.35);
    margin-bottom: 16px;
}
.summary-card h3 {
    color: white !important;
    margin: 0 0 8px 0;
}
.summary-value {
    font-size: 2.2em;
    font-weight: 800;
    line-height: 1.1;
}
.summary-label {
    font-size: 0.88em;
    opacity: 0.85;
    margin-top: 4px;
}

/* Sifirlama alani */
.reset-area {
    background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
    border-radius: 12px;
    padding: 16px;
    border-left: 4px solid #ffc107;
    color: #856404;
    margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Yardimci fonksiyonlar
# ---------------------------------------------------------------------------

DIFFICULTY_COLORS: Dict[str, str] = {
    "easy": "#28a745",
    "medium": "#007bff",
    "hard": "#fd7e14",
    "legendary": "#dc3545",
}

DIFFICULTY_LABELS_TR: Dict[str, str] = {
    "easy": "Kolay",
    "medium": "Orta",
    "hard": "Zor",
    "legendary": "Efsanevi",
}


def _get_diff_class(difficulty: str) -> str:
    """Zorluk seviyesine gore CSS sinifi dondurur."""
    return f"diff-{difficulty}" if difficulty in DIFFICULTY_COLORS else "diff-easy"


def _get_diff_badge_html(difficulty: str) -> str:
    """Zorluk seviyesine gore HTML rozet dondurur."""
    label = DIFFICULTY_LABELS_TR.get(difficulty, difficulty.title())
    css = f"diff-badge-{difficulty}" if difficulty in DIFFICULTY_COLORS else "diff-badge-easy"
    return f'<span class="diff-badge {css}">{label}</span>'


def _render_challenge_card(challenge: Dict[str, Any]) -> None:
    """Tek bir gorev kartini render eder."""
    title_tr = challenge.get("title_tr", challenge.get("title", "Gorev"))
    desc_tr = challenge.get("description_tr", challenge.get("description", ""))
    icon = challenge.get("icon", "🎯")
    difficulty = challenge.get("difficulty", "easy")
    xp_reward = challenge.get("xp_reward", 10)
    time_limit = challenge.get("time_limit_minutes", None)

    prog = challenge.get("progress", {})
    current = prog.get("current", 0)
    target = prog.get("target", 1)
    percent = prog.get("percent", 0)
    is_completed = prog.get("is_completed", False)
    completed_at = prog.get("completed_at", None)

    diff_class = _get_diff_class(difficulty)
    diff_badge = _get_diff_badge_html(difficulty)
    pg_class = f"pg-{difficulty}" if difficulty in DIFFICULTY_COLORS else "pg-easy"
    bar_pct = min(max(percent, 0), 100)

    # Tamamlandi rozeti
    completed_html = ""
    if is_completed:
        completed_html = '<span class="completed-badge">✅ Tamamlandi</span>'

    # Zaman siniri rozeti
    time_html = ""
    if time_limit:
        time_html = f'<span class="time-badge">⏰ {time_limit} dk</span>'

    st.markdown(f"""
    <div class="challenge-card {diff_class}">
        <div class="challenge-card-header">
            <div class="challenge-icon">{icon}</div>
            <div style="flex:1;">
                <div class="challenge-title">{title_tr}</div>
                <div style="margin-top:6px; display:flex; gap:6px; flex-wrap:wrap; align-items:center;">
                    {diff_badge}
                    <span class="xp-reward-badge">⭐ {xp_reward} XP</span>
                    {time_html}
                    {completed_html}
                </div>
            </div>
        </div>
        <div class="challenge-desc">{desc_tr}</div>
        <div class="challenge-progress-outer">
            <div class="challenge-progress-inner {pg_class}" style="width: {bar_pct}%"></div>
        </div>
        <div class="challenge-progress-text">
            <span>{current} / {target}</span>
            <span>%{bar_pct:.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Yedek / demo veriler
# ---------------------------------------------------------------------------

FALLBACK_DAILY_CHALLENGES: List[Dict[str, Any]] = [
    {
        "id": "daily_1",
        "type": "question_count",
        "difficulty": "easy",
        "title": "Daily Practice",
        "title_tr": "Gunluk Pratik",
        "description": "Solve 5 math questions today",
        "description_tr": "Bugun 5 matematik sorusu coz ve guclenmeni surdurmeni sagla.",
        "target_value": 5,
        "xp_reward": 25,
        "icon": "📝",
        "color": "#28a745",
        "topic_slug": None,
        "time_limit_minutes": None,
        "progress": {
            "current": 2,
            "target": 5,
            "percent": 40,
            "is_completed": False,
            "completed_at": None,
        },
    },
    {
        "id": "daily_2",
        "type": "correct_streak",
        "difficulty": "medium",
        "title": "Accuracy Streak",
        "title_tr": "Dogru Cevap Serisi",
        "description": "Get 3 correct answers in a row",
        "description_tr": "Arka arkaya 3 dogru cevap vererek konsantrasyonunu kanitla.",
        "target_value": 3,
        "xp_reward": 40,
        "icon": "🎯",
        "color": "#007bff",
        "topic_slug": None,
        "time_limit_minutes": 30,
        "progress": {
            "current": 1,
            "target": 3,
            "percent": 33,
            "is_completed": False,
            "completed_at": None,
        },
    },
    {
        "id": "daily_3",
        "type": "topic_mastery",
        "difficulty": "hard",
        "title": "Topic Challenge",
        "title_tr": "Konu Hakimiyeti",
        "description": "Reach 80% mastery in algebra",
        "description_tr": "Cebir konusunda %80 hakimiyet seviyesine ulas ve ustunlugunu goster.",
        "target_value": 80,
        "xp_reward": 60,
        "icon": "🧠",
        "color": "#fd7e14",
        "topic_slug": "algebra",
        "time_limit_minutes": 60,
        "progress": {
            "current": 55,
            "target": 80,
            "percent": 69,
            "is_completed": False,
            "completed_at": None,
        },
    },
]

FALLBACK_WEEKLY_CHALLENGES: List[Dict[str, Any]] = [
    {
        "id": "weekly_1",
        "type": "question_count",
        "difficulty": "easy",
        "title": "Weekly Marathon",
        "title_tr": "Haftalik Maraton",
        "description": "Solve 30 questions this week",
        "description_tr": "Bu hafta toplam 30 soru cozerek duzeni aliskanligi haline getir.",
        "target_value": 30,
        "xp_reward": 100,
        "icon": "🏃",
        "color": "#28a745",
        "topic_slug": None,
        "time_limit_minutes": None,
        "progress": {
            "current": 12,
            "target": 30,
            "percent": 40,
            "is_completed": False,
            "completed_at": None,
        },
    },
    {
        "id": "weekly_2",
        "type": "multi_topic",
        "difficulty": "medium",
        "title": "Explorer Challenge",
        "title_tr": "Kesif Gorevi",
        "description": "Practice in 4 different topics",
        "description_tr": "4 farkli konuda pratik yaparak bilgi ufkunu genislet.",
        "target_value": 4,
        "xp_reward": 75,
        "icon": "🌍",
        "color": "#007bff",
        "topic_slug": None,
        "time_limit_minutes": None,
        "progress": {
            "current": 2,
            "target": 4,
            "percent": 50,
            "is_completed": False,
            "completed_at": None,
        },
    },
    {
        "id": "weekly_3",
        "type": "speed_challenge",
        "difficulty": "legendary",
        "title": "Speed Master",
        "title_tr": "Hiz Ustasi",
        "description": "Solve 10 questions in under 30 seconds each",
        "description_tr": "10 soruyu 30 saniyeden kisa surede cozerek hiz rekoru kir.",
        "target_value": 10,
        "xp_reward": 150,
        "icon": "⚡",
        "color": "#dc3545",
        "topic_slug": None,
        "time_limit_minutes": 15,
        "progress": {
            "current": 3,
            "target": 10,
            "percent": 30,
            "is_completed": False,
            "completed_at": None,
        },
    },
]


def _compute_summary(challenges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Gorev listesi icin ozet istatistikler hesaplar."""
    total = len(challenges)
    completed = sum(1 for c in challenges if c.get("progress", {}).get("is_completed", False))
    total_xp = sum(c.get("xp_reward", 0) for c in challenges)
    earned_xp = sum(
        c.get("xp_reward", 0)
        for c in challenges
        if c.get("progress", {}).get("is_completed", False)
    )
    overall_pct = (
        sum(c.get("progress", {}).get("percent", 0) for c in challenges) / total
        if total > 0
        else 0
    )
    return {
        "total": total,
        "completed": completed,
        "total_xp": total_xp,
        "earned_xp": earned_xp,
        "overall_percent": overall_pct,
    }


# ---------------------------------------------------------------------------
# 1. Hero Karti
# ---------------------------------------------------------------------------
st.markdown("""
<div class="challenge-hero">
    <h1>🎯 Gunluk Gorevler</h1>
    <p>Her gun yeni gorevler tamamla, XP kazan ve matematik becerilerini gelistir!
       Duzenli calisma aliskanligi edinmek basarinin anahtaridir.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. Kullanici ID girisi
# ---------------------------------------------------------------------------
col_input, _ = st.columns([1, 2])
with col_input:
    user_id = st.text_input(
        "👤 Kullanici ID",
        value="demo_user",
        help="Gorevlerinizi gormek icin kullanici kimliginizi girin.",
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# 3. Verileri cek
# ---------------------------------------------------------------------------
daily_data = api_get(f"/challenges/daily/{user_id}")
weekly_data = api_get(f"/challenges/weekly/{user_id}")

using_fallback = False

if daily_data is not None:
    daily_challenges = daily_data.get("challenges", [])
else:
    daily_challenges = FALLBACK_DAILY_CHALLENGES
    using_fallback = True

if weekly_data is not None:
    weekly_challenges = weekly_data.get("challenges", [])
else:
    weekly_challenges = FALLBACK_WEEKLY_CHALLENGES
    using_fallback = True

if using_fallback:
    st.caption("⚠️ API baglantisi kurulamadi, ornek veriler gosteriliyor.")

# ---------------------------------------------------------------------------
# 4. Ozet Istatistikler
# ---------------------------------------------------------------------------
daily_summary = _compute_summary(daily_challenges)
weekly_summary = _compute_summary(weekly_challenges)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    stat_card(
        f"{daily_summary['completed']}/{daily_summary['total']}",
        "Gunluk Tamamlanan",
        "✅",
    )
with col_s2:
    stat_card(
        f"{weekly_summary['completed']}/{weekly_summary['total']}",
        "Haftalik Tamamlanan",
        "📅",
    )
with col_s3:
    total_earned = daily_summary["earned_xp"] + weekly_summary["earned_xp"]
    stat_card(f"{total_earned}", "Kazanilan XP", "⭐")
with col_s4:
    total_possible = daily_summary["total_xp"] + weekly_summary["total_xp"]
    stat_card(f"{total_possible}", "Toplam XP Odulu", "💫")

st.markdown("")

# Genel ilerleme cubugu
all_challenges = daily_challenges + weekly_challenges
all_summary = _compute_summary(all_challenges)
progress_bar(
    all_summary["overall_percent"] / 100,
    "Genel Gorev Ilerleme",
)

st.markdown("---")

# ---------------------------------------------------------------------------
# 5. Sekmeler: Gunluk ve Haftalik
# ---------------------------------------------------------------------------
tab_daily, tab_weekly = st.tabs(
    ["📆 Gunluk Gorevler", "📅 Haftalik Gorevler"]
)

# ===== GUNLUK GOREVLER =====================================================
with tab_daily:
    section_header("📆 Bugunun Gorevleri")

    if not daily_challenges:
        st.info("Bugun icin henuz gorev bulunmuyor. Daha sonra tekrar kontrol edin!")
    else:
        # Ozet kutusu
        d_sum = daily_summary
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.markdown(f"""
            <div class="summary-card">
                <h3>🎯 Gunluk Ilerleme</h3>
                <div class="summary-value">%{d_sum['overall_percent']:.0f}</div>
                <div class="summary-label">{d_sum['completed']}/{d_sum['total']} gorev tamamlandi</div>
            </div>
            """, unsafe_allow_html=True)
        with col_d2:
            st.markdown(f"""
            <div class="summary-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); box-shadow: 0 8px 30px rgba(40, 167, 69, 0.35);">
                <h3>⭐ Kazanilan XP</h3>
                <div class="summary-value">{d_sum['earned_xp']}</div>
                <div class="summary-label">{d_sum['total_xp']} toplam XP mevcut</div>
            </div>
            """, unsafe_allow_html=True)
        with col_d3:
            remaining = d_sum["total"] - d_sum["completed"]
            st.markdown(f"""
            <div class="summary-card" style="background: linear-gradient(135deg, #fd7e14 0%, #fdb97e 100%); box-shadow: 0 8px 30px rgba(253, 126, 20, 0.35);">
                <h3>📋 Kalan Gorevler</h3>
                <div class="summary-value">{remaining}</div>
                <div class="summary-label">Tamamlanmayi bekliyor</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Gorev kartlarini listele
        for challenge in daily_challenges:
            _render_challenge_card(challenge)

    st.markdown("")

    # Sifirlama bolumu
    st.markdown("")
    with st.expander("🔄 Gunluk Ilerlemeyi Sifirla"):
        st.markdown("""
        <div class="reset-area">
            <strong>⚠️ Dikkat:</strong> Bu islem bugunun tum gorev ilerlemesini sifirlar.
            Bu islem geri alinamaz.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button(
            "🔄 Gunluk Ilerlemeyi Sifirla",
            key="reset_daily",
            type="secondary",
            use_container_width=True,
        ):
            result = api_post(f"/challenges/reset/{user_id}")
            if result is not None:
                st.success("✅ Gunluk ilerleme basariyla sifirlandi!")
                st.rerun()
            else:
                st.error("Sifirlama basarisiz oldu. API baglantisini kontrol edin.")


# ===== HAFTALIK GOREVLER ====================================================
with tab_weekly:
    section_header("📅 Bu Haftanin Gorevleri")

    if not weekly_challenges:
        st.info("Bu hafta icin henuz gorev bulunmuyor. Daha sonra tekrar kontrol edin!")
    else:
        # Ozet kutusu
        w_sum = weekly_summary
        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            st.markdown(f"""
            <div class="summary-card">
                <h3>📅 Haftalik Ilerleme</h3>
                <div class="summary-value">%{w_sum['overall_percent']:.0f}</div>
                <div class="summary-label">{w_sum['completed']}/{w_sum['total']} gorev tamamlandi</div>
            </div>
            """, unsafe_allow_html=True)
        with col_w2:
            st.markdown(f"""
            <div class="summary-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); box-shadow: 0 8px 30px rgba(40, 167, 69, 0.35);">
                <h3>⭐ Kazanilan XP</h3>
                <div class="summary-value">{w_sum['earned_xp']}</div>
                <div class="summary-label">{w_sum['total_xp']} toplam XP mevcut</div>
            </div>
            """, unsafe_allow_html=True)
        with col_w3:
            w_remaining = w_sum["total"] - w_sum["completed"]
            st.markdown(f"""
            <div class="summary-card" style="background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); box-shadow: 0 8px 30px rgba(118, 75, 162, 0.35);">
                <h3>📋 Kalan Gorevler</h3>
                <div class="summary-value">{w_remaining}</div>
                <div class="summary-label">Tamamlanmayi bekliyor</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Gorev kartlarini listele
        for challenge in weekly_challenges:
            _render_challenge_card(challenge)

st.markdown("---")

# ---------------------------------------------------------------------------
# 6. Gorev Aksiyonlari - Cevap Kaydet, Ilerleme Guncelle, Hakimiyet Kaydet
# ---------------------------------------------------------------------------
section_header("🎮 Gorev Aksiyonlari")

st.markdown("""
<div class="info-box">
    <strong>💡 Bilgi:</strong> Asagidaki formlar ile gorev ilerlemesi kaydedebilir,
    cevap girebilir ve konu hakimiyetinizi guncelleyebilirsiniz.
</div>
""", unsafe_allow_html=True)

st.markdown("")

action_tab1, action_tab2, action_tab3 = st.tabs(
    ["✅ Cevap Kaydet", "📈 Ilerleme Guncelle", "🎓 Hakimiyet Kaydet"]
)

# ----- Cevap Kaydet ---------------------------------------------------------
with action_tab1:
    st.markdown("##### ✅ Soru Cevabi Kaydet")
    st.markdown(
        "Cozdugunuz bir sorunun sonucunu kaydedin. "
        "Bu, gunluk gorevlerin otomatik olarak guncellenmesini saglar."
    )
    st.markdown("")

    with st.form("record_answer_form", clear_on_submit=True):
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            is_correct = st.selectbox(
                "Sonuc",
                options=[True, False],
                format_func=lambda x: "✅ Dogru" if x else "❌ Yanlis",
            )
        with col_a2:
            answer_topic = st.text_input(
                "Konu (slug)",
                value="algebra",
                placeholder="Ornegin: algebra, geometry...",
            )

        col_a3, col_a4 = st.columns(2)
        with col_a3:
            response_time_ms = st.number_input(
                "Cevap Suresi (ms)",
                min_value=100,
                max_value=600000,
                value=5000,
                step=500,
                help="Soruya cevap verme suresi milisaniye cinsinden.",
            )
        with col_a4:
            current_streak = st.number_input(
                "Mevcut Seri",
                min_value=0,
                max_value=1000,
                value=0,
                step=1,
                help="Arka arkaya dogru cevap sayisi.",
            )

        submitted_answer = st.form_submit_button(
            "💾 Cevabi Kaydet",
            use_container_width=True,
            type="primary",
        )

        if submitted_answer:
            payload = {
                "user_id": user_id,
                "is_correct": is_correct,
                "topic_slug": answer_topic.strip(),
                "response_time_ms": int(response_time_ms),
                "current_streak": int(current_streak),
            }
            result = api_post("/challenges/record-answer", data=payload)
            if result is not None:
                st.success(
                    "✅ Cevap basariyla kaydedildi! "
                    "Gorev ilerlemeleriniz guncellendi."
                )
                st.rerun()
            else:
                st.error(
                    "Cevap kaydedilemedi. API baglantisini kontrol edin."
                )

# ----- Ilerleme Guncelle ----------------------------------------------------
with action_tab2:
    st.markdown("##### 📈 Gorev Ilerlemesini Guncelle")
    st.markdown(
        "Belirli bir gorev turundeki ilerlemenizi manuel olarak guncelleyin."
    )
    st.markdown("")

    with st.form("update_progress_form", clear_on_submit=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            challenge_type = st.selectbox(
                "Gorev Turu",
                options=[
                    "question_count",
                    "correct_streak",
                    "topic_mastery",
                    "multi_topic",
                    "speed_challenge",
                ],
                format_func=lambda x: {
                    "question_count": "Soru Sayisi",
                    "correct_streak": "Dogru Serisi",
                    "topic_mastery": "Konu Hakimiyeti",
                    "multi_topic": "Coklu Konu",
                    "speed_challenge": "Hiz Meydan Okumasi",
                }.get(x, x),
            )
        with col_p2:
            progress_value = st.number_input(
                "Deger",
                min_value=1,
                max_value=1000,
                value=1,
                step=1,
                help="Ilerleme miktari (ornegin: cozulen soru sayisi).",
            )

        progress_topic = st.text_input(
            "Konu (slug) - Opsiyonel",
            value="",
            placeholder="Bos birakilabilir. Ornegin: geometry, fractions...",
        )

        submitted_progress = st.form_submit_button(
            "📈 Ilerlemeyi Guncelle",
            use_container_width=True,
            type="primary",
        )

        if submitted_progress:
            payload = {
                "user_id": user_id,
                "challenge_type": challenge_type,
                "value": int(progress_value),
            }
            if progress_topic.strip():
                payload["topic_slug"] = progress_topic.strip()

            result = api_post("/challenges/update-progress", data=payload)
            if result is not None:
                st.success(
                    "✅ Ilerleme basariyla guncellendi!"
                )
                st.rerun()
            else:
                st.error(
                    "Ilerleme guncellenemedi. API baglantisini kontrol edin."
                )

# ----- Hakimiyet Kaydet ------------------------------------------------------
with action_tab3:
    st.markdown("##### 🎓 Konu Hakimiyeti Kaydet")
    st.markdown(
        "Bir konudaki hakimiyet yuzdenizi kaydedin. "
        "Bu, konu hakimiyeti gorevlerinin tamamlanmasini tetikleyebilir."
    )
    st.markdown("")

    with st.form("record_mastery_form", clear_on_submit=True):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            mastery_topic = st.text_input(
                "Konu (slug)",
                value="algebra",
                placeholder="Ornegin: algebra, geometry...",
            )
        with col_m2:
            mastery_percent = st.slider(
                "Hakimiyet Yuzdesi",
                min_value=0,
                max_value=100,
                value=75,
                step=5,
                help="Konudaki hakimiyet yuzdesi (0-100).",
            )

        submitted_mastery = st.form_submit_button(
            "🎓 Hakimiyeti Kaydet",
            use_container_width=True,
            type="primary",
        )

        if submitted_mastery:
            if not mastery_topic.strip():
                st.error("Lutfen bir konu girin.")
            else:
                payload = {
                    "user_id": user_id,
                    "topic_slug": mastery_topic.strip(),
                    "mastery_percent": int(mastery_percent),
                }
                result = api_post("/challenges/record-mastery", data=payload)
                if result is not None:
                    st.success(
                        f"✅ {mastery_topic.strip()} konusunda "
                        f"%{mastery_percent} hakimiyet basariyla kaydedildi!"
                    )
                    st.rerun()
                else:
                    st.error(
                        "Hakimiyet kaydedilemedi. API baglantisini kontrol edin."
                    )


# ---------------------------------------------------------------------------
# 7. Alt bilgi
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:16px 0; color:#999; font-size:0.8em;">
    🎯 MathAI Gunluk Gorevler - Adaptif Matematik Platformu •
    Her gun bir adim daha ileri!
</div>
""", unsafe_allow_html=True)
