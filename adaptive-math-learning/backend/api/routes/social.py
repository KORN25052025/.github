"""Social and Competition API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ...services.social_service import (
    DuelService, TournamentService, FriendService, WeeklyCompetitionService,
)

router = APIRouter(prefix="/social", tags=["Social & Competition"])

# Service instances
duel_service = DuelService()
tournament_service = TournamentService()
friend_service = FriendService()
weekly_competition_service = WeeklyCompetitionService()


class CreateDuelRequest(BaseModel):
    challenger_id: str
    opponent_id: str
    topic: Optional[str] = None
    question_count: int = 5

class JoinDuelRequest(BaseModel):
    user_id: str

class DuelAnswerRequest(BaseModel):
    user_id: str
    question_id: str
    answer: str

class CreateTournamentRequest(BaseModel):
    creator_id: str
    name: str
    topic: Optional[str] = None
    max_participants: int = 10

class JoinTournamentRequest(BaseModel):
    user_id: str

class FriendRequestModel(BaseModel):
    from_user_id: str
    to_user_id: str


@router.post("/duel/create")
async def create_duel(req: CreateDuelRequest):
    """Duello olustur."""
    try:
        duel = duel_service.create_duel(
            challenger_id=req.challenger_id,
            opponent_id=req.opponent_id,
            topic=req.topic,
            question_count=req.question_count,
        )
        return duel
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/duel/join/{duel_id}")
async def join_duel(duel_id: str, req: JoinDuelRequest):
    """Duelloya katil."""
    try:
        result = duel_service.join_duel(duel_id=duel_id, user_id=req.user_id)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Duello bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/duel/answer/{duel_id}")
async def submit_duel_answer(duel_id: str, req: DuelAnswerRequest):
    """Duello cevabi gonder."""
    try:
        result = duel_service.submit_duel_answer(
            duel_id=duel_id,
            user_id=req.user_id,
            question_id=req.question_id,
            answer=req.answer,
        )
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Duello bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/duel/status/{duel_id}")
async def get_duel_status(duel_id: str):
    """Duello durumunu getir."""
    try:
        status = duel_service.get_duel_status(duel_id)
        return status
    except KeyError:
        raise HTTPException(status_code=404, detail="Duello bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tournament/create")
async def create_tournament(req: CreateTournamentRequest):
    """Turnuva olustur."""
    try:
        tournament = tournament_service.create_tournament(
            creator_id=req.creator_id,
            name=req.name,
            topic=req.topic,
            max_participants=req.max_participants,
        )
        return tournament
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tournament/join/{tournament_id}")
async def join_tournament(tournament_id: str, req: JoinTournamentRequest):
    """Turnuvaya katil."""
    try:
        result = tournament_service.join_tournament(
            tournament_id=tournament_id,
            user_id=req.user_id,
        )
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Turnuva bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tournament/leaderboard/{tournament_id}")
async def get_tournament_leaderboard(tournament_id: str):
    """Turnuva siralama tablosunu getir."""
    try:
        leaderboard = tournament_service.get_tournament_leaderboard(tournament_id)
        return leaderboard
    except KeyError:
        raise HTTPException(status_code=404, detail="Turnuva bulunamadi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/friends/request")
async def send_friend_request(req: FriendRequestModel):
    """Arkadaslik istegi gonder."""
    try:
        result = friend_service.send_friend_request(
            from_user_id=req.from_user_id,
            to_user_id=req.to_user_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/friends/{user_id}")
async def get_friends(user_id: str):
    """Arkadas listesini getir."""
    try:
        friends = friend_service.get_friends(user_id)
        return friends
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/weekly")
async def get_current_competition():
    """Haftalik yarisma bilgilerini getir."""
    try:
        competition = weekly_competition_service.get_current_competition()
        return competition
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
