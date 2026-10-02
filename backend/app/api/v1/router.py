"""
Users & Analytics API router — /api/v1 (100% Stateless & In-Memory).
Zero database queries or persistence.
"""
from __future__ import annotations
import logging
import re
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.stateless_service import StatelessService
from app.schemas.analytics import (
    OverviewResponse, TopicsResponse, PatternsResponse,
    CoverageResponse, ProblemsResponse,
)
from app.schemas.user import UserResponse
from pydantic import BaseModel, Field, constr
from typing import Optional

class EnrichProblem(BaseModel):
    leetcode_id: int
    title: Optional[str] = None
    slug: constr(pattern=r"^[a-z0-9-]+$")
    difficulty: str
    url: Optional[str] = None
    solved_at: Optional[str] = None
    topics: Optional[list[str]] = None

class EnrichRequest(BaseModel):
    history: list[EnrichProblem] = Field(max_length=500)

logger = logging.getLogger(__name__)

router = APIRouter()


def _normalize_username(username_or_url: str) -> str:
    """Extract username from a profile URL or return as-is."""
    s = username_or_url.strip().rstrip("/")
    # e.g. https://leetcode.com/u/username/ or https://leetcode.com/username/
    match = re.search(r"leetcode\.com/(?:u/)?([^/?#]+)", s)
    if match:
        return match.group(1)
    return s



@router.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str):
    username = _normalize_username(username)
    user = await StatelessService.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return user




@router.post("/users/{username}/enrich")
async def enrich_history(username: str, req: EnrichRequest):
    username = _normalize_username(username)
    history_dicts = [p.model_dump() for p in req.history]
    result = await StatelessService.get_or_fetch(username, force=True, history_dicts=history_dicts)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return {"status": "ok", "problems": result.get("problems", {}).get("problems", [])}


@router.get("/users/{username}/overview", response_model=OverviewResponse)
async def get_overview(username: str):
    username = _normalize_username(username)
    result = await StatelessService.get_overview(username)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/topics", response_model=TopicsResponse)
async def get_topics(username: str):
    username = _normalize_username(username)
    result = await StatelessService.get_topics(username)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/patterns", response_model=PatternsResponse)
async def get_patterns(username: str):
    username = _normalize_username(username)
    result = await StatelessService.get_patterns(username)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/patterns/{pattern_slug}")
async def get_pattern_detail(username: str, pattern_slug: str):
    username = _normalize_username(username)
    result = await StatelessService.get_pattern_detail(username, pattern_slug)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Pattern '{pattern_slug}' not found for user '{username}'",
        )
    return result


@router.get("/users/{username}/gaps", response_model=CoverageResponse)
@router.get("/users/{username}/coverage", response_model=CoverageResponse)
async def get_coverage(username: str):
    username = _normalize_username(username)
    result = await StatelessService.get_coverage(username)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/taxonomy-explorer")
async def get_taxonomy_explorer(username: str):
    username = _normalize_username(username)
    result = await StatelessService.get_taxonomy_explorer(username)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/student-analysis")
async def get_student_analysis(username: str):
    username = _normalize_username(username)
    result = await StatelessService.get_student_analysis(username)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/activity-timeline")
async def get_activity_timeline(username: str):
    username = _normalize_username(username)
    result = await StatelessService.get_activity_timeline(username)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/pattern-practice")
async def get_pattern_practice(username: str):
    username = _normalize_username(username)
    result = await StatelessService.get_pattern_practice(username)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/problems", response_model=ProblemsResponse)
async def get_problems(
    username: str,
    difficulty: str | None = Query(None, description="Filter: Easy | Medium | Hard"),
):
    username = _normalize_username(username)
    result = await StatelessService.get_problems(username, difficulty=difficulty)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result



