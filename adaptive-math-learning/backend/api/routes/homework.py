"""Homework, Goals, and Class Analytics API routes."""

from dataclasses import asdict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime

from ...services.enhanced_parent_teacher_service import (
    homework_service,
    weekly_report_service,
    goal_setting_service,
    class_analytics_service,
)


def _serialize_goal(goal) -> Dict[str, Any]:
    """Serialize a LearningGoal dataclass to JSON-safe dict."""
    d = asdict(goal)
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
        elif hasattr(v, "value"):
            d[k] = v.value
    return d

router = APIRouter(prefix="/homework", tags=["Homework & Goals"])


class CreateHomeworkRequest(BaseModel):
    teacher_id: str
    class_id: str
    topics: List[str]
    question_count: int = 10
    due_date: Optional[str] = None
    title: str = "Odev"

class SubmitHomeworkRequest(BaseModel):
    student_id: str
    answers: List[Dict[str, Any]]

class SetGoalRequest(BaseModel):
    parent_id: str
    child_id: str
    goal_type: str  # "questions_per_week", "accuracy_target", etc.
    target_value: float
    deadline: Optional[str] = None


@router.post("/create")
async def create_homework(req: CreateHomeworkRequest):
    """Odev olustur."""
    try:
        from datetime import timedelta
        if req.due_date:
            due_dt = datetime.fromisoformat(req.due_date)
        else:
            due_dt = datetime.utcnow() + timedelta(days=7)
        hw = homework_service.create_homework(
            teacher_id=req.teacher_id,
            class_id=req.class_id,
            topics=req.topics,
            question_count=req.question_count,
            due_date=due_dt,
            title=req.title,
        )
        return {
            "homework_id": hw.homework_id,
            "title": hw.title,
            "topics": hw.topics,
            "question_count": hw.question_count,
            "due_date": hw.due_date.isoformat(),
            "status": hw.status.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{homework_id}")
async def get_homework(homework_id: str):
    """Odev detaylarini getir."""
    try:
        hw = homework_service.get_homework(homework_id)
        if hw is None:
            raise HTTPException(status_code=404, detail="Odev bulunamadi.")
        return hw
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{homework_id}/submit")
async def submit_homework(homework_id: str, req: SubmitHomeworkRequest):
    """Odevi teslim et."""
    try:
        result = homework_service.submit_homework(
            homework_id=homework_id,
            student_id=req.student_id,
            answers=req.answers,
        )
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Odev bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{homework_id}/grade")
async def grade_homework(homework_id: str):
    """Odevi notlandir."""
    try:
        result = homework_service.grade_homework(
            homework_id=homework_id,
        )
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Odev bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/student/{student_id}")
async def get_student_homework_list(student_id: str):
    """Ogrencinin odevlerini listele."""
    try:
        homeworks = homework_service.get_student_homework_list(student_id)
        return homeworks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/goals/set")
async def set_goal(req: SetGoalRequest):
    """Ogrenme hedefi belirle."""
    try:
        from ...services.enhanced_parent_teacher_service import GoalType
        goal_type = GoalType(req.goal_type)
        deadline = datetime.fromisoformat(req.deadline) if req.deadline else None
        goal = goal_setting_service.set_goal(
            parent_id=req.parent_id,
            child_id=req.child_id,
            goal_type=goal_type,
            target_value=req.target_value,
            deadline=deadline,
        )
        return _serialize_goal(goal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/goals/{child_id}")
async def get_goals(child_id: str):
    """Cocugun hedeflerini getir."""
    try:
        goals = goal_setting_service.get_goals(child_id)
        return [_serialize_goal(g) for g in goals]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/goals/{goal_id}/progress")
async def check_goal_progress(goal_id: str):
    """Hedef ilerlemesini kontrol et."""
    try:
        progress = goal_setting_service.check_progress(goal_id)
        return progress
    except KeyError:
        raise HTTPException(status_code=404, detail="Hedef bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/class/{class_id}/overview")
async def get_class_overview(class_id: str):
    """Sinif genel bakisini getir."""
    try:
        overview = class_analytics_service.get_class_overview(class_id)
        return overview
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/class/{class_id}/topics")
async def get_class_topic_analysis(class_id: str):
    """Sinifin konu analizini getir."""
    try:
        analysis = class_analytics_service.get_topic_analysis(class_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/class/{class_id}/at-risk")
async def get_at_risk_students(class_id: str):
    """Risk altindaki ogrencileri getir."""
    try:
        students = class_analytics_service.get_at_risk_students(class_id)
        return students
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
