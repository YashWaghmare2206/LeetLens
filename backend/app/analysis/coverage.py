"""
Analysis Engine — Coverage
Shows which patterns the user has practiced vs. not practiced.
Correlates with verified LeetCode skill data so patterns practiced on LeetCode
are properly recognized.
"""
from __future__ import annotations
import json
from typing import TYPE_CHECKING
from app.models.problem import UserSolvedProblem, Pattern

if TYPE_CHECKING:
    from app.models.user import User


def compute_coverage(
    username: str,
    solved: list[UserSolvedProblem],
    all_patterns: list[Pattern],
    user: User | None = None,
) -> dict:
    # 1. Collect patterns from confirmed problems
    practiced_slugs: dict[str, int] = {}
    for usp in solved:
        for pp in usp.problem.patterns:
            slug = pp.pattern.slug
            practiced_slugs[slug] = practiced_slugs.get(slug, 0) + 1

    # 2. Correlate with LeetCode skills
    if user and user.skill_stats_json:
        try:
            skills = json.loads(user.skill_stats_json)
            skill_map = {item.get("tag_slug"): item.get("problems_solved", 0) for item in skills}
            for slug, count in skill_map.items():
                if count > 0:
                    for p in all_patterns:
                        if p.slug == slug or slug in p.slug:
                            current = practiced_slugs.get(p.slug, 0)
                            if count > current:
                                practiced_slugs[p.slug] = count
        except Exception:
            pass

    items = []
    for pattern in all_patterns:
        solved_count = practiced_slugs.get(pattern.slug, 0)
        parent = str(pattern.parent_id) if pattern.parent_id else None
        items.append({
            "pattern": pattern.name,
            "pattern_slug": pattern.slug,
            "parent": parent,
            "solved_count": solved_count,
            "practiced": solved_count > 0,
        })

    # Sort: practiced first, then by count descending, then by name
    items.sort(key=lambda x: (-x["solved_count"], x["pattern"]))

    total = len(items)
    practiced_count = sum(1 for i in items if i["practiced"])
    coverage_ratio = practiced_count / total if total > 0 else 0.0

    return {
        "username": username,
        "total_patterns": total,
        "practiced_count": practiced_count,
        "coverage_ratio": round(coverage_ratio, 4),
        "items": items,
    }
