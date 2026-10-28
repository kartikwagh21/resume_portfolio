import logging
import json
import re
from typing import Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.ai.prompts import (
    RESUME_PARSE_PROMPT, JD_ANALYSIS_PROMPT, PORTFOLIO_MATCH_PROMPT, BULLET_REPHRASE_PROMPT
)
from backend.app.ai.parsers import clean_and_parse_json

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self._client = None
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize google-genai Client: {e}")

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def generate_json(self, prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        """Generate structured JSON from Gemini with fallback handling."""
        if not self.is_configured:
            logger.warning("Gemini API key not configured or client initialization skipped.")
            return {}

        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json"
            )
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            parsed = clean_and_parse_json(response.text)
            if parsed is not None:
                return parsed
            logger.error("Failed to parse Gemini response as JSON.")
            return {}
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise e

    # ---------------- SMART RESUME PARSING ----------------
    def parse_resume_text(self, raw_text: str) -> Dict[str, Any]:
        """Convert unstructured resume text to structured portfolio draft."""
        if self.is_configured:
            prompt = RESUME_PARSE_PROMPT.format(raw_text=raw_text)
            try:
                result = self.generate_json(prompt, temperature=0.1)
                if result:
                    result["parsing_engine"] = "gemini"
                    return result
            except Exception as e:
                logger.warning(f"Gemini resume parsing failed ({e}), falling back to heuristic parser.")

        # Heuristic fallback parser
        return self._heuristic_parse_resume(raw_text)

    # ---------------- JD ANALYSIS ----------------
    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Extract structured criteria from a job description."""
        if self.is_configured:
            prompt = JD_ANALYSIS_PROMPT.format(jd_text=jd_text)
            try:
                result = self.generate_json(prompt, temperature=0.1)
                if result:
                    result["parsing_engine"] = "gemini"
                    return result
            except Exception as e:
                logger.warning(f"Gemini JD analysis failed ({e}), falling back to heuristic parser.")

        # Heuristic fallback parser
        return self._heuristic_parse_jd(jd_text)

    # ---------------- HEURISTIC FALLBACKS ----------------
    def _heuristic_parse_jd(self, text: str) -> Dict[str, Any]:
        """Deterministic heuristic extraction when Gemini is unavailable."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        role_title = lines[0] if lines else "Target Software Role"
        # Try to clean role title
        if ":" in role_title:
            role_title = role_title.split(":")[-1].strip()

        common_skills = [
            "Python", "FastAPI", "React", "TypeScript", "JavaScript", "Docker", "Kubernetes",
            "SQL", "PostgreSQL", "AWS", "GCP", "Azure", "Git", "Redis", "Kafka", "Node.js",
            "CI/CD", "Terraform", "Pandas", "GraphQL", "Agile", "Linux", "REST APIs"
        ]
        
        found_skills = [s for s in common_skills if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE)]
        req_skills = found_skills[:6] if len(found_skills) >= 6 else found_skills
        pref_skills = found_skills[6:] if len(found_skills) > 6 else ["System Architecture", "Leadership"]

        responsibilities = []
        for line in lines:
            if line.startswith(("-", "•", "*")) or any(verb in line.lower() for verb in ["develop", "build", "lead", "architect", "collaborate", "design"]):
                cleaned_line = re.sub(r"^[-•*]\s*", "", line).strip()
                if len(cleaned_line) > 15:
                    responsibilities.append(cleaned_line)
            if len(responsibilities) >= 5:
                break

        return {
            "role_title": role_title,
            "company": "Target Organization",
            "seniority_level": "Mid-Senior Level",
            "required_skills": req_skills,
            "preferred_skills": pref_skills,
            "keywords": req_skills + ["Scalability", "High Availability", "Microservices"],
            "tools_and_technologies": [s for s in found_skills if s in ["Docker", "Kubernetes", "Git", "Terraform", "AWS", "Redis"]],
            "key_responsibilities": responsibilities or [
                "Design and maintain scalable distributed web systems.",
                "Collaborate with cross-functional teams to deliver customer-facing features.",
                "Ensure high test coverage, code reliability, and operational monitoring."
            ],
            "summary_requirements": f"Seeking a skilled engineer proficient in {', '.join(req_skills[:3]) if req_skills else 'software engineering'} to deliver resilient cloud software.",
            "parsing_engine": "heuristic_fallback"
        }

    def _heuristic_parse_resume(self, text: str) -> Dict[str, Any]:
        """Deterministic heuristic resume parser when Gemini is unavailable."""
        # Extract email and phone
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        full_name = lines[0] if lines else "Candidate Name"
        
        common_skills = [
            "Python", "FastAPI", "React", "TypeScript", "JavaScript", "Docker", "Kubernetes",
            "SQL", "PostgreSQL", "AWS", "Git", "Redis", "Kafka", "Node.js", "Terraform"
        ]
        found_skills = [
            {"name": s, "category": "technical", "proficiency": "advanced"}
            for s in common_skills if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE)
        ]

        return {
            "profile": {
                "full_name": full_name,
                "headline": "Software Engineer",
                "email": email_match.group(0) if email_match else "candidate@example.com",
                "phone": phone_match.group(0) if phone_match else None,
                "location": "San Francisco, CA",
                "website": None,
                "linkedin_url": None,
                "github_url": None,
                "summary": "Experienced engineer with a focus on scalable systems and high-quality software."
            },
            "education": [
                {
                    "institution": "University / College",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "location": None,
                    "start_date": "2018",
                    "end_date": "2022",
                    "gpa": None,
                    "highlights": []
                }
            ],
            "skills": found_skills,
            "projects": [],
            "experience": [],
            "certifications": [],
            "achievements": [],
            "publications": [],
            "languages": [{"language": "English", "proficiency": "Professional"}],
            "extra_activities": [],
            "raw_source_length": len(text),
            "parsing_engine": "heuristic_fallback"
        }


gemini_client = GeminiClient()
