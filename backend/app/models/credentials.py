from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    issuer = Column(String(150), nullable=False)
    issue_date = Column(String(50), nullable=False)
    expiry_date = Column(String(50), nullable=True)
    credential_id = Column(String(150), nullable=True)
    credential_url = Column(String(255), nullable=True)
    include_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    issuer = Column(String(150), nullable=True)
    date = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    include_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    publisher = Column(String(200), nullable=True)  # Conference, journal, or publisher
    publication_date = Column(String(50), nullable=True)
    url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    include_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
