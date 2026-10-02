"""Pydantic schemas for analysis engine responses."""
from pydantic import BaseModel
from app.models.problem import Difficulty


class DifficultyBreakdown(BaseModel):
    easy: int = 0
    medium: int = 0
    hard: int = 0


class OverviewResponse(BaseModel):
    username: str
    total_solved: int
    easy: int
    medium: int
    hard: int
    total_submissions: int = 0
    acceptance_rate: float | None = None
    ranking: int | None = None
    real_name: str | None = None
    avatar_url: str | None = None
    reputation: int | None = None
    streak: int | None = None
    total_active_days: int | None = None
    beats_easy: float | None = None
    beats_medium: float | None = None
    beats_hard: float | None = None
    recent_solved_count: int = 0
    badges: list[dict] = []
    upcoming_badges: list[dict] = []
    languages: list[dict] = []
    submission_calendar: dict[str, int] | None = None


class TopicStats(BaseModel):
    topic: str
    topic_slug: str
    solved_count: int
    easy: int
    medium: int
    hard: int


class TopicsResponse(BaseModel):
    username: str
    topics: list[TopicStats]


class ProblemInPattern(BaseModel):
    leetcode_id: int
    title: str
    slug: str
    difficulty: Difficulty
    url: str | None
    solved_at: str | None = None
    topics: list[str] = []


class PatternStats(BaseModel):
    pattern: str
    pattern_slug: str
    solved_count: int
    easy: int
    medium: int
    hard: int
    problems: list[ProblemInPattern] = []


class PatternsResponse(BaseModel):
    username: str
    patterns: list[PatternStats]


class CoverageItem(BaseModel):
    pattern: str
    pattern_slug: str
    parent: str | None
    solved_count: int
    practiced: bool


class CoverageResponse(BaseModel):
    username: str
    total_patterns: int
    practiced_count: int
    coverage_ratio: float
    items: list[CoverageItem]


class ProblemsResponse(BaseModel):
    username: str
    total: int
    total_confirmed: int = 0
    problems: list[ProblemInPattern]
