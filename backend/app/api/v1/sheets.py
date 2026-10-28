from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.app.core.database import get_db
from backend.app.services.sheets_service import SheetsService

router = APIRouter(prefix="/sheets", tags=["Google Sheets Sync"])


class SheetsActionRequest(BaseModel):
    spreadsheet_id: Optional[str] = None


@router.get("/status")
def get_sheets_sync_status():
    return SheetsService.get_sync_status()


@router.post("/export")
def export_portfolio_to_sheets(payload: SheetsActionRequest = SheetsActionRequest(), db: Session = Depends(get_db)):
    return SheetsService.export_to_sheets(db, spreadsheet_id=payload.spreadsheet_id)


@router.post("/sync")
def sync_portfolio_from_sheets(payload: SheetsActionRequest = SheetsActionRequest(), db: Session = Depends(get_db)):
    return SheetsService.sync_from_sheets(db, spreadsheet_id=payload.spreadsheet_id)
