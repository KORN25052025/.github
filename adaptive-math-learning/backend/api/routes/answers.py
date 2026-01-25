"""
Answer validation routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ...database import get_db
from ...schemas import AnswerRequest, AnswerResponse

from adaptation.mastery_tracker import MasteryTracker

router = APIRouter()

# In-memory storage for questions (temporary; would use DB in production)
_question_cache: Dict[str, Dict[str, Any]] = {}

# Mastery tracker
mastery_tracker = MasteryTracker()


def store_question(question_id: str, data: Dict[str, Any]):
    """Store question data for later validation."""
    _question_cache[question_id] = data


def get_question_data(question_id: str) -> Dict[str, Any]:
    """Retrieve stored question data."""
    return _question_cache.get(question_id)


@router.post("/answers/validate", response_model=AnswerResponse)
async def validate_answer(
    request: AnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a user's answer.

    Updates mastery score and returns feedback.
    """
    # For now, we'll use a simple approach since we don't have
    # the full question stored. In production, this would query the DB.

    # Parse user answer
    user_answer = request.user_answer.strip()

    # Get question data from cache
    question_data = get_question_data(request.question_id)

    if not question_data:
        # If no cached data, we can't validate properly
        # This is a limitation of the MVP; production would use DB
        return AnswerResponse(
            is_correct=False,
            user_answer=user_answer,
            correct_answer="Unknown",
            feedback="Question not found. Please try generating a new question.",
            streak=0,
        )

    # Get correct answer
    correct_answer = str(question_data.get("correct_answer", ""))
    topic_key = question_data.get("topic", "arithmetic")

    # Compare answers
    try:
        # Try numeric comparison
        user_val = float(user_answer)
        correct_val = float(correct_answer)
        is_correct = abs(user_val - correct_val) < 0.001
    except ValueError:
        # String comparison
        is_correct = user_answer.lower() == correct_answer.lower()

    # Update mastery
    old_mastery = mastery_tracker.get_mastery(topic_key)
    new_mastery = mastery_tracker.update(
        topic_key,
        is_correct,
        response_time_ms=request.response_time_ms,
    )
    mastery_change = new_mastery - old_mastery

    # Get current streak
    record = mastery_tracker.get_record(topic_key)
    streak = record.streak

    # Generate feedback
    if is_correct:
        feedback = "Correct! Great job!"
        if streak >= 5:
            feedback = f"Correct! You're on a {streak}-question streak!"
        elif streak >= 3:
            feedback = "Correct! Keep it up!"
    else:
        feedback = f"Not quite. The correct answer is {correct_answer}."
        if streak == 0 and record.attempts > 1:
            feedback += " Don't give up - you'll get the next one!"

    return AnswerResponse(
        is_correct=is_correct,
        user_answer=user_answer,
        correct_answer=correct_answer,
        feedback=feedback,
        new_mastery_score=new_mastery,
        mastery_change=mastery_change,
        streak=streak,
    )


@router.post("/answers/store")
async def store_answer_data(question_id: str, correct_answer: str, topic: str = "arithmetic"):
    """
    Store question data for validation.

    This is called after generating a question to enable answer validation.
    """
    store_question(question_id, {
        "correct_answer": correct_answer,
        "topic": topic,
    })
    return {"status": "stored"}
