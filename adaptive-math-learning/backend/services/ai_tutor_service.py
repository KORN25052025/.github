"""
AI Math Tutor Chatbot Service (MatBot).

Provides an interactive AI-powered math tutoring experience for Turkish students.
Uses Anthropic Claude API to deliver personalized, curriculum-aligned explanations
in Turkish with age-appropriate language and encouraging pedagogy.

Features:
- Interactive tutoring sessions with conversation memory
- Step-by-step question explanations in Turkish
- Detailed error analysis with common mistake pattern detection
- Problem-solving strategy suggestions by topic and difficulty
- Rate limiting (max 50 messages per session)
- Graceful fallback when API is unavailable
- MEB (Milli Egitim Bakanligi) curriculum alignment

Author: Adaptive Math Learning Platform
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_MESSAGES_PER_SESSION = 50
API_TIMEOUT_SECONDS = 30
MAX_TOKENS_RESPONSE = 1024
CONVERSATION_CONTEXT_WINDOW = 20  # max prior messages sent to the model


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ErrorPattern(str, Enum):
    """Common mathematical error patterns students make."""
    SIGN_ERROR = "sign_error"
    OPERATION_CONFUSION = "operation_confusion"
    ORDER_OF_OPERATIONS = "order_of_operations"
    FRACTION_ERROR = "fraction_error"
    DECIMAL_ERROR = "decimal_error"
    ALGEBRAIC_MANIPULATION = "algebraic_manipulation"
    PLACE_VALUE_ERROR = "place_value_error"
    DISTRIBUTION_ERROR = "distribution_error"
    UNKNOWN = "unknown"


class SessionStatus(str, Enum):
    """Tutoring session lifecycle states."""
    ACTIVE = "active"
    ENDED = "ended"
    RATE_LIMITED = "rate_limited"



# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ChatMessage:
    """A single message in the tutoring conversation."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    role: MessageRole = MessageRole.USER
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_api_format(self) -> Dict[str, str]:
        """Convert to the format expected by the Anthropic messages API."""
        return {"role": self.role.value, "content": self.content}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API responses / persistence."""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class TutorSession:
    """Represents a single tutoring conversation session."""
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    user_id: str = ""
    topic: Optional[str] = None
    question_context: Optional[Dict[str, Any]] = None
    grade_level: Optional[int] = None
    status: SessionStatus = SessionStatus.ACTIVE
    messages: List[ChatMessage] = field(default_factory=list)
    message_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    system_prompt: str = ""

    @property
    def is_active(self) -> bool:
        return self.status == SessionStatus.ACTIVE

    @property
    def is_rate_limited(self) -> bool:
        return self.message_count >= MAX_MESSAGES_PER_SESSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "topic": self.topic,
            "status": self.status.value,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }


@dataclass
class TutorResponse:
    """Response returned to the caller after an AI interaction."""
    session_id: str
    message: ChatMessage
    error_pattern: Optional[ErrorPattern] = None
    suggestions: List[str] = field(default_factory=list)
    is_fallback: bool = False
    remaining_messages: int = MAX_MESSAGES_PER_SESSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "message": self.message.to_dict(),
            "error_pattern": self.error_pattern.value if self.error_pattern else None,
            "suggestions": self.suggestions,
            "is_fallback": self.is_fallback,
            "remaining_messages": self.remaining_messages,
        }



# ---------------------------------------------------------------------------
# Error-pattern detection helpers
# ---------------------------------------------------------------------------

_ERROR_PATTERN_DEFINITIONS: Dict[ErrorPattern, Dict[str, str]] = {
    ErrorPattern.SIGN_ERROR: {
        "name_tr": "Isaret Hatasi",
        "description_tr": (
            "Toplama veya cikarma islemlerinde isaret (+/-) karistirmasi yapilmis. "
            "Eksi isaretini gozden kacirmis veya yanlis yere koymus olabilirsin."
        ),
        "tip_tr": "Her adimda isareti kontrol et. Negatif sayi cikarildiginda toplama donusur!",
    },
    ErrorPattern.OPERATION_CONFUSION: {
        "name_tr": "Islem Karistirmasi",
        "description_tr": (
            "Yapilmasi gereken islem ile farkli bir islem uygulanmis. "
            "Ornegin carpma yerine toplama yapilmis olabilir."
        ),
        "tip_tr": "Soruyu tekrar oku ve hangi islemin istendigine dikkat et.",
    },
    ErrorPattern.ORDER_OF_OPERATIONS: {
        "name_tr": "Islem Onceligi Hatasi",
        "description_tr": (
            "Islem onceligi kurallari (PEMDAS/BODMAS) dogru uygulanmamis. "
            "Carpma ve bolme, toplama ve cikarmadan once yapilir."
        ),
        "tip_tr": "Hatirla: Parantez > Us > Carpma/Bolme > Toplama/Cikarma.",
    },
    ErrorPattern.FRACTION_ERROR: {
        "name_tr": "Kesir Hatasi",
        "description_tr": (
            "Kesir islemlerinde hata yapilmis. Ortak payda bulmada, "
            "sadelestirmede veya kesir carpmasinda sorun olabilir."
        ),
        "tip_tr": "Toplama/cikarmada once ortak payda bul. Carpmada pay x pay, payda x payda.",
    },
    ErrorPattern.DECIMAL_ERROR: {
        "name_tr": "Ondalik Hatasi",
        "description_tr": (
            "Ondalik sayi islemlerinde virgulun yeri yanlis belirlenmis "
            "veya basamak kaydirmasi hatasi yapilmis."
        ),
        "tip_tr": "Ondalik noktasini hizala. Carpmada toplam ondalik basamak sayisini say.",
    },
    ErrorPattern.ALGEBRAIC_MANIPULATION: {
        "name_tr": "Cebirsel Islem Hatasi",
        "description_tr": (
            "Denklem cozerken terimlerin tasimasi veya sadelestirmesi sirasinda "
            "hata yapilmis. Iki tarafa ayni islemi dogru uygulamadigin olabilir."
        ),
        "tip_tr": "Bir terimi tasirken isareti degistirmeyi unutma. Iki tarafa esit isle yap.",
    },
    ErrorPattern.PLACE_VALUE_ERROR: {
        "name_tr": "Basamak Degeri Hatasi",
        "description_tr": (
            "Basamak degerleri karistirilmis. Birler, onlar veya yuzler "
            "basamagi yanlis hesaplanmis olabilir."
        ),
        "tip_tr": "Sayilari alt alta yazarken basamaklari hizala.",
    },
    ErrorPattern.DISTRIBUTION_ERROR: {
        "name_tr": "Dagitma Ozelligi Hatasi",
        "description_tr": (
            "Parantez acilirken (dagitma ozelligi) tum terimlere "
            "carpma uygulanmamis."
        ),
        "tip_tr": "a(b + c) = ab + ac.  Parantez icindeki HER terimi carp.",
    },
}


def detect_error_pattern(
    question_data: Dict[str, Any],
    user_answer: Any,
    correct_answer: Any,
) -> ErrorPattern:
    """
    Heuristic detection of the most likely error pattern.

    Analyzes the difference between the student's answer and the correct answer
    together with the question type to infer what kind of mistake was made.

    Args:
        question_data: The question definition (type, operation, expression, etc.)
        user_answer: What the student answered.
        correct_answer: The actual correct answer.

    Returns:
        The most likely ErrorPattern.
    """
    q_type = question_data.get("question_type", "").lower()
    operation = question_data.get("operation", "").lower()

    try:
        user_val = float(user_answer)
        correct_val = float(correct_answer)
    except (ValueError, TypeError):
        return ErrorPattern.UNKNOWN

    diff = user_val - correct_val

    # --- Sign error: answer has opposite sign ---
    if correct_val != 0 and abs(user_val - (-correct_val)) < 1e-9:
        return ErrorPattern.SIGN_ERROR

    # --- Fraction / decimal questions ---
    if q_type in ("fractions", "kesir"):
        return ErrorPattern.FRACTION_ERROR
    if q_type in ("decimals", "ondalik"):
        return ErrorPattern.DECIMAL_ERROR

    # --- Algebra ---
    if q_type in ("algebra", "cebir", "denklem"):
        return ErrorPattern.ALGEBRAIC_MANIPULATION

    # --- Operation confusion heuristic ---
    expression = question_data.get("expression", "")
    numbers = re.findall(r"-?\d+\.?\d*", expression)
    if len(numbers) >= 2:
        a, b = float(numbers[0]), float(numbers[1])
        operation_results: Dict[str, float] = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
        }
        if b != 0:
            operation_results["divide"] = a / b

        for op_name, op_result in operation_results.items():
            if op_name != operation and abs(user_val - op_result) < 1e-9:
                return ErrorPattern.OPERATION_CONFUSION

    # --- Order of operations (multi-operator expressions) ---
    op_chars = set("+-*/^")
    op_count = sum(1 for ch in expression if ch in op_chars)
    if op_count >= 2:
        return ErrorPattern.ORDER_OF_OPERATIONS

    # --- Place value (off by a factor of 10) ---
    if correct_val != 0:
        ratio = user_val / correct_val
        if ratio in (10, 100, 0.1, 0.01):
            return ErrorPattern.PLACE_VALUE_ERROR

    return ErrorPattern.UNKNOWN



# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

def _build_system_prompt(
    grade_level: Optional[int] = None,
    topic: Optional[str] = None,
    question_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build the system prompt that shapes MatBot's personality and pedagogy.

    The prompt is constructed dynamically based on the student's grade level,
    active topic, and any question context so that responses stay relevant.
    """
    grade_desc = ""
    if grade_level is not None:
        if grade_level <= 4:
            grade_desc = (
                "Ogrenci ilkokul seviyesinde (1-4. sinif). Cok basit ve eglenceli bir dil kullan. "
                "Somut ornekler ver (elmalar, oyuncaklar gibi). Kisa cumleler kur."
            )
        elif grade_level <= 8:
            grade_desc = (
                "Ogrenci ortaokul seviyesinde (5-8. sinif). Anlasilir ama biraz daha "
                "teknik bir dil kullanabilirsin. Gunluk hayattan ornekler ver."
            )
        else:
            grade_desc = (
                "Ogrenci lise seviyesinde (9-12. sinif). Matematiksel terminolojiyi "
                "rahatca kullanabilirsin. Soyut aciklamalar da yapabilirsin."
            )

    topic_desc = ""
    if topic:
        topic_desc = f"Su anda uzerinde calisilan konu: {topic}."

    question_desc = ""
    if question_context:
        q_type = question_context.get("question_type", "")
        expression = question_context.get("expression", "")
        difficulty = question_context.get("difficulty_tier", "")
        if expression:
            question_desc = (
                f"Aktif soru: {expression} (Tur: {q_type}, Zorluk: {difficulty})."
            )

    system_prompt = (
        'Sen "MatBot" adinda, Turkce konusan, samimi ve sabir dolu bir matematik ogretmenisin.\n'
        "Turkiye Milli Egitim Bakanligi (MEB) mufredatina uygun sekilde ogrencilere matematik ogretiyorsun.\n"
        "\n"
        "TEMEL KURALLARIN:\n"
        "1. Her zaman Turkce yaz. Matematiksel ifadeler icin standart notasyon kullan.\n"
        "2. Asla dogrudan cevabi verme. Bunun yerine yonlendirici sorular sor ve ipuclari ver.\n"
        "3. Adim adim acikla. Her adimi numaralandir.\n"
        '4. Cesaretlendirici ve pozitif bir ton kullan. "Harika dusunuyorsun!", "Cok yaklastin!" gibi ifadeler kullan.\n'
        "5. Ogrenci hata yaptiginda onu asagilama; hatayi ogrenme firsati olarak goster.\n"
        "6. Yas seviyesine uygun dil kullan.\n"
        "7. Gerektiginde gunluk hayattan ornekler ver.\n"
        "8. MEB mufredatindaki kavramlara ve terminolojiye sadik kal.\n"
        "9. Uzun aciklamalar yerine kisa ve net paragraflar tercih et.\n"
        "10. Ogrencinin anladigini teyit etmek icin ara sorular sor.\n"
        "\n"
        f"{grade_desc}\n"
        f"{topic_desc}\n"
        f"{question_desc}\n"
        "\n"
        "YASAKLAR:\n"
        "- Kufur veya uygunsuz icerik uretme.\n"
        "- Matematik disi konularda uzun sohbet etme; kibarca konuyu matemtige getir.\n"
        "- Cevabi dogrudan soyleme; ogrencinin kendi bulmasi icin yonlendir.\n"
        "- Yanlis bilgi verme. Emin olmadigin bir sey varsa duraksayarak belirt.\n"
        "\n"
        "ORNEK DAVRANIS:\n"
        'Ogrenci: "3x + 5 = 14 nasil cozulur?"\n'
        'MatBot: "Guzel soru! Hadi birlikte dusunelim. Amacimiz x\'i yalniz birakmak.\n'
        'Ilk adim olarak, esitligin iki tarafindan 5\'i cikarsak ne olur? Dene bakalim!"\n'
    )
    return system_prompt.strip()



# ---------------------------------------------------------------------------
# Fallback (offline) responses
# ---------------------------------------------------------------------------

_FALLBACK_RESPONSES: Dict[str, str] = {
    "greeting": (
        "Merhaba! Ben MatBot, senin matematik arkadasin. "
        "Su anda baglantiyi tam kuramadim ama yine de sana yardimci olmaya calisacagim. "
        "Hangi konuda calisiyorsun?"
    ),
    "explain": (
        "Su anda ayrintili aciklama yapamiyorum cunku baglantimda bir sorun var. "
        "Ama sana su ipucunu verebilirim: problemi adim adim parcalara ayir, "
        "once verilen bilgileri yaz, sonra ne bulman gerektigini belirle. "
        "Biraz sonra tekrar deneyebilirsin!"
    ),
    "error_analysis": (
        "Cevabini incelemek isterdim ama su anda tam kapasite calisamiyorum. "
        "Sana su oneriyi verebilirim: cevabini kontrol ederken islemi tersten yap. "
        "Ornegin cikarma yaptiysan, sonucu toplayarak dogrula."
    ),
    "rate_limited": (
        "Bu oturum icin mesaj limitine ulastin (maksimum {limit} mesaj). "
        "Yeni bir oturum baslat veya biraz ara verdikten sonra tekrar gel!"
    ),
    "session_ended": (
        "Bu oturum sona erdi. Yeni bir oturum baslatmak ister misin?"
    ),
    "general_error": (
        "Bir seyler ters gitti. Endise etme, biraz sonra tekrar deneyelim!"
    ),
}



# ---------------------------------------------------------------------------
# Main service class
# ---------------------------------------------------------------------------

class AITutorService:
    """
    AI-powered math tutoring service using Anthropic Claude.

    Manages tutoring sessions, conversation memory, error analysis, and
    provides curriculum-aligned explanations in Turkish.

    Usage::

        service = AITutorService()
        session = await service.start_session(user_id="u123", topic="kesirler")
        response = await service.send_message(session.session_id, "Merhaba!")
        history = service.get_session_history(session.session_id)
        await service.end_session(session.session_id)
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._sessions: Dict[str, TutorSession] = {}
        self._http_client: Optional[httpx.AsyncClient] = None

    # -- lifecycle helpers --------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize and return the shared httpx.AsyncClient."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                base_url="https://api.anthropic.com",
                headers={
                    "x-api-key": self._settings.anthropic_api_key or "",
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                timeout=httpx.Timeout(API_TIMEOUT_SECONDS),
            )
        return self._http_client

    async def close(self) -> None:
        """Close the underlying HTTP client. Call on application shutdown."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    # -- session management -------------------------------------------------

    async def start_session(
        self,
        user_id: str,
        topic: Optional[str] = None,
        question_context: Optional[Dict[str, Any]] = None,
        grade_level: Optional[int] = None,
    ) -> TutorSession:
        """
        Begin a new tutoring session.

        Args:
            user_id: Unique identifier of the student.
            topic: Optional math topic to focus on (e.g. 'kesirler').
            question_context: Optional dict describing the active question.
            grade_level: Student's school grade (1-12) for language calibration.

        Returns:
            A new TutorSession instance.
        """
        system_prompt = _build_system_prompt(
            grade_level=grade_level,
            topic=topic,
            question_context=question_context,
        )

        session = TutorSession(
            user_id=user_id,
            topic=topic,
            question_context=question_context,
            grade_level=grade_level,
            system_prompt=system_prompt,
        )

        # Build greeting text
        topic_part = ""
        if topic:
            topic_part = f"Bugun {topic} konusunda calisacagiz. "

        greeting = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=(
                f"Merhaba! Ben MatBot, senin matematik arkadasin! "
                f"{topic_part}"
                f"Sana nasil yardimci olabilirim? Istersen bir soru sor, "
                f"istersen bir problemi birlikte cozelim!"
            ),
        )
        session.messages.append(greeting)

        self._sessions[session.session_id] = session
        logger.info(
            "Tutor session started: session_id=%s user_id=%s topic=%s",
            session.session_id, user_id, topic,
        )
        return session


    async def send_message(
        self,
        session_id: str,
        user_message: str,
    ) -> TutorResponse:
        """
        Send a user message and receive the AI tutor's reply.

        Enforces rate limiting and maintains conversation memory.

        Args:
            session_id: The active session identifier.
            user_message: The student's message text.

        Returns:
            TutorResponse containing the assistant reply.

        Raises:
            ValueError: If session_id is unknown or session is no longer active.
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Bilinmeyen oturum: {session_id}")

        if session.status == SessionStatus.ENDED:
            return TutorResponse(
                session_id=session_id,
                message=ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=_FALLBACK_RESPONSES["session_ended"],
                ),
                is_fallback=True,
                remaining_messages=0,
            )

        # -- rate limit check --
        if session.is_rate_limited:
            session.status = SessionStatus.RATE_LIMITED
            return TutorResponse(
                session_id=session_id,
                message=ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=_FALLBACK_RESPONSES["rate_limited"].format(
                        limit=MAX_MESSAGES_PER_SESSION
                    ),
                ),
                is_fallback=True,
                remaining_messages=0,
            )

        # Record user message
        user_msg = ChatMessage(role=MessageRole.USER, content=user_message)
        session.messages.append(user_msg)
        session.message_count += 1

        # Build messages payload (keep within context window)
        api_messages = self._build_api_messages(session)

        # Call Claude
        assistant_text = await self._call_claude(
            system_prompt=session.system_prompt,
            messages=api_messages,
        )

        is_fallback = assistant_text in (
            _FALLBACK_RESPONSES["explain"],
            _FALLBACK_RESPONSES["general_error"],
        )

        assistant_msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=assistant_text,
            metadata={"is_fallback": is_fallback},
        )
        session.messages.append(assistant_msg)

        remaining = MAX_MESSAGES_PER_SESSION - session.message_count

        return TutorResponse(
            session_id=session_id,
            message=assistant_msg,
            is_fallback=is_fallback,
            remaining_messages=max(remaining, 0),
        )


    async def explain_question(
        self,
        question_data: Dict[str, Any],
        user_answer: Optional[str] = None,
        grade_level: Optional[int] = None,
    ) -> TutorResponse:
        """
        Generate a step-by-step explanation for a specific question.

        This is a one-shot call that does not require an active session.

        Args:
            question_data: Dict with keys like expression, question_type,
                operation, correct_answer, difficulty_tier.
            user_answer: The student's submitted answer (if any).
            grade_level: Student grade for language adjustment.

        Returns:
            TutorResponse with the explanation.
        """
        expression = question_data.get("expression", "")
        correct_answer = question_data.get("correct_answer", "")
        q_type = question_data.get("question_type", "matematik")
        difficulty = question_data.get("difficulty_tier", "orta")

        user_answer_part = ""
        if user_answer is not None:
            user_answer_part = f"\nOgrencinin verdigi cevap: {user_answer}"

        prompt = (
            f"Asagidaki matematik sorusunu adim adim acikla.\n"
            f"Soru: {expression}\n"
            f"Dogru cevap: {correct_answer}\n"
            f"Soru turu: {q_type}\n"
            f"Zorluk: {difficulty}"
            f"{user_answer_part}\n\n"
            f"Lutfen:\n"
            f"1. Soruyu anlat.\n"
            f"2. Cozumu adim adim goster.\n"
            f"3. Her adimi kisa ve net acikla.\n"
            f"4. Sonunda ogrenciye anlayip anlamadigini sor."
        )

        system = _build_system_prompt(
            grade_level=grade_level,
            topic=q_type,
            question_context=question_data,
        )

        messages = [{"role": "user", "content": prompt}]
        response_text = await self._call_claude(system_prompt=system, messages=messages)

        ephemeral_id = f"explain-{uuid.uuid4().hex[:8]}"
        msg = ChatMessage(role=MessageRole.ASSISTANT, content=response_text)

        return TutorResponse(
            session_id=ephemeral_id,
            message=msg,
            is_fallback=(response_text == _FALLBACK_RESPONSES["explain"]),
            remaining_messages=MAX_MESSAGES_PER_SESSION,
        )


    async def explain_error(
        self,
        question_data: Dict[str, Any],
        user_answer: str,
        correct_answer: str,
        grade_level: Optional[int] = None,
    ) -> TutorResponse:
        """
        Analyze why the student's answer is wrong and explain the mistake.

        Performs heuristic error-pattern detection first, then asks Claude
        for a pedagogically sound explanation.

        Args:
            question_data: The question definition dict.
            user_answer: The student's incorrect answer.
            correct_answer: The actual correct answer.
            grade_level: Student grade for language adjustment.

        Returns:
            TutorResponse with error analysis, including detected pattern.
        """
        # Detect error pattern heuristically
        pattern = detect_error_pattern(question_data, user_answer, correct_answer)
        pattern_info = _ERROR_PATTERN_DEFINITIONS.get(pattern, {})
        pattern_name = pattern_info.get("name_tr", "Bilinmeyen Hata")
        pattern_desc = pattern_info.get("description_tr", "")
        pattern_tip = pattern_info.get("tip_tr", "")

        expression = question_data.get("expression", "")
        q_type = question_data.get("question_type", "matematik")

        prompt = (
            f"Ogrenci asagidaki soruda hata yapti. Hatayi analiz et ve nazikce acikla.\n\n"
            f"Soru: {expression}\n"
            f"Soru turu: {q_type}\n"
            f"Ogrencinin cevabi: {user_answer}\n"
            f"Dogru cevap: {correct_answer}\n\n"
            f"Tespit edilen hata kalibi: {pattern_name}\n"
            f"Aciklama: {pattern_desc}\n"
            f"Ipucu: {pattern_tip}\n\n"
            f"Lutfen:\n"
            f"1. Ogrencinin hatasini kibarca belirt.\n"
            f"2. Hatanin neden kaynaklandigini acikla.\n"
            f"3. Dogru cozumu adim adim goster.\n"
            f"4. Benzer hatalari onlemek icin bir ipucu ver.\n"
            f"5. Cesaretlendirici bir mesajla bitir."
        )

        system = _build_system_prompt(
            grade_level=grade_level,
            topic=q_type,
            question_context=question_data,
        )

        messages = [{"role": "user", "content": prompt}]
        response_text = await self._call_claude(system_prompt=system, messages=messages)

        is_fallback = response_text in (
            _FALLBACK_RESPONSES["error_analysis"],
            _FALLBACK_RESPONSES["explain"],
            _FALLBACK_RESPONSES["general_error"],
        )

        # Provide actionable suggestions
        suggestions: List[str] = []
        if pattern_tip:
            suggestions.append(pattern_tip)
        if pattern == ErrorPattern.SIGN_ERROR:
            suggestions.append("Her adimda isaretin dogru oldugunu kontrol et.")
        elif pattern == ErrorPattern.ORDER_OF_OPERATIONS:
            suggestions.append(
                "Islem onceligi kuralini hatirla: PUCC (Parantez, Us, Carpma/Cikarma)."
            )
        elif pattern == ErrorPattern.FRACTION_ERROR:
            suggestions.append("Kesirlerde ortak payda bulmadan toplama/cikarma yapma.")
        elif pattern == ErrorPattern.DECIMAL_ERROR:
            suggestions.append("Islem yaparken ondalik virgullerini hizalamayi unutma.")
        elif pattern == ErrorPattern.ALGEBRAIC_MANIPULATION:
            suggestions.append(
                "Terimi esitligin diger tarafina tasirken isaretini degistir."
            )
        elif pattern == ErrorPattern.PLACE_VALUE_ERROR:
            suggestions.append("Sayilari alt alta yazarken basamak degerlerini hizala.")
        elif pattern == ErrorPattern.DISTRIBUTION_ERROR:
            suggestions.append("Parantez acarken disardaki terimi icteki her terimle carp.")
        elif pattern == ErrorPattern.OPERATION_CONFUSION:
            suggestions.append(
                "Sorudaki anahtar kelimelere dikkat et: toplam, fark, carpim, bolum."
            )

        ephemeral_id = f"error-{uuid.uuid4().hex[:8]}"
        msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=response_text,
            metadata={"error_pattern": pattern.value, "is_fallback": is_fallback},
        )

        return TutorResponse(
            session_id=ephemeral_id,
            message=msg,
            error_pattern=pattern,
            suggestions=suggestions,
            is_fallback=is_fallback,
            remaining_messages=MAX_MESSAGES_PER_SESSION,
        )


    async def suggest_approach(
        self,
        topic: str,
        difficulty: str,
        grade_level: Optional[int] = None,
    ) -> TutorResponse:
        """
        Suggest problem-solving strategies for a given topic and difficulty.

        Args:
            topic: Math topic (e.g. 'cebir', 'kesirler', 'geometri').
            difficulty: Difficulty label (e.g. 'kolay', 'orta', 'zor').
            grade_level: Student grade for language adjustment.

        Returns:
            TutorResponse with suggested strategies.
        """
        prompt = (
            f"Asagidaki konu ve zorluk seviyesi icin problem cozme stratejileri oner.\n\n"
            f"Konu: {topic}\n"
            f"Zorluk: {difficulty}\n\n"
            f"Lutfen:\n"
            f"1. Bu konudaki genel yaklasimi acikla.\n"
            f"2. 3-5 arasinda strateji ver.\n"
            f"3. Her strateji icin kisa bir ornek ver.\n"
            f"4. Sik yapilan hatalardan bahset.\n"
            f"5. Cesaretlendirici bir mesajla bitir."
        )

        system = _build_system_prompt(grade_level=grade_level, topic=topic)
        messages = [{"role": "user", "content": prompt}]
        response_text = await self._call_claude(system_prompt=system, messages=messages)

        ephemeral_id = f"approach-{uuid.uuid4().hex[:8]}"
        msg = ChatMessage(role=MessageRole.ASSISTANT, content=response_text)

        return TutorResponse(
            session_id=ephemeral_id,
            message=msg,
            is_fallback=(response_text == _FALLBACK_RESPONSES["explain"]),
            remaining_messages=MAX_MESSAGES_PER_SESSION,
        )

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve the full chat history for a session.

        Args:
            session_id: Session identifier.

        Returns:
            List of serialized ChatMessage dicts.

        Raises:
            ValueError: If the session does not exist.
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Bilinmeyen oturum: {session_id}")
        return [msg.to_dict() for msg in session.messages]

    async def end_session(self, session_id: str) -> TutorSession:
        """
        End an active tutoring session.

        Args:
            session_id: Session identifier.

        Returns:
            The ended TutorSession.

        Raises:
            ValueError: If the session does not exist.
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Bilinmeyen oturum: {session_id}")

        session.status = SessionStatus.ENDED
        session.ended_at = datetime.utcnow()

        # Append a farewell message
        farewell = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=(
                "Bugunluk bu kadar! Harika calistin. "
                "Unutma, her gun biraz pratik yapmak seni cok ileri goturur. "
                "Tekrar gorusmek uzere!"
            ),
        )
        session.messages.append(farewell)

        logger.info(
            "Tutor session ended: session_id=%s messages=%d",
            session_id, session.message_count,
        )
        return session

    def get_session(self, session_id: str) -> Optional[TutorSession]:
        """Return a session by ID, or None if not found."""
        return self._sessions.get(session_id)

    def get_active_sessions_for_user(self, user_id: str) -> List[TutorSession]:
        """Return all active sessions belonging to a given user."""
        return [
            s for s in self._sessions.values()
            if s.user_id == user_id and s.is_active
        ]


    # -- internal helpers ---------------------------------------------------

    def _build_api_messages(
        self,
        session: TutorSession,
    ) -> List[Dict[str, str]]:
        """
        Build the messages list for the Anthropic API call.

        Trims older messages to stay within CONVERSATION_CONTEXT_WINDOW
        while always keeping the most recent exchange.
        """
        # Filter to user/assistant messages only (system is sent separately)
        conversation = [
            msg.to_api_format()
            for msg in session.messages
            if msg.role in (MessageRole.USER, MessageRole.ASSISTANT)
        ]

        if len(conversation) > CONVERSATION_CONTEXT_WINDOW:
            conversation = conversation[-CONVERSATION_CONTEXT_WINDOW:]

        # Anthropic API requires the first message to be from the user.
        # If trimming left an assistant message first, prepend a synthetic user msg.
        if conversation and conversation[0]["role"] == "assistant":
            conversation.insert(0, {
                "role": "user",
                "content": "(oturum devam ediyor)",
            })

        return conversation

    async def _call_claude(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
    ) -> str:
        """
        Make an async request to the Anthropic Messages API.

        Falls back to a static response if the API key is missing,
        the request fails, or the response cannot be parsed.

        Args:
            system_prompt: The system-level instruction.
            messages: List of role/content dicts.

        Returns:
            The assistant's reply text.
        """
        if not self._settings.anthropic_api_key:
            logger.warning("Anthropic API key is not configured; returning fallback.")
            return _FALLBACK_RESPONSES["explain"]

        # Ensure first message is from user (API requirement)
        if not messages or messages[0]["role"] != "user":
            messages.insert(0, {"role": "user", "content": "Merhaba!"})

        payload = {
            "model": self._settings.anthropic_model,
            "max_tokens": MAX_TOKENS_RESPONSE,
            "system": system_prompt,
            "messages": messages,
        }

        try:
            client = await self._get_client()
            response = await client.post("/v1/messages", json=payload)
            response.raise_for_status()

            data = response.json()
            # Extract text from the first content block
            content_blocks = data.get("content", [])
            if content_blocks:
                text = content_blocks[0].get("text", "")
                if text:
                    return text

            logger.error("Claude API returned empty content: %s", data)
            return _FALLBACK_RESPONSES["explain"]

        except httpx.TimeoutException:
            logger.error(
                "Claude API request timed out after %ds.", API_TIMEOUT_SECONDS
            )
            return _FALLBACK_RESPONSES["explain"]

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Claude API HTTP error %d: %s",
                exc.response.status_code,
                exc.response.text[:500],
            )
            if exc.response.status_code == 429:
                return (
                    "Cok fazla istek gonderildi, lutfen biraz bekle ve tekrar dene. "
                    "Bu arada soruyu kagit uzerinde cozmeyi deneyebilirsin!"
                )
            return _FALLBACK_RESPONSES["explain"]

        except httpx.RequestError as exc:
            logger.error("Claude API connection error: %s", exc)
            return _FALLBACK_RESPONSES["explain"]

        except Exception:
            logger.exception("Unexpected error calling Claude API.")
            return _FALLBACK_RESPONSES["general_error"]


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

ai_tutor_service = AITutorService()
"""Global AI tutor service instance. Import this in route handlers."""
