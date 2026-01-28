"""
Topics Page - Browse and Select Math Topics.

Displays all available math topics with their descriptions and difficulty levels.
"""

import streamlit as st
import requests
from typing import Optional, Dict, List

# Page config
st.set_page_config(
    page_title="Topics - Adaptive Math",
    page_icon="📚",
    layout="wide",
)

import os
try:
    from frontend.theme import API_URL
except ImportError:
    API_URL = os.environ.get("API_URL", "http://localhost:8000/api/v1")


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


def get_topics() -> List[Dict]:
    """Fetch topics from API or return defaults."""
    result = api_request("GET", "/topics")
    if result:
        # API returns a list directly, not {"topics": [...]}
        if isinstance(result, list):
            return result
        return result.get("topics", [])

    # Fallback to default topics
    return [
        {
            "name": "Arithmetic",
            "slug": "arithmetic",
            "description": "Basic arithmetic operations: addition, subtraction, multiplication, division",
            "grade_range_start": 1,
            "grade_range_end": 6,
            "icon": "➕",
            "color": "#4CAF50",
            "subtopics": [
                {"name": "Addition", "slug": "addition", "difficulty_base": 20},
                {"name": "Subtraction", "slug": "subtraction", "difficulty_base": 25},
                {"name": "Multiplication", "slug": "multiplication", "difficulty_base": 40},
                {"name": "Division", "slug": "division", "difficulty_base": 50},
                {"name": "Mixed Operations", "slug": "mixed", "difficulty_base": 60},
            ]
        },
        {
            "name": "Fractions",
            "slug": "fractions",
            "description": "Operations with fractions: addition, subtraction, multiplication, division",
            "grade_range_start": 3,
            "grade_range_end": 8,
            "icon": "½",
            "color": "#2196F3",
            "subtopics": [
                {"name": "Adding Fractions", "slug": "addition", "difficulty_base": 40},
                {"name": "Subtracting Fractions", "slug": "subtraction", "difficulty_base": 45},
                {"name": "Multiplying Fractions", "slug": "multiplication", "difficulty_base": 50},
                {"name": "Dividing Fractions", "slug": "division", "difficulty_base": 55},
            ]
        },
        {
            "name": "Percentages",
            "slug": "percentages",
            "description": "Working with percentages: finding percentages, discounts, tax calculations",
            "grade_range_start": 5,
            "grade_range_end": 9,
            "icon": "%",
            "color": "#FF9800",
            "subtopics": [
                {"name": "Finding Percentage", "slug": "find_percentage", "difficulty_base": 35},
                {"name": "Finding the Whole", "slug": "find_whole", "difficulty_base": 45},
                {"name": "Finding What Percent", "slug": "find_percent", "difficulty_base": 50},
                {"name": "Percentage Change", "slug": "percentage_change", "difficulty_base": 55},
                {"name": "Discounts", "slug": "discount", "difficulty_base": 50},
                {"name": "Tax Calculations", "slug": "tax", "difficulty_base": 50},
            ]
        },
        {
            "name": "Algebra",
            "slug": "algebra",
            "description": "Algebraic equations and expressions",
            "grade_range_start": 6,
            "grade_range_end": 12,
            "icon": "x",
            "color": "#9C27B0",
            "subtopics": [
                {"name": "One-Step Equations", "slug": "one_step", "difficulty_base": 30},
                {"name": "Two-Step Equations", "slug": "two_step", "difficulty_base": 45},
                {"name": "Multi-Step Equations", "slug": "multi_step", "difficulty_base": 60},
                {"name": "Variables on Both Sides", "slug": "both_sides", "difficulty_base": 70},
                {"name": "Quadratic Equations", "slug": "quadratic", "difficulty_base": 80},
            ]
        },
        {
            "name": "Geometry",
            "slug": "geometry",
            "description": "Geometric calculations: area, perimeter, volume, Pythagorean theorem",
            "grade_range_start": 3,
            "grade_range_end": 12,
            "icon": "△",
            "color": "#E91E63",
            "subtopics": [
                {"name": "Perimeter", "slug": "perimeter", "difficulty_base": 25},
                {"name": "Area of 2D Shapes", "slug": "area", "difficulty_base": 35},
                {"name": "Circumference", "slug": "circumference", "difficulty_base": 45},
                {"name": "Volume", "slug": "volume", "difficulty_base": 50},
                {"name": "Surface Area", "slug": "surface_area", "difficulty_base": 60},
                {"name": "Pythagorean Theorem", "slug": "pythagorean", "difficulty_base": 55},
            ]
        },
        {
            "name": "Ratios",
            "slug": "ratios",
            "description": "Ratios and proportions",
            "grade_range_start": 5,
            "grade_range_end": 9,
            "icon": ":",
            "color": "#00BCD4",
            "subtopics": [
                {"name": "Simplifying Ratios", "slug": "simplify", "difficulty_base": 30},
                {"name": "Equivalent Ratios", "slug": "equivalent", "difficulty_base": 40},
                {"name": "Solving Proportions", "slug": "solve_proportion", "difficulty_base": 50},
                {"name": "Ratio Word Problems", "slug": "word_problem", "difficulty_base": 55},
                {"name": "Part-to-Whole", "slug": "part_to_whole", "difficulty_base": 60},
                {"name": "Scale Problems", "slug": "scale", "difficulty_base": 60},
            ]
        },
    ]


def get_mastery_data() -> Dict[str, Dict]:
    """Fetch mastery data from API."""
    result = api_request("GET", "/progress/mastery")
    if result:
        return {item["topic_name"].lower(): item for item in result}
    return {}


def render_topic_card(topic: Dict, mastery: Dict):
    """Render a single topic card."""
    name = topic["name"]
    slug = topic["slug"]
    description = topic.get("description", "")
    grade_start = topic.get("grade_range_start", 1)
    grade_end = topic.get("grade_range_end", 12)
    subtopics = topic.get("subtopics", [])
    icon = topic.get("icon", "📘")

    # Get mastery for this topic
    topic_mastery = mastery.get(slug.lower(), {})
    mastery_score = topic_mastery.get("mastery_score", 0.5)
    attempts = topic_mastery.get("attempts", 0)

    # Determine mastery color
    if mastery_score < 0.3:
        mastery_color = "red"
        mastery_label = "Needs Practice"
    elif mastery_score < 0.5:
        mastery_color = "orange"
        mastery_label = "Developing"
    elif mastery_score < 0.7:
        mastery_color = "yellow"
        mastery_label = "Progressing"
    elif mastery_score < 0.85:
        mastery_color = "green"
        mastery_label = "Proficient"
    else:
        mastery_color = "green"
        mastery_label = "Mastered"

    with st.container():
        st.markdown(f"### {icon} {name}")
        st.caption(f"Grades {grade_start}-{grade_end}")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(description)

            # Subtopics
            if subtopics:
                subtopic_names = [s["name"] for s in subtopics[:5]]
                if len(subtopics) > 5:
                    subtopic_names.append(f"and {len(subtopics) - 5} more...")
                st.caption(f"**Subtopics:** {', '.join(subtopic_names)}")

        with col2:
            # Mastery progress
            st.progress(mastery_score)
            st.caption(f"{mastery_label} ({mastery_score:.0%})")
            if attempts > 0:
                st.caption(f"{attempts} questions attempted")

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(f"Practice {name}", key=f"practice_{slug}", use_container_width=True):
                st.session_state.selected_topic = slug
                st.switch_page("pages/practice.py")

        with col2:
            if st.button(f"View Details", key=f"details_{slug}", use_container_width=True):
                st.session_state.expanded_topic = slug

        with col3:
            if st.button(f"Quick Quiz", key=f"quiz_{slug}", use_container_width=True):
                st.session_state.quiz_topic = slug
                st.session_state.selected_topic = slug
                st.switch_page("pages/practice.py")

        st.markdown("---")


def render_topic_details(topic: Dict, mastery: Dict):
    """Render detailed view of a topic with all subtopics."""
    name = topic["name"]
    slug = topic["slug"]
    subtopics = topic.get("subtopics", [])

    st.markdown(f"## {name} - Detailed View")

    # Back button
    if st.button("Back to Topics"):
        st.session_state.expanded_topic = None
        st.rerun()

    st.markdown("---")

    # Description
    st.markdown(f"**{topic.get('description', '')}**")
    st.markdown(f"**Grade Range:** {topic.get('grade_range_start', 1)} - {topic.get('grade_range_end', 12)}")

    st.markdown("---")
    st.markdown("### Subtopics")

    # Display each subtopic
    for subtopic in subtopics:
        sub_name = subtopic["name"]
        sub_slug = subtopic["slug"]
        difficulty_base = subtopic.get("difficulty_base", 50)

        # Calculate difficulty level
        if difficulty_base < 30:
            difficulty_label = "Easy"
            difficulty_color = "green"
        elif difficulty_base < 50:
            difficulty_label = "Medium"
            difficulty_color = "orange"
        elif difficulty_base < 70:
            difficulty_label = "Hard"
            difficulty_color = "red"
        else:
            difficulty_label = "Advanced"
            difficulty_color = "purple"

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"**{sub_name}**")

        with col2:
            st.caption(f"Difficulty: {difficulty_label}")

        with col3:
            if st.button("Practice", key=f"sub_practice_{slug}_{sub_slug}", use_container_width=True):
                st.session_state.selected_topic = slug
                st.session_state.selected_subtopic = sub_slug
                st.switch_page("pages/practice.py")

    st.markdown("---")

    # Learning tips
    st.markdown("### Learning Tips")
    tips = get_learning_tips(slug)
    for tip in tips:
        st.markdown(f"- {tip}")


def get_learning_tips(topic_slug: str) -> List[str]:
    """Get learning tips for a topic."""
    tips = {
        "arithmetic": [
            "Practice mental math daily to build speed and accuracy",
            "Learn multiplication tables up to 12x12",
            "Use estimation to check your answers",
            "Break complex problems into smaller steps",
        ],
        "fractions": [
            "Always simplify fractions to their lowest terms",
            "Remember: dividing by a fraction is the same as multiplying by its reciprocal",
            "Visualize fractions as parts of a whole",
            "Practice finding common denominators",
        ],
        "percentages": [
            "Remember: percent means 'per hundred'",
            "To find X% of a number, multiply by X/100",
            "Use benchmarks: 10% = divide by 10, 50% = divide by 2",
            "Percentages and decimals are interchangeable",
        ],
        "algebra": [
            "Whatever you do to one side of an equation, do to the other",
            "Isolate the variable step by step",
            "Check your solution by substituting back",
            "Use inverse operations to solve equations",
        ],
        "geometry": [
            "Memorize key formulas: A = l x w (rectangle), A = 1/2 x b x h (triangle)",
            "Draw diagrams to visualize problems",
            "Label all given information on your diagram",
            "Remember: perimeter is around, area is inside",
        ],
        "ratios": [
            "Ratios can be written as fractions",
            "Simplify ratios by dividing both parts by their GCD",
            "In proportions, cross-multiply to solve",
            "Unit rates help compare different quantities",
        ],
    }
    return tips.get(topic_slug, ["Practice regularly", "Review your mistakes", "Ask for help when needed"])


def render_grade_filter():
    """Render grade level filter."""
    st.sidebar.markdown("### Filter by Grade")

    grade_range = st.sidebar.slider(
        "Grade Level",
        min_value=1,
        max_value=12,
        value=(1, 12),
        help="Filter topics by grade range"
    )

    return grade_range


def main():
    st.title("Math Topics")
    st.markdown("Explore and practice different math topics")

    # Sidebar filters
    grade_range = render_grade_filter()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Actions")

    if st.sidebar.button("Random Practice", use_container_width=True):
        import random
        topics = get_topics()
        topic = random.choice(topics)
        st.session_state.selected_topic = topic["slug"]
        st.switch_page("pages/practice.py")

    if st.sidebar.button("View Progress", use_container_width=True):
        st.switch_page("pages/progress.py")

    # Get data
    topics = get_topics()
    mastery = get_mastery_data()

    # Check if viewing details
    if hasattr(st.session_state, 'expanded_topic') and st.session_state.expanded_topic:
        topic = next((t for t in topics if t["slug"] == st.session_state.expanded_topic), None)
        if topic:
            render_topic_details(topic, mastery)
            return

    # Filter topics by grade
    min_grade, max_grade = grade_range
    filtered_topics = [
        t for t in topics
        if t.get("grade_range_start", 1) <= max_grade and t.get("grade_range_end", 12) >= min_grade
    ]

    # Summary stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Topics", len(filtered_topics))

    with col2:
        total_subtopics = sum(len(t.get("subtopics", [])) for t in filtered_topics)
        st.metric("Total Subtopics", total_subtopics)

    with col3:
        avg_mastery = sum(mastery.get(t["slug"].lower(), {}).get("mastery_score", 0.5) for t in filtered_topics) / max(len(filtered_topics), 1)
        st.metric("Average Mastery", f"{avg_mastery:.0%}")

    st.markdown("---")

    # Display topics
    for topic in filtered_topics:
        render_topic_card(topic, mastery)


if __name__ == "__main__":
    main()
