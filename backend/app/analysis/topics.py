"""
Analysis Engine — Topics
Calculates per-topic solved counts with difficulty breakdown.
Uses verified LeetCode tagProblemCounts when available so all 35+ DSA topics
accurately reflect total problems solved.
"""
from __future__ import annotations
import json
from collections import defaultdict
from typing import TYPE_CHECKING
from app.models.problem import UserSolvedProblem, Difficulty

if TYPE_CHECKING:
    from app.models.user import User


def compute_topics(
    username: str,
    solved: list[UserSolvedProblem],
    user: User | None = None,
) -> dict:
    stats: dict[str, dict] = defaultdict(
        lambda: {"solved_count": 0, "easy": 0, "medium": 0, "hard": 0, "topic": "", "topic_slug": ""}
    )

    # 1. First count from local solved problems
    for usp in solved:
        diff = usp.problem.difficulty
        for pt in usp.problem.topics:
            slug = pt.topic.slug
            stats[slug]["topic"] = pt.topic.name
            stats[slug]["topic_slug"] = slug
            stats[slug]["solved_count"] += 1
            if diff == Difficulty.EASY:
                stats[slug]["easy"] += 1
            elif diff == Difficulty.MEDIUM:
                stats[slug]["medium"] += 1
            elif diff == Difficulty.HARD:
                stats[slug]["hard"] += 1

    # 2. If user has verified skill stats from LeetCode, incorporate all 35+ topics
    if user and user.skill_stats_json:
        try:
            skills = json.loads(user.skill_stats_json)
            total_solved = user.total_solved or 1
            easy_ratio = (user.easy_solved or 0) / total_solved
            med_ratio = (user.medium_solved or 0) / total_solved
            hard_ratio = (user.hard_solved or 0) / total_solved

            for item in skills:
                slug = item.get("tag_slug") or ""
                name = item.get("tag_name") or ""
                count = item.get("problems_solved", 0)
                if not slug or count == 0:
                    continue

                if slug not in stats:
                    stats[slug]["topic"] = name
                    stats[slug]["topic_slug"] = slug
                    stats[slug]["solved_count"] = count
                    stats[slug]["easy"] = round(count * easy_ratio)
                    stats[slug]["medium"] = round(count * med_ratio)
                    stats[slug]["hard"] = max(0, count - stats[slug]["easy"] - stats[slug]["medium"])
                else:
                    # If LeetCode tag count is greater than our local subset, update total count
                    if count > stats[slug]["solved_count"]:
                        stats[slug]["topic"] = name
                        diff_rem = count - stats[slug]["solved_count"]
                        stats[slug]["solved_count"] = count
                        stats[slug]["easy"] += round(diff_rem * easy_ratio)
                        stats[slug]["medium"] += round(diff_rem * med_ratio)
                        stats[slug]["hard"] = max(0, count - stats[slug]["easy"] - stats[slug]["medium"])
        except Exception:
            pass

    sorted_topics = sorted(stats.values(), key=lambda x: x["solved_count"], reverse=True)
    return {"username": username, "topics": sorted_topics}
