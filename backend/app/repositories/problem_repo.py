"""
Problem repository — database access for problems, topics, patterns,
and their junction tables.
"""
from __future__ import annotations
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.problem import (
    Problem, Topic, Pattern,
    ProblemTopic, ProblemPattern, UserSolvedProblem,
    Difficulty, ClassificationSource, ClassificationStatus,
)


class ProblemRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Problems ──────────────────────────────────────────────────────────

    async def get_problem_by_leetcode_id(self, leetcode_id: int) -> Problem | None:
        result = await self._db.execute(
            select(Problem).where(Problem.leetcode_id == leetcode_id)
        )
        return result.scalar_one_or_none()

    async def get_problem_by_slug(self, slug: str) -> Problem | None:
        result = await self._db.execute(
            select(Problem).where(Problem.slug == slug)
        )
        return result.scalar_one_or_none()

    async def upsert_problem(
        self,
        leetcode_id: int,
        title: str,
        slug: str,
        difficulty: str,
        url: str | None = None,
        paid_only: bool = False,
    ) -> Problem:
        diff = Difficulty(difficulty) if difficulty in Difficulty._value2member_map_ else Difficulty.UNKNOWN
        problem = await self.get_problem_by_slug(slug)
        if not problem and leetcode_id > 0:
            problem = await self.get_problem_by_leetcode_id(leetcode_id)

        if problem:
            problem.title = title
            problem.slug = slug
            if leetcode_id > 0:
                problem.leetcode_id = leetcode_id
            if diff != Difficulty.UNKNOWN:
                problem.difficulty = diff
            if url:
                problem.url = url
            problem.paid_only = paid_only
        else:
            url = url or f"https://leetcode.com/problems/{slug}/"
            problem = Problem(
                leetcode_id=leetcode_id,
                title=title,
                slug=slug,
                difficulty=diff,
                url=url,
                paid_only=paid_only,
                classification_status=ClassificationStatus.UNCLASSIFIED,
            )
            self._db.add(problem)
        await self._db.flush()
        await self._db.refresh(problem)
        return problem

    async def get_all_problems(self) -> list[Problem]:
        result = await self._db.execute(select(Problem))
        return list(result.scalars().all())

    # ── Topics ───────────────────────────────────────────────────────────

    async def get_topic_by_slug(self, slug: str) -> Topic | None:
        result = await self._db.execute(
            select(Topic).where(Topic.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_all_topics(self) -> list[Topic]:
        result = await self._db.execute(select(Topic))
        return list(result.scalars().all())

    async def upsert_topic(self, name: str, slug: str, parent_id: int | None = None) -> Topic:
        topic = await self.get_topic_by_slug(slug)
        if not topic:
            topic = Topic(name=name, slug=slug, parent_id=parent_id)
            self._db.add(topic)
            await self._db.flush()
            await self._db.refresh(topic)
        return topic

    async def link_problem_topic(
        self, problem_id: int, topic_id: int, source: ClassificationSource = ClassificationSource.LEETCODE
    ) -> None:
        result = await self._db.execute(
            select(ProblemTopic).where(
                ProblemTopic.problem_id == problem_id,
                ProblemTopic.topic_id == topic_id,
            )
        )
        if not result.scalar_one_or_none():
            self._db.add(ProblemTopic(problem_id=problem_id, topic_id=topic_id, source=source))
            await self._db.flush()

    # ── Patterns ──────────────────────────────────────────────────────────

    async def get_pattern_by_slug(self, slug: str) -> Pattern | None:
        result = await self._db.execute(
            select(Pattern).where(Pattern.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_pattern_by_name(self, name: str) -> Pattern | None:
        result = await self._db.execute(
            select(Pattern).where(Pattern.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_patterns(self) -> list[Pattern]:
        result = await self._db.execute(select(Pattern))
        return list(result.scalars().all())

    async def upsert_pattern(
        self, name: str, slug: str, description: str | None = None, parent_id: int | None = None
    ) -> Pattern:
        pattern = await self.get_pattern_by_slug(slug)
        if not pattern:
            pattern = Pattern(name=name, slug=slug, description=description, parent_id=parent_id)
            self._db.add(pattern)
            await self._db.flush()
            await self._db.refresh(pattern)
        return pattern

    async def link_problem_pattern(
        self,
        problem_id: int,
        pattern_id: int,
        confidence: float = 1.0,
        source: ClassificationSource = ClassificationSource.CURATED,
    ) -> None:
        result = await self._db.execute(
            select(ProblemPattern).where(
                ProblemPattern.problem_id == problem_id,
                ProblemPattern.pattern_id == pattern_id,
            )
        )
        if not result.scalar_one_or_none():
            self._db.add(ProblemPattern(
                problem_id=problem_id,
                pattern_id=pattern_id,
                confidence=confidence,
                source=source,
            ))
            await self._db.flush()

    # ── UserSolvedProblems ────────────────────────────────────────────────

    async def get_user_solved(self, user_id: int) -> list[UserSolvedProblem]:
        result = await self._db.execute(
            select(UserSolvedProblem)
            .options(
                selectinload(UserSolvedProblem.problem)
                .selectinload(Problem.patterns)
                .selectinload(ProblemPattern.pattern),
                selectinload(UserSolvedProblem.problem)
                .selectinload(Problem.topics)
                .selectinload(ProblemTopic.topic),
            )
            .where(UserSolvedProblem.user_id == user_id)
        )
        return list(result.scalars().all())

    async def upsert_solved_problem(
        self,
        user_id: int,
        problem_id: int,
        last_solved_at=None,
    ) -> UserSolvedProblem:
        result = await self._db.execute(
            select(UserSolvedProblem).where(
                UserSolvedProblem.user_id == user_id,
                UserSolvedProblem.problem_id == problem_id,
            )
        )
        usp = result.scalar_one_or_none()
        if usp:
            usp.attempts += 1
            if last_solved_at:
                usp.last_solved_at = last_solved_at
        else:
            from datetime import datetime, timezone
            now = last_solved_at or datetime.now(timezone.utc)
            usp = UserSolvedProblem(
                user_id=user_id,
                problem_id=problem_id,
                first_solved_at=now,
                last_solved_at=now,
                attempts=1,
            )
            self._db.add(usp)
        await self._db.flush()
        return usp
