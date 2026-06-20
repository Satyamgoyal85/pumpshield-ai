"""Create tables on startup for SQLite dev; use Alembic for PostgreSQL production."""

from app.database import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
