"""
User repository — database access for users.
All raw SQL/ORM queries for users live here.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_username(self, username: str) -> User | None:
        result = await self._db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, username: str, leetcode_url: str | None = None) -> User:
        user = User(username=username, leetcode_url=leetcode_url)
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def update(self, user: User, **kwargs) -> User:
        for k, v in kwargs.items():
            setattr(user, k, v)
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def get_or_create(self, username: str) -> tuple[User, bool]:
        """Returns (user, created)."""
        user = await self.get_by_username(username)
        if user:
            return user, False
        user = await self.create(username)
        return user, True
