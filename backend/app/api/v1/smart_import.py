from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas import ai as ai_schemas
from backend.app.schemas import portfolio as port_schemas
from backend.app.ai.gemini_client import gemini_client
from backend.app.ai.parsers import extract_text_from_file_bytes
from backend.app.services.portfolio_service import PortfolioService
from backend.app.models.portfolio import Profile, Education, Skill, Project, Experience
from backend.app.models.credentials import Certification, Achievement, Publication
from backend.app.models.activities import Language, ExtraActivity

router = APIRouter(prefix="/import", tags=["Smart Import"])


@router.post("/parse-text", response_model=ai_schemas.SmartImportDraftResponse)
def parse_resume_text(request: ai_schemas.SmartImportParseRequest):
    if len(request.raw_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Resume text is too short to analyze.")
    parsed = gemini_client.parse_resume_text(request.raw_text)
    parsed["raw_source_length"] = len(request.raw_text)
    return parsed


@router.post("/parse-file", response_model=ai_schemas.SmartImportDraftResponse)
async def parse_resume_file(file: UploadFile = File(...)):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    extracted_text = extract_text_from_file_bytes(contents, file.filename or "resume.txt")
    if not extracted_text or len(extracted_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Could not extract readable text from the uploaded file.")

    parsed = gemini_client.parse_resume_text(extracted_text)
    parsed["raw_source_length"] = len(extracted_text)
    return parsed


@router.post("/commit", status_code=status.HTTP_200_OK)
def commit_imported_portfolio(
    payload: ai_schemas.SmartImportCommitRequest,
    db: Session = Depends(get_db)
):
    """Save user-reviewed smart import fields into database."""
    if payload.replace_existing:
        # Clear out existing portfolio entities if requested
        db.query(Education).delete()
        db.query(Project).delete()
        db.query(Experience).delete()
        db.query(Certification).delete()
        db.query(Achievement).delete()
        db.query(Publication).delete()
        db.query(Language).delete()
        db.query(ExtraActivity).delete()
        # Keep profile but will update fields
        db.commit()

    # 1. Profile
    if payload.profile:
        PortfolioService.update_profile(
            db,
            port_schemas.ProfileUpdate(**payload.profile.model_dump(exclude_unset=True))
        )

    # 2. Skills
    for s in payload.skills:
        PortfolioService.create_skill(db, port_schemas.SkillCreate(**s.model_dump()))

    # 3. Education
    for edu in payload.education:
        PortfolioService.create_education(db, port_schemas.EducationCreate(**edu.model_dump()))

    # 4. Experience
    for exp in payload.experience:
        PortfolioService.create_experience(db, port_schemas.ExperienceCreate(**exp.model_dump()))

    # 5. Projects
    for proj in payload.projects:
        PortfolioService.create_project(db, port_schemas.ProjectCreate(**proj.model_dump()))

    # 6. Certifications
    for cert in payload.certifications:
        PortfolioService.create_certification(db, port_schemas.CertificationCreate(**cert.model_dump()))

    # 7. Achievements
    for ach in payload.achievements:
        PortfolioService.create_achievement(db, port_schemas.AchievementCreate(**ach.model_dump()))

    # 8. Publications
    for pub in payload.publications:
        PortfolioService.create_publication(db, port_schemas.PublicationCreate(**pub.model_dump()))

    # 9. Languages
    for lang in payload.languages:
        PortfolioService.create_language(db, port_schemas.LanguageCreate(**lang.model_dump()))

    # 10. Extra Activities
    for act in payload.extra_activities:
        PortfolioService.create_extra_activity(db, port_schemas.ExtraActivityCreate(**act.model_dump()))

    return {
        "status": "success",
        "message": "Portfolio updated successfully from smart import.",
        "committed_counts": {
            "skills": len(payload.skills),
            "education": len(payload.education),
            "experience": len(payload.experience),
            "projects": len(payload.projects),
            "certifications": len(payload.certifications)
        }
    }
