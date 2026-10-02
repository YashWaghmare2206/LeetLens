"""
Profile service — fetches user analytics from the database.
Computes overview, topics, patterns, coverage using the analysis engine.
"""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.repositories.problem_repo import ProblemRepository
from app.analysis.overview import compute_overview
from app.analysis.topics import compute_topics
from app.analysis.patterns import compute_patterns, compute_pattern_detail
from app.analysis.coverage import compute_coverage
from app.analysis.taxonomy_explorer import compute_taxonomy_explorer
from app.analysis.student_analysis import compute_student_analysis
from app.analysis.activity_timeline import compute_activity_timeline
from app.analysis.pattern_practice import compute_pattern_practice


class ProfileService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._user_repo = UserRepository(db)
        self._problem_repo = ProblemRepository(db)

    async def get_user(self, username: str):
        return await self._user_repo.get_by_username(username)

    async def get_overview(self, username: str) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        return compute_overview(
            username=username,
            solved=solved,
            user=user,
            ranking=user.ranking,
            real_name=user.real_name,
            avatar_url=user.avatar_url,
        )

    async def get_topics(self, username: str) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        return compute_topics(username=username, solved=solved, user=user)

    async def get_patterns(self, username: str) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        return compute_patterns(username=username, solved=solved, user=user)

    async def get_pattern_detail(self, username: str, pattern_slug: str) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        return compute_pattern_detail(username=username, solved=solved, pattern_slug=pattern_slug, user=user)

    async def get_coverage(self, username: str) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        all_patterns = await self._problem_repo.get_all_patterns()
        return compute_coverage(username=username, solved=solved, all_patterns=all_patterns, user=user)

    async def get_problems(self, username: str, difficulty: str | None = None) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        problems = []
        for usp in solved:
            p = usp.problem
            if difficulty and p.difficulty.value.lower() != difficulty.lower():
                continue
            problems.append({
                "leetcode_id": p.leetcode_id,
                "title": p.title,
                "slug": p.slug,
                "difficulty": p.difficulty.value,
                "url": p.url,
                "solved_at": usp.last_solved_at.strftime("%Y-%m-%d %H:%M") if usp.last_solved_at else None,
                "topics": [pt.topic.name for pt in p.topics] if p.topics else [],
            })
        problems.sort(key=lambda x: x["leetcode_id"])
        total_solved = user.total_solved if user.total_solved > 0 else len(problems)
        return {
            "username": username,
            "total": total_solved,
            "total_confirmed": len(problems),
            "problems": problems,
        }

    async def get_taxonomy_explorer(self, username: str) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        return compute_taxonomy_explorer(username=username, solved=solved, user=user)

    async def get_student_analysis(self, username: str) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        return compute_student_analysis(username=username, solved=solved, user=user)

    async def get_activity_timeline(self, username: str) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        return compute_activity_timeline(username=username, solved=solved, user=user)

    async def get_pattern_practice(self, username: str) -> dict | None:
        user = await self._user_repo.get_by_username(username)
        if not user:
            return None
        solved = await self._problem_repo.get_user_solved(user.id)
        return compute_pattern_practice(username=username, solved=solved, user=user)
