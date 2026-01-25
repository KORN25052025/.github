"""
Feedback Component.

Displays answer feedback, explanations, and hints.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import random


def render_feedback(result: Dict[str, Any], show_mastery: bool = True) -> None:
    """Render complete answer feedback."""
    is_correct = result.get("is_correct", False)
    feedback_text = result.get("feedback", "")
    
    if is_correct:
        st.success(f"**{feedback_text}**")
    else:
        st.error(f"**{feedback_text}**")
    
    if not is_correct and result.get("hint"):
        with st.expander("Hint"):
            st.markdown(f"**{result[\"hint\"]}**")
    
    if result.get("explanation") or result.get("steps"):
        render_explanation(result.get("explanation"), result.get("steps", []), not is_correct)
    
    if show_mastery and result.get("new_mastery") is not None:
        render_mastery_update(result.get("new_mastery", 0), result.get("old_mastery"))


def render_explanation(explanation: Optional[str] = None, steps: Optional[List[str]] = None, expanded: bool = True) -> None:
    """Render step-by-step explanation."""
    if not explanation and not steps:
        return
    
    with st.expander("Step-by-Step Solution", expanded=expanded):
        if explanation:
            st.markdown(f"**{explanation}**")
            st.markdown("---")
        if steps:
            for i, step in enumerate(steps, 1):
                st.markdown(step if step.startswith(("Step", "Given")) else f"**Step {i}:** {step}")


def render_hint(hint: str, expanded: bool = False) -> None:
    """Render a hint."""
    with st.expander("Hint", expanded=expanded):
        st.markdown(f"**{hint}**")


def render_mastery_update(new_mastery: float, old_mastery: Optional[float] = None) -> None:
    """Render mastery level update."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(new_mastery)
    with col2:
        if old_mastery is not None:
            delta = new_mastery - old_mastery
            st.metric("Mastery", f"{new_mastery:.0%}", f"{delta:+.0%}" if delta != 0 else None)
        else:
            st.metric("Mastery", f"{new_mastery:.0%}")
    st.caption(f"Level: {get_mastery_level(new_mastery)}")


def get_mastery_level(mastery: float) -> str:
    """Get mastery level name."""
    if mastery < 0.2: return "Novice"
    elif mastery < 0.4: return "Beginner"
    elif mastery < 0.6: return "Developing"
    elif mastery < 0.8: return "Proficient"
    else: return "Expert"


def render_streak_notification(streak: int, best_streak: int) -> None:
    """Render streak notification."""
    if streak >= 3:
        st.success(f"You are on a **{streak}** answer streak!")
        if streak == best_streak and streak >= 5:
            st.balloons()


def render_progress_summary(attempted: int, correct: int, streak: int) -> None:
    """Render session progress summary."""
    col1, col2, col3 = st.columns(3)
    with col1:
        accuracy = (correct / attempted * 100) if attempted > 0 else 0
        st.metric("Accuracy", f"{accuracy:.0f}%")
    with col2:
        st.metric("Correct", f"{correct}/{attempted}")
    with col3:
        st.metric("Streak", streak)


def render_encouragement(is_correct: bool, streak: int = 0) -> Optional[str]:
    """Generate encouragement message."""
    if is_correct:
        if streak >= 5: msg = "Amazing! Keep going!"
        elif streak >= 3: msg = "Great streak!"
        else: msg = random.choice(["Correct!", "Well done!", "Great job!"])
        if streak >= 3: st.success(msg)
    else:
        msg = random.choice(["Keep trying!", "Good effort!"])
        st.info(msg)
    return msg

