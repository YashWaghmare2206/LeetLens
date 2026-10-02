"""
Seed service — loads taxonomy data into the database.
Called once on startup (idempotent).
"""
from __future__ import annotations
import logging
import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.problem_repo import ProblemRepository
from app.data.taxonomy import TOPICS, TAXONOMY, PROBLEM_PATTERNS

logger = logging.getLogger(__name__)


def _to_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


async def seed_taxonomy(db: AsyncSession) -> None:
    """Seed topics and patterns from curated taxonomy. Idempotent."""
    repo = ProblemRepository(db)

    # 1. Upsert parent topics
    topic_name_to_id: dict[str, int] = {}
    for slug, name, _desc in TOPICS:
        topic = await repo.upsert_topic(name=name, slug=slug)
        topic_name_to_id[slug] = topic.id
    logger.info("Seeded %d topics", len(TOPICS))

    # 2. Upsert patterns with parent references
    pattern_name_to_id: dict[str, int] = {}
    for entry in TAXONOMY:
        parent_topic_id = topic_name_to_id.get(entry.parent)
        slug = _to_slug(entry.pattern)
        pattern = await repo.upsert_pattern(
            name=entry.pattern,
            slug=slug,
            description=entry.description,
            parent_id=parent_topic_id,
        )
        pattern_name_to_id[entry.pattern] = pattern.id
    logger.info("Seeded %d patterns", len(TAXONOMY))

    # 3. Link problem↔pattern mappings (only for problems that exist in DB)
    linked = 0
    for leetcode_id, pattern_name, confidence in PROBLEM_PATTERNS:
        problem = await repo.get_problem_by_leetcode_id(leetcode_id)
        if not problem:
            continue  # Problem not yet in DB — skip, link later after sync
        pattern_id = pattern_name_to_id.get(pattern_name)
        if not pattern_id:
            logger.warning("Unknown pattern in taxonomy: %s", pattern_name)
            continue
        await repo.link_problem_pattern(
            problem_id=problem.id,
            pattern_id=pattern_id,
            confidence=confidence,
        )
        linked += 1

    logger.info("Linked %d problem-pattern mappings", linked)
    await db.commit()
