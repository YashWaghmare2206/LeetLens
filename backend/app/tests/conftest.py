"""
Test configuration and shared fixtures.
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app

import socket

@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    import socket
    original_connect = socket.socket.connect
    def _blocked_connect(self, address):
        if hasattr(address, "__len__") and address[0] in ("127.0.0.1", "::1", "localhost"):
            return original_connect(self, address)
        raise RuntimeError(f"Network access blocked during tests (tried to connect to {address})")
    monkeypatch.setattr(socket.socket, "connect", _blocked_connect)

@pytest.fixture(autouse=True)
def mock_leetcode_provider(monkeypatch):
    """Prevent hitting live LeetCode API in tests."""
    from app.providers.leetcode.client import LeetCodeProvider
    async def _mock_none(self, *args, **kwargs):
        return None
    async def _mock_empty_list(self, *args, **kwargs):
        return []

    monkeypatch.setattr(LeetCodeProvider, "get_profile", _mock_none)
    monkeypatch.setattr(LeetCodeProvider, "get_full_user_data", _mock_none)
    monkeypatch.setattr(LeetCodeProvider, "get_question_data", _mock_none)
    monkeypatch.setattr(LeetCodeProvider, "get_solved_stats", _mock_none)
    monkeypatch.setattr(LeetCodeProvider, "get_recent_ac_submissions", _mock_empty_list)
    monkeypatch.setattr(LeetCodeProvider, "get_recent_submissions", _mock_empty_list)
    monkeypatch.setattr(LeetCodeProvider, "get_all_problems", _mock_empty_list)
    monkeypatch.setattr(LeetCodeProvider, "get_problem_page", _mock_none)

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

