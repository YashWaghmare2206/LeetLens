"""
Analysis Engine — Patterns
Calculates per-pattern solved counts with difficulty breakdown and exact problem list.

IMPORTANT: A problem may belong to multiple patterns.
- Pattern counts: each (problem × pattern) pair counts once per pattern.
- Total solved (in overview): each problem counted exactly once.
- Incorporates verified LeetCode skill counts when available.
"""
from __future__ import annotations
import json
import re
from collections import defaultdict
from typing import TYPE_CHECKING
from app.schemas.enums import Difficulty
from app.schemas.stateless import StatelessSolved

if TYPE_CHECKING:
    from app.schemas.stateless import StatelessUser


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def compute_patterns(
    username: str,
    solved: list[StatelessSolved],
    user: StatelessUser | None = None,
) -> dict:
    stats: dict[str, dict] = defaultdict(lambda: {
        "pattern": "",
        "pattern_slug": "",
        "solved_count": 0,
        "easy": 0,
        "medium": 0,
        "hard": 0,
        "problems": [],
    })

    # 1. Tally from confirmed solved problems
    for usp in solved:
        p = usp.problem
        diff = p.difficulty
        for pp in p.patterns:
            slug = pp.pattern.slug
            stats[slug]["pattern"] = pp.pattern.name
            stats[slug]["pattern_slug"] = slug
            stats[slug]["solved_count"] += 1
            if diff == Difficulty.EASY:
                stats[slug]["easy"] += 1
            elif diff == Difficulty.MEDIUM:
                stats[slug]["medium"] += 1
            elif diff == Difficulty.HARD:
                stats[slug]["hard"] += 1
            stats[slug]["problems"].append({
                "leetcode_id": p.leetcode_id,
                "title": p.title,
                "slug": p.slug,
                "difficulty": p.difficulty.value,
                "url": p.url,
            })

    # 2. Correlate with LeetCode verified skills (e.g. two-pointers: 38, sliding-window: 14)
    if user and user.skill_stats_json:
        try:
            skills = json.loads(user.skill_stats_json)
            total_solved = user.total_solved or 1
            easy_ratio = (user.easy_solved or 0) / total_solved
            med_ratio = (user.medium_solved or 0) / total_solved

            skill_map = {item.get("tag_slug"): item for item in skills}

            for slug, item in skill_map.items():
                count = item.get("problems_solved", 0)
                name = item.get("tag_name", "")
                if count <= 0:
                    continue

                # Match patterns that correspond directly to this skill
                matched_slugs = []
                for p_slug in list(stats.keys()):
                    if p_slug == slug or slug in p_slug:
                        matched_slugs.append(p_slug)

                if matched_slugs:
                    for m_slug in matched_slugs:
                        if count > stats[m_slug]["solved_count"]:
                            diff_rem = count - stats[m_slug]["solved_count"]
                            stats[m_slug]["solved_count"] = count
                            stats[m_slug]["easy"] += round(diff_rem * easy_ratio)
                            stats[m_slug]["medium"] += round(diff_rem * med_ratio)
                            stats[m_slug]["hard"] = max(0, count - stats[m_slug]["easy"] - stats[m_slug]["medium"])
                else:
                    # If it's a prominent algorithmic pattern, ensure it exists in patterns list
                    if slug in (
                        "two-pointers", "sliding-window", "binary-search", "dynamic-programming",
                        "depth-first-search", "breadth-first-search", "monotonic-stack",
                        "monotonic-queue", "union-find", "backtracking", "divide-and-conquer",
                        "shortest-path", "trie",
                    ):
                        p_slug = slug
                        stats[p_slug]["pattern"] = name
                        stats[p_slug]["pattern_slug"] = p_slug
                        stats[p_slug]["solved_count"] = count
                        stats[p_slug]["easy"] = round(count * easy_ratio)
                        stats[p_slug]["medium"] = round(count * med_ratio)
                        stats[p_slug]["hard"] = max(0, count - stats[p_slug]["easy"] - stats[p_slug]["medium"])
        except Exception:
            pass

    sorted_patterns = sorted(stats.values(), key=lambda x: x["solved_count"], reverse=True)
    return {"username": username, "patterns": sorted_patterns}


def compute_pattern_detail(
    username: str,
    solved: list[StatelessSolved],
    pattern_slug: str,
    user: StatelessUser | None = None,
) -> dict | None:
    """Returns detail for a single pattern, or None if pattern not found in user's solved."""
    aggregated = compute_patterns(username, solved, user=user)
    for p in aggregated["patterns"]:
        if p["pattern_slug"] == pattern_slug:
            return p
    return None
