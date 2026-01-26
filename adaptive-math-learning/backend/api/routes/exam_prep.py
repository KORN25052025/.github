"""Exam Preparation API routes."""

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ...services.exam_prep_service import exam_prep_service

router = APIRouter(prefix="/exam", tags=["Exam Preparation"])


class ExamSessionRequest(BaseModel):
    user_id: str
    exam_type: str
    topics: Optional[List[str]] = None
    question_count: int = 20

class MockExamRequest(BaseModel):
    user_id: str = "current_user"

class EvaluateExamRequest(BaseModel):
    answers: Dict[str, str]


@router.post("/session")
async def generate_exam_session(req: ExamSessionRequest):
    """Sinav oturumu olustur."""
    try:
        session = exam_prep_service.generate_exam_session(
            user_id=req.user_id,
            exam_type=req.exam_type,
            topics=req.topics,
            question_count=req.question_count,
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mock/{exam_type}")
async def generate_mock_exam(exam_type: str, req: Optional[MockExamRequest] = Body(None)):
    """Deneme sinavi olustur."""
    try:
        user_id = req.user_id if req else "current_user"
        exam = exam_prep_service.generate_mock_exam(
            exam_type=exam_type,
            user_id=user_id,
        )
        return exam
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/evaluate/{session_id}")
async def evaluate_exam(session_id: str, req: EvaluateExamRequest):
    """Sinav sonuclarini degerlendir."""
    try:
        result = exam_prep_service.evaluate_exam(
            session_id=session_id,
            answers=req.answers,
        )
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Sinav oturumu bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/{user_id}/{exam_type}")
async def get_exam_statistics(user_id: str, exam_type: str):
    """Kullanicinin sinav istatistiklerini getir."""
    try:
        stats = exam_prep_service.get_exam_statistics(user_id, exam_type)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/topics/{exam_type}")
async def get_topic_weights(exam_type: str):
    """Sinav turune gore konu agirliklarini getir."""
    try:
        weights = exam_prep_service.get_topic_weights(exam_type)
        return weights
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
