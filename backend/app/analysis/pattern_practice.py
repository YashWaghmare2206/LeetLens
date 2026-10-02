"""
Analysis Engine — Pattern Practice Roadmaps with Company Filters & Spaced Repetition
Curated high-frequency interview problem bank categorized by Topic and Pattern.
Features:
- Parent Topic Grouping (Arrays, Trees, Graphs, DP, etc.)
- Top Tech Company Tagging (Google, Meta, Amazon, Microsoft, Apple, Uber)
- Spaced Repetition / "Revise Today" tracking for previously solved questions
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from app.models.problem import UserSolvedProblem
from app.data.taxonomy import TOPICS, TAXONOMY

if TYPE_CHECKING:
    from app.models.user import User

# Canonical high-frequency interview problems with company tags
PATTERN_PRACTICE_CURRICULUM: dict[str, list[dict]] = {
    "Two Pointers": [
        {"leetcode_id": 125, "title": "Valid Palindrome", "difficulty": "Easy", "slug": "valid-palindrome", "tier": "Warm-up", "companies": ["Meta", "Amazon", "Microsoft"]},
        {"leetcode_id": 167, "title": "Two Sum II - Input Array Is Sorted", "difficulty": "Medium", "slug": "two-sum-ii-input-array-is-sorted", "tier": "Core Interview", "companies": ["Amazon", "Google", "Apple"]},
        {"leetcode_id": 15, "title": "3Sum", "difficulty": "Medium", "slug": "3sum", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google", "Microsoft", "Apple"]},
        {"leetcode_id": 11, "title": "Container With Most Water", "difficulty": "Medium", "slug": "container-with-most-water", "tier": "Core Interview", "companies": ["Google", "Amazon", "Meta", "Adobe"]},
        {"leetcode_id": 42, "title": "Trapping Rain Water", "difficulty": "Hard", "slug": "trapping-rain-water", "tier": "Advanced Differentiator", "companies": ["Google", "Amazon", "Meta", "Microsoft", "Uber"]},
    ],
    "Sliding Window": [
        {"leetcode_id": 121, "title": "Best Time to Buy and Sell Stock", "difficulty": "Easy", "slug": "best-time-to-buy-and-sell-stock", "tier": "Warm-up", "companies": ["Amazon", "Meta", "Microsoft", "Google"]},
        {"leetcode_id": 3, "title": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "slug": "longest-substring-without-repeating-characters", "tier": "Core Interview", "companies": ["Amazon", "Google", "Meta", "Microsoft"]},
        {"leetcode_id": 424, "title": "Longest Repeating Character Replacement", "difficulty": "Medium", "slug": "longest-repeating-character-replacement", "tier": "Core Interview", "companies": ["Google", "Amazon", "Uber"]},
        {"leetcode_id": 567, "title": "Permutation in String", "difficulty": "Medium", "slug": "permutation-in-string", "tier": "Core Interview", "companies": ["Microsoft", "Amazon", "Meta"]},
        {"leetcode_id": 76, "title": "Minimum Window Substring", "difficulty": "Hard", "slug": "minimum-window-substring", "tier": "Advanced Differentiator", "companies": ["Meta", "Amazon", "Google", "LinkedIn"]},
        {"leetcode_id": 239, "title": "Sliding Window Maximum", "difficulty": "Hard", "slug": "sliding-window-maximum", "tier": "Advanced Differentiator", "companies": ["Amazon", "Google", "Microsoft"]},
    ],
    "Prefix Sum": [
        {"leetcode_id": 303, "title": "Range Sum Query - Immutable", "difficulty": "Easy", "slug": "range-sum-query-immutable", "tier": "Warm-up", "companies": ["Meta", "Amazon"]},
        {"leetcode_id": 560, "title": "Subarray Sum Equals K", "difficulty": "Medium", "slug": "subarray-sum-equals-k", "tier": "Core Interview", "companies": ["Meta", "Google", "Amazon", "Microsoft"]},
        {"leetcode_id": 525, "title": "Contiguous Array", "difficulty": "Medium", "slug": "contiguous-array", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google"]},
        {"leetcode_id": 238, "title": "Product of Array Except Self", "difficulty": "Medium", "slug": "product-of-array-except-self", "tier": "Core Interview", "companies": ["Amazon", "Meta", "Google", "Microsoft", "Apple"]},
    ],
    "Binary Search": [
        {"leetcode_id": 704, "title": "Binary Search", "difficulty": "Easy", "slug": "binary-search", "tier": "Warm-up", "companies": ["Apple", "Microsoft", "Google"]},
        {"leetcode_id": 74, "title": "Search a 2D Matrix", "difficulty": "Medium", "slug": "search-a-2d-matrix", "tier": "Core Interview", "companies": ["Amazon", "Microsoft", "Meta"]},
        {"leetcode_id": 33, "title": "Search in Rotated Sorted Array", "difficulty": "Medium", "slug": "search-in-rotated-sorted-array", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google", "Microsoft"]},
        {"leetcode_id": 153, "title": "Find Minimum in Rotated Sorted Array", "difficulty": "Medium", "slug": "find-minimum-in-rotated-sorted-array", "tier": "Core Interview", "companies": ["Amazon", "Google", "Microsoft"]},
        {"leetcode_id": 875, "title": "Koko Eating Bananas", "difficulty": "Medium", "slug": "koko-eating-bananas", "tier": "Core Interview", "companies": ["Google", "Amazon", "Uber"]},
        {"leetcode_id": 4, "title": "Median of Two Sorted Arrays", "difficulty": "Hard", "slug": "median-of-two-sorted-arrays", "tier": "Advanced Differentiator", "companies": ["Google", "Amazon", "Meta", "Microsoft", "Apple"]},
    ],
    "Monotonic Stack": [
        {"leetcode_id": 496, "title": "Next Greater Element I", "difficulty": "Easy", "slug": "next-greater-element-i", "tier": "Warm-up", "companies": ["Amazon", "Meta"]},
        {"leetcode_id": 739, "title": "Daily Temperatures", "difficulty": "Medium", "slug": "daily-temperatures", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google"]},
        {"leetcode_id": 503, "title": "Next Greater Element II", "difficulty": "Medium", "slug": "next-greater-element-ii", "tier": "Core Interview", "companies": ["Google", "Amazon"]},
        {"leetcode_id": 84, "title": "Largest Rectangle in Histogram", "difficulty": "Hard", "slug": "largest-rectangle-in-histogram", "tier": "Advanced Differentiator", "companies": ["Amazon", "Google", "Meta"]},
        {"leetcode_id": 85, "title": "Maximal Rectangle", "difficulty": "Hard", "slug": "maximal-rectangle", "tier": "Advanced Differentiator", "companies": ["Google", "Apple", "Amazon"]},
    ],
    "Tree DFS": [
        {"leetcode_id": 104, "title": "Maximum Depth of Binary Tree", "difficulty": "Easy", "slug": "maximum-depth-of-binary-tree", "tier": "Warm-up", "companies": ["Amazon", "Google", "LinkedIn"]},
        {"leetcode_id": 226, "title": "Invert Binary Tree", "difficulty": "Easy", "slug": "invert-binary-tree", "tier": "Warm-up", "companies": ["Google", "Amazon", "Microsoft"]},
        {"leetcode_id": 100, "title": "Same Tree", "difficulty": "Easy", "slug": "same-tree", "tier": "Warm-up", "companies": ["Amazon", "Microsoft", "Google"]},
        {"leetcode_id": 236, "title": "Lowest Common Ancestor of a Binary Tree", "difficulty": "Medium", "slug": "lowest-common-ancestor-of-a-binary-tree", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Microsoft", "Google"]},
        {"leetcode_id": 124, "title": "Binary Tree Maximum Path Sum", "difficulty": "Hard", "slug": "binary-tree-maximum-path-sum", "tier": "Advanced Differentiator", "companies": ["Meta", "Amazon", "Google", "DoorDash"]},
    ],
    "Tree BFS": [
        {"leetcode_id": 102, "title": "Binary Tree Level Order Traversal", "difficulty": "Medium", "slug": "binary-tree-level-order-traversal", "tier": "Core Interview", "companies": ["Amazon", "Meta", "Microsoft"]},
        {"leetcode_id": 103, "title": "Binary Tree Zigzag Level Order Traversal", "difficulty": "Medium", "slug": "binary-tree-zigzag-level-order-traversal", "tier": "Core Interview", "companies": ["Amazon", "Microsoft", "Google"]},
        {"leetcode_id": 199, "title": "Binary Tree Right Side View", "difficulty": "Medium", "slug": "binary-tree-right-side-view", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Bloomberg"]},
        {"leetcode_id": 297, "title": "Serialize and Deserialize Binary Tree", "difficulty": "Hard", "slug": "serialize-and-deserialize-binary-tree", "tier": "Advanced Differentiator", "companies": ["Meta", "Amazon", "Google", "Microsoft"]},
    ],
    "Graph BFS": [
        {"leetcode_id": 200, "title": "Number of Islands", "difficulty": "Medium", "slug": "number-of-islands", "tier": "Core Interview", "companies": ["Amazon", "Google", "Meta", "Microsoft", "Apple"]},
        {"leetcode_id": 994, "title": "Rotting Oranges", "difficulty": "Medium", "slug": "rotting-oranges", "tier": "Core Interview", "companies": ["Amazon", "Microsoft", "Google", "Uber"]},
        {"leetcode_id": 286, "title": "Walls and Gates", "difficulty": "Medium", "slug": "walls-and-gates", "tier": "Core Interview", "companies": ["Meta", "Google", "Amazon"]},
        {"leetcode_id": 127, "title": "Word Ladder", "difficulty": "Hard", "slug": "word-ladder", "tier": "Advanced Differentiator", "companies": ["Amazon", "Google", "Meta"]},
    ],
    "Graph DFS": [
        {"leetcode_id": 133, "title": "Clone Graph", "difficulty": "Medium", "slug": "clone-graph", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google", "Microsoft"]},
        {"leetcode_id": 417, "title": "Pacific Atlantic Water Flow", "difficulty": "Medium", "slug": "pacific-atlantic-water-flow", "tier": "Core Interview", "companies": ["Google", "Amazon"]},
        {"leetcode_id": 695, "title": "Max Area of Island", "difficulty": "Medium", "slug": "max-area-of-island", "tier": "Core Interview", "companies": ["Amazon", "Meta", "DoorDash"]},
    ],
    "Topological Sort": [
        {"leetcode_id": 207, "title": "Course Schedule", "difficulty": "Medium", "slug": "course-schedule", "tier": "Core Interview", "companies": ["Amazon", "Google", "Meta", "Microsoft"]},
        {"leetcode_id": 210, "title": "Course Schedule II", "difficulty": "Medium", "slug": "course-schedule-ii", "tier": "Core Interview", "companies": ["Amazon", "Google", "Meta"]},
        {"leetcode_id": 269, "title": "Alien Dictionary", "difficulty": "Hard", "slug": "alien-dictionary", "tier": "Advanced Differentiator", "companies": ["Meta", "Google", "Airbnb"]},
    ],
    "Union Find": [
        {"leetcode_id": 684, "title": "Redundant Connection", "difficulty": "Medium", "slug": "redundant-connection", "tier": "Core Interview", "companies": ["Google", "Amazon"]},
        {"leetcode_id": 547, "title": "Number of Provinces", "difficulty": "Medium", "slug": "number-of-provinces", "tier": "Core Interview", "companies": ["Amazon", "Microsoft", "Google"]},
        {"leetcode_id": 128, "title": "Longest Consecutive Sequence", "difficulty": "Medium", "slug": "longest-consecutive-sequence", "tier": "Core Interview", "companies": ["Google", "Amazon", "Meta"]},
        {"leetcode_id": 305, "title": "Number of Islands II", "difficulty": "Hard", "slug": "number-of-islands-ii", "tier": "Advanced Differentiator", "companies": ["Google", "Amazon", "Uber"]},
    ],
    "1D DP": [
        {"leetcode_id": 70, "title": "Climbing Stairs", "difficulty": "Easy", "slug": "climbing-stairs", "tier": "Warm-up", "companies": ["Amazon", "Google", "Adobe"]},
        {"leetcode_id": 198, "title": "House Robber", "difficulty": "Medium", "slug": "house-robber", "tier": "Core Interview", "companies": ["Google", "Amazon", "Microsoft"]},
        {"leetcode_id": 213, "title": "House Robber II", "difficulty": "Medium", "slug": "house-robber-ii", "tier": "Core Interview", "companies": ["Amazon", "Google"]},
        {"leetcode_id": 300, "title": "Longest Increasing Subsequence", "difficulty": "Medium", "slug": "longest-increasing-subsequence", "tier": "Core Interview", "companies": ["Google", "Amazon", "Microsoft"]},
        {"leetcode_id": 322, "title": "Coin Change", "difficulty": "Medium", "slug": "coin-change", "tier": "Core Interview", "companies": ["Amazon", "Meta", "Google", "Microsoft"]},
        {"leetcode_id": 139, "title": "Word Break", "difficulty": "Medium", "slug": "word-break", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google", "Bloomberg"]},
    ],
    "2D DP": [
        {"leetcode_id": 62, "title": "Unique Paths", "difficulty": "Medium", "slug": "unique-paths", "tier": "Core Interview", "companies": ["Amazon", "Google", "Meta"]},
        {"leetcode_id": 1143, "title": "Longest Common Subsequence", "difficulty": "Medium", "slug": "longest-common-subsequence", "tier": "Core Interview", "companies": ["Amazon", "Microsoft"]},
        {"leetcode_id": 72, "title": "Edit Distance", "difficulty": "Hard", "slug": "edit-distance", "tier": "Advanced Differentiator", "companies": ["Google", "Amazon", "Microsoft"]},
        {"leetcode_id": 10, "title": "Regular Expression Matching", "difficulty": "Hard", "slug": "regular-expression-matching", "tier": "Advanced Differentiator", "companies": ["Meta", "Google", "Uber"]},
    ],
    "Knapsack": [
        {"leetcode_id": 416, "title": "Partition Equal Subset Sum", "difficulty": "Medium", "slug": "partition-equal-subset-sum", "tier": "Core Interview", "companies": ["Amazon", "Meta", "Google"]},
        {"leetcode_id": 494, "title": "Target Sum", "difficulty": "Medium", "slug": "target-sum", "tier": "Core Interview", "companies": ["Amazon", "Meta"]},
        {"leetcode_id": 518, "title": "Coin Change II", "difficulty": "Medium", "slug": "coin-change-ii", "tier": "Core Interview", "companies": ["Google", "Amazon"]},
    ],
    "Fast/Slow Pointers": [
        {"leetcode_id": 141, "title": "Linked List Cycle", "difficulty": "Easy", "slug": "linked-list-cycle", "tier": "Warm-up", "companies": ["Amazon", "Microsoft", "Apple"]},
        {"leetcode_id": 876, "title": "Middle of the Linked List", "difficulty": "Easy", "slug": "middle-of-the-linked-list", "tier": "Warm-up", "companies": ["Amazon", "Google"]},
        {"leetcode_id": 142, "title": "Linked List Cycle II", "difficulty": "Medium", "slug": "linked-list-cycle-ii", "tier": "Core Interview", "companies": ["Microsoft", "Amazon"]},
        {"leetcode_id": 287, "title": "Find the Duplicate Number", "difficulty": "Medium", "slug": "find-the-duplicate-number", "tier": "Core Interview", "companies": ["Amazon", "Microsoft", "Google"]},
    ],
    "List Reversal": [
        {"leetcode_id": 206, "title": "Reverse Linked List", "difficulty": "Easy", "slug": "reverse-linked-list", "tier": "Warm-up", "companies": ["Amazon", "Meta", "Google", "Apple", "Microsoft"]},
        {"leetcode_id": 92, "title": "Reverse Linked List II", "difficulty": "Medium", "slug": "reverse-linked-list-ii", "tier": "Core Interview", "companies": ["Amazon", "Meta", "Microsoft"]},
        {"leetcode_id": 25, "title": "Reverse Nodes in k-Group", "difficulty": "Hard", "slug": "reverse-nodes-in-k-group", "tier": "Advanced Differentiator", "companies": ["Microsoft", "Amazon", "Google"]},
    ],
    "Subsets": [
        {"leetcode_id": 78, "title": "Subsets", "difficulty": "Medium", "slug": "subsets", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google", "Bloomberg"]},
        {"leetcode_id": 90, "title": "Subsets II", "difficulty": "Medium", "slug": "subsets-ii", "tier": "Core Interview", "companies": ["Amazon", "Google"]},
    ],
    "Permutations": [
        {"leetcode_id": 46, "title": "Permutations", "difficulty": "Medium", "slug": "permutations", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google", "Microsoft"]},
        {"leetcode_id": 47, "title": "Permutations II", "difficulty": "Medium", "slug": "permutations-ii", "tier": "Core Interview", "companies": ["Amazon", "Google"]},
    ],
    "Frequency Map": [
        {"leetcode_id": 1, "title": "Two Sum", "difficulty": "Easy", "slug": "two-sum", "tier": "Warm-up", "companies": ["Amazon", "Google", "Meta", "Microsoft", "Apple", "Uber"]},
        {"leetcode_id": 242, "title": "Valid Anagram", "difficulty": "Easy", "slug": "valid-anagram", "tier": "Warm-up", "companies": ["Amazon", "Google", "Bloomberg"]},
        {"leetcode_id": 49, "title": "Group Anagrams", "difficulty": "Medium", "slug": "group-anagrams", "tier": "Core Interview", "companies": ["Amazon", "Meta", "Google", "Microsoft"]},
        {"leetcode_id": 347, "title": "Top K Frequent Elements", "difficulty": "Medium", "slug": "top-k-frequent-elements", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google"]},
    ],
    "Top-K": [
        {"leetcode_id": 215, "title": "Kth Largest Element in an Array", "difficulty": "Medium", "slug": "kth-largest-element-in-an-array", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google", "Microsoft"]},
        {"leetcode_id": 347, "title": "Top K Frequent Elements", "difficulty": "Medium", "slug": "top-k-frequent-elements", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google"]},
        {"leetcode_id": 973, "title": "K Closest Points to Origin", "difficulty": "Medium", "slug": "k-closest-points-to-origin", "tier": "Core Interview", "companies": ["Meta", "Amazon", "Google"]},
        {"leetcode_id": 295, "title": "Find Median from Data Stream", "difficulty": "Hard", "slug": "find-median-from-data-stream", "tier": "Advanced Differentiator", "companies": ["Google", "Amazon", "Microsoft", "Uber"]},
    ],
    "Prefix Search": [
        {"leetcode_id": 208, "title": "Implement Trie (Prefix Tree)", "difficulty": "Medium", "slug": "implement-trie-prefix-tree", "tier": "Core Interview", "companies": ["Google", "Amazon", "Meta", "Twitter"]},
        {"leetcode_id": 211, "title": "Design Add and Search Words Data Structure", "difficulty": "Medium", "slug": "design-add-and-search-words-data-structure", "tier": "Core Interview", "companies": ["Meta", "Amazon"]},
        {"leetcode_id": 212, "title": "Word Search II", "difficulty": "Hard", "slug": "word-search-ii", "tier": "Advanced Differentiator", "companies": ["Amazon", "Google", "Meta", "Uber"]},
    ],
}

# Grouping map: Topic Name -> list of Pattern Names
TOPIC_GROUPS: dict[str, list[str]] = {
    "Arrays & Strings": ["Two Pointers", "Sliding Window", "Prefix Sum", "Frequency Map"],
    "Binary Search": ["Binary Search"],
    "Stacks & Queues": ["Monotonic Stack"],
    "Linked Lists": ["Fast/Slow Pointers", "List Reversal"],
    "Trees & Tries": ["Tree DFS", "Tree BFS", "Prefix Search"],
    "Graphs": ["Graph BFS", "Graph DFS", "Topological Sort", "Union Find"],
    "Dynamic Programming": ["1D DP", "2D DP", "Knapsack"],
    "Backtracking": ["Subsets", "Permutations"],
    "Heaps & Priority Queues": ["Top-K"],
}


def compute_pattern_practice(
    username: str,
    solved: list[UserSolvedProblem],
    user: User | None = None,
) -> dict:
    """
    Computes curated practice roadmaps with Company Tags & Spaced Repetition.
    """
    now = datetime.now(timezone.utc)

    # Build solved lookup: slug/id -> last_solved_at
    solved_date_by_slug: dict[str, datetime | None] = {}
    solved_date_by_id: dict[int, datetime | None] = {}
    for usp in solved:
        p = usp.problem
        solved_date_by_slug[p.slug] = usp.last_solved_at
        if p.leetcode_id > 0:
            solved_date_by_id[p.leetcode_id] = usp.last_solved_at

    # Taxonomy lookup: pattern -> topic
    pattern_to_topic = {}
    pattern_to_desc = {}
    for entry in TAXONOMY:
        pattern_to_topic[entry.pattern] = entry.parent.title().replace("-", " ")
        pattern_to_desc[entry.pattern] = entry.description

    patterns_out = []
    total_curated_problems = 0
    total_user_solved_curated = 0
    total_needs_revision = 0
    revision_queue = []

    all_pattern_names = list(PATTERN_PRACTICE_CURRICULUM.keys())

    for pname in all_pattern_names:
        problems_list = PATTERN_PRACTICE_CURRICULUM[pname]
        parent_topic = pattern_to_topic.get(pname, "Algorithmic Patterns")
        desc = pattern_to_desc.get(pname, f"Curated practice problems for {pname}")

        pattern_solved_count = 0
        enriched_problems = []

        for prob in problems_list:
            total_curated_problems += 1
            slug = prob["slug"]
            lid = prob["leetcode_id"]

            is_solved = (slug in solved_date_by_slug) or (lid in solved_date_by_id)
            solved_at = solved_date_by_slug.get(slug) or solved_date_by_id.get(lid)

            # Spaced Repetition calculation
            days_ago = None
            needs_revision = False
            revision_status = "Unsolved"

            if is_solved:
                pattern_solved_count += 1
                total_user_solved_curated += 1

                if solved_at:
                    if solved_at.tzinfo is None:
                        solved_at = solved_at.replace(tzinfo=timezone.utc)
                    days_ago = max(0, (now - solved_at).days)
                    # If solved > 21 days ago, flag for spaced repetition revision
                    if days_ago >= 21:
                        needs_revision = True
                        revision_status = f"Needs Revision ({days_ago}d ago)"
                        total_needs_revision += 1
                        revision_queue.append({
                            "leetcode_id": lid,
                            "title": prob["title"],
                            "difficulty": prob["difficulty"],
                            "slug": slug,
                            "pattern": pname,
                            "days_ago": days_ago,
                            "url": f"https://leetcode.com/problems/{slug}/",
                        })
                    elif days_ago >= 7:
                        revision_status = f"Good ({days_ago}d ago)"
                    else:
                        revision_status = "Fresh (< 7d)"
                else:
                    revision_status = "Solved"

            enriched_problems.append({
                "leetcode_id": lid,
                "title": prob["title"],
                "difficulty": prob["difficulty"],
                "slug": slug,
                "url": f"https://leetcode.com/problems/{slug}/",
                "tier": prob.get("tier", "Core Interview"),
                "companies": prob.get("companies", ["Top Tech"]),
                "is_solved": is_solved,
                "needs_revision": needs_revision,
                "revision_status": revision_status,
                "days_since_solved": days_ago,
            })

        total_p = len(enriched_problems)
        completion_pct = round((pattern_solved_count / max(total_p, 1)) * 100)

        patterns_out.append({
            "pattern_name": pname,
            "pattern_slug": pname.lower().replace(" ", "-").replace("/", "-"),
            "parent_topic": parent_topic,
            "description": desc,
            "total_problems": total_p,
            "solved_count": pattern_solved_count,
            "completion_pct": completion_pct,
            "problems": enriched_problems,
        })

    # Build Topic Groups
    topic_groups_out = []
    pattern_by_name = {p["pattern_name"]: p for p in patterns_out}

    for group_name, pnames in TOPIC_GROUPS.items():
        group_patterns = [pattern_by_name[pn] for pn in pnames if pn in pattern_by_name]
        total_p_group = sum(p["total_problems"] for p in group_patterns)
        solved_p_group = sum(p["solved_count"] for p in group_patterns)
        topic_groups_out.append({
            "topic_group": group_name,
            "patterns": group_patterns,
            "total_problems": total_p_group,
            "solved_count": solved_p_group,
            "completion_pct": round((solved_p_group / max(total_p_group, 1)) * 100),
        })

    # Sort revision queue most overdue first
    revision_queue.sort(key=lambda x: x["days_ago"], reverse=True)

    return {
        "username": username,
        "total_patterns": len(patterns_out),
        "total_curated_problems": total_curated_problems,
        "total_user_solved_curated": total_user_solved_curated,
        "overall_completion_pct": round((total_user_solved_curated / max(total_curated_problems, 1)) * 100),
        "total_needs_revision": total_needs_revision,
        "revision_queue": revision_queue[:10],
        "topic_groups": topic_groups_out,
        "patterns": patterns_out,
    }
