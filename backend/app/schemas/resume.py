from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TailorResumeRequest(BaseModel):
    target_role: str = Field(default="Software Engineer", min_length=2)
    target_company: Optional[str] = "Target Company"
    jd_text: Optional[str] = ""
    selected_skill_ids: List[int] = Field(default_factory=list)
    selected_project_ids: List[int] = Field(default_factory=list)
    selected_experience_ids: List[int] = Field(default_factory=list)
    selected_cert_ids: List[int] = Field(default_factory=list)
    custom_summary: Optional[str] = None
    tailored_bullets: Optional[Dict[str, List[str]]] = Field(default_factory=dict)
    template_name: str = Field(default="modern_clean")  # "modern_clean" or "classic_ivy"
    match_score: Optional[float] = None
    save_to_history: bool = False


class ResumeHistoryItemResponse(BaseModel):
    id: int
    target_role: str
    target_company: Optional[str]
    template_name: str
    match_score: Optional[float]
    created_at: Optional[datetime]
    selected_ids: Dict[str, Any]
    generated_summary: Optional[str]


class ResumePreviewResponse(BaseModel):
    html_preview: str
    template_name: str
    history_id: Optional[int] = None
    resume_data: Dict[str, Any]
