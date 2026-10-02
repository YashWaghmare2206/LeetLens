"""User model."""
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    leetcode_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    real_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ranking: Mapped[int | None] = mapped_column(nullable=True)
    total_solved: Mapped[int] = mapped_column(default=0)
    easy_solved: Mapped[int] = mapped_column(default=0)
    medium_solved: Mapped[int] = mapped_column(default=0)
    hard_solved: Mapped[int] = mapped_column(default=0)
    total_submissions: Mapped[int] = mapped_column(default=0)
    streak: Mapped[int | None] = mapped_column(nullable=True)
    total_active_days: Mapped[int | None] = mapped_column(nullable=True)
    beats_easy: Mapped[float | None] = mapped_column(nullable=True)
    beats_medium: Mapped[float | None] = mapped_column(nullable=True)
    beats_hard: Mapped[float | None] = mapped_column(nullable=True)
    skill_stats_json: Mapped[str | None] = mapped_column(String(10000), nullable=True)
    badges_json: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    upcoming_badges_json: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    languages_json: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    submission_calendar_json: Mapped[str | None] = mapped_column(String(20000), nullable=True)
    acceptance_rate: Mapped[float | None] = mapped_column(nullable=True)
    reputation: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    solved_problems: Mapped[list["UserSolvedProblem"]] = relationship(  # noqa: F821
        "UserSolvedProblem", back_populates="user", cascade="all, delete-orphan"
    )
    sync_jobs: Mapped[list["SyncJob"]] = relationship(  # noqa: F821
        "SyncJob", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User username={self.username!r}>"
