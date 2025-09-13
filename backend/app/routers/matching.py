from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/match", tags=["Matching"])


def _score(student: models.Student, job: models.Internship) -> float:
    """Simple scoring logic between a student and an internship."""
    if student.cgpa < job.min_cgpa:
        return 0.0

    # 1) CGPA fit
    cgpa_fit = min(
        1.0,
        0.7 + 0.3 * ((student.cgpa - job.min_cgpa) / 3.0)
        if student.cgpa > job.min_cgpa else 0.7
    )

    # 2) Field match (ignore if student.field not present)
    field_val = getattr(student, "field", None)
    field_match = 1.0 if field_val and field_val.strip().lower() == job.field.strip().lower() else 0.5

    # 3) Location match
    location_match = 1.0 if (
        student.location.strip().lower() == job.location.strip().lower()
        and student.location.strip()
    ) else 0.6

    # 4) Skills vs role tokens
    student_skills = {s.strip().lower() for s in (student.skills or "").split(",") if s.strip()}
    role_tokens = {t.lower() for t in (job.suggested_role or "").split() if t}
    overlap = student_skills & role_tokens
    role_alignment = 0.6 + 0.4 * (len(overlap) / max(1, len(role_tokens))) if role_tokens else 0.6

    # Weighted average
    return round(0.35 * cgpa_fit + 0.20 * location_match + 0.45 * role_alignment, 4)


@router.get("/{student_id}", response_model=schemas.MatchResult)
def match_internships_for_student(
    student_id: int,
    top_k: int = Query(3, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Return the top internships for a given student."""
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    jobs = db.query(models.Internship).all()
    if not jobs:
        return schemas.MatchResult(
            student_id=student.id,
            student_name=student.full_name,
            best_match=None,
            top_matches=[]
        )

    scored = [{"score": _score(student, j), "internship": j} for j in jobs]
    scored = [x for x in scored if x["score"] > 0]
    scored.sort(key=lambda x: x["score"], reverse=True)

    top = scored[:top_k]
    best = top[0]["internship"] if top else None

    return schemas.MatchResult(
        student_id=student.id,
        student_name=student.full_name,
        best_match=best,
        top_matches=[{"score": t["score"], "internship": t["internship"]} for t in top],
    )
