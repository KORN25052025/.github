"""Hint and Solution API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
from dataclasses import asdict

from ...services.hint_service import hint_service

router = APIRouter(prefix="/hints", tags=["Hints & Solutions"])


class GetHintsRequest(BaseModel):
    question_type: str
    operation: Optional[str] = None
    expression: str
    difficulty_tier: int = 1


class GetSolutionRequest(BaseModel):
    question_type: str
    operation: Optional[str] = None
    expression: str
    correct_answer: str
    params: Optional[Dict[str, Any]] = None


@router.post("/get")
async def get_hints(req: GetHintsRequest):
    """Soru icin ipuclari getir."""
    try:
        hints = hint_service.get_hints(
            question_type=req.question_type,
            operation=req.operation,
            expression=req.expression,
            difficulty_tier=req.difficulty_tier,
        )
        return {
            "hints": [
                {
                    "level": h.level.value,
                    "text": h.text,
                    "text_tr": h.text_tr,
                    "xp_cost": h.xp_cost,
                }
                for h in hints
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/solution")
async def get_solution(req: GetSolutionRequest):
    """Adim adim cozum getir."""
    try:
        solution = hint_service.get_solution_steps(
            question_type=req.question_type,
            operation=req.operation,
            expression=req.expression,
            correct_answer=req.correct_answer,
            params=req.params,
        )
        return {
            "question_id": solution.question_id,
            "total_steps": solution.total_steps,
            "final_answer": solution.final_answer,
            "final_answer_latex": solution.final_answer_latex,
            "steps": [
                {
                    "step_number": s.step_number,
                    "description": s.description,
                    "description_tr": s.description_tr,
                    "expression": s.expression,
                    "expression_latex": s.expression_latex,
                    "explanation": s.explanation,
                    "explanation_tr": s.explanation_tr,
                }
                for s in solution.steps
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
