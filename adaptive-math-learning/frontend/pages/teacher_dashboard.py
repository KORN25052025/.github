"""
Ogretmen Kontrol Paneli - Teacher Dashboard Page.

Sinif yonetimi, ogrenci takibi, konu analizi, A/B test sonuclari
ve odev olusturma islevlerini sunan kapsamli ogretmen paneli.
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
    page_title="Ogretmen Paneli - MathAI",
    page_icon="\U0001F468\u200D\U0001F3EB",
    layout="wide",
)

apply_theme()
render_sidebar(active_page="pages/teacher_dashboard")


# ---------------------------------------------------------------------------
# Fallback / demo data generators
# ---------------------------------------------------------------------------

def _demo_class_statistics() -> Dict[str, Any]:
    return {
        "total_students": 32,
        "active_today": 18,
        "active_this_week": 27,
        "average_mastery": 0.64,
        "average_accuracy": 0.71,
        "total_questions_answered": 4820,
        "questions_today": 187,
    }


def _demo_student_list() -> List[Dict[str, Any]]:
    names = [
        "Ahmet Yilmaz", "Elif Demir", "Mehmet Kaya", "Zeynep Celik",
        "Burak Sahin", "Ayse Ozturk", "Emre Arslan", "Fatma Dogan",
        "Can Yildiz", "Selin Aydin", "Omer Koc", "Busra Polat",
        "Kerem Erdogan", "Deniz Ozdemir", "Yusuf Acar", "Merve Tas",
    ]
    import random
    random.seed(42)
    students = []
    topics_pool = [
        "Aritmetik", "Kesirler", "Yuzdeler", "Cebir",
        "Geometri", "Oranlar", "Uslu Sayilar", "Istatistik",
    ]
    for i, name in enumerate(names):
        mastery = round(random.uniform(0.3, 0.95), 2)
        accuracy = round(random.uniform(0.4, 0.98), 2)
        xp = random.randint(200, 5000)
        streak = random.randint(0, 25)
        n_struggling = random.randint(0, 3)
        struggling = random.sample(topics_pool, n_struggling) if n_struggling else []
        students.append({
            "student_id": f"student_{i+1:03d}",
            "name": name,
            "mastery": mastery,
            "accuracy": accuracy,
            "xp": xp,
            "streak": streak,
            "struggling_topics": struggling,
        })
    return students


def _demo_topic_performance() -> List[Dict[str, Any]]:
    return [
        {"topic": "Aritmetik", "avg_mastery": 0.78, "avg_accuracy": 0.82, "total_questions": 980, "student_count": 30},
        {"topic": "Kesirler", "avg_mastery": 0.65, "avg_accuracy": 0.70, "total_questions": 740, "student_count": 28},
        {"topic": "Yuzdeler", "avg_mastery": 0.60, "avg_accuracy": 0.66, "total_questions": 520, "student_count": 25},
        {"topic": "Cebir", "avg_mastery": 0.55, "avg_accuracy": 0.61, "total_questions": 680, "student_count": 27},
        {"topic": "Geometri", "avg_mastery": 0.70, "avg_accuracy": 0.74, "total_questions": 610, "student_count": 26},
        {"topic": "Oranlar", "avg_mastery": 0.58, "avg_accuracy": 0.63, "total_questions": 430, "student_count": 22},
        {"topic": "Uslu Sayilar", "avg_mastery": 0.50, "avg_accuracy": 0.56, "total_questions": 310, "student_count": 20},
        {"topic": "Istatistik", "avg_mastery": 0.48, "avg_accuracy": 0.53, "total_questions": 280, "student_count": 18},
        {"topic": "Trigonometri", "avg_mastery": 0.42, "avg_accuracy": 0.48, "total_questions": 190, "student_count": 15},
        {"topic": "Polinomlar", "avg_mastery": 0.45, "avg_accuracy": 0.50, "total_questions": 260, "student_count": 17},
    ]


def _demo_struggling_students() -> List[Dict[str, Any]]:
    return [
        {
            "student_id": "student_007",
            "student_name": "Emre Arslan",
            "accuracy": 0.38,
            "mastery": 0.32,
            "active_days_this_week": 1,
            "questions_this_week": 8,
            "risk_level": "yuksek",
            "risk_factors": ["Dusuk dogruluk orani", "Az soru cozuyor", "Duzenli calismiyor"],
            "struggling_topics": ["Cebir", "Kesirler", "Uslu Sayilar"],
        },
        {
            "student_id": "student_012",
            "student_name": "Busra Polat",
            "accuracy": 0.42,
            "mastery": 0.37,
            "active_days_this_week": 2,
            "questions_this_week": 12,
            "risk_level": "yuksek",
            "risk_factors": ["Dusuk dogruluk orani", "Az soru cozuyor"],
            "struggling_topics": ["Geometri", "Oranlar"],
        },
        {
            "student_id": "student_005",
            "student_name": "Burak Sahin",
            "accuracy": 0.50,
            "mastery": 0.44,
            "active_days_this_week": 3,
            "questions_this_week": 18,
            "risk_level": "orta",
            "risk_factors": ["Dogruluk orani dusuk"],
            "struggling_topics": ["Trigonometri"],
        },
    ]


def _demo_ab_test_results() -> Dict[str, Any]:
    return {
        "test_name": "Ipucu Gosterim Zamanlama Testi",
        "status": "aktif",
        "start_date": (datetime.utcnow() - timedelta(days=14)).isoformat(),
        "control_group": {
            "name": "Kontrol (Standart)",
            "student_count": 16,
            "avg_accuracy": 0.68,
            "avg_mastery": 0.60,
            "avg_questions_per_day": 12.4,
            "avg_session_minutes": 18.2,
            "retention_rate": 0.75,
        },
        "treatment_group": {
            "name": "Deney (Erken Ipucu)",
            "student_count": 16,
            "avg_accuracy": 0.74,
            "avg_mastery": 0.67,
            "avg_questions_per_day": 15.1,
            "avg_session_minutes": 22.5,
            "retention_rate": 0.82,
        },
        "significance": {
            "accuracy_p_value": 0.032,
            "mastery_p_value": 0.018,
            "is_significant": True,
        },
    }


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_hero():
    """Baslik alani."""
    st.markdown("""
    <div class="hero-card">
        <h2>Ogretmen Kontrol Paneli</h2>
        <p>Sinifinizi yonetin, ogrenci ilerlemesini takip edin ve veri odakli kararlar alin.</p>
    </div>
    """, unsafe_allow_html=True)


def render_class_statistics(stats: Dict[str, Any]):
    """Sinif istatistiklerini goster."""
    section_header("Sinif Istatistikleri")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card(stats.get("total_students", 0), "Toplam Ogrenci", icon="👥")
    with c2:
        stat_card(stats.get("active_today", 0), "Bugun Aktif", icon="🟢")
    with c3:
        stat_card(stats.get("active_this_week", 0), "Bu Hafta Aktif", icon="📅")
    with c4:
        avg_mastery = stats.get("average_mastery", 0)
        stat_card(f"%{avg_mastery * 100:.0f}", "Ort. Hakimiyet", icon="🎯")

    st.markdown("")  # spacer

    c5, c6, c7 = st.columns(3)
    with c5:
        avg_acc = stats.get("average_accuracy", 0)
        stat_card(f"%{avg_acc * 100:.0f}", "Ort. Dogruluk", icon="✅")
    with c6:
        stat_card(f"{stats.get('total_questions_answered', 0):,}", "Toplam Soru", icon="📝")
    with c7:
        stat_card(stats.get("questions_today", 0), "Bugunun Sorulari", icon="⚡")


def render_student_list(students: List[Dict[str, Any]]):
    """Ogrenci listesi tablosu."""
    section_header("Ogrenci Listesi")

    if not students:
        st.info("Henuz ogrenci verisi bulunamadi.")
        return

    # Filtreleme
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        search = st.text_input("Ogrenci Ara", placeholder="Isim ile arama...", key="student_search")
    with col_f2:
        sort_by = st.selectbox("Siralama", [
            "Isme Gore (A-Z)", "Hakimiyete Gore (Azalan)",
            "Dogruluk Oranina Gore (Azalan)", "XP (Azalan)", "Seri (Azalan)",
        ], key="student_sort")

    filtered = students
    if search:
        filtered = [s for s in filtered if search.lower() in s.get("name", "").lower()]

    if sort_by == "Hakimiyete Gore (Azalan)":
        filtered = sorted(filtered, key=lambda x: x.get("mastery", 0), reverse=True)
    elif sort_by == "Dogruluk Oranina Gore (Azalan)":
        filtered = sorted(filtered, key=lambda x: x.get("accuracy", 0), reverse=True)
    elif sort_by == "XP (Azalan)":
        filtered = sorted(filtered, key=lambda x: x.get("xp", 0), reverse=True)
    elif sort_by == "Seri (Azalan)":
        filtered = sorted(filtered, key=lambda x: x.get("streak", 0), reverse=True)
    else:
        filtered = sorted(filtered, key=lambda x: x.get("name", ""))

    # Build table data
    rows = []
    for s in filtered:
        struggling = ", ".join(s.get("struggling_topics", [])) if s.get("struggling_topics") else "-"
        rows.append({
            "Ogrenci": s.get("name", s.get("student_id", "")),
            "Hakimiyet": f"%{s.get('mastery', 0) * 100:.0f}",
            "Dogruluk": f"%{s.get('accuracy', 0) * 100:.0f}",
            "XP": s.get("xp", 0),
            "Seri": s.get("streak", 0),
            "Zorlanan Konular": struggling,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption(f"Toplam {len(filtered)} ogrenci gosteriliyor.")


def render_topic_performance(topics: List[Dict[str, Any]]):
    """Konu bazli performans analizi."""
    section_header("Konu Bazli Performans")

    if not topics:
        st.info("Konu verisi bulunamadi.")
        return

    # Tabs: chart vs table
    tab_chart, tab_table = st.tabs(["Grafik", "Tablo"])

    with tab_chart:
        chart_data = pd.DataFrame({
            "Konu": [t["topic"] for t in topics],
            "Ort. Hakimiyet (%)": [round(t.get("avg_mastery", 0) * 100, 1) for t in topics],
            "Ort. Dogruluk (%)": [round(t.get("avg_accuracy", 0) * 100, 1) for t in topics],
        })
        chart_data = chart_data.set_index("Konu")
        st.bar_chart(chart_data, height=400)

    with tab_table:
        table_rows = []
        for t in topics:
            table_rows.append({
                "Konu": t["topic"],
                "Ort. Hakimiyet": f"%{t.get('avg_mastery', 0) * 100:.0f}",
                "Ort. Dogruluk": f"%{t.get('avg_accuracy', 0) * 100:.0f}",
                "Toplam Soru": t.get("total_questions", 0),
                "Katilan Ogrenci": t.get("student_count", 0),
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    # Per-topic progress bars
    st.markdown("")
    with st.expander("Konu Hakimiyet Detaylari", expanded=False):
        for t in sorted(topics, key=lambda x: x.get("avg_mastery", 0), reverse=True):
            progress_bar(t.get("avg_mastery", 0), label=t["topic"])
            st.markdown("")


def render_struggling_students(students: List[Dict[str, Any]]):
    """Risk altindaki ogrencileri goster."""
    section_header("Risk Altindaki Ogrenciler")

    if not students:
        st.markdown("""
        <div class="success-box">
            <strong>Harika!</strong> Su anda risk altinda ogrenci bulunmuyor.
        </div>
        """, unsafe_allow_html=True)
        return

    for s in students:
        risk = s.get("risk_level", "orta")
        if risk == "yuksek":
            box_class = "warning-box"
            badge = '<span class="badge badge-red">Yuksek Risk</span>'
            border_color = "#dc3545"
        else:
            box_class = "info-box"
            badge = '<span class="badge badge-orange">Orta Risk</span>'
            border_color = "#fd7e14"

        name = s.get("student_name", s.get("student_id", ""))
        accuracy = s.get("accuracy", 0)
        mastery = s.get("mastery", 0)
        active_days = s.get("active_days_this_week", 0)
        weekly_q = s.get("questions_this_week", 0)
        factors = s.get("risk_factors", [])
        struggling = s.get("struggling_topics", [])

        factors_html = "".join(f"<li>{f}</li>" for f in factors)
        topics_html = ", ".join(struggling) if struggling else "Belirtilmemis"

        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 20px;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
                    border-left: 5px solid {border_color}; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="margin:0; color: #333;">{name}</h4>
                {badge}
            </div>
            <div style="display: flex; gap: 24px; margin-bottom: 12px; flex-wrap: wrap;">
                <div><strong>Dogruluk:</strong> %{accuracy * 100:.0f}</div>
                <div><strong>Hakimiyet:</strong> %{mastery * 100:.0f}</div>
                <div><strong>Haftalik Aktif Gun:</strong> {active_days}</div>
                <div><strong>Haftalik Soru:</strong> {weekly_q}</div>
            </div>
            <div style="margin-bottom: 8px;"><strong>Risk Faktorleri:</strong>
                <ul style="margin: 4px 0 0 0; padding-left: 20px;">{factors_html}</ul>
            </div>
            <div><strong>Zorlanan Konular:</strong> {topics_html}</div>
        </div>
        """, unsafe_allow_html=True)


def render_ab_test_results(data: Dict[str, Any]):
    """A/B test sonuclarini goster."""
    section_header("A/B Test Sonuclari")

    if not data:
        st.info("Aktif A/B testi bulunamadi.")
        return

    test_name = data.get("test_name", "Bilinmeyen Test")
    status = data.get("status", "bilinmiyor")
    status_badge = "badge-green" if status == "aktif" else "badge-orange"

    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 20px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h4 style="margin:0; color: #333;">{test_name}</h4>
            <span class="badge {status_badge}">{status.capitalize()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    control = data.get("control_group", {})
    treatment = data.get("treatment_group", {})
    sig = data.get("significance", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
                    border-radius: 12px; padding: 20px; margin-bottom: 12px;">
            <h4 style="margin: 0 0 12px 0; color: #283593;">
                {control.get('name', 'Kontrol Grubu')}
            </h4>
            <div style="color: #333; line-height: 2;">
                <strong>Ogrenci Sayisi:</strong> {control.get('student_count', 0)}<br>
                <strong>Ort. Dogruluk:</strong> %{control.get('avg_accuracy', 0) * 100:.0f}<br>
                <strong>Ort. Hakimiyet:</strong> %{control.get('avg_mastery', 0) * 100:.0f}<br>
                <strong>Gunluk Soru:</strong> {control.get('avg_questions_per_day', 0):.1f}<br>
                <strong>Oturum Suresi:</strong> {control.get('avg_session_minutes', 0):.1f} dk<br>
                <strong>Devam Orani:</strong> %{control.get('retention_rate', 0) * 100:.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                    border-radius: 12px; padding: 20px; margin-bottom: 12px;">
            <h4 style="margin: 0 0 12px 0; color: #2e7d32;">
                {treatment.get('name', 'Deney Grubu')}
            </h4>
            <div style="color: #333; line-height: 2;">
                <strong>Ogrenci Sayisi:</strong> {treatment.get('student_count', 0)}<br>
                <strong>Ort. Dogruluk:</strong> %{treatment.get('avg_accuracy', 0) * 100:.0f}<br>
                <strong>Ort. Hakimiyet:</strong> %{treatment.get('avg_mastery', 0) * 100:.0f}<br>
                <strong>Gunluk Soru:</strong> {treatment.get('avg_questions_per_day', 0):.1f}<br>
                <strong>Oturum Suresi:</strong> {treatment.get('avg_session_minutes', 0):.1f} dk<br>
                <strong>Devam Orani:</strong> %{treatment.get('retention_rate', 0) * 100:.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Comparison chart
    metrics = ["Dogruluk (%)", "Hakimiyet (%)", "Gunluk Soru", "Oturum (dk)", "Devam (%)"]
    control_vals = [
        control.get("avg_accuracy", 0) * 100,
        control.get("avg_mastery", 0) * 100,
        control.get("avg_questions_per_day", 0),
        control.get("avg_session_minutes", 0),
        control.get("retention_rate", 0) * 100,
    ]
    treatment_vals = [
        treatment.get("avg_accuracy", 0) * 100,
        treatment.get("avg_mastery", 0) * 100,
        treatment.get("avg_questions_per_day", 0),
        treatment.get("avg_session_minutes", 0),
        treatment.get("retention_rate", 0) * 100,
    ]

    comparison_df = pd.DataFrame({
        "Metrik": metrics,
        control.get("name", "Kontrol"): control_vals,
        treatment.get("name", "Deney"): treatment_vals,
    }).set_index("Metrik")

    st.bar_chart(comparison_df, height=350)

    # Significance
    is_sig = sig.get("is_significant", False)
    if is_sig:
        st.markdown("""
        <div class="success-box">
            <strong>Istatistiksel olarak anlamli!</strong>
            Deney grubu kontrol grubuna kiyasla anlamli derecede daha iyi performans gostermektedir.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-box">
            <strong>Henuz anlamli degil.</strong>
            Sonuclar istatistiksel olarak anlamli bir fark gostermemektedir. Daha fazla veri toplanmasi gerekmektedir.
        </div>
        """, unsafe_allow_html=True)

    acc_p = sig.get("accuracy_p_value", 1.0)
    mas_p = sig.get("mastery_p_value", 1.0)
    st.caption(f"Dogruluk p-degeri: {acc_p:.3f}  |  Hakimiyet p-degeri: {mas_p:.3f}")


def render_create_assignment(teacher_id: str):
    """Odev olusturma formu."""
    section_header("Yeni Odev Olustur")

    with st.form("create_assignment_form", clear_on_submit=True):
        st.markdown("##### Odev Bilgileri")

        title = st.text_input("Odev Basligi", placeholder="Ornegin: Haftalik Cebir Calismasi")

        topics_options = [
            "Aritmetik", "Kesirler", "Yuzdeler", "Cebir", "Geometri",
            "Oranlar", "Uslu Sayilar", "Istatistik", "Trigonometri",
            "Polinomlar", "Esitsizlikler", "Fonksiyonlar",
            "Koordinat Geometrisi", "Kumeler ve Mantik",
            "Denklem Sistemleri", "Sayi Teorisi",
        ]
        selected_topics = st.multiselect("Konular", topics_options, default=["Cebir"])

        col_a, col_b = st.columns(2)
        with col_a:
            question_count = st.number_input(
                "Soru Sayisi", min_value=1, max_value=50, value=10, step=1,
            )
        with col_b:
            due_days = st.number_input(
                "Teslim Suresi (gun)", min_value=1, max_value=30, value=7, step=1,
            )

        difficulty = st.select_slider(
            "Zorluk Seviyesi",
            options=["Cok Kolay", "Kolay", "Orta", "Zor", "Cok Zor"],
            value="Orta",
        )

        notes = st.text_area("Notlar (Opsiyonel)", placeholder="Ogrencilere not birakabilirsiniz...")

        submitted = st.form_submit_button("Odev Olustur", type="primary", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("Lutfen bir odev basligi girin.")
            elif not selected_topics:
                st.error("Lutfen en az bir konu secin.")
            else:
                due_date = (datetime.utcnow() + timedelta(days=due_days)).isoformat()
                payload = {
                    "title": title,
                    "topics": selected_topics,
                    "question_count": question_count,
                    "due_date": due_date,
                    "difficulty": difficulty,
                    "notes": notes,
                }
                result = api_post(f"/teacher/assignments?teacher_id={teacher_id}", data=payload)
                if result:
                    st.success(f"Odev basariyla olusturuldu: {title}")
                    st.balloons()
                else:
                    # Fallback: show success with demo mode note
                    st.warning("API baglantisi kurulamadi. Demo modunda odev olusturuldu.")
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>Odev Olusturuldu (Demo)</strong><br>
                        <strong>Baslik:</strong> {title}<br>
                        <strong>Konular:</strong> {', '.join(selected_topics)}<br>
                        <strong>Soru Sayisi:</strong> {question_count}<br>
                        <strong>Zorluk:</strong> {difficulty}<br>
                        <strong>Teslim Tarihi:</strong> {due_days} gun sonra
                    </div>
                    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    render_hero()

    # Teacher ID input
    st.markdown("")
    teacher_id = st.text_input(
        "Ogretmen Kimlik Numarasi",
        value="teacher_001",
        key="teacher_id_input",
        help="Ogretmen ID'nizi girerek sinifinizin verilerine erisebilirsiniz.",
    )

    if not teacher_id.strip():
        st.warning("Lutfen gecerli bir Ogretmen ID girin.")
        return

    st.markdown("---")

    # ---- 1. Class Statistics ----
    stats = api_get("/teacher/class/statistics", params={"teacher_id": teacher_id})
    if stats is None:
        stats = _demo_class_statistics()
    render_class_statistics(stats)

    st.markdown("---")

    # ---- 2. Student List ----
    students = api_get("/teacher/class/students", params={"teacher_id": teacher_id})
    if students is None:
        students = _demo_student_list()
    render_student_list(students)

    st.markdown("---")

    # ---- 3. Topic Performance ----
    topics = api_get("/teacher/class/topics", params={"teacher_id": teacher_id})
    if topics is None:
        topics = _demo_topic_performance()
    render_topic_performance(topics)

    st.markdown("---")

    # ---- 4. Struggling Students ----
    struggling = api_get("/teacher/struggling-students", params={"teacher_id": teacher_id})
    if struggling is None:
        struggling = _demo_struggling_students()
    render_struggling_students(struggling)

    st.markdown("---")

    # ---- 5. A/B Test Results ----
    ab_data = api_get("/teacher/ab-test/results", params={"teacher_id": teacher_id})
    if ab_data is None:
        ab_data = _demo_ab_test_results()
    render_ab_test_results(ab_data)

    st.markdown("---")

    # ---- 6. Create Assignment ----
    render_create_assignment(teacher_id)

    # Footer
    st.markdown("---")
    st.caption("MathAI Ogretmen Paneli - Adaptif Matematik Ogrenme Platformu")


if __name__ == "__main__":
    main()
