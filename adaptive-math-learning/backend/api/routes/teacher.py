"""
Teacher Dashboard API routes.

Provides classroom analytics and student progress tracking for teachers.
Implements UC-04 (Monitor Class) and UC-05 (Assign Practice) from specifications.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from ...database import get_db
from ...models import User, Session as LearningSession, Response, Mastery, Topic

router = APIRouter(prefix="/teacher", tags=["Teacher Dashboard"])


# Pydantic models for responses
class StudentSummary(BaseModel):
    user_id: str
    display_name: str
    grade_level: int
    total_xp: int
    level: int
    average_mastery: float
    total_questions: int
    accuracy: float
    current_streak: int
    last_active: Optional[datetime] = None
    struggling_topics: List[str] = []


class ClassStatistics(BaseModel):
    total_students: int
    active_today: int
    active_this_week: int
    average_mastery: float
    average_accuracy: float
    total_questions_answered: int
    questions_today: int


class TopicPerformance(BaseModel):
    topic_id: int
    topic_name: str
    topic_slug: str
    students_practiced: int
    average_mastery: float
    average_accuracy: float
    struggling_students: int
    excelling_students: int


class StudentDetail(BaseModel):
    user_id: str
    display_name: str
    grade_level: int
    total_xp: int
    level: int
    ab_group: str
    created_at: datetime
    topic_mastery: List[dict]
    recent_sessions: List[dict]
    daily_activity: List[dict]


class AssignmentCreate(BaseModel):
    student_ids: List[str]
    topic_id: int
    target_questions: int = 10
    difficulty_tier: Optional[int] = None
    due_date: Optional[datetime] = None


class Assignment(BaseModel):
    id: int
    topic_id: int
    topic_name: str
    target_questions: int
    difficulty_tier: Optional[int]
    due_date: Optional[datetime]
    assigned_at: datetime
    completed_students: int
    total_students: int


@router.get("/class/statistics", response_model=ClassStatistics)
async def get_class_statistics(
    teacher_id: str = Query(..., description="Teacher's user ID"),
    db: Session = Depends(get_db)
):
    """Get overall class statistics for a teacher's students."""
    # In a real system, we'd filter by teacher's class
    # For now, get all students' stats

    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)

    # Total students
    total_students = db.query(func.count(User.id)).scalar() or 0

    # Active today
    active_today = db.query(func.count(func.distinct(LearningSession.user_id))).filter(
        LearningSession.started_at >= today
    ).scalar() or 0

    # Active this week
    active_week = db.query(func.count(func.distinct(LearningSession.user_id))).filter(
        LearningSession.started_at >= week_ago
    ).scalar() or 0

    # Average mastery
    avg_mastery = db.query(func.avg(Mastery.mastery_score)).scalar() or 0.0

    # Total questions and accuracy
    total_questions = db.query(func.count(Response.id)).scalar() or 0
    correct_count = db.query(func.count(Response.id)).filter(Response.is_correct == True).scalar() or 0
    avg_accuracy = correct_count / total_questions if total_questions > 0 else 0.0

    # Questions today
    questions_today = db.query(func.count(Response.id)).filter(
        Response.created_at >= today
    ).scalar() or 0

    return ClassStatistics(
        total_students=total_students,
        active_today=active_today,
        active_this_week=active_week,
        average_mastery=avg_mastery,
        average_accuracy=avg_accuracy,
        total_questions_answered=total_questions,
        questions_today=questions_today,
    )


@router.get("/class/students", response_model=List[StudentSummary])
async def get_class_students(
    teacher_id: str = Query(..., description="Teacher's user ID"),
    sort_by: str = Query("last_active", description="Sort by: last_active, mastery, accuracy, xp"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of all students with their progress summaries."""
    # Get all users with their mastery data
    students = db.query(User).offset(offset).limit(limit).all()

    result = []
    for student in students:
        # Get mastery data
        masteries = db.query(Mastery).filter(Mastery.user_id == student.id).all()

        avg_mastery = sum(m.mastery_score for m in masteries) / len(masteries) if masteries else 0.0

        # Get response stats
        total_q = db.query(func.count(Response.id)).filter(Response.user_id == student.id).scalar() or 0
        correct_q = db.query(func.count(Response.id)).filter(
            Response.user_id == student.id,
            Response.is_correct == True
        ).scalar() or 0
        accuracy = correct_q / total_q if total_q > 0 else 0.0

        # Get last active
        last_session = db.query(LearningSession).filter(
            LearningSession.user_id == student.id
        ).order_by(desc(LearningSession.started_at)).first()

        # Find struggling topics (mastery < 0.3)
        struggling = [
            m.topic.name for m in masteries
            if m.mastery_score < 0.3 and m.topic
        ]

        # Get current streak from mastery
        current_streak = max((m.current_streak for m in masteries), default=0)

        result.append(StudentSummary(
            user_id=student.id,
            display_name=student.display_name or "Unknown",
            grade_level=student.grade_level or 6,
            total_xp=student.total_xp,
            level=student.level,
            average_mastery=avg_mastery,
            total_questions=total_q,
            accuracy=accuracy,
            current_streak=current_streak,
            last_active=last_session.started_at if last_session else None,
            struggling_topics=struggling[:3],  # Top 3 struggling topics
        ))

    # Sort results
    if sort_by == "mastery":
        result.sort(key=lambda x: x.average_mastery, reverse=True)
    elif sort_by == "accuracy":
        result.sort(key=lambda x: x.accuracy, reverse=True)
    elif sort_by == "xp":
        result.sort(key=lambda x: x.total_xp, reverse=True)
    else:  # last_active
        result.sort(key=lambda x: x.last_active or datetime.min, reverse=True)

    return result


@router.get("/class/topics", response_model=List[TopicPerformance])
async def get_topic_performance(
    teacher_id: str = Query(..., description="Teacher's user ID"),
    db: Session = Depends(get_db)
):
    """Get performance breakdown by topic."""
    topics = db.query(Topic).all()

    result = []
    for topic in topics:
        masteries = db.query(Mastery).filter(Mastery.topic_id == topic.id).all()

        if not masteries:
            result.append(TopicPerformance(
                topic_id=topic.id,
                topic_name=topic.name,
                topic_slug=topic.slug,
                students_practiced=0,
                average_mastery=0.0,
                average_accuracy=0.0,
                struggling_students=0,
                excelling_students=0,
            ))
            continue

        avg_mastery = sum(m.mastery_score for m in masteries) / len(masteries)
        avg_accuracy = sum(m.correct / m.attempts if m.attempts > 0 else 0 for m in masteries) / len(masteries)

        struggling = sum(1 for m in masteries if m.mastery_score < 0.3)
        excelling = sum(1 for m in masteries if m.mastery_score >= 0.8)

        result.append(TopicPerformance(
            topic_id=topic.id,
            topic_name=topic.name,
            topic_slug=topic.slug,
            students_practiced=len(masteries),
            average_mastery=avg_mastery,
            average_accuracy=avg_accuracy,
            struggling_students=struggling,
            excelling_students=excelling,
        ))

    return result


@router.get("/student/{user_id}", response_model=StudentDetail)
async def get_student_detail(
    user_id: str,
    teacher_id: str = Query(..., description="Teacher's user ID"),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a specific student."""
    student = db.query(User).filter(User.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get topic mastery
    masteries = db.query(Mastery).filter(Mastery.user_id == user_id).all()
    topic_mastery = []
    for m in masteries:
        topic = db.query(Topic).filter(Topic.id == m.topic_id).first()
        topic_mastery.append({
            "topic_id": m.topic_id,
            "topic_name": topic.name if topic else "Unknown",
            "mastery_score": m.mastery_score,
            "attempts": m.attempts,
            "correct": m.correct,
            "accuracy": m.correct / m.attempts if m.attempts > 0 else 0,
            "difficulty_tier": m.difficulty_tier,
            "streak": m.current_streak,
        })

    # Get recent sessions
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == user_id
    ).order_by(desc(LearningSession.started_at)).limit(10).all()

    recent_sessions = []
    for s in sessions:
        topic = db.query(Topic).filter(Topic.id == s.topic_id).first()
        recent_sessions.append({
            "session_id": s.id,
            "topic_name": topic.name if topic else "Unknown",
            "started_at": s.started_at.isoformat(),
            "duration_minutes": (s.ended_at - s.started_at).seconds // 60 if s.ended_at else 0,
            "questions_attempted": s.questions_attempted,
            "questions_correct": s.questions_correct,
            "accuracy": s.questions_correct / s.questions_attempted if s.questions_attempted > 0 else 0,
        })

    # Get daily activity for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_responses = db.query(
        func.date(Response.created_at).label('date'),
        func.count(Response.id).label('count'),
        func.sum(func.cast(Response.is_correct, sqlalchemy.Integer)).label('correct')
    ).filter(
        Response.user_id == user_id,
        Response.created_at >= thirty_days_ago
    ).group_by(func.date(Response.created_at)).all()

    daily_activity = [
        {
            "date": str(d.date),
            "questions": d.count,
            "correct": d.correct or 0,
        }
        for d in daily_responses
    ]

    return StudentDetail(
        user_id=student.id,
        display_name=student.display_name or "Unknown",
        grade_level=student.grade_level or 6,
        total_xp=student.total_xp,
        level=student.level,
        ab_group=student.ab_group or "control",
        created_at=student.created_at,
        topic_mastery=topic_mastery,
        recent_sessions=recent_sessions,
        daily_activity=daily_activity,
    )


@router.get("/struggling-students")
async def get_struggling_students(
    teacher_id: str = Query(..., description="Teacher's user ID"),
    topic_id: Optional[int] = Query(None, description="Filter by topic"),
    threshold: float = Query(0.3, description="Mastery threshold for struggling"),
    db: Session = Depends(get_db)
):
    """Identify students who are struggling and may need intervention."""
    query = db.query(Mastery).filter(Mastery.mastery_score < threshold)

    if topic_id:
        query = query.filter(Mastery.topic_id == topic_id)

    struggling = query.all()

    result = []
    seen_users = set()

    for m in struggling:
        if m.user_id in seen_users:
            continue
        seen_users.add(m.user_id)

        user = db.query(User).filter(User.id == m.user_id).first()
        topic = db.query(Topic).filter(Topic.id == m.topic_id).first()

        # Get struggling topics for this user
        user_masteries = db.query(Mastery).filter(
            Mastery.user_id == m.user_id,
            Mastery.mastery_score < threshold
        ).all()

        result.append({
            "user_id": m.user_id,
            "display_name": user.display_name if user else "Unknown",
            "grade_level": user.grade_level if user else 6,
            "struggling_topics": [
                {
                    "topic_name": db.query(Topic).filter(Topic.id == um.topic_id).first().name,
                    "mastery": um.mastery_score,
                    "attempts": um.attempts,
                }
                for um in user_masteries
            ],
            "recommendation": "Needs additional practice and support",
        })

    return {"struggling_students": result, "total_count": len(result)}


@router.post("/assignments")
async def create_assignment(
    assignment: AssignmentCreate,
    teacher_id: str = Query(..., description="Teacher's user ID"),
    db: Session = Depends(get_db)
):
    """Create a practice assignment for students."""
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == assignment.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # In a real system, we'd store assignments in a table
    # For now, return confirmation
    return {
        "success": True,
        "message": f"Assignment created for {len(assignment.student_ids)} students",
        "assignment": {
            "topic": topic.name,
            "target_questions": assignment.target_questions,
            "difficulty_tier": assignment.difficulty_tier,
            "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
            "students": assignment.student_ids,
        }
    }


@router.get("/ab-test/results")
async def get_ab_test_results(
    teacher_id: str = Query(..., description="Teacher's user ID"),
    db: Session = Depends(get_db)
):
    """Get A/B test results for the class."""
    # Get control group stats
    control_users = db.query(User).filter(User.ab_group == "control").all()
    treatment_users = db.query(User).filter(User.ab_group == "treatment").all()

    def get_group_stats(users):
        if not users:
            return {"count": 0, "avg_mastery": 0, "avg_questions": 0, "avg_accuracy": 0}

        user_ids = [u.id for u in users]

        masteries = db.query(Mastery).filter(Mastery.user_id.in_(user_ids)).all()
        responses = db.query(Response).filter(Response.user_id.in_(user_ids)).all()

        avg_mastery = sum(m.mastery_score for m in masteries) / len(masteries) if masteries else 0
        total_questions = len(responses)
        correct = sum(1 for r in responses if r.is_correct)

        return {
            "count": len(users),
            "avg_mastery": avg_mastery,
            "avg_questions": total_questions / len(users) if users else 0,
            "avg_accuracy": correct / total_questions if total_questions > 0 else 0,
        }

    control_stats = get_group_stats(control_users)
    treatment_stats = get_group_stats(treatment_users)

    # Calculate differences
    mastery_diff = treatment_stats["avg_mastery"] - control_stats["avg_mastery"]
    questions_diff = treatment_stats["avg_questions"] - control_stats["avg_questions"]
    accuracy_diff = treatment_stats["avg_accuracy"] - control_stats["avg_accuracy"]

    return {
        "control_group": control_stats,
        "treatment_group": treatment_stats,
        "differences": {
            "mastery_improvement": mastery_diff,
            "mastery_improvement_percent": (mastery_diff / control_stats["avg_mastery"] * 100) if control_stats["avg_mastery"] > 0 else 0,
            "questions_difference": questions_diff,
            "accuracy_difference": accuracy_diff,
        },
        "hypothesis_met": {
            "engagement_30_percent": questions_diff >= control_stats["avg_questions"] * 0.3 if control_stats["avg_questions"] > 0 else False,
            "mastery_20_percent": mastery_diff >= control_stats["avg_mastery"] * 0.2 if control_stats["avg_mastery"] > 0 else False,
        }
    }


# Need to import sqlalchemy for func.cast
import sqlalchemy
