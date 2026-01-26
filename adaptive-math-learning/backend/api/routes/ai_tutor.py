"""AI Tutor API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ...services.ai_tutor_service import ai_tutor_service

router = APIRouter(prefix="/tutor", tags=["AI Tutor"])


class StartSessionRequest(BaseModel):
    user_id: str
    topic: Optional[str] = None

class SendMessageRequest(BaseModel):
    message: str

class ExplainQuestionRequest(BaseModel):
    question_data: Dict[str, Any]
    user_answer: Optional[str] = None
    grade_level: Optional[int] = None

class ExplainErrorRequest(BaseModel):
    question_data: Dict[str, Any]
    user_answer: str
    correct_answer: str
    grade_level: Optional[int] = None


@router.post("/start")
async def start_session(req: StartSessionRequest):
    """AI tutor oturumu baslat."""
    try:
        session = await ai_tutor_service.start_session(
            user_id=req.user_id,
            topic=req.topic,
        )
        return session.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/message/{session_id}")
async def send_message(session_id: str, req: SendMessageRequest):
    """AI tutora mesaj gonder."""
    try:
        response = await ai_tutor_service.send_message(
            session_id=session_id,
            user_message=req.message,
        )
        return response.to_dict()
    except ValueError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/explain")
async def explain_question(req: ExplainQuestionRequest):
    """Soruyu acikla."""
    try:
        explanation = await ai_tutor_service.explain_question(
            question_data=req.question_data,
            user_answer=req.user_answer,
            grade_level=req.grade_level,
        )
        return explanation.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/error")
async def explain_error(req: ExplainErrorRequest):
    """Hatanin nedenini acikla."""
    try:
        explanation = await ai_tutor_service.explain_error(
            question_data=req.question_data,
            user_answer=req.user_answer,
            correct_answer=req.correct_answer,
            grade_level=req.grade_level,
        )
        return explanation.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{session_id}")
async def get_session_history(session_id: str):
    """Oturum gecmisini getir."""
    try:
        history = ai_tutor_service.get_session_history(session_id)
        return history
    except ValueError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/end/{session_id}")
async def end_session(session_id: str):
    """Oturumu sonlandir."""
    try:
        result = await ai_tutor_service.end_session(session_id)
        return result.to_dict()
    except ValueError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
