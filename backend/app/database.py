from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import sessionmaker, registry

# --- Database target ---------------------------------------------------------
# You can override this with the env var APP_DATABASE_URL when deploying.
DB_FILE = Path("app.db")
DATABASE_URL = os.getenv("APP_DATABASE_URL", f"sqlite:///{DB_FILE.as_posix()}")

# --- Engine ------------------------------------------------------------------
# SQLite needs a special flag for multi-threaded apps; other backends don't.
is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,  # flip to True if you want to see SQL logs while debugging
    connect_args={"check_same_thread": False} if is_sqlite else {},
)

# --- Session factory ----------------------------------------------------------
# expire_on_commit=False keeps loaded attributes available after commit.
SessionFactory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# --- Declarative base ---------------------------------------------------------
# Using the registry() path makes this feel less like cookie-cutter code.
_mapper_registry = registry()
Base = _mapper_registry.generate_base()

# --- Session provider (FastAPI-friendly) -------------------------------------
def get_session() -> Iterator[OrmSession]:
    """
    Yields a database session for request-scoped work and guarantees cleanup.
    Usage (FastAPI):
        @app.get("/items")
        def route(db: OrmSession = Depends(get_session)): ...
    """
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()

__all__ = ["engine", "SessionFactory", "Base", "get_session"]
