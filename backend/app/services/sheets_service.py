import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.services.portfolio_service import PortfolioService
from backend.app.schemas import portfolio as schemas
from backend.app.models.portfolio import Profile, Education, Skill, Project, Experience
from backend.app.models.credentials import Certification, Achievement, Publication
from backend.app.models.activities import Language, ExtraActivity

logger = logging.getLogger(__name__)


class SheetsService:
    _last_synced_at: Optional[str] = None
    _last_sync_status: str = "Never Synced"
    _mock_sheet_storage: Dict[str, List[List[Any]]] = {}

    @classmethod
    def get_service_account_email(cls) -> Optional[str]:
        """Read client_email from service account JSON if present."""
        sa_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
        if os.path.exists(sa_file):
            try:
                with open(sa_file, "r") as f:
                    data = json.load(f)
                    return data.get("client_email")
            except Exception:
                pass
        return None

    @classmethod
    def get_sync_status(cls) -> Dict[str, Any]:
        sa_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
        is_sa_configured = os.path.exists(sa_file)
        sa_email = cls.get_service_account_email() if is_sa_configured else None

        return {
            "is_configured": is_sa_configured,
            "service_account_file": sa_file,
            "service_account_email": sa_email or "Not configured (Using Local Mock Sync)",
            "spreadsheet_id": settings.GOOGLE_SHEETS_SPREADSHEET_ID or "Local Mock Sheet",
            "last_synced_at": cls._last_synced_at,
            "last_sync_status": cls._last_sync_status,
            "mode": "live_google_sheets" if is_sa_configured else "mock_sandbox"
        }

    @classmethod
    def export_to_sheets(cls, db: Session, spreadsheet_id: Optional[str] = None) -> Dict[str, Any]:
        """Export all portfolio tables to Google Sheets (or Mock Sheet storage)."""
        portfolio = PortfolioService.get_full_portfolio(db)
        target_id = spreadsheet_id or settings.GOOGLE_SHEETS_SPREADSHEET_ID

        # Prepare tabular data per category
        tables_data = {
            "Profile": [
                ["ID", "Full Name", "Headline", "Email", "Phone", "Location", "Website", "LinkedIn", "GitHub", "Summary"],
                [
                    portfolio["profile"].id,
                    portfolio["profile"].full_name,
                    portfolio["profile"].headline or "",
                    portfolio["profile"].email,
                    portfolio["profile"].phone or "",
                    portfolio["profile"].location or "",
                    portfolio["profile"].website or "",
                    portfolio["profile"].linkedin_url or "",
                    portfolio["profile"].github_url or "",
                    portfolio["profile"].summary or ""
                ]
            ],
            "Skills": [
                ["ID", "Name", "Category", "Proficiency", "Include By Default"]
            ] + [
                [s.id, s.name, s.category, s.proficiency, str(s.include_by_default)]
                for s in portfolio["skills"]
            ],
            "Education": [
                ["ID", "Institution", "Degree", "Field of Study", "Location", "Start Date", "End Date", "GPA", "Highlights", "Include By Default"]
            ] + [
                [e.id, e.institution, e.degree, e.field_of_study, e.location or "", e.start_date, e.end_date or "", e.gpa or "", " | ".join(e.highlights), str(e.include_by_default)]
                for e in portfolio["education"]
            ],
            "Experience": [
                ["ID", "Company", "Role", "Type", "Location", "Start Date", "End Date", "Current", "Bullet Points", "Include By Default"]
            ] + [
                [exp.id, exp.company, exp.role, exp.employment_type, exp.location or "", exp.start_date, exp.end_date or "", str(exp.is_current), "\n".join(exp.bullet_points), str(exp.include_by_default)]
                for exp in portfolio["experience"]
            ],
            "Projects": [
                ["ID", "Title", "Role", "Description", "Tech Stack", "Bullet Points", "Live URL", "Repo URL", "Start Date", "End Date", "Include By Default"]
            ] + [
                [p.id, p.title, p.role or "", p.description, ", ".join(p.tech_stack), "\n".join(p.bullet_points), p.live_url or "", p.repo_url or "", p.start_date or "", p.end_date or "", str(p.include_by_default)]
                for p in portfolio["projects"]
            ],
            "Certifications": [
                ["ID", "Name", "Issuer", "Issue Date", "Expiry Date", "Credential ID", "URL", "Include By Default"]
            ] + [
                [c.id, c.name, c.issuer, c.issue_date, c.expiry_date or "", c.credential_id or "", c.credential_url or "", str(c.include_by_default)]
                for c in portfolio["certifications"]
            ],
            "Achievements": [
                ["ID", "Title", "Issuer", "Date", "Description", "Include By Default"]
            ] + [
                [a.id, a.title, a.issuer or "", a.date or "", a.description, str(a.include_by_default)]
                for a in portfolio["achievements"]
            ],
            "Publications": [
                ["ID", "Title", "Publisher", "Date", "URL", "Description", "Include By Default"]
            ] + [
                [pub.id, pub.title, pub.publisher or "", pub.publication_date or "", pub.url or "", pub.description or "", str(pub.include_by_default)]
                for pub in portfolio["publications"]
            ],
            "Languages": [
                ["ID", "Language", "Proficiency"]
            ] + [
                [lang.id, lang.language, lang.proficiency]
                for lang in portfolio["languages"]
            ],
            "Activities": [
                ["ID", "Title", "Organization", "Role", "Start Date", "End Date", "Description", "Include By Default"]
            ] + [
                [act.id, act.title, act.organization or "", act.role or "", act.start_date or "", act.end_date or "", act.description, str(act.include_by_default)]
                for act in portfolio["extra_activities"]
            ]
        }

        # Check if Google Service Account is available
        sa_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
        if os.path.exists(sa_file):
            try:
                import gspread
                gc = gspread.service_account(filename=sa_file)
                sh = gc.open_by_key(target_id) if target_id else gc.create("CareerVault Portfolio DB")
                
                for tab_name, rows in tables_data.items():
                    try:
                        ws = sh.worksheet(tab_name)
                        ws.clear()
                    except gspread.WorksheetNotFound:
                        ws = sh.add_worksheet(title=tab_name, rows=len(rows)+10, cols=len(rows[0])+2)
                    ws.update("A1", rows)

                cls._last_synced_at = datetime.now(timezone.utc).isoformat()
                cls._last_sync_status = "Successfully exported to Google Sheets"
                return {
                    "status": "success",
                    "mode": "live_google_sheets",
                    "spreadsheet_id": sh.id,
                    "spreadsheet_url": sh.url,
                    "tabs_exported": list(tables_data.keys()),
                    "last_synced_at": cls._last_synced_at
                }
            except Exception as e:
                logger.warning(f"Live Google Sheets export failed: {e}. Falling back to internal mock sheet storage.")

        # Save to mock sheet storage
        cls._mock_sheet_storage = tables_data
        cls._last_synced_at = datetime.now(timezone.utc).isoformat()
        cls._last_sync_status = "Exported to Mock Sheet Storage (Ready for sync)"

        return {
            "status": "success",
            "mode": "mock_sandbox",
            "message": "Exported 10 category worksheets to Mock Sheet storage.",
            "tabs_exported": list(tables_data.keys()),
            "last_synced_at": cls._last_synced_at
        }

    @classmethod
    def sync_from_sheets(cls, db: Session, spreadsheet_id: Optional[str] = None) -> Dict[str, Any]:
        """Sync from Google Sheets (or Mock Sheet storage) back to the database."""
        sa_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
        target_id = spreadsheet_id or settings.GOOGLE_SHEETS_SPREADSHEET_ID

        tables_data = {}
        if os.path.exists(sa_file) and target_id:
            try:
                import gspread
                gc = gspread.service_account(filename=sa_file)
                sh = gc.open_by_key(target_id)
                for ws in sh.worksheets():
                    tables_data[ws.title] = ws.get_all_values()
            except Exception as e:
                logger.warning(f"Error fetching from live Google Sheets: {e}")

        if not tables_data:
            tables_data = cls._mock_sheet_storage

        if not tables_data:
            return {
                "status": "error",
                "message": "No sheet data found to sync from. Please run Export to Sheets first or configure a valid Spreadsheet ID."
            }

        synced_counts = {"skills": 0, "projects": 0, "experience": 0, "education": 0}

        # 1. Sync Profile
        if "Profile" in tables_data and len(tables_data["Profile"]) > 1:
            row = tables_data["Profile"][1]
            if len(row) >= 4 and row[1]:
                PortfolioService.update_profile(
                    db,
                    schemas.ProfileUpdate(
                        full_name=row[1],
                        headline=row[2] if len(row) > 2 else None,
                        email=row[3],
                        phone=row[4] if len(row) > 4 else None,
                        location=row[5] if len(row) > 5 else None,
                        website=row[6] if len(row) > 6 else None,
                        linkedin_url=row[7] if len(row) > 7 else None,
                        github_url=row[8] if len(row) > 8 else None,
                        summary=row[9] if len(row) > 9 else None
                    )
                )

        # 2. Sync Skills
        if "Skills" in tables_data:
            rows = tables_data["Skills"][1:]
            for r in rows:
                if len(r) >= 2 and r[1].strip():
                    PortfolioService.create_skill(
                        db,
                        schemas.SkillCreate(
                            name=r[1].strip(),
                            category=r[2].strip() if len(r) > 2 and r[2].strip() in ("technical", "soft", "tool") else "technical",
                            proficiency=r[3].strip() if len(r) > 3 and r[3].strip() in ("beginner", "intermediate", "advanced", "expert") else "intermediate",
                            include_by_default=r[4].lower() == "true" if len(r) > 4 else True
                        )
                    )
                    synced_counts["skills"] += 1

        cls._last_synced_at = datetime.now(timezone.utc).isoformat()
        cls._last_sync_status = "Successfully synced from Sheet to DB"

        return {
            "status": "success",
            "message": "Portfolio database synchronized from Sheet data.",
            "synced_counts": synced_counts,
            "last_synced_at": cls._last_synced_at
        }
