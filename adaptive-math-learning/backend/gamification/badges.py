"""
Badge/Achievement System.

Manages achievement badges for student motivation.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Set
from datetime import datetime
from enum import Enum


class BadgeCategory(str, Enum):
    """Badge categories."""
    MASTERY = "mastery"          # Topic mastery achievements
    STREAK = "streak"            # Streak achievements
    PRACTICE = "practice"        # Practice volume achievements
    ACCURACY = "accuracy"        # Accuracy achievements
    SPEED = "speed"              # Speed achievements
    SPECIAL = "special"          # Special/seasonal achievements


class BadgeRarity(str, Enum):
    """Badge rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Badge:
    """Badge definition."""
    id: str
    name: str
    name_tr: str  # Turkish name
    description: str
    description_tr: str  # Turkish description
    category: BadgeCategory
    rarity: BadgeRarity
    icon: str  # Emoji or icon name
    xp_reward: int = 50
    requirement: Dict = field(default_factory=dict)


@dataclass
class EarnedBadge:
    """Record of an earned badge."""
    badge_id: str
    earned_at: datetime = field(default_factory=datetime.utcnow)
    context: Dict = field(default_factory=dict)


@dataclass
class BadgeRecord:
    """Badge record for a user."""
    user_id: str
    earned_badges: List[EarnedBadge] = field(default_factory=list)
    badge_ids: Set[str] = field(default_factory=set)


class BadgeSystem:
    """
    Badge system for achievements.

    Predefined badges for K-12 math learning context.
    """

    # Predefined badges
    BADGES = {
        # Mastery badges
        "first_mastery": Badge(
            id="first_mastery",
            name="First Steps",
            name_tr="Ilk Adimlar",
            description="Reach 50% mastery in any topic",
            description_tr="Herhangi bir konuda %50 ustalığa ulaş",
            category=BadgeCategory.MASTERY,
            rarity=BadgeRarity.COMMON,
            icon="🎯",
            xp_reward=50,
            requirement={"mastery": 0.5, "count": 1},
        ),
        "topic_master": Badge(
            id="topic_master",
            name="Topic Master",
            name_tr="Konu Ustası",
            description="Reach 90% mastery in any topic",
            description_tr="Herhangi bir konuda %90 ustalığa ulaş",
            category=BadgeCategory.MASTERY,
            rarity=BadgeRarity.RARE,
            icon="🏆",
            xp_reward=100,
            requirement={"mastery": 0.9, "count": 1},
        ),
        "math_wizard": Badge(
            id="math_wizard",
            name="Math Wizard",
            name_tr="Matematik Sihirbazı",
            description="Reach 90% mastery in all topics",
            description_tr="Tüm konularda %90 ustalığa ulaş",
            category=BadgeCategory.MASTERY,
            rarity=BadgeRarity.LEGENDARY,
            icon="🧙",
            xp_reward=500,
            requirement={"mastery": 0.9, "count": 6},
        ),

        # Streak badges
        "streak_3": Badge(
            id="streak_3",
            name="Getting Started",
            name_tr="Başlangıç",
            description="Get 3 correct answers in a row",
            description_tr="Arka arkaya 3 doğru cevap ver",
            category=BadgeCategory.STREAK,
            rarity=BadgeRarity.COMMON,
            icon="🔥",
            xp_reward=25,
            requirement={"streak": 3},
        ),
        "streak_10": Badge(
            id="streak_10",
            name="On Fire",
            name_tr="Ateşte",
            description="Get 10 correct answers in a row",
            description_tr="Arka arkaya 10 doğru cevap ver",
            category=BadgeCategory.STREAK,
            rarity=BadgeRarity.UNCOMMON,
            icon="🔥🔥",
            xp_reward=75,
            requirement={"streak": 10},
        ),
        "streak_25": Badge(
            id="streak_25",
            name="Unstoppable",
            name_tr="Durdurulamaz",
            description="Get 25 correct answers in a row",
            description_tr="Arka arkaya 25 doğru cevap ver",
            category=BadgeCategory.STREAK,
            rarity=BadgeRarity.EPIC,
            icon="💫",
            xp_reward=200,
            requirement={"streak": 25},
        ),
        "streak_50": Badge(
            id="streak_50",
            name="Legend",
            name_tr="Efsane",
            description="Get 50 correct answers in a row",
            description_tr="Arka arkaya 50 doğru cevap ver",
            category=BadgeCategory.STREAK,
            rarity=BadgeRarity.LEGENDARY,
            icon="⭐",
            xp_reward=500,
            requirement={"streak": 50},
        ),

        # Practice badges
        "practice_10": Badge(
            id="practice_10",
            name="Practice Makes Perfect",
            name_tr="Pratik Mükemmelleştirir",
            description="Answer 10 questions",
            description_tr="10 soru cevapla",
            category=BadgeCategory.PRACTICE,
            rarity=BadgeRarity.COMMON,
            icon="📚",
            xp_reward=25,
            requirement={"questions": 10},
        ),
        "practice_100": Badge(
            id="practice_100",
            name="Dedicated Learner",
            name_tr="Adanmış Öğrenci",
            description="Answer 100 questions",
            description_tr="100 soru cevapla",
            category=BadgeCategory.PRACTICE,
            rarity=BadgeRarity.UNCOMMON,
            icon="📖",
            xp_reward=100,
            requirement={"questions": 100},
        ),
        "practice_500": Badge(
            id="practice_500",
            name="Knowledge Seeker",
            name_tr="Bilgi Arayıcısı",
            description="Answer 500 questions",
            description_tr="500 soru cevapla",
            category=BadgeCategory.PRACTICE,
            rarity=BadgeRarity.RARE,
            icon="🎓",
            xp_reward=250,
            requirement={"questions": 500},
        ),
        "practice_1000": Badge(
            id="practice_1000",
            name="Math Champion",
            name_tr="Matematik Şampiyonu",
            description="Answer 1000 questions",
            description_tr="1000 soru cevapla",
            category=BadgeCategory.PRACTICE,
            rarity=BadgeRarity.EPIC,
            icon="🏅",
            xp_reward=500,
            requirement={"questions": 1000},
        ),

        # Accuracy badges
        "perfect_session": Badge(
            id="perfect_session",
            name="Perfect Session",
            name_tr="Mükemmel Oturum",
            description="Complete a session with 100% accuracy",
            description_tr="Bir oturumu %100 doğrulukla tamamla",
            category=BadgeCategory.ACCURACY,
            rarity=BadgeRarity.UNCOMMON,
            icon="✨",
            xp_reward=100,
            requirement={"session_accuracy": 1.0},
        ),
        "accuracy_90": Badge(
            id="accuracy_90",
            name="Sharp Mind",
            name_tr="Keskin Zihin",
            description="Maintain 90% accuracy over 50 questions",
            description_tr="50 soruda %90 doğruluk oranını koru",
            category=BadgeCategory.ACCURACY,
            rarity=BadgeRarity.RARE,
            icon="🎯",
            xp_reward=150,
            requirement={"accuracy": 0.9, "min_questions": 50},
        ),

        # Speed badges
        "quick_thinker": Badge(
            id="quick_thinker",
            name="Quick Thinker",
            name_tr="Hızlı Düşünen",
            description="Answer 5 questions correctly under 10 seconds each",
            description_tr="5 soruyu her biri 10 saniyenin altında doğru cevapla",
            category=BadgeCategory.SPEED,
            rarity=BadgeRarity.UNCOMMON,
            icon="⚡",
            xp_reward=75,
            requirement={"quick_answers": 5},
        ),
        "lightning": Badge(
            id="lightning",
            name="Lightning Fast",
            name_tr="Şimşek Hızında",
            description="Answer a question correctly in under 5 seconds",
            description_tr="Bir soruyu 5 saniyenin altında doğru cevapla",
            category=BadgeCategory.SPEED,
            rarity=BadgeRarity.RARE,
            icon="⚡⚡",
            xp_reward=100,
            requirement={"response_time_ms": 5000},
        ),

        # Daily streak badges
        "daily_streak_7": Badge(
            id="daily_streak_7",
            name="Week Warrior",
            name_tr="Hafta Savaşçısı",
            description="Practice for 7 days in a row",
            description_tr="7 gün arka arkaya pratik yap",
            category=BadgeCategory.STREAK,
            rarity=BadgeRarity.UNCOMMON,
            icon="📅",
            xp_reward=100,
            requirement={"daily_streak": 7},
        ),
        "daily_streak_30": Badge(
            id="daily_streak_30",
            name="Month Master",
            name_tr="Ay Ustası",
            description="Practice for 30 days in a row",
            description_tr="30 gün arka arkaya pratik yap",
            category=BadgeCategory.STREAK,
            rarity=BadgeRarity.EPIC,
            xp_reward=300,
            icon="🗓️",
            requirement={"daily_streak": 30},
        ),
    }

    def __init__(self):
        """Initialize badge system."""
        self._records: Dict[str, BadgeRecord] = {}

    def get_record(self, user_id: str) -> BadgeRecord:
        """Get badge record for a user."""
        if user_id not in self._records:
            self._records[user_id] = BadgeRecord(user_id=user_id)
        return self._records[user_id]

    def award_badge(
        self,
        user_id: str,
        badge_id: str,
        context: Optional[Dict] = None
    ) -> Optional[Badge]:
        """
        Award a badge to a user.

        Args:
            user_id: User identifier
            badge_id: Badge to award
            context: Context for earning (e.g., which topic)

        Returns:
            Badge if newly awarded, None if already had
        """
        if badge_id not in self.BADGES:
            return None

        record = self.get_record(user_id)

        # Check if already earned
        if badge_id in record.badge_ids:
            return None

        # Award badge
        badge = self.BADGES[badge_id]
        earned = EarnedBadge(
            badge_id=badge_id,
            earned_at=datetime.utcnow(),
            context=context or {},
        )

        record.earned_badges.append(earned)
        record.badge_ids.add(badge_id)

        return badge

    def check_and_award(
        self,
        user_id: str,
        stats: Dict
    ) -> List[Badge]:
        """
        Check stats and award any earned badges.

        Args:
            user_id: User identifier
            stats: Current stats dict with keys like:
                   - streak: current answer streak
                   - questions: total questions answered
                   - accuracy: overall accuracy
                   - mastery: dict of topic masteries
                   - daily_streak: consecutive days practiced
                   - response_time_ms: last response time

        Returns:
            List of newly awarded badges
        """
        awarded = []

        for badge_id, badge in self.BADGES.items():
            if self._check_requirement(badge, stats):
                result = self.award_badge(user_id, badge_id, stats)
                if result:
                    awarded.append(result)

        return awarded

    def _check_requirement(self, badge: Badge, stats: Dict) -> bool:
        """Check if stats meet badge requirements."""
        req = badge.requirement

        # Streak requirements
        if "streak" in req:
            if stats.get("streak", 0) < req["streak"]:
                return False

        # Questions answered
        if "questions" in req:
            if stats.get("questions", 0) < req["questions"]:
                return False

        # Accuracy requirements
        if "accuracy" in req:
            if stats.get("accuracy", 0) < req["accuracy"]:
                return False
            if "min_questions" in req:
                if stats.get("questions", 0) < req["min_questions"]:
                    return False

        # Mastery requirements
        if "mastery" in req:
            mastery_dict = stats.get("mastery", {})
            count_needed = req.get("count", 1)
            count_met = sum(1 for m in mastery_dict.values() if m >= req["mastery"])
            if count_met < count_needed:
                return False

        # Daily streak
        if "daily_streak" in req:
            if stats.get("daily_streak", 0) < req["daily_streak"]:
                return False

        # Response time
        if "response_time_ms" in req:
            if stats.get("response_time_ms", float("inf")) > req["response_time_ms"]:
                return False

        # Session accuracy
        if "session_accuracy" in req:
            if stats.get("session_accuracy", 0) < req["session_accuracy"]:
                return False

        return True

    def get_earned_badges(self, user_id: str) -> List[Dict]:
        """Get all earned badges for a user."""
        record = self.get_record(user_id)
        result = []

        for earned in record.earned_badges:
            badge = self.BADGES.get(earned.badge_id)
            if badge:
                result.append({
                    "badge_id": badge.id,
                    "name": badge.name,
                    "name_tr": badge.name_tr,
                    "description": badge.description,
                    "description_tr": badge.description_tr,
                    "category": badge.category.value,
                    "rarity": badge.rarity.value,
                    "icon": badge.icon,
                    "earned_at": earned.earned_at.isoformat(),
                })

        return result

    def get_available_badges(self, user_id: str) -> List[Dict]:
        """Get badges not yet earned by user."""
        record = self.get_record(user_id)
        result = []

        for badge_id, badge in self.BADGES.items():
            if badge_id not in record.badge_ids:
                result.append({
                    "badge_id": badge.id,
                    "name": badge.name,
                    "name_tr": badge.name_tr,
                    "description": badge.description,
                    "description_tr": badge.description_tr,
                    "category": badge.category.value,
                    "rarity": badge.rarity.value,
                    "icon": badge.icon,
                    "requirement": badge.requirement,
                })

        return result

    def get_badge_count(self, user_id: str) -> Dict:
        """Get badge count summary."""
        record = self.get_record(user_id)
        total = len(self.BADGES)
        earned = len(record.badge_ids)

        return {
            "earned": earned,
            "total": total,
            "progress": earned / total if total > 0 else 0,
        }
