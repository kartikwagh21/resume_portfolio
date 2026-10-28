from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas import portfolio as schemas
from backend.app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


# ---------------- AGGREGATE ----------------
@router.get("", response_model=schemas.PortfolioFullResponse)
def get_full_portfolio(db: Session = Depends(get_db)):
    return PortfolioService.get_full_portfolio(db)


# ---------------- EDUCATION ----------------
@router.get("/education", response_model=List[schemas.EducationResponse])
def get_education(db: Session = Depends(get_db)):
    return PortfolioService.list_education(db)


@router.post("/education", response_model=schemas.EducationResponse, status_code=status.HTTP_201_CREATED)
def add_education(data: schemas.EducationCreate, db: Session = Depends(get_db)):
    return PortfolioService.create_education(db, data)


@router.put("/education/{item_id}", response_model=schemas.EducationResponse)
def edit_education(item_id: int, data: schemas.EducationUpdate, db: Session = Depends(get_db)):
    updated = PortfolioService.update_education(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Education record not found")
    return updated


@router.delete("/education/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_education(item_id: int, db: Session = Depends(get_db)):
    if not PortfolioService.delete_education(db, item_id):
        raise HTTPException(status_code=404, detail="Education record not found")
    return None


# ---------------- SKILLS ----------------
@router.get("/skills", response_model=List[schemas.SkillResponse])
def get_skills(db: Session = Depends(get_db)):
    return PortfolioService.list_skills(db)


@router.post("/skills", response_model=schemas.SkillResponse, status_code=status.HTTP_201_CREATED)
def add_skill(data: schemas.SkillCreate, db: Session = Depends(get_db)):
    return PortfolioService.create_skill(db, data)


@router.put("/skills/{item_id}", response_model=schemas.SkillResponse)
def edit_skill(item_id: int, data: schemas.SkillUpdate, db: Session = Depends(get_db)):
    updated = PortfolioService.update_skill(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Skill record not found")
    return updated


@router.delete("/skills/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_skill(item_id: int, db: Session = Depends(get_db)):
    if not PortfolioService.delete_skill(db, item_id):
        raise HTTPException(status_code=404, detail="Skill record not found")
    return None


# ---------------- PROJECTS ----------------
@router.get("/projects", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return PortfolioService.list_projects(db)


@router.post("/projects", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def add_project(data: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return PortfolioService.create_project(db, data)


@router.put("/projects/{item_id}", response_model=schemas.ProjectResponse)
def edit_project(item_id: int, data: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    updated = PortfolioService.update_project(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Project record not found")
    return updated


@router.delete("/projects/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project(item_id: int, db: Session = Depends(get_db)):
    if not PortfolioService.delete_project(db, item_id):
        raise HTTPException(status_code=404, detail="Project record not found")
    return None


# ---------------- EXPERIENCE ----------------
@router.get("/experience", response_model=List[schemas.ExperienceResponse])
def get_experience(db: Session = Depends(get_db)):
    return PortfolioService.list_experience(db)


@router.post("/experience", response_model=schemas.ExperienceResponse, status_code=status.HTTP_201_CREATED)
def add_experience(data: schemas.ExperienceCreate, db: Session = Depends(get_db)):
    return PortfolioService.create_experience(db, data)


@router.put("/experience/{item_id}", response_model=schemas.ExperienceResponse)
def edit_experience(item_id: int, data: schemas.ExperienceUpdate, db: Session = Depends(get_db)):
    updated = PortfolioService.update_experience(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Experience record not found")
    return updated


@router.delete("/experience/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_experience(item_id: int, db: Session = Depends(get_db)):
    if not PortfolioService.delete_experience(db, item_id):
        raise HTTPException(status_code=404, detail="Experience record not found")
    return None


# ---------------- CERTIFICATIONS ----------------
@router.get("/certifications", response_model=List[schemas.CertificationResponse])
def get_certifications(db: Session = Depends(get_db)):
    return PortfolioService.list_certifications(db)


@router.post("/certifications", response_model=schemas.CertificationResponse, status_code=status.HTTP_201_CREATED)
def add_certification(data: schemas.CertificationCreate, db: Session = Depends(get_db)):
    return PortfolioService.create_certification(db, data)


@router.put("/certifications/{item_id}", response_model=schemas.CertificationResponse)
def edit_certification(item_id: int, data: schemas.CertificationUpdate, db: Session = Depends(get_db)):
    updated = PortfolioService.update_certification(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Certification record not found")
    return updated


@router.delete("/certifications/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_certification(item_id: int, db: Session = Depends(get_db)):
    if not PortfolioService.delete_certification(db, item_id):
        raise HTTPException(status_code=404, detail="Certification record not found")
    return None


# ---------------- ACHIEVEMENTS ----------------
@router.get("/achievements", response_model=List[schemas.AchievementResponse])
def get_achievements(db: Session = Depends(get_db)):
    return PortfolioService.list_achievements(db)


@router.post("/achievements", response_model=schemas.AchievementResponse, status_code=status.HTTP_201_CREATED)
def add_achievement(data: schemas.AchievementCreate, db: Session = Depends(get_db)):
    return PortfolioService.create_achievement(db, data)


@router.put("/achievements/{item_id}", response_model=schemas.AchievementResponse)
def edit_achievement(item_id: int, data: schemas.AchievementUpdate, db: Session = Depends(get_db)):
    updated = PortfolioService.update_achievement(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Achievement record not found")
    return updated


@router.delete("/achievements/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_achievement(item_id: int, db: Session = Depends(get_db)):
    if not PortfolioService.delete_achievement(db, item_id):
        raise HTTPException(status_code=404, detail="Achievement record not found")
    return None


# ---------------- PUBLICATIONS ----------------
@router.get("/publications", response_model=List[schemas.PublicationResponse])
def get_publications(db: Session = Depends(get_db)):
    return PortfolioService.list_publications(db)


@router.post("/publications", response_model=schemas.PublicationResponse, status_code=status.HTTP_201_CREATED)
def add_publication(data: schemas.PublicationCreate, db: Session = Depends(get_db)):
    return PortfolioService.create_publication(db, data)


@router.put("/publications/{item_id}", response_model=schemas.PublicationResponse)
def edit_publication(item_id: int, data: schemas.PublicationUpdate, db: Session = Depends(get_db)):
    updated = PortfolioService.update_publication(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Publication record not found")
    return updated


@router.delete("/publications/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_publication(item_id: int, db: Session = Depends(get_db)):
    if not PortfolioService.delete_publication(db, item_id):
        raise HTTPException(status_code=404, detail="Publication record not found")
    return None


# ---------------- LANGUAGES ----------------
@router.get("/languages", response_model=List[schemas.LanguageResponse])
def get_languages(db: Session = Depends(get_db)):
    return PortfolioService.list_languages(db)


@router.post("/languages", response_model=schemas.LanguageResponse, status_code=status.HTTP_201_CREATED)
def add_language(data: schemas.LanguageCreate, db: Session = Depends(get_db)):
    return PortfolioService.create_language(db, data)


@router.put("/languages/{item_id}", response_model=schemas.LanguageResponse)
def edit_language(item_id: int, data: schemas.LanguageUpdate, db: Session = Depends(get_db)):
    updated = PortfolioService.update_language(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Language record not found")
    return updated


@router.delete("/languages/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_language(item_id: int, db: Session = Depends(get_db)):
    if not PortfolioService.delete_language(db, item_id):
        raise HTTPException(status_code=404, detail="Language record not found")
    return None


# ---------------- EXTRA ACTIVITIES ----------------
@router.get("/activities", response_model=List[schemas.ExtraActivityResponse])
def get_extra_activities(db: Session = Depends(get_db)):
    return PortfolioService.list_extra_activities(db)


@router.post("/activities", response_model=schemas.ExtraActivityResponse, status_code=status.HTTP_201_CREATED)
def add_extra_activity(data: schemas.ExtraActivityCreate, db: Session = Depends(get_db)):
    return PortfolioService.create_extra_activity(db, data)


@router.put("/activities/{item_id}", response_model=schemas.ExtraActivityResponse)
def edit_extra_activity(item_id: int, data: schemas.ExtraActivityUpdate, db: Session = Depends(get_db)):
    updated = PortfolioService.update_extra_activity(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Activity record not found")
    return updated


@router.delete("/activities/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_extra_activity(item_id: int, db: Session = Depends(get_db)):
    if not PortfolioService.delete_extra_activity(db, item_id):
        raise HTTPException(status_code=404, detail="Activity record not found")
    return None
