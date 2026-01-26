"""Diagnostic Assessment API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ...services.diagnostic_service import diagnostic_service

router = APIRouter(prefix="/diagnostic", tags=["Diagnostic Assessment"])


class StartDiagnosticRequest(BaseModel):
    user_id: str
    grade_level: Optional[int] = None

class SubmitAnswerRequest(BaseModel):
    question_id: Optional[str] = None
    answer: str


@router.post("/start")
async def start_diagnostic(req: StartDiagnosticRequest):
    """Tanilayici test baslat."""
    try:
        session = diagnostic_service.start_diagnostic(
            user_id=req.user_id,
            grade_level=req.grade_level or 5,
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/next/{session_id}")
async def get_next_question(session_id: str):
    """Sonraki soruyu getir."""
    try:
        question = diagnostic_service.get_next_question(session_id)
        if question is None:
            return {"message": "Test tamamlandi.", "completed": True}
        return question
    except KeyError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/answer/{session_id}")
async def submit_answer(session_id: str, req: SubmitAnswerRequest):
    """Cevap gonder."""
    try:
        result = diagnostic_service.submit_answer(
            session_id=session_id,
            question_id=req.question_id,
            answer=req.answer,
        )
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/complete/{session_id}")
async def complete_diagnostic(session_id: str):
    """Tanilayici testi tamamla."""
    try:
        result = diagnostic_service.complete_diagnostic(session_id)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/result/{session_id}")
async def get_placement_result(session_id: str):
    """Yerlestirme sonucunu getir."""
    try:
        result = diagnostic_service.get_placement_result(session_id)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
