from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.app.core.database import get_db
from backend.app.services.matching_service import MatchingService
from backend.app.services.portfolio_service import PortfolioService
from backend.app.ai.gemini_client import gemini_client
from backend.app.ai.guardrails import AntiHallucinationGuard
from backend.app.ai.prompts import BULLET_REPHRASE_PROMPT

router = APIRouter(prefix="/matching", tags=["Matching & Verification"])


class MatchRequest(BaseModel):
    jd_text: str = Field(..., min_length=20)


class RephraseBulletRequest(BaseModel):
    original_bullet: str = Field(..., min_length=5)
    keywords: Optional[str] = "scalability, performance, latency"
    target_role: Optional[str] = "Software Engineer"


@router.post("/match")
def match_portfolio(request: MatchRequest, db: Session = Depends(get_db)):
    return MatchingService.match_portfolio_to_jd(db, request.jd_text)


@router.post("/rephrase-bullet")
def rephrase_bullet(request: RephraseBulletRequest, db: Session = Depends(get_db)):
    """Rephrase a bullet point with strict zero-hallucination verification and automatic fallback."""
    portfolio = PortfolioService.get_full_portfolio(db)
    allowed_skills = {s.name for s in portfolio["skills"]}

    # Function to attempt AI rephrasing via Gemini
    def call_ai(bullet: str, strict_warning: str = "") -> str:
        if not gemini_client.is_configured:
            # Deterministic rephrase: strengthen action verb without inventing facts
            clean_b = bullet.strip().rstrip(".")
            return f"Spearheaded and delivered: {clean_b}."
        
        prompt = BULLET_REPHRASE_PROMPT.format(
            original_bullet=bullet + (f" [STRICT NOTE: {strict_warning}]" if strict_warning else ""),
            keywords=request.keywords,
            verified_skills=", ".join(list(allowed_skills)[:15])
        )
        res = gemini_client.generate_json(prompt, temperature=0.0)
        return res.get("rephrased_bullet", bullet)

    candidate_rephrase = call_ai(request.original_bullet)

    # Retry callback for the guardrail
    def retry_callback(original: str, issues: List[str]) -> str:
        warning_msg = f"Do NOT include unverified tokens: {', '.join(issues)}. Use ONLY exact metrics from original."
        return call_ai(original, warning_msg)

    # Pass through Anti-Hallucination Guard
    final_bullet, status, issues = AntiHallucinationGuard.guard_bullet_rephrase(
        original_bullet=request.original_bullet,
        candidate_rephrase=candidate_rephrase,
        allowed_skills=allowed_skills,
        retry_callback=retry_callback
    )

    return {
        "original_bullet": request.original_bullet,
        "rephrased_bullet": final_bullet,
        "verification_status": status,
        "is_verified": status in ("VERIFIED_CLEAN", "VERIFIED_AFTER_RETRY"),
        "issues_detected": issues
    }
