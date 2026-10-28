import json
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from backend.app.core.database import Base


class ResumeHistory(Base):
    __tablename__ = "resume_history"

    id = Column(Integer, primary_key=True, index=True)
    target_role = Column(String(200), nullable=False)
    target_company = Column(String(150), nullable=True)
    jd_text = Column(Text, nullable=False)
    selected_ids_json = Column(Text, nullable=False, default="{}")
    generated_summary = Column(Text, nullable=True)
    tailored_bullets_json = Column(Text, nullable=True, default="{}")
    template_name = Column(String(100), default="modern_clean")
    match_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    @property
    def selected_ids(self):
        try:
            return json.loads(self.selected_ids_json) if self.selected_ids_json else {}
        except Exception:
            return {}

    @selected_ids.setter
    def selected_ids(self, value):
        self.selected_ids_json = json.dumps(value if isinstance(value, dict) else {})

    @property
    def tailored_bullets(self):
        try:
            return json.loads(self.tailored_bullets_json) if self.tailored_bullets_json else {}
        except Exception:
            return {}

    @tailored_bullets.setter
    def tailored_bullets(self, value):
        self.tailored_bullets_json = json.dumps(value if isinstance(value, dict) else {})
