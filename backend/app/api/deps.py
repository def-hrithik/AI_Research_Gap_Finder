"""
API dependencies — 08 §2.
FastAPI dependency injection: DB sessions, settings, shared resources.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database.session import get_db


def get_settings_dep() -> Settings:
    """Return the cached settings singleton."""
    return get_settings()


# Type aliases for FastAPI Depends
SettingsDep = Annotated[Settings, Depends(get_settings_dep)]
DbDep = Annotated[Session, Depends(get_db)]
