"""
Question generation routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from ...database import get_db
from ...models import Topic, Subtopic, Question, LearningSession
from ...schemas import QuestionRequest, QuestionResponse

from question_engine.base import QuestionType, OperationType
from question_engine.registry import registry
from adaptation.bkt_tracker import BKTTracker

router = APIRouter()

# BKT-based mastery tracker (Bayesian Knowledge Tracing)
mastery_tracker = BKTTracker()


@router.post("/questions/generate", response_model=QuestionResponse)
async def generate_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a new question based on parameters.

    Uses mastery-based difficulty if not specified.
    """
    # Determine topic
    topic = None
    topic_name = None

    if request.topic_id:
        topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
    elif request.topic_slug:
        topic = db.query(Topic).filter(Topic.slug == request.topic_slug).first()

    if topic:
        topic_name = topic.name

    # Determine question type from topic or request
    question_type = QuestionType.ARITHMETIC  # Default
    if request.question_type:
        question_type = QuestionType(request.question_type.value)
    elif topic:
        # Map topic slug to question type
        type_map = {
            "arithmetic": QuestionType.ARITHMETIC,
            "fractions": QuestionType.FRACTIONS,
            "percentages": QuestionType.PERCENTAGES,
            "algebra": QuestionType.ALGEBRA,
            "geometry": QuestionType.GEOMETRY,
            "ratios": QuestionType.RATIOS,
        }
        question_type = type_map.get(topic.slug, QuestionType.ARITHMETIC)

    # Get generator
    generator = registry.get(question_type)
    if not generator:
        # Fallback to arithmetic if type not implemented
        generator = registry.get(QuestionType.ARITHMETIC)
        if not generator:
            raise HTTPException(
                status_code=500,
                detail="No question generator available"
            )

    # Determine difficulty
    difficulty = request.difficulty
    if difficulty is None:
        # Use mastery-based difficulty
        topic_key = topic.slug if topic else "arithmetic"
        difficulty = mastery_tracker.get_recommended_difficulty(topic_key)

    # Determine operation
    operation = None
    if request.operation:
        operation = OperationType(request.operation.value)

    # Generate question
    try:
        question = generator.generate(
            difficulty=difficulty,
            operation=operation,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate question: {str(e)}"
        )

    # Prepare response
    return QuestionResponse(
        question_id=question.question_id,
        session_id=None,
        question_type=question.question_type.value,
        operation=question.operation.value if question.operation else None,
        expression=question.expression,
        expression_latex=question.expression_latex,
        story_text=question.story_text,
        visual_url=question.visual_url,
        answer_format=question.answer_format.value,
        multiple_choice=request.multiple_choice,
        options=question.all_options if request.multiple_choice else None,
        difficulty_score=question.difficulty_score,
        difficulty_tier=question.difficulty_tier.value,
        topic_name=topic_name,
        subtopic_name=None,
    )


@router.get("/questions/types")
async def get_question_types():
    """Get all registered question types."""
    types = registry.list_types()
    return {
        "types": [t.value for t in types],
        "count": len(types),
    }
