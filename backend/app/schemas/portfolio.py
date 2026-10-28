from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime


# ------------------ PROFILE ------------------
class ProfileBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    headline: Optional[str] = Field(None, max_length=200)
    email: str = Field(..., max_length=150)
    phone: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    linkedin_url: Optional[str] = Field(None, max_length=200)
    github_url: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    headline: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    summary: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ EDUCATION ------------------
class EducationBase(BaseModel):
    institution: str = Field(..., min_length=1, max_length=200)
    degree: str = Field(..., min_length=1, max_length=150)
    field_of_study: str = Field(..., min_length=1, max_length=150)
    location: Optional[str] = None
    start_date: str = Field(..., min_length=1)
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    highlights: Optional[List[str]] = Field(default_factory=list)
    include_by_default: bool = True


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    highlights: Optional[List[str]] = None
    include_by_default: Optional[bool] = None


class EducationResponse(EducationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ SKILLS ------------------
class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Literal["technical", "soft", "tool"] = "technical"
    proficiency: Literal["beginner", "intermediate", "advanced", "expert"] = "intermediate"
    include_by_default: bool = True


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[Literal["technical", "soft", "tool"]] = None
    proficiency: Optional[Literal["beginner", "intermediate", "advanced", "expert"]] = None
    include_by_default: Optional[bool] = None


class SkillResponse(SkillBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ PROJECTS ------------------
class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    role: Optional[str] = None
    description: str = Field(..., min_length=1)
    tech_stack: Optional[List[str]] = Field(default_factory=list)
    bullet_points: Optional[List[str]] = Field(default_factory=list)
    live_url: Optional[str] = None
    repo_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    include_by_default: bool = True


class ProjectCreate(ProjectBase):
    skill_ids: Optional[List[int]] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    bullet_points: Optional[List[str]] = None
    live_url: Optional[str] = None
    repo_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    include_by_default: Optional[bool] = None
    skill_ids: Optional[List[int]] = None


class ProjectResponse(ProjectBase):
    id: int
    skills: List[SkillResponse] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ EXPERIENCE ------------------
class ExperienceBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=150)
    role: str = Field(..., min_length=1, max_length=150)
    employment_type: str = "Full-time"
    location: Optional[str] = None
    start_date: str = Field(..., min_length=1)
    end_date: Optional[str] = None
    is_current: bool = False
    bullet_points: Optional[List[str]] = Field(default_factory=list)
    include_by_default: bool = True


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    bullet_points: Optional[List[str]] = None
    include_by_default: Optional[bool] = None


class ExperienceResponse(ExperienceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ CERTIFICATIONS ------------------
class CertificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    issuer: str = Field(..., min_length=1, max_length=150)
    issue_date: str = Field(..., min_length=1)
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    include_by_default: bool = True


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    include_by_default: Optional[bool] = None


class CertificationResponse(CertificationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ ACHIEVEMENTS ------------------
class AchievementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    issuer: Optional[str] = None
    date: Optional[str] = None
    description: str = Field(..., min_length=1)
    include_by_default: bool = True


class AchievementCreate(AchievementBase):
    pass


class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    include_by_default: Optional[bool] = None


class AchievementResponse(AchievementBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ PUBLICATIONS ------------------
class PublicationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=250)
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    include_by_default: bool = True


class PublicationCreate(PublicationBase):
    pass


class PublicationUpdate(BaseModel):
    title: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    include_by_default: Optional[bool] = None


class PublicationResponse(PublicationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ LANGUAGES ------------------
class LanguageBase(BaseModel):
    language: str = Field(..., min_length=1, max_length=100)
    proficiency: str = Field(default="Professional", max_length=50)


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    language: Optional[str] = None
    proficiency: Optional[str] = None


class LanguageResponse(LanguageBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ EXTRA ACTIVITIES ------------------
class ExtraActivityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    organization: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: str = Field(..., min_length=1)
    include_by_default: bool = True


class ExtraActivityCreate(ExtraActivityBase):
    pass


class ExtraActivityUpdate(BaseModel):
    title: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    include_by_default: Optional[bool] = None


class ExtraActivityResponse(ExtraActivityBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ------------------ AGGREGATE PORTFOLIO ------------------
class PortfolioFullResponse(BaseModel):
    profile: Optional[ProfileResponse] = None
    education: List[EducationResponse] = Field(default_factory=list)
    skills: List[SkillResponse] = Field(default_factory=list)
    projects: List[ProjectResponse] = Field(default_factory=list)
    experience: List[ExperienceResponse] = Field(default_factory=list)
    certifications: List[CertificationResponse] = Field(default_factory=list)
    achievements: List[AchievementResponse] = Field(default_factory=list)
    publications: List[PublicationResponse] = Field(default_factory=list)
    languages: List[LanguageResponse] = Field(default_factory=list)
    extra_activities: List[ExtraActivityResponse] = Field(default_factory=list)
    counts: dict = Field(default_factory=dict)
