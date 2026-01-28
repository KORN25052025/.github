"""
Shared theme, CSS, and API utilities for the Streamlit frontend.
Provides a consistent, modern Turkish UI across all pages.
"""

import streamlit as st
import requests
import os
from typing import Optional, Dict, Any, List


# API URL from environment variable (allows configuration per-machine)
API_URL = os.environ.get("API_URL", "http://localhost:8000/api/v1")


def apply_theme():
    """Apply custom CSS theme to the page."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Gradient hero cards */
    .hero-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        margin-bottom: 16px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .hero-card h2, .hero-card h3 {
        color: white !important;
        margin: 0;
    }
    .hero-card p {
        color: rgba(255,255,255,0.9);
        margin: 8px 0 0 0;
    }

    /* Stat cards */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    .stat-value {
        font-size: 2em;
        font-weight: 700;
        color: #667eea;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.85em;
        color: #666;
        margin-top: 4px;
    }

    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
        height: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .feature-icon {
        font-size: 2.5em;
        margin-bottom: 12px;
    }
    .feature-title {
        font-size: 1.1em;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
    }
    .feature-desc {
        font-size: 0.9em;
        color: #666;
        line-height: 1.5;
    }

    /* Topic cards with color coding */
    .topic-card {
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        transition: transform 0.2s;
    }
    .topic-card:hover {
        transform: scale(1.02);
    }

    /* Section headers */
    .section-header {
        font-size: 1.5em;
        font-weight: 600;
        color: #333;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }

    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #667eea;
    }

    /* Success/Warning/Error boxes */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #28a745;
        color: #155724;
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #ffc107;
        color: #856404;
    }

    /* Badge styles */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .badge-purple { background: #667eea; color: white; }
    .badge-green { background: #28a745; color: white; }
    .badge-orange { background: #fd7e14; color: white; }
    .badge-red { background: #dc3545; color: white; }

    /* Progress bar custom */
    .custom-progress {
        background: #e9ecef;
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
    }
    .custom-progress-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.5s ease;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }

    /* Leaderboard table */
    .leaderboard-row {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        background: white;
        border-radius: 8px;
        margin-bottom: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .leaderboard-rank {
        font-size: 1.2em;
        font-weight: 700;
        width: 40px;
        color: #667eea;
    }
    .leaderboard-gold { color: #FFD700; }
    .leaderboard-silver { color: #C0C0C0; }
    .leaderboard-bronze { color: #CD7F32; }

    /* Glassmorphism card */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
    }

    /* Animation for numbers */
    @keyframes countUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animated-stat {
        animation: countUp 0.5s ease-out;
    }

    /* Pulse animation for live elements */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }
    .pulse {
        animation: pulse 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar(active_page: str = ""):
    """Render the navigation sidebar."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 16px 0;">
            <span style="font-size: 2.5em;">🧮</span>
            <h2 style="color: white; margin: 8px 0 0 0;">MathAI</h2>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.85em;">Adaptif Matematik Platformu</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        nav_items = [
            ("Ana Sayfa", "🏠", "app"),
            ("Pratik Yap", "📝", "pages/practice"),
            ("Konular", "📚", "pages/topics"),
            ("Ilerleme", "📊", "pages/progress"),
        ]

        feature_items = [
            ("Oyunlastirma", "🏆", "pages/gamification"),
            ("Gunluk Gorevler", "🎯", "pages/daily_challenges"),
            ("Motivasyon", "💡", "pages/motivation"),
            ("Sinav Hazirlik", "📋", "pages/exam_prep"),
            ("AI Ders Arkadasi", "🤖", "pages/ai_tutor"),
            ("Aralikli Tekrar", "🔄", "pages/spaced_repetition"),
            ("Sosyal", "👥", "pages/social"),
            ("Odevler", "📓", "pages/homework"),
            ("Erisebilirlik", "♿", "pages/accessibility"),
        ]

        st.markdown("##### 📌 Ana Menuler")
        for label, icon, page in nav_items:
            if st.button(f"{icon}  {label}", key=f"nav_{page}", use_container_width=True):
                if page == "app":
                    st.switch_page("app.py")
                else:
                    st.switch_page(f"{page}.py")

        st.markdown("---")
        st.markdown("##### 🚀 Ozellikler")
        for label, icon, page in feature_items:
            if st.button(f"{icon}  {label}", key=f"nav_{page}", use_container_width=True):
                st.switch_page(f"{page}.py")

        st.markdown("---")
        st.markdown("##### 📊 Yonetim Panelleri")
        mgmt_items = [
            ("Ogretmen Paneli", "👨‍🏫", "pages/teacher_dashboard"),
            ("Veli Paneli", "👨‍👧", "pages/parent_dashboard"),
        ]
        for label, icon, page in mgmt_items:
            if st.button(f"{icon}  {label}", key=f"nav_{page}", use_container_width=True):
                st.switch_page(f"{page}.py")

        # API status
        st.markdown("---")
        connected = check_api()
        if connected:
            st.markdown('<div style="text-align:center"><span class="badge badge-green">● API Bagli</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center"><span class="badge badge-red">● API Bagli Degil</span></div>', unsafe_allow_html=True)


def check_api() -> bool:
    """Check API connectivity."""
    try:
        r = requests.get(API_URL.replace("/api/v1", "/health"), timeout=3)
        return r.status_code == 200
    except:
        return False


def api_get(endpoint: str, params: dict = None) -> Optional[Any]:
    """GET request to API."""
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return None


def api_post(endpoint: str, data: dict = None) -> Optional[Any]:
    """POST request to API."""
    try:
        r = requests.post(f"{API_URL}{endpoint}", json=data, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return None


def api_put(endpoint: str, data: dict = None) -> Optional[Any]:
    """PUT request to API."""
    try:
        r = requests.put(f"{API_URL}{endpoint}", json=data, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return None


def api_delete(endpoint: str) -> Optional[Any]:
    """DELETE request to API."""
    try:
        r = requests.delete(f"{API_URL}{endpoint}", timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return None


def stat_card(value, label, icon=""):
    """Render a stat card."""
    st.markdown(f"""
    <div class="stat-card animated-stat">
        <div style="font-size:1.5em; margin-bottom:4px;">{icon}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def feature_card(icon, title, description):
    """Render a feature card."""
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-icon">{icon}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def progress_bar(value: float, label: str = ""):
    """Render a custom progress bar."""
    pct = min(max(value * 100, 0), 100)
    st.markdown(f"""
    {f'<div style="font-size:0.85em; color:#666; margin-bottom:4px;">{label} - %{pct:.0f}</div>' if label else ''}
    <div class="custom-progress">
        <div class="custom-progress-fill" style="width: {pct}%"></div>
    </div>
    """, unsafe_allow_html=True)


def section_header(text: str):
    """Render a section header."""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


TOPIC_COLORS = {
    "arithmetic": "#FF6B6B",
    "fractions": "#4ECDC4",
    "percentages": "#45B7D1",
    "algebra": "#96CEB4",
    "geometry": "#FFEAA7",
    "ratios": "#DDA0DD",
    "exponents": "#98D8C8",
    "statistics": "#F7DC6F",
    "number_theory": "#BB8FCE",
    "systems_of_equations": "#85C1E9",
    "inequalities": "#F1948A",
    "functions": "#82E0AA",
    "trigonometry": "#F8C471",
    "polynomials": "#AED6F1",
    "sets_and_logic": "#D7BDE2",
    "coordinate_geometry": "#A3E4D7",
}


def get_topic_color(slug: str) -> str:
    """Get color for a topic."""
    return TOPIC_COLORS.get(slug, "#667eea")
