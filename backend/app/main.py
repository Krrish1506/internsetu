from __future__ import annotations

from fastapi import FastAPI

from app.database import engine, Base
from app.routers import students, internships, matching

# Initialize database schema (simple setup).
# ⚠️ For production, consider Alembic migrations instead of auto-create.
Base.metadata.create_all(bind=engine)

# Application entrypoint
app = FastAPI(
    title="Internship Matcher Service",
    version="1.0",
    description="Lightweight API for linking students with internships"
)

# Attach routers from different feature modules
app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(internships.router, prefix="/internships", tags=["Internships"])
app.include_router(matching.router, prefix="/matching", tags=["Matching"])

@app.get("/health", tags=["System"])
def check_health() -> dict[str, str]:
    """Quick endpoint to verify the service is up."""
    return {"status": "healthy"}
