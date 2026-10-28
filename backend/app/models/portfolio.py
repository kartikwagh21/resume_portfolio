import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base

# Association table for Project <-> Skill (Many-to-Many)
project_skills = Table(
    "project_skills",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    headline = Column(String(200), nullable=True)
    email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=True)
    location = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    linkedin_url = Column(String(200), nullable=True)
    github_url = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String(200), nullable=False)
    degree = Column(String(150), nullable=False)
    field_of_study = Column(String(150), nullable=False)
    location = Column(String(100), nullable=True)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=True)  # Can be 'Present' or date
    gpa = Column(String(20), nullable=True)
    highlights_json = Column(Text, nullable=True, default="[]")  # List of accomplishments / coursework
    include_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    @property
    def highlights(self):
        try:
            return json.loads(self.highlights_json) if self.highlights_json else []
        except Exception:
            return []

    @highlights.setter
    def highlights(self, value):
        self.highlights_json = json.dumps(value if isinstance(value, list) else [])


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False, default="technical")  # technical, soft, tool
    proficiency = Column(String(50), nullable=False, default="intermediate")  # beginner, intermediate, advanced, expert
    include_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    projects = relationship("Project", secondary=project_skills, back_populates="skills")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    role = Column(String(150), nullable=True)
    description = Column(Text, nullable=False)
    tech_stack_json = Column(Text, nullable=True, default="[]")  # List of tech/libraries
    bullet_points_json = Column(Text, nullable=True, default="[]")  # Bullet points
    live_url = Column(String(255), nullable=True)
    repo_url = Column(String(255), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    include_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    skills = relationship("Skill", secondary=project_skills, back_populates="projects")

    @property
    def bullet_points(self):
        try:
            return json.loads(self.bullet_points_json) if self.bullet_points_json else []
        except Exception:
            return []

    @bullet_points.setter
    def bullet_points(self, value):
        self.bullet_points_json = json.dumps(value if isinstance(value, list) else [])

    @property
    def tech_stack(self):
        try:
            return json.loads(self.tech_stack_json) if self.tech_stack_json else []
        except Exception:
            return []

    @tech_stack.setter
    def tech_stack(self, value):
        self.tech_stack_json = json.dumps(value if isinstance(value, list) else [])


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(150), nullable=False)
    role = Column(String(150), nullable=False)
    employment_type = Column(String(50), default="Full-time")  # Full-time, Internship, Contract, Freelance
    location = Column(String(100), nullable=True)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=True)
    is_current = Column(Boolean, default=False)
    bullet_points_json = Column(Text, nullable=True, default="[]")
    include_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    @property
    def bullet_points(self):
        try:
            return json.loads(self.bullet_points_json) if self.bullet_points_json else []
        except Exception:
            return []

    @bullet_points.setter
    def bullet_points(self, value):
        self.bullet_points_json = json.dumps(value if isinstance(value, list) else [])
