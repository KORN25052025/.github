"""
Progress Dashboard Page.

Comprehensive progress tracking and analytics visualization.
"""

import streamlit as st
import requests
from typing import Optional, Dict, List
import json

# Page config
st.set_page_config(
    page_title="Progress Dashboard - Adaptive Math",
    page_icon="📊",
    layout="wide",
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


def render_mastery_card(topic: str, data: Dict):
    """Render a mastery card for a topic."""
    mastery = data.get("mastery_score", 0.5)
    level = data.get("level", "Developing")
    attempts = data.get("attempts", 0)
    correct = data.get("correct", 0)
    accuracy = data.get("accuracy", 0)
    streak = data.get("streak", 0)

    # Color based on mastery level
    if mastery < 0.3:
        color = "🔴"
        bar_color = "red"
    elif mastery < 0.5:
        color = "🟠"
        bar_color = "orange"
    elif mastery < 0.7:
        color = "🟡"
        bar_color = "yellow"
    elif mastery < 0.85:
        color = "🟢"
        bar_color = "green"
    else:
        color = "⭐"
        bar_color = "green"

    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.markdown(f"### {color} {topic.title()}")
            st.progress(mastery, text=f"Mastery: {mastery:.0%}")

        with col2:
            st.metric("Level", level)
            st.caption(f"Accuracy: {accuracy:.0%}")

        with col3:
            st.metric("Questions", attempts)
            if streak > 0:
                st.success(f"🔥 {streak} streak")


def render_statistics(stats: Dict):
    """Render overall statistics."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Questions",
            stats.get("total_questions", 0),
            help="Total questions attempted"
        )

    with col2:
        accuracy = stats.get("overall_accuracy", 0)
        st.metric(
            "Overall Accuracy",
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
        avg_mastery = stats.get("average_mastery", 0.5)
        st.metric(
            "Average Mastery",
            f"{avg_mastery:.0%}",
            help="Average mastery across all topics"
        )


def render_recommendations(recommendations: List[Dict]):
    """Render topic recommendations."""
    if not recommendations:
        st.info("Great job! Keep practicing to maintain your skills.")
        return

    st.markdown("### 🎯 Recommended Topics")
    st.caption("Based on your performance, we suggest focusing on these topics:")

    for i, rec in enumerate(recommendations, 1):
        topic = rec.get("topic", "Unknown")
        mastery = rec.get("current_mastery", 0.5)
        reason = rec.get("reason", "Needs practice")

        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                st.markdown(f"**{i}. {topic.title()}**")
                st.caption(reason)

            with col2:
                st.progress(mastery, text=f"{mastery:.0%}")

            with col3:
                if st.button(f"Practice {topic}", key=f"practice_{topic}"):
                    st.session_state.selected_topic = topic
                    st.switch_page("pages/practice.py")


def main():
    st.title("📊 Progress Dashboard")
    st.markdown("Track your learning progress across all topics.")

    st.markdown("---")

    # Fetch data from API
    stats = api_request("GET", "/progress/statistics")
    mastery_data = api_request("GET", "/progress/mastery")
    recommendations = api_request("GET", "/progress/recommendations")

    # Check API connection
    if stats is None:
        st.warning("Cannot connect to the API server. Please ensure the backend is running.")
        st.code("python run_backend.py", language="bash")

        # Show placeholder data
        stats = {
            "total_questions": 0,
            "overall_accuracy": 0,
            "best_streak": 0,
            "average_mastery": 0.5,
        }
        mastery_data = []
        recommendations = []

    # Overall Statistics
    st.markdown("### 📈 Overall Statistics")
    render_statistics(stats)

    st.markdown("---")

    # Topic Mastery
    st.markdown("### 🎓 Topic Mastery")

    if mastery_data:
        # Create tabs for each topic
        topics = [m.get("topic_name", "Unknown") for m in mastery_data]

        for data in mastery_data:
            render_mastery_card(
                data.get("topic_name", "Unknown"),
                data
            )
            st.markdown("---")
    else:
        # Show default topics
        default_topics = [
            {"topic_name": "Arithmetic", "mastery_score": 0.5, "level": "Developing", "attempts": 0, "correct": 0, "accuracy": 0, "streak": 0},
            {"topic_name": "Fractions", "mastery_score": 0.5, "level": "Developing", "attempts": 0, "correct": 0, "accuracy": 0, "streak": 0},
            {"topic_name": "Percentages", "mastery_score": 0.5, "level": "Developing", "attempts": 0, "correct": 0, "accuracy": 0, "streak": 0},
            {"topic_name": "Algebra", "mastery_score": 0.5, "level": "Developing", "attempts": 0, "correct": 0, "accuracy": 0, "streak": 0},
            {"topic_name": "Geometry", "mastery_score": 0.5, "level": "Developing", "attempts": 0, "correct": 0, "accuracy": 0, "streak": 0},
            {"topic_name": "Ratios", "mastery_score": 0.5, "level": "Developing", "attempts": 0, "correct": 0, "accuracy": 0, "streak": 0},
        ]
        for data in default_topics:
            render_mastery_card(data["topic_name"], data)
            st.markdown("---")

    # Recommendations
    if recommendations:
        render_recommendations(recommendations)

    # Reset Progress
    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset All Progress", type="secondary"):
            result = api_request("POST", "/progress/reset")
            if result:
                st.success("Progress reset successfully!")
                st.rerun()
            else:
                st.error("Failed to reset progress.")


if __name__ == "__main__":
    main()
