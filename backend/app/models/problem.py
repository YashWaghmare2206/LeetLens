"""Problem, Topic, Pattern, and junction models."""
import enum
from sqlalchemy import (
    String, Text, Boolean, Integer, Float, ForeignKey,
    DateTime, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class Difficulty(str, enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    UNKNOWN = "Unknown"


class ClassificationSource(str, enum.Enum):
    CURATED = "curated"
    LEETCODE = "leetcode"
    AI = "ai"
    MANUAL = "manual"


class ClassificationStatus(str, enum.Enum):
    CLASSIFIED = "classified"
    UNCLASSIFIED = "unclassified"
    PENDING = "pending"


# Problem

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    leetcode_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(
        SAEnum(Difficulty, native_enum=False), default=Difficulty.UNKNOWN
    )
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    paid_only: Mapped[bool] = mapped_column(Boolean, default=False)
    classification_status: Mapped[ClassificationStatus] = mapped_column(
        SAEnum(ClassificationStatus, native_enum=False), default=ClassificationStatus.UNCLASSIFIED
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    topics: Mapped[list["ProblemTopic"]] = relationship(
        "ProblemTopic", back_populates="problem", cascade="all, delete-orphan"
    )
    patterns: Mapped[list["ProblemPattern"]] = relationship(
        "ProblemPattern", back_populates="problem", cascade="all, delete-orphan"
    )
    solved_by: Mapped[list["UserSolvedProblem"]] = relationship(  # noqa: F821
        "UserSolvedProblem", back_populates="problem"
    )

    def __repr__(self) -> str:
        return f"<Problem #{self.leetcode_id} {self.title!r}>"


# Topic

class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), nullable=True)
    topic_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    problems: Mapped[list["ProblemTopic"]] = relationship(
        "ProblemTopic", back_populates="topic", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Topic {self.name!r}>"


# Pattern

class Pattern(Base):
    __tablename__ = "patterns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("patterns.id"), nullable=True)

    problems: Mapped[list["ProblemPattern"]] = relationship(
        "ProblemPattern", back_populates="pattern", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Pattern {self.name!r}>"


# Junction: Problem ↔ Topic

class ProblemTopic(Base):
    __tablename__ = "problem_topics"
    __table_args__ = (UniqueConstraint("problem_id", "topic_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[ClassificationSource] = mapped_column(
        SAEnum(ClassificationSource, native_enum=False), default=ClassificationSource.LEETCODE
    )

    problem: Mapped["Problem"] = relationship("Problem", back_populates="topics")
    topic: Mapped["Topic"] = relationship("Topic", back_populates="problems")


# Junction: Problem ↔ Pattern

class ProblemPattern(Base):
    __tablename__ = "problem_patterns"
    __table_args__ = (UniqueConstraint("problem_id", "pattern_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False)
    pattern_id: Mapped[int] = mapped_column(ForeignKey("patterns.id"), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[ClassificationSource] = mapped_column(
        SAEnum(ClassificationSource, native_enum=False), default=ClassificationSource.CURATED
    )

    problem: Mapped["Problem"] = relationship("Problem", back_populates="patterns")
    pattern: Mapped["Pattern"] = relationship("Pattern", back_populates="problems")


# UserSolvedProblem

class UserSolvedProblem(Base):
    __tablename__ = "user_solved_problems"
    __table_args__ = (UniqueConstraint("user_id", "problem_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False)
    first_solved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_solved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=1)

    user: Mapped["User"] = relationship("User", back_populates="solved_problems")  # noqa: F821
    problem: Mapped["Problem"] = relationship("Problem", back_populates="solved_by")
