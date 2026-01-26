"""
Enhanced Parent & Teacher Dashboard Services
=============================================

Ogretmen ve veli panelleri icin gelismis servisler.
Odev yonetimi, haftalik raporlar, hedef belirleme ve sinif analizleri.

Services:
    - HomeworkService: Odev olusturma, gonderme ve otomatik degerlendirme
    - WeeklyReportService: Haftalik ilerleme raporlari
    - GoalSettingService: Ogrenme hedefleri belirleme ve takip
    - ClassAnalyticsService: Sinif duzeyinde analiz ve raporlama
"""

from __future__ import annotations

import uuid
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class GoalType(Enum):
    """Ogrenme hedefi turleri."""
    QUESTIONS_PER_WEEK = "questions_per_week"       # Haftalik soru sayisi
    ACCURACY_TARGET = "accuracy_target"             # Dogruluk orani hedefi (%)
    STREAK_TARGET = "streak_target"                 # Ardisik dogru sayisi
    MASTERY_TARGET = "mastery_target"               # Konu hakimiyet hedefi
    PRACTICE_MINUTES = "practice_minutes"           # Haftalik calisma suresi (dk)


class HomeworkStatus(Enum):
    """Odev durumu."""
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class Homework:
    """Odev bilgisi."""
    homework_id: str
    teacher_id: str
    class_id: str
    title: str
    topics: List[str]
    question_count: int
    questions: List[Dict[str, Any]]
    due_date: datetime
    created_at: datetime
    status: HomeworkStatus = HomeworkStatus.ASSIGNED
    sinif_ortalamasi: Optional[float] = None
    teslim_sayisi: int = 0
    toplam_ogrenci: int = 0


@dataclass
class HomeworkSubmission:
    """Odev teslimi."""
    submission_id: str
    homework_id: str
    student_id: str
    answers: List[Dict[str, Any]]
    submitted_at: datetime
    score: Optional[float] = None
    dogru_sayisi: int = 0
    yanlis_sayisi: int = 0
    bos_sayisi: int = 0
    graded_at: Optional[datetime] = None
    feedback: Optional[str] = None
    topic_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class WeeklyReport:
    """Haftalik ilerleme raporu."""
    report_id: str
    child_id: str
    week_start: datetime
    week_end: datetime
    generated_at: datetime
    toplam_soru: int = 0
    dogru_orani: float = 0.0
    calisma_suresi_dakika: int = 0
    aktif_gun_sayisi: int = 0
    en_uzun_seri: int = 0
    guclu_konular: List[str] = field(default_factory=list)
    zayif_konular: List[str] = field(default_factory=list)
    gelisen_konular: List[str] = field(default_factory=list)
    gerileyen_konular: List[str] = field(default_factory=list)
    soru_degisim_yuzdesi: float = 0.0
    dogruluk_degisim: float = 0.0
    sure_degisim_yuzdesi: float = 0.0
    oneriler: List[str] = field(default_factory=list)
    oncelikli_konular: List[str] = field(default_factory=list)
    goal_progress: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LearningGoal:
    """Ogrenme hedefi."""
    goal_id: str
    parent_id: str
    child_id: str
    goal_type: GoalType
    target_value: float
    current_value: float = 0.0
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    is_active: bool = True
    progress_percentage: float = 0.0
    description: str = ""


@dataclass
class ClassAnalytics:
    """Sinif duzeyinde analiz verileri."""
    class_id: str
    generated_at: datetime
    ogrenci_sayisi: int = 0
    ortalama_dogruluk: float = 0.0
    ortalama_soru_sayisi: float = 0.0
    ortalama_calisma_suresi: float = 0.0
    en_basarili_konular: List[Dict[str, Any]] = field(default_factory=list)
    en_zayif_konular: List[Dict[str, Any]] = field(default_factory=list)
    basari_dagilimi: Dict[str, int] = field(default_factory=dict)
    risk_altindaki_ogrenciler: List[Dict[str, Any]] = field(default_factory=list)
    ortalama_odev_puani: float = 0.0
    odev_teslim_orani: float = 0.0


# ---------------------------------------------------------------------------
# Simulated Data Store
# ---------------------------------------------------------------------------

class _DataStore:
    """
    In-memory data store simulating database access.
    In production this layer is replaced by PostgreSQL / MongoDB.
    """

    def __init__(self) -> None:
        self.homeworks: Dict[str, Homework] = {}
        self.submissions: Dict[str, HomeworkSubmission] = {}
        self.weekly_reports: Dict[str, WeeklyReport] = {}
        self.learning_goals: Dict[str, LearningGoal] = {}
        self.student_activity: Dict[str, List[Dict[str, Any]]] = {}
        self.class_rosters: Dict[str, List[str]] = {}
        self.question_bank: Dict[str, List[Dict[str, Any]]] = {}
        self.parent_children: Dict[str, List[str]] = {}
        self.parent_emails: Dict[str, str] = {}

    def get_student_activity(self, student_id: str, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Ogrencinin aktivite kaydini dondurur."""
        activities = self.student_activity.get(student_id, [])
        if since:
            activities = [a for a in activities if a.get("timestamp", datetime.min) >= since]
        return activities

    def get_class_students(self, class_id: str) -> List[str]:
        """Siniftaki ogrenci ID listesini dondurur."""
        return self.class_rosters.get(class_id, [])

    def get_student_name(self, student_id: str) -> str:
        """Placeholder - in production comes from user service."""
        return f"Ogrenci_{student_id[:6]}"

    def generate_questions_for_topics(self, topics: List[str], count: int) -> List[Dict[str, Any]]:
        """Konulara gore soru uretir (simulasyon)."""
        questions: List[Dict[str, Any]] = []
        per_topic = max(1, count // len(topics))
        remaining = count - per_topic * len(topics)
        for idx, topic in enumerate(topics):
            topic_count = per_topic + (1 if idx < remaining else 0)
            for q_idx in range(topic_count):
                question_id = str(uuid.uuid4())
                questions.append({"question_id": question_id, "topic": topic,
                    "soru_metni": f"{topic} - Soru {q_idx + 1}",
                    "secenekler": ["A", "B", "C", "D"],
                    "dogru_cevap": "A", "zorluk": "orta",
                    "puan": round(100 / count, 2)})
                if len(questions) >= count:
                    break
            if len(questions) >= count:
                break
        return questions[:count]


_store = _DataStore()


# ---------------------------------------------------------------------------
# HomeworkService - Odev Yonetimi
# ---------------------------------------------------------------------------

class HomeworkService:
    """
    Odev olusturma, teslim alma ve otomatik degerlendirme servisi.
    Ogretmenler odev olusturur, ogrenciler teslim eder,
    sistem otomatik olarak degerlendirir.
    """

    def __init__(self, store: Optional[_DataStore] = None) -> None:
        self._store = store or _store

    def create_homework(self, teacher_id: str, class_id: str, topics: List[str],
                        question_count: int, due_date: datetime, title: str) -> Homework:
        """Yeni odev olusturur ve sinifa atar."""
        if question_count <= 0:
            raise ValueError("Soru sayisi pozitif olmalidir.")
        if not topics:
            raise ValueError("En az bir konu belirtilmelidir.")
        if due_date <= datetime.utcnow():
            raise ValueError("Son teslim tarihi gelecekte olmalidir.")
        homework_id = str(uuid.uuid4())
        questions = self._store.generate_questions_for_topics(topics, question_count)
        students = self._store.get_class_students(class_id)
        homework = Homework(homework_id=homework_id, teacher_id=teacher_id, class_id=class_id,
            title=title, topics=topics, question_count=question_count, questions=questions,
            due_date=due_date, created_at=datetime.utcnow(), status=HomeworkStatus.ASSIGNED,
            toplam_ogrenci=len(students))
        self._store.homeworks[homework_id] = homework
        return homework

    def get_homework(self, homework_id: str) -> Homework:
        """Odev detaylarini getirir."""
        if homework_id not in self._store.homeworks:
            raise KeyError(f"Odev bulunamadi: {homework_id}")
        homework = self._store.homeworks[homework_id]
        self._refresh_homework_status(homework)
        return homework

    def submit_homework(self, homework_id: str, student_id: str, answers: List[Dict[str, Any]]) -> HomeworkSubmission:
        """Ogrenci odev teslimi yapar."""
        homework = self.get_homework(homework_id)
        if homework.status == HomeworkStatus.CANCELLED:
            raise ValueError("Bu odev iptal edilmistir.")
        if datetime.utcnow() > homework.due_date:
            raise ValueError("Odev teslim suresi gecmistir.")
        existing = self._find_submission(homework_id, student_id)
        if existing is not None:
            raise ValueError("Bu odev zaten teslim edilmis.")
        submission_id = str(uuid.uuid4())
        submission = HomeworkSubmission(submission_id=submission_id, homework_id=homework_id,
            student_id=student_id, answers=answers, submitted_at=datetime.utcnow())
        self._store.submissions[submission_id] = submission
        homework.teslim_sayisi += 1
        if homework.status == HomeworkStatus.ASSIGNED:
            homework.status = HomeworkStatus.IN_PROGRESS
        return submission

    def grade_homework(self, homework_id: str) -> Dict[str, Any]:
        """Odeve ait tum teslimleri otomatik degerlendirir."""
        homework = self.get_homework(homework_id)
        submissions = self._get_homework_submissions(homework_id)
        if not submissions:
            return {"homework_id": homework_id, "graded_count": 0,
                    "sinif_ortalamasi": 0.0, "en_yuksek_puan": 0.0,
                    "en_dusuk_puan": 0.0, "submissions": []}
        scores: List[float] = []
        for submission in submissions:
            self._grade_single_submission(submission, homework)
            if submission.score is not None:
                scores.append(submission.score)
        avg_score = statistics.mean(scores) if scores else 0.0
        homework.sinif_ortalamasi = round(avg_score, 2)
        homework.status = HomeworkStatus.GRADED
        return {"homework_id": homework_id, "graded_count": len(submissions),
                "sinif_ortalamasi": round(avg_score, 2),
                "en_yuksek_puan": max(scores) if scores else 0.0,
                "en_dusuk_puan": min(scores) if scores else 0.0,
                "submissions": submissions}

    def get_homework_results(self, homework_id: str) -> Dict[str, Any]:
        """Ogretmen icin odev sonuclarini dondurur."""
        homework = self.get_homework(homework_id)
        submissions = self._get_homework_submissions(homework_id)
        student_results: List[Dict[str, Any]] = []
        topic_totals: Dict[str, List[float]] = {}
        for sub in submissions:
            student_results.append({"student_id": sub.student_id,
                "student_name": self._store.get_student_name(sub.student_id),
                "score": sub.score, "dogru_sayisi": sub.dogru_sayisi,
                "yanlis_sayisi": sub.yanlis_sayisi, "bos_sayisi": sub.bos_sayisi,
                "submitted_at": sub.submitted_at.isoformat(),
                "topic_scores": sub.topic_scores})
            for topic, score in sub.topic_scores.items():
                topic_totals.setdefault(topic, []).append(score)
        topic_analysis = [{"topic": t, "ortalama": round(statistics.mean(v), 2),
             "en_dusuk": round(min(v), 2), "en_yuksek": round(max(v), 2)}
            for t, v in topic_totals.items()]
        teslim_orani = (homework.teslim_sayisi / homework.toplam_ogrenci * 100
                        if homework.toplam_ogrenci > 0 else 0.0)
        return {"homework_id": homework_id, "title": homework.title,
                "status": homework.status.value, "sinif_ortalamasi": homework.sinif_ortalamasi,
                "teslim_orani": round(teslim_orani, 1), "teslim_sayisi": homework.teslim_sayisi,
                "toplam_ogrenci": homework.toplam_ogrenci, "student_results": student_results,
                "topic_analysis": topic_analysis}

    def get_student_homework_list(self, student_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Ogrencinin bekleyen ve tamamlanan odevlerini listeler."""
        bekleyen: List[Dict[str, Any]] = []
        tamamlanan: List[Dict[str, Any]] = []
        suresi_gecmis: List[Dict[str, Any]] = []
        for hw in self._store.homeworks.values():
            class_students = self._store.get_class_students(hw.class_id)
            if student_id not in class_students:
                continue
            submission = self._find_submission(hw.homework_id, student_id)
            hw_info = {"homework_id": hw.homework_id, "title": hw.title,
                "topics": hw.topics, "question_count": hw.question_count,
                "due_date": hw.due_date.isoformat(), "status": hw.status.value}
            if submission is not None:
                hw_info["score"] = submission.score
                hw_info["submitted_at"] = submission.submitted_at.isoformat()
                tamamlanan.append(hw_info)
            elif datetime.utcnow() > hw.due_date:
                suresi_gecmis.append(hw_info)
            else:
                kalan = hw.due_date - datetime.utcnow()
                hw_info["kalan_sure_saat"] = round(kalan.total_seconds() / 3600, 1)
                bekleyen.append(hw_info)
        return {"bekleyen": bekleyen, "tamamlanan": tamamlanan, "suresi_gecmis": suresi_gecmis}

    # -- Private helpers ---------------------------------------------------

    def _refresh_homework_status(self, homework: Homework) -> None:
        if (homework.status in (HomeworkStatus.ASSIGNED, HomeworkStatus.IN_PROGRESS)
                and datetime.utcnow() > homework.due_date):
            homework.status = HomeworkStatus.OVERDUE

    def _find_submission(self, homework_id: str, student_id: str) -> Optional[HomeworkSubmission]:
        for sub in self._store.submissions.values():
            if sub.homework_id == homework_id and sub.student_id == student_id:
                return sub
        return None

    def _get_homework_submissions(self, homework_id: str) -> List[HomeworkSubmission]:
        return [s for s in self._store.submissions.values() if s.homework_id == homework_id]

    def _grade_single_submission(self, submission: HomeworkSubmission, homework: Homework) -> None:
        """Tek bir teslimi degerlendirir."""
        answer_map = {a["question_id"]: a.get("answer") for a in submission.answers}
        dogru, yanlis, bos = 0, 0, 0
        topic_correct: Dict[str, int] = {}
        topic_total: Dict[str, int] = {}
        for q in homework.questions:
            qid = q["question_id"]
            topic = q["topic"]
            topic_total[topic] = topic_total.get(topic, 0) + 1
            student_answer = answer_map.get(qid)
            if student_answer is None or student_answer == "":
                bos += 1
            elif student_answer == q["dogru_cevap"]:
                dogru += 1
                topic_correct[topic] = topic_correct.get(topic, 0) + 1
            else:
                yanlis += 1
        total = len(homework.questions)
        score = round((dogru / total) * 100, 2) if total > 0 else 0.0
        topic_scores: Dict[str, float] = {}
        for topic, total_q in topic_total.items():
            correct_q = topic_correct.get(topic, 0)
            topic_scores[topic] = round((correct_q / total_q) * 100, 2) if total_q > 0 else 0.0
        submission.score = score
        submission.dogru_sayisi = dogru
        submission.yanlis_sayisi = yanlis
        submission.bos_sayisi = bos
        submission.topic_scores = topic_scores
        submission.graded_at = datetime.utcnow()
        submission.feedback = self._generate_feedback(score, topic_scores)

    @staticmethod
    def _generate_feedback(score: float, topic_scores: Dict[str, float]) -> str:
        """Puana gore otomatik geri bildirim uretir."""
        if score >= 90:
            feedback = "Harika bir performans! Tebrikler."
        elif score >= 70:
            feedback = "Iyi bir calisma, biraz daha pratik yaparak daha da iyilesebilirsin."
        elif score >= 50:
            feedback = "Ortalama bir sonuc. Zayif konularina odaklanmani oneririm."
        else:
            feedback = "Bu konularda daha fazla calisman gerekiyor."
        weak_topics = [t for t, s in topic_scores.items() if s < 50]
        if weak_topics:
            feedback += f" Ozellikle su konulara calis: {', '.join(weak_topics)}."
        return feedback


# ---------------------------------------------------------------------------
# WeeklyReportService - Haftalik Raporlar
# ---------------------------------------------------------------------------

class WeeklyReportService:
    """
    Haftalik ogrenme raporu olusturma ve e-posta hazirlama servisi.
    Veliler cocuklarinin haftalik ilerlemesini takip edebilir.
    """

    def __init__(self, store: Optional[_DataStore] = None) -> None:
        self._store = store or _store

    def generate_weekly_report(self, child_id: str) -> WeeklyReport:
        """Son bir hafta icin kapsamli ilerleme raporu uretir."""
        now = datetime.utcnow()
        week_start = now - timedelta(days=7)
        week_end = now
        activities = self._store.get_student_activity(child_id, since=week_start)
        prev_week_start = week_start - timedelta(days=7)
        prev_activities = self._store.get_student_activity(child_id, since=prev_week_start)
        prev_activities = [a for a in prev_activities
                           if a.get("timestamp", datetime.min) < week_start]

        toplam_soru = self._count_questions(activities)
        dogru_sayisi = self._count_correct(activities)
        dogru_orani = round((dogru_sayisi / toplam_soru) * 100, 2) if toplam_soru > 0 else 0.0
        calisma_suresi = self._total_minutes(activities)
        aktif_gunler = self._active_days(activities)
        en_uzun_seri = self._longest_streak(activities)

        prev_soru = self._count_questions(prev_activities)
        prev_dogru = self._count_correct(prev_activities)
        prev_dogru_orani = round((prev_dogru / prev_soru) * 100, 2) if prev_soru > 0 else 0.0
        prev_sure = self._total_minutes(prev_activities)

        soru_degisim = self._percentage_change(prev_soru, toplam_soru)
        dogruluk_degisim = round(dogru_orani - prev_dogru_orani, 2)
        sure_degisim = self._percentage_change(prev_sure, calisma_suresi)

        topic_stats = self._topic_breakdown(activities)
        prev_topic_stats = self._topic_breakdown(prev_activities)
        guclu = [t for t, s in topic_stats.items() if s >= 80]
        zayif = [t for t, s in topic_stats.items() if s < 50]
        gelisen = [t for t in topic_stats if t in prev_topic_stats and topic_stats[t] - prev_topic_stats[t] >= 10]
        gerileyen = [t for t in topic_stats if t in prev_topic_stats and prev_topic_stats[t] - topic_stats[t] >= 10]
        oneriler = self._generate_suggestions(dogru_orani, toplam_soru, calisma_suresi, aktif_gunler, zayif)
        oncelikli = zayif[:3] if zayif else []
        goal_progress = self._get_goal_progress(child_id)

        report_id = str(uuid.uuid4())
        report = WeeklyReport(report_id=report_id, child_id=child_id,
            week_start=week_start, week_end=week_end, generated_at=now,
            toplam_soru=toplam_soru, dogru_orani=dogru_orani,
            calisma_suresi_dakika=calisma_suresi, aktif_gun_sayisi=aktif_gunler,
            en_uzun_seri=en_uzun_seri, guclu_konular=guclu, zayif_konular=zayif,
            gelisen_konular=gelisen, gerileyen_konular=gerileyen,
            soru_degisim_yuzdesi=soru_degisim, dogruluk_degisim=dogruluk_degisim,
            sure_degisim_yuzdesi=sure_degisim, oneriler=oneriler,
            oncelikli_konular=oncelikli, goal_progress=goal_progress)
        self._store.weekly_reports[report_id] = report
        return report

    def send_email_report(self, parent_id: str, child_id: str) -> Dict[str, Any]:
        """E-posta gonderime hazir rapor verisi dondurur."""
        report = self.generate_weekly_report(child_id)
        parent_email = self._store.parent_emails.get(parent_id, f"{parent_id}@example.com")
        child_name = self._store.get_student_name(child_id)
        subject = f"Haftalik Matematik Raporu - {child_name}"
        return {"to": parent_email, "subject": subject, "report": report}

    def get_report_history(self, child_id: str, weeks: int = 12) -> List[Dict[str, Any]]:
        """Gecmis haftalik raporlarin ozetini dondurur."""
        cutoff = datetime.utcnow() - timedelta(weeks=weeks)
        reports = [r for r in self._store.weekly_reports.values()
                   if r.child_id == child_id and r.generated_at >= cutoff]
        reports.sort(key=lambda r: r.week_start)
        return [{"report_id": r.report_id,
                 "week_start": r.week_start.isoformat(),
                 "week_end": r.week_end.isoformat(),
                 "toplam_soru": r.toplam_soru,
                 "dogru_orani": r.dogru_orani,
                 "calisma_suresi_dakika": r.calisma_suresi_dakika,
                 "aktif_gun_sayisi": r.aktif_gun_sayisi,
                 "guclu_konular": r.guclu_konular,
                 "zayif_konular": r.zayif_konular} for r in reports]

    # -- Private helpers ---------------------------------------------------

    @staticmethod
    def _count_questions(activities: List[Dict[str, Any]]) -> int:
        return sum(a.get("questions_answered", 0) for a in activities)

    @staticmethod
    def _count_correct(activities: List[Dict[str, Any]]) -> int:
        return sum(a.get("correct_answers", 0) for a in activities)

    @staticmethod
    def _total_minutes(activities: List[Dict[str, Any]]) -> int:
        return sum(a.get("duration_minutes", 0) for a in activities)

    @staticmethod
    def _active_days(activities: List[Dict[str, Any]]) -> int:
        days = set()
        for a in activities:
            ts = a.get("timestamp")
            if isinstance(ts, datetime):
                days.add(ts.date())
        return len(days)

    @staticmethod
    def _longest_streak(activities: List[Dict[str, Any]]) -> int:
        max_streak = 0
        current = 0
        for a in activities:
            for r in a.get("results", []):
                if r.get("correct"):
                    current += 1
                    max_streak = max(max_streak, current)
                else:
                    current = 0
        return max_streak

    @staticmethod
    def _topic_breakdown(activities: List[Dict[str, Any]]) -> Dict[str, float]:
        topic_correct: Dict[str, int] = {}
        topic_total: Dict[str, int] = {}
        for a in activities:
            topic = a.get("topic", "Genel")
            answered = a.get("questions_answered", 0)
            correct = a.get("correct_answers", 0)
            topic_total[topic] = topic_total.get(topic, 0) + answered
            topic_correct[topic] = topic_correct.get(topic, 0) + correct
        return {t: round((topic_correct.get(t, 0) / total) * 100, 2) if total > 0 else 0.0
                for t, total in topic_total.items()}

    @staticmethod
    def _percentage_change(old: float, new: float) -> float:
        if old == 0:
            return 100.0 if new > 0 else 0.0
        return round(((new - old) / old) * 100, 2)

    def _generate_suggestions(self, accuracy, total_q, minutes, active_days, weak_topics):
        suggestions: List[str] = []
        if active_days < 3:
            suggestions.append(f"Bu hafta yalnizca {active_days} gun calisildi.")
        if accuracy < 60:
            suggestions.append(f"Dogruluk orani dusuk (%{accuracy}).")
        if total_q < 20:
            suggestions.append(f"Bu hafta yalnizca {total_q} soru cozuldu.")
        if minutes < 30:
            suggestions.append(f"Toplam calisma suresi {minutes} dakika.")
        if weak_topics:
            suggestions.append(f"Zayif konular: {', '.join(weak_topics)}.")
        if not suggestions:
            suggestions.append("Harika bir hafta gecirildi! Ayni tempoda devam edin.")
        return suggestions

    def _get_goal_progress(self, child_id: str) -> List[Dict[str, Any]]:
        goals = [g for g in self._store.learning_goals.values()
                 if g.child_id == child_id and g.is_active]
        return [{"goal_id": g.goal_id, "goal_type": g.goal_type.value,
                 "target_value": g.target_value, "current_value": g.current_value,
                 "progress_percentage": g.progress_percentage,
                 "deadline": g.deadline.isoformat() if g.deadline else None}
                for g in goals]


# ---------------------------------------------------------------------------
# GoalSettingService - Hedef Belirleme
# ---------------------------------------------------------------------------

class GoalSettingService:
    """
    Veli/ogretmen tarafindan ogrenci icin ogrenme hedefi belirleme servisi.
    Hedefler izlenebilir ve ilerleme raporlarina yansir.
    """

    def __init__(self, store: Optional[_DataStore] = None) -> None:
        self._store = store or _store

    def set_goal(
        self,
        parent_id: str,
        child_id: str,
        goal_type: GoalType,
        target_value: float,
        deadline: Optional[datetime] = None,
    ) -> LearningGoal:
        """Yeni ogrenme hedefi belirler."""
        if target_value <= 0:
            raise ValueError("Hedef degeri pozitif olmalidir.")

        descriptions = {
            GoalType.QUESTIONS_PER_WEEK: f"Haftada {int(target_value)} soru coz",
            GoalType.ACCURACY_TARGET: f"%{int(target_value)} dogruluk oranina ulas",
            GoalType.STREAK_TARGET: f"{int(target_value)} ardisik dogru yap",
            GoalType.MASTERY_TARGET: f"%{int(target_value)} konu hakimiyetine ulas",
            GoalType.PRACTICE_MINUTES: f"Haftada {int(target_value)} dakika calis",
        }

        goal = LearningGoal(
            goal_id=str(uuid.uuid4()),
            parent_id=parent_id,
            child_id=child_id,
            goal_type=goal_type,
            target_value=target_value,
            deadline=deadline,
            description=descriptions.get(goal_type, f"Hedef: {target_value}"),
        )
        self._store.learning_goals[goal.goal_id] = goal
        return goal

    def get_goals(self, child_id: str, active_only: bool = True) -> List[LearningGoal]:
        """Cocugun hedeflerini listeler."""
        goals = [g for g in self._store.learning_goals.values()
                 if g.child_id == child_id]
        if active_only:
            goals = [g for g in goals if g.is_active]
        return goals

    def check_progress(self, goal_id: str) -> Dict[str, Any]:
        """Hedef ilerlemesini kontrol eder ve gunceller."""
        goal = self._store.learning_goals.get(goal_id)
        if goal is None:
            raise KeyError(f"Hedef bulunamadi: {goal_id}")

        # Aktivite verilerinden ilerlemeyi hesapla
        activities = self._store.get_student_activity(goal.child_id)
        current = self._calculate_current_value(goal, activities)
        goal.current_value = current
        goal.progress_percentage = min(100.0, round((current / goal.target_value) * 100, 2))

        # Hedefe ulasildi mi?
        if goal.progress_percentage >= 100.0 and goal.completed_at is None:
            goal.completed_at = datetime.utcnow()

        # Sure asimi kontrolu
        is_overdue = False
        if goal.deadline and datetime.utcnow() > goal.deadline and goal.completed_at is None:
            is_overdue = True

        return {
            "goal_id": goal.goal_id,
            "goal_type": goal.goal_type.value,
            "target_value": goal.target_value,
            "current_value": round(goal.current_value, 2),
            "progress_percentage": goal.progress_percentage,
            "is_completed": goal.completed_at is not None,
            "is_overdue": is_overdue,
            "description": goal.description,
            "deadline": goal.deadline.isoformat() if goal.deadline else None,
        }

    def deactivate_goal(self, goal_id: str) -> None:
        """Hedefi deaktif eder."""
        goal = self._store.learning_goals.get(goal_id)
        if goal is not None:
            goal.is_active = False

    @staticmethod
    def _calculate_current_value(goal: LearningGoal, activities: List[Dict[str, Any]]) -> float:
        """Aktivitelerden mevcut degeri hesaplar."""
        # Son 7 gunluk aktiviteleri filtrele
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent = [a for a in activities
                  if a.get("timestamp", datetime.min) >= week_ago]

        if goal.goal_type == GoalType.QUESTIONS_PER_WEEK:
            return float(sum(a.get("questions_answered", 0) for a in recent))
        elif goal.goal_type == GoalType.ACCURACY_TARGET:
            total = sum(a.get("questions_answered", 0) for a in recent)
            correct = sum(a.get("correct_answers", 0) for a in recent)
            return round((correct / total) * 100, 2) if total > 0 else 0.0
        elif goal.goal_type == GoalType.STREAK_TARGET:
            max_streak = 0
            current = 0
            for a in recent:
                for r in a.get("results", []):
                    if r.get("correct"):
                        current += 1
                        max_streak = max(max_streak, current)
                    else:
                        current = 0
            return float(max_streak)
        elif goal.goal_type == GoalType.MASTERY_TARGET:
            # Ortalama konu hakimiyeti
            total = sum(a.get("questions_answered", 0) for a in activities)
            correct = sum(a.get("correct_answers", 0) for a in activities)
            return round((correct / total) * 100, 2) if total > 0 else 0.0
        elif goal.goal_type == GoalType.PRACTICE_MINUTES:
            return float(sum(a.get("duration_minutes", 0) for a in recent))
        return 0.0


# ---------------------------------------------------------------------------
# ClassAnalyticsService - Sinif Analitikleri
# ---------------------------------------------------------------------------

class ClassAnalyticsService:
    """
    Ogretmenler icin sinif duzeyinde analiz ve raporlama servisi.
    Sinifin genel durumu, konu bazli analiz ve risk altindaki ogrencileri tespit eder.
    """

    def __init__(self, store: Optional[_DataStore] = None) -> None:
        self._store = store or _store

    def get_class_overview(self, class_id: str) -> Dict[str, Any]:
        """Sinifin genel performans ozetini dondurur."""
        students = self._store.get_class_students(class_id)
        if not students:
            return {
                "class_id": class_id,
                "ogrenci_sayisi": 0,
                "ortalama_dogruluk": 0.0,
                "ortalama_soru_sayisi": 0.0,
                "ortalama_calisma_suresi": 0.0,
                "basari_dagilimi": {},
                "en_basarili_konular": [],
                "en_zayif_konular": [],
            }

        student_stats: List[Dict[str, Any]] = []
        topic_accuracy: Dict[str, List[float]] = {}

        for student_id in students:
            activities = self._store.get_student_activity(student_id)
            total_q = sum(a.get("questions_answered", 0) for a in activities)
            correct = sum(a.get("correct_answers", 0) for a in activities)
            minutes = sum(a.get("duration_minutes", 0) for a in activities)
            accuracy = (correct / total_q * 100) if total_q > 0 else 0.0

            student_stats.append({
                "student_id": student_id,
                "total_questions": total_q,
                "accuracy": round(accuracy, 2),
                "minutes": minutes,
            })

            # Konu bazli
            for a in activities:
                topic = a.get("topic", "Genel")
                q = a.get("questions_answered", 0)
                c = a.get("correct_answers", 0)
                if q > 0:
                    topic_accuracy.setdefault(topic, []).append(c / q * 100)

        accuracies = [s["accuracy"] for s in student_stats]
        total_questions = [s["total_questions"] for s in student_stats]
        total_minutes = [s["minutes"] for s in student_stats]

        # Basari dagilimi
        dagilim = {"cok_iyi": 0, "iyi": 0, "orta": 0, "zayif": 0, "cok_zayif": 0}
        for acc in accuracies:
            if acc >= 85:
                dagilim["cok_iyi"] += 1
            elif acc >= 70:
                dagilim["iyi"] += 1
            elif acc >= 55:
                dagilim["orta"] += 1
            elif acc >= 40:
                dagilim["zayif"] += 1
            else:
                dagilim["cok_zayif"] += 1

        # Konu siralamalari
        topic_avgs = {t: round(statistics.mean(v), 2) for t, v in topic_accuracy.items() if v}
        sorted_topics = sorted(topic_avgs.items(), key=lambda x: x[1], reverse=True)
        en_basarili = [{"topic": t, "ortalama": v} for t, v in sorted_topics[:5]]
        en_zayif = [{"topic": t, "ortalama": v} for t, v in sorted_topics[-5:]] if len(sorted_topics) >= 5 else []

        return {
            "class_id": class_id,
            "ogrenci_sayisi": len(students),
            "ortalama_dogruluk": round(statistics.mean(accuracies), 2) if accuracies else 0.0,
            "ortalama_soru_sayisi": round(statistics.mean(total_questions), 1) if total_questions else 0.0,
            "ortalama_calisma_suresi": round(statistics.mean(total_minutes), 1) if total_minutes else 0.0,
            "basari_dagilimi": dagilim,
            "en_basarili_konular": en_basarili,
            "en_zayif_konular": en_zayif,
        }

    def get_topic_analysis(self, class_id: str) -> List[Dict[str, Any]]:
        """Sinifin konu bazli detayli analizini dondurur."""
        students = self._store.get_class_students(class_id)
        topic_data: Dict[str, Dict[str, Any]] = {}

        for student_id in students:
            activities = self._store.get_student_activity(student_id)
            for a in activities:
                topic = a.get("topic", "Genel")
                if topic not in topic_data:
                    topic_data[topic] = {"total_q": 0, "correct": 0, "students": set()}
                topic_data[topic]["total_q"] += a.get("questions_answered", 0)
                topic_data[topic]["correct"] += a.get("correct_answers", 0)
                topic_data[topic]["students"].add(student_id)

        result: List[Dict[str, Any]] = []
        for topic, data in topic_data.items():
            accuracy = (data["correct"] / data["total_q"] * 100) if data["total_q"] > 0 else 0.0
            result.append({
                "topic": topic,
                "toplam_soru": data["total_q"],
                "dogruluk_orani": round(accuracy, 2),
                "katilan_ogrenci": len(data["students"]),
                "ogrenci_orani": round(len(data["students"]) / len(students) * 100, 1) if students else 0.0,
            })

        result.sort(key=lambda x: x["dogruluk_orani"])
        return result

    def get_at_risk_students(self, class_id: str) -> List[Dict[str, Any]]:
        """Risk altindaki ogrencileri tespit eder."""
        students = self._store.get_class_students(class_id)
        at_risk: List[Dict[str, Any]] = []

        for student_id in students:
            activities = self._store.get_student_activity(student_id)
            total_q = sum(a.get("questions_answered", 0) for a in activities)
            correct = sum(a.get("correct_answers", 0) for a in activities)
            accuracy = (correct / total_q * 100) if total_q > 0 else 0.0
            minutes = sum(a.get("duration_minutes", 0) for a in activities)

            # Son 7 gun aktivite
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent = [a for a in activities
                      if a.get("timestamp", datetime.min) >= week_ago]
            recent_q = sum(a.get("questions_answered", 0) for a in recent)
            active_days = len(set(
                a.get("timestamp", datetime.min).date()
                for a in recent if isinstance(a.get("timestamp"), datetime)
            ))

            risk_factors: List[str] = []
            if accuracy < 40:
                risk_factors.append("Dusuk dogruluk orani")
            if recent_q < 5:
                risk_factors.append("Az soru cozuyor")
            if active_days < 2:
                risk_factors.append("Duzenli calismiyor")
            if total_q == 0:
                risk_factors.append("Hic aktivite yok")

            if risk_factors:
                at_risk.append({
                    "student_id": student_id,
                    "student_name": self._store.get_student_name(student_id),
                    "dogruluk_orani": round(accuracy, 2),
                    "haftalik_soru": recent_q,
                    "aktif_gun": active_days,
                    "risk_faktorleri": risk_factors,
                    "risk_seviyesi": "yuksek" if len(risk_factors) >= 3 else "orta",
                })

        at_risk.sort(key=lambda x: len(x["risk_faktorleri"]), reverse=True)
        return at_risk


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

homework_service = HomeworkService()
weekly_report_service = WeeklyReportService()
goal_setting_service = GoalSettingService()
class_analytics_service = ClassAnalyticsService()
