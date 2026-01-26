"""
Oyunlastirma Sayfasi - Gamification Dashboard.

XP, rozet, seri ve liderlik tablosu ile oyunlastirma merkezi.
Turkce arayuz ile gorsel olarak zengin bir oyun basari paneli.
"""

import streamlit as st
from frontend.theme import (
    apply_theme,
    render_sidebar,
    api_get,
    api_post,
    stat_card,
    section_header,
    progress_bar,
)

# Sayfa yapilandirmasi
st.set_page_config(
    page_title="Oyunlastirma - MathAI",
    page_icon="\U0001F3C6",
    layout="wide",
)

# Tema ve kenar cubugu
apply_theme()
render_sidebar("gamification")

# ---------------------------------------------------------------------------
# Ek CSS - oyunlastirma sayfasina ozel stiller
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Seviye ilerleme cubugu */
.xp-progress-outer {
    background: #e9ecef;
    border-radius: 12px;
    height: 24px;
    overflow: hidden;
    position: relative;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}
.xp-progress-inner {
    height: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.xp-progress-inner::after {
    content: '';
    position: absolute;
    top: 0; left: -100%; width: 200%; height: 100%;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
    animation: shimmer 2s infinite;
}
@keyframes shimmer {
    0% { transform: translateX(-50%); }
    100% { transform: translateX(50%); }
}
.xp-progress-text {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.75em;
    font-weight: 700;
    color: #333;
    text-shadow: 0 0 4px rgba(255,255,255,0.8);
    z-index: 2;
    width: 100%;
    text-align: center;
}

/* Seviye rozeti */
.level-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 20px;
    border-radius: 24px;
    font-weight: 700;
    font-size: 1.1em;
    color: white;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* Seri karti */
.streak-card {
    background: linear-gradient(135deg, #ff9a56 0%, #ff6a00 100%);
    border-radius: 16px;
    padding: 24px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 30px rgba(255, 106, 0, 0.3);
    position: relative;
    overflow: hidden;
}
.streak-card::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 100px; height: 100px;
    background: rgba(255,255,255,0.1);
    border-radius: 50%;
}
.streak-value {
    font-size: 3em;
    font-weight: 800;
    line-height: 1;
    margin: 8px 0;
}
.streak-label {
    font-size: 0.9em;
    opacity: 0.9;
}
.streak-dead {
    background: linear-gradient(135deg, #636e72 0%, #2d3436 100%);
    box-shadow: 0 8px 30px rgba(45, 52, 54, 0.3);
}

/* Rozet kartlari */
.badge-card {
    background: white;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 3px 15px rgba(0,0,0,0.08);
    border: 2px solid #f0f0f0;
    transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
    height: 100%;
    min-height: 180px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.badge-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}
.badge-card.earned {
    border-color: #667eea;
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
}
.badge-card.unearned {
    opacity: 0.5;
    filter: grayscale(60%);
}
.badge-icon {
    font-size: 2.8em;
    margin-bottom: 8px;
}
.badge-name {
    font-weight: 700;
    font-size: 0.95em;
    color: #333;
    margin-bottom: 4px;
}
.badge-desc {
    font-size: 0.78em;
    color: #888;
    line-height: 1.4;
}
.badge-earned-tag {
    display: inline-block;
    margin-top: 8px;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.7em;
    font-weight: 600;
    background: #667eea;
    color: white;
}
.badge-locked-tag {
    display: inline-block;
    margin-top: 8px;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.7em;
    font-weight: 600;
    background: #ccc;
    color: #666;
}

/* Liderlik tablosu */
.lb-row {
    display: flex;
    align-items: center;
    padding: 14px 20px;
    background: white;
    border-radius: 10px;
    margin-bottom: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}
.lb-row:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.lb-row.gold {
    background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
    border-left: 4px solid #FFD700;
}
.lb-row.silver {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-left: 4px solid #C0C0C0;
}
.lb-row.bronze {
    background: linear-gradient(135deg, #fef5ee 0%, #fde8d0 100%);
    border-left: 4px solid #CD7F32;
}
.lb-rank {
    font-size: 1.3em;
    font-weight: 800;
    width: 50px;
    text-align: center;
    flex-shrink: 0;
}
.lb-rank.r1 { color: #FFD700; }
.lb-rank.r2 { color: #C0C0C0; }
.lb-rank.r3 { color: #CD7F32; }
.lb-rank.rn { color: #667eea; }
.lb-user {
    flex: 1;
    font-weight: 600;
    color: #333;
    padding-left: 12px;
}
.lb-xp {
    font-weight: 700;
    color: #667eea;
    padding-right: 16px;
    white-space: nowrap;
}
.lb-level {
    font-size: 0.85em;
    color: #666;
    white-space: nowrap;
}

/* XP kazanim bildirim kutusu */
.xp-award-result {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    border-radius: 12px;
    padding: 20px;
    border-left: 5px solid #28a745;
    text-align: center;
}
.xp-award-result h4 {
    color: #155724;
    margin: 0 0 8px 0;
}
.xp-award-result p {
    color: #155724;
    margin: 0;
}

/* Kendi siraniz kutusu */
.my-rank-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 14px;
    padding: 20px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.35);
}
.my-rank-value {
    font-size: 2.5em;
    font-weight: 800;
    line-height: 1.1;
}
.my-rank-label {
    font-size: 0.9em;
    opacity: 0.85;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Yardimci fonksiyonlar
# ---------------------------------------------------------------------------

LEVEL_NAMES = {
    1: "Cirak",
    2: "Ogrenci",
    3: "Kesfedici",
    4: "Problem Cozucu",
    5: "Matematik Yildizi",
    6: "Uzman",
    7: "Bilge",
    8: "Usta",
    9: "Dahi",
    10: "Efsane",
}


def get_level_name_tr(level: int, api_name: str = "") -> str:
    """Seviye numarasina gore Turkce seviye adi dondurur."""
    return LEVEL_NAMES.get(level, api_name if api_name else f"Seviye {level}")


FALLBACK_BADGES = [
    {"badge_type": "first_question", "name": "Ilk Adim", "description": "Ilk soruyu coz", "icon": "\U0001F476", "earned": False, "progress": 0.0},
    {"badge_type": "streak_3", "name": "Atesi Yak", "description": "3 gunluk seri yap", "icon": "\U0001F525", "earned": False, "progress": 0.0},
    {"badge_type": "streak_7", "name": "Haftalik Savas\u00E7i", "description": "7 gunluk seri yap", "icon": "\u2694\uFE0F", "earned": False, "progress": 0.0},
    {"badge_type": "streak_30", "name": "Ay Yildizi", "description": "30 gunluk seri yap", "icon": "\U0001F319", "earned": False, "progress": 0.0},
    {"badge_type": "xp_100", "name": "XP Avcisi", "description": "100 XP kazan", "icon": "\U0001F4AB", "earned": False, "progress": 0.0},
    {"badge_type": "xp_500", "name": "XP Ustasi", "description": "500 XP kazan", "icon": "\U0001F451", "earned": False, "progress": 0.0},
    {"badge_type": "xp_1000", "name": "XP Efsanesi", "description": "1000 XP kazan", "icon": "\U0001F3C6", "earned": False, "progress": 0.0},
    {"badge_type": "perfect_10", "name": "Mukemmel 10", "description": "Arka arkaya 10 dogru cevap ver", "icon": "\U0001F4AF", "earned": False, "progress": 0.0},
    {"badge_type": "topic_master", "name": "Konu Ustasi", "description": "Bir konuda ustunluk kazan", "icon": "\U0001F393", "earned": False, "progress": 0.0},
    {"badge_type": "night_owl", "name": "Gece Kusu", "description": "Gece 23:00'ten sonra calis", "icon": "\U0001F989", "earned": False, "progress": 0.0},
    {"badge_type": "speed_demon", "name": "Hiz Seytani", "description": "Bir soruyu 10 saniyede coz", "icon": "\u26A1", "earned": False, "progress": 0.0},
    {"badge_type": "social_star", "name": "Sosyal Yildiz", "description": "3 arkadasi davet et", "icon": "\U0001F31F", "earned": False, "progress": 0.0},
]

FALLBACK_LEADERBOARD = [
    {"rank": 1, "user_id": "matematik_dahi", "display_name": "MatematikDahi42", "total_xp": 4850, "level": 8},
    {"rank": 2, "user_id": "sayi_ustasi", "display_name": "SayiUstasi", "total_xp": 3720, "level": 7},
    {"rank": 3, "user_id": "formul_krali", "display_name": "FormulKrali", "total_xp": 3100, "level": 6},
    {"rank": 4, "user_id": "pi_sever", "display_name": "PiSever314", "total_xp": 2450, "level": 5},
    {"rank": 5, "user_id": "delta_x", "display_name": "DeltaX", "total_xp": 1980, "level": 5},
    {"rank": 6, "user_id": "integral_fan", "display_name": "IntegralFan", "total_xp": 1540, "level": 4},
    {"rank": 7, "user_id": "demo_user", "display_name": "demo_user", "total_xp": 1200, "level": 4},
    {"rank": 8, "user_id": "cebir_ninja", "display_name": "CebirNinja", "total_xp": 890, "level": 3},
    {"rank": 9, "user_id": "geometri_pro", "display_name": "GeometriPro", "total_xp": 650, "level": 3},
    {"rank": 10, "user_id": "yeni_baslayen", "display_name": "YeniBaslayen", "total_xp": 320, "level": 2},
]


# ---------------------------------------------------------------------------
# 1. Hero Karti
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-card">
    <h2>\U0001F3C6 Oyunla\u015Ft\u0131rma Merkezi</h2>
    <p>
        XP kazan, seviye atla, rozet topla ve liderlik tablosunda zirvaye \u00E7\u0131k!
        Her do\u011Fru cevap seni bir ad\u0131m ileriye ta\u015F\u0131r. Matematik yolculu\u011Funu
        bir oyuna d\u00F6n\u00FC\u015Ft\u00FCr ve \u00F6\u011Frenmenin keyfini \u00E7\u0131kar.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 2. Kullanici ID girisi
# ---------------------------------------------------------------------------
st.markdown("")
col_input, _ = st.columns([1, 2])
with col_input:
    user_id = st.text_input(
        "\U0001F464 Kullan\u0131c\u0131 ID",
        value="demo_user",
        help="Oyunla\u015Ft\u0131rma verilerinizi g\u00F6rmek i\u00E7in kullan\u0131c\u0131 kimli\u011Finizi girin.",
    )

st.markdown("---")


# ---------------------------------------------------------------------------
# 3. XP & Seviye Bolumu
# ---------------------------------------------------------------------------
section_header("\u2B50 XP & Seviye")

xp_data = api_get(f"/gamification/xp/{user_id}")

if xp_data is None:
    xp_data = {
        "user_id": user_id,
        "total_xp": 1200,
        "level": 4,
        "xp_this_level": 200,
        "xp_to_next_level": 500,
        "level_name": "Problem Cozucu",
    }
    st.caption("\u26A0\uFE0F API ba\u011Flant\u0131s\u0131 kurulamad\u0131, \u00F6rnek veriler g\u00F6steriliyor.")

total_xp = xp_data.get("total_xp", 0)
level = xp_data.get("level", 1)
xp_this_level = xp_data.get("xp_this_level", 0)
xp_to_next = xp_data.get("xp_to_next_level", 100)
level_name_api = xp_data.get("level_name", "")
level_name = get_level_name_tr(level, level_name_api)

# XP istatistik kartlari
col1, col2, col3, col4 = st.columns(4)
with col1:
    stat_card(f"Sv. {level}", "Mevcut Seviye", "\U0001F396\uFE0F")
with col2:
    stat_card(f"{total_xp:,}", "Toplam XP", "\U0001F4AB")
with col3:
    stat_card(f"{xp_this_level:,}", "Bu Seviyede XP", "\U0001F4C8")
with col4:
    stat_card(f"{xp_to_next:,}", "Sonraki Seviyeye", "\U0001F3AF")

st.markdown("")

# Seviye adi
st.markdown(f"""
<div style="text-align:center; margin: 12px 0 16px 0;">
    <span class="level-badge">\U0001F31F {level_name}</span>
</div>
""", unsafe_allow_html=True)

# Ozel ilerleme cubugu
if xp_to_next > 0:
    pct = min(xp_this_level / xp_to_next * 100, 100)
else:
    pct = 100

st.markdown(f"""
<div style="margin: 0 0 8px 0;">
    <div class="xp-progress-outer">
        <div class="xp-progress-text">{xp_this_level:,} / {xp_to_next:,} XP</div>
        <div class="xp-progress-inner" style="width: {pct:.1f}%"></div>
    </div>
</div>
""", unsafe_allow_html=True)

progress_bar(pct / 100, f"Seviye {level} \u2192 Seviye {level + 1}")

st.markdown("---")


# ---------------------------------------------------------------------------
# 4. Seri Bolumu
# ---------------------------------------------------------------------------
section_header("\U0001F525 G\u00FCnl\u00FCk Seri")

streak_data = api_get(f"/gamification/streak/{user_id}")

if streak_data is None:
    streak_data = {
        "user_id": user_id,
        "current_streak": 5,
        "best_streak": 14,
        "last_activity": "2025-05-10T15:30:00",
        "streak_alive": True,
    }
    st.caption("\u26A0\uFE0F API ba\u011Flant\u0131s\u0131 kurulamad\u0131, \u00F6rnek veriler g\u00F6steriliyor.")

current_streak = streak_data.get("current_streak", 0)
best_streak = streak_data.get("best_streak", 0)
streak_alive = streak_data.get("streak_alive", False)

col_s1, col_s2, col_s3 = st.columns([1, 1, 1])

with col_s1:
    alive_cls = "" if streak_alive else " streak-dead"
    fire = "\U0001F525" if streak_alive else "\u2744\uFE0F"
    alive_text = "Seri aktif! Devam et!" if streak_alive else "Seri koptu! Bug\u00FCn \u00E7al\u0131\u015Farak yeniden ba\u015Flat!"
    st.markdown(f"""
    <div class="streak-card{alive_cls}">
        <div style="font-size:2.2em;">{fire}</div>
        <div class="streak-value">{current_streak}</div>
        <div class="streak-label">G\u00FCnl\u00FCk Seri</div>
        <div style="font-size:0.8em; margin-top:8px; opacity:0.85;">{alive_text}</div>
    </div>
    """, unsafe_allow_html=True)

with col_s2:
    stat_card(f"{best_streak}", "En Iyi Seri", "\U0001F3C5")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    status_icon = "\U0001F7E2" if streak_alive else "\U0001F534"
    status_text = "Aktif" if streak_alive else "Koptu"
    stat_card(f"{status_icon} {status_text}", "Seri Durumu", "")

with col_s3:
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    if st.button("\U0001F525 Seriyi G\u00FCncelle", use_container_width=True, type="primary"):
        result = api_post(f"/gamification/streak/{user_id}/update")
        if result and result.get("success"):
            new_streak = result.get("current_streak", current_streak)
            bonus_xp = result.get("streak_bonus_xp", 0)
            extended = result.get("streak_extended", False)
            if extended:
                st.success(f"\U0001F525 Seri uzat\u0131ld\u0131! Mevcut seri: {new_streak} g\u00FCn")
            else:
                st.info(f"Seri zaten g\u00FCncel. Mevcut seri: {new_streak} g\u00FCn")
            if bonus_xp > 0:
                st.success(f"\U0001F4AB Seri bonusu: +{bonus_xp} XP kazand\u0131n!")
            st.rerun()
        else:
            st.error("Seri g\u00FCncellenemedi. L\u00FCtfen tekrar deneyin.")

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="font-size:0.85em;">
        <strong>\U0001F4A1 Ipucu:</strong> Her g\u00FCn en az bir soru \u00E7\u00F6zerek serini devam ettir.
        Uzun seriler ekstra XP bonusu kazan\u0131r!
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ---------------------------------------------------------------------------
# 5. Rozetler Bolumu
# ---------------------------------------------------------------------------
section_header("\U0001F3C5 Rozetler")

badges_response = api_get(f"/gamification/badges/{user_id}")

if badges_response is not None:
    badges = badges_response.get("badges", FALLBACK_BADGES)
else:
    badges = FALLBACK_BADGES
    st.caption("\u26A0\uFE0F API ba\u011Flant\u0131s\u0131 kurulamad\u0131, \u00F6rnek rozetler g\u00F6steriliyor.")

earned_badges = [b for b in badges if b.get("earned", False)]
unearned_badges = [b for b in badges if not b.get("earned", False)]

col_b1, col_b2 = st.columns(2)
with col_b1:
    stat_card(f"{len(earned_badges)}", "Kazanilan Rozet", "\U0001F3C6")
with col_b2:
    stat_card(f"{len(badges)}", "Toplam Rozet", "\U0001F4CB")

st.markdown("")

# Kazanilmis rozetler
if earned_badges:
    st.markdown("##### \u2705 Kazand\u0131\u011F\u0131n Rozetler")
    cols_earned = st.columns(min(len(earned_badges), 4))
    for idx, badge in enumerate(earned_badges):
        with cols_earned[idx % min(len(earned_badges), 4)]:
            icon = badge.get("icon", "\U0001F3C5")
            name = badge.get("name", "Rozet")
            desc = badge.get("description", "")
            st.markdown(f"""
            <div class="badge-card earned">
                <div class="badge-icon">{icon}</div>
                <div class="badge-name">{name}</div>
                <div class="badge-desc">{desc}</div>
                <div class="badge-earned-tag">\u2705 Kazan\u0131ld\u0131</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("")

# Kazanilmamis rozetler
if unearned_badges:
    st.markdown("##### \U0001F512 Hen\u00FCz Kazan\u0131lmam\u0131\u015F Rozetler")
    num_cols = min(len(unearned_badges), 4)
    cols_unearned = st.columns(num_cols)
    for idx, badge in enumerate(unearned_badges):
        with cols_unearned[idx % num_cols]:
            icon = badge.get("icon", "\U0001F3C5")
            name = badge.get("name", "Rozet")
            desc = badge.get("description", "")
            prog = badge.get("progress", 0.0)
            prog_text = ""
            if prog and prog > 0:
                prog_pct = min(prog * 100, 100)
                prog_text = f'<div style="margin-top:6px;"><div class="custom-progress" style="height:6px;"><div class="custom-progress-fill" style="width:{prog_pct:.0f}%"></div></div><div style="font-size:0.7em;color:#999;margin-top:2px;">%{prog_pct:.0f}</div></div>'
            st.markdown(f"""
            <div class="badge-card unearned">
                <div class="badge-icon">{icon}</div>
                <div class="badge-name">{name}</div>
                <div class="badge-desc">{desc}</div>
                {prog_text}
                <div class="badge-locked-tag">\U0001F512 Kilitli</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("")

# Yeni rozet kontrol butonu
col_badge_btn, _ = st.columns([1, 2])
with col_badge_btn:
    if st.button("\U0001F50D Yeni Rozetleri Kontrol Et", use_container_width=True, type="primary"):
        check_result = api_post(f"/gamification/badges/check/{user_id}")
        if check_result:
            new_count = check_result.get("badges_earned", 0)
            new_badges_list = check_result.get("new_badges", [])
            if new_count > 0:
                st.balloons()
                st.success(f"\U0001F389 Tebrikler! {new_count} yeni rozet kazand\u0131n!")
                for nb in new_badges_list:
                    nb_name = nb.get("name", "Rozet")
                    nb_icon = nb.get("icon", "\U0001F3C5")
                    st.markdown(f"""
                    <div class="success-box" style="text-align:center; margin:8px 0;">
                        <span style="font-size:1.5em;">{nb_icon}</span>
                        <strong> {nb_name}</strong> kazanildi!
                    </div>
                    """, unsafe_allow_html=True)
                st.rerun()
            else:
                st.info("Hen\u00FCz yeni rozet yok. \u00C7al\u0131\u015Fmaya devam et!")
        else:
            st.error("Rozet kontrol\u00FC ba\u015Far\u0131s\u0131z oldu. L\u00FCtfen tekrar deneyin.")

st.markdown("---")


# ---------------------------------------------------------------------------
# 6. Liderlik Tablosu
# ---------------------------------------------------------------------------
section_header("\U0001F4CA Liderlik Tablosu")

leaderboard_data = api_get("/gamification/leaderboard", params={"limit": 10, "offset": 0})

if leaderboard_data is not None:
    lb_entries = leaderboard_data.get("entries", FALLBACK_LEADERBOARD)
    total_users = leaderboard_data.get("total_users", len(lb_entries))
else:
    lb_entries = FALLBACK_LEADERBOARD
    total_users = len(lb_entries)
    st.caption("\u26A0\uFE0F API ba\u011Flant\u0131s\u0131 kurulamad\u0131, \u00F6rnek liderlik tablosu g\u00F6steriliyor.")

# Kullanicinin kendi sirasi
user_rank_data = api_get(f"/gamification/leaderboard/{user_id}/rank")
if user_rank_data is None:
    user_rank_data = {"user_id": user_id, "rank": 7, "total_xp": 1200, "percentile": 72}

col_lb_main, col_lb_side = st.columns([2, 1])

with col_lb_side:
    my_rank = user_rank_data.get("rank", 0)
    my_xp = user_rank_data.get("total_xp", 0)
    my_pct = user_rank_data.get("percentile", 0)

    st.markdown(f"""
    <div class="my-rank-box">
        <div style="font-size:0.9em; opacity:0.85;">Senin S\u0131ran</div>
        <div class="my-rank-value">#{my_rank}</div>
        <div class="my-rank-label">{my_xp:,} XP</div>
        <div style="margin-top:12px; font-size:0.85em; opacity:0.8;">
            \U0001F4C8 Oyuncularin %{my_pct}'inden iyi
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    stat_card(f"{total_users}", "Toplam Oyuncu", "\U0001F465")

with col_lb_main:
    rank_medals = {1: "\U0001F947", 2: "\U0001F948", 3: "\U0001F949"}
    rank_classes = {1: "gold", 2: "silver", 3: "bronze"}
    rank_r_classes = {1: "r1", 2: "r2", 3: "r3"}

    for entry in lb_entries:
        rank = entry.get("rank", 0)
        display_name = entry.get("display_name", entry.get("user_id", "?"))
        entry_xp = entry.get("total_xp", 0)
        entry_level = entry.get("level", 1)

        medal = rank_medals.get(rank, "")
        row_cls = rank_classes.get(rank, "")
        r_cls = rank_r_classes.get(rank, "rn")

        rank_display = f"{medal} {rank}" if medal else str(rank)
        entry_level_name = get_level_name_tr(entry_level)

        is_me = (entry.get("user_id", "") == user_id)
        highlight = "border: 2px solid #667eea; background: linear-gradient(135deg, #f0f0ff 0%, #e8e5ff 100%);" if is_me else ""
        me_tag = " \u2B50" if is_me else ""

        st.markdown(f"""
        <div class="lb-row {row_cls}" style="{highlight}">
            <div class="lb-rank {r_cls}">{rank_display}</div>
            <div class="lb-user">{display_name}{me_tag}</div>
            <div class="lb-xp">{entry_xp:,} XP</div>
            <div class="lb-level">Sv.{entry_level} - {entry_level_name}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")


# ---------------------------------------------------------------------------
# 7. XP Odul Bolumu
# ---------------------------------------------------------------------------
section_header("\U0001F381 XP \u00D6d\u00FCl Ver")

st.markdown("""
<div class="info-box">
    <strong>\U0001F4A1 Bilgi:</strong> Bu alan, \u00F6\u011Fretmen veya y\u00F6neticilerin \u00F6\u011Frencilere
    manuel olarak XP \u00F6d\u00FCl\u00FC vermesi i\u00E7in tasarlanm\u0131\u015Ft\u0131r.
    \u00D6zel ba\u015Far\u0131lar, s\u0131n\u0131f i\u00E7i katk\u0131lar veya ekstra \u00E7aba i\u00E7in kullan\u0131labilir.
</div>
""", unsafe_allow_html=True)

st.markdown("")

with st.form("xp_award_form", clear_on_submit=True):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        award_user_id = st.text_input(
            "\U0001F464 Kullan\u0131c\u0131 ID",
            value=user_id,
            key="award_uid",
            help="\u00D6d\u00FCl verilecek kullan\u0131c\u0131n\u0131n kimli\u011Fi",
        )
    with col_f2:
        xp_amount = st.number_input(
            "\U0001F4AB XP Miktar\u0131",
            min_value=1,
            max_value=1000,
            value=50,
            step=10,
            help="Verilecek XP miktar\u0131 (1-1000)",
        )
    reason = st.text_input(
        "\U0001F4DD Sebep",
        placeholder="\u00D6r: S\u0131n\u0131fta m\u00FCkemmel performans, ekstra \u00F6dev tamamlama...",
        help="XP \u00F6d\u00FCl\u00FCn\u00FCn sebebini yaz\u0131n",
    )

    submitted = st.form_submit_button(
        "\U0001F381 XP \u00D6d\u00FCl\u00FC Ver",
        use_container_width=True,
        type="primary",
    )

    if submitted:
        if not award_user_id.strip():
            st.error("Kullan\u0131c\u0131 ID bo\u015F b\u0131rak\u0131lamaz.")
        elif not reason.strip():
            st.error("L\u00FCtfen bir sebep yaz\u0131n.")
        else:
            award_result = api_post("/gamification/xp/award", data={
                "user_id": award_user_id.strip(),
                "xp_amount": int(xp_amount),
                "reason": reason.strip(),
            })
            if award_result and award_result.get("success"):
                new_total = award_result.get("new_total", 0)
                level_up = award_result.get("level_up", False)
                new_level = award_result.get("new_level", 0)
                st.markdown(f"""
                <div class="xp-award-result">
                    <h4>\u2705 XP Ba\u015Far\u0131yla Verildi!</h4>
                    <p><strong>{award_user_id}</strong> kullan\u0131c\u0131s\u0131na
                    <strong>+{xp_amount} XP</strong> \u00F6d\u00FCl\u00FC verildi.</p>
                    <p>Yeni toplam: <strong>{new_total:,} XP</strong></p>
                </div>
                """, unsafe_allow_html=True)
                if level_up:
                    st.balloons()
                    lvl_name = get_level_name_tr(new_level)
                    st.success(
                        f"\U0001F389 Seviye atland\u0131! {award_user_id} art\u0131k "
                        f"Seviye {new_level} - {lvl_name}!"
                    )
            else:
                st.error(
                    "XP \u00F6d\u00FCl\u00FC verilemedi. API ba\u011Flant\u0131s\u0131n\u0131 kontrol edin "
                    "ve tekrar deneyin."
                )


# ---------------------------------------------------------------------------
# Alt bilgi
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:16px 0; color:#999; font-size:0.8em;">
    \U0001F3AE Oyunla\u015Ft\u0131rma Merkezi &bull; MathAI Adaptif Matematik Platformu &bull;
    Her do\u011Fru ad\u0131m seni zirveye ta\u015F\u0131r!
</div>
""", unsafe_allow_html=True)
