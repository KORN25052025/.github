"""
Question Display Component.

Renders math questions with various formats and styles.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import random


def render_question(
    question: Dict[str, Any],
    show_difficulty: bool = True,
    show_hints: bool = False,
) -> None:
    """
    Render a complete question display.

    Args:
        question: Question data dictionary
        show_difficulty: Whether to show difficulty indicator
        show_hints: Whether to show hints about the question
    """
    # Header with difficulty
    col1, col2 = st.columns([3, 1])

    with col1:
        question_text = question.get("question_text", "")
        if question_text:
            st.markdown(f"### {question_text}")
        else:
            st.markdown("### Solve:")

    with col2:
        if show_difficulty:
            difficulty = question.get("difficulty_score", 0.5)
            label = get_difficulty_label(difficulty)
            color = get_difficulty_color(difficulty)
            st.markdown(f"**Difficulty:** :{color}[{label}]")

    # Story text (if available)
    if question.get("story_text"):
        with st.container():
            st.info(question["story_text"])

    # Main expression
    expression = question.get("expression", "")
    if expression:
        render_expression(expression, question.get("question_type", ""))

    # Answer format hint
    answer_format = question.get("answer_format", "integer")
    st.caption(f"Enter your answer as: {get_format_description(answer_format)}")

    # Additional hints
    if show_hints and question.get("hint"):
        with st.expander("Need a hint?"):
            st.markdown(question["hint"])


def render_expression(
    expression: str,
    question_type: str = "",
    size: str = "large",
) -> None:
    """
    Render a mathematical expression.

    Args:
        expression: Mathematical expression string
        question_type: Type of question for formatting hints
        size: Display size ("small", "medium", "large")
    """
    latex_expr = to_latex(expression, question_type)

    if size == "large":
        st.latex(latex_expr)
    elif size == "medium":
        st.markdown(f"$${latex_expr}$$")
    else:
        st.markdown(f"${latex_expr}$")


def render_multiple_choice(
    question: Dict[str, Any],
    key_prefix: str = "mc",
) -> Optional[str]:
    """
    Render multiple choice options.

    Args:
        question: Question data with distractors
        key_prefix: Prefix for button keys

    Returns:
        Selected answer or None
    """
    distractors = question.get("distractors", [])
    correct = question.get("correct_answer")

    if not distractors or not correct:
        return None

    # Combine and shuffle options
    options = [correct] + distractors[:3]
    random.shuffle(options)

    st.markdown("**Choose your answer:**")

    # Create columns for options
    cols = st.columns(len(options))
    selected = None

    for i, (col, option) in enumerate(zip(cols, options)):
        with col:
            if st.button(
                format_option(option, question.get("answer_format", "integer")),
                key=f"{key_prefix}_{i}",
                use_container_width=True,
            ):
                selected = str(option)

    return selected


def to_latex(expression: str, question_type: str = "") -> str:
    """
    Convert expression to LaTeX format.

    Args:
        expression: Mathematical expression
        question_type: Type for specialized formatting

    Returns:
        LaTeX formatted string
    """
    result = expression

    # Handle fractions
    if "/" in result and question_type == "fractions":
        # Try to convert a/b to LaTeX fraction
        parts = result.split("/")
        if len(parts) == 2:
            try:
                num, den = parts[0].strip(), parts[1].strip()
                if num.lstrip("-").isdigit() and den.isdigit():
                    result = f"\frac{{{num}}}{{{den}}}"
            except:
                pass

    # Handle operators
    result = result.replace("*", " \times ")
    result = result.replace("/", " \div ")
    
    # Handle special symbols
    result = result.replace("sqrt", "\sqrt")
    result = result.replace("pi", "\pi")
    result = result.replace(">=", "\geq")
    result = result.replace("<=", "\leq")
    result = result.replace("!=", "\neq")

    # Handle exponents
    import re
    result = re.sub(r'\^(\d+)', r'^{\1}', result)
    result = re.sub(r'\^([a-zA-Z])', r'^{\1}', result)

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


def get_difficulty_color(difficulty: float) -> str:
    """Get color for difficulty level."""
    if difficulty < 0.2:
        return "green"
    elif difficulty < 0.4:
        return "green"
    elif difficulty < 0.6:
        return "orange"
    elif difficulty < 0.8:
        return "red"
    else:
        return "red"


def get_format_description(answer_format: str) -> str:
    """Get description of expected answer format."""
    descriptions = {
        "integer": "a whole number (e.g., 42)",
        "decimal": "a decimal number (e.g., 3.14)",
        "fraction": "a fraction (e.g., 3/4)",
        "ratio": "a ratio (e.g., 2:3)",
        "percentage": "a percentage (e.g., 25 or 25%)",
        "expression": "a mathematical expression",
    }
    return descriptions.get(answer_format, "a number")


def format_option(option: Any, answer_format: str) -> str:
    """Format an option for display."""
    if answer_format == "fraction":
        return str(option)
    elif answer_format == "decimal":
        try:
            return f"{float(option):.2f}"
        except:
            return str(option)
    elif answer_format == "percentage":
        return f"{option}%"
    elif answer_format == "ratio":
        return str(option)
    else:
        return str(option)
