from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.portfolio import (
    Profile, Education, Skill, Project, Experience, project_skills
)
from backend.app.models.credentials import Certification, Achievement, Publication
from backend.app.models.activities import Language, ExtraActivity
from backend.app.models.history import ResumeHistory
from backend.app.schemas import portfolio as schemas


class PortfolioService:
    @staticmethod
    def get_or_create_profile(db: Session) -> Profile:
        profile = db.query(Profile).first()
        if not profile:
            profile = Profile(
                full_name="Your Name",
                headline="Software Engineer",
                email="you@example.com",
                summary="Passionate software engineer."
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    @staticmethod
    def update_profile(db: Session, update_data: schemas.ProfileUpdate) -> Profile:
        profile = PortfolioService.get_or_create_profile(db)
        data = update_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(profile, key, value)
        db.commit()
        db.refresh(profile)
        return profile

    # ---------------- EDUCATION ----------------
    @staticmethod
    def list_education(db: Session) -> List[Education]:
        return db.query(Education).order_by(Education.id.desc()).all()

    @staticmethod
    def create_education(db: Session, data: schemas.EducationCreate) -> Education:
        item = Education(
            institution=data.institution,
            degree=data.degree,
            field_of_study=data.field_of_study,
            location=data.location,
            start_date=data.start_date,
            end_date=data.end_date,
            gpa=data.gpa,
            highlights=data.highlights,
            include_by_default=data.include_by_default
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_education(db: Session, item_id: int, data: schemas.EducationUpdate) -> Optional[Education]:
        item = db.query(Education).filter(Education.id == item_id).first()
        if not item:
            return None
        dump = data.model_dump(exclude_unset=True)
        if "highlights" in dump:
            item.highlights = dump.pop("highlights")
        for k, v in dump.items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_education(db: Session, item_id: int) -> bool:
        item = db.query(Education).filter(Education.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    # ---------------- SKILLS ----------------
    @staticmethod
    def list_skills(db: Session) -> List[Skill]:
        return db.query(Skill).order_by(Skill.category, Skill.name).all()

    @staticmethod
    def create_skill(db: Session, data: schemas.SkillCreate) -> Skill:
        # Check if already exists
        existing = db.query(Skill).filter(func.lower(Skill.name) == func.lower(data.name.strip())).first()
        if existing:
            existing.category = data.category
            existing.proficiency = data.proficiency
            existing.include_by_default = data.include_by_default
            db.commit()
            db.refresh(existing)
            return existing
        item = Skill(
            name=data.name.strip(),
            category=data.category,
            proficiency=data.proficiency,
            include_by_default=data.include_by_default
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_skill(db: Session, item_id: int, data: schemas.SkillUpdate) -> Optional[Skill]:
        item = db.query(Skill).filter(Skill.id == item_id).first()
        if not item:
            return None
        dump = data.model_dump(exclude_unset=True)
        for k, v in dump.items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_skill(db: Session, item_id: int) -> bool:
        item = db.query(Skill).filter(Skill.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    # ---------------- PROJECTS ----------------
    @staticmethod
    def list_projects(db: Session) -> List[Project]:
        return db.query(Project).order_by(Project.id.desc()).all()

    @staticmethod
    def create_project(db: Session, data: schemas.ProjectCreate) -> Project:
        item = Project(
            title=data.title,
            role=data.role,
            description=data.description,
            tech_stack=data.tech_stack,
            bullet_points=data.bullet_points,
            live_url=data.live_url,
            repo_url=data.repo_url,
            start_date=data.start_date,
            end_date=data.end_date,
            include_by_default=data.include_by_default
        )
        if data.skill_ids:
            skills = db.query(Skill).filter(Skill.id.in_(data.skill_ids)).all()
            item.skills = skills
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_project(db: Session, item_id: int, data: schemas.ProjectUpdate) -> Optional[Project]:
        item = db.query(Project).filter(Project.id == item_id).first()
        if not item:
            return None
        dump = data.model_dump(exclude_unset=True)
        if "bullet_points" in dump:
            item.bullet_points = dump.pop("bullet_points")
        if "tech_stack" in dump:
            item.tech_stack = dump.pop("tech_stack")
        if "skill_ids" in dump:
            skill_ids = dump.pop("skill_ids")
            if skill_ids is not None:
                skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
                item.skills = skills
        for k, v in dump.items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_project(db: Session, item_id: int) -> bool:
        item = db.query(Project).filter(Project.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    # ---------------- EXPERIENCE ----------------
    @staticmethod
    def list_experience(db: Session) -> List[Experience]:
        return db.query(Experience).order_by(Experience.id.desc()).all()

    @staticmethod
    def create_experience(db: Session, data: schemas.ExperienceCreate) -> Experience:
        item = Experience(
            company=data.company,
            role=data.role,
            employment_type=data.employment_type,
            location=data.location,
            start_date=data.start_date,
            end_date=data.end_date,
            is_current=data.is_current,
            bullet_points=data.bullet_points,
            include_by_default=data.include_by_default
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_experience(db: Session, item_id: int, data: schemas.ExperienceUpdate) -> Optional[Experience]:
        item = db.query(Experience).filter(Experience.id == item_id).first()
        if not item:
            return None
        dump = data.model_dump(exclude_unset=True)
        if "bullet_points" in dump:
            item.bullet_points = dump.pop("bullet_points")
        for k, v in dump.items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_experience(db: Session, item_id: int) -> bool:
        item = db.query(Experience).filter(Experience.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    # ---------------- CERTIFICATIONS ----------------
    @staticmethod
    def list_certifications(db: Session) -> List[Certification]:
        return db.query(Certification).order_by(Certification.id.desc()).all()

    @staticmethod
    def create_certification(db: Session, data: schemas.CertificationCreate) -> Certification:
        item = Certification(**data.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_certification(db: Session, item_id: int, data: schemas.CertificationUpdate) -> Optional[Certification]:
        item = db.query(Certification).filter(Certification.id == item_id).first()
        if not item:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_certification(db: Session, item_id: int) -> bool:
        item = db.query(Certification).filter(Certification.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    # ---------------- ACHIEVEMENTS ----------------
    @staticmethod
    def list_achievements(db: Session) -> List[Achievement]:
        return db.query(Achievement).order_by(Achievement.id.desc()).all()

    @staticmethod
    def create_achievement(db: Session, data: schemas.AchievementCreate) -> Achievement:
        item = Achievement(**data.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_achievement(db: Session, item_id: int, data: schemas.AchievementUpdate) -> Optional[Achievement]:
        item = db.query(Achievement).filter(Achievement.id == item_id).first()
        if not item:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_achievement(db: Session, item_id: int) -> bool:
        item = db.query(Achievement).filter(Achievement.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    # ---------------- PUBLICATIONS ----------------
    @staticmethod
    def list_publications(db: Session) -> List[Publication]:
        return db.query(Publication).order_by(Publication.id.desc()).all()

    @staticmethod
    def create_publication(db: Session, data: schemas.PublicationCreate) -> Publication:
        item = Publication(**data.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_publication(db: Session, item_id: int, data: schemas.PublicationUpdate) -> Optional[Publication]:
        item = db.query(Publication).filter(Publication.id == item_id).first()
        if not item:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_publication(db: Session, item_id: int) -> bool:
        item = db.query(Publication).filter(Publication.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    # ---------------- LANGUAGES ----------------
    @staticmethod
    def list_languages(db: Session) -> List[Language]:
        return db.query(Language).order_by(Language.id.desc()).all()

    @staticmethod
    def create_language(db: Session, data: schemas.LanguageCreate) -> Language:
        item = Language(**data.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_language(db: Session, item_id: int, data: schemas.LanguageUpdate) -> Optional[Language]:
        item = db.query(Language).filter(Language.id == item_id).first()
        if not item:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_language(db: Session, item_id: int) -> bool:
        item = db.query(Language).filter(Language.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    # ---------------- EXTRA ACTIVITIES ----------------
    @staticmethod
    def list_extra_activities(db: Session) -> List[ExtraActivity]:
        return db.query(ExtraActivity).order_by(ExtraActivity.id.desc()).all()

    @staticmethod
    def create_extra_activity(db: Session, data: schemas.ExtraActivityCreate) -> ExtraActivity:
        item = ExtraActivity(**data.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_extra_activity(db: Session, item_id: int, data: schemas.ExtraActivityUpdate) -> Optional[ExtraActivity]:
        item = db.query(ExtraActivity).filter(ExtraActivity.id == item_id).first()
        if not item:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_extra_activity(db: Session, item_id: int) -> bool:
        item = db.query(ExtraActivity).filter(ExtraActivity.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    # ---------------- COMPLETE PORTFOLIO ----------------
    @staticmethod
    def get_full_portfolio(db: Session) -> Dict[str, Any]:
        profile = PortfolioService.get_or_create_profile(db)
        education = PortfolioService.list_education(db)
        skills = PortfolioService.list_skills(db)
        projects = PortfolioService.list_projects(db)
        experience = PortfolioService.list_experience(db)
        certifications = PortfolioService.list_certifications(db)
        achievements = PortfolioService.list_achievements(db)
        publications = PortfolioService.list_publications(db)
        languages = PortfolioService.list_languages(db)
        extra_activities = PortfolioService.list_extra_activities(db)

        counts = {
            "education": len(education),
            "skills": len(skills),
            "projects": len(projects),
            "experience": len(experience),
            "certifications": len(certifications),
            "achievements": len(achievements),
            "publications": len(publications),
            "languages": len(languages),
            "extra_activities": len(extra_activities)
        }

        return {
            "profile": profile,
            "education": education,
            "skills": skills,
            "projects": projects,
            "experience": experience,
            "certifications": certifications,
            "achievements": achievements,
            "publications": publications,
            "languages": languages,
            "extra_activities": extra_activities,
            "counts": counts
        }
