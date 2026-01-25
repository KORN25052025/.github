"""
Gamification API routes - XP, badges, streaks, leaderboard.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from ...database import get_db
from ...gamification.xp_system import XPSystem
from ...gamification.badges import BadgeSystem, BadgeType
from ...gamification.streaks import StreakManager
from ...gamification.leaderboard import Leaderboard

router = APIRouter(prefix="/gamification", tags=["Gamification"])


# Pydantic models for responses
class XPResponse(BaseModel):
    user_id: str
    total_xp: int
    level: int
    xp_this_level: int
    xp_to_next_level: int
    level_name: str


class BadgeResponse(BaseModel):
    badge_type: str
    name: str
    description: str
    icon: str
    earned: bool
    earned_at: Optional[str] = None
    progress: Optional[float] = None


class StreakResponse(BaseModel):
    user_id: str
    current_streak: int
    best_streak: int
    last_activity: Optional[str] = None
    streak_alive: bool


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    display_name: str
    total_xp: int
    level: int


class XPAwardRequest(BaseModel):
    user_id: str
    xp_amount: int
    reason: str


# Initialize systems
xp_system = XPSystem()
badge_system = BadgeSystem()
streak_manager = StreakManager()
leaderboard = Leaderboard()


@router.get("/xp/{user_id}", response_model=XPResponse)
async def get_user_xp(user_id: str):
    """Get XP and level info for a user."""
    xp_data = xp_system.get_user_xp(user_id)
    return XPResponse(
        user_id=user_id,
        total_xp=xp_data.get("total_xp", 0),
        level=xp_data.get("level", 1),
        xp_this_level=xp_data.get("xp_this_level", 0),
        xp_to_next_level=xp_data.get("xp_to_next_level", 100),
        level_name=xp_data.get("level_name", "Beginner"),
    )


@router.post("/xp/award")
async def award_xp(request: XPAwardRequest):
    """Award XP to a user."""
    result = xp_system.award_xp(
        user_id=request.user_id,
        xp_amount=request.xp_amount,
        reason=request.reason,
    )
    return {
        "success": True,
        "xp_awarded": request.xp_amount,
        "new_total": result.get("total_xp", 0),
        "level_up": result.get("level_up", False),
        "new_level": result.get("level", 1),
    }


@router.get("/badges/{user_id}")
async def get_user_badges(user_id: str):
    """Get all badges and their status for a user."""
    badges = badge_system.get_user_badges(user_id)
    return {"user_id": user_id, "badges": badges}


@router.post("/badges/check/{user_id}")
async def check_badges(user_id: str):
    """Check and award any newly earned badges."""
    new_badges = badge_system.check_and_award_badges(user_id)
    return {
        "user_id": user_id,
        "new_badges": new_badges,
        "badges_earned": len(new_badges),
    }


@router.get("/streak/{user_id}", response_model=StreakResponse)
async def get_user_streak(user_id: str):
    """Get streak info for a user."""
    streak_data = streak_manager.get_streak(user_id)
    return StreakResponse(
        user_id=user_id,
        current_streak=streak_data.get("current_streak", 0),
        best_streak=streak_data.get("best_streak", 0),
        last_activity=streak_data.get("last_activity"),
        streak_alive=streak_data.get("streak_alive", False),
    )


@router.post("/streak/{user_id}/update")
async def update_streak(user_id: str):
    """Update streak for user activity."""
    result = streak_manager.record_activity(user_id)
    return {
        "success": True,
        "current_streak": result.get("current_streak", 0),
        "streak_extended": result.get("streak_extended", False),
        "streak_bonus_xp": result.get("bonus_xp", 0),
    }


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, offset: int = 0):
    """Get the global leaderboard."""
    entries = leaderboard.get_top_users(limit=limit, offset=offset)
    return {
        "entries": entries,
        "total_users": leaderboard.get_total_users(),
    }


@router.get("/leaderboard/{user_id}/rank")
async def get_user_rank(user_id: str):
    """Get a user's rank on the leaderboard."""
    rank_data = leaderboard.get_user_rank(user_id)
    return {
        "user_id": user_id,
        "rank": rank_data.get("rank", 0),
        "total_xp": rank_data.get("total_xp", 0),
        "percentile": rank_data.get("percentile", 0),
    }


@router.get("/summary/{user_id}")
async def get_gamification_summary(user_id: str):
    """Get complete gamification summary for a user."""
    xp_data = xp_system.get_user_xp(user_id)
    streak_data = streak_manager.get_streak(user_id)
    badges = badge_system.get_user_badges(user_id)
    rank_data = leaderboard.get_user_rank(user_id)

    earned_badges = [b for b in badges if b.get("earned", False)]

    return {
        "user_id": user_id,
        "xp": {
            "total": xp_data.get("total_xp", 0),
            "level": xp_data.get("level", 1),
            "level_name": xp_data.get("level_name", "Beginner"),
            "progress_to_next": xp_data.get("xp_this_level", 0) / max(xp_data.get("xp_to_next_level", 100), 1),
        },
        "streak": {
            "current": streak_data.get("current_streak", 0),
            "best": streak_data.get("best_streak", 0),
            "alive": streak_data.get("streak_alive", False),
        },
        "badges": {
            "earned_count": len(earned_badges),
            "total_count": len(badges),
            "recent": earned_badges[:5],
        },
        "rank": rank_data.get("rank", 0),
    }
