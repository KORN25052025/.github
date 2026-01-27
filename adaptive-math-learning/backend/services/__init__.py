"""
Business logic services.
"""

from .question_service import QuestionService, SessionService, MasteryService
from .answer_service import AnswerService
from .hint_service import HintService, hint_service
from .ai_tutor_service import AITutorService, ai_tutor_service
from .diagnostic_service import DiagnosticService, diagnostic_service
from .exam_prep_service import ExamPrepService, exam_prep_service
from .spaced_repetition_service import SpacedRepetitionService, spaced_repetition_service
from .motivation_service import (
    MathHistoryService, MathPuzzleService, CertificateService, SeasonalContentService,
    math_history_service, math_puzzle_service, certificate_service, seasonal_content_service,
)
from .social_service import DuelService, TournamentService, FriendService, WeeklyCompetitionService
from .accessibility_service import (
    TextToSpeechService, AccessibilitySettingsService, MultiLanguageService, SpecialEducationService,
    tts_service, accessibility_settings_service, multi_language_service, special_education_service,
)
from .enhanced_parent_teacher_service import (
    HomeworkService, WeeklyReportService, GoalSettingService, ClassAnalyticsService,
    homework_service, weekly_report_service, goal_setting_service, class_analytics_service,
)

__all__ = [
    "QuestionService",
    "SessionService",
    "MasteryService",
    "AnswerService",
    "HintService",
    "hint_service",
    "AITutorService",
    "ai_tutor_service",
    "DiagnosticService",
    "diagnostic_service",
    "ExamPrepService",
    "exam_prep_service",
    "SpacedRepetitionService",
    "spaced_repetition_service",
    "MathHistoryService",
    "MathPuzzleService",
    "CertificateService",
    "SeasonalContentService",
    "math_history_service",
    "math_puzzle_service",
    "certificate_service",
    "seasonal_content_service",
    "DuelService",
    "TournamentService",
    "FriendService",
    "WeeklyCompetitionService",
    "TextToSpeechService",
    "AccessibilitySettingsService",
    "MultiLanguageService",
    "SpecialEducationService",
    "tts_service",
    "accessibility_settings_service",
    "multi_language_service",
    "special_education_service",
    "HomeworkService",
    "WeeklyReportService",
    "GoalSettingService",
    "ClassAnalyticsService",
    "homework_service",
    "weekly_report_service",
    "goal_setting_service",
    "class_analytics_service",
]
