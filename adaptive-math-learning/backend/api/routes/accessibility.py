"""Accessibility API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ...services.accessibility_service import (
    tts_service,
    accessibility_settings_service,
    multi_language_service,
    special_education_service,
    SimplificationLevel,
)

router = APIRouter(prefix="/accessibility", tags=["Accessibility"])


class UpdateSettingsRequest(BaseModel):
    font_size: Optional[int] = None
    high_contrast: Optional[bool] = None
    dyslexia_font: Optional[str] = None
    color_blind_mode: Optional[str] = None
    screen_reader_mode: Optional[bool] = None
    reduced_motion: Optional[bool] = None
    language: Optional[str] = None
    auto_read_questions: Optional[bool] = None
    extra_time_multiplier: Optional[float] = None
    simplified_ui: Optional[bool] = None
    text_spacing: Optional[float] = None
    cursor_size: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    language: str = "tr"

class SimplifyRequest(BaseModel):
    question_data: Dict[str, Any]
    level: str = "moderate"  # "minimal", "moderate", "maximum"


@router.get("/settings/{user_id}")
async def get_settings(user_id: str):
    """Kullanici erisebilirlik ayarlarini getir."""
    prefs = accessibility_settings_service.get_settings(user_id)
    return {"status": "success", "settings": prefs.to_dict()}


@router.put("/settings/{user_id}")
async def update_settings(user_id: str, req: UpdateSettingsRequest):
    """Erisebilirlik ayarlarini guncelle."""
    try:
        updates = req.dict(exclude_none=True)
        prefs = accessibility_settings_service.update_settings(user_id, updates)
        return {"status": "success", "settings": prefs.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tts")
async def generate_speech(req: TTSRequest):
    """Metinden sese donustur."""
    try:
        result = tts_service.generate_speech(text=req.text, lang=req.language)
        return {"status": "success", "speech": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/glossary/{term}")
async def get_math_glossary(term: str, lang: str = "tr"):
    """Matematik terimi sozluk girisi getir."""
    entry = multi_language_service.get_math_glossary(term, lang)
    if entry is None:
        raise HTTPException(status_code=404, detail="Terim bulunamadi.")
    return {"status": "success", "entry": entry}


@router.get("/glossary")
async def search_glossary(q: str = "", lang: str = "tr"):
    """Sozlukte ara."""
    if not q:
        raise HTTPException(status_code=400, detail="Arama sorgusu gerekli.")
    results = multi_language_service.search_glossary(q, lang)
    return {"status": "success", "results": results, "count": len(results)}


@router.get("/languages")
async def get_available_languages():
    """Desteklenen dilleri listele."""
    languages = multi_language_service.get_available_languages()
    return {"status": "success", "languages": languages}


@router.post("/simplify")
async def get_simplified_question(req: SimplifyRequest):
    """Soruyu basitlestir (ozel egitim destegi)."""
    try:
        level = SimplificationLevel(req.level)
        simplified = special_education_service.get_simplified_question(
            question_data=req.question_data,
            level=level,
        )
        return {"status": "success", "simplified": simplified.to_dict()}
    except ValueError:
        raise HTTPException(status_code=400, detail="Gecersiz basitlestirme seviyesi.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/scaffolding")
async def get_scaffolding(req: SimplifyRequest):
    """Ek ogrenme destegi getir."""
    try:
        level = SimplificationLevel(req.level)
        scaffolding = special_education_service.get_extra_scaffolding(
            question_data=req.question_data,
            level=level,
        )
        return {"status": "success", "scaffolding": scaffolding.to_dict()}
    except ValueError:
        raise HTTPException(status_code=400, detail="Gecersiz seviye.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/celebration")
async def get_celebration():
    """Rastgele Turkce kutlama mesaji getir."""
    message = special_education_service.celebration_feedback()
    return {"status": "success", "message": message}
