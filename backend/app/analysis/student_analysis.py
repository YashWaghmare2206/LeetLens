"""
Analysis Engine — Student DSA Analysis & Interview Readiness Index
Evaluates a student's DSA progress across:
- Interview Readiness Score (0-100) with Tier
- Strengths (proven masteries)
- Critical Blindspots (patterns with high interview yield but 0 or low practice)
- Curated 3-Phase Action Plan (Next recommended problems to solve)
- Practice Velocity & Consistency
"""
from __future__ import annotations
import json
from typing import TYPE_CHECKING
from app.schemas.enums import Difficulty
from app.schemas.stateless import StatelessSolved
from app.data.taxonomy import TOPICS, TAXONOMY

if TYPE_CHECKING:
    from app.schemas.stateless import StatelessUser

# High-frequency interview patterns and their interview weight (1 to 10)
HIGH_FREQUENCY_PATTERNS = {
    "Two Pointers": {"topic": "Array", "weight": 9, "desc": "Crucial for arrays, strings, sorted collections"},
    "Sliding Window": {"topic": "Array", "weight": 9, "desc": "Subarrays, substrings, optimal window sizes"},
    "Binary Search": {"topic": "Array", "weight": 9, "desc": "Search spaces, monotonic conditions, optimization"},
    "Tree DFS": {"topic": "Tree", "weight": 10, "desc": "Path sums, traversals, recursion fundamentals"},
    "Tree BFS": {"topic": "Tree", "weight": 9, "desc": "Level-order traversals, shortest path in unweighted trees"},
    "Graph BFS": {"topic": "Graph", "weight": 9, "desc": "Shortest paths, grid traversal (islands, rotting oranges)"},
    "Graph DFS": {"topic": "Graph", "weight": 8, "desc": "Connected components, cycle detection, cloning"},
    "Topological Sort": {"topic": "Graph", "weight": 8, "desc": "Task scheduling, dependency ordering (Course Schedule)"},
    "Union Find": {"topic": "Graph", "weight": 8, "desc": "Dynamic connectivity, redundant connections"},
    "1D DP": {"topic": "Dynamic Programming", "weight": 9, "desc": "Decision making, climb stairs, robber, coin change"},
    "2D DP": {"topic": "Dynamic Programming", "weight": 8, "desc": "Grid paths, edit distance, longest common subsequence"},
    "Knapsack": {"topic": "Dynamic Programming", "weight": 7, "desc": "Subset sum partitions, 0/1 decision trees"},
    "Monotonic Stack": {"topic": "Stack", "weight": 8, "desc": "Next greater/smaller element, stock spans, histograms"},
    "Fast/Slow Pointers": {"topic": "Linked List", "weight": 8, "desc": "Cycle detection, finding middle of linked list"},
    "Subsets": {"topic": "Backtracking", "weight": 8, "desc": "Combinatorial generation, power sets"},
}

TARGET_RECOMMENDED_PROBLEMS = [
    {
        "pattern": "Topological Sort",
        "topic": "Graph",
        "leetcode_id": 207,
        "title": "Course Schedule",
        "difficulty": "Medium",
        "slug": "course-schedule",
        "why": "Classic dependency resolution interview question asked by Google, Meta, Amazon.",
    },
    {
        "pattern": "Union Find",
        "topic": "Graph",
        "leetcode_id": 684,
        "title": "Redundant Connection",
        "difficulty": "Medium",
        "slug": "redundant-connection",
        "why": "Essential for detecting cycles and connected components without recursion.",
    },
    {
        "pattern": "2D DP",
        "topic": "Dynamic Programming",
        "leetcode_id": 1143,
        "title": "Longest Common Subsequence",
        "difficulty": "Medium",
        "slug": "longest-common-subsequence",
        "why": "Fundamental 2D DP matrix pattern; foundational for string matching and diffing.",
    },
    {
        "pattern": "Knapsack",
        "topic": "Dynamic Programming",
        "leetcode_id": 416,
        "title": "Partition Equal Subset Sum",
        "difficulty": "Medium",
        "slug": "partition-equal-subset-sum",
        "why": "The quintessential 0/1 knapsack variation asked at Microsoft & Uber.",
    },
    {
        "pattern": "Monotonic Stack",
        "topic": "Stack",
        "leetcode_id": 84,
        "title": "Largest Rectangle in Histogram",
        "difficulty": "Hard",
        "slug": "largest-rectangle-in-histogram",
        "why": "Elite stack problem that separates proficient candidates from top 5% performers.",
    },
    {
        "pattern": "Graph BFS",
        "topic": "Graph",
        "leetcode_id": 994,
        "title": "Rotting Oranges",
        "difficulty": "Medium",
        "slug": "rotting-oranges",
        "why": "Multi-source BFS simulation, one of the most frequently asked problems in 2024-2026.",
    },
    {
        "pattern": "Trie",
        "topic": "Trie",
        "leetcode_id": 208,
        "title": "Implement Trie (Prefix Tree)",
        "difficulty": "Medium",
        "slug": "implement-trie-prefix-tree",
        "why": "High-yield data structure design problem frequently tested for autocomplete features.",
    },
]


def compute_student_analysis(
    username: str,
    solved: list[StatelessSolved],
    user: StatelessUser | None = None,
) -> dict:
    """Computes an actionable, comprehensive diagnostic report for a DSA student."""
    total_solved = user.total_solved if (user and user.total_solved > 0) else len(solved)
    easy = user.easy_solved if user else sum(1 for s in solved if s.problem.difficulty == Difficulty.EASY)
    med = user.medium_solved if user else sum(1 for s in solved if s.problem.difficulty == Difficulty.MEDIUM)
    hard = user.hard_solved if user else sum(1 for s in solved if s.problem.difficulty == Difficulty.HARD)
    streak = user.streak if user else None
    active_days = user.total_active_days if user else None
    ac_rate = user.acceptance_rate if user else None

    # Parse skills
    skill_map: dict[str, int] = {}
    if user and user.skill_stats_json:
        try:
            skills = json.loads(user.skill_stats_json)
            for item in skills:
                slug = item.get("tag_slug", "")
                cnt = item.get("problems_solved", 0)
                if slug and cnt > 0:
                    skill_map[slug] = cnt
        except Exception:
            pass

    # 1. Breadth Score (0-30 pts)
    # Checks coverage of Core Topics: Array, String, Hash Table, Linked List, Tree, Graph, DP, Stack, Binary Search
    core_topics = [
        "array", "string", "hash-table", "linked-list", "tree",
        "depth-first-search", "dynamic-programming", "stack", "binary-search", "two-pointers"
    ]
    covered_core = sum(1 for t in core_topics if skill_map.get(t, 0) >= 10)
    breadth_score = min(30, round((covered_core / len(core_topics)) * 30))

    # 2. Depth Score (0-30 pts)
    # Interviews test Mediums & Hards! If >= 40% are Medium/Hard, high score
    non_easy = med + hard
    if total_solved > 0:
        med_hard_ratio = non_easy / total_solved
        depth_score = min(30, round(med_hard_ratio * 45))  # 66% med/hard = 30 pts
    else:
        depth_score = 0

    # 3. Mastery Score (0-25 pts)
    # High volume in advanced patterns, scaled by confidence so inferred patterns don't count at full weight.
    adv_count = 0.0
    for s in solved:
        for pp in s.problem.patterns:
            if pp.pattern.slug in ("dynamic-programming", "graph", "monotonic-stack", "trie", "union-find", "backtracking"):
                adv_count += pp.confidence
    
    mastery_score = min(25, round(min(adv_count, 35) / 35 * 25))

    # 4. Consistency Score (0-15 pts)
    cons_score = 0
    if streak and streak >= 30:
        cons_score += 8
    elif streak and streak >= 7:
        cons_score += 4
    if active_days and active_days >= 60:
        cons_score += 7
    elif active_days and active_days >= 20:
        cons_score += 4
    consistency_score = min(15, cons_score)

    overall_score = min(100, breadth_score + depth_score + mastery_score + consistency_score)

    if overall_score >= 85:
        tier = "FAANG & Tier-1 Ready"
        tier_color = "#22c55e"
        readiness_badge = "🏆 Elite Readiness"
    elif overall_score >= 70:
        tier = "Strong Contender"
        tier_color = "#6172f3"
        readiness_badge = "⚡ Interview Strong"
    elif overall_score >= 50:
        tier = "Interview Apprentice"
        tier_color = "#f59e0b"
        readiness_badge = "📈 High Growth Potential"
    else:
        tier = "Foundation Builder"
        tier_color = "#ec4899"
        readiness_badge = "🌱 Foundation Phase"

    # Identify Strengths
    strengths = []
    if skill_map.get("array", 0) >= 50:
        strengths.append({
            "title": "Array & Sequence Mastery",
            "metric": f"{skill_map.get('array')} Solved",
            "description": "Formidable foundation in linear data structures, two pointers, and sliding window manipulations.",
            "icon": "📦",
        })
    if skill_map.get("tree", 0) >= 25 or skill_map.get("binary-tree", 0) >= 25:
        strengths.append({
            "title": "Tree & Hierarchical Traversals",
            "metric": f"{max(skill_map.get('tree', 0), skill_map.get('binary-tree', 0))} Solved",
            "description": "Consistent performance in recursive tree DFS and level-order BFS traversal problems.",
            "icon": "🌲",
        })
    if skill_map.get("depth-first-search", 0) >= 30:
        strengths.append({
            "title": "Search & Graph Traversal",
            "metric": f"{skill_map.get('depth-first-search')} Solved",
            "description": "Strong command over recursive backtracking and deep state space explorations.",
            "icon": "🔍",
        })
    if streak and streak >= 30:
        strengths.append({
            "title": "Elite Daily Discipline",
            "metric": f"{streak} Day Streak",
            "description": "Consistent problem-solving rhythm; top 5% among active LeetCode engineers.",
            "icon": "🔥",
        })

    # Identify Critical Blindspots
    blindspots = []
    if skill_map.get("graph", 0) < 10:
        blindspots.append({
            "pattern": "Graph Algorithms (BFS/DFS, Topological Sort)",
            "priority": "HIGH",
            "current_solved": skill_map.get("graph", 0),
            "target": 15,
            "impact": "Graph problems (Topological Sort, Dijkstra, Cycle Detection) appear in ~40% of tech screen interviews.",
            "action": "Solve Course Schedule (207) and Rotting Oranges (994).",
        })
    if skill_map.get("dynamic-programming", 0) < 25 or hard == 0:
        blindspots.append({
            "pattern": "2D Dynamic Programming & Knapsack",
            "priority": "HIGH",
            "current_solved": skill_map.get("dynamic-programming", 0),
            "target": 25,
            "impact": "Crucial differentiator in L4/L5 & senior engineering interviews. Practice state transitions.",
            "action": "Solve Longest Common Subsequence (1143) and Partition Equal Subset Sum (416).",
        })
    if skill_map.get("trie", 0) < 3:
        blindspots.append({
            "pattern": "Trie & Prefix Search",
            "priority": "MEDIUM",
            "current_solved": skill_map.get("trie", 0),
            "target": 5,
            "impact": "Essential for search autocomplete and word matrix problems (Word Search II).",
            "action": "Implement Trie (208) from scratch.",
        })
    if skill_map.get("union-find", 0) < 5:
        blindspots.append({
            "pattern": "Union-Find (Disjoint Set)",
            "priority": "MEDIUM",
            "current_solved": skill_map.get("union-find", 0),
            "target": 6,
            "impact": "O(1) amortized connectivity queries make complex graph problems trivial to code.",
            "action": "Solve Redundant Connection (684).",
        })

    # Recommended next problems (filter out already solved)
    solved_slugs = {usp.problem.slug for usp in solved}
    recommended = [p for p in TARGET_RECOMMENDED_PROBLEMS if p["slug"] not in solved_slugs][:6]

    return {
        "username": username,
        "readiness_score": overall_score,
        "readiness_tier": tier,
        "readiness_color": tier_color,
        "readiness_badge": readiness_badge,
        "score_breakdown": {
            "breadth": {"score": breadth_score, "max": 30, "label": "Topic Breadth"},
            "depth": {"score": depth_score, "max": 30, "label": "Difficulty Depth (M/H Ratio)"},
            "mastery": {"score": mastery_score, "max": 25, "label": "Pattern Mastery"},
            "consistency": {"score": consistency_score, "max": 15, "label": "Streak & Velocity"},
        },
        "strengths": strengths,
        "blindspots": blindspots,
        "recommended_problems": recommended,
        "velocity": {
            "active_days": active_days or 0,
            "streak": streak or 0,
            "total_solved": total_solved,
            "easy": easy,
            "medium": med,
            "hard": hard,
            "acceptance_rate": ac_rate,
            "average_per_active_day": round(total_solved / max(active_days or 1, 1), 1),
        },
    }
