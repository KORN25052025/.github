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
    user_id: str
    message: str

class ExplainQuestionRequest(BaseModel):
    user_id: str
    question_data: Dict[str, Any]

class ExplainErrorRequest(BaseModel):
    user_id: str
    question_data: Dict[str, Any]
    user_answer: str
    correct_answer: str


@router.post("/start")
async def start_session(req: StartSessionRequest):
    """AI tutor oturumu baslat."""
    try:
        session = ai_tutor_service.start_session(
            user_id=req.user_id,
            topic=req.topic,
        )
        return {"status": "success", "session": session}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/message/{session_id}")
async def send_message(session_id: str, req: SendMessageRequest):
    """AI tutora mesaj gonder."""
    try:
        response = ai_tutor_service.send_message(
            session_id=session_id,
            user_id=req.user_id,
            message=req.message,
        )
        return {"status": "success", "response": response}
    except KeyError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/explain")
async def explain_question(req: ExplainQuestionRequest):
    """Soruyu acikla."""
    try:
        explanation = ai_tutor_service.explain_question(
            user_id=req.user_id,
            question_data=req.question_data,
        )
        return {"status": "success", "explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/error")
async def explain_error(req: ExplainErrorRequest):
    """Hatanin nedenini acikla."""
    try:
        explanation = ai_tutor_service.explain_error(
            user_id=req.user_id,
            question_data=req.question_data,
            user_answer=req.user_answer,
            correct_answer=req.correct_answer,
        )
        return {"status": "success", "explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{session_id}")
async def get_session_history(session_id: str):
    """Oturum gecmisini getir."""
    try:
        history = ai_tutor_service.get_session_history(session_id)
        return {"status": "success", "history": history}
    except KeyError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/end/{session_id}")
async def end_session(session_id: str):
    """Oturumu sonlandir."""
    try:
        result = ai_tutor_service.end_session(session_id)
        return {"status": "success", "result": result}
    except KeyError:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
