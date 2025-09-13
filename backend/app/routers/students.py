from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=schemas.StudentRead)
def add_student(data: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Insert a new student into the system.
    - Email is forced to lowercase for consistency.
    - Duplicate email check is done here before saving.
    """
    normalized_email = str(data.email).strip().lower()

    if db.query(models.Student).filter(models.Student.email == normalized_email).first():
        raise HTTPException(status_code=400, detail="Email already exists. Please try another one.")

    student = models.Student(
        full_name=data.full_name.strip(),
        email=normalized_email,
        password=data.password,  # 🔒 in real-world apps, hash the password
        college=(data.college or "").strip(),
        cgpa=data.cgpa,
        location=(data.location or "").strip(),
        skills=(data.skills or "").strip(),
        qualification=(data.qualification or "").strip(),
        bio=(data.bio or None),
    )

    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=schemas.StudentRead)
def read_student(student_id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a student by their ID.
    Returns 404 if no match is found.
    """
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="No student found with that ID.")
    return student


@router.get("/", response_model=list[schemas.StudentRead])
def get_all_students(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 25,
):
    """
    List students ordered by newest first.
    Pagination supported with `skip` and `limit`.
    """
    query = db.query(models.Student).order_by(models.Student.id.desc())
    return query.offset(skip).limit(limit).all()
