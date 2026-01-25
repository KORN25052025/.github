"""
Parent Dashboard API routes.

Provides parents/guardians with visibility into their child's
learning progress, activity, and achievements.

Features:
- Child progress overview
- Weekly/monthly reports
- Activity notifications
- Goal setting
- Screen time insights
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from ...database import get_db
from ...models import User, Session as LearningSession, Response, Mastery, Topic

router = APIRouter(prefix="/parent", tags=["Parent Dashboard"])


# Pydantic models
class ChildOverview(BaseModel):
    user_id: str
    display_name: str
    grade_level: int
    total_xp: int
    level: int
    level_name: str
    current_streak: int
    best_streak: int
    badges_earned: int
    average_mastery: float
    total_questions_answered: int
    overall_accuracy: float
    member_since: datetime


class WeeklyReport(BaseModel):
    week_start: datetime
    week_end: datetime
    days_active: int
    total_questions: int
    correct_answers: int
    accuracy: float
    xp_earned: int
    topics_practiced: List[str]
    strongest_topic: Optional[str]
    needs_improvement: Optional[str]
    average_session_minutes: float
    streak_maintained: bool


class DailyActivity(BaseModel):
    date: str
    questions_answered: int
    correct: int
    accuracy: float
    minutes_practiced: int
    topics: List[str]
    xp_earned: int


class LearningGoal(BaseModel):
    id: str
    title: str
    target_value: int
    current_value: int
    goal_type: str  # "questions", "accuracy", "streak", "mastery"
    deadline: Optional[datetime]
    is_completed: bool
    progress_percent: float


class TopicProgress(BaseModel):
    topic_id: int
    topic_name: str
    mastery_score: float
    mastery_level: str
    questions_attempted: int
    accuracy: float
    last_practiced: Optional[datetime]
    trend: str  # "improving", "stable", "declining"


# Level names
LEVEL_NAMES = {
    1: "Beginner",
    2: "Learner",
    3: "Student",
    4: "Scholar",
    5: "Expert",
    6: "Master",
    7: "Grandmaster",
    8: "Legend",
    9: "Champion",
    10: "Math Wizard",
}


def get_level_name(level: int) -> str:
    return LEVEL_NAMES.get(min(level, 10), f"Level {level}")


@router.get("/child/{child_id}/overview", response_model=ChildOverview)
async def get_child_overview(
    child_id: str,
    parent_id: str = Query(..., description="Parent's user ID for verification"),
    db: Session = Depends(get_db)
):
    """Get comprehensive overview of child's learning progress."""
    # In production, verify parent-child relationship
    child = db.query(User).filter(User.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    # Get mastery data with eager loading for topic relationship
    masteries = db.query(Mastery).options(
        joinedload(Mastery.topic)
    ).filter(Mastery.user_id == child_id).all()
    avg_mastery = sum(m.mastery_score for m in masteries) / len(masteries) if masteries else 0.0
    current_streak = max((m.current_streak for m in masteries), default=0)
    best_streak = max((m.best_streak for m in masteries), default=0)

    # Get response stats
    total_questions = db.query(func.count(Response.id)).filter(
        Response.user_id == child_id
    ).scalar() or 0

    correct_questions = db.query(func.count(Response.id)).filter(
        Response.user_id == child_id,
        Response.is_correct == True
    ).scalar() or 0

    accuracy = correct_questions / total_questions if total_questions > 0 else 0.0

    # Count badges (simplified - in production would query badges table)
    badges_earned = min(child.level * 2, 20)  # Approximate

    return ChildOverview(
        user_id=child.id,
        display_name=child.display_name or "Student",
        grade_level=child.grade_level or 6,
        total_xp=child.total_xp,
        level=child.level,
        level_name=get_level_name(child.level),
        current_streak=current_streak,
        best_streak=best_streak,
        badges_earned=badges_earned,
        average_mastery=avg_mastery,
        total_questions_answered=total_questions,
        overall_accuracy=accuracy,
        member_since=child.created_at,
    )


@router.get("/child/{child_id}/weekly-report", response_model=WeeklyReport)
async def get_weekly_report(
    child_id: str,
    parent_id: str = Query(..., description="Parent's user ID"),
    weeks_ago: int = Query(0, ge=0, le=12, description="0 = current week"),
    db: Session = Depends(get_db)
):
    """Get detailed weekly progress report."""
    # Calculate week boundaries
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=today.weekday() + (weeks_ago * 7))
    end_of_week = start_of_week + timedelta(days=6)

    start_dt = datetime.combine(start_of_week, datetime.min.time())
    end_dt = datetime.combine(end_of_week, datetime.max.time())

    # Get sessions for the week
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == child_id,
        LearningSession.started_at >= start_dt,
        LearningSession.started_at <= end_dt,
    ).all()

    # Get responses for the week
    responses = db.query(Response).filter(
        Response.user_id == child_id,
        Response.created_at >= start_dt,
        Response.created_at <= end_dt,
    ).all()

    # Calculate metrics
    total_questions = len(responses)
    correct = sum(1 for r in responses if r.is_correct)
    accuracy = correct / total_questions if total_questions > 0 else 0.0

    # Days active
    active_days = len(set(r.created_at.date() for r in responses))

    # Topics practiced
    topic_ids = set(s.topic_id for s in sessions if s.topic_id)
    topics = db.query(Topic).filter(Topic.id.in_(topic_ids)).all() if topic_ids else []
    topic_names = [t.name for t in topics]

    # Calculate session duration (approximate)
    total_minutes = 0
    for s in sessions:
        if s.ended_at:
            duration = (s.ended_at - s.started_at).total_seconds() / 60
            total_minutes += min(duration, 60)  # Cap at 60 min per session
        else:
            total_minutes += 15  # Estimate for incomplete sessions

    avg_minutes = total_minutes / len(sessions) if sessions else 0

    # Find strongest and weakest topics
    topic_accuracies = {}
    for s in sessions:
        if s.topic_id and s.questions_attempted > 0:
            acc = s.questions_correct / s.questions_attempted
            if s.topic_id not in topic_accuracies:
                topic_accuracies[s.topic_id] = []
            topic_accuracies[s.topic_id].append(acc)

    strongest = None
    weakest = None
    if topic_accuracies:
        avg_by_topic = {
            tid: sum(accs) / len(accs)
            for tid, accs in topic_accuracies.items()
        }
        strongest_id = max(avg_by_topic, key=avg_by_topic.get)
        weakest_id = min(avg_by_topic, key=avg_by_topic.get)
        strongest_topic = db.query(Topic).filter(Topic.id == strongest_id).first()
        weakest_topic = db.query(Topic).filter(Topic.id == weakest_id).first()
        strongest = strongest_topic.name if strongest_topic else None
        weakest = weakest_topic.name if weakest_topic else None

    # Check streak
    masteries = db.query(Mastery).filter(Mastery.user_id == child_id).all()
    streak_maintained = any(m.current_streak >= 7 for m in masteries)

    # Estimate XP earned (20 per correct, 5 per wrong)
    xp_earned = correct * 20 + (total_questions - correct) * 5

    return WeeklyReport(
        week_start=start_dt,
        week_end=end_dt,
        days_active=active_days,
        total_questions=total_questions,
        correct_answers=correct,
        accuracy=accuracy,
        xp_earned=xp_earned,
        topics_practiced=topic_names,
        strongest_topic=strongest,
        needs_improvement=weakest,
        average_session_minutes=avg_minutes,
        streak_maintained=streak_maintained,
    )


@router.get("/child/{child_id}/daily-activity", response_model=List[DailyActivity])
async def get_daily_activity(
    child_id: str,
    parent_id: str = Query(..., description="Parent's user ID"),
    days: int = Query(30, ge=7, le=90, description="Number of days to retrieve"),
    db: Session = Depends(get_db)
):
    """Get daily activity breakdown for the past N days."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get responses grouped by day
    responses = db.query(Response).filter(
        Response.user_id == child_id,
        Response.created_at >= start_date,
    ).all()

    # Group by day
    daily_data = {}
    for r in responses:
        day = r.created_at.date().isoformat()
        if day not in daily_data:
            daily_data[day] = {
                "questions": 0,
                "correct": 0,
                "topics": set(),
            }
        daily_data[day]["questions"] += 1
        if r.is_correct:
            daily_data[day]["correct"] += 1
        # Topic would come from session - simplified here

    # Get session durations
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == child_id,
        LearningSession.started_at >= start_date,
    ).all()

    session_minutes = {}
    for s in sessions:
        day = s.started_at.date().isoformat()
        if day not in session_minutes:
            session_minutes[day] = 0
        if s.ended_at:
            duration = (s.ended_at - s.started_at).total_seconds() / 60
            session_minutes[day] += min(duration, 60)
        else:
            session_minutes[day] += 10

    # Build result
    result = []
    for day, data in sorted(daily_data.items(), reverse=True):
        questions = data["questions"]
        correct = data["correct"]
        result.append(DailyActivity(
            date=day,
            questions_answered=questions,
            correct=correct,
            accuracy=correct / questions if questions > 0 else 0.0,
            minutes_practiced=int(session_minutes.get(day, 0)),
            topics=list(data["topics"]),
            xp_earned=correct * 20 + (questions - correct) * 5,
        ))

    return result[:days]  # Limit to requested days


@router.get("/child/{child_id}/topics", response_model=List[TopicProgress])
async def get_topic_progress(
    child_id: str,
    parent_id: str = Query(..., description="Parent's user ID"),
    db: Session = Depends(get_db)
):
    """Get detailed progress for each topic."""
    topics = db.query(Topic).all()
    result = []

    for topic in topics:
        mastery = db.query(Mastery).filter(
            Mastery.user_id == child_id,
            Mastery.topic_id == topic.id,
        ).first()

        # Get last session for this topic
        last_session = db.query(LearningSession).filter(
            LearningSession.user_id == child_id,
            LearningSession.topic_id == topic.id,
        ).order_by(desc(LearningSession.started_at)).first()

        # Determine mastery level
        mastery_score = mastery.mastery_score if mastery else 0.0
        if mastery_score < 0.2:
            mastery_level = "Novice"
        elif mastery_score < 0.4:
            mastery_level = "Beginner"
        elif mastery_score < 0.6:
            mastery_level = "Intermediate"
        elif mastery_score < 0.8:
            mastery_level = "Advanced"
        else:
            mastery_level = "Expert"

        # Determine trend (simplified - would need historical data)
        trend = "stable"
        if mastery and mastery.attempts > 10:
            recent_accuracy = mastery.correct / mastery.attempts
            if recent_accuracy > 0.7:
                trend = "improving"
            elif recent_accuracy < 0.4:
                trend = "declining"

        result.append(TopicProgress(
            topic_id=topic.id,
            topic_name=topic.name,
            mastery_score=mastery_score,
            mastery_level=mastery_level,
            questions_attempted=mastery.attempts if mastery else 0,
            accuracy=mastery.correct / mastery.attempts if mastery and mastery.attempts > 0 else 0.0,
            last_practiced=last_session.started_at if last_session else None,
            trend=trend,
        ))

    return result


@router.get("/child/{child_id}/achievements")
async def get_achievements(
    child_id: str,
    parent_id: str = Query(..., description="Parent's user ID"),
    db: Session = Depends(get_db)
):
    """Get child's achievements and milestones."""
    child = db.query(User).filter(User.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    masteries = db.query(Mastery).filter(Mastery.user_id == child_id).all()
    total_questions = db.query(func.count(Response.id)).filter(
        Response.user_id == child_id
    ).scalar() or 0

    correct_questions = db.query(func.count(Response.id)).filter(
        Response.user_id == child_id,
        Response.is_correct == True
    ).scalar() or 0

    # Define achievements
    achievements = [
        {
            "id": "first_question",
            "title": "First Steps",
            "title_tr": "Ilk Adimlar",
            "description": "Answer your first question",
            "icon": "star",
            "earned": total_questions >= 1,
        },
        {
            "id": "questions_10",
            "title": "Getting Started",
            "title_tr": "Baslangiç",
            "description": "Answer 10 questions",
            "icon": "trending-up",
            "earned": total_questions >= 10,
        },
        {
            "id": "questions_100",
            "title": "Century Club",
            "title_tr": "Yuzler Kulubu",
            "description": "Answer 100 questions",
            "icon": "medal",
            "earned": total_questions >= 100,
        },
        {
            "id": "questions_500",
            "title": "Dedicated Learner",
            "title_tr": "Adanmis Ogrenci",
            "description": "Answer 500 questions",
            "icon": "trophy",
            "earned": total_questions >= 500,
        },
        {
            "id": "accuracy_80",
            "title": "Sharp Mind",
            "title_tr": "Keskin Zihin",
            "description": "Achieve 80% overall accuracy",
            "icon": "checkmark-circle",
            "earned": (correct_questions / total_questions >= 0.8) if total_questions > 20 else False,
        },
        {
            "id": "streak_7",
            "title": "Week Warrior",
            "title_tr": "Hafta Savascisi",
            "description": "7-day practice streak",
            "icon": "flame",
            "earned": any(m.best_streak >= 7 for m in masteries),
        },
        {
            "id": "streak_30",
            "title": "Monthly Champion",
            "title_tr": "Aylik Sampiyon",
            "description": "30-day practice streak",
            "icon": "ribbon",
            "earned": any(m.best_streak >= 30 for m in masteries),
        },
        {
            "id": "mastery_topic",
            "title": "Topic Master",
            "title_tr": "Konu Ustasi",
            "description": "Reach 80% mastery in any topic",
            "icon": "school",
            "earned": any(m.mastery_score >= 0.8 for m in masteries),
        },
        {
            "id": "all_topics",
            "title": "Well Rounded",
            "title_tr": "Cok Yonlu",
            "description": "Practice all 6 topics",
            "icon": "globe",
            "earned": len(masteries) >= 6,
        },
        {
            "id": "level_5",
            "title": "Rising Star",
            "title_tr": "Yukselen Yildiz",
            "description": "Reach level 5",
            "icon": "star",
            "earned": child.level >= 5,
        },
        {
            "id": "level_10",
            "title": "Math Wizard",
            "title_tr": "Matematik Sihirbazi",
            "description": "Reach level 10",
            "icon": "sparkles",
            "earned": child.level >= 10,
        },
    ]

    earned_count = sum(1 for a in achievements if a["earned"])

    return {
        "achievements": achievements,
        "earned_count": earned_count,
        "total_count": len(achievements),
        "completion_percent": (earned_count / len(achievements)) * 100,
    }


@router.post("/child/{child_id}/goals")
async def set_learning_goal(
    child_id: str,
    parent_id: str = Query(..., description="Parent's user ID"),
    goal_type: str = Query(..., description="Type: questions, accuracy, streak, mastery"),
    target_value: int = Query(..., ge=1),
    deadline_days: Optional[int] = Query(None, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Set a learning goal for the child."""
    # Validate goal type
    valid_types = ["questions", "accuracy", "streak", "mastery"]
    if goal_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid goal type. Must be one of: {valid_types}")

    deadline = None
    if deadline_days:
        deadline = datetime.utcnow() + timedelta(days=deadline_days)

    # In production, store in database
    goal = {
        "id": f"goal_{child_id}_{goal_type}_{datetime.utcnow().timestamp()}",
        "child_id": child_id,
        "goal_type": goal_type,
        "target_value": target_value,
        "current_value": 0,
        "deadline": deadline.isoformat() if deadline else None,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": parent_id,
    }

    return {
        "success": True,
        "message": "Learning goal created",
        "goal": goal,
    }


@router.get("/child/{child_id}/screen-time")
async def get_screen_time(
    child_id: str,
    parent_id: str = Query(..., description="Parent's user ID"),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get screen time / practice time insights."""
    start_date = datetime.utcnow() - timedelta(days=days)

    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == child_id,
        LearningSession.started_at >= start_date,
    ).all()

    # Calculate daily screen time
    daily_minutes = {}
    for s in sessions:
        day = s.started_at.date().isoformat()
        if day not in daily_minutes:
            daily_minutes[day] = 0

        if s.ended_at:
            duration = (s.ended_at - s.started_at).total_seconds() / 60
            daily_minutes[day] += min(duration, 120)  # Cap at 2 hours
        else:
            daily_minutes[day] += 15  # Estimate

    total_minutes = sum(daily_minutes.values())
    avg_daily = total_minutes / days if days > 0 else 0

    # Find peak hours (simplified)
    hour_counts = {}
    for s in sessions:
        hour = s.started_at.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1

    peak_hour = max(hour_counts, key=hour_counts.get) if hour_counts else 16

    return {
        "total_minutes": int(total_minutes),
        "average_daily_minutes": round(avg_daily, 1),
        "days_tracked": days,
        "daily_breakdown": [
            {"date": day, "minutes": int(mins)}
            for day, mins in sorted(daily_minutes.items())
        ],
        "peak_practice_hour": peak_hour,
        "peak_practice_hour_label": f"{peak_hour}:00 - {peak_hour + 1}:00",
        "sessions_count": len(sessions),
    }
