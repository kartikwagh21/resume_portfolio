from fastapi import APIRouter, HTTPException
from backend.app.schemas import ai as ai_schemas
from backend.app.ai.gemini_client import gemini_client

router = APIRouter(prefix="/jd", tags=["Job Description Analysis"])


@router.post("/analyze", response_model=ai_schemas.JDAnalysisResponse)
def analyze_job_description(request: ai_schemas.JDAnalysisRequest):
    if len(request.jd_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Job description text is too short to analyze.")
    analysis = gemini_client.analyze_job_description(request.jd_text)
    return analysis
