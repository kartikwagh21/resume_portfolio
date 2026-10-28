from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.app.core.database import get_db
from backend.app.schemas import resume as resume_schemas
from backend.app.services.portfolio_service import PortfolioService
from backend.app.services.export_service import ResumeExportService
from backend.app.models.history import ResumeHistory

router = APIRouter(prefix="/resume", tags=["Resume Generation & Export"])


def assemble_tailored_data(db: Session, request: resume_schemas.TailorResumeRequest) -> Dict[str, Any]:
    """Assemble verified portfolio items according to user selections and customizations."""
    portfolio = PortfolioService.get_full_portfolio(db)
    
    # 1. Profile
    profile_dict = {
        "full_name": portfolio["profile"].full_name,
        "headline": request.target_role or portfolio["profile"].headline,
        "email": portfolio["profile"].email,
        "phone": portfolio["profile"].phone,
        "location": portfolio["profile"].location,
        "website": portfolio["profile"].website,
        "linkedin_url": portfolio["profile"].linkedin_url,
        "github_url": portfolio["profile"].github_url,
        "summary": request.custom_summary or portfolio["profile"].summary
    }

    # 2. Filter Skills
    if request.selected_skill_ids:
        skills_filtered = [s for s in portfolio["skills"] if s.id in request.selected_skill_ids]
    else:
        skills_filtered = [s for s in portfolio["skills"] if s.include_by_default]
    skills_data = [{"id": s.id, "name": s.name, "category": s.category, "proficiency": s.proficiency} for s in skills_filtered]

    # 3. Filter Experience & Apply Tailored Bullets
    if request.selected_experience_ids:
        exp_filtered = [e for e in portfolio["experience"] if e.id in request.selected_experience_ids]
    else:
        exp_filtered = [e for e in portfolio["experience"] if e.include_by_default]

    exp_data = []
    for e in exp_filtered:
        bullets = e.bullet_points
        # Check if user customized bullets
        custom_key = f"exp_{e.id}"
        if request.tailored_bullets and custom_key in request.tailored_bullets:
            bullets = request.tailored_bullets[custom_key]
        exp_data.append({
            "id": e.id,
            "company": e.company,
            "role": e.role,
            "employment_type": e.employment_type,
            "location": e.location,
            "start_date": e.start_date,
            "end_date": e.end_date,
            "is_current": e.is_current,
            "bullet_points": bullets
        })

    # 4. Filter Projects & Apply Tailored Bullets
    if request.selected_project_ids:
        proj_filtered = [p for p in portfolio["projects"] if p.id in request.selected_project_ids]
    else:
        proj_filtered = [p for p in portfolio["projects"] if p.include_by_default]

    proj_data = []
    for p in proj_filtered:
        bullets = p.bullet_points
        custom_key = f"proj_{p.id}"
        if request.tailored_bullets and custom_key in request.tailored_bullets:
            bullets = request.tailored_bullets[custom_key]
        proj_data.append({
            "id": p.id,
            "title": p.title,
            "role": p.role,
            "description": p.description,
            "tech_stack": p.tech_stack,
            "bullet_points": bullets,
            "live_url": p.live_url,
            "repo_url": p.repo_url,
            "start_date": p.start_date,
            "end_date": p.end_date
        })

    # 5. Education
    edu_data = [
        {
            "id": edu.id,
            "institution": edu.institution,
            "degree": edu.degree,
            "field_of_study": edu.field_of_study,
            "start_date": edu.start_date,
            "end_date": edu.end_date,
            "gpa": edu.gpa,
            "highlights": edu.highlights
        }
        for edu in portfolio["education"] if edu.include_by_default
    ]

    # 6. Certifications
    if request.selected_cert_ids:
        cert_filtered = [c for c in portfolio["certifications"] if c.id in request.selected_cert_ids]
    else:
        cert_filtered = [c for c in portfolio["certifications"] if c.include_by_default]

    cert_data = [
        {
            "id": c.id,
            "name": c.name,
            "issuer": c.issuer,
            "issue_date": c.issue_date,
            "credential_id": c.credential_id
        }
        for c in cert_filtered
    ]

    # 7. Achievements
    ach_data = [
        {
            "id": a.id,
            "title": a.title,
            "issuer": a.issuer,
            "date": a.date,
            "description": a.description
        }
        for a in portfolio["achievements"] if a.include_by_default
    ]

    return {
        "profile": profile_dict,
        "summary": request.custom_summary or profile_dict["summary"],
        "skills": skills_data,
        "experience": exp_data,
        "projects": proj_data,
        "education": edu_data,
        "certifications": cert_data,
        "achievements": ach_data
    }


@router.post("/preview", response_model=resume_schemas.ResumePreviewResponse)
def generate_resume_preview(request: resume_schemas.TailorResumeRequest, db: Session = Depends(get_db)):
    resume_data = assemble_tailored_data(db, request)
    html_preview = ResumeExportService.generate_html_preview(resume_data, template_name=request.template_name)
    
    history_id = None
    if request.save_to_history:
        record = ResumeHistory(
            target_role=request.target_role,
            target_company=request.target_company,
            jd_text=request.jd_text or "",
            selected_ids={
                "skills": request.selected_skill_ids,
                "projects": request.selected_project_ids,
                "experience": request.selected_experience_ids,
                "certifications": request.selected_cert_ids
            },
            generated_summary=request.custom_summary,
            tailored_bullets=request.tailored_bullets or {},
            template_name=request.template_name,
            match_score=request.match_score
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        history_id = record.id

    return {
        "html_preview": html_preview,
        "template_name": request.template_name,
        "history_id": history_id,
        "resume_data": resume_data
    }


@router.post("/export/pdf")
def export_pdf_resume(request: resume_schemas.TailorResumeRequest, db: Session = Depends(get_db)):
    resume_data = assemble_tailored_data(db, request)
    pdf_bytes = ResumeExportService.generate_pdf(resume_data, template_name=request.template_name)
    filename = f"Resume_{request.target_role.replace(' ', '_')}_{request.template_name}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/export/docx")
def export_docx_resume(request: resume_schemas.TailorResumeRequest, db: Session = Depends(get_db)):
    resume_data = assemble_tailored_data(db, request)
    docx_bytes = ResumeExportService.generate_docx(resume_data, template_name=request.template_name)
    filename = f"Resume_{request.target_role.replace(' ', '_')}_{request.template_name}.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/history", response_model=List[resume_schemas.ResumeHistoryItemResponse])
def get_resume_history(db: Session = Depends(get_db)):
    items = db.query(ResumeHistory).order_by(ResumeHistory.id.desc()).all()
    results = []
    for it in items:
        results.append({
            "id": it.id,
            "target_role": it.target_role,
            "target_company": it.target_company,
            "template_name": it.template_name,
            "match_score": it.match_score,
            "created_at": it.created_at,
            "selected_ids": it.selected_ids,
            "generated_summary": it.generated_summary
        })
    return results


@router.get("/history/{history_id}")
def load_resume_history_item(history_id: int, db: Session = Depends(get_db)):
    item = db.query(ResumeHistory).filter(ResumeHistory.id == history_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Resume history configuration not found")
    return {
        "id": item.id,
        "target_role": item.target_role,
        "target_company": item.target_company,
        "jd_text": item.jd_text,
        "selected_ids": item.selected_ids,
        "generated_summary": item.generated_summary,
        "tailored_bullets": item.tailored_bullets,
        "template_name": item.template_name,
        "match_score": item.match_score,
        "created_at": item.created_at
    }
