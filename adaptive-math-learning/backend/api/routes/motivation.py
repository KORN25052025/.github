"""Motivation and Content API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ...services.motivation_service import (
    math_history_service,
    math_puzzle_service,
    certificate_service,
    seasonal_content_service,
)

router = APIRouter(prefix="/motivation", tags=["Motivation & Content"])


class CheckPuzzleRequest(BaseModel):
    answer: str

class GenerateCertificateRequest(BaseModel):
    user_id: str
    topic: str
    mastery: float


@router.get("/daily-fact")
async def get_daily_fact():
    """Gunun matematik tarihi bilgisini getir."""
    try:
        fact = math_history_service.get_daily_fact()
        return fact.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/random-fact")
async def get_random_fact():
    """Rastgele bir matematik bilgisi getir."""
    try:
        fact = math_history_service.get_random_fact()
        return fact.to_dict()
    except Exception:
        # Fallback: daily fact dondur
        try:
            fact = math_history_service.get_daily_fact()
            return fact.to_dict()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.get("/mathematician/{mathematician_id}")
async def get_mathematician_story(mathematician_id: str):
    """Matematikci biyografi kartini getir."""
    story = math_history_service.get_mathematician_story(mathematician_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Matematikci bulunamadi.")
    return story.to_dict()


@router.get("/mathematicians")
async def get_all_mathematicians():
    """Tum matematikci listesini getir."""
    mathematicians = math_history_service.get_all_mathematicians()
    return [m.to_dict() for m in mathematicians]


@router.get("/puzzle")
async def get_daily_puzzle():
    """Gunun bulmacasini getir."""
    try:
        puzzle = math_puzzle_service.get_daily_puzzle()
        return puzzle.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/puzzle/{puzzle_id}/check")
async def check_puzzle_answer(puzzle_id: str, req: CheckPuzzleRequest):
    """Bulmaca cevabini kontrol et."""
    result = math_puzzle_service.check_puzzle_answer(puzzle_id, req.answer)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail="Bulmaca bulunamadi.")
    return result


@router.get("/puzzle/{puzzle_id}/hint")
async def get_puzzle_hint(puzzle_id: str, hint_index: int = 0):
    """Bulmaca ipucu getir."""
    hint = math_puzzle_service.get_puzzle_hint(puzzle_id, hint_index)
    if hint is None:
        raise HTTPException(status_code=404, detail="Ipucu bulunamadi.")
    return {"hint": hint}


@router.get("/certificates/{user_id}")
async def get_user_certificates(user_id: str):
    """Kullanicinin sertifikalarini getir."""
    certs = certificate_service.get_user_certificates(user_id)
    return [c.to_dict() for c in certs]


@router.post("/certificates/generate")
async def generate_certificate(req: GenerateCertificateRequest):
    """Sertifika olustur."""
    try:
        cert = certificate_service.generate_certificate(
            user_id=req.user_id,
            topic=req.topic,
            mastery=req.mastery,
        )
        return cert.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/seasonal")
async def get_current_season():
    """Mevcut mevsim ve temasini getir."""
    season = seasonal_content_service.get_current_season()
    return season


@router.get("/seasonal/challenges")
async def get_seasonal_challenges():
    """Mevsimsel gorevleri getir."""
    challenges = seasonal_content_service.get_seasonal_challenges()
    return challenges


@router.get("/seasonal/holiday/{holiday_id}")
async def get_holiday_content(holiday_id: str):
    """Tatil icerigini getir."""
    content = seasonal_content_service.get_holiday_content(holiday_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Tatil icerigi bulunamadi.")
    return content
