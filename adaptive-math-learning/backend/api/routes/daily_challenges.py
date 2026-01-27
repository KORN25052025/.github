"""Daily Challenges API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ...gamification.daily_challenges import daily_challenge_system, ChallengeType

router = APIRouter(prefix="/challenges", tags=["Daily Challenges"])


class RecordAnswerRequest(BaseModel):
    user_id: str
    is_correct: bool
    topic_slug: str
    response_time_ms: int = 0
    current_streak: int = 0


class UpdateProgressRequest(BaseModel):
    user_id: str
    challenge_type: str
    value: int = 1
    topic_slug: Optional[str] = None


class RecordMasteryRequest(BaseModel):
    user_id: str
    topic_slug: str
    mastery_percent: int


@router.get("/daily/{user_id}")
async def get_daily_challenges(user_id: str):
    """Gunluk gorevleri getir."""
    try:
        challenges = daily_challenge_system.get_daily_challenges(user_id)
        return {"challenges": challenges}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/weekly/{user_id}")
async def get_weekly_challenges(user_id: str):
    """Haftalik gorevleri getir."""
    try:
        challenges = daily_challenge_system.get_weekly_challenges(user_id)
        return {"challenges": challenges}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/record-answer")
async def record_answer(req: RecordAnswerRequest):
    """Cevap kaydet ve gorev ilerlemesini guncelle."""
    try:
        completed = daily_challenge_system.record_answer(
            user_id=req.user_id,
            is_correct=req.is_correct,
            topic_slug=req.topic_slug,
            response_time_ms=req.response_time_ms,
            current_streak=req.current_streak,
        )
        return {"completed_challenges": completed}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-progress")
async def update_progress(req: UpdateProgressRequest):
    """Gorev ilerlemesini guncelle."""
    try:
        challenge_type = ChallengeType(req.challenge_type)
        completed = daily_challenge_system.update_progress(
            user_id=req.user_id,
            challenge_type=challenge_type,
            value=req.value,
            topic_slug=req.topic_slug,
        )
        return {"completed_challenges": completed}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/record-mastery")
async def record_mastery(req: RecordMasteryRequest):
    """Ustalık guncellemesi kaydet."""
    try:
        completed = daily_challenge_system.record_mastery_update(
            user_id=req.user_id,
            topic_slug=req.topic_slug,
            mastery_percent=req.mastery_percent,
        )
        return {"completed_challenges": completed}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset/{user_id}")
async def reset_daily(user_id: str):
    """Gunluk gorev ilerlemesini sifirla."""
    try:
        daily_challenge_system.reset_daily_progress(user_id)
        return {"status": "reset", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
