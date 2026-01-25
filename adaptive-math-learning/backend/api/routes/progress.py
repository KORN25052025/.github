"""
Progress tracking routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...models import Topic, Mastery
from ...schemas import MasteryResponse, TopicMasteryResponse, StatisticsResponse

from adaptation.bkt_tracker import BKTTracker

router = APIRouter()

# BKT-based mastery tracker (Bayesian Knowledge Tracing)
mastery_tracker = BKTTracker()


@router.get("/progress/mastery", response_model=List[MasteryResponse])
async def get_all_mastery(db: Session = Depends(get_db)):
    """Get mastery scores for all topics."""
    topics = db.query(Topic).filter(Topic.is_active == True).all()

    result = []
    for topic in topics:
        record = mastery_tracker.get_record(topic.slug)

        result.append(MasteryResponse(
            topic_id=topic.id,
            topic_name=topic.name,
            mastery_score=record.mastery,  # BKT uses 'mastery' instead of 'mastery_score'
            level=record.difficulty_tier.name,  # BKT uses 'difficulty_tier' instead of 'level'
            attempts=record.attempts,
            correct=record.correct,
            accuracy=record.accuracy,
            streak=record.streak,
            best_streak=record.best_streak,
            last_updated=record.last_updated,
        ))

    return result


@router.get("/progress/mastery/{topic_slug}", response_model=MasteryResponse)
async def get_topic_mastery(
    topic_slug: str,
    db: Session = Depends(get_db)
):
    """Get mastery score for a specific topic."""
    topic = db.query(Topic).filter(
        Topic.slug == topic_slug,
        Topic.is_active == True
    ).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    record = mastery_tracker.get_record(topic_slug)

    return MasteryResponse(
        topic_id=topic.id,
        topic_name=topic.name,
        mastery_score=record.mastery,  # BKT uses 'mastery' instead of 'mastery_score'
        level=record.difficulty_tier.name,  # BKT uses 'difficulty_tier' instead of 'level'
        attempts=record.attempts,
        correct=record.correct,
        accuracy=record.accuracy,
        streak=record.streak,
        best_streak=record.best_streak,
        last_updated=record.last_updated,
    )


@router.get("/progress/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall statistics."""
    # Aggregate from mastery tracker
    records = mastery_tracker.get_all_records()

    total_attempts = sum(r.attempts for r in records.values())
    total_correct = sum(r.correct for r in records.values())
    overall_accuracy = total_correct / total_attempts if total_attempts > 0 else 0.0

    # Average mastery (BKT uses 'mastery' property)
    mastery_scores = [r.mastery for r in records.values()]
    avg_mastery = sum(mastery_scores) / len(mastery_scores) if mastery_scores else 0.5

    # Best streak across all topics
    best_streak = max((r.best_streak for r in records.values()), default=0)
    current_streak = max((r.streak for r in records.values()), default=0)

    return StatisticsResponse(
        total_questions=total_attempts,
        total_correct=total_correct,
        overall_accuracy=overall_accuracy,
        total_sessions=0,  # Would track in production
        total_time_minutes=0,  # Would track in production
        current_streak=current_streak,
        best_streak=best_streak,
        topics_practiced=len(records),
        average_mastery=avg_mastery,
    )


@router.post("/progress/reset")
async def reset_progress(topic_slug: str = None):
    """Reset progress for a topic or all topics."""
    if topic_slug:
        mastery_tracker.reset(topic_slug)
        return {"message": f"Progress reset for {topic_slug}"}
    else:
        mastery_tracker.reset_all()
        return {"message": "All progress reset"}


@router.get("/progress/recommendations")
async def get_recommendations(db: Session = Depends(get_db)):
    """Get topic recommendations based on mastery."""
    topics = db.query(Topic).filter(Topic.is_active == True).all()

    recommendations = []
    for topic in topics:
        mastery = mastery_tracker.get_mastery(topic.slug)
        record = mastery_tracker.get_record(topic.slug)

        # Recommend topics with low mastery or not practiced
        if mastery < 0.7 or record.attempts < 10:
            priority = 1 if mastery < 0.4 else (2 if mastery < 0.6 else 3)
            recommendations.append({
                "topic_id": topic.id,
                "topic_name": topic.name,
                "topic_slug": topic.slug,
                "current_mastery": mastery,
                "attempts": record.attempts,
                "priority": priority,
                "reason": "Needs practice" if mastery < 0.5 else "Room for improvement",
            })

    # Sort by priority and mastery
    recommendations.sort(key=lambda x: (x["priority"], x["current_mastery"]))

    return recommendations[:5]  # Top 5 recommendations
