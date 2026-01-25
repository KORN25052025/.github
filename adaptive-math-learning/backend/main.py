"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db
from .api.routes import questions, answers, sessions, topics, progress, gamification, teacher, parent

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Adaptive Mathematics Learning System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend
# In production, set CORS_ORIGINS env var to restrict allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(topics.router, prefix="/api/v1", tags=["Topics"])
app.include_router(questions.router, prefix="/api/v1", tags=["Questions"])
app.include_router(answers.router, prefix="/api/v1", tags=["Answers"])
app.include_router(sessions.router, prefix="/api/v1", tags=["Sessions"])
app.include_router(progress.router, prefix="/api/v1", tags=["Progress"])
app.include_router(gamification.router, prefix="/api/v1", tags=["Gamification"])
app.include_router(teacher.router, prefix="/api/v1", tags=["Teacher Dashboard"])
app.include_router(parent.router, prefix="/api/v1", tags=["Parent Dashboard"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
