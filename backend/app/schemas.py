from __future__ import annotations
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field as PydField


# =========================
# Students (Sign Up fields)
# =========================
class StudentBase(BaseModel):
    full_name: str = PydField(min_length=1, max_length=150)
    email: EmailStr
    password: str = PydField(min_length=6, max_length=200)  # NOTE: store hashed in production
    college: str = PydField(min_length=0, max_length=200)
    cgpa: float = PydField(ge=0, le=10)
    location: str = PydField(min_length=0, max_length=120)
    skills: str = PydField(min_length=0, max_length=800)  # comma-separated
    qualification: str = PydField(min_length=0, max_length=120)
    bio: Optional[str] = None


class StudentCreate(StudentBase):
    """Payload for creating a student (includes password)."""
    pass


class StudentRead(BaseModel):
    """What we send back to clients (no password)."""
    id: int
    full_name: str
    email: EmailStr
    college: str
    cgpa: float
    location: str
    skills: str
    qualification: str
    bio: Optional[str] = None

    class Config:
        from_attributes = True  # ORM mode (Pydantic v2)


# =========================
# Internships
# =========================
class InternshipBase(BaseModel):
    company_name: str = PydField(min_length=1, max_length=200)
    suggested_role: str = PydField(min_length=1, max_length=160)
    location: str = PydField(min_length=0, max_length=120)
    min_cgpa: float = PydField(ge=0, le=10)
    field: str = PydField(min_length=0, max_length=120)
    program: str = PydField(min_length=0, max_length=120)


class InternshipCreate(InternshipBase):
    pass


class InternshipRead(InternshipBase):
    id: int

    class Config:
        from_attributes = True


# =========================
# Matching result schemas
# =========================
class TopMatch(BaseModel):
    score: float
    internship: "InternshipRead"

    class Config:
        from_attributes = True


class MatchResult(BaseModel):
    student_id: int
    student_name: str
    best_match: Optional["InternshipRead"] = None
    top_matches: List[TopMatch]


# Resolve forward references (Pydantic v2)
TopMatch.model_rebuild()
MatchResult.model_rebuild()
