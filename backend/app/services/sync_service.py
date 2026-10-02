"""
Sync service — orchestrates a full user profile synchronization.

Flow:
  POST /users/{username}/sync
    → create SyncJob
    → run in background thread (no Celery needed locally)
    → fetch LeetCode profile + solved stats + recent submissions
    → upsert user + problems
    → link problem patterns from taxonomy
    → mark job SUCCESS

Error handling:
  - If LeetCode is unavailable → job FAILED, existing data preserved
  - If user not found → job FAILED with descriptive error
"""
from __future__ import annotations
import asyncio
import logging
import re
import threading
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_job import SyncJob
from app.repositories.user_repo import UserRepository
from app.repositories.problem_repo import ProblemRepository
from app.repositories.sync_repo import SyncJobRepository
from app.providers.leetcode.client import LeetCodeProvider
from app.services.seed_service import seed_taxonomy, _to_slug
from app.data.taxonomy import PROBLEM_PATTERNS, TAXONOMY

logger = logging.getLogger(__name__)


# In-memory cache: username → analysis data (cleared on new sync)
_analysis_cache: dict[str, dict] = {}


def invalidate_cache(username: str) -> None:
    _analysis_cache.pop(username, None)


def get_cache(username: str) -> dict | None:
    return _analysis_cache.get(username)


def set_cache(username: str, data: dict) -> None:
    _analysis_cache[username] = data


async def _run_sync(job_id: int, username: str) -> None:
    """The actual sync logic, runs in an async context."""
    from app.database import AsyncSessionLocal as SessionLocal

    async with SessionLocal() as db:
        sync_repo = SyncJobRepository(db)
        user_repo = UserRepository(db)
        problem_repo = ProblemRepository(db)

        job = await sync_repo.get_by_id(job_id)
        if not job:
            logger.error("SyncJob %d not found", job_id)
            return

        await sync_repo.mark_running(job)
        await db.commit()

        try:
            async with LeetCodeProvider() as lc:
                # Step 1: fetch full user profile & stats
                await sync_repo.set_progress(job, 10)
                await db.commit()

                full_data = await lc.get_full_user_data(username)
                if not full_data:
                    profile = await lc.get_profile(username)
                    if not profile:
                        await sync_repo.mark_failed(job, f"LeetCode user '{username}' not found")
                        await db.commit()
                        return
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

                # Step 2: update user in DB
                user, _ = await user_repo.get_or_create(username)
                import json
                skill_json = json.dumps([
                    {
                        "tag_name": t.tag_name,
                        "tag_slug": t.tag_slug,
                        "problems_solved": t.problems_solved,
                        "category": t.category,
                    }
                    for t in full_data.tag_problem_counts
                ])
                badges_json = json.dumps(full_data.badges) if full_data.badges else None
                upcoming_json = json.dumps(full_data.upcoming_badges) if full_data.upcoming_badges else None
                languages_json = json.dumps(full_data.languages) if full_data.languages else None
                
                await user_repo.update(
                    user,
                    real_name=full_data.real_name,
                    avatar_url=full_data.avatar_url,
                    ranking=full_data.ranking,
                    leetcode_url=f"https://leetcode.com/u/{username}/",
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
                    badges_json=badges_json,
                    upcoming_badges_json=upcoming_json,
                    languages_json=languages_json,
                    submission_calendar_json=full_data.submission_calendar,
                )
                await db.commit()
                await sync_repo.set_progress(job, 30)
                await db.commit()

                # Ensure all topics from skill stats are registered in DB
                for t in full_data.tag_problem_counts:
                    await problem_repo.upsert_topic(name=t.tag_name, slug=t.tag_slug)
                await db.commit()

                # Step 3: fetch both recent AC submissions and general recent submissions
                recent_ac = await lc.get_recent_ac_submissions(username, limit=20)
                try:
                    all_recent = await lc.get_recent_submissions(username, limit=20)
                except Exception:
                    all_recent = []

                # Merge unique by slug
                seen_slugs = set()
                recent = []
                for s in recent_ac + all_recent:
                    if s.slug and s.slug not in seen_slugs:
                        seen_slugs.add(s.slug)
                        recent.append(s)

                await sync_repo.set_progress(job, 45)
                await db.commit()

                # Step 4: ensure problems exist in DB and link patterns
                pattern_name_to_id = await _build_pattern_name_map(problem_repo)

                # Build a map of problem patterns from taxonomy
                lc_id_to_patterns: dict[int, list[tuple[str, float]]] = {}
                for (lc_id, pname, conf) in PROBLEM_PATTERNS:
                    if lc_id not in lc_id_to_patterns:
                        lc_id_to_patterns[lc_id] = []
                    lc_id_to_patterns[lc_id].append((pname, conf))

                # Pre-fetch any missing problem details concurrently to speed up sync dramatically
                missing_slugs = []
                for sub in recent:
                    prob = await problem_repo.get_problem_by_slug(sub.slug)
                    if not prob or prob.difficulty.value == "Unknown" or prob.leetcode_id == 0:
                        missing_slugs.append(sub.slug)

                fetched_q_map = {}
                if missing_slugs:
                    sem = asyncio.Semaphore(6)
                    async def fetch_q(slug: str):
                        async with sem:
                            try:
                                return slug, await lc.get_question_data(slug)
                            except Exception:
                                return slug, None
                    q_results = await asyncio.gather(*(fetch_q(s) for s in set(missing_slugs)))
                    fetched_q_map = dict(q_results)

                total_recent = len(recent)
                for i, sub in enumerate(recent):
                    prob = await problem_repo.get_problem_by_slug(sub.slug)
                    if not prob or prob.difficulty.value == "Unknown" or prob.leetcode_id == 0:
                        q_data = fetched_q_map.get(sub.slug)
                        if q_data:
                            prob = await problem_repo.upsert_problem(
                                leetcode_id=q_data.frontend_id,
                                title=q_data.title or sub.title,
                                slug=sub.slug,
                                difficulty=q_data.difficulty,
                                url=f"https://leetcode.com/problems/{sub.slug}/",
                                paid_only=q_data.is_paid_only,
                            )
                            for tag_name in q_data.topic_tags:
                                t_slug = _to_slug(tag_name)
                                top = await problem_repo.upsert_topic(name=tag_name, slug=t_slug)
                                await problem_repo.link_problem_topic(prob.id, top.id)
                        else:
                            if not prob:
                                prob = await problem_repo.upsert_problem(
                                    leetcode_id=0,
                                    title=sub.title,
                                    slug=sub.slug,
                                    difficulty="Unknown",
                                    url=f"https://leetcode.com/problems/{sub.slug}/",
                                )
                    # Link user solved
                    await problem_repo.upsert_solved_problem(
                        user_id=user.id,
                        problem_id=prob.id,
                        last_solved_at=sub.timestamp,
                    )
                    # Link patterns for this problem
                    if prob.leetcode_id and prob.leetcode_id in lc_id_to_patterns:
                        for pname, conf in lc_id_to_patterns[prob.leetcode_id]:
                            pid = pattern_name_to_id.get(pname)
                            if pid:
                                await problem_repo.link_problem_pattern(
                                    problem_id=prob.id,
                                    pattern_id=pid,
                                    confidence=conf,
                                )
                    progress = 45 + int(((i + 1) / max(total_recent, 1)) * 50)
                    await sync_repo.set_progress(job, progress)

                await db.commit()
                await sync_repo.mark_success(job)
                await db.commit()
                invalidate_cache(username)
                logger.info("Sync complete for user %s (job %d)", username, job_id)

        except Exception as exc:
            logger.exception("Sync failed for user %s (job %d): %s", username, job_id, exc)
            # IMPORTANT: never delete existing user data on sync failure
            try:
                job = await sync_repo.get_by_id(job_id)
                if job:
                    await sync_repo.mark_failed(job, str(exc)[:1000])
                    await db.commit()
            except Exception:
                pass


async def _build_pattern_name_map(problem_repo: ProblemRepository) -> dict[str, int]:
    """Builds a {pattern_name: pattern_id} map from DB."""
    patterns = await problem_repo.get_all_patterns()
    return {p.name: p.id for p in patterns}


def run_sync_in_background(job_id: int, username: str) -> None:
    """Launch sync as a background thread (no Celery needed for local dev)."""
    def _thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_run_sync(job_id, username))
        finally:
            loop.close()

    thread = threading.Thread(target=_thread, daemon=True)
    thread.start()
    logger.info("Started background sync thread for job %d (user=%s)", job_id, username)
