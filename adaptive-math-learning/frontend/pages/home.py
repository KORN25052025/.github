"""
Home Page - Landing page for Adaptive Math Learning.

Welcome screen with quick navigation and learning summary.
"""

import streamlit as st
import requests
from typing import Optional, Dict, List

# Page config
st.set_page_config(
    page_title="Adaptive Math Learning",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000/api/v1"


def api_request(method: str, endpoint: str, data: dict = None) -> Optional[dict]:
    """Make API request."""
    try:
        url = f"{API_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, params=data, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.RequestException:
        return None


def check_api_connection() -> bool:
    """Check if API is available."""
    # Health endpoint is at root level, not under /api/v1
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_quick_stats() -> Dict:
    """Get quick statistics."""
    stats = api_request("GET", "/progress/statistics")
    if stats:
        return stats

    return {
        "total_questions": 0,
        "overall_accuracy": 0,
        "best_streak": 0,
        "average_mastery": 0.5,
        "topics_practiced": 0,
    }


def get_recommendations() -> List[Dict]:
    """Get topic recommendations."""
    result = api_request("GET", "/progress/recommendations")
    if result:
        return result[:3]

    return [
        {"topic": "arithmetic", "current_mastery": 0.5, "reason": "Start with the basics"},
        {"topic": "fractions", "current_mastery": 0.5, "reason": "Build on arithmetic skills"},
        {"topic": "algebra", "current_mastery": 0.5, "reason": "Essential for higher math"},
    ]


def render_hero_section():
    """Render the hero/welcome section."""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        # Welcome to Adaptive Math Learning

        **Master mathematics at your own pace** with our intelligent learning system.

        Our adaptive platform:
        - Generates questions tailored to your skill level
        - Provides instant feedback and step-by-step explanations
        - Tracks your progress and adapts difficulty automatically
        - Covers topics from basic arithmetic to advanced algebra
        """)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("Start Practicing", type="primary", use_container_width=True):
                st.switch_page("pages/practice.py")
        with col_b:
            if st.button("Browse Topics", use_container_width=True):
                st.switch_page("pages/topics.py")
        with col_c:
            if st.button("View Progress", use_container_width=True):
                st.switch_page("pages/progress.py")

    with col2:
        st.markdown("""
        ### Quick Start Guide

        1. **Choose a topic** from our curriculum
        2. **Practice** with adaptive questions
        3. **Get feedback** on every answer
        4. **Track progress** as you improve
        """)


def render_stats_section(stats: Dict):
    """Render the statistics section."""
    st.markdown("---")
    st.markdown("### Your Learning Journey")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Questions Solved",
            stats.get("total_questions", 0),
            help="Total questions attempted"
        )

    with col2:
        accuracy = stats.get("overall_accuracy", 0)
        st.metric(
            "Accuracy",
            f"{accuracy:.0%}",
            help="Percentage of correct answers"
        )

    with col3:
        st.metric(
            "Best Streak",
            stats.get("best_streak", 0),
            help="Longest streak of correct answers"
        )

    with col4:
        mastery = stats.get("average_mastery", 0.5)
        st.metric(
            "Overall Mastery",
            f"{mastery:.0%}",
            help="Average mastery across all topics"
        )

    with col5:
        st.metric(
            "Topics Practiced",
            stats.get("topics_practiced", 0),
            help="Number of topics you've practiced"
        )


def render_recommendations_section(recommendations: List[Dict]):
    """Render topic recommendations."""
    st.markdown("---")
    st.markdown("### Recommended for You")

    if not recommendations:
        st.info("Complete some practice sessions to get personalized recommendations!")
        return

    cols = st.columns(len(recommendations))

    for i, (col, rec) in enumerate(zip(cols, recommendations)):
        with col:
            topic = rec.get("topic", "Unknown")
            mastery = rec.get("current_mastery", 0.5)
            reason = rec.get("reason", "Recommended for practice")

            st.markdown(f"#### {topic.title()}")
            st.progress(mastery)
            st.caption(f"Mastery: {mastery:.0%}")
            st.caption(reason)

            if st.button(f"Practice {topic.title()}", key=f"rec_{i}", use_container_width=True):
                st.session_state.selected_topic = topic
                st.switch_page("pages/practice.py")


def render_topics_preview():
    """Render a preview of available topics."""
    st.markdown("---")
    st.markdown("### Available Topics")

    topics = [
        ("Arithmetic", "Basic operations: +, -, *, /", "1-6"),
        ("Fractions", "Add, subtract, multiply, divide fractions", "3-8"),
        ("Percentages", "Percent calculations and applications", "5-9"),
        ("Algebra", "Equations and expressions", "6-12"),
        ("Geometry", "Area, perimeter, volume", "3-12"),
        ("Ratios", "Ratios and proportions", "5-9"),
    ]

    cols = st.columns(3)
    for i, (name, desc, grades) in enumerate(topics):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"**{name}**")
                st.caption(desc)
                st.caption(f"Grades {grades}")


def render_features_section():
    """Render the features section."""
    st.markdown("---")
    st.markdown("### Why Adaptive Learning?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### Personalized Difficulty

        Questions adapt to your skill level. Too easy? We'll challenge you more.
        Struggling? We'll help build your foundation.
        """)

    with col2:
        st.markdown("""
        #### Instant Feedback

        Get immediate feedback on every answer with detailed step-by-step
        explanations to help you understand your mistakes.
        """)

    with col3:
        st.markdown("""
        #### Progress Tracking

        Monitor your improvement over time. See your strengths, identify
        areas for improvement, and celebrate your achievements.
        """)


def render_api_status(connected: bool):
    """Render API connection status."""
    if connected:
        st.sidebar.success("Backend connected")
    else:
        st.sidebar.warning("Backend offline")
        st.sidebar.caption("Some features may be limited")
        st.sidebar.code("python run_backend.py", language="bash")


def main():
    # Sidebar
    st.sidebar.title("Navigation")

    if st.sidebar.button("Practice", use_container_width=True):
        st.switch_page("pages/practice.py")

    if st.sidebar.button("Topics", use_container_width=True):
        st.switch_page("pages/topics.py")

    if st.sidebar.button("Progress", use_container_width=True):
        st.switch_page("pages/progress.py")

    st.sidebar.markdown("---")

    # API status
    connected = check_api_connection()
    render_api_status(connected)

    # Main content
    render_hero_section()

    # Stats
    stats = get_quick_stats()
    render_stats_section(stats)

    # Recommendations
    recommendations = get_recommendations()
    render_recommendations_section(recommendations)

    # Topics preview
    render_topics_preview()

    # Features
    render_features_section()

    # Footer
    st.markdown("---")
    st.caption("Adaptive Mathematics Learning System - TOBB ETU BIL495/YAP495 Spring 2025")


if __name__ == "__main__":
    main()
