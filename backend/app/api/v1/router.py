"""
Users & Analytics API router — /api/v1 (100% Stateless & In-Memory).
Zero database queries or persistence.
"""
from __future__ import annotations
import logging
import re
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.services.stateless_service import StatelessService
from app.schemas.analytics import (
    OverviewResponse, TopicsResponse, PatternsResponse,
    CoverageResponse, ProblemsResponse,
)
from app.schemas.user import UserResponse
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from pydantic.types import StringConstraints

class EnrichProblem(BaseModel):
    leetcode_id: int
    title: Optional[str] = None
    slug: Annotated[str, StringConstraints(pattern=r"^[a-z0-9-]+$")]
    difficulty: str
    url: Optional[str] = None
    solved_at: Optional[str] = None
    topics: Optional[list[str]] = None

class EnrichRequest(BaseModel):
    history: list[EnrichProblem] = Field(max_length=500)

_ENRICH_IP_RATE_LIMIT = {}


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
async def get_user(username: str, history_key: str | None = None):
    username = _normalize_username(username)
    user = await StatelessService.get_user(username, history_key=history_key)
    if not user:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return user




@router.post("/users/{username}/enrich")
async def enrich_history(username: str, req: EnrichRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    import time
    now = time.time()
    if client_ip in _ENRICH_IP_RATE_LIMIT and now - _ENRICH_IP_RATE_LIMIT[client_ip] < 2:
        raise HTTPException(status_code=429, detail="Too many enrich requests")
    _ENRICH_IP_RATE_LIMIT[client_ip] = now
    
    username = _normalize_username(username)
    history_dicts = [p.model_dump() for p in req.history]
    result = await StatelessService.get_or_fetch(username, force=True, history_dicts=history_dicts)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return {"status": "ok", "history_key": result.get("history_key"), "problems": result.get("problems", {}).get("problems", [])}



@router.get("/users/{username}/overview", response_model=OverviewResponse)
async def get_overview(username: str, history_key: str | None = None):
    username = _normalize_username(username)
    result = await StatelessService.get_overview(username, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/topics", response_model=TopicsResponse)
async def get_topics(username: str, history_key: str | None = None):
    username = _normalize_username(username)
    result = await StatelessService.get_topics(username, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/patterns", response_model=PatternsResponse)
async def get_patterns(username: str, history_key: str | None = None):
    username = _normalize_username(username)
    result = await StatelessService.get_patterns(username, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/patterns/{pattern_slug}")
async def get_pattern_detail(username: str, pattern_slug: str, history_key: str | None = None):
    username = _normalize_username(username)
    result = await StatelessService.get_pattern_detail(username, pattern_slug, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(
            status_code=404,
            detail=f"Pattern '{pattern_slug}' not found for user '{username}'",
        )
    return result


@router.get("/users/{username}/gaps", response_model=CoverageResponse)
@router.get("/users/{username}/coverage", response_model=CoverageResponse)
async def get_coverage(username: str, history_key: str | None = None):
    username = _normalize_username(username)
    result = await StatelessService.get_coverage(username, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/taxonomy-explorer")
async def get_taxonomy_explorer(username: str, history_key: str | None = None):
    username = _normalize_username(username)
    result = await StatelessService.get_taxonomy_explorer(username, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/student-analysis")
async def get_student_analysis(username: str, history_key: str | None = None):
    username = _normalize_username(username)
    result = await StatelessService.get_student_analysis(username, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/activity-timeline")
async def get_activity_timeline(username: str, history_key: str | None = None):
    username = _normalize_username(username)
    result = await StatelessService.get_activity_timeline(username, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/pattern-practice")
async def get_pattern_practice(username: str, history_key: str | None = None):
    username = _normalize_username(username)
    result = await StatelessService.get_pattern_practice(username, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result


@router.get("/users/{username}/problems", response_model=ProblemsResponse)
async def get_problems(
    username: str,
    difficulty: str | None = Query(None, description="Filter: Easy | Medium | Hard"),
    history_key: str | None = None
):
    username = _normalize_username(username)
    result = await StatelessService.get_problems(username, difficulty=difficulty, history_key=history_key)
    if result is None:
        if history_key: raise HTTPException(status_code=409, detail="history_expired")
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    return result



