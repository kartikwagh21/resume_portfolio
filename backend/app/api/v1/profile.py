from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas import portfolio as schemas
from backend.app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=schemas.ProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    return PortfolioService.get_or_create_profile(db)


@router.put("", response_model=schemas.ProfileResponse)
def update_profile(data: schemas.ProfileUpdate, db: Session = Depends(get_db)):
    return PortfolioService.update_profile(db, data)
