"""
Daily Challenges System.

Provides daily quests and challenges to increase engagement and retention.
Features:
- Daily rotating challenges
- Weekly special challenges
- Streak bonuses for consecutive daily completions
- Challenge categories (speed, accuracy, mastery, exploration)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import random
import hashlib


class ChallengeType(str, Enum):
    """Types of daily challenges."""
    SPEED = "speed"           # Complete X questions in Y minutes
    ACCURACY = "accuracy"     # Get X questions correct in a row
    MASTERY = "mastery"       # Reach mastery level in a topic
    EXPLORATION = "exploration"  # Try a new topic
    STREAK = "streak"         # Maintain daily streak
    VOLUME = "volume"         # Answer X questions total
    PERFECT = "perfect"       # Get 100% on a practice session
    TIME_ATTACK = "time_attack"  # Best time for 10 questions


class ChallengeDifficulty(str, Enum):
    """Challenge difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    LEGENDARY = "legendary"


@dataclass
class Challenge:
    """A daily challenge definition."""
    id: str
    type: ChallengeType
    difficulty: ChallengeDifficulty
    title: str
    title_tr: str  # Turkish title
    description: str
    description_tr: str  # Turkish description
    target_value: int
    xp_reward: int
    icon: str
    color: str
    topic_slug: Optional[str] = None  # If challenge is topic-specific
    time_limit_minutes: Optional[int] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "difficulty": self.difficulty.value,
            "title": self.title,
            "title_tr": self.title_tr,
            "description": self.description,
            "description_tr": self.description_tr,
            "target_value": self.target_value,
            "xp_reward": self.xp_reward,
            "icon": self.icon,
            "color": self.color,
            "topic_slug": self.topic_slug,
            "time_limit_minutes": self.time_limit_minutes,
        }


@dataclass
class ChallengeProgress:
    """Tracks progress on a challenge."""
    challenge_id: str
    user_id: str
    current_value: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    is_completed: bool = False

    @property
    def progress_percent(self) -> float:
        return min(100, (self.current_value / max(1, 1)) * 100)


# Challenge Templates
CHALLENGE_TEMPLATES: List[Challenge] = [
    # Speed Challenges
    Challenge(
        id="speed_10_5",
        type=ChallengeType.SPEED,
        difficulty=ChallengeDifficulty.EASY,
        title="Quick Thinker",
        title_tr="Hizli Dusunur",
        description="Answer 10 questions in 5 minutes",
        description_tr="5 dakikada 10 soru coz",
        target_value=10,
        xp_reward=50,
        icon="flash",
        color="#F59E0B",
        time_limit_minutes=5,
    ),
    Challenge(
        id="speed_20_8",
        type=ChallengeType.SPEED,
        difficulty=ChallengeDifficulty.MEDIUM,
        title="Speed Demon",
        title_tr="Hiz Seytani",
        description="Answer 20 questions in 8 minutes",
        description_tr="8 dakikada 20 soru coz",
        target_value=20,
        xp_reward=100,
        icon="rocket",
        color="#EF4444",
        time_limit_minutes=8,
    ),

    # Accuracy Challenges
    Challenge(
        id="accuracy_5",
        type=ChallengeType.ACCURACY,
        difficulty=ChallengeDifficulty.EASY,
        title="Sharp Mind",
        title_tr="Keskin Zihin",
        description="Get 5 questions correct in a row",
        description_tr="Ust uste 5 dogru cevap ver",
        target_value=5,
        xp_reward=40,
        icon="checkmark-circle",
        color="#10B981",
    ),
    Challenge(
        id="accuracy_10",
        type=ChallengeType.ACCURACY,
        difficulty=ChallengeDifficulty.MEDIUM,
        title="Precision Master",
        title_tr="Hassasiyet Ustasi",
        description="Get 10 questions correct in a row",
        description_tr="Ust uste 10 dogru cevap ver",
        target_value=10,
        xp_reward=100,
        icon="ribbon",
        color="#8B5CF6",
    ),
    Challenge(
        id="accuracy_20",
        type=ChallengeType.ACCURACY,
        difficulty=ChallengeDifficulty.HARD,
        title="Flawless",
        title_tr="Kusursuz",
        description="Get 20 questions correct in a row",
        description_tr="Ust uste 20 dogru cevap ver",
        target_value=20,
        xp_reward=250,
        icon="trophy",
        color="#F59E0B",
    ),

    # Volume Challenges
    Challenge(
        id="volume_15",
        type=ChallengeType.VOLUME,
        difficulty=ChallengeDifficulty.EASY,
        title="Dedicated Learner",
        title_tr="Adanmis Ogrenci",
        description="Answer 15 questions today",
        description_tr="Bugun 15 soru coz",
        target_value=15,
        xp_reward=30,
        icon="school",
        color="#4F46E5",
    ),
    Challenge(
        id="volume_30",
        type=ChallengeType.VOLUME,
        difficulty=ChallengeDifficulty.MEDIUM,
        title="Math Marathon",
        title_tr="Matematik Maratonu",
        description="Answer 30 questions today",
        description_tr="Bugun 30 soru coz",
        target_value=30,
        xp_reward=75,
        icon="fitness",
        color="#06B6D4",
    ),
    Challenge(
        id="volume_50",
        type=ChallengeType.VOLUME,
        difficulty=ChallengeDifficulty.HARD,
        title="Unstoppable",
        title_tr="Durdurulamaz",
        description="Answer 50 questions today",
        description_tr="Bugun 50 soru coz",
        target_value=50,
        xp_reward=150,
        icon="flame",
        color="#EF4444",
    ),

    # Exploration Challenges
    Challenge(
        id="explore_2",
        type=ChallengeType.EXPLORATION,
        difficulty=ChallengeDifficulty.EASY,
        title="Explorer",
        title_tr="Kasif",
        description="Practice 2 different topics today",
        description_tr="Bugun 2 farkli konuda calis",
        target_value=2,
        xp_reward=40,
        icon="compass",
        color="#10B981",
    ),
    Challenge(
        id="explore_4",
        type=ChallengeType.EXPLORATION,
        difficulty=ChallengeDifficulty.MEDIUM,
        title="Well-Rounded",
        title_tr="Cok Yonlu",
        description="Practice 4 different topics today",
        description_tr="Bugun 4 farkli konuda calis",
        target_value=4,
        xp_reward=100,
        icon="globe",
        color="#8B5CF6",
    ),

    # Perfect Session Challenges
    Challenge(
        id="perfect_5",
        type=ChallengeType.PERFECT,
        difficulty=ChallengeDifficulty.MEDIUM,
        title="Perfect Five",
        title_tr="Mukemmel Bes",
        description="Get 100% accuracy on 5 questions",
        description_tr="5 soruda %100 basari",
        target_value=5,
        xp_reward=60,
        icon="star",
        color="#F59E0B",
    ),
    Challenge(
        id="perfect_10",
        type=ChallengeType.PERFECT,
        difficulty=ChallengeDifficulty.HARD,
        title="Perfect Ten",
        title_tr="Mukemmel On",
        description="Get 100% accuracy on 10 questions",
        description_tr="10 soruda %100 basari",
        target_value=10,
        xp_reward=150,
        icon="medal",
        color="#EF4444",
    ),

    # Topic-Specific Challenges
    Challenge(
        id="arithmetic_master",
        type=ChallengeType.MASTERY,
        difficulty=ChallengeDifficulty.MEDIUM,
        title="Arithmetic Ace",
        title_tr="Aritmetik Asi",
        description="Reach 60% mastery in Arithmetic",
        description_tr="Aritmetikte %60 ustalık",
        target_value=60,
        xp_reward=100,
        icon="calculator",
        color="#4F46E5",
        topic_slug="arithmetic",
    ),
    Challenge(
        id="algebra_master",
        type=ChallengeType.MASTERY,
        difficulty=ChallengeDifficulty.HARD,
        title="Algebra Wizard",
        title_tr="Cebir Sihirbazi",
        description="Reach 50% mastery in Algebra",
        description_tr="Cebirde %50 ustalık",
        target_value=50,
        xp_reward=150,
        icon="code-slash",
        color="#EF4444",
        topic_slug="algebra",
    ),
    Challenge(
        id="geometry_master",
        type=ChallengeType.MASTERY,
        difficulty=ChallengeDifficulty.HARD,
        title="Geometry Guru",
        title_tr="Geometri Gurusu",
        description="Reach 50% mastery in Geometry",
        description_tr="Geometride %50 ustalık",
        target_value=50,
        xp_reward=150,
        icon="shapes",
        color="#8B5CF6",
        topic_slug="geometry",
    ),
]

# Weekly Special Challenges
WEEKLY_CHALLENGES: List[Challenge] = [
    Challenge(
        id="weekly_100",
        type=ChallengeType.VOLUME,
        difficulty=ChallengeDifficulty.HARD,
        title="Weekly Warrior",
        title_tr="Haftalik Savasci",
        description="Answer 100 questions this week",
        description_tr="Bu hafta 100 soru coz",
        target_value=100,
        xp_reward=300,
        icon="shield",
        color="#F59E0B",
    ),
    Challenge(
        id="weekly_streak_7",
        type=ChallengeType.STREAK,
        difficulty=ChallengeDifficulty.LEGENDARY,
        title="7-Day Legend",
        title_tr="7 Gunluk Efsane",
        description="Practice every day for 7 days",
        description_tr="7 gun boyunca her gun calis",
        target_value=7,
        xp_reward=500,
        icon="calendar",
        color="#EF4444",
    ),
    Challenge(
        id="weekly_all_topics",
        type=ChallengeType.EXPLORATION,
        difficulty=ChallengeDifficulty.LEGENDARY,
        title="Renaissance Mind",
        title_tr="Ronesans Zihni",
        description="Practice all 6 topics this week",
        description_tr="Bu hafta 6 konunun hepsinde calis",
        target_value=6,
        xp_reward=400,
        icon="library",
        color="#8B5CF6",
    ),
]


class DailyChallengeSystem:
    """
    Manages daily challenges for users.

    Features:
    - Generates 3 daily challenges (easy, medium, hard)
    - Tracks progress across sessions
    - Awards XP on completion
    - Bonus XP for completing all daily challenges
    """

    DAILY_CHALLENGE_COUNT = 3
    ALL_COMPLETE_BONUS_XP = 100

    def __init__(self):
        self._user_progress: Dict[str, Dict[str, ChallengeProgress]] = {}
        self._user_daily_challenges: Dict[str, List[Challenge]] = {}

    def get_daily_challenges(self, user_id: str, date: Optional[datetime] = None) -> List[Dict]:
        """
        Get today's challenges for a user.

        Challenges are deterministically generated based on date and user_id
        to ensure consistency across sessions.
        """
        if date is None:
            date = datetime.utcnow()

        date_str = date.strftime("%Y-%m-%d")
        cache_key = f"{user_id}:{date_str}"

        if cache_key not in self._user_daily_challenges:
            challenges = self._generate_daily_challenges(user_id, date)
            self._user_daily_challenges[cache_key] = challenges

        challenges = self._user_daily_challenges[cache_key]

        # Add progress information
        result = []
        for challenge in challenges:
            progress = self._get_progress(user_id, challenge.id)
            challenge_dict = challenge.to_dict()
            challenge_dict["progress"] = {
                "current": progress.current_value,
                "target": challenge.target_value,
                "percent": min(100, (progress.current_value / challenge.target_value) * 100),
                "is_completed": progress.is_completed,
                "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
            }
            result.append(challenge_dict)

        return result

    def get_weekly_challenges(self, user_id: str) -> List[Dict]:
        """Get this week's special challenges."""
        result = []
        for challenge in WEEKLY_CHALLENGES:
            progress = self._get_progress(user_id, challenge.id)
            challenge_dict = challenge.to_dict()
            challenge_dict["progress"] = {
                "current": progress.current_value,
                "target": challenge.target_value,
                "percent": min(100, (progress.current_value / challenge.target_value) * 100),
                "is_completed": progress.is_completed,
            }
            result.append(challenge_dict)
        return result

    def update_progress(
        self,
        user_id: str,
        challenge_type: ChallengeType,
        value: int = 1,
        topic_slug: Optional[str] = None,
    ) -> List[Dict]:
        """
        Update progress on relevant challenges.

        Returns list of newly completed challenges with rewards.
        """
        completed = []
        date = datetime.utcnow()
        date_str = date.strftime("%Y-%m-%d")
        cache_key = f"{user_id}:{date_str}"

        # Get today's challenges
        if cache_key not in self._user_daily_challenges:
            self._user_daily_challenges[cache_key] = self._generate_daily_challenges(user_id, date)

        all_challenges = self._user_daily_challenges[cache_key] + WEEKLY_CHALLENGES

        for challenge in all_challenges:
            if challenge.type != challenge_type:
                continue

            # Check topic-specific challenges
            if challenge.topic_slug and challenge.topic_slug != topic_slug:
                continue

            progress = self._get_progress(user_id, challenge.id)

            if progress.is_completed:
                continue

            # Update progress
            progress.current_value += value

            # Check completion
            if progress.current_value >= challenge.target_value:
                progress.is_completed = True
                progress.completed_at = datetime.utcnow()
                completed.append({
                    "challenge": challenge.to_dict(),
                    "xp_earned": challenge.xp_reward,
                })

        # Check if all daily challenges completed
        daily_challenges = self._user_daily_challenges.get(cache_key, [])
        all_daily_complete = all(
            self._get_progress(user_id, c.id).is_completed
            for c in daily_challenges
        )

        if all_daily_complete and len(daily_challenges) == self.DAILY_CHALLENGE_COUNT:
            # Check if bonus already awarded
            bonus_key = f"daily_bonus:{date_str}"
            if not self._get_progress(user_id, bonus_key).is_completed:
                self._get_progress(user_id, bonus_key).is_completed = True
                completed.append({
                    "challenge": {
                        "id": "daily_bonus",
                        "title": "Daily Champion",
                        "title_tr": "Gunun Sampiyonu",
                        "description": "Completed all daily challenges!",
                        "description_tr": "Tum gunluk gorevleri tamamladin!",
                        "icon": "trophy",
                        "color": "#F59E0B",
                    },
                    "xp_earned": self.ALL_COMPLETE_BONUS_XP,
                    "is_bonus": True,
                })

        return completed

    def record_answer(
        self,
        user_id: str,
        is_correct: bool,
        topic_slug: str,
        response_time_ms: int,
        current_streak: int,
    ) -> List[Dict]:
        """
        Record an answer and update all relevant challenge progress.

        This is the main entry point for tracking challenge progress.
        """
        completed = []

        # Volume challenges - always increment
        completed.extend(self.update_progress(user_id, ChallengeType.VOLUME, 1))

        # Accuracy challenges - only on correct answers
        if is_correct:
            completed.extend(self.update_progress(
                user_id, ChallengeType.ACCURACY, current_streak
            ))

        # Exploration - track unique topics
        completed.extend(self.update_progress(
            user_id, ChallengeType.EXPLORATION, 1, topic_slug
        ))

        # Mastery - handled separately when mastery updates

        return completed

    def record_mastery_update(
        self,
        user_id: str,
        topic_slug: str,
        mastery_percent: int,
    ) -> List[Dict]:
        """Record mastery update for mastery challenges."""
        return self.update_progress(
            user_id,
            ChallengeType.MASTERY,
            mastery_percent,
            topic_slug,
        )

    def _generate_daily_challenges(
        self,
        user_id: str,
        date: datetime
    ) -> List[Challenge]:
        """
        Generate deterministic daily challenges.

        Uses hash of user_id + date to ensure same challenges
        for same user on same day.
        """
        date_str = date.strftime("%Y-%m-%d")
        seed = int(hashlib.md5(f"{user_id}:{date_str}".encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)

        # Group by difficulty
        easy = [c for c in CHALLENGE_TEMPLATES if c.difficulty == ChallengeDifficulty.EASY]
        medium = [c for c in CHALLENGE_TEMPLATES if c.difficulty == ChallengeDifficulty.MEDIUM]
        hard = [c for c in CHALLENGE_TEMPLATES if c.difficulty == ChallengeDifficulty.HARD]

        challenges = []

        if easy:
            challenges.append(rng.choice(easy))
        if medium:
            challenges.append(rng.choice(medium))
        if hard:
            challenges.append(rng.choice(hard))

        return challenges

    def _get_progress(self, user_id: str, challenge_id: str) -> ChallengeProgress:
        """Get or create progress record for a challenge."""
        if user_id not in self._user_progress:
            self._user_progress[user_id] = {}

        if challenge_id not in self._user_progress[user_id]:
            self._user_progress[user_id][challenge_id] = ChallengeProgress(
                challenge_id=challenge_id,
                user_id=user_id,
            )

        return self._user_progress[user_id][challenge_id]

    def reset_daily_progress(self, user_id: str) -> None:
        """Reset daily challenge progress (called at midnight)."""
        if user_id in self._user_progress:
            # Keep weekly progress, reset daily
            weekly_ids = {c.id for c in WEEKLY_CHALLENGES}
            self._user_progress[user_id] = {
                k: v for k, v in self._user_progress[user_id].items()
                if k in weekly_ids
            }


# Global instance
daily_challenge_system = DailyChallengeSystem()
