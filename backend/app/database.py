"""
Async SQLAlchemy database setup (SQLite via aiosqlite for local dev,
trivially swappable to PostgreSQL+asyncpg for production).
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency: yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables on startup and apply lightweight migrations for SQLite."""
    async with engine.begin() as conn:
        from app.models import user, problem, sync_job  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

        # Ensure SQLite has newly added columns
        if "sqlite" in settings.DATABASE_URL:
            from sqlalchemy import text
            columns_to_check = [
                ("users", "badges_json", "TEXT"),
                ("users", "upcoming_badges_json", "TEXT"),
                ("users", "languages_json", "TEXT"),
                ("users", "submission_calendar_json", "TEXT"),
                ("users", "acceptance_rate", "REAL"),
                ("users", "reputation", "INTEGER"),
                ("users", "streak", "INTEGER"),
                ("users", "total_active_days", "INTEGER"),
                ("users", "beats_easy", "REAL"),
                ("users", "beats_medium", "REAL"),
                ("users", "beats_hard", "REAL"),
                ("users", "skill_stats_json", "TEXT"),
                ("users", "total_solved", "INTEGER DEFAULT 0"),
                ("users", "easy_solved", "INTEGER DEFAULT 0"),
                ("users", "medium_solved", "INTEGER DEFAULT 0"),
                ("users", "hard_solved", "INTEGER DEFAULT 0"),
                ("users", "total_submissions", "INTEGER DEFAULT 0"),
            ]
            for table, col, col_type in columns_to_check:
                try:
                    await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                except Exception:
                    # Column already exists
                    pass
