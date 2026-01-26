"""Spaced Repetition (SRS) API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ...services.spaced_repetition_service import spaced_repetition_service

router = APIRouter(prefix="/srs", tags=["Spaced Repetition"])


class RecordWrongAnswerRequest(BaseModel):
    user_id: str
    question_id: str
    question_data: Dict[str, Any]
    user_answer: str
    correct_answer: str

class SubmitReviewRequest(BaseModel):
    user_id: str
    question_id: str
    quality: int  # 0-5 SM-2 quality rating


@router.post("/record")
async def record_wrong_answer(req: RecordWrongAnswerRequest):
    """Yanlis cevabi kaydet."""
    try:
        entry = spaced_repetition_service.record_wrong_answer(
            user_id=req.user_id,
            question_id=req.question_id,
            question_data=req.question_data,
            user_answer=req.user_answer,
            correct_answer=req.correct_answer,
        )
        return {"status": "success", "entry": entry}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/review/{user_id}")
async def get_review_queue(user_id: str):
    """Tekrar kuyrugunu getir."""
    try:
        queue = spaced_repetition_service.get_review_queue(user_id)
        return {"status": "success", "queue": queue, "count": len(queue)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/review")
async def submit_review(req: SubmitReviewRequest):
    """Tekrar sonucunu kaydet."""
    try:
        result = spaced_repetition_service.submit_review(
            user_id=req.user_id,
            question_id=req.question_id,
            quality=req.quality,
        )
        return {"status": "success", "result": result}
    except KeyError:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/notebook/{user_id}")
async def get_wrong_answer_notebook(user_id: str):
    """Yanlis soru defterini getir."""
    try:
        notebook = spaced_repetition_service.get_wrong_answer_notebook(user_id)
        return {"status": "success", "notebook": notebook, "total": len(notebook)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/{user_id}")
async def get_srs_statistics(user_id: str):
    """SRS istatistiklerini getir."""
    try:
        stats = spaced_repetition_service.get_srs_statistics(user_id)
        return {"status": "success", "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/mastered/{user_id}")
async def clear_mastered(user_id: str):
    """Ogrenilmis kayitlari temizle."""
    try:
        count = spaced_repetition_service.clear_mastered(user_id)
        return {"status": "success", "cleared_count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
