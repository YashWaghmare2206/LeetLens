"""
Stateless Service — Pure in-memory DSA analysis engine.
Zero database dependencies. Fetches directly from LeetCode public API and caches in-memory.
"""
from __future__ import annotations
import asyncio
import json
import logging
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.models.problem import Difficulty
from app.providers.leetcode.client import LeetCodeProvider
from app.data.taxonomy import TOPICS, TAXONOMY, PROBLEM_PATTERNS
from app.analysis.overview import compute_overview
from app.analysis.topics import compute_topics
from app.analysis.patterns import compute_patterns, compute_pattern_detail
from app.analysis.coverage import compute_coverage
from app.analysis.taxonomy_explorer import compute_taxonomy_explorer
from app.analysis.student_analysis import compute_student_analysis
from app.analysis.activity_timeline import compute_activity_timeline
from app.analysis.pattern_practice import compute_pattern_practice

logger = logging.getLogger(__name__)


def _to_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")



@dataclass
class StatelessTopic:
    id: int
    name: str
    slug: str


@dataclass
class StatelessProblemTopic:
    topic: StatelessTopic


@dataclass
class StatelessPattern:
    id: int
    name: str
    slug: str
    description: str = ""
    parent: str | None = None
    parent_id: int | None = None
    parent_topic: StatelessTopic | None = None


@dataclass
class StatelessProblemPattern:
    pattern: StatelessPattern
    confidence: float


@dataclass
class StatelessProblem:
    id: int
    leetcode_id: int
    title: str
    slug: str
    difficulty: Difficulty
    url: str | None = None
    is_paid_only: bool = False
    topics: list[StatelessProblemTopic] = field(default_factory=list)
    patterns: list[StatelessProblemPattern] = field(default_factory=list)


@dataclass
class StatelessSolved:
    problem: StatelessProblem
    last_solved_at: datetime | None


@dataclass
class StatelessUser:
    id: int
    username: str
    real_name: str | None = None
    avatar_url: str | None = None
    ranking: int | None = None
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    total_submissions: int = 0
    streak: int | None = None
    total_active_days: int | None = None
    beats_easy: float | None = None
    beats_medium: float | None = None
    beats_hard: float | None = None
    badges_json: str | None = None
    upcoming_badges_json: str | None = None
    languages_json: str | None = None
    submission_calendar_json: str | None = None
    skill_stats_json: str | None = None
    acceptance_rate: float | None = None
    reputation: int | None = None



_TOPIC_MAP: dict[str, StatelessTopic] = {}
for idx, (slug, name, _desc) in enumerate(TOPICS, 1):
    _TOPIC_MAP[slug] = StatelessTopic(id=idx, name=name, slug=slug)

_PATTERN_MAP: dict[str, StatelessPattern] = {}
_ALL_PATTERNS: list[StatelessPattern] = []
for idx, entry in enumerate(TAXONOMY, 1):
    slug = _to_slug(entry.pattern)
    parent_top = _TOPIC_MAP.get(entry.parent)
    pat = StatelessPattern(
        id=idx,
        name=entry.pattern,
        slug=slug,
        description=entry.description,
        parent=entry.parent,
        parent_id=parent_top.id if parent_top else None,
        parent_topic=parent_top,
    )
    _PATTERN_MAP[entry.pattern] = pat
    _PATTERN_MAP[slug] = pat
    _ALL_PATTERNS.append(pat)

_LC_ID_TO_PATTERNS: dict[int, list[tuple[StatelessPattern, float]]] = defaultdict(list)
for (lc_id, pname, conf) in PROBLEM_PATTERNS:
    if pname in _PATTERN_MAP:
        _LC_ID_TO_PATTERNS[lc_id].append((_PATTERN_MAP[pname], conf))



_STATELESS_STORE: dict[str, dict[str, Any]] = {}
_CACHE_TTL = 300  # 5 minutes


class StatelessService:
    @staticmethod
    async def get_or_fetch(username: str, force: bool = False) -> dict[str, Any] | None:
        """Fetch and compute all analytics in-memory directly from LeetCode."""
        normalized = username.strip().lower()
        now = time.time()

        if not force and normalized in _STATELESS_STORE:
            cached = _STATELESS_STORE[normalized]
            if now - cached.get("cached_at", 0) < _CACHE_TTL:
                return cached

        async with LeetCodeProvider() as lc:
            full_data = await lc.get_full_user_data(username)
            if not full_data:
                profile = await lc.get_profile(username)
                if not profile:
                    return None
                from app.providers.leetcode.parser import LCFullUserData
                full_data = LCFullUserData(
                    username=profile.username,
                    real_name=profile.real_name,
                    avatar_url=profile.avatar_url,
                    ranking=profile.ranking,
                    total_solved=0,
                    easy_solved=0,
                    medium_solved=0,
                    hard_solved=0,
                    total_submissions=0,
                    streak=None,
                    total_active_days=None,
                    beats_easy=None,
                    beats_medium=None,
                    beats_hard=None,
                    tag_problem_counts=[],
                )

            # Build StatelessUser
            skill_json = json.dumps([
                {
                    "tag_name": t.tag_name,
                    "tag_slug": t.tag_slug,
                    "problems_solved": t.problems_solved,
                    "category": t.category,
                }
                for t in full_data.tag_problem_counts
            ]) if full_data.tag_problem_counts else None

            user = StatelessUser(
                id=1,
                username=username,
                real_name=full_data.real_name,
                avatar_url=full_data.avatar_url,
                ranking=full_data.ranking,
                total_solved=full_data.total_solved,
                easy_solved=full_data.easy_solved,
                medium_solved=full_data.medium_solved,
                hard_solved=full_data.hard_solved,
                total_submissions=full_data.total_submissions,
                acceptance_rate=full_data.acceptance_rate,
                reputation=full_data.reputation,
                streak=full_data.streak,
                total_active_days=full_data.total_active_days,
                beats_easy=full_data.beats_easy,
                beats_medium=full_data.beats_medium,
                beats_hard=full_data.beats_hard,
                skill_stats_json=skill_json,
                badges_json=json.dumps(full_data.badges) if full_data.badges else None,
                upcoming_badges_json=json.dumps(full_data.upcoming_badges) if full_data.upcoming_badges else None,
                languages_json=json.dumps(full_data.languages) if full_data.languages else None,
                submission_calendar_json=full_data.submission_calendar,
            )

            # Fetch recent submissions
            recent_ac = await lc.get_recent_ac_submissions(username, limit=20)
            try:
                all_recent = await lc.get_recent_submissions(username, limit=20)
            except Exception:
                all_recent = []

            seen_slugs = set()
            recent = []
            for s in recent_ac + all_recent:
                if s.slug and s.slug not in seen_slugs:
                    seen_slugs.add(s.slug)
                    recent.append(s)

            # Concurrently fetch problem metadata (difficulty & topic tags)
            sem = asyncio.Semaphore(4)
            async def fetch_q(slug: str):
                async with sem:
                    try:
                        return slug, await lc.get_question_data(slug)
                    except Exception:
                        return slug, None

            missing_q = await asyncio.gather(*(fetch_q(s.slug) for s in recent))
            q_map = dict(missing_q)

            # Build list of StatelessSolved
            solved: list[StatelessSolved] = []
            for idx, sub in enumerate(recent, 1):
                q_data = q_map.get(sub.slug)
                diff_str = (q_data.difficulty if q_data else "Unknown").title()
                try:
                    diff = Difficulty(diff_str)
                except Exception:
                    diff = Difficulty.UNKNOWN

                lc_id = q_data.frontend_id if q_data else 0
                title = (q_data.title if q_data else None) or sub.title

                # Map topics
                problem_topics = []
                if q_data and q_data.topic_tags:
                    for tag in q_data.topic_tags:
                        t_slug = _to_slug(tag)
                        top = _TOPIC_MAP.get(t_slug) or StatelessTopic(id=len(_TOPIC_MAP) + 1, name=tag, slug=t_slug)
                        problem_topics.append(StatelessProblemTopic(topic=top))

                # Map patterns
                problem_patterns = []
                if lc_id in _LC_ID_TO_PATTERNS:
                    for pat, conf in _LC_ID_TO_PATTERNS[lc_id]:
                        problem_patterns.append(StatelessProblemPattern(pattern=pat, confidence=conf))

                prob = StatelessProblem(
                    id=idx,
                    leetcode_id=lc_id,
                    title=title,
                    slug=sub.slug,
                    difficulty=diff,
                    url=f"https://leetcode.com/problems/{sub.slug}/",
                    topics=problem_topics,
                    patterns=problem_patterns,
                )

                solved.append(StatelessSolved(problem=prob, last_solved_at=sub.timestamp))

        # Compute full analysis in memory
        overview = compute_overview(username=username, solved=solved, user=user)
        topics = compute_topics(username=username, solved=solved, user=user)
        patterns = compute_patterns(username=username, solved=solved, user=user)
        coverage = compute_coverage(username=username, solved=solved, all_patterns=_ALL_PATTERNS, user=user)
        taxonomy = compute_taxonomy_explorer(username=username, solved=solved, user=user)
        student_analysis = compute_student_analysis(username=username, solved=solved, user=user)
        timeline = compute_activity_timeline(username=username, solved=solved, user=user)
        practice = compute_pattern_practice(username=username, solved=solved, user=user)

        # Build problems table payload
        problems_list = []
        for usp in solved:
            p = usp.problem
            problems_list.append({
                "leetcode_id": p.leetcode_id,
                "title": p.title,
                "slug": p.slug,
                "difficulty": p.difficulty.value,
                "url": p.url,
                "solved_at": usp.last_solved_at.strftime("%Y-%m-%d %H:%M") if usp.last_solved_at else None,
                "topics": [pt.topic.name for pt in p.topics],
            })
        problems_list.sort(key=lambda x: x["leetcode_id"])

        data = {
            "cached_at": now,
            "user": {
                "id": 1,
                "username": username,
                "real_name": user.real_name,
                "avatar_url": user.avatar_url,
                "ranking": user.ranking,
                "total_solved": user.total_solved,
                "easy_solved": user.easy_solved,
                "medium_solved": user.medium_solved,
                "hard_solved": user.hard_solved,
                "total_submissions": user.total_submissions,
                "streak": user.streak,
                "total_active_days": user.total_active_days,
                "beats_easy": user.beats_easy,
                "beats_medium": user.beats_medium,
                "beats_hard": user.beats_hard,
                "acceptance_rate": user.acceptance_rate,
                "reputation": user.reputation,
                "created_at": datetime.now(timezone.utc),
            },
            "overview": overview,
            "topics": topics,
            "patterns": patterns,
            "coverage": coverage,
            "taxonomy": taxonomy,
            "student_analysis": student_analysis,
            "timeline": timeline,
            "practice": practice,
            "problems": {
                "username": username,
                "total": user.total_solved if user.total_solved > 0 else len(problems_list),
                "total_confirmed": len(problems_list),
                "problems": problems_list,
            },
        }

        _STATELESS_STORE[normalized] = data
        return data

    @staticmethod
    async def get_overview(username: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        return data.get("overview") if data else None

    @staticmethod
    async def get_topics(username: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        return data.get("topics") if data else None

    @staticmethod
    async def get_patterns(username: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        return data.get("patterns") if data else None

    @staticmethod
    async def get_pattern_detail(username: str, pattern_slug: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        if not data:
            return None
        patterns_data = data.get("patterns", {}).get("patterns", [])
        for p in patterns_data:
            if p.get("pattern_slug") == pattern_slug:
                return {
                    "username": username,
                    "pattern": p["pattern"],
                    "pattern_slug": p["pattern_slug"],
                    "solved_count": p["solved_count"],
                    "easy": p["easy"],
                    "medium": p["medium"],
                    "hard": p["hard"],
                    "problems": p.get("problems", []),
                }
        return None

    @staticmethod
    async def get_coverage(username: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        return data.get("coverage") if data else None

    @staticmethod
    async def get_problems(username: str, difficulty: str | None = None) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        if not data:
            return None
        raw = data.get("problems", {})
        if not difficulty:
            return raw
        filtered = [p for p in raw.get("problems", []) if p["difficulty"].lower() == difficulty.lower()]
        return {
            "username": username,
            "total": raw.get("total", len(filtered)),
            "total_confirmed": len(filtered),
            "problems": filtered,
        }

    @staticmethod
    async def get_taxonomy_explorer(username: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        return data.get("taxonomy") if data else None

    @staticmethod
    async def get_student_analysis(username: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        return data.get("student_analysis") if data else None

    @staticmethod
    async def get_activity_timeline(username: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        return data.get("timeline") if data else None

    @staticmethod
    async def get_pattern_practice(username: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        return data.get("practice") if data else None

    @staticmethod
    async def get_user(username: str) -> dict | None:
        data = await StatelessService.get_or_fetch(username)
        return data.get("user") if data else None
