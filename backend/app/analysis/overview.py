"""
Analysis Engine — Overview
Computes total solved / easy / medium / hard counts.
Each problem counted exactly once (not summed across patterns).
Uses real LeetCode stats from user profile when available.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from app.schemas.enums import Difficulty
from app.schemas.stateless import StatelessSolved

if TYPE_CHECKING:
    from app.schemas.stateless import StatelessUser


def compute_overview(
    username: str,
    solved: list[StatelessSolved],
    user: StatelessUser | None = None,
    ranking: int | None = None,
    real_name: str | None = None,
    avatar_url: str | None = None,
) -> dict:
    import json

    badges = []
    upcoming_badges = []
    languages = []
    submission_cal = None
    acceptance_rate = None
    reputation = None
    total_submissions = 0

    if user and user.total_solved > 0:
        total = user.total_solved
        easy = user.easy_solved
        medium = user.medium_solved
        hard = user.hard_solved
        ranking = user.ranking
        real_name = user.real_name
        avatar_url = user.avatar_url
        streak = user.streak
        active_days = user.total_active_days
        beats_easy = user.beats_easy
        beats_medium = user.beats_medium
        beats_hard = user.beats_hard
        total_submissions = user.total_submissions or 0
        acceptance_rate = user.acceptance_rate
        reputation = user.reputation

        if user.badges_json:
            try:
                badges = json.loads(user.badges_json)
            except Exception:
                badges = []
        if user.upcoming_badges_json:
            try:
                upcoming_badges = json.loads(user.upcoming_badges_json)
            except Exception:
                upcoming_badges = []
        if user.languages_json:
            try:
                languages = json.loads(user.languages_json)
            except Exception:
                languages = []
        if user.submission_calendar_json:
            try:
                submission_cal = json.loads(user.submission_calendar_json)
            except Exception:
                submission_cal = None
    else:
        total = len(solved)
        easy = sum(1 for s in solved if s.problem.difficulty == Difficulty.EASY)
        medium = sum(1 for s in solved if s.problem.difficulty == Difficulty.MEDIUM)
        hard = sum(1 for s in solved if s.problem.difficulty == Difficulty.HARD)
        streak = None
        active_days = None
        beats_easy = None
        beats_medium = None
        beats_hard = None

    return {
        "username": username,
        "total_solved": total,
        "easy": easy,
        "medium": medium,
        "hard": hard,
        "total_submissions": total_submissions,
        "acceptance_rate": acceptance_rate,
        "ranking": ranking,
        "real_name": real_name,
        "avatar_url": avatar_url,
        "reputation": reputation,
        "streak": streak,
        "total_active_days": active_days,
        "beats_easy": beats_easy,
        "beats_medium": beats_medium,
        "beats_hard": beats_hard,
        "recent_solved_count": len(solved),
        "badges": badges,
        "upcoming_badges": upcoming_badges,
        "languages": languages,
        "submission_calendar": submission_cal,
    }
