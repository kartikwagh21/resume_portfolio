from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import Base, engine
import backend.app.models  # Ensure all models are registered

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CareerVault & ResumeForge AI Backend API"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "status": "online"
    }


# Include Routers
from backend.app.api.v1.profile import router as profile_router
from backend.app.api.v1.portfolio import router as portfolio_router
from backend.app.api.v1.smart_import import router as import_router
from backend.app.api.v1.jd_analysis import router as jd_router
from backend.app.api.v1.matching import router as matching_router
from backend.app.api.v1.sheets import router as sheets_router
from backend.app.api.v1.resume import router as resume_router

app.include_router(profile_router, prefix=settings.API_V1_STR)
app.include_router(portfolio_router, prefix=settings.API_V1_STR)
app.include_router(import_router, prefix=settings.API_V1_STR)
app.include_router(jd_router, prefix=settings.API_V1_STR)
app.include_router(matching_router, prefix=settings.API_V1_STR)
app.include_router(sheets_router, prefix=settings.API_V1_STR)
app.include_router(resume_router, prefix=settings.API_V1_STR)
