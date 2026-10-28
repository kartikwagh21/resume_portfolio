from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.app.schemas.portfolio import (
    ProfileBase, EducationBase, SkillBase, ProjectBase, ExperienceBase,
    CertificationBase, AchievementBase, PublicationBase, LanguageBase, ExtraActivityBase
)


# ---------------- SMART IMPORT SCHEMAS ----------------
class SmartImportParseRequest(BaseModel):
    raw_text: str = Field(..., min_length=10)


class SmartImportDraftResponse(BaseModel):
    profile: Optional[ProfileBase] = None
    education: List[EducationBase] = Field(default_factory=list)
    skills: List[SkillBase] = Field(default_factory=list)
    projects: List[ProjectBase] = Field(default_factory=list)
    experience: List[ExperienceBase] = Field(default_factory=list)
    certifications: List[CertificationBase] = Field(default_factory=list)
    achievements: List[AchievementBase] = Field(default_factory=list)
    publications: List[PublicationBase] = Field(default_factory=list)
    languages: List[LanguageBase] = Field(default_factory=list)
    extra_activities: List[ExtraActivityBase] = Field(default_factory=list)
    raw_source_length: int = 0
    parsing_engine: str = "gemini"


class SmartImportCommitRequest(BaseModel):
    profile: Optional[ProfileBase] = None
    education: List[EducationBase] = Field(default_factory=list)
    skills: List[SkillBase] = Field(default_factory=list)
    projects: List[ProjectBase] = Field(default_factory=list)
    experience: List[ExperienceBase] = Field(default_factory=list)
    certifications: List[CertificationBase] = Field(default_factory=list)
    achievements: List[AchievementBase] = Field(default_factory=list)
    publications: List[PublicationBase] = Field(default_factory=list)
    languages: List[LanguageBase] = Field(default_factory=list)
    extra_activities: List[ExtraActivityBase] = Field(default_factory=list)
    replace_existing: bool = False  # If True, cleans existing records before inserting


# ---------------- JD ANALYSIS SCHEMAS ----------------
class JDAnalysisRequest(BaseModel):
    jd_text: str = Field(..., min_length=20)


class JDAnalysisResponse(BaseModel):
    role_title: str
    company: Optional[str] = "Target Company"
    seniority_level: Optional[str] = "Mid-Senior"
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    tools_and_technologies: List[str] = Field(default_factory=list)
    key_responsibilities: List[str] = Field(default_factory=list)
    summary_requirements: Optional[str] = None
    parsing_engine: str = "gemini"
