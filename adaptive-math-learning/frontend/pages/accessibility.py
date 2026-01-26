"""
Accessibility Page - Erisebilirlik ve Kapsayicilik Merkezi.

Matematik sozlugu, metin okuma (TTS), erisebilirlik ayarlari ve
ozel egitim destegi saglayan kapsamli erisebilirlik sayfasi.
"""

import streamlit as st
from frontend.theme import apply_theme, render_sidebar, api_get, api_post, api_put, stat_card, section_header

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Erisebilirlik - MathAI",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar("accessibility")

# ---------------------------------------------------------------------------
# Extra page-level CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Glossary result card */
.glossary-card {
    background: white;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-left: 5px solid #667eea;
    margin-bottom: 16px;
    transition: transform 0.2s;
}
.glossary-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(0,0,0,0.12);
}
.glossary-term {
    font-size: 1.4em;
    font-weight: 700;
    color: #333;
    margin-bottom: 4px;
}
.glossary-lang-tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 16px;
    font-size: 0.78em;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
}
.lang-tr { background: #e8f0fe; color: #1a56db; }
.lang-en { background: #fef3c7; color: #b45309; }
.lang-ku { background: #d1fae5; color: #065f46; }
.lang-ar { background: #fce7f3; color: #9d174d; }

/* TTS result card */
.tts-card {
    background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
    border-radius: 14px;
    padding: 24px;
    border-left: 5px solid #4f46e5;
    margin-top: 12px;
}

/* Settings panel */
.settings-panel {
    background: white;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    border: 1px solid #f0f0f0;
}

/* Special ed card */
.sped-card {
    background: linear-gradient(135deg, #fef9c3 0%, #fde68a 100%);
    border-radius: 14px;
    padding: 20px;
    border-left: 5px solid #f59e0b;
    margin-bottom: 12px;
}

/* Scaffolding card */
.scaffold-card {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    border-radius: 14px;
    padding: 20px;
    border-left: 5px solid #10b981;
    margin-bottom: 12px;
}

/* Celebration card */
.celebration-card {
    background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
    border-radius: 16px;
    padding: 28px;
    text-align: center;
    border: 2px solid #ec4899;
    box-shadow: 0 6px 24px rgba(236,72,153,0.2);
}
.celebration-card .emoji {
    font-size: 3em;
    margin-bottom: 8px;
}
.celebration-card .message {
    font-size: 1.3em;
    font-weight: 600;
    color: #9d174d;
}

/* Step list */
.step-item {
    background: white;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    border-left: 4px solid #667eea;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    display: flex;
    align-items: center;
    gap: 12px;
}
.step-number {
    background: #667eea;
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85em;
    flex-shrink: 0;
}
.step-text {
    color: #333;
    font-size: 0.95em;
}

/* Language card */
.lang-card {
    background: white;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    border: 1px solid #e5e7eb;
    transition: transform 0.2s, box-shadow 0.2s;
}
.lang-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.lang-card .flag { font-size: 2em; margin-bottom: 6px; }
.lang-card .name { font-weight: 600; color: #333; font-size: 1.05em; }
.lang-card .native { color: #666; font-size: 0.9em; }
.lang-card .dir-tag {
    display: inline-block;
    margin-top: 6px;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.75em;
    font-weight: 600;
    background: #f3f4f6;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Hero Section
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-card" style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);">
    <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
        <span style="font-size:2.8em;">♿</span>
        <div>
            <h2 style="margin:0; font-size:1.8em;">Erisebilirlik ve Kapsayicilik</h2>
            <p style="margin:6px 0 0 0; font-size:1.05em; opacity:0.92;">
                Herkes icin matematik! Cok dilli sozluk, metin okuma, kisisellestirme ve ozel egitim destegi.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    stat_card("35+", "Sozluk Terimi", "📖")
with col2:
    stat_card("4", "Desteklenen Dil", "🌍")
with col3:
    stat_card("12+", "Ayar Secenegi", "⚙️")
with col4:
    stat_card("3", "Destek Seviyesi", "🎓")

st.markdown("")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_glossary, tab_tts, tab_settings, tab_sped = st.tabs([
    "📖 Matematik Sozlugu",
    "🔊 Metin Okuma (TTS)",
    "⚙️ Ayarlar",
    "🎓 Ozel Egitim",
])

# ========================== TAB 1: Matematik Sozlugu =======================
with tab_glossary:
    section_header("Matematik Sozlugu")
    st.markdown("Matematik terimlerini Turkce, Ingilizce, Kurtce ve Arapca olarak arayin.")

    st.markdown("")

    # --- Search by exact term ---
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        search_term = st.text_input(
            "Terim Ara",
            placeholder="Ornegin: toplama, fraction, denklem ...",
            key="glossary_search_term",
            label_visibility="collapsed",
        )
    with col_btn:
        search_clicked = st.button("🔍 Ara", use_container_width=True, type="primary", key="btn_search_glossary")

    if search_clicked and search_term:
        with st.spinner("Terim araniyor..."):
            result = api_get(f"/accessibility/glossary/{search_term.strip()}")

        if result:
            _render_glossary_entry(result) if callable(globals().get("_render_glossary_entry")) else None

            # Inline rendering since helper not yet defined at module scope;
            # we render directly:
            all_tr = result.get("all_translations", {})
            st.markdown(f"""
            <div class="glossary-card">
                <div class="glossary-term">{result.get('term', search_term)}</div>
                <div style="margin:8px 0 12px 0;">
                    <span class="glossary-lang-tag lang-tr">🇹🇷 {all_tr.get('tr', '-')}</span>
                    <span class="glossary-lang-tag lang-en">🇬🇧 {all_tr.get('en', '-')}</span>
                    <span class="glossary-lang-tag lang-ku">🟢 {all_tr.get('ku', '-')}</span>
                    <span class="glossary-lang-tag lang-ar">🟣 {all_tr.get('ar', '-')}</span>
                </div>
                <div style="color:#555; line-height:1.6; margin-bottom:8px;">
                    <strong>Tanim:</strong> {result.get('definition', '-')}
                </div>
                {"<div style='color:#667eea; font-weight:600;'>Ornek: " + result.get('example') + "</div>" if result.get('example') else ""}
                {"<div style='margin-top:8px; color:#888; font-size:0.85em;'>Iliskili terimler: " + ", ".join(result.get('related_terms', [])) + "</div>" if result.get('related_terms') else ""}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"'{search_term}' terimi bulunamadi. Farkli bir terim deneyin.")

    # --- Browse / search glossary ---
    st.markdown("")
    section_header("Sozluge Gozat")

    browse_query = st.text_input(
        "Sozlukte ara",
        placeholder="Anahtar kelime girin (bos birakirsaniz tum terimler listelenir)...",
        key="glossary_browse_query",
    )

    if st.button("Gozat", key="btn_browse_glossary", use_container_width=False):
        with st.spinner("Sozluk yukleniyor..."):
            params = {"q": browse_query} if browse_query else {"q": ""}
            browse_results = api_get("/accessibility/glossary", params=params)

        if browse_results and isinstance(browse_results, list) and len(browse_results) > 0:
            st.success(f"{len(browse_results)} terim bulundu.")
            for entry in browse_results:
                all_tr = entry.get("all_translations", {})
                with st.expander(f"📐 {entry.get('term', '?')} — {all_tr.get('en', '')}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Turkce:** {all_tr.get('tr', '-')}")
                        st.markdown(f"**Ingilizce:** {all_tr.get('en', '-')}")
                    with c2:
                        st.markdown(f"**Kurtce:** {all_tr.get('ku', '-')}")
                        st.markdown(f"**Arapca:** {all_tr.get('ar', '-')}")
                    st.markdown(f"**Tanim:** {entry.get('definition', '-')}")
                    if entry.get("example"):
                        st.info(f"Ornek: {entry['example']}")
                    if entry.get("related_terms"):
                        st.caption(f"Iliskili: {', '.join(entry['related_terms'])}")
        elif browse_results is not None:
            st.info("Aramaniza uygun terim bulunamadi.")
        else:
            st.error("Sozluk yuklenirken bir hata olustu. Lutfen API baglantisini kontrol edin.")

    # --- Available languages ---
    st.markdown("")
    section_header("Desteklenen Diller")

    lang_data = api_get("/accessibility/languages")
    if lang_data and isinstance(lang_data, list):
        lang_cols = st.columns(len(lang_data))
        flag_map = {"tr": "🇹🇷", "en": "🇬🇧", "ku": "🟢", "ar": "🟣"}
        for col, lang in zip(lang_cols, lang_data):
            with col:
                flag = flag_map.get(lang.get("code", ""), "🌐")
                st.markdown(f"""
                <div class="lang-card">
                    <div class="flag">{flag}</div>
                    <div class="name">{lang.get('name', '-')}</div>
                    <div class="native">{lang.get('native_name', '-')}</div>
                    <div class="dir-tag">Yazi yonu: {lang.get('direction', 'ltr').upper()}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Fallback static display
        fallback_cols = st.columns(4)
        fallback_langs = [
            ("🇹🇷", "Turkce", "Turkce", "LTR"),
            ("🇬🇧", "English", "English", "LTR"),
            ("🟢", "Kurdish", "Kurdi", "LTR"),
            ("🟣", "Arabic", "العربية", "RTL"),
        ]
        for col, (flag, name, native, direction) in zip(fallback_cols, fallback_langs):
            with col:
                st.markdown(f"""
                <div class="lang-card">
                    <div class="flag">{flag}</div>
                    <div class="name">{name}</div>
                    <div class="native">{native}</div>
                    <div class="dir-tag">Yazi yonu: {direction}</div>
                </div>
                """, unsafe_allow_html=True)


# ========================== TAB 2: Metin Okuma (TTS) =======================
with tab_tts:
    section_header("Metin Okuma (Text-to-Speech)")
    st.markdown("Matematik sorularini veya herhangi bir metni sesli okutun. Ogrencilerin dinleyerek ogrenmesini destekler.")

    st.markdown("")

    tts_text = st.text_area(
        "Okunacak Metin",
        placeholder="Sesli okunmasini istediginiz metni buraya yazin...",
        height=120,
        key="tts_text_input",
    )

    col_lang, col_gen = st.columns([2, 1])
    with col_lang:
        tts_language = st.selectbox(
            "Dil Secin",
            options=["tr", "en"],
            format_func=lambda x: "Turkce" if x == "tr" else "English",
            key="tts_language",
        )
    with col_gen:
        st.markdown("")
        tts_generate = st.button("🔊 Sesi Olustur", type="primary", use_container_width=True, key="btn_tts_generate")

    if tts_generate:
        if not tts_text or not tts_text.strip():
            st.warning("Lutfen okunacak bir metin girin.")
        else:
            with st.spinner("Ses olusturuluyor..."):
                tts_result = api_post("/accessibility/tts", data={
                    "text": tts_text.strip(),
                    "language": tts_language,
                })

            if tts_result:
                st.markdown(f"""
                <div class="tts-card">
                    <div style="font-size:1.2em; font-weight:600; color:#312e81; margin-bottom:12px;">
                        🔊 Ses Basariyla Olusturuldu
                    </div>
                    <div style="display:flex; gap:24px; flex-wrap:wrap;">
                        <div>
                            <span style="color:#4338ca; font-weight:600;">Ses Dosyasi:</span><br/>
                            <code style="font-size:0.85em;">{tts_result.get('audio_url', '-')}</code>
                        </div>
                        <div>
                            <span style="color:#4338ca; font-weight:600;">Dil:</span><br/>
                            {'Turkce' if tts_result.get('language') == 'tr' else 'English'}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if tts_result.get("phonetic"):
                    st.markdown("")
                    st.info(f"Fonetik: {tts_result['phonetic']}")

                if tts_result.get("duration_seconds"):
                    st.caption(f"Tahmini sure: {tts_result['duration_seconds']} saniye")
            else:
                st.error("Ses olusturulurken bir hata olustu. Lutfen API baglantisini kontrol edin.")

    # Helpful info
    st.markdown("")
    with st.expander("ℹ️ Metin Okuma Hakkinda"):
        st.markdown("""
        **Metin Okuma (TTS) Ozellikleri:**

        - Turkce ve Ingilizce dil destegi
        - Matematik ifadelerini sesli okuma (ornek: "3 arti 5 esittir 8")
        - Ozel egitim ogrencileri icin yavaslatilmis okuma secenegi
        - Soru metinlerini otomatik sesli okutma imkani

        **Kullanim Alanlari:**
        - Gorme engelli ogrenciler icin ekran okuyucu destegi
        - Disleksi olan ogrenciler icin isitsel ogrenme
        - Kucuk yas grubu ogrenciler icin dinleyerek anlama
        """)


# ========================== TAB 3: Ayarlar ================================
with tab_settings:
    section_header("Erisebilirlik Ayarlari")
    st.markdown("Kullanici bazli erisebilirlik tercihlerini yapilandirin. Tum ayarlar aninda uygulanir.")

    st.markdown("")

    settings_user_id = st.text_input(
        "Kullanici Kimlik Numarasi (User ID)",
        placeholder="ornek: user_001",
        key="settings_user_id",
    )

    if not settings_user_id:
        st.info("Ayarlari yuklemek icin lutfen bir Kullanici ID girin.")
    else:
        # Load current settings
        load_settings = st.button("📥 Ayarlari Yukle", key="btn_load_settings")

        if load_settings or st.session_state.get("_settings_loaded_for") == settings_user_id:
            with st.spinner("Ayarlar yukleniyor..."):
                current_settings = api_get(f"/accessibility/settings/{settings_user_id}")

            if current_settings is None:
                # Use defaults when API is unavailable
                current_settings = {
                    "user_id": settings_user_id,
                    "font_size": 16,
                    "high_contrast": False,
                    "color_blind_mode": "none",
                    "dyslexia_font": "default",
                    "reduced_motion": False,
                    "screen_reader_mode": False,
                }
                st.warning("API baglantisi kurulamadi. Varsayilan ayarlar gosteriliyor.")

            st.session_state["_settings_loaded_for"] = settings_user_id

            st.markdown("")
            st.markdown('<div class="settings-panel">', unsafe_allow_html=True)

            # --- Settings form ---
            with st.form("accessibility_settings_form"):
                st.markdown("##### 🎨 Gorunum Ayarlari")
                col_a, col_b = st.columns(2)

                with col_a:
                    font_size = st.slider(
                        "Yazi Boyutu (px)",
                        min_value=12,
                        max_value=32,
                        value=int(current_settings.get("font_size", 16)),
                        step=1,
                        key="setting_font_size",
                        help="Yazi boyutunu 12 ile 32 piksel arasinda ayarlayin.",
                    )

                    high_contrast = st.checkbox(
                        "Yuksek Kontrast Modu",
                        value=bool(current_settings.get("high_contrast", False)),
                        key="setting_high_contrast",
                        help="Yazi ve arka plan arasindaki kontrasti artirir.",
                    )

                    dyslexia_font = st.checkbox(
                        "Disleksi Dostu Yazi Tipi",
                        value=current_settings.get("dyslexia_font", "default") != "default",
                        key="setting_dyslexia_font",
                        help="OpenDyslexic yazi tipini etkinlestirir.",
                    )

                with col_b:
                    color_blind_options = {
                        "none": "Yok",
                        "protanopia": "Protanopi (Kirmizi-Yesil)",
                        "deuteranopia": "Deuteranopi (Yesil-Kirmizi)",
                        "tritanopia": "Tritanopi (Mavi-Sari)",
                    }
                    current_cb = current_settings.get("color_blind_mode", "none")
                    color_blind_mode = st.selectbox(
                        "Renk Korlugu Modu",
                        options=list(color_blind_options.keys()),
                        format_func=lambda x: color_blind_options[x],
                        index=list(color_blind_options.keys()).index(current_cb) if current_cb in color_blind_options else 0,
                        key="setting_color_blind",
                        help="Renk korlugu turunuze uygun goruntuleme modunu secin.",
                    )

                    reduced_motion = st.checkbox(
                        "Azaltilmis Hareket",
                        value=bool(current_settings.get("reduced_motion", False)),
                        key="setting_reduced_motion",
                        help="Animasyonlari ve gecis efektlerini azaltir.",
                    )

                    screen_reader = st.checkbox(
                        "Ekran Okuyucu Modu",
                        value=bool(current_settings.get("screen_reader_mode", False)),
                        key="setting_screen_reader",
                        help="Ekran okuyucu yazilimlar icin optimize edilmis mod.",
                    )

                st.markdown("---")

                save_submitted = st.form_submit_button(
                    "💾 Ayarlari Kaydet",
                    type="primary",
                    use_container_width=True,
                )

                if save_submitted:
                    update_body = {
                        "font_size": font_size,
                        "high_contrast": high_contrast,
                        "color_blind_mode": color_blind_mode,
                        "dyslexia_font": "OpenDyslexic" if dyslexia_font else "default",
                        "reduced_motion": reduced_motion,
                        "screen_reader_mode": screen_reader,
                    }

                    with st.spinner("Ayarlar kaydediliyor..."):
                        save_result = api_put(
                            f"/accessibility/settings/{settings_user_id}",
                            data=update_body,
                        )

                    if save_result:
                        st.success("Ayarlar basariyla kaydedildi!")
                    else:
                        st.error("Ayarlar kaydedilirken bir hata olustu. Lutfen tekrar deneyin.")

            st.markdown('</div>', unsafe_allow_html=True)

            # Preview of current settings
            st.markdown("")
            with st.expander("👁️ Ayar Onizleme"):
                prev_cols = st.columns(3)
                with prev_cols[0]:
                    st.markdown(f"**Yazi Boyutu:** {current_settings.get('font_size', 16)}px")
                    st.markdown(f"**Yuksek Kontrast:** {'Acik' if current_settings.get('high_contrast') else 'Kapali'}")
                with prev_cols[1]:
                    cb_label = color_blind_options.get(current_settings.get("color_blind_mode", "none"), "Yok")
                    st.markdown(f"**Renk Korlugu:** {cb_label}")
                    df_val = current_settings.get("dyslexia_font", "default")
                    st.markdown(f"**Disleksi Yazi Tipi:** {'Acik' if df_val != 'default' else 'Kapali'}")
                with prev_cols[2]:
                    st.markdown(f"**Azaltilmis Hareket:** {'Acik' if current_settings.get('reduced_motion') else 'Kapali'}")
                    st.markdown(f"**Ekran Okuyucu:** {'Acik' if current_settings.get('screen_reader_mode') else 'Kapali'}")


# ========================== TAB 4: Ozel Egitim ============================
with tab_sped:
    section_header("Ozel Egitim Destegi")
    st.markdown("Ozel egitim ihtiyaci olan ogrenciler icin soru sadeleStirme, iskele destegi ve motivasyon araclari.")

    st.markdown("")

    # --- Simplified question ---
    st.markdown("##### 📝 Soru Sadeleistirme")
    st.markdown("Bir matematik sorusunu daha kolay anlasilir hale getirin.")

    sped_col1, sped_col2 = st.columns([3, 1])
    with sped_col1:
        simplify_question = st.text_area(
            "Soru Metni",
            placeholder="Sadeleistirilecek soruyu buraya yazin. Ornek: 3x + 7 = 22 denkleminde x kactir?",
            height=100,
            key="simplify_question_text",
            label_visibility="collapsed",
        )
    with sped_col2:
        simplify_level = st.selectbox(
            "Seviye",
            options=["basic", "moderate", "maximum"],
            format_func=lambda x: {
                "basic": "Temel",
                "moderate": "Orta",
                "maximum": "Maksimum",
            }[x],
            key="simplify_level",
        )
        simplify_btn = st.button(
            "📝 Sadelesitir",
            type="primary",
            use_container_width=True,
            key="btn_simplify",
        )

    if simplify_btn:
        if not simplify_question or not simplify_question.strip():
            st.warning("Lutfen sadelestirilecek bir soru metni girin.")
        else:
            with st.spinner("Soru sadelestiriliyor..."):
                simplify_result = api_post("/accessibility/simplify", data={
                    "question_text": simplify_question.strip(),
                    "level": simplify_level,
                })

            if simplify_result:
                st.markdown(f"""
                <div class="sped-card">
                    <div style="font-weight:700; font-size:1.1em; color:#92400e; margin-bottom:10px;">
                        📝 Sadelestirilmis Soru
                    </div>
                    <div style="color:#78350f; line-height:1.7; font-size:1.05em;">
                        {simplify_result.get('simplified_text', '-')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Visual aids
                visual_aids = simplify_result.get("visual_aids", [])
                if visual_aids:
                    st.markdown("**Gorsel Yardimcilar:**")
                    for aid in visual_aids:
                        st.markdown(f"- 🖼️ {aid}")

                # Step-by-step breakdown
                steps = simplify_result.get("step_by_step_breakdown", [])
                if steps:
                    st.markdown("**Adim Adim Cozum:**")
                    for i, step in enumerate(steps, 1):
                        st.markdown(f"""
                        <div class="step-item">
                            <div class="step-number">{i}</div>
                            <div class="step-text">{step}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Vocabulary hints
                vocab = simplify_result.get("vocabulary_hints", {})
                if vocab:
                    st.markdown("**Kelime Ipuclari:**")
                    for word, hint in vocab.items():
                        st.markdown(f"- **{word}**: {hint}")

                # Extra time
                extra_time = simplify_result.get("estimated_extra_time_seconds")
                if extra_time:
                    st.caption(f"Tahmini ek sure: {extra_time} saniye")
            else:
                st.error("Soru sadelestirilirken bir hata olustu. Lutfen API baglantisini kontrol edin.")

    st.markdown("---")

    # --- Scaffolding support ---
    st.markdown("##### 🏗️ Iskele (Scaffolding) Destegi")
    st.markdown("Bir konu icin gorsel, sozel ve uygulamali destek materyalleri olusturun.")

    scaf_col1, scaf_col2, scaf_col3 = st.columns([2, 1, 1])
    with scaf_col1:
        scaffold_topic = st.text_input(
            "Konu",
            placeholder="Ornek: arithmetic, fractions, geometry...",
            key="scaffold_topic",
        )
    with scaf_col2:
        scaffold_difficulty = st.slider(
            "Zorluk",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            key="scaffold_difficulty",
            help="0 = Cok kolay, 1 = Cok zor",
        )
    with scaf_col3:
        st.markdown("")
        scaffold_btn = st.button(
            "🏗️ Destek Olustur",
            type="primary",
            use_container_width=True,
            key="btn_scaffold",
        )

    if scaffold_btn:
        if not scaffold_topic or not scaffold_topic.strip():
            st.warning("Lutfen bir konu girin.")
        else:
            with st.spinner("Iskele destegi hazirlaniyor..."):
                scaffold_result = api_post("/accessibility/scaffolding", data={
                    "topic": scaffold_topic.strip(),
                    "difficulty": scaffold_difficulty,
                })

            if scaffold_result:
                st.markdown(f"""
                <div class="scaffold-card">
                    <div style="font-weight:700; font-size:1.1em; color:#065f46; margin-bottom:6px;">
                        🏗️ Iskele Destegi Hazirlandi
                    </div>
                    <div style="color:#064e3b; font-size:0.9em;">
                        Seviye: {scaffold_result.get('simplification_level', '-')} | Konu: {scaffold_topic}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                scaf_tabs = st.columns(2)

                with scaf_tabs[0]:
                    # Visual aids
                    visual_aids = scaffold_result.get("visual_aids", [])
                    if visual_aids:
                        st.markdown("**🖼️ Gorsel Yardimcilar:**")
                        for aid in visual_aids:
                            st.markdown(f"- {aid}")

                    # Verbal prompts
                    prompts = scaffold_result.get("verbal_prompts", [])
                    if prompts:
                        st.markdown("**💬 Sozel Yonlendirmeler:**")
                        for prompt in prompts:
                            st.markdown(f"- {prompt}")

                    # Manipulative suggestions
                    manips = scaffold_result.get("manipulative_suggestions", [])
                    if manips:
                        st.markdown("**🧩 Uygulamali Materyaller:**")
                        for m in manips:
                            st.markdown(f"- {m}")

                with scaf_tabs[1]:
                    # Real world connections
                    connections = scaffold_result.get("real_world_connections", [])
                    if connections:
                        st.markdown("**🌍 Gercek Hayat Baglantilari:**")
                        for conn in connections:
                            st.markdown(f"- {conn}")

                    # Prerequisite skills
                    prereqs = scaffold_result.get("prerequisite_skills", [])
                    if prereqs:
                        st.markdown("**📋 On Kosul Beceriler:**")
                        for prereq in prereqs:
                            st.markdown(f"- {prereq}")
            else:
                st.error("Iskele destegi olusturulurken bir hata olustu. Lutfen API baglantisini kontrol edin.")

    st.markdown("---")

    # --- Celebration feedback ---
    st.markdown("##### 🎉 Motivasyon ve Kutlama")
    st.markdown("Ogrencileri motive etmek icin olumlu geri bildirim mesajlari.")

    if st.button("🎉 Motivasyon Mesaji Al", type="primary", key="btn_celebration"):
        with st.spinner("Mesaj hazirlaniyor..."):
            celebration_result = api_get("/accessibility/celebration")

        if celebration_result:
            message = celebration_result if isinstance(celebration_result, str) else celebration_result.get("message", celebration_result.get("feedback", "Harika is cikariyorsun!"))
            st.markdown(f"""
            <div class="celebration-card">
                <div class="emoji">🎉🌟🏆</div>
                <div class="message">{message}</div>
            </div>
            """, unsafe_allow_html=True)

            st.balloons()
        else:
            # Fallback motivational messages when API is unavailable
            import random
            fallback_messages = [
                "Harika! Sen cok zekasin!",
                "Tebrikler! Muhtesem bir is cikardin!",
                "Supersin! Her seferinde daha iyi oluyorsun!",
                "Aferin! Matematik senin icin cok kolay olacak!",
                "Muhteeem! Matematik yildizi olma yolundasin!",
            ]
            msg = random.choice(fallback_messages)
            st.markdown(f"""
            <div class="celebration-card">
                <div class="emoji">🎉🌟🏆</div>
                <div class="message">{msg}</div>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

    # --- Informational section ---
    st.markdown("")
    with st.expander("ℹ️ Ozel Egitim Destegi Hakkinda"):
        st.markdown("""
        **Bu bolum su ogrenci gruplarina yoneliktir:**

        - **Ogrenme Guclugu** olan ogrenciler (disleksi, diskalkuli)
        - **Dikkat Eksikligi** olan ogrenciler (DEHB)
        - **Gorme / Isitme Engeli** olan ogrenciler
        - **Zihinsel Gelisim** farkliiliklari olan ogrenciler
        - **Dil Engeli** olan ogrenciler (ana dili Turkce olmayan)

        **Sunulan Destekler:**
        1. **Soru Sadelestirme:** Karmasik sorulari anlasilir adimlar halinde sunar
        2. **Iskele Destegi:** Gorsel, sozel ve uygulamali materyallerle destekler
        3. **Motivasyon:** Olumlu geri bildirim ile ogrenci ozguvenini arttirir
        4. **Ek Sure:** Ozel ihtiyaca gore ek sure tahsisi
        5. **Cok Dilli Destek:** Turkce, Ingilizce, Kurtce ve Arapca terimler
        """)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#9ca3af; font-size:0.85em; padding:12px 0;">
    ♿ Erisebilirlik Merkezi — MathAI Adaptif Matematik Platformu<br/>
    <span style="font-size:0.8em;">Herkes icin esit firsatlarla matematik egitimi</span>
</div>
""", unsafe_allow_html=True)
