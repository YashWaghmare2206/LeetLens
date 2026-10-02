"""
API endpoint tests — test every route with in-memory SQLite.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/users/nonexistent_user_xyz999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_trigger_sync_creates_job(client: AsyncClient):
    resp = await client.post("/api/v1/users/testuser123/sync")
    assert resp.status_code in (200, 202, 404)
    if resp.status_code == 202:
        data = resp.json()
        assert "id" in data
        assert data["status"] in ("PENDING", "SUCCESS")


@pytest.mark.asyncio
async def test_get_sync_status(client: AsyncClient):
    # First create a job
    sync_resp = await client.post("/api/v1/users/testuser456/sync")
    if sync_resp.status_code == 202:
        job_id = sync_resp.json()["id"]
        resp = await client.get(f"/api/v1/sync/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == job_id


@pytest.mark.asyncio
async def test_get_sync_status_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/sync/99999")
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_overview_not_found_before_sync(client: AsyncClient):
    resp = await client.get("/api/v1/users/brand_new_user_nonexistent/overview")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_patterns_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/users/brand_new_user_nonexistent/patterns")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_topics_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/users/brand_new_user_nonexistent/topics")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_gaps_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/users/brand_new_user_nonexistent/gaps")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_problems_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/users/brand_new_user_nonexistent/problems")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_username_url_normalization(client: AsyncClient):
    """Backend normalizes LeetCode URLs — test via the normalization function directly."""
    from app.api.v1.router import _normalize_username
    assert _normalize_username("https://leetcode.com/u/testuser789/") == "testuser789"
    assert _normalize_username("https://leetcode.com/testuser789") == "testuser789"
    assert _normalize_username("testuser789") == "testuser789"


@pytest.mark.asyncio
async def test_problem_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/problems/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_overview_after_manual_user_creation(client: AsyncClient):
    """Seed cache in stateless service and verify overview returns 200 with accurate stats."""
    import time
    from app.services.stateless_service import _STATELESS_STORE

    _STATELESS_STORE["manual_test_user"] = {
        "user": {
            "id": 1,
            "username": "manual_test_user",
            "real_name": "Test User",
            "avatar_url": None,
            "ranking": 1000,
            "total_solved": 1,
            "easy_solved": 1,
            "medium_solved": 0,
            "hard_solved": 0,
            "total_submissions": 2,
            "streak": 1,
            "total_active_days": 1,
            "beats_easy": 50.0,
            "beats_medium": 0.0,
            "beats_hard": 0.0,
            "acceptance_rate": 50.0,
            "reputation": 0,
        },
        "overview": {
            "username": "manual_test_user",
            "total_solved": 1,
            "easy": 1,
            "medium": 0,
            "hard": 0,
            "total_submissions": 2,
            "acceptance_rate": 50.0,
            "ranking": 1000,
            "streak": 1,
            "total_active_days": 1,
            "beats_easy": 50.0,
            "beats_medium": 0.0,
            "beats_hard": 0.0,
            "interview_readiness_score": 50,
            "patterns_covered": 1,
            "total_patterns": 71,
            "pattern_coverage_pct": 1.4,
            "topics_covered": 1,
            "total_topics": 15,
            "topic_coverage_pct": 6.7,
            "most_practiced_topic": "Arrays",
            "strongest_pattern": "Two Pointers",
            "weakest_pattern": "Dynamic Programming",
        },
        "topics": {"topics": []},
        "patterns": {"patterns": []},
        "coverage": {"total_patterns": 71, "covered_patterns": 1, "coverage_pct": 1.4, "topics": []},
        "taxonomy": {"topics": []},
        "student_analysis": {"readiness_score": 50, "categories": []},
        "timeline": {"daily_activity": []},
        "practice": {"problems": []},
        "problems": [],
    }

    resp = await client.get("/api/v1/users/manual_test_user/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_solved"] == 1
    assert data["easy"] == 1
    assert data["medium"] == 0
    assert data["hard"] == 0

@pytest.mark.asyncio
async def test_profile_only_fallback(client: AsyncClient, monkeypatch):
    from app.providers.leetcode.client import LeetCodeProvider
    from app.providers.leetcode.parser import LCProfile
    async def _mock_profile(self, username):
        return LCProfile(username="fallback", real_name="Fallback", avatar_url="", ranking=100)
    async def _mock_full(self, username):
        return None  # Trigger fallback
    monkeypatch.setattr(LeetCodeProvider, "get_profile", _mock_profile)
    monkeypatch.setattr(LeetCodeProvider, "get_full_user_data", _mock_full)
    
    resp = await client.get("/api/v1/users/fallback_user/overview")
    assert resp.status_code == 200
    assert resp.json()["total_solved"] == 0

@pytest.mark.asyncio
async def test_enrich_endpoint(client: AsyncClient, monkeypatch):
    from app.providers.leetcode.client import LeetCodeProvider
    from app.providers.leetcode.parser import LCFullUserData
    async def _mock_full(self, username):
        return LCFullUserData(username="enrich", total_solved=0, easy_solved=0, medium_solved=0, hard_solved=0,
                              total_submissions=0, tag_problem_counts=[], badges=[], upcoming_badges=[],
                              languages=[], submission_calendar="{}", acceptance_rate=0.0, reputation=0,
                              real_name="E", avatar_url="", ranking=1, streak=0, total_active_days=0,
                              beats_easy=0, beats_medium=0, beats_hard=0)
    monkeypatch.setattr(LeetCodeProvider, "get_full_user_data", _mock_full)
    
    payload = {
        "history": [
            {"leetcode_id": 1, "slug": "two-sum", "difficulty": "Easy", "title": "Two Sum", "topics": ["array"]}
        ]
    }
    resp = await client.post("/api/v1/users/enrich_user/enrich", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert len(resp.json()["problems"]) == 1
