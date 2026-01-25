"""
Answer Input Component.

Provides various input methods for math answers.
"""

import streamlit as st
from typing import Optional, Tuple, Any


def render_answer_form(
    answer_format: str = "integer",
    placeholder: str = "Type your answer...",
    key: str = "answer_form",
) -> Optional[str]:
    """
    Render a form for answer input.

    Args:
        answer_format: Expected answer format
        placeholder: Input placeholder text
        key: Unique key for the form

    Returns:
        Submitted answer or None
    """
    with st.form(key, clear_on_submit=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            # Choose appropriate input type
            if answer_format == "integer":
                user_input = st.text_input(
                    "Your Answer",
                    placeholder=placeholder,
                    key=f"{key}_input",
                )
            elif answer_format == "decimal":
                user_input = st.text_input(
                    "Your Answer",
                    placeholder="e.g., 3.14",
                    key=f"{key}_input",
                )
            elif answer_format == "fraction":
                user_input = st.text_input(
                    "Your Answer",
                    placeholder="e.g., 3/4",
                    key=f"{key}_input",
                    help="Enter as numerator/denominator",
                )
            elif answer_format == "ratio":
                user_input = st.text_input(
                    "Your Answer",
                    placeholder="e.g., 2:3",
                    key=f"{key}_input",
                    help="Enter as a:b",
                )
            elif answer_format == "percentage":
                user_input = st.text_input(
                    "Your Answer",
                    placeholder="e.g., 25",
                    key=f"{key}_input",
                    help="Enter number without % sign",
                )
            else:
                user_input = st.text_input(
                    "Your Answer",
                    placeholder=placeholder,
                    key=f"{key}_input",
                )

        with col2:
            st.write("")  # Vertical spacing
            submitted = st.form_submit_button(
                "Submit",
                type="primary",
                use_container_width=True,
            )

        if submitted and user_input:
            return user_input.strip()

    return None


def render_quick_answer(
    options: list,
    key_prefix: str = "quick",
) -> Optional[str]:
    """
    Render quick answer buttons for common values.

    Args:
        options: List of quick answer options
        key_prefix: Prefix for button keys

    Returns:
        Selected answer or None
    """
    st.caption("Quick answers:")

    cols = st.columns(len(options))
    selected = None

    for i, (col, option) in enumerate(zip(cols, options)):
        with col:
            if st.button(str(option), key=f"{key_prefix}_{i}", use_container_width=True):
                selected = str(option)

    return selected


def render_fraction_input(key: str = "fraction") -> Optional[str]:
    """
    Render specialized fraction input.

    Args:
        key: Unique key for inputs

    Returns:
        Fraction as string (e.g., "3/4") or None
    """
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        numerator = st.number_input(
            "Numerator",
            min_value=-999,
            max_value=999,
            value=0,
            step=1,
            key=f"{key}_num",
        )

    with col2:
        st.markdown("<div style='text-align: center; font-size: 24px; padding-top: 25px;'>-</div>",
                   unsafe_allow_html=True)

    with col3:
        denominator = st.number_input(
            "Denominator",
            min_value=1,
            max_value=999,
            value=1,
            step=1,
            key=f"{key}_den",
        )

    return f"{int(numerator)}/{int(denominator)}"


def render_ratio_input(key: str = "ratio") -> Optional[str]:
    """
    Render specialized ratio input.

    Args:
        key: Unique key for inputs

    Returns:
        Ratio as string (e.g., "2:3") or None
    """
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        first = st.number_input(
            "First part",
            min_value=1,
            max_value=999,
            value=1,
            step=1,
            key=f"{key}_first",
        )

    with col2:
        st.markdown("<div style='text-align: center; font-size: 24px; padding-top: 25px;'>:</div>",
                   unsafe_allow_html=True)

    with col3:
        second = st.number_input(
            "Second part",
            min_value=1,
            max_value=999,
            value=1,
            step=1,
            key=f"{key}_second",
        )

    return f"{int(first)}:{int(second)}"


def render_equation_input(
    variable: str = "x",
    key: str = "equation",
) -> Optional[str]:
    """
    Render input for equation solving.

    Args:
        variable: Variable being solved for
        key: Unique key for input

    Returns:
        Answer value or None
    """
    st.markdown(f"**{variable} = ?**")

    col1, col2 = st.columns([3, 1])

    with col1:
        value = st.text_input(
            f"Value of {variable}",
            placeholder=f"Enter value for {variable}",
            key=f"{key}_value",
            label_visibility="collapsed",
        )

    with col2:
        if st.button("Submit", key=f"{key}_submit", type="primary"):
            return value.strip() if value else None

    return None


def validate_input_format(
    user_input: str,
    expected_format: str,
) -> Tuple[bool, str]:
    """
    Validate input matches expected format.

    Args:
        user_input: User's input string
        expected_format: Expected format type

    Returns:
        Tuple of (is_valid, error_message)
    """
    user_input = user_input.strip()

    if not user_input:
        return False, "Please enter an answer"

    if expected_format == "integer":
        try:
            int(float(user_input))
            return True, ""
        except ValueError:
            return False, "Please enter a whole number"

    elif expected_format == "decimal":
        try:
            float(user_input)
            return True, ""
        except ValueError:
            return False, "Please enter a valid decimal number"

    elif expected_format == "fraction":
        if "/" not in user_input:
            return False, "Please enter as a fraction (e.g., 3/4)"
        parts = user_input.split("/")
        if len(parts) != 2:
            return False, "Invalid fraction format"
        try:
            int(parts[0].strip())
            int(parts[1].strip())
            return True, ""
        except ValueError:
            return False, "Numerator and denominator must be numbers"

    elif expected_format == "ratio":
        if ":" not in user_input:
            return False, "Please enter as a ratio (e.g., 2:3)"
        parts = user_input.split(":")
        if len(parts) != 2:
            return False, "Invalid ratio format"
        try:
            int(parts[0].strip())
            int(parts[1].strip())
            return True, ""
        except ValueError:
            return False, "Both parts of ratio must be numbers"

    elif expected_format == "percentage":
        cleaned = user_input.replace("%", "").strip()
        try:
            float(cleaned)
            return True, ""
        except ValueError:
            return False, "Please enter a valid percentage"

    return True, ""
