"""
Social and Competitive Features Service for Adaptive Math Learning Platform.

Provides duel (duello), tournament (turnuva), friend (arkadas), and weekly
competition (haftalik yarisma) functionality designed for Turkish K-12 math
students.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DuelStatus(Enum):
    """Lifecycle states of a 1-v-1 duel."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TournamentStatus(Enum):
    """Lifecycle states of a tournament."""
    REGISTRATION = "registration"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FriendRequestStatus(Enum):
    """States of a friend request."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# XP / Reward Constants
# ---------------------------------------------------------------------------

XP_DUEL_WIN = 50
XP_DUEL_LOSS = 10
XP_DUEL_DRAW = 25
XP_DUEL_PARTICIPATION = 5
XP_TOURNAMENT_FIRST = 150
XP_TOURNAMENT_SECOND = 100
XP_TOURNAMENT_THIRD = 75
XP_TOURNAMENT_PARTICIPATION = 20
XP_WEEKLY_FIRST = 200
XP_WEEKLY_SECOND = 130
XP_WEEKLY_THIRD = 90
XP_WEEKLY_PARTICIPATION = 15
XP_CORRECT_ANSWER_BASE = 10
XP_SPEED_BONUS_THRESHOLD_SECONDS = 10

DUEL_EXPIRY_MINUTES = 30
TOURNAMENT_MIN_PARTICIPANTS = 2


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class DuelAnswer:
    """A single answer submitted during a duel."""
    user_id: str
    question_id: str
    answer: Any
    is_correct: bool = False
    time_taken_seconds: float = 0.0
    xp_earned: int = 0
    submitted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DuelSession:
    """Represents a 1-v-1 math duel between two students."""
    duel_id: str
    challenger_id: str
    opponent_id: Optional[str] = None
    topic: Optional[str] = None
    question_count: int = 5
    question_ids: List[str] = field(default_factory=list)
    status: DuelStatus = DuelStatus.PENDING
    answers: List[DuelAnswer] = field(default_factory=list)
    challenger_score: int = 0
    opponent_score: int = 0
    winner_id: Optional[str] = None
    xp_rewards: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: datetime = field(
        default_factory=lambda: datetime.utcnow() + timedelta(minutes=DUEL_EXPIRY_MINUTES)
    )


@dataclass
class TournamentParticipant:
    """Tracks a single participant inside a tournament."""
    user_id: str
    score: int = 0
    correct_answers: int = 0
    total_answers: int = 0
    total_time_seconds: float = 0.0
    xp_earned: int = 0
    joined_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Tournament:
    """A multi-player tournament, typically created by a teacher."""
    tournament_id: str
    creator_id: str
    name: str
    topic: str
    max_participants: int
    start_time: datetime
    status: TournamentStatus = TournamentStatus.REGISTRATION
    question_ids: List[str] = field(default_factory=list)
    participants: Dict[str, TournamentParticipant] = field(default_factory=dict)
    answers: List[DuelAnswer] = field(default_factory=list)
    leaderboard: List[Dict[str, Any]] = field(default_factory=list)
    prizes_awarded: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class FriendRequest:
    """A directional friend request between two users."""
    request_id: str
    from_user_id: str
    to_user_id: str
    status: FriendRequestStatus = FriendRequestStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None


@dataclass
class WeeklyCompetition:
    """A platform-wide weekly competition on a specific math topic."""
    competition_id: str
    topic: str
    title: str
    description: str
    question_ids: List[str] = field(default_factory=list)
    scores: Dict[str, int] = field(default_factory=dict)
    xp_rewards: Dict[str, int] = field(default_factory=dict)
    week_start: datetime = field(default_factory=lambda: _current_week_start())
    week_end: datetime = field(
        default_factory=lambda: _current_week_start() + timedelta(days=7)
    )
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_id(prefix: str = "") -> str:
    """Return a prefixed UUID4 string."""
    short = uuid.uuid4().hex[:12]
    return f"{prefix}_{short}" if prefix else short


def _current_week_start() -> datetime:
    """Return the Monday 00:00 UTC of the current ISO week."""
    today = datetime.utcnow().date()
    monday = today - timedelta(days=today.weekday())
    return datetime(monday.year, monday.month, monday.day)


def _check_answer(question_id: str, answer: Any) -> bool:
    """
    Placeholder answer checker.

    In production this delegates to the question_service / answer_service
    to validate the response against the stored correct answer.
    """
    # TODO: integrate with question_service.check_answer()
    return True


def _generate_questions(topic: Optional[str], count: int) -> List[str]:
    """
    Placeholder question generator.

    In production this delegates to the question_service to pull or
    generate *count* questions filtered by *topic*.
    """
    # TODO: integrate with question_service.get_questions()
    return [_generate_id("q") for _ in range(count)]


# ---------------------------------------------------------------------------
# DuelService
# ---------------------------------------------------------------------------

class DuelService:
    """Manages 1-v-1 math duels (duello) between two students."""

    def __init__(self) -> None:
        self._duels: Dict[str, DuelSession] = {}

    def create_duel(
        self,
        challenger_id: str,
        opponent_id: str,
        topic: Optional[str] = None,
        question_count: int = 5,
    ) -> DuelSession:
        """
        Create a new duel and send an invitation to the opponent.

        Args:
            challenger_id: The user who initiates the duel.
            opponent_id: The invited opponent.
            topic: Optional math topic filter (e.g. kesirler, denklemler).
            question_count: Number of questions in the duel (default 5).

        Returns:
            The newly created DuelSession.

        Raises:
            ValueError: If challenger tries to duel themselves or
                        question_count is out of range.
        """
        if challenger_id == opponent_id:
            raise ValueError("Kendinizle duello yapamazsiniz.")
        if not 1 <= question_count <= 20:
            raise ValueError("Soru sayisi 1 ile 20 arasinda olmalidir.")

        duel_id = _generate_id("duel")
        question_ids = _generate_questions(topic, question_count)

        duel = DuelSession(
            duel_id=duel_id,
            challenger_id=challenger_id,
            opponent_id=opponent_id,
            topic=topic,
            question_count=question_count,
            question_ids=question_ids,
        )
        self._duels[duel_id] = duel
        return duel

    def join_duel(self, duel_id: str, user_id: str) -> DuelSession:
        """
        The invited opponent accepts and joins the duel.

        Args:
            duel_id: Identifier of the duel to join.
            user_id: The user attempting to join.

        Returns:
            The updated DuelSession now in progress.

        Raises:
            ValueError: If the duel does not exist, is not pending,
                        the user is not the expected opponent, or
                        the invitation has expired.
        """
        duel = self._get_duel(duel_id)

        if duel.status != DuelStatus.PENDING:
            raise ValueError("Bu duello artik katilima acik degil.")

        if datetime.utcnow() > duel.expires_at:
            duel.status = DuelStatus.EXPIRED
            raise ValueError("Duello davetinin suresi dolmus.")

        if duel.opponent_id and duel.opponent_id != user_id:
            raise ValueError("Bu duelloya katilma yetkiniz yok.")

        duel.opponent_id = user_id
        duel.status = DuelStatus.IN_PROGRESS
        duel.started_at = datetime.utcnow()
        return duel

    def submit_duel_answer(
        self,
        duel_id: str,
        user_id: str,
        question_id: str,
        answer: Any,
        time_taken_seconds: float = 0.0,
    ) -> DuelAnswer:
        """
        Submit an answer for a duel question.

        Args:
            duel_id: The active duel.
            user_id: The answering player.
            question_id: Which question is being answered.
            answer: The student answer value.
            time_taken_seconds: How long the student took (seconds).

        Returns:
            A DuelAnswer recording the submission and whether it was correct.

        Raises:
            ValueError: If the duel is not in progress, the user is not a
                        participant, or the question is not part of the duel.
        """
        duel = self._get_duel(duel_id)

        if duel.status != DuelStatus.IN_PROGRESS:
            raise ValueError("Duello su anda aktif degil.")

        if user_id not in (duel.challenger_id, duel.opponent_id):
            raise ValueError("Bu duellonun katilimcisi degilsiniz.")

        if question_id not in duel.question_ids:
            raise ValueError("Bu soru duelloya ait degil.")

        already_answered = any(
            a.user_id == user_id and a.question_id == question_id
            for a in duel.answers
        )
        if already_answered:
            raise ValueError("Bu soruyu zaten cevapladiniz.")

        is_correct = _check_answer(question_id, answer)

        xp = 0
        if is_correct:
            xp = XP_CORRECT_ANSWER_BASE
            if time_taken_seconds <= XP_SPEED_BONUS_THRESHOLD_SECONDS:
                xp += 5  # speed bonus

        duel_answer = DuelAnswer(
            user_id=user_id,
            question_id=question_id,
            answer=answer,
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds,
            xp_earned=xp,
        )
        duel.answers.append(duel_answer)

        if is_correct:
            if user_id == duel.challenger_id:
                duel.challenger_score += 1
            else:
                duel.opponent_score += 1

        return duel_answer

    def get_duel_status(self, duel_id: str) -> Dict[str, Any]:
        """
        Return a snapshot of the duel current state including scores,
        question progress, status, and who is currently winning.
        """
        duel = self._get_duel(duel_id)

        challenger_answers = [
            a for a in duel.answers if a.user_id == duel.challenger_id
        ]
        opponent_answers = [
            a for a in duel.answers if a.user_id == duel.opponent_id
        ]

        if duel.challenger_score > duel.opponent_score:
            leading = duel.challenger_id
        elif duel.opponent_score > duel.challenger_score:
            leading = duel.opponent_id
        else:
            leading = None  # tied

        return {
            "duel_id": duel.duel_id,
            "status": duel.status.value,
            "topic": duel.topic,
            "question_count": duel.question_count,
            "challenger": {
                "user_id": duel.challenger_id,
                "score": duel.challenger_score,
                "answers_submitted": len(challenger_answers),
            },
            "opponent": {
                "user_id": duel.opponent_id,
                "score": duel.opponent_score,
                "answers_submitted": len(opponent_answers),
            },
            "leading": leading,
            "winner_id": duel.winner_id,
            "created_at": duel.created_at.isoformat(),
            "started_at": duel.started_at.isoformat() if duel.started_at else None,
            "completed_at": duel.completed_at.isoformat() if duel.completed_at else None,
        }

    def complete_duel(self, duel_id: str) -> DuelSession:
        """
        Finalize the duel: determine the winner and award XP.

        Returns:
            The completed DuelSession with winner and XP rewards set.

        Raises:
            ValueError: If the duel is not in progress.
        """
        duel = self._get_duel(duel_id)

        if duel.status != DuelStatus.IN_PROGRESS:
            raise ValueError("Sadece devam eden duellolar tamamlanabilir.")

        if duel.challenger_score > duel.opponent_score:
            duel.winner_id = duel.challenger_id
            winner_id = duel.challenger_id
            loser_id = duel.opponent_id
        elif duel.opponent_score > duel.challenger_score:
            duel.winner_id = duel.opponent_id
            winner_id = duel.opponent_id
            loser_id = duel.challenger_id
        else:
            duel.winner_id = None
            winner_id = None
            loser_id = None

        ch_xp = sum(a.xp_earned for a in duel.answers if a.user_id == duel.challenger_id)
        op_xp = sum(a.xp_earned for a in duel.answers if a.user_id == duel.opponent_id)

        if winner_id is None:
            duel.xp_rewards[duel.challenger_id] = XP_DUEL_DRAW + XP_DUEL_PARTICIPATION + ch_xp
            duel.xp_rewards[duel.opponent_id] = XP_DUEL_DRAW + XP_DUEL_PARTICIPATION + op_xp
        else:
            w_axp = ch_xp if winner_id == duel.challenger_id else op_xp
            l_axp = ch_xp if loser_id == duel.challenger_id else op_xp
            duel.xp_rewards[winner_id] = XP_DUEL_WIN + XP_DUEL_PARTICIPATION + w_axp
            duel.xp_rewards[loser_id] = XP_DUEL_LOSS + XP_DUEL_PARTICIPATION + l_axp

        duel.status = DuelStatus.COMPLETED
        duel.completed_at = datetime.utcnow()
        return duel

    def get_duel_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Return a list of past duels for a given user with summarised results.

        Each entry includes duel id, opponent, result (win/loss/draw), scores,
        topic, and XP earned.
        """
        history: List[Dict[str, Any]] = []
        for duel in self._duels.values():
            if user_id not in (duel.challenger_id, duel.opponent_id):
                continue

            is_challenger = user_id == duel.challenger_id
            opponent_id = duel.opponent_id if is_challenger else duel.challenger_id
            user_score = duel.challenger_score if is_challenger else duel.opponent_score
            opponent_score = duel.opponent_score if is_challenger else duel.challenger_score

            if duel.winner_id == user_id:
                result = "win"
            elif duel.winner_id is None and duel.status == DuelStatus.COMPLETED:
                result = "draw"
            elif duel.status == DuelStatus.COMPLETED:
                result = "loss"
            else:
                result = duel.status.value

            history.append({
                "duel_id": duel.duel_id,
                "opponent_id": opponent_id,
                "result": result,
                "user_score": user_score,
                "opponent_score": opponent_score,
                "topic": duel.topic,
                "xp_earned": duel.xp_rewards.get(user_id, 0),
                "status": duel.status.value,
                "created_at": duel.created_at.isoformat(),
                "completed_at": duel.completed_at.isoformat() if duel.completed_at else None,
            })

        history.sort(key=lambda h: h["created_at"], reverse=True)
        return history

    def _get_duel(self, duel_id: str) -> DuelSession:
        """Retrieve a duel by ID or raise ValueError."""
        duel = self._duels.get(duel_id)
        if duel is None:
            raise ValueError(f"Duello bulunamadi: {duel_id}")
        return duel


# ---------------------------------------------------------------------------
# TournamentService
# ---------------------------------------------------------------------------

class TournamentService:
    """Manages multi-player tournaments (turnuva) typically created by teachers."""

    def __init__(self) -> None:
        self._tournaments: Dict[str, Tournament] = {}

    def create_tournament(
        self,
        creator_id: str,
        name: str,
        topic: str,
        max_participants: int = 30,
        start_time: Optional[datetime] = None,
        question_count: int = 10,
    ) -> Tournament:
        """
        Create a new tournament.

        Args:
            creator_id: The teacher or admin creating the tournament.
            name: Display name (e.g. 5. Sinif Kesirler Turnuvasi).
            topic: Math topic the questions will cover.
            max_participants: Upper limit on registrations.
            start_time: Scheduled start; defaults to 1 hour from now.
            question_count: Number of questions in the tournament.

        Returns:
            The newly created Tournament in REGISTRATION status.
        """
        if max_participants < TOURNAMENT_MIN_PARTICIPANTS:
            raise ValueError(
                f"Turnuva en az {TOURNAMENT_MIN_PARTICIPANTS} katilimciya ihtiyac duyar."
            )

        if start_time is None:
            start_time = datetime.utcnow() + timedelta(hours=1)

        tournament_id = _generate_id("trn")
        question_ids = _generate_questions(topic, question_count)

        tournament = Tournament(
            tournament_id=tournament_id,
            creator_id=creator_id,
            name=name,
            topic=topic,
            max_participants=max_participants,
            start_time=start_time,
            question_ids=question_ids,
        )
        self._tournaments[tournament_id] = tournament
        return tournament

    def join_tournament(self, tournament_id: str, user_id: str) -> Tournament:
        """
        Register a student for a tournament.

        Raises:
            ValueError: If the tournament is not accepting registrations or
                        the participant cap has been reached.
        """
        tournament = self._get_tournament(tournament_id)

        if tournament.status != TournamentStatus.REGISTRATION:
            raise ValueError("Bu turnuva su anda kayit almiyor.")

        if len(tournament.participants) >= tournament.max_participants:
            raise ValueError("Turnuva katilimci kapasitesine ulasti.")

        if user_id in tournament.participants:
            raise ValueError("Zaten bu turnuvaya kayitlisiniz.")

        tournament.participants[user_id] = TournamentParticipant(user_id=user_id)
        return tournament

    def start_tournament(self, tournament_id: str) -> Tournament:
        """
        Transition the tournament from REGISTRATION to IN_PROGRESS.

        Raises:
            ValueError: If minimum participant count is not met or
                        tournament is not in REGISTRATION status.
        """
        tournament = self._get_tournament(tournament_id)

        if tournament.status != TournamentStatus.REGISTRATION:
            raise ValueError("Sadece kayit asamasindaki turnuvalar baslatilabilir.")

        if len(tournament.participants) < TOURNAMENT_MIN_PARTICIPANTS:
            raise ValueError(
                f"Turnuva baslatmak icin en az {TOURNAMENT_MIN_PARTICIPANTS} "
                f"katilimci gereklidir (mevcut: {len(tournament.participants)})."
            )

        tournament.status = TournamentStatus.IN_PROGRESS
        tournament.start_time = datetime.utcnow()
        return tournament

    def submit_tournament_answer(
        self,
        tournament_id: str,
        user_id: str,
        question_id: str,
        answer: Any,
        time_taken_seconds: float = 0.0,
    ) -> DuelAnswer:
        """
        Submit an answer during an active tournament.

        Returns:
            A DuelAnswer (reused dataclass) with correctness and XP.

        Raises:
            ValueError: If the tournament is not in progress, the user is
                        not a participant, or the question is invalid.
        """
        tournament = self._get_tournament(tournament_id)

        if tournament.status != TournamentStatus.IN_PROGRESS:
            raise ValueError("Turnuva su anda aktif degil.")

        if user_id not in tournament.participants:
            raise ValueError("Bu turmuvanin katilimcisi degilsiniz.")

        if question_id not in tournament.question_ids:
            raise ValueError("Bu soru turnuvaya ait degil.")

        already_answered = any(
            a.user_id == user_id and a.question_id == question_id
            for a in tournament.answers
        )
        if already_answered:
            raise ValueError("Bu soruyu zaten cevapladiniz.")

        is_correct = _check_answer(question_id, answer)

        xp = 0
        if is_correct:
            xp = XP_CORRECT_ANSWER_BASE
            if time_taken_seconds <= XP_SPEED_BONUS_THRESHOLD_SECONDS:
                xp += 5

        duel_answer = DuelAnswer(
            user_id=user_id,
            question_id=question_id,
            answer=answer,
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds,
            xp_earned=xp,
        )
        tournament.answers.append(duel_answer)

        participant = tournament.participants[user_id]
        participant.total_answers += 1
        participant.total_time_seconds += time_taken_seconds
        if is_correct:
            participant.correct_answers += 1
            participant.score += xp

        return duel_answer

    def get_tournament_leaderboard(self, tournament_id: str) -> List[Dict[str, Any]]:
        """
        Return a live leaderboard sorted by score (desc), then by total time
        (asc) as a tiebreaker.
        """
        tournament = self._get_tournament(tournament_id)

        entries: List[Dict[str, Any]] = []
        for p in tournament.participants.values():
            entries.append({
                "user_id": p.user_id,
                "score": p.score,
                "correct_answers": p.correct_answers,
                "total_answers": p.total_answers,
                "total_time_seconds": round(p.total_time_seconds, 2),
                "xp_earned": p.xp_earned,
            })

        entries.sort(key=lambda e: (-e["score"], e["total_time_seconds"]))

        for rank, entry in enumerate(entries, start=1):
            entry["rank"] = rank

        tournament.leaderboard = entries
        return entries

    def complete_tournament(self, tournament_id: str) -> Tournament:
        """
        Finalize the tournament, compute final standings, and award XP prizes.

        Returns:
            The completed Tournament with prizes distributed.

        Raises:
            ValueError: If the tournament is not in progress.
        """
        tournament = self._get_tournament(tournament_id)

        if tournament.status != TournamentStatus.IN_PROGRESS:
            raise ValueError("Sadece devam eden turnuvalar tamamlanabilir.")

        leaderboard = self.get_tournament_leaderboard(tournament_id)

        prize_map = {
            1: XP_TOURNAMENT_FIRST,
            2: XP_TOURNAMENT_SECOND,
            3: XP_TOURNAMENT_THIRD,
        }

        for entry in leaderboard:
            user_id = entry["user_id"]
            rank = entry["rank"]
            placement_xp = prize_map.get(rank, XP_TOURNAMENT_PARTICIPATION)
            total_xp = placement_xp + entry["score"]

            participant = tournament.participants[user_id]
            participant.xp_earned = total_xp
            entry["xp_earned"] = total_xp

        tournament.leaderboard = leaderboard
        tournament.prizes_awarded = True
        tournament.status = TournamentStatus.COMPLETED
        tournament.completed_at = datetime.utcnow()
        return tournament

    def _get_tournament(self, tournament_id: str) -> Tournament:
        """Retrieve a tournament by ID or raise ValueError."""
        tournament = self._tournaments.get(tournament_id)
        if tournament is None:
            raise ValueError(f"Turnuva bulunamadi: {tournament_id}")
        return tournament


# ---------------------------------------------------------------------------
# FriendService
# ---------------------------------------------------------------------------

class FriendService:
    """Manages friendships and friend requests between students."""

    def __init__(self) -> None:
        self._requests: Dict[str, FriendRequest] = {}
        # Adjacency set: user_id -> set of friend user_ids
        self._friends: Dict[str, set] = {}

    def send_friend_request(self, from_user_id: str, to_user_id: str) -> FriendRequest:
        """
        Send a friend request from one user to another.

        Raises:
            ValueError: If the user tries to befriend themselves, a pending
                        request already exists, or they are already friends.
        """
        if from_user_id == to_user_id:
            raise ValueError("Kendinize arkadaslik istegi gonderemezsiniz.")

        if to_user_id in self._friends.get(from_user_id, set()):
            raise ValueError("Bu kullaniciyla zaten arkadassiniz.")

        for req in self._requests.values():
            if req.status != FriendRequestStatus.PENDING:
                continue
            if (
                (req.from_user_id == from_user_id and req.to_user_id == to_user_id)
                or (req.from_user_id == to_user_id and req.to_user_id == from_user_id)
            ):
                raise ValueError("Bu kullaniciya zaten bekleyen bir istek var.")

        request_id = _generate_id("freq")
        request = FriendRequest(
            request_id=request_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )
        self._requests[request_id] = request
        return request

    def accept_friend_request(self, request_id: str) -> FriendRequest:
        """
        Accept a pending friend request, establishing a mutual friendship.

        Raises:
            ValueError: If the request is not found or not pending.
        """
        request = self._get_request(request_id)

        if request.status != FriendRequestStatus.PENDING:
            raise ValueError("Bu istek zaten yanitlanmis.")

        request.status = FriendRequestStatus.ACCEPTED
        request.responded_at = datetime.utcnow()

        self._friends.setdefault(request.from_user_id, set()).add(request.to_user_id)
        self._friends.setdefault(request.to_user_id, set()).add(request.from_user_id)

        return request

    def reject_friend_request(self, request_id: str) -> FriendRequest:
        """
        Reject a pending friend request.

        Raises:
            ValueError: If the request is not found or not pending.
        """
        request = self._get_request(request_id)

        if request.status != FriendRequestStatus.PENDING:
            raise ValueError("Bu istek zaten yanitlanmis.")

        request.status = FriendRequestStatus.REJECTED
        request.responded_at = datetime.utcnow()
        return request

    def get_friends(self, user_id: str) -> List[str]:
        """Return a sorted list of friend user IDs for the given user."""
        return sorted(self._friends.get(user_id, set()))

    def get_friend_comparison(
        self,
        user_id: str,
        friend_id: str,
        *,
        duel_service: Optional[DuelService] = None,
    ) -> Dict[str, Any]:
        """
        Compare learning progress between two friends.

        If a DuelService is supplied, head-to-head duel stats are included.

        Raises:
            ValueError: If the users are not friends.
        """
        if friend_id not in self._friends.get(user_id, set()):
            raise ValueError("Bu kullanici arkadas listenizde degil.")

        comparison: Dict[str, Any] = {
            "user_id": user_id,
            "friend_id": friend_id,
            "compared_at": datetime.utcnow().isoformat(),
            "head_to_head": None,
        }

        if duel_service is not None:
            user_wins = 0
            friend_wins = 0
            draws = 0

            for duel in duel_service._duels.values():
                if duel.status != DuelStatus.COMPLETED:
                    continue
                participants = {duel.challenger_id, duel.opponent_id}
                if participants != {user_id, friend_id}:
                    continue

                if duel.winner_id == user_id:
                    user_wins += 1
                elif duel.winner_id == friend_id:
                    friend_wins += 1
                else:
                    draws += 1

            comparison["head_to_head"] = {
                "user_wins": user_wins,
                "friend_wins": friend_wins,
                "draws": draws,
                "total_duels": user_wins + friend_wins + draws,
            }

        return comparison

    def remove_friend(self, user_id: str, friend_id: str) -> bool:
        """
        Remove a mutual friendship.

        Returns:
            True if the friendship was removed; False if they were not friends.
        """
        user_friends = self._friends.get(user_id, set())
        friend_friends = self._friends.get(friend_id, set())

        if friend_id not in user_friends:
            return False

        user_friends.discard(friend_id)
        friend_friends.discard(user_id)
        return True

    def _get_request(self, request_id: str) -> FriendRequest:
        """Retrieve a friend request by ID or raise ValueError."""
        request = self._requests.get(request_id)
        if request is None:
            raise ValueError(f"Arkadaslik istegi bulunamadi: {request_id}")
        return request


# ---------------------------------------------------------------------------
# WeeklyCompetitionService
# ---------------------------------------------------------------------------

class WeeklyCompetitionService:
    """Manages platform-wide weekly math competitions (haftalik yarisma)."""

    # Predefined rotation of weekly topics (cycles through continuously)
    _WEEKLY_TOPICS: List[Dict[str, str]] = [
        {
            "topic": "toplama_cikarma",
            "title": "Toplama ve Cikarma Haftasi",
            "description": "Bu hafta toplama ve cikarma becerilerinizi test edin!",
        },
        {
            "topic": "carpma_bolme",
            "title": "Carpma ve Bolme Haftasi",
            "description": "Carpma ve bolme sorulariyla yarisin!",
        },
        {
            "topic": "kesirler",
            "title": "Kesirler Haftasi",
            "description": "Kesirlerde ustalasma zamani!",
        },
        {
            "topic": "geometri",
            "title": "Geometri Haftasi",
            "description": "Geometri bilginizi konusturun!",
        },
        {
            "topic": "denklemler",
            "title": "Denklemler Haftasi",
            "description": "Denklem cozme yarismasina katilin!",
        },
        {
            "topic": "oran_oranti",
            "title": "Oran ve Oranti Haftasi",
            "description": "Oran-oranti problemlerinde yarisin!",
        },
        {
            "topic": "olasilik",
            "title": "Olasilik Haftasi",
            "description": "Olasilik konusunda sansinizi deneyin!",
        },
        {
            "topic": "istatistik",
            "title": "Istatistik Haftasi",
            "description": "Veri analizi ve istatistik yarismasi!",
        },
    ]

    def __init__(self) -> None:
        self._competitions: Dict[str, WeeklyCompetition] = {}
        self._current_competition: Optional[WeeklyCompetition] = None

    def get_current_competition(self) -> WeeklyCompetition:
        """
        Return the active weekly competition.

        If no competition exists for the current week, one is automatically
        created based on the rotating topic schedule.
        """
        week_start = _current_week_start()

        # Return cached if still valid
        if (
            self._current_competition is not None
            and self._current_competition.week_start == week_start
            and self._current_competition.is_active
        ):
            return self._current_competition

        # Check stored competitions
        for comp in self._competitions.values():
            if comp.week_start == week_start and comp.is_active:
                self._current_competition = comp
                return comp

        # Create a new competition for this week
        week_number = week_start.isocalendar()[1]  # ISO week number
        topic_index = week_number % len(self._WEEKLY_TOPICS)
        topic_info = self._WEEKLY_TOPICS[topic_index]

        competition_id = _generate_id("wcomp")
        question_ids = _generate_questions(topic_info["topic"], 15)

        comp = WeeklyCompetition(
            competition_id=competition_id,
            topic=topic_info["topic"],
            title=topic_info["title"],
            description=topic_info["description"],
            question_ids=question_ids,
            week_start=week_start,
            week_end=week_start + timedelta(days=7),
        )
        self._competitions[competition_id] = comp
        self._current_competition = comp
        return comp

    def submit_score(self, user_id: str, score: int) -> Dict[str, Any]:
        """
        Submit (or update) a user score for the current weekly competition.

        Only the highest score is kept. Submitting a lower score than the
        user current best is silently ignored.

        Args:
            user_id: The competing student.
            score: The score achieved.

        Returns:
            A dict summarising the submission including whether the score
            was a new personal best.

        Raises:
            ValueError: If the competition has ended or score is negative.
        """
        if score < 0:
            raise ValueError("Puan negatif olamaz.")

        comp = self.get_current_competition()

        now = datetime.utcnow()
        if now > comp.week_end:
            comp.is_active = False
            raise ValueError("Bu haftanin yarismasi sona erdi.")

        previous_best = comp.scores.get(user_id, 0)
        is_new_best = score > previous_best

        if is_new_best:
            comp.scores[user_id] = score

        return {
            "competition_id": comp.competition_id,
            "user_id": user_id,
            "submitted_score": score,
            "personal_best": max(score, previous_best),
            "is_new_best": is_new_best,
            "topic": comp.topic,
            "title": comp.title,
        }

    def get_weekly_leaderboard(self, limit: int = 50) -> Dict[str, Any]:
        """
        Return the current week leaderboard.

        Args:
            limit: Maximum number of entries to return (default 50).

        Returns:
            A dict containing competition metadata and a ranked list of
            top performers.
        """
        comp = self.get_current_competition()

        sorted_scores: List[Tuple[str, int]] = sorted(
            comp.scores.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        entries: List[Dict[str, Any]] = []
        for rank, (user_id, score) in enumerate(sorted_scores, start=1):
            xp = self._calculate_weekly_xp(rank)
            entries.append({
                "rank": rank,
                "user_id": user_id,
                "score": score,
                "projected_xp": xp,
            })

        return {
            "competition_id": comp.competition_id,
            "topic": comp.topic,
            "title": comp.title,
            "description": comp.description,
            "week_start": comp.week_start.isoformat(),
            "week_end": comp.week_end.isoformat(),
            "total_participants": len(comp.scores),
            "leaderboard": entries,
        }

    def finalize_weekly_competition(self, competition_id: str) -> WeeklyCompetition:
        """
        Called at week end to mark the competition inactive and distribute
        XP rewards to all participants.

        Returns:
            The finalized WeeklyCompetition with xp_rewards populated.
        """
        comp = self._competitions.get(competition_id)
        if comp is None:
            raise ValueError(f"Yarisma bulunamadi: {competition_id}")

        if not comp.is_active:
            raise ValueError("Bu yarisma zaten tamamlanmis.")

        sorted_scores: List[Tuple[str, int]] = sorted(
            comp.scores.items(), key=lambda x: x[1], reverse=True
        )

        for rank, (user_id, _score) in enumerate(sorted_scores, start=1):
            comp.xp_rewards[user_id] = self._calculate_weekly_xp(rank)

        comp.is_active = False
        return comp

    @staticmethod
    def _calculate_weekly_xp(rank: int) -> int:
        """Determine XP award based on final ranking."""
        if rank == 1:
            return XP_WEEKLY_FIRST
        elif rank == 2:
            return XP_WEEKLY_SECOND
        elif rank == 3:
            return XP_WEEKLY_THIRD
        else:
            return XP_WEEKLY_PARTICIPATION

