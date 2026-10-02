"""
Test configuration and shared fixtures.
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app

@pytest.fixture(autouse=True)
def mock_leetcode_provider(monkeypatch):
    """Prevent hitting live LeetCode API in tests."""
    from app.providers.leetcode.client import LeetCodeProvider
    async def _mock_profile(self, username):
        return None
    monkeypatch.setattr(LeetCodeProvider, "get_profile", _mock_profile)
    async def _mock_full(self, username):
        return None
    monkeypatch.setattr(LeetCodeProvider, "get_full_user_data", _mock_full)

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

