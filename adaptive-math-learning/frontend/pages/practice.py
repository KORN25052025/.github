"""
Practice Page - Question Solving Interface.

Core learning experience where students solve math problems.
"""

import streamlit as st
import requests
from typing import Optional, Dict, Any, List
import time

# Page config
st.set_page_config(
    page_title="Practice - Adaptive Math",
    page_icon="📝",
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
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "current_question": None,
        "question_start_time": None,
        "session_stats": {
            "attempted": 0,
            "correct": 0,
            "streak": 0,
            "best_streak": 0,
        },
        "selected_topic": None,
        "selected_subtopic": None,
        "show_explanation": False,
        "last_result": None,
        "difficulty_override": None,
        "with_story": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_topics() -> List[Dict]:
    """Fetch available topics."""
    result = api_request("GET", "/topics")
    if result:
        return result.get("topics", [])
    # Fallback topics
    return [
        {"name": "Arithmetic", "slug": "arithmetic", "subtopics": [
            {"name": "Addition", "slug": "addition"},
            {"name": "Subtraction", "slug": "subtraction"},
            {"name": "Multiplication", "slug": "multiplication"},
            {"name": "Division", "slug": "division"},
        ]},
        {"name": "Fractions", "slug": "fractions", "subtopics": [
            {"name": "Adding Fractions", "slug": "addition"},
            {"name": "Subtracting Fractions", "slug": "subtraction"},
            {"name": "Multiplying Fractions", "slug": "multiplication"},
            {"name": "Dividing Fractions", "slug": "division"},
        ]},
        {"name": "Percentages", "slug": "percentages", "subtopics": [
            {"name": "Finding Percentage", "slug": "find_percentage"},
            {"name": "Finding the Whole", "slug": "find_whole"},
            {"name": "Percentage Change", "slug": "percentage_change"},
        ]},
        {"name": "Algebra", "slug": "algebra", "subtopics": [
            {"name": "One-Step Equations", "slug": "one_step"},
            {"name": "Two-Step Equations", "slug": "two_step"},
            {"name": "Quadratic Equations", "slug": "quadratic"},
        ]},
        {"name": "Geometry", "slug": "geometry", "subtopics": [
            {"name": "Area", "slug": "area"},
            {"name": "Perimeter", "slug": "perimeter"},
            {"name": "Volume", "slug": "volume"},
        ]},
        {"name": "Ratios", "slug": "ratios", "subtopics": [
            {"name": "Simplifying Ratios", "slug": "simplify"},
            {"name": "Solving Proportions", "slug": "solve_proportion"},
            {"name": "Word Problems", "slug": "word_problem"},
        ]},
    ]


def generate_question(topic: str, subtopic: str = None, difficulty: float = None, with_story: bool = False) -> Optional[Dict]:
    """Generate a new question."""
    data = {
        "topic": topic,
        "with_story": with_story,
    }
    if subtopic:
        data["subtopic"] = subtopic
    if difficulty is not None:
        data["difficulty"] = difficulty

    return api_request("POST", "/questions/generate", data)


def submit_answer(question_id: str, user_answer: str) -> Optional[Dict]:
    """Submit an answer for validation."""
    data = {
        "question_id": question_id,
        "user_answer": user_answer,
    }

    # Calculate response time
    if st.session_state.question_start_time:
        response_time = int((time.time() - st.session_state.question_start_time) * 1000)
        data["response_time_ms"] = response_time

    return api_request("POST", "/answers/validate", data)


def render_topic_selector():
    """Render topic and subtopic selection."""
    topics = get_topics()

    col1, col2 = st.columns(2)

    with col1:
        topic_names = ["Select a topic..."] + [t["name"] for t in topics]
        selected_idx = st.selectbox(
            "Topic",
            range(len(topic_names)),
            format_func=lambda i: topic_names[i],
            key="topic_select"
        )

        if selected_idx > 0:
            st.session_state.selected_topic = topics[selected_idx - 1]["slug"]
            selected_topic_data = topics[selected_idx - 1]
        else:
            st.session_state.selected_topic = None
            selected_topic_data = None

    with col2:
        if selected_topic_data and "subtopics" in selected_topic_data:
            subtopics = selected_topic_data.get("subtopics", [])
            subtopic_names = ["All subtopics"] + [s["name"] for s in subtopics]
            subtopic_idx = st.selectbox(
                "Subtopic",
                range(len(subtopic_names)),
                format_func=lambda i: subtopic_names[i],
                key="subtopic_select"
            )

            if subtopic_idx > 0:
                st.session_state.selected_subtopic = subtopics[subtopic_idx - 1]["slug"]
            else:
                st.session_state.selected_subtopic = None
        else:
            st.selectbox("Subtopic", ["Select topic first"], disabled=True)
            st.session_state.selected_subtopic = None


def render_difficulty_controls():
    """Render difficulty control options."""
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)

        with col1:
            difficulty_mode = st.radio(
                "Difficulty Mode",
                ["Adaptive", "Manual"],
                help="Adaptive mode adjusts based on your performance"
            )

            if difficulty_mode == "Manual":
                st.session_state.difficulty_override = st.slider(
                    "Difficulty Level",
                    0.0, 1.0, 0.5,
                    help="0 = Easy, 1 = Hard"
                )
            else:
                st.session_state.difficulty_override = None

        with col2:
            st.session_state.with_story = st.checkbox(
                "Include Story Problems",
                value=st.session_state.with_story,
                help="Generate word problems with stories (requires AI)"
            )


def render_session_stats():
    """Render current session statistics."""
    stats = st.session_state.session_stats

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Questions", stats["attempted"])

    with col2:
        accuracy = (stats["correct"] / stats["attempted"] * 100) if stats["attempted"] > 0 else 0
        st.metric("Accuracy", f"{accuracy:.0f}%")

    with col3:
        st.metric("Current Streak", stats["streak"])

    with col4:
        st.metric("Best Streak", stats["best_streak"])


def render_question(question: Dict):
    """Render the current question."""
    st.markdown("---")

    # Question header
    difficulty = question.get("difficulty_score", 0.5)
    difficulty_label = get_difficulty_label(difficulty)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Question")
    with col2:
        st.caption(f"Difficulty: {difficulty_label}")

    # Story text (if available)
    if question.get("story_text"):
        st.info(question["story_text"])

    # Main expression/question
    expression = question.get("expression", "")
    question_text = question.get("question_text", "")

    if question_text:
        st.markdown(f"**{question_text}**")

    # Display mathematical expression
    if expression:
        # Check if it's a solvable equation
        if "=" in expression and "x" in expression.lower():
            st.latex(f"\\text{{Solve: }} {format_latex(expression)}")
        else:
            st.latex(format_latex(expression))

    # Hint about answer format
    answer_format = question.get("answer_format", "integer")
    st.caption(f"Answer format: {get_format_hint(answer_format)}")


def format_latex(expression: str) -> str:
    """Convert expression to LaTeX format."""
    # Basic conversions
    result = expression
    result = result.replace("*", " \\times ")
    result = result.replace("/", " \\div ")
    result = result.replace("sqrt", "\\sqrt")
    result = result.replace("pi", "\\pi")
    return result


def get_difficulty_label(difficulty: float) -> str:
    """Get human-readable difficulty label."""
    if difficulty < 0.2:
        return "Very Easy"
    elif difficulty < 0.4:
        return "Easy"
    elif difficulty < 0.6:
        return "Medium"
    elif difficulty < 0.8:
        return "Hard"
    else:
        return "Very Hard"


def get_format_hint(answer_format: str) -> str:
    """Get hint for expected answer format."""
    hints = {
        "integer": "whole number (e.g., 42)",
        "decimal": "decimal number (e.g., 3.14)",
        "fraction": "fraction (e.g., 3/4)",
        "ratio": "ratio (e.g., 2:3)",
        "percentage": "percentage (e.g., 25 or 25%)",
        "expression": "mathematical expression",
    }
    return hints.get(answer_format, "number")


def render_answer_input():
    """Render the answer input form."""
    with st.form("answer_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            user_answer = st.text_input(
                "Your Answer",
                placeholder="Type your answer here...",
                key="answer_input"
            )

        with col2:
            st.write("")  # Spacing
            submit = st.form_submit_button("Submit", type="primary", use_container_width=True)

        if submit and user_answer:
            return user_answer

    return None


def render_feedback(result: Dict):
    """Render answer feedback."""
    is_correct = result.get("is_correct", False)
    feedback = result.get("feedback", "")
    correct_answer = result.get("correct_answer", "")

    if is_correct:
        st.success(f"**{feedback}**")
    else:
        st.error(f"**{feedback}**")

        # Show hint if available
        if result.get("hint"):
            st.warning(f"Hint: {result['hint']}")

    # Show explanation if requested
    if st.session_state.show_explanation or not is_correct:
        render_explanation(result)

    # Mastery update
    if result.get("new_mastery"):
        mastery = result["new_mastery"]
        st.caption(f"Topic mastery: {mastery:.0%}")


def render_explanation(result: Dict):
    """Render step-by-step explanation."""
    explanation = result.get("explanation")
    steps = result.get("steps", [])

    if explanation or steps:
        with st.expander("Step-by-Step Solution", expanded=not result.get("is_correct", False)):
            if explanation:
                st.markdown(f"**{explanation}**")

            if steps:
                st.markdown("---")
                for i, step in enumerate(steps, 1):
                    st.markdown(f"{step}")


def render_multiple_choice(question: Dict):
    """Render multiple choice options if available."""
    distractors = question.get("distractors", [])
    correct = question.get("correct_answer")

    if not distractors:
        return None

    # Combine correct answer with distractors
    import random
    options = [correct] + distractors[:3]
    random.shuffle(options)

    st.markdown("**Choose your answer:**")

    cols = st.columns(len(options))
    selected = None

    for i, (col, option) in enumerate(zip(cols, options)):
        with col:
            if st.button(str(option), key=f"mc_{i}", use_container_width=True):
                selected = str(option)

    return selected


def main():
    init_session_state()

    st.title("Practice Mode")
    st.markdown("Solve math problems and improve your skills!")

    # Topic selection
    render_topic_selector()

    # Difficulty controls
    render_difficulty_controls()

    st.markdown("---")

    # Session stats
    render_session_stats()

    # Check if topic is selected
    if not st.session_state.selected_topic:
        st.info("Please select a topic to start practicing.")
        return

    # Generate new question button
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("New Question", type="primary", use_container_width=True):
            question = generate_question(
                topic=st.session_state.selected_topic,
                subtopic=st.session_state.selected_subtopic,
                difficulty=st.session_state.difficulty_override,
                with_story=st.session_state.with_story
            )

            if question:
                st.session_state.current_question = question
                st.session_state.question_start_time = time.time()
                st.session_state.last_result = None
                st.rerun()
            else:
                st.error("Failed to generate question. Is the backend running?")

    with col2:
        st.session_state.show_explanation = st.checkbox(
            "Always show explanation",
            value=st.session_state.show_explanation
        )

    with col3:
        if st.button("Reset Session"):
            st.session_state.session_stats = {
                "attempted": 0,
                "correct": 0,
                "streak": 0,
                "best_streak": 0,
            }
            st.session_state.current_question = None
            st.session_state.last_result = None
            st.rerun()

    # Display current question
    if st.session_state.current_question:
        question = st.session_state.current_question
        render_question(question)

        # Show last result if available
        if st.session_state.last_result:
            render_feedback(st.session_state.last_result)

            # Next question button after answering
            if st.button("Next Question", type="primary"):
                new_question = generate_question(
                    topic=st.session_state.selected_topic,
                    subtopic=st.session_state.selected_subtopic,
                    difficulty=st.session_state.difficulty_override,
                    with_story=st.session_state.with_story
                )

                if new_question:
                    st.session_state.current_question = new_question
                    st.session_state.question_start_time = time.time()
                    st.session_state.last_result = None
                    st.rerun()
        else:
            # Answer input
            user_answer = render_answer_input()

            if user_answer:
                result = submit_answer(
                    question_id=question.get("question_id", ""),
                    user_answer=user_answer
                )

                if result:
                    st.session_state.last_result = result

                    # Update session stats
                    stats = st.session_state.session_stats
                    stats["attempted"] += 1

                    if result.get("is_correct"):
                        stats["correct"] += 1
                        stats["streak"] += 1
                        stats["best_streak"] = max(stats["streak"], stats["best_streak"])
                    else:
                        stats["streak"] = 0

                    st.rerun()
                else:
                    # Fallback validation (if API unavailable)
                    correct_answer = question.get("correct_answer")
                    is_correct = str(user_answer).strip() == str(correct_answer).strip()

                    st.session_state.last_result = {
                        "is_correct": is_correct,
                        "feedback": "Correct!" if is_correct else f"Incorrect. The answer was {correct_answer}.",
                        "correct_answer": correct_answer,
                    }

                    stats = st.session_state.session_stats
                    stats["attempted"] += 1
                    if is_correct:
                        stats["correct"] += 1
                        stats["streak"] += 1
                        stats["best_streak"] = max(stats["streak"], stats["best_streak"])
                    else:
                        stats["streak"] = 0

                    st.rerun()
    else:
        st.info("Click 'New Question' to start practicing!")

        # Show topic info
        topic = st.session_state.selected_topic
        st.markdown(f"**Selected Topic:** {topic.title()}")
        if st.session_state.selected_subtopic:
            st.markdown(f"**Subtopic:** {st.session_state.selected_subtopic.replace('_', ' ').title()}")


if __name__ == "__main__":
    main()
