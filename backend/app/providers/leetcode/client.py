"""
LeetCode HTTP/GraphQL client.
Handles: requests, retries, timeouts, upstream error handling.
The interface (method signatures) must remain stable even if the
implementation changes when LeetCode updates its API.
"""
from __future__ import annotations
import asyncio
import logging
import threading
from typing import Any

import httpx

from app.config import settings
from app.providers.leetcode import queries as q
from app.providers.leetcode.parser import (
    LCProfile, LCSolvedStats, LCProblem, LCRecentSubmission, LCFullUserData,
    parse_profile, parse_solved_stats, parse_recent_submissions, parse_problem_list,
    parse_full_user_data, parse_question_data, parse_all_recent_submissions,
)

logger = logging.getLogger(__name__)

_HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
}

_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
_MAX_RETRIES = 3
_RETRY_BACKOFF = 1.5  # seconds

# Concurrency limiter: at most 3 concurrent outbound HTTP requests to LeetCode
_OUTBOUND_SEMAPHORE = threading.Semaphore(3)


async def _post_with_semaphore(client: httpx.AsyncClient, payload: dict[str, Any]) -> dict:
    """Acquires a concurrency token, executes the HTTP request, and releases the token."""
    await asyncio.to_thread(_OUTBOUND_SEMAPHORE.acquire)
    try:
        resp = await client.post(
            settings.LEETCODE_GRAPHQL_URL,
            json=payload,
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    finally:
        _OUTBOUND_SEMAPHORE.release()


async def _graphql(
    client: httpx.AsyncClient, payload: dict[str, Any], attempt: int = 0
) -> dict:
    try:
        return await _post_with_semaphore(client, payload)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (429, 503) and attempt < _MAX_RETRIES:
            wait = _RETRY_BACKOFF * (2 ** attempt)
            logger.warning(
                "LeetCode rate limited (%d). Retrying in %.1fs (attempt %d/%d)",
                e.response.status_code, wait, attempt + 1, _MAX_RETRIES
            )
            await asyncio.sleep(wait)
            return await _graphql(client, payload, attempt + 1)
        raise
    except httpx.TransportError as e:
        if attempt < _MAX_RETRIES:
            wait = _RETRY_BACKOFF * (2 ** attempt)
            logger.warning("LeetCode transport error: %s. Retrying in %.1fs", e, wait)
            await asyncio.sleep(wait)
            return await _graphql(client, payload, attempt + 1)
        raise


class LeetCodeProvider:
    """Stable interface for all LeetCode data fetches."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "LeetCodeProvider":
        self._client = httpx.AsyncClient()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()

    def _ensure_client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("LeetCodeProvider must be used as an async context manager")
        return self._client

    async def get_profile(self, username: str) -> LCProfile | None:
        """Fetch public profile for a username. Returns None if user not found."""
        data = await _graphql(
            self._ensure_client(),
            {"query": q.USER_PROFILE_QUERY, "variables": {"username": username}},
        )
        return parse_profile(data)

    async def get_full_user_data(self, username: str) -> LCFullUserData | None:
        """Fetch complete public user profile, including submitStats, tagProblemCounts, streak, beats%."""
        data = await _graphql(
            self._ensure_client(),
            {"query": q.USER_FULL_DATA_QUERY, "variables": {"username": username}},
        )
        return parse_full_user_data(data)

    async def get_question_data(self, title_slug: str) -> LCProblem | None:
        """Fetch problem details (difficulty, frontend id, topic tags) by titleSlug."""
        data = await _graphql(
            self._ensure_client(),
            {"query": q.PROBLEM_DETAIL_QUERY, "variables": {"titleSlug": title_slug}},
        )
        return parse_question_data(data)

    async def get_solved_stats(self, username: str) -> LCSolvedStats | None:
        """Fetch total easy/medium/hard solved counts."""
        data = await _graphql(
            self._ensure_client(),
            {"query": q.USER_SOLVED_QUERY, "variables": {"username": username}},
        )
        return parse_solved_stats(data)

    async def get_recent_ac_submissions(
        self, username: str, limit: int = 20
    ) -> list[LCRecentSubmission]:
        """Fetch recent accepted submissions (up to limit, max ~20 from public API)."""
        data = await _graphql(
            self._ensure_client(),
            {
                "query": q.USER_RECENT_AC_QUERY,
                "variables": {"username": username, "limit": limit},
            },
        )
        return parse_recent_submissions(data)

    async def get_recent_submissions(
        self, username: str, limit: int = 20
    ) -> list[LCRecentSubmission]:
        """Fetch general recent submissions, returning only accepted ones."""
        data = await _graphql(
            self._ensure_client(),
            {
                "query": q.USER_ALL_RECENT_SUBMISSIONS_QUERY,
                "variables": {"username": username, "limit": limit},
            },
        )
        return parse_all_recent_submissions(data)

    async def get_problem_page(self, skip: int = 0, limit: int = 50) -> tuple[int, list[LCProblem]]:
        """Fetch a page of problems from the public problem list."""
        data = await _graphql(
            self._ensure_client(),
            {
                "query": q.ALL_PROBLEMS_QUERY,
                "variables": {"skip": skip, "limit": limit},
            },
        )
        return parse_problem_list(data)

    async def get_all_problems(
        self, page_size: int = 100, max_problems: int = 3000
    ) -> list[LCProblem]:
        """Fetch all public problems (paginated)."""
        all_problems: list[LCProblem] = []
        skip = 0
        total, first_page = await self.get_problem_page(skip=0, limit=page_size)
        all_problems.extend(first_page)
        skip += len(first_page)

        while skip < total and skip < max_problems:
            _, page = await self.get_problem_page(skip=skip, limit=page_size)
            if not page:
                break
            all_problems.extend(page)
            skip += len(page)
            await asyncio.sleep(0.5)  # gentle rate limiting

        logger.info("Fetched %d problems from LeetCode (total=%d)", len(all_problems), total)
        return all_problems
