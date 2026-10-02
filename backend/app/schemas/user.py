"""Pydantic response schemas for users."""
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    username: str
    leetcode_url: str | None = None
    real_name: str | None = None
    avatar_url: str | None = None
    ranking: int | None = None
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    total_submissions: int = 0
    acceptance_rate: float | None = None
    reputation: int | None = None
    streak: int | None = None
    total_active_days: int | None = None
    beats_easy: float | None = None
    beats_medium: float | None = None
    beats_hard: float | None = None
    badges_json: str | None = None
    upcoming_badges_json: str | None = None
    languages_json: str | None = None
    submission_calendar_json: str | None = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
