"""
AI Ders Arkadasi Sayfasi - AI Tutor Chat Interface.

Yapay zeka destekli matematik ders arkadasi. Ogrenciler
sohbet ederek soru sorabilir, adim adim aciklamalar alabilir
ve hatalarini anlamlandirabilir. Turkce kullanici arayuzu.
"""

import streamlit as st
from datetime import datetime
from typing import Any, Dict, List, Optional

from frontend.theme import apply_theme, render_sidebar, api_get, api_post, stat_card, section_header

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Ders Arkadasi - MathAI",
    page_icon="\U0001f916",
    layout="wide",
)

apply_theme()
render_sidebar("pages/ai_tutor")

# ---------------------------------------------------------------------------
# Additional page-specific CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Tutor hero gradient */
.tutor-hero {
    background: linear-gradient(135deg, #667eea 0%, #5a3fbe 50%, #764ba2 100%);
    border-radius: 20px;
    padding: 40px 36px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 12px 48px rgba(102, 126, 234, 0.4);
    position: relative;
    overflow: hidden;
}
.tutor-hero::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -15%;
    width: 350px;
    height: 350px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.tutor-hero::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -10%;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(118,75,162,0.3) 0%, transparent 70%);
    border-radius: 50%;
}
.tutor-hero h1 {
    color: white !important;
    font-size: 2.3em;
    font-weight: 700;
    margin: 0 0 8px 0;
    position: relative;
    z-index: 1;
}
.tutor-hero p {
    color: rgba(255,255,255,0.88);
    font-size: 1.08em;
    line-height: 1.6;
    margin: 0;
    max-width: 680px;
    position: relative;
    z-index: 1;
}
.tutor-hero .hero-badges {
    margin-top: 16px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}
.hero-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 24px;
    font-size: 0.85em;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.25);
    background: rgba(255,255,255,0.12);
    color: white;
    backdrop-filter: blur(4px);
}

/* Session info panel */
.session-info {
    background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid #667eea;
    margin-bottom: 16px;
}
.session-info p {
    margin: 2px 0;
    font-size: 0.92em;
    color: #3730a3;
}
.session-info strong {
    color: #1e1b4b;
}

/* Explanation card */
.explanation-card {
    background: white;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.07);
    border-left: 5px solid #667eea;
    margin: 16px 0;
}
.explanation-card h4 {
    color: #333 !important;
    margin: 0 0 12px 0;
    font-size: 1.1em;
}
.explanation-card p, .explanation-card li {
    color: #444;
    line-height: 1.7;
    font-size: 0.96em;
}

/* Step card */
.step-card {
    background: #f5f3ff;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 4px solid #8b5cf6;
}
.step-card .step-num {
    font-weight: 700;
    color: #667eea;
    font-size: 0.9em;
    margin-bottom: 4px;
}
.step-card .step-text {
    color: #333;
    font-size: 0.95em;
    line-height: 1.6;
}

/* Error analysis card */
.error-card {
    background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
    border-radius: 14px;
    padding: 24px;
    border-left: 5px solid #ef4444;
    margin: 16px 0;
}
.error-card h4 {
    color: #991b1b !important;
    margin: 0 0 12px 0;
}
.error-card p {
    color: #7f1d1d;
    line-height: 1.7;
}

/* Correct answer box */
.correct-box {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid #10b981;
    margin: 12px 0;
}
.correct-box strong {
    color: #065f46;
}
.correct-box p {
    color: #064e3b;
    margin: 4px 0 0 0;
    line-height: 1.6;
}

/* Tip box */
.tip-box {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid #f59e0b;
    margin: 12px 0;
}
.tip-box p {
    color: #78350f;
    margin: 0;
    line-height: 1.6;
}

/* Active session pulse */
@keyframes session-pulse {
    0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4); }
    70% { box-shadow: 0 0 0 8px rgba(102, 126, 234, 0); }
    100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
}
.session-active-dot {
    display: inline-block;
    width: 10px; height: 10px;
    background: #667eea;
    border-radius: 50%;
    animation: session-pulse 2s infinite;
    vertical-align: middle;
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_SESSION_DEFAULTS = {
    "tutor_user_id": "",
    "tutor_session_id": None,
    "tutor_session_active": False,
    "tutor_messages": [],
    "tutor_topic": None,
    "tutor_message_count": 0,
}
for _k, _v in _SESSION_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ---------------------------------------------------------------------------
# Topic list (Turkish)
# ---------------------------------------------------------------------------
KONU_LISTESI = {
    "": "Konu Secilmedi (Genel)",
    "arithmetic": "Aritmetik",
    "fractions": "Kesirler",
    "percentages": "Yuzdelik",
    "algebra": "Cebir",
    "geometry": "Geometri",
    "ratios": "Oran-Oranti",
    "exponents": "Uslu Sayilar",
    "statistics": "Istatistik",
    "number_theory": "Sayi Teorisi",
    "systems_of_equations": "Denklem Sistemleri",
    "inequalities": "Esitsizlikler",
    "functions": "Fonksiyonlar",
    "trigonometry": "Trigonometri",
    "polynomials": "Polinomlar",
    "sets_and_logic": "Kumeler ve Mantik",
    "coordinate_geometry": "Koordinat Geometrisi",
}

SINIF_SEVIYELERI = {
    5: "5. Sinif",
    6: "6. Sinif",
    7: "7. Sinif",
    8: "8. Sinif (LGS)",
    9: "9. Sinif",
    10: "10. Sinif",
    11: "11. Sinif",
    12: "12. Sinif (YKS)",
}
# ---------------------------------------------------------------------------
# Fallback / demo data
# ---------------------------------------------------------------------------

FALLBACK_RESPONSES = [
    (
        "Tabii ki yardimci olabilirim! Bu konuyu birlikte adim adim cozelim.\n\n"
        "Oncelikle problemi anladigimizdan emin olalim. Ne biliyoruz ve ne bulmamiz gerekiyor?\n\n"
        "Adim 1: Verilen bilgileri yazalim.\n"
        "Adim 2: Hangi formul veya yontemi kullanacagimizi belirleyelim.\n"
        "Adim 3: Cozumu uygulayalim.\n\n"
        "Soruyu bana yazarsan, birlikte cozebiliriz!"
    ),
    (
        "Harika bir soru! Bunu anlamanin en iyi yolu bir ornekle bakmak.\n\n"
        "Ornegin: Bir sayinin %25'i 30 ise, sayi kactir?\n\n"
        "Cozum:\n"
        "- %25 demek 25/100 = 1/4 demektir\n"
        "- 1/4 x sayi = 30\n"
        "- sayi = 30 x 4 = 120\n\n"
        "Yani cevap 120! Senin sorunla ayni mantigi uygulayabiliriz."
    ),
    (
        "Bu konuda zorlanman cok normal, bircogu icin zor bir konu.\n\n"
        "Temel kavramlara donelim:\n"
        "1. Denklemin iki tarafi birbirine esittir\n"
        "2. Bir tarafa ne yaparsak, diger tarafa da ayni seyi yapariz\n"
        "3. Amacimiz bilinmeyeni yalniz birakmaktir\n\n"
        "Ornek: 3x + 5 = 20\n"
        "- Iki taraftan 5 cikaralim: 3x = 15\n"
        "- Iki tarafi 3'e bolelim: x = 5\n\n"
        "Daha fazla ornek ister misin?"
    ),
    (
        "Bu soruyu anlamanin anahtar noktasi, dogru stratejiyi secmektir.\n\n"
        "Matematik problemlerinde su adimlari takip etmek faydalidir:\n"
        "1. Problemi dikkatlice oku\n"
        "2. Bilinenleri ve bilinmeyenleri belirle\n"
        "3. Bir plan yap (formul, cizim, tablo vb.)\n"
        "4. Plani uygula\n"
        "5. Sonucu kontrol et\n\n"
        "Hangi adimda takildigini soylersen, oradan devam edelim!"
    ),
    (
        "Geometri sorularinda gorsel dusunmek cok onemlidir!\n\n"
        "Uc onemli formul:\n"
        "- Ucgenin alani = (taban x yukseklik) / 2\n"
        "- Dairenin alani = pi x r^2\n"
        "- Dikdortgenin cevresi = 2 x (uzunluk + genislik)\n\n"
        "Bir sekil cizerek problemi gorunur hale getirmek, cozumu "
        "bulmada cok yardimci olur. Hangi geometri konusunda yardim istersin?"
    ),
]

FALLBACK_EXPLANATION = {
    "explanation": (
        "Bu soruyu adim adim birlikte cozelim:\n\n"
        "Adim 1: Soruyu anla\n"
        "Soruda bize verilen bilgileri yazalim ve ne bulmamiz gerektigini belirleyelim.\n\n"
        "Adim 2: Strateji belirle\n"
        "Bu tur sorularda genellikle ilgili formulu veya kurali uygulamamiz gerekir.\n\n"
        "Adim 3: Cozumu uygula\n"
        "Bilinen degerleri formule yerlestirelim ve bilinmeyeni hesaplayalim.\n\n"
        "Adim 4: Kontrol et\n"
        "Buldugumuz sonucu tekrar soruya koyarak dogru olup olmadigini kontrol edelim."
    ),
    "steps": [
        {"step": 1, "title": "Soruyu Anla", "description": "Verilen ve istenen degerleri belirle."},
        {"step": 2, "title": "Strateji Belirle", "description": "Uygun formul veya yontemi sec."},
        {"step": 3, "title": "Cozumu Uygula", "description": "Hesaplamalari adim adim yap."},
        {"step": 4, "title": "Kontrol Et", "description": "Sonucu dogrula ve mantiksal tutarliligini kontrol et."},
    ],
    "tips": [
        "Problemi dikkatlice okuyun, bazi bilgiler satirlar arasinda gizli olabilir.",
        "Birim donusumlerine dikkat edin.",
        "Sonucunuzu kontrol etmek icin farkli bir yontem deneyin.",
    ],
    "related_topics": ["Temel islemler", "Denklem cozme"],
}

FALLBACK_ERROR_EXPLANATION = {
    "error_type": "Islem Hatasi",
    "explanation": (
        "Bu soruda yapilan hata, islem onceligi kurallarina dikkat edilmemesinden "
        "kaynaklanmaktadir.\n\n"
        "Dogru yaklasim:\n"
        "1. Oncelikle parantez icindeki islemleri yap\n"
        "2. Sonra carpma ve bolme islemlerini yap (soldan saga)\n"
        "3. En son toplama ve cikarma islemlerini yap (soldan saga)\n\n"
        "Bu kurala PEMDAS veya islem onceligi kurali denir."
    ),
    "correct_solution_steps": [
        "Parantez icini hesapla",
        "Uslu ifadeleri hesapla",
        "Carpma ve bolme islemlerini yap",
        "Toplama ve cikarma islemlerini yap",
    ],
    "common_mistake": (
        "Bu tur hatalar genellikle islem onceligi atlandiginda veya "
        "isaret kurallari hatali uygulandiginda ortaya cikar."
    ),
    "tips": [
        "Islem onceligi kuralini her zaman hatirla: Parantez > Us > Carpma/Bolme > Toplama/Cikarma",
        "Islemleri adim adim yaz, kafadan yapmaya calisma.",
        "Her adimda sonucu kontrol et.",
    ],
    "encouragement": (
        "Bu hatayi yapmak cok dogal! Bir dahaki sefere islem sirasina dikkat ederek "
        "bu tur sorulari rahatlica cozebilirsin. Pratik yaptikca daha iyi olacaksin!"
    ),
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_fallback_response(message: str) -> str:
    """Return a relevant fallback response based on simple keyword matching."""
    message_lower = message.lower()

    if any(kw in message_lower for kw in ["geometri", "ucgen", "daire", "alan", "cevre", "dikdortgen"]):
        return FALLBACK_RESPONSES[4]
    elif any(kw in message_lower for kw in ["denklem", "x =", "bilinmeyen", "coz"]):
        return FALLBACK_RESPONSES[2]
    elif any(kw in message_lower for kw in ["yuzde", "%", "oran", "oranti"]):
        return FALLBACK_RESPONSES[1]
    elif any(kw in message_lower for kw in ["nasil", "yardim", "anlamadim", "zor"]):
        return FALLBACK_RESPONSES[3]
    else:
        return FALLBACK_RESPONSES[0]


def _render_chat_message(role: str, content: str, timestamp: Optional[str] = None):
    """Render a single chat message using st.chat_message."""
    avatar = "\U0001f9d1‍\U0001f393" if role == "user" else "\U0001f916"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)
        if timestamp:
            st.caption(timestamp)


def _format_timestamp(iso_str: Optional[str] = None) -> str:
    """Format an ISO timestamp or return current time."""
    if iso_str:
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return dt.strftime("%H:%M")
        except (ValueError, AttributeError):
            pass
    return datetime.now().strftime("%H:%M")


# ===========================================================================
# HERO
# ===========================================================================
st.markdown("""
<div class="tutor-hero">
    <h1>\U0001f916 AI Ders Arkadasi</h1>
    <p>
        Yapay zeka destekli matematik ders arkadasinla sohbet et, sorularini sor,
        adim adim aciklamalar al ve hatalarini anla. Matematik ogrenmenin en
        eglenceli yolu!
    </p>
    <div class="hero-badges">
        <span class="hero-badge">\U0001f4ac Sohbet</span>
        <span class="hero-badge">\U0001f4dd Adim Adim Aciklama</span>
        <span class="hero-badge">\U0001f50d Hata Analizi</span>
        <span class="hero-badge">\U0001f1f9\U0001f1f7 Turkce Destek</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick stats row
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    stat_card("\U0001f4ac", "Sohbet", "Sorularini sor")
with col_s2:
    stat_card("\U0001f4dd", "Aciklama", "Adim adim ogren")
with col_s3:
    stat_card("\U0001f50d", "Hata Analizi", "Hatalarini anla")
with col_s4:
    stat_card("\U0001f3af", "Kisisel", "Sana ozel cevaplar")

st.markdown("")

# ===========================================================================
# TABS
# ===========================================================================
tab_chat, tab_explain = st.tabs([
    "\U0001f4ac Sohbet",
    "\U0001f4dd Soru Aciklama",
])

# ---------------------------------------------------------------------------
# TAB 1 - CHAT (Sohbet)
# ---------------------------------------------------------------------------
with tab_chat:

    section_header("Matematik Sohbet Asistani")

    # -- Session setup area --
    if not st.session_state.tutor_session_active:

        st.markdown("""
        <div class="session-info">
            <p><strong>\U0001f4a1 Nasil Baslanir?</strong></p>
            <p>Kullanici ID'nizi girin, istege bagli olarak bir konu secin ve
            &quot;Oturumu Baslat&quot; butonuna basin. Ardindan sohbet alaninda
            sorularinizi sorabilirsiniz.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("start_session_form", clear_on_submit=False):
            form_col1, form_col2 = st.columns(2)

            with form_col1:
                user_id_input = st.text_input(
                    "Kullanici ID",
                    value=st.session_state.tutor_user_id,
                    placeholder="ornek: ogrenci_42",
                    key="form_user_id",
                )

            with form_col2:
                topic_keys = list(KONU_LISTESI.keys())
                topic_labels = list(KONU_LISTESI.values())
                selected_topic_idx = st.selectbox(
                    "Konu (istege bagli)",
                    range(len(topic_keys)),
                    format_func=lambda i: topic_labels[i],
                    key="form_topic_select",
                )
                selected_topic = topic_keys[selected_topic_idx] if selected_topic_idx else None

            start_btn = st.form_submit_button(
                "\U0001f680 Oturumu Baslat",
                type="primary",
                use_container_width=True,
            )

        if start_btn:
            if not user_id_input or not user_id_input.strip():
                st.error("Lutfen bir Kullanici ID girin.")
            else:
                st.session_state.tutor_user_id = user_id_input.strip()

                # Build request payload
                payload = {"user_id": user_id_input.strip()}
                if selected_topic:
                    payload["topic"] = selected_topic

                result = api_post("/tutor/start", payload)

                if result:
                    session_data = result if isinstance(result, dict) else {}
                    session_id = session_data.get("session_id", session_data.get("id", ""))
                    st.session_state.tutor_session_id = session_id
                    st.session_state.tutor_session_active = True
                    st.session_state.tutor_messages = []
                    st.session_state.tutor_topic = selected_topic
                    st.session_state.tutor_message_count = 0

                    # Add welcome message
                    topic_name = KONU_LISTESI.get(selected_topic, "Genel") if selected_topic else "Genel"
                    welcome_msg = (
                        f"Merhaba! Ben senin matematik ders arkadasinim. "
                        f"Bugunku konumuz: **{topic_name}**. "
                        f"Bana istedigin soruyu sorabilirsin. Birlikte cozelim!"
                    )
                    st.session_state.tutor_messages.append({
                        "role": "assistant",
                        "content": welcome_msg,
                        "timestamp": datetime.now().strftime("%H:%M"),
                    })
                    st.rerun()
                else:
                    # Fallback: start session locally
                    import uuid as _uuid
                    local_session_id = f"local_{_uuid.uuid4().hex[:8]}"
                    st.session_state.tutor_session_id = local_session_id
                    st.session_state.tutor_session_active = True
                    st.session_state.tutor_messages = []
                    st.session_state.tutor_topic = selected_topic
                    st.session_state.tutor_message_count = 0

                    topic_name = KONU_LISTESI.get(selected_topic, "Genel") if selected_topic else "Genel"
                    welcome_msg = (
                        f"Merhaba! Ben senin matematik ders arkadasinim. "
                        f"Bugunku konumuz: **{topic_name}**. "
                        f"Sunucu baglantisi kurulamadi, ama yine de sana yardimci olabilirim. "
                        f"Sorularini bana yaz!"
                    )
                    st.session_state.tutor_messages.append({
                        "role": "assistant",
                        "content": welcome_msg,
                        "timestamp": datetime.now().strftime("%H:%M"),
                    })
                    st.rerun()

    # -- Active session area --
    else:
        session_id = st.session_state.tutor_session_id
        topic = st.session_state.tutor_topic
        topic_name = KONU_LISTESI.get(topic, "Genel") if topic else "Genel"
        msg_count = st.session_state.tutor_message_count

        # Session info bar
        st.markdown(f"""
        <div class="session-info">
            <p>
                <span class="session-active-dot"></span>
                <strong>Aktif Oturum</strong> &middot;
                Oturum ID: <code>{session_id[:16]}...</code> &middot;
                Konu: <strong>{topic_name}</strong> &middot;
                Mesaj: <strong>{msg_count}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Load history from server if messages are empty (e.g. page refresh)
        if not st.session_state.tutor_messages and session_id and not session_id.startswith("local_"):
            history_data = api_get(f"/tutor/history/{session_id}")
            if history_data:
                messages_list = history_data if isinstance(history_data, list) else history_data.get("messages", [])
                for msg in messages_list:
                    st.session_state.tutor_messages.append({
                        "role": msg.get("role", "assistant"),
                        "content": msg.get("content", ""),
                        "timestamp": _format_timestamp(msg.get("timestamp")),
                    })

        # Render chat messages
        for msg in st.session_state.tutor_messages:
            _render_chat_message(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg.get("timestamp"),
            )

        # Chat input
        user_input = st.chat_input(
            placeholder="Matematik sorunuzu yazin...",
            key="chat_input",
        )

        if user_input:
            # Add user message to state
            now_str = datetime.now().strftime("%H:%M")
            st.session_state.tutor_messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": now_str,
            })
            st.session_state.tutor_message_count += 1

            # Display user message immediately
            _render_chat_message("user", user_input, now_str)

            # Send to backend
            response_text = None
            if session_id and not session_id.startswith("local_"):
                result = api_post(
                    f"/tutor/message/{session_id}",
                    {"message": user_input},
                )
                if result:
                    resp_data = result if isinstance(result, dict) else {}
                    # Response might be nested: result.message.content or result.response
                    msg_obj = resp_data.get("message", {})
                    if isinstance(msg_obj, dict):
                        response_text = msg_obj.get("content", "")
                    if not response_text:
                        response_text = resp_data.get("response", resp_data.get("content", ""))

            # Fallback if API failed or local session
            if not response_text:
                response_text = _get_fallback_response(user_input)

            # Add assistant message
            resp_time = datetime.now().strftime("%H:%M")
            st.session_state.tutor_messages.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": resp_time,
            })

            # Display assistant message
            _render_chat_message("assistant", response_text, resp_time)

            st.rerun()

        # End session button
        st.markdown("")
        end_col1, end_col2, end_col3 = st.columns([1, 2, 1])
        with end_col2:
            if st.button(
                "\U0001f6d1 Oturumu Bitir",
                key="end_session_btn",
                use_container_width=True,
                type="secondary",
            ):
                # Notify backend
                if session_id and not session_id.startswith("local_"):
                    api_post(f"/tutor/end/{session_id}")

                # Show summary
                total_msgs = st.session_state.tutor_message_count
                st.success(
                    f"Oturum basariyla sonlandirildi. "
                    f"Toplam {total_msgs} mesaj gonderdiniz. "
                    f"Tekrar gorusmek uzere!"
                )

                # Reset session state
                st.session_state.tutor_session_id = None
                st.session_state.tutor_session_active = False
                st.session_state.tutor_messages = []
                st.session_state.tutor_topic = None
                st.session_state.tutor_message_count = 0
                st.rerun()

# ---------------------------------------------------------------------------
# TAB 2 - QUESTION EXPLANATION (Soru Aciklama)
# ---------------------------------------------------------------------------
with tab_explain:

    section_header("Soru Aciklama ve Hata Analizi")

    explain_col, error_col = st.columns(2)

    # -- Left column: Question Explanation --
    with explain_col:
        st.markdown("##### \U0001f4dd Soru Aciklama")
        st.markdown(
            "Bir matematik sorusunu girin, adim adim cozum aciklamasi alin."
        )
        st.markdown("")

        with st.form("explain_form", clear_on_submit=False):
            question_text = st.text_area(
                "Soru Metni",
                placeholder="Ornek: 3x + 7 = 22 denkleminde x kactir?",
                height=120,
                key="explain_question_text",
            )

            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                user_answer_opt = st.text_input(
                    "Senin Cevabin (istege bagli)",
                    placeholder="Ornek: 5",
                    key="explain_user_answer",
                )
            with exp_col2:
                grade_level = st.selectbox(
                    "Sinif Seviyesi",
                    options=list(SINIF_SEVIYELERI.keys()),
                    format_func=lambda k: SINIF_SEVIYELERI[k],
                    index=3,  # default 8. sinif
                    key="explain_grade_level",
                )

            explain_btn = st.form_submit_button(
                "\U0001f50d Acikla",
                type="primary",
                use_container_width=True,
            )

        if explain_btn:
            if not question_text or not question_text.strip():
                st.error("Lutfen bir soru metni girin.")
            else:
                payload = {
                    "question_data": {"text": question_text.strip()},
                    "grade_level": grade_level,
                }
                if user_answer_opt and user_answer_opt.strip():
                    payload["user_answer"] = user_answer_opt.strip()

                result = api_post("/tutor/explain", payload)

                if result is None:
                    result = FALLBACK_EXPLANATION

                # Render explanation
                explanation_text = result.get("explanation", "")
                steps = result.get("steps", [])
                tips = result.get("tips", [])
                related = result.get("related_topics", [])

                if explanation_text:
                    st.markdown(f"""
                    <div class="explanation-card">
                        <h4>\U0001f4a1 Aciklama</h4>
                        <p>{explanation_text.replace(chr(10), '<br>')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                if steps:
                    st.markdown("**Adim Adim Cozum:**")
                    for step_data in steps:
                        step_num = step_data.get("step", "")
                        step_title = step_data.get("title", "")
                        step_desc = step_data.get("description", "")
                        st.markdown(f"""
                        <div class="step-card">
                            <div class="step-num">Adim {step_num}: {step_title}</div>
                            <div class="step-text">{step_desc}</div>
                        </div>
                        """, unsafe_allow_html=True)

                if tips:
                    st.markdown("")
                    st.markdown("**\U0001f4a1 Ipuclari:**")
                    for tip in tips:
                        st.markdown(f"""
                        <div class="tip-box">
                            <p>\U0001f4cc {tip}</p>
                        </div>
                        """, unsafe_allow_html=True)

                if related:
                    st.markdown("")
                    related_str = ", ".join(related)
                    st.info(f"\U0001f517 Ilgili Konular: {related_str}")
    # -- Right column: Error Explanation --
    with error_col:
        st.markdown("##### ❌ Hata Analizi")
        st.markdown(
            "Yanlis cevapladigin bir soruyu gir, hatanin nedenini ve dogru cozumu ogren."
        )
        st.markdown("")

        with st.form("error_form", clear_on_submit=False):
            error_question = st.text_area(
                "Soru Metni",
                placeholder="Ornek: 2 + 3 x 4 = ?",
                height=120,
                key="error_question_text",
            )

            err_col1, err_col2 = st.columns(2)
            with err_col1:
                wrong_answer = st.text_input(
                    "Senin Cevabin (yanlis)",
                    placeholder="Ornek: 20",
                    key="error_wrong_answer",
                )
            with err_col2:
                correct_answer = st.text_input(
                    "Dogru Cevap",
                    placeholder="Ornek: 14",
                    key="error_correct_answer",
                )

            error_grade = st.selectbox(
                "Sinif Seviyesi",
                options=list(SINIF_SEVIYELERI.keys()),
                format_func=lambda k: SINIF_SEVIYELERI[k],
                index=3,
                key="error_grade_level",
            )

            error_btn = st.form_submit_button(
                "\U0001f50d Hatami Analiz Et",
                type="primary",
                use_container_width=True,
            )

        if error_btn:
            if not error_question or not error_question.strip():
                st.error("Lutfen soru metnini girin.")
            elif not wrong_answer or not wrong_answer.strip():
                st.error("Lutfen yanlis cevabin ne oldugunu girin.")
            elif not correct_answer or not correct_answer.strip():
                st.error("Lutfen dogru cevabi girin.")
            else:
                payload = {
                    "question_data": {"text": error_question.strip()},
                    "user_answer": wrong_answer.strip(),
                    "correct_answer": correct_answer.strip(),
                    "grade_level": error_grade,
                }

                result = api_post("/tutor/error", payload)

                if result is None:
                    result = FALLBACK_ERROR_EXPLANATION

                # Render error analysis
                error_type = result.get("error_type", "Bilinmeyen Hata")
                explanation = result.get("explanation", "")
                correct_steps = result.get("correct_solution_steps", [])
                common_mistake = result.get("common_mistake", "")
                err_tips = result.get("tips", [])
                encouragement = result.get("encouragement", "")

                # Error type and explanation
                st.markdown(f"""
                <div class="error-card">
                    <h4>⚠️ Hata Turu: {error_type}</h4>
                    <p>{explanation.replace(chr(10), '<br>')}</p>
                </div>
                """, unsafe_allow_html=True)

                # Correct solution
                if correct_steps:
                    st.markdown(f"""
                    <div class="correct-box">
                        <strong>✅ Dogru Cozum Adimlari:</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    for i, step in enumerate(correct_steps, 1):
                        st.markdown(f"""
                        <div class="step-card">
                            <div class="step-num">Adim {i}</div>
                            <div class="step-text">{step}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Common mistake pattern
                if common_mistake:
                    st.markdown(f"""
                    <div class="tip-box">
                        <p>\U0001f50e <strong>Sik Yapilan Hata:</strong> {common_mistake}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Tips
                if err_tips:
                    st.markdown("")
                    st.markdown("**\U0001f4a1 Onerilerin:**")
                    for tip in err_tips:
                        st.markdown(f"""
                        <div class="tip-box">
                            <p>\U0001f4cc {tip}</p>
                        </div>
                        """, unsafe_allow_html=True)

                # Encouragement
                if encouragement:
                    st.markdown(f"""
                    <div class="correct-box">
                        <strong>\U0001f4aa Motivasyon:</strong>
                        <p>{encouragement}</p>
                    </div>
                    """, unsafe_allow_html=True)


# ===========================================================================
# FOOTER
# ===========================================================================
st.markdown("")
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #888;">
    <p style="font-size: 0.88em;">
        \U0001f916 <strong>AI Ders Arkadasi</strong> - MathAI Adaptif Matematik Platformu<br>
        <span style="font-size: 0.8em; color: #aaa;">
            Yapay zeka destekli kisisel matematik egitimi. Turkce olarak gelistirilmistir.
        </span>
    </p>
</div>
""", unsafe_allow_html=True)
