"""
Database session management — 08 §11.
SQLAlchemy engine and session factory. Background jobs get their own sessions.
"""

from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import Base

# Module-level engine and factory, initialized by init_db()
_engine = None
_SessionFactory: sessionmaker[Session] | None = None


def init_db(database_url: str, data_dir: str = "./data") -> None:
    """Initialize the database engine and create all tables.

    Args:
        database_url: SQLAlchemy database URL.
        data_dir: Base data directory (for creating parent dirs).
    """
    global _engine, _SessionFactory

    # Ensure data directory exists
    Path(data_dir).mkdir(parents=True, exist_ok=True)

    connect_args = {}
    if database_url.startswith("sqlite"):
        # SQLite needs check_same_thread=False for FastAPI (08 §11)
        connect_args["check_same_thread"] = False

        # Ensure the SQLite file directory exists
        db_path = database_url.replace("sqlite:///", "")
        if db_path.startswith("./"):
            db_path = db_path[2:]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    _engine = create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        echo=False,
    )

    # Enable WAL mode for SQLite (better concurrent reads)
    if database_url.startswith("sqlite"):
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    _SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False)

    # Create all tables
    Base.metadata.create_all(bind=_engine)


def get_session() -> Session:
    """Get a new database session.

    Used by FastAPI dependency injection and background jobs.
    Background jobs must get their own session (08 §11).

    Returns:
        A new SQLAlchemy Session.

    Raises:
        RuntimeError: If init_db() has not been called.
    """
    if _SessionFactory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionFactory()


def get_db():
    """FastAPI dependency that yields a DB session and closes it after the request.

    Yields:
        SQLAlchemy Session.
    """
    db = get_session()
    try:
        yield db
    finally:
        db.close()
