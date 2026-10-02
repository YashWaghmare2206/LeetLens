from dataclasses import dataclass, field
from datetime import datetime
from app.schemas.enums import Difficulty

@dataclass
class StatelessTopic:
    id: int
    name: str
    slug: str


@dataclass
class StatelessProblemTopic:
    topic: StatelessTopic


@dataclass
class StatelessPattern:
    id: int
    name: str
    slug: str
    description: str = ""
    parent: str | None = None
    parent_id: int | None = None
    parent_topic: StatelessTopic | None = None


@dataclass
class StatelessProblemPattern:
    pattern: StatelessPattern
    confidence: float
    inferred: bool = False


@dataclass
class StatelessProblem:
    id: int
    leetcode_id: int
    title: str
    slug: str
    difficulty: Difficulty
    url: str | None = None
    is_paid_only: bool = False
    topics: list[StatelessProblemTopic] = field(default_factory=list)
    patterns: list[StatelessProblemPattern] = field(default_factory=list)


@dataclass
class StatelessSolved:
    problem: StatelessProblem
    last_solved_at: datetime | None


@dataclass
class StatelessUser:
    id: int
    username: str
    real_name: str | None = None
    avatar_url: str | None = None
    ranking: int | None = None
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    total_submissions: int = 0
    streak: int | None = None
    total_active_days: int | None = None
    beats_easy: float | None = None
    beats_medium: float | None = None
    beats_hard: float | None = None
    badges_json: str | None = None
    upcoming_badges_json: str | None = None
    languages_json: str | None = None
    submission_calendar_json: str | None = None
    skill_stats_json: str | None = None
    acceptance_rate: float | None = None
    reputation: int | None = None
