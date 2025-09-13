from __future__ import annotations

from typing import Annotated, Optional, Iterable

from sqlalchemy import (
    String, Integer, Float, Text, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# --- Type aliases to make intent obvious -------------------------------------
PKInt      = Annotated[int, mapped_column(Integer, primary_key=True, index=True)]
NameStr    = Annotated[str, mapped_column("Full_Name", String(150), index=True, nullable=False)]
EmailStr   = Annotated[str, mapped_column("Email", String(200), nullable=False, unique=True)]
SecretStr  = Annotated[str, mapped_column("Password", String(200), nullable=False)]
CollegeStr = Annotated[str, mapped_column("College", String(200), nullable=False, default="")]
LocStr     = Annotated[str, mapped_column("Location", String(120), nullable=False, default="")]
SkillsStr  = Annotated[str, mapped_column("Skills", String(800),  nullable=False, default="")]
QualStr    = Annotated[str, mapped_column("Qualification", String(120), nullable=False, default="")]
BioText    = Annotated[Optional[str], mapped_column("Bio", Text, nullable=True, default=None)]
CGPAFloat  = Annotated[float, mapped_column("CGPA", Float, nullable=False)]


class Student(Base):
    """
    A single learner profile in the system.
    Column names are kept TitleCase to match an existing DB (e.g., CSV import).
    """

    __tablename__ = "students"

    id: Mapped[PKInt]
    full_name: Mapped[NameStr]
    email: Mapped[EmailStr]
    password: Mapped[SecretStr]

    college: Mapped[CollegeStr]
    cgpa: Mapped[CGPAFloat]

    location: Mapped[LocStr]
    skills: Mapped[SkillsStr]

    qualification: Mapped[QualStr]
    bio: Mapped[BioText]

    __table_args__ = (
        # CGPA should be in a 0–10 scale (inclusive)
        CheckConstraint("CGPA >= 0 AND CGPA <= 10", name="ck_students_cgpa_range"),
        # Handy search pattern: where is this student and what level are they?
        Index("ix_students_location_qualification", "Location", "Qualification"),
    )

    # --- Convenience helpers (pure Python, not required by SQLAlchemy) -------

    def skill_list(self) -> list[str]:
        """Return the skills column as a clean Python list."""
        return [s.strip() for s in (self.skills or "").split(",") if s.strip()]

    def set_skills(self, items: Iterable[str]) -> None:
        """Update skills from any iterable; normalizes and deduplicates."""
        # Normalize & deduplicate while preserving order
        seen = set()
        cleaned = []
        for raw in items:
            s = (raw or "").strip()
            if s and s.lower() not in seen:
                seen.add(s.lower())
                cleaned.append(s)
        self.skills = ", ".join(cleaned)

    def __repr__(self) -> str:  # human-friendly and debug-friendly
        return f"<Student #{self.id} {self.full_name!r} cgpa={self.cgpa}>"

    def __str__(self) -> str:
        return f"{self.full_name} ({self.email})"
