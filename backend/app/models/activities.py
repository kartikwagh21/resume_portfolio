from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(100), nullable=False)
    proficiency = Column(String(50), nullable=False, default="Professional")  # Native, Fluent, Professional, Conversational
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class ExtraActivity(Base):
    __tablename__ = "extra_activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    organization = Column(String(150), nullable=True)
    role = Column(String(100), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    include_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
