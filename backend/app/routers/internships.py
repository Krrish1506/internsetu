from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/internships", tags=["Internships"])

@router.post("/", response_model=schemas.InternshipRead)
def create_internship(payload: schemas.InternshipCreate, db: Session = Depends(get_db)):
    job = models.Internship(
        company_name=payload.company_name,
        suggested_role=payload.suggested_role,
        location=payload.location,
        min_cgpa=payload.min_cgpa,
        field=payload.field,
        program=payload.program,
    )
    db.add(job); db.commit(); db.refresh(job)
    return job

@router.get("/{internship_id}", response_model=schemas.InternshipRead)
def get_internship(internship_id: int, db: Session = Depends(get_db)):
    job = db.get(models.Internship, internship_id)
    if not job:
        raise HTTPException(status_code=404, detail="Internship not found.")
    return job

@router.get("/", response_model=list[schemas.InternshipRead])
def list_internships(db: Session = Depends(get_db)):
    return db.query(models.Internship).order_by(models.Internship.id.desc()).all()
