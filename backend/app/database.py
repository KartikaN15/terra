"""
Database session management.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from .config import settings

_engine_kwargs = {}
if settings.database_url.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug,
    **_engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Enable pgvector if available
@event.listens_for(engine, "connect")
def setup_pgvector(dbapi_conn, connection_record):
    try:
        with dbapi_conn.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
    except Exception:
        pass  # pgvector not installed, that's okay for MVP


def get_db():
    """FastAPI dependency for DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
