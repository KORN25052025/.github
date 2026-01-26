"""
Gamification API routes - XP, badges, streaks, leaderboard.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

from ...gamification.xp_system import XPSystem, XPEvent
from ...gamification.badges import BadgeSystem
from ...gamification.streaks import StreakTracker
from ...gamification.leaderboard import Leaderboard, LeaderboardType

router = APIRouter(prefix="/gamification", tags=["Gamification"])


# Pydantic models
class XPAwardRequest(BaseModel):
    user_id: str
    xp_amount: int
    reason: str = "manual"


# Level name helper
LEVEL_NAMES = {
    range(1, 6): "Baslangic",
    range(6, 11): "Cirak",
    range(11, 21): "Orta",
    range(21, 36): "Ileri",
    range(36, 51): "Uzman",
    range(51, 76): "Usta",
    range(76, 101): "Efsane",
}


def _level_name(level: int) -> str:
    for r, name in LEVEL_NAMES.items():
        if level in r:
            return name
    return "Efsane"


# Initialize systems
xp_system = XPSystem()
badge_system = BadgeSystem()
streak_manager = StreakTracker()
leaderboard = Leaderboard()


@router.get("/xp/{user_id}")
async def get_user_xp(user_id: str):
    """Get XP and level info for a user."""
    xp_data = xp_system.to_dict(user_id)
    return {
        "user_id": user_id,
        "total_xp": xp_data.get("total_xp", 0),
        "level": xp_data.get("level", 1),
        "xp_this_level": xp_data.get("xp_this_level", 0),
        "xp_to_next_level": xp_data.get("xp_to_next_level", 100),
        "level_name": _level_name(xp_data.get("level", 1)),
    }


@router.post("/xp/award")
async def award_xp(request: XPAwardRequest):
    """Award XP to a user."""
    record = xp_system.get_record(request.user_id)
    old_level = record.level
    record.total_xp += request.xp_amount
    record.xp_today += request.xp_amount
    record.xp_this_week += request.xp_amount
    record.xp_this_month += request.xp_amount
    xp_system._update_level(record)
    leveled_up = record.level > old_level

    return {
        "success": True,
        "xp_awarded": request.xp_amount,
        "new_total": record.total_xp,
        "level_up": leveled_up,
        "new_level": record.level,
    }


@router.get("/badges/{user_id}")
async def get_user_badges(user_id: str):
    """Get all badges and their status for a user."""
    earned = badge_system.get_earned_badges(user_id)
    available = badge_system.get_available_badges(user_id)
    all_badges = [
        {**b, "earned": True} for b in earned
    ] + [
        {**b, "earned": False} for b in available
    ]
    return {"user_id": user_id, "badges": all_badges}


@router.post("/badges/check/{user_id}")
async def check_badges(user_id: str):
    """Check and award any newly earned badges."""
    # Provide empty stats - badges will be checked against current state
    new_badges = badge_system.check_and_award(user_id, stats={})
    return {
        "user_id": user_id,
        "new_badges": [{"name": b.name, "icon": b.icon} for b in new_badges],
        "badges_earned": len(new_badges),
    }


@router.get("/streak/{user_id}")
async def get_user_streak(user_id: str):
    """Get streak info for a user."""
    streak_data = streak_manager.get_streak_status(user_id)
    daily = streak_data.get("daily_streak", {})
    return {
        "user_id": user_id,
        "current_streak": daily.get("current", 0),
        "best_streak": daily.get("best", 0),
        "last_activity": streak_data.get("last_practice"),
        "streak_alive": not daily.get("at_risk", True),
    }


@router.post("/streak/{user_id}/update")
async def update_streak(user_id: str):
    """Update streak for user activity."""
    result = streak_manager.update_daily_streak(user_id)
    return {
        "success": True,
        "current_streak": result.get("current_daily_streak", 0),
        "best_streak": result.get("best_daily_streak", 0),
        "streak_at_risk": result.get("streak_at_risk", False),
    }


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, offset: int = 0):
    """Get the global leaderboard."""
    entries = leaderboard.get_leaderboard(
        LeaderboardType.ALL_TIME_XP, limit=limit, offset=offset
    )
    return {
        "entries": entries,
        "total_users": len(leaderboard._user_stats),
    }


@router.get("/leaderboard/{user_id}/rank")
async def get_user_rank(user_id: str):
    """Get a user's rank on the leaderboard."""
    rank_data = leaderboard.get_user_rank(user_id, LeaderboardType.ALL_TIME_XP)
    if rank_data is None:
        return {
            "user_id": user_id,
            "rank": 0,
            "total_xp": 0,
            "percentile": 0,
        }
    return {
        "user_id": user_id,
        "rank": rank_data.get("rank", 0),
        "total_xp": rank_data.get("value", 0),
        "percentile": rank_data.get("percentile", 0),
    }


@router.get("/summary/{user_id}")
async def get_gamification_summary(user_id: str):
    """Get complete gamification summary for a user."""
    xp_data = xp_system.to_dict(user_id)
    streak_data = streak_manager.get_streak_status(user_id)
    earned_badges = badge_system.get_earned_badges(user_id)
    badge_count = badge_system.get_badge_count(user_id)
    rank_data = leaderboard.get_user_rank(user_id, LeaderboardType.ALL_TIME_XP)

    daily = streak_data.get("daily_streak", {})
    level = xp_data.get("level", 1)

    return {
        "user_id": user_id,
        "xp": {
            "total": xp_data.get("total_xp", 0),
            "level": level,
            "level_name": _level_name(level),
            "progress_to_next": xp_data.get("xp_this_level", 0) / max(xp_data.get("xp_to_next_level", 100), 1),
        },
        "streak": {
            "current": daily.get("current", 0),
            "best": daily.get("best", 0),
            "alive": not daily.get("at_risk", True),
        },
        "badges": {
            "earned_count": badge_count.get("earned", 0),
            "total_count": badge_count.get("total", 0),
            "recent": earned_badges[:5],
        },
        "rank": rank_data.get("rank", 0) if rank_data else 0,
    }
