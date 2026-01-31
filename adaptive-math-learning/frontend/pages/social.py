"""
Sosyal ve Yarisma Sayfasi - Social & Competition Page.

Esports/gaming tarzinda rekabetci matematik platformu.
Duello, turnuva, haftalik yarisma ve arkadaslik ozellikleri.
"""

import streamlit as st
from datetime import datetime, timedelta

from theme import apply_theme, render_sidebar, api_get, api_post, stat_card, section_header

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Sosyal - MathAI",
    page_icon="\U0001F465",
    layout="wide",
)

apply_theme()
render_sidebar("social")

# ---------------------------------------------------------------------------
# Extra CSS  esports / gaming competition theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ---- Arena hero banner ---- */
.arena-hero {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    border-radius: 20px;
    padding: 40px 36px;
    color: #fff;
    text-align: center;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 48px rgba(48, 43, 99, 0.55);
}
.arena-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 20% 80%, rgba(255,0,128,0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(0,200,255,0.12) 0%, transparent 50%);
    pointer-events: none;
}
.arena-hero h1 {
    font-size: 2.6em;
    font-weight: 800;
    margin: 0 0 8px 0;
    background: linear-gradient(90deg, #00f2fe, #4facfe, #ff6fd8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.arena-hero p {
    color: rgba(255,255,255,0.82);
    font-size: 1.12em;
    margin: 0;
    max-width: 620px;
    display: inline-block;
}

/* ---- Neon stat cards ---- */
.neon-card {
    background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid rgba(79, 172, 254, 0.25);
    border-radius: 14px;
    padding: 22px 18px;
    text-align: center;
    box-shadow: 0 0 20px rgba(79, 172, 254, 0.08);
    transition: transform 0.25s, box-shadow 0.25s;
}
.neon-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 30px rgba(79, 172, 254, 0.2);
}
.neon-card .neon-val {
    font-size: 2.2em;
    font-weight: 800;
    background: linear-gradient(90deg, #00f2fe, #4facfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.neon-card .neon-lbl {
    font-size: 0.82em;
    color: rgba(255,255,255,0.55);
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ---- VS divider ---- */
.vs-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px; height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6fd8, #4facfe);
    color: #fff;
    font-weight: 900;
    font-size: 1.15em;
    box-shadow: 0 0 18px rgba(255,111,216,0.45);
    margin: 0 auto;
}

/* ---- Score bar ---- */
.score-bar-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 6px 0;
}
.score-bar-wrap .sb-name {
    font-weight: 600;
    color: #e0e0e0;
    min-width: 90px;
    text-align: right;
}
.score-bar-track {
    flex: 1;
    height: 14px;
    background: rgba(255,255,255,0.08);
    border-radius: 7px;
    overflow: hidden;
}
.score-bar-fill-blue {
    height: 100%;
    border-radius: 7px;
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    transition: width 0.6s ease;
}
.score-bar-fill-pink {
    height: 100%;
    border-radius: 7px;
    background: linear-gradient(90deg, #ff6fd8, #ff9a9e);
    transition: width 0.6s ease;
}
.score-bar-wrap .sb-score {
    font-weight: 700;
    color: #4facfe;
    min-width: 36px;
}

/* ---- Leaderboard rows ---- */
.lb-row {
    display: flex;
    align-items: center;
    padding: 14px 18px;
    border-radius: 10px;
    margin-bottom: 8px;
    transition: transform 0.2s, background 0.2s;
}
.lb-row:hover {
    transform: translateX(4px);
}
.lb-row-gold   { background: linear-gradient(90deg, rgba(255,215,0,0.12), transparent); border-left: 4px solid #FFD700; }
.lb-row-silver { background: linear-gradient(90deg, rgba(192,192,192,0.10), transparent); border-left: 4px solid #C0C0C0; }
.lb-row-bronze { background: linear-gradient(90deg, rgba(205,127,50,0.10), transparent); border-left: 4px solid #CD7F32; }
.lb-row-normal { background: rgba(255,255,255,0.04); border-left: 4px solid rgba(79,172,254,0.3); }

.lb-rank {
    font-size: 1.35em;
    font-weight: 800;
    width: 44px;
    text-align: center;
}
.lb-rank-1 { color: #FFD700; }
.lb-rank-2 { color: #C0C0C0; }
.lb-rank-3 { color: #CD7F32; }
.lb-rank-n { color: rgba(255,255,255,0.5); }
.lb-name {
    flex: 1;
    font-weight: 600;
    color: #e0e0e0;
    padding-left: 12px;
}
.lb-score {
    font-weight: 700;
    font-size: 1.1em;
    color: #4facfe;
    padding-right: 8px;
}
.lb-xp {
    font-size: 0.82em;
    color: rgba(255,255,255,0.45);
    min-width: 64px;
    text-align: right;
}

/* ---- Game panel card ---- */
.game-panel {
    background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid rgba(79,172,254,0.15);
    border-radius: 16px;
    padding: 28px 24px;
    margin-bottom: 20px;
}
.game-panel h3 {
    color: #fff !important;
    margin: 0 0 4px 0;
}
.game-panel .gp-sub {
    color: rgba(255,255,255,0.5);
    font-size: 0.88em;
    margin-bottom: 18px;
}

/* ---- Friend card ---- */
.friend-card {
    display: flex;
    align-items: center;
    gap: 14px;
    background: linear-gradient(145deg, #1a1a2e, #16213e);
    border: 1px solid rgba(79,172,254,0.15);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.friend-card:hover {
    border-color: rgba(79,172,254,0.45);
}
.friend-avatar {
    width: 44px; height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.15em;
    color: #fff;
    flex-shrink: 0;
}
.friend-info {
    flex: 1;
}
.friend-name {
    font-weight: 600;
    color: #e0e0e0;
}
.friend-status {
    font-size: 0.8em;
    color: rgba(255,255,255,0.4);
}

/* ---- Live pulse ---- */
@keyframes live-pulse {
    0%   { box-shadow: 0 0 0 0 rgba(0,242,254,0.5); }
    70%  { box-shadow: 0 0 0 12px rgba(0,242,254,0); }
    100% { box-shadow: 0 0 0 0 rgba(0,242,254,0); }
}
.live-dot {
    display: inline-block;
    width: 10px; height: 10px;
    background: #00f2fe;
    border-radius: 50%;
    animation: live-pulse 2s infinite;
    vertical-align: middle;
    margin-right: 6px;
}

/* ---- Timer pill ---- */
.timer-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(79,172,254,0.2);
    border-radius: 24px;
    padding: 8px 20px;
    color: #4facfe;
    font-weight: 600;
    font-size: 0.95em;
}

/* ---- Competition theme card ---- */
.comp-theme {
    background: linear-gradient(135deg, #302b63, #24243e);
    border-radius: 14px;
    padding: 24px;
    border-left: 5px solid #4facfe;
    margin-bottom: 16px;
}
.comp-theme h4 {
    color: #fff !important;
    margin: 0 0 6px 0;
}
.comp-theme p {
    color: rgba(255,255,255,0.65);
    margin: 0;
}

/* Tab overrides for dark gaming look */
div[data-baseweb="tab-list"] {
    gap: 8px;
}
button[data-baseweb="tab"] {
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "social_user_id": "",
    "active_duel_id": "",
    "active_tournament_id": "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ---------------------------------------------------------------------------
# Topics list (Turkish)
# ---------------------------------------------------------------------------
KONU_LISTESI = [
    "Aritmetik",
    "Kesirler",
    "Yuzdelik",
    "Cebir",
    "Geometri",
    "Oran-Oranti",
    "Uslu Sayilar",
    "Istatistik",
    "Sayi Teorisi",
    "Denklem Sistemleri",
    "Esitsizlikler",
    "Fonksiyonlar",
    "Trigonometri",
    "Polinomlar",
    "Kumeler ve Mantik",
    "Koordinat Geometrisi",
]


# ---------------------------------------------------------------------------
# Helper renderers
# ---------------------------------------------------------------------------
def _neon_stat(value, label, icon=""):
    """Render a dark-themed neon stat card."""
    st.markdown(f"""
    <div class="neon-card">
        <div style="font-size:1.4em; margin-bottom:4px;">{icon}</div>
        <div class="neon-val">{value}</div>
        <div class="neon-lbl">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def _leaderboard_row(rank, name, score, xp=""):
    """Render a single leaderboard row."""
    if rank == 1:
        row_cls, rank_cls, medal = "lb-row-gold", "lb-rank-1", "\U0001F947"
    elif rank == 2:
        row_cls, rank_cls, medal = "lb-row-silver", "lb-rank-2", "\U0001F948"
    elif rank == 3:
        row_cls, rank_cls, medal = "lb-row-bronze", "lb-rank-3", "\U0001F949"
    else:
        row_cls, rank_cls, medal = "lb-row-normal", "lb-rank-n", ""

    xp_html = f'<span class="lb-xp">+{xp} XP</span>' if xp else ""
    st.markdown(f"""
    <div class="lb-row {row_cls}">
        <span class="lb-rank {rank_cls}">{medal if medal else rank}</span>
        <span class="lb-name">{name}</span>
        <span class="lb-score">{score} puan</span>
        {xp_html}
    </div>
    """, unsafe_allow_html=True)


def _render_duel_scores(status_data):
    """Render a live VS score comparison for a duel."""
    challenger = status_data.get("challenger", {})
    opponent = status_data.get("opponent", {})
    q_count = status_data.get("question_count", 10)
    ch_score = challenger.get("score", 0)
    op_score = opponent.get("score", 0)
    max_score = max(ch_score, op_score, 1)

    ch_pct = min(int(ch_score / max_score * 100), 100) if max_score else 0
    op_pct = min(int(op_score / max_score * 100), 100) if max_score else 0

    st.markdown(f"""
    <div style="text-align:center; margin: 16px 0 20px 0;">
        <div class="vs-badge">VS</div>
    </div>
    <div class="score-bar-wrap">
        <span class="sb-name">{challenger.get('user_id', 'Oyuncu 1')}</span>
        <div class="score-bar-track">
            <div class="score-bar-fill-blue" style="width:{ch_pct}%"></div>
        </div>
        <span class="sb-score">{ch_score}</span>
    </div>
    <div class="score-bar-wrap">
        <span class="sb-name">{opponent.get('user_id', 'Oyuncu 2')}</span>
        <div class="score-bar-track">
            <div class="score-bar-fill-pink" style="width:{op_pct}%"></div>
        </div>
        <span class="sb-score">{op_score}</span>
    </div>
    <p style="text-align:center; color:rgba(255,255,255,0.4); font-size:0.85em; margin-top:10px;">
        Toplam {q_count} soru &middot;
        <span class="live-dot"></span> Canli
    </p>
    """, unsafe_allow_html=True)


# =========================================================================
# HERO
# =========================================================================
st.markdown("""
<div class="arena-hero">
    <h1>\u2694\uFE0F Yarisma Arenasi</h1>
    <p>
        Arkadaslarinla matematik duellosu yap, turnuvalara katil ve haftalik
        yarismalarla liderlik tablosunda zirveye oyna. Goster bakalim en iyi
        matematikci kimm\u0131\u015F!
    </p>
</div>
""", unsafe_allow_html=True)

# Quick-stats row
c1, c2, c3, c4 = st.columns(4)
with c1:
    _neon_stat("0", "Duello Galibiyet", "\u2694\uFE0F")
with c2:
    _neon_stat("0", "Turnuva Katilim", "\U0001F3C6")
with c3:
    _neon_stat("0", "Haftalik Siralama", "\U0001F4C5")
with c4:
    _neon_stat("0", "Toplam XP", "\u26A1")

st.markdown("")

# =========================================================================
# TABS
# =========================================================================
tab_duel, tab_tournament, tab_weekly = st.tabs([
    "\u2694\uFE0F Duello",
    "\U0001F3C6 Turnuva",
    "\U0001F4C5 Haftalik Yarisma",
])

# -------------------------------------------------------------------------
# TAB 1  DUELLO
# -------------------------------------------------------------------------
with tab_duel:

    col_create, col_join = st.columns(2)

    # -- Create Duel --
    with col_create:
        st.markdown("""
        <div class="game-panel">
            <h3>\u2694\uFE0F Yeni Duello Olustur</h3>
            <p class="gp-sub">Bir rakip sec ve matematik arenasina gir!</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("create_duel_form", clear_on_submit=False):
            duel_challenger = st.text_input(
                "Senin Kullanici ID'n",
                placeholder="ornek: ogrenci_42",
                key="duel_ch_id",
            )
            duel_opponent = st.text_input(
                "Rakip Kullanici ID'si",
                placeholder="ornek: ogrenci_99",
                key="duel_op_id",
            )
            duel_topic = st.selectbox("Konu", KONU_LISTESI, key="duel_topic")
            duel_q_count = st.slider(
                "Soru Sayisi",
                min_value=5,
                max_value=20,
                value=10,
                step=1,
                key="duel_q_count",
            )

            submit_duel = st.form_submit_button(
                "\u2694\uFE0F Duello Baslat",
                type="primary",
                use_container_width=True,
            )

        if submit_duel:
            if not duel_challenger or not duel_opponent:
                st.error("Lutfen hem kendi ID'nizi hem de rakip ID'sini girin.")
            elif duel_challenger == duel_opponent:
                st.error("Kendinizle duello yapamazsiniz!")
            else:
                payload = {
                    "challenger_id": duel_challenger,
                    "opponent_id": duel_opponent,
                    "topic": duel_topic,
                    "question_count": duel_q_count,
                }
                result = api_post("/social/duel/create", payload)
                if result:
                    duel_id = result.get("duel_id", "")
                    st.session_state.active_duel_id = duel_id
                    st.success(f"Duello olusturuldu! ID: {duel_id}")
                    st.info(f"Rakibinize bu ID'yi gonderin: **{duel_id}**")
                else:
                    st.warning(
                        "Duello olusturulamadi. Sunucu baglantisini kontrol edin."
                    )

    # -- Join Duel --
    with col_join:
        st.markdown("""
        <div class="game-panel">
            <h3>\U0001F3AE Duelloya Katil</h3>
            <p class="gp-sub">Sana gonderilen duello davetini kabul et.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("join_duel_form", clear_on_submit=False):
            join_duel_id = st.text_input(
                "Duello ID",
                placeholder="ornek: duel_a1b2c3d4e5f6",
                key="join_duel_id_input",
            )
            join_user_id = st.text_input(
                "Senin Kullanici ID'n",
                placeholder="ornek: ogrenci_99",
                key="join_user_id_input",
            )
            join_submit = st.form_submit_button(
                "\U0001F3AE Katil",
                type="primary",
                use_container_width=True,
            )

        if join_submit:
            if not join_duel_id or not join_user_id:
                st.error("Lutfen Duello ID ve Kullanici ID girin.")
            else:
                result = api_post(
                    f"/social/duel/join/{join_duel_id}",
                    {"user_id": join_user_id},
                )
                if result:
                    st.session_state.active_duel_id = join_duel_id
                    st.success("Duelloya basariyla katildiniz! Oyun basliyor...")
                else:
                    st.warning(
                        "Duelloya katilamadim. ID'yi kontrol edin veya suresi dolmus olabilir."
                    )

    st.markdown("---")

    # -- Active duel status --
    section_header("Aktif Duello Durumu")

    active_id_input = st.text_input(
        "Duello ID girin veya mevcut aktif ID'yi kullanin",
        value=getattr(st.session_state, "active_duel_id", ""),
        key="active_duel_status_id",
    )

    col_status_btn, col_ans_btn = st.columns(2)

    with col_status_btn:
        check_status = st.button(
            "\U0001F50D Durumu Kontrol Et",
            use_container_width=True,
        )

    if check_status and active_id_input:
        status_data = api_get(f"/social/duel/status/{active_id_input}")
        if status_data:
            st.session_state.active_duel_id = active_id_input

            duel_status_val = status_data.get("status", "unknown")
            status_colors = {
                "pending": ("\u23F3", "Bekliyor"),
                "in_progress": ("\U0001F534", "Devam Ediyor"),
                "completed": ("\u2705", "Tamamlandi"),
                "cancelled": ("\u274C", "Iptal Edildi"),
                "expired": ("\u23F0", "Suresi Doldu"),
            }
            icon, label = status_colors.get(duel_status_val, ("\u2753", duel_status_val))

            st.markdown(f"""
            <div style="text-align:center; margin:12px 0;">
                <span class="live-dot"></span>
                <span style="color:#e0e0e0; font-weight:600;">
                    Durum: {icon} {label}
                </span>
                &nbsp;&middot;&nbsp;
                <span style="color:rgba(255,255,255,0.5);">
                    Konu: {status_data.get('topic', '-')}
                </span>
            </div>
            """, unsafe_allow_html=True)

            _render_duel_scores(status_data)

            if duel_status_val == "completed":
                winner = status_data.get("winner_id")
                if winner:
                    st.success(f"Kazanan: {winner}")
                else:
                    st.info("Sonuc: Berabere!")
        elif active_id_input:
            st.warning("Duello bulunamadi veya sunucuya ulasilamadi.")

    # -- Answer submission --
    st.markdown("")
    with st.expander("Cevap Gonder (Aktif Duello)", expanded=False):
        with st.form("duel_answer_form", clear_on_submit=True):
            ans_user = st.text_input(
                "Kullanici ID",
                key="duel_ans_user",
            )
            ans_q_id = st.text_input(
                "Soru ID",
                key="duel_ans_q",
            )
            ans_value = st.text_input(
                "Cevabin",
                key="duel_ans_val",
            )
            ans_time = st.number_input(
                "Cevaplama Suresi (saniye)",
                min_value=0.0,
                max_value=600.0,
                value=0.0,
                step=1.0,
                key="duel_ans_time",
            )
            ans_submit = st.form_submit_button(
                "Gonder",
                type="primary",
                use_container_width=True,
            )

        if ans_submit:
            d_id = getattr(st.session_state, "active_duel_id", "") or active_id_input
            if not d_id:
                st.error("Oncelikle bir Duello ID belirleyin.")
            elif not ans_user or not ans_q_id or not ans_value:
                st.error("Tum alanlari doldurun.")
            else:
                payload = {
                    "user_id": ans_user,
                    "question_id": ans_q_id,
                    "answer": ans_value,
                    "time_taken_seconds": ans_time,
                }
                result = api_post(f"/social/duel/answer/{d_id}", payload)
                if result:
                    is_correct = result.get("is_correct", False)
                    xp = result.get("xp_earned", 0)
                    if is_correct:
                        st.success(f"Dogru cevap! +{xp} XP kazandin.")
                    else:
                        st.error("Yanlis cevap. Tekrar dene!")
                else:
                    st.warning("Cevap gonderilemedi. Baglanti veya duello durumunu kontrol edin.")


# -------------------------------------------------------------------------
# TAB 2  TURNUVA
# -------------------------------------------------------------------------
with tab_tournament:

    col_t_create, col_t_join = st.columns(2)

    # -- Create Tournament --
    with col_t_create:
        st.markdown("""
        <div class="game-panel">
            <h3>\U0001F3C6 Turnuva Olustur</h3>
            <p class="gp-sub">Sinifin veya okulun icin bir turnuva kur!</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("create_tournament_form", clear_on_submit=False):
            trn_creator = st.text_input(
                "Olusturan Kullanici ID",
                placeholder="ornek: ogretmen_01",
                key="trn_creator",
            )
            trn_name = st.text_input(
                "Turnuva Adi",
                placeholder="ornek: 5. Sinif Kesirler Sampiyonasi",
                key="trn_name",
            )
            trn_topic = st.selectbox("Konu", KONU_LISTESI, key="trn_topic")
            trn_max = st.slider(
                "Maksimum Katilimci",
                min_value=2,
                max_value=100,
                value=30,
                step=1,
                key="trn_max",
            )
            trn_submit = st.form_submit_button(
                "\U0001F3C6 Turnuva Olustur",
                type="primary",
                use_container_width=True,
            )

        if trn_submit:
            if not trn_creator or not trn_name:
                st.error("Lutfen tum alanlari doldurun.")
            else:
                payload = {
                    "creator_id": trn_creator,
                    "name": trn_name,
                    "topic": trn_topic,
                    "max_participants": trn_max,
                }
                result = api_post("/social/tournament/create", payload)
                if result:
                    tid = result.get("tournament_id", "")
                    st.session_state.active_tournament_id = tid
                    st.success(f"Turnuva olusturuldu! ID: {tid}")
                else:
                    st.warning("Turnuva olusturulamadi. Sunucu baglantisini kontrol edin.")

    # -- Join Tournament --
    with col_t_join:
        st.markdown("""
        <div class="game-panel">
            <h3>\U0001F3AB Turnuvaya Katil</h3>
            <p class="gp-sub">Mevcut bir turnuvaya kayit ol ve yaris!</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("join_tournament_form", clear_on_submit=False):
            join_trn_id = st.text_input(
                "Turnuva ID",
                placeholder="ornek: trn_a1b2c3d4e5f6",
                key="join_trn_id",
            )
            join_trn_user = st.text_input(
                "Kullanici ID",
                placeholder="ornek: ogrenci_42",
                key="join_trn_user",
            )
            join_trn_submit = st.form_submit_button(
                "\U0001F3AB Kayit Ol",
                type="primary",
                use_container_width=True,
            )

        if join_trn_submit:
            if not join_trn_id or not join_trn_user:
                st.error("Lutfen Turnuva ID ve Kullanici ID girin.")
            else:
                result = api_post(
                    f"/social/tournament/join/{join_trn_id}",
                    {"user_id": join_trn_user},
                )
                if result:
                    st.session_state.active_tournament_id = join_trn_id
                    st.success("Turnuvaya basariyla kayit oldunuz!")
                else:
                    st.warning(
                        "Turnuvaya katilamadim. ID'yi kontrol edin "
                        "veya kapasite dolmus olabilir."
                    )

    st.markdown("---")

    # -- Tournament leaderboard --
    section_header("Turnuva Liderlik Tablosu")

    lb_trn_id = st.text_input(
        "Liderlik tablosu icin Turnuva ID girin",
        value=getattr(st.session_state, "active_tournament_id", ""),
        key="lb_trn_id",
    )

    if st.button("\U0001F4CA Liderlik Tablosunu Getir", key="fetch_trn_lb"):
        if not lb_trn_id:
            st.error("Lutfen bir Turnuva ID girin.")
        else:
            lb_data = api_get(f"/social/tournament/leaderboard/{lb_trn_id}")
            if lb_data:
                entries = lb_data if isinstance(lb_data, list) else lb_data.get("leaderboard", lb_data.get("entries", []))
                if entries:
                    for entry in entries:
                        _leaderboard_row(
                            rank=entry.get("rank", 0),
                            name=entry.get("user_id", "?"),
                            score=entry.get("score", 0),
                            xp=entry.get("xp_earned", ""),
                        )
                else:
                    st.info("Henuz skor tablosunda kimse yok. Yarisma baslamayi bekliyor.")
            else:
                st.warning("Liderlik tablosu yuklenemedi. Turnuva ID'yi kontrol edin.")


# -------------------------------------------------------------------------
# TAB 3  HAFTALIK YARISMA
# -------------------------------------------------------------------------
with tab_weekly:

    st.markdown("""
    <div class="game-panel">
        <h3>\U0001F4C5 Bu Haftanin Yarismasi</h3>
        <p class="gp-sub">Her hafta yeni bir konu, yeni bir macera!</p>
    </div>
    """, unsafe_allow_html=True)

    weekly_data = api_get("/social/weekly")

    if weekly_data:
        w_title = weekly_data.get("title", "Haftalik Yarisma")
        w_desc = weekly_data.get("description", "")
        w_topic = weekly_data.get("topic", "-")
        w_participants = weekly_data.get("total_participants", 0)
        w_start = weekly_data.get("week_start", "")
        w_end = weekly_data.get("week_end", "")

        # Compute remaining time
        remaining_str = ""
        if w_end:
            try:
                end_dt = datetime.fromisoformat(w_end.replace("Z", "+00:00")) if isinstance(w_end, str) else w_end
                now = datetime.utcnow()
                if hasattr(end_dt, "tzinfo") and end_dt.tzinfo is not None:
                    from datetime import timezone
                    now = datetime.now(timezone.utc)
                delta = end_dt - now
                if delta.total_seconds() > 0:
                    days = delta.days
                    hours = delta.seconds // 3600
                    mins = (delta.seconds % 3600) // 60
                    remaining_str = f"{days} gun {hours} saat {mins} dakika"
                else:
                    remaining_str = "Sure doldu"
            except Exception:
                remaining_str = "Hesaplanamadi"

        # Theme card
        st.markdown(f"""
        <div class="comp-theme">
            <h4>\U0001F3AF {w_title}</h4>
            <p>{w_desc}</p>
        </div>
        """, unsafe_allow_html=True)

        # Info cards
        wc1, wc2, wc3 = st.columns(3)
        with wc1:
            _neon_stat(w_topic.replace("_", " ").title(), "Konu", "\U0001F4D6")
        with wc2:
            _neon_stat(str(w_participants), "Katilimci", "\U0001F465")
        with wc3:
            _neon_stat(
                remaining_str if remaining_str else "-",
                "Kalan Sure",
                "\u23F1\uFE0F",
            )

        st.markdown("")

        # Weekly leaderboard
        section_header("Haftalik Liderlik Tablosu")

        w_leaderboard = weekly_data.get("leaderboard", [])
        if w_leaderboard:
            for entry in w_leaderboard:
                _leaderboard_row(
                    rank=entry.get("rank", 0),
                    name=entry.get("user_id", "?"),
                    score=entry.get("score", 0),
                    xp=entry.get("projected_xp", ""),
                )
        else:
            st.info("Henuz kimse skor gondermedi. Ilk sen ol!")

    else:
        # Offline / demo mode
        st.markdown(f"""
        <div class="comp-theme">
            <h4>\U0001F3AF Haftalik Yarisma</h4>
            <p>Sunucuya baglanilamiyor. Arka ucu calistirdiginizda
            bu haftanin yarismasi burada gorunecek.</p>
        </div>
        """, unsafe_allow_html=True)

        wc1, wc2, wc3 = st.columns(3)
        with wc1:
            _neon_stat("-", "Konu", "\U0001F4D6")
        with wc2:
            _neon_stat("0", "Katilimci", "\U0001F465")
        with wc3:
            _neon_stat("-", "Kalan Sure", "\u23F1\uFE0F")

        st.markdown("")
        section_header("Haftalik Liderlik Tablosu")
        st.info("Sunucu baglantisi kurulamadiginda liderlik tablosu gosterilemiyor.")


# =========================================================================
# ARKADASLAR (Friends) SECTION  below tabs
# =========================================================================
st.markdown("")
st.markdown("")
section_header("Arkadaslar")

fr_col1, fr_col2 = st.columns(2)

# -- Send friend request --
with fr_col1:
    st.markdown("""
    <div class="game-panel">
        <h3>\U0001F91D Arkadaslik Istegi Gonder</h3>
        <p class="gp-sub">Arkadaslarini ekle, birlikte yaris!</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("friend_request_form", clear_on_submit=True):
        fr_from = st.text_input(
            "Senin Kullanici ID'n",
            placeholder="ornek: ogrenci_42",
            key="fr_from",
        )
        fr_to = st.text_input(
            "Eklemek Istedigin Kullanici ID",
            placeholder="ornek: ogrenci_99",
            key="fr_to",
        )
        fr_submit = st.form_submit_button(
            "\U0001F91D Istek Gonder",
            type="primary",
            use_container_width=True,
        )

    if fr_submit:
        if not fr_from or not fr_to:
            st.error("Lutfen her iki ID'yi de girin.")
        elif fr_from == fr_to:
            st.error("Kendinize arkadaslik istegi gonderemezsiniz!")
        else:
            result = api_post(
                "/social/friends/request",
                {"from_user_id": fr_from, "to_user_id": fr_to},
            )
            if result:
                st.success(
                    f"Arkadaslik istegi gonderildi! "
                    f"Istek ID: {result.get('request_id', '-')}"
                )
            else:
                st.warning(
                    "Istek gonderilemedi. Zaten bekleyen bir isteg olabilir "
                    "veya sunucuya ulasilamiyor."
                )

# -- Friends list --
with fr_col2:
    st.markdown("""
    <div class="game-panel">
        <h3>\U0001F465 Arkadas Listem</h3>
        <p class="gp-sub">Arkadaslarini gor ve duelloya davet et.</p>
    </div>
    """, unsafe_allow_html=True)

    fr_user_id = st.text_input(
        "Kullanici ID",
        placeholder="ornek: ogrenci_42",
        key="fr_list_user",
    )

    if st.button("\U0001F50D Arkadas Listesini Getir", key="fetch_friends"):
        if not fr_user_id:
            st.error("Lutfen Kullanici ID'nizi girin.")
        else:
            friends_data = api_get(f"/social/friends/{fr_user_id}")
            if friends_data:
                friends_list = friends_data if isinstance(friends_data, list) else friends_data.get("friends", [])
                if friends_list:
                    for friend in friends_list:
                        f_id = friend if isinstance(friend, str) else friend.get("user_id", "?")
                        initials = f_id[:2].upper() if f_id else "??"
                        st.markdown(f"""
                        <div class="friend-card">
                            <div class="friend-avatar">{initials}</div>
                            <div class="friend-info">
                                <div class="friend-name">{f_id}</div>
                                <div class="friend-status">\U0001F7E2 Cevrimici</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Henuz arkadasiniz yok. Yukaridaki formla arkadaslik istegi gonderin!")
            else:
                st.warning("Arkadas listesi yuklenemedi. Sunucu baglantisini kontrol edin.")


# =========================================================================
# Footer
# =========================================================================
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:rgba(255,255,255,0.3); font-size:0.82em;">'
    "MathAI Yarisma Arenasi &middot; Adaptif Matematik Ogrenme Platformu"
    "</p>",
    unsafe_allow_html=True,
)
