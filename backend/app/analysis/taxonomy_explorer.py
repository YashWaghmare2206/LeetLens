"""
Analysis Engine — Taxonomy Explorer (Hierarchical Topic → Pattern Breakdown)
Segregates DSA patterns under their parent topics (e.g. Array → Two Pointers, Sliding Window, Prefix Sum).
Provides per-pattern mastery metrics, solved problems, and recommended problems to solve next.
"""
from __future__ import annotations
import json
from collections import defaultdict
from typing import TYPE_CHECKING
from app.models.problem import UserSolvedProblem, Difficulty
from app.data.taxonomy import TOPICS, TAXONOMY, PROBLEM_PATTERNS

if TYPE_CHECKING:
    from app.models.user import User

# Standard interview problem recommendations by pattern name (canonical LeetCode problems)
PATTERN_RECOMMENDED_PROBLEMS: dict[str, list[dict]] = {
    "Two Pointers": [
        {"leetcode_id": 167, "title": "Two Sum II - Input Array Is Sorted", "difficulty": "Medium", "slug": "two-sum-ii-input-array-is-sorted"},
        {"leetcode_id": 15, "title": "3Sum", "difficulty": "Medium", "slug": "3sum"},
        {"leetcode_id": 11, "title": "Container With Most Water", "difficulty": "Medium", "slug": "container-with-most-water"},
        {"leetcode_id": 42, "title": "Trapping Rain Water", "difficulty": "Hard", "slug": "trapping-rain-water"},
    ],
    "Sliding Window": [
        {"leetcode_id": 3, "title": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "slug": "longest-substring-without-repeating-characters"},
        {"leetcode_id": 76, "title": "Minimum Window Substring", "difficulty": "Hard", "slug": "minimum-window-substring"},
        {"leetcode_id": 424, "title": "Longest Repeating Character Replacement", "difficulty": "Medium", "slug": "longest-repeating-character-replacement"},
        {"leetcode_id": 209, "title": "Minimum Size Subarray Sum", "difficulty": "Medium", "slug": "minimum-size-subarray-sum"},
    ],
    "Prefix Sum": [
        {"leetcode_id": 560, "title": "Subarray Sum Equals K", "difficulty": "Medium", "slug": "subarray-sum-equals-k"},
        {"leetcode_id": 525, "title": "Contiguous Array", "difficulty": "Medium", "slug": "contiguous-array"},
        {"leetcode_id": 238, "title": "Product of Array Except Self", "difficulty": "Medium", "slug": "product-of-array-except-self"},
    ],
    "Binary Search": [
        {"leetcode_id": 704, "title": "Binary Search", "difficulty": "Easy", "slug": "binary-search"},
        {"leetcode_id": 33, "title": "Search in Rotated Sorted Array", "difficulty": "Medium", "slug": "search-in-rotated-sorted-array"},
        {"leetcode_id": 875, "title": "Koko Eating Bananas", "difficulty": "Medium", "slug": "koko-eating-bananas"},
        {"leetcode_id": 4, "title": "Median of Two Sorted Arrays", "difficulty": "Hard", "slug": "median-of-two-sorted-arrays"},
    ],
    "Monotonic Stack": [
        {"leetcode_id": 739, "title": "Daily Temperatures", "difficulty": "Medium", "slug": "daily-temperatures"},
        {"leetcode_id": 84, "title": "Largest Rectangle in Histogram", "difficulty": "Hard", "slug": "largest-rectangle-in-histogram"},
        {"leetcode_id": 85, "title": "Maximal Rectangle", "difficulty": "Hard", "slug": "maximal-rectangle"},
    ],
    "Tree DFS": [
        {"leetcode_id": 104, "title": "Maximum Depth of Binary Tree", "difficulty": "Easy", "slug": "maximum-depth-of-binary-tree"},
        {"leetcode_id": 226, "title": "Invert Binary Tree", "difficulty": "Easy", "slug": "invert-binary-tree"},
        {"leetcode_id": 124, "title": "Binary Tree Maximum Path Sum", "difficulty": "Hard", "slug": "binary-tree-maximum-path-sum"},
    ],
    "Tree BFS": [
        {"leetcode_id": 102, "title": "Binary Tree Level Order Traversal", "difficulty": "Medium", "slug": "binary-tree-level-order-traversal"},
        {"leetcode_id": 103, "title": "Binary Tree Zigzag Level Order Traversal", "difficulty": "Medium", "slug": "binary-tree-zigzag-level-order-traversal"},
        {"leetcode_id": 199, "title": "Binary Tree Right Side View", "difficulty": "Medium", "slug": "binary-tree-right-side-view"},
    ],
    "Graph BFS": [
        {"leetcode_id": 200, "title": "Number of Islands", "difficulty": "Medium", "slug": "number-of-islands"},
        {"leetcode_id": 127, "title": "Word Ladder", "difficulty": "Hard", "slug": "word-ladder"},
        {"leetcode_id": 994, "title": "Rotting Oranges", "difficulty": "Medium", "slug": "rotting-oranges"},
    ],
    "Graph DFS": [
        {"leetcode_id": 133, "title": "Clone Graph", "difficulty": "Medium", "slug": "clone-graph"},
        {"leetcode_id": 417, "title": "Pacific Atlantic Water Flow", "difficulty": "Medium", "slug": "pacific-atlantic-water-flow"},
        {"leetcode_id": 207, "title": "Course Schedule", "difficulty": "Medium", "slug": "course-schedule"},
    ],
    "Topological Sort": [
        {"leetcode_id": 207, "title": "Course Schedule", "difficulty": "Medium", "slug": "course-schedule"},
        {"leetcode_id": 210, "title": "Course Schedule II", "difficulty": "Medium", "slug": "course-schedule-ii"},
        {"leetcode_id": 269, "title": "Alien Dictionary", "difficulty": "Hard", "slug": "alien-dictionary"},
    ],
    "Union Find": [
        {"leetcode_id": 684, "title": "Redundant Connection", "difficulty": "Medium", "slug": "redundant-connection"},
        {"leetcode_id": 547, "title": "Number of Provinces", "difficulty": "Medium", "slug": "number-of-provinces"},
        {"leetcode_id": 128, "title": "Longest Consecutive Sequence", "difficulty": "Medium", "slug": "longest-consecutive-sequence"},
    ],
    "1D DP": [
        {"leetcode_id": 70, "title": "Climbing Stairs", "difficulty": "Easy", "slug": "climbing-stairs"},
        {"leetcode_id": 198, "title": "House Robber", "difficulty": "Medium", "slug": "house-robber"},
        {"leetcode_id": 300, "title": "Longest Increasing Subsequence", "difficulty": "Medium", "slug": "longest-increasing-subsequence"},
        {"leetcode_id": 322, "title": "Coin Change", "difficulty": "Medium", "slug": "coin-change"},
    ],
    "2D DP": [
        {"leetcode_id": 62, "title": "Unique Paths", "difficulty": "Medium", "slug": "unique-paths"},
        {"leetcode_id": 1143, "title": "Longest Common Subsequence", "difficulty": "Medium", "slug": "longest-common-subsequence"},
        {"leetcode_id": 72, "title": "Edit Distance", "difficulty": "Hard", "slug": "edit-distance"},
    ],
    "Knapsack": [
        {"leetcode_id": 416, "title": "Partition Equal Subset Sum", "difficulty": "Medium", "slug": "partition-equal-subset-sum"},
        {"leetcode_id": 494, "title": "Target Sum", "difficulty": "Medium", "slug": "target-sum"},
        {"leetcode_id": 518, "title": "Coin Change II", "difficulty": "Medium", "slug": "coin-change-ii"},
    ],
    "Subsets": [
        {"leetcode_id": 78, "title": "Subsets", "difficulty": "Medium", "slug": "subsets"},
        {"leetcode_id": 90, "title": "Subsets II", "difficulty": "Medium", "slug": "subsets-ii"},
    ],
    "Permutations": [
        {"leetcode_id": 46, "title": "Permutations", "difficulty": "Medium", "slug": "permutations"},
        {"leetcode_id": 47, "title": "Permutations II", "difficulty": "Medium", "slug": "permutations-ii"},
    ],
    "Fast/Slow Pointers": [
        {"leetcode_id": 141, "title": "Linked List Cycle", "difficulty": "Easy", "slug": "linked-list-cycle"},
        {"leetcode_id": 142, "title": "Linked List Cycle II", "difficulty": "Medium", "slug": "linked-list-cycle-ii"},
        {"leetcode_id": 876, "title": "Middle of the Linked List", "difficulty": "Easy", "slug": "middle-of-the-linked-list"},
    ],
    "List Reversal": [
        {"leetcode_id": 206, "title": "Reverse Linked List", "difficulty": "Easy", "slug": "reverse-linked-list"},
        {"leetcode_id": 92, "title": "Reverse Linked List II", "difficulty": "Medium", "slug": "reverse-linked-list-ii"},
        {"leetcode_id": 25, "title": "Reverse Nodes in k-Group", "difficulty": "Hard", "slug": "reverse-nodes-in-k-group"},
    ],
    "Matrix Traversal": [
        {"leetcode_id": 54, "title": "Spiral Matrix", "difficulty": "Medium", "slug": "spiral-matrix"},
        {"leetcode_id": 73, "title": "Set Matrix Zeroes", "difficulty": "Medium", "slug": "set-matrix-zeroes"},
        {"leetcode_id": 48, "title": "Rotate Image", "difficulty": "Medium", "slug": "rotate-image"},
        {"leetcode_id": 240, "title": "Search a 2D Matrix II", "difficulty": "Medium", "slug": "search-a-2d-matrix-ii"},
    ],
    "In-Place Matrix Transformation": [
        {"leetcode_id": 48, "title": "Rotate Image", "difficulty": "Medium", "slug": "rotate-image"},
        {"leetcode_id": 73, "title": "Set Matrix Zeroes", "difficulty": "Medium", "slug": "set-matrix-zeroes"},
        {"leetcode_id": 289, "title": "Game of Life", "difficulty": "Medium", "slug": "game-of-life"},
    ],
    "2D Grid Search": [
        {"leetcode_id": 200, "title": "Number of Islands", "difficulty": "Medium", "slug": "number-of-islands"},
        {"leetcode_id": 695, "title": "Max Area of Island", "difficulty": "Medium", "slug": "max-area-of-island"},
        {"leetcode_id": 79, "title": "Word Search", "difficulty": "Medium", "slug": "word-search"},
    ],
    "Direct State Simulation": [
        {"leetcode_id": 657, "title": "Robot Return to Origin", "difficulty": "Easy", "slug": "robot-return-to-origin"},
        {"leetcode_id": 289, "title": "Game of Life", "difficulty": "Medium", "slug": "game-of-life"},
        {"leetcode_id": 68, "title": "Text Justification", "difficulty": "Hard", "slug": "text-justification"},
    ],
    "Rule-Based Grid Walking": [
        {"leetcode_id": 1041, "title": "Robot Bounded In Circle", "difficulty": "Medium", "slug": "robot-bounded-in-circle"},
        {"leetcode_id": 54, "title": "Spiral Matrix", "difficulty": "Medium", "slug": "spiral-matrix"},
    ],
    "Custom Comparator Sorting": [
        {"leetcode_id": 179, "title": "Largest Number", "difficulty": "Medium", "slug": "largest-number"},
        {"leetcode_id": 56, "title": "Merge Intervals", "difficulty": "Medium", "slug": "merge-intervals"},
        {"leetcode_id": 451, "title": "Sort Characters By Frequency", "difficulty": "Medium", "slug": "sort-characters-by-frequency"},
    ],
    "In-Place & Bucket Sort": [
        {"leetcode_id": 75, "title": "Sort Colors", "difficulty": "Medium", "slug": "sort-colors"},
        {"leetcode_id": 41, "title": "First Missing Positive", "difficulty": "Hard", "slug": "first-missing-positive"},
    ],
    "Tree DFS Traversal": [
        {"leetcode_id": 104, "title": "Maximum Depth of Binary Tree", "difficulty": "Easy", "slug": "maximum-depth-of-binary-tree"},
        {"leetcode_id": 543, "title": "Diameter of Binary Tree", "difficulty": "Easy", "slug": "diameter-of-binary-tree"},
        {"leetcode_id": 236, "title": "Lowest Common Ancestor of a Binary Tree", "difficulty": "Medium", "slug": "lowest-common-ancestor-of-a-binary-tree"},
    ],
    "Tree Level-Order BFS": [
        {"leetcode_id": 102, "title": "Binary Tree Level Order Traversal", "difficulty": "Medium", "slug": "binary-tree-level-order-traversal"},
        {"leetcode_id": 199, "title": "Binary Tree Right Side View", "difficulty": "Medium", "slug": "binary-tree-right-side-view"},
    ],
    "Opposite-Direction Two Pointers": [
        {"leetcode_id": 167, "title": "Two Sum II - Input Array Is Sorted", "difficulty": "Medium", "slug": "two-sum-ii-input-array-is-sorted"},
        {"leetcode_id": 15, "title": "3Sum", "difficulty": "Medium", "slug": "3sum"},
        {"leetcode_id": 11, "title": "Container With Most Water", "difficulty": "Medium", "slug": "container-with-most-water"},
    ],
    "Same-Direction Fast & Slow": [
        {"leetcode_id": 26, "title": "Remove Duplicates from Sorted Array", "difficulty": "Easy", "slug": "remove-duplicates-from-sorted-array"},
        {"leetcode_id": 283, "title": "Move Zeroes", "difficulty": "Easy", "slug": "move-zeroes"},
    ],
    "Fixed-Size Sliding Window": [
        {"leetcode_id": 643, "title": "Maximum Average Subarray I", "difficulty": "Easy", "slug": "maximum-average-subarray-i"},
        {"leetcode_id": 438, "title": "Find All Anagrams in a String", "difficulty": "Medium", "slug": "find-all-anagrams-in-a-string"},
    ],
    "Variable-Size Sliding Window": [
        {"leetcode_id": 3, "title": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "slug": "longest-substring-without-repeating-characters"},
        {"leetcode_id": 209, "title": "Minimum Size Subarray Sum", "difficulty": "Medium", "slug": "minimum-size-subarray-sum"},
    ],
    "Direct Binary Search": [
        {"leetcode_id": 704, "title": "Binary Search", "difficulty": "Easy", "slug": "binary-search"},
        {"leetcode_id": 33, "title": "Search in Rotated Sorted Array", "difficulty": "Medium", "slug": "search-in-rotated-sorted-array"},
        {"leetcode_id": 153, "title": "Find Minimum in Rotated Sorted Array", "difficulty": "Medium", "slug": "find-minimum-in-rotated-sorted-array"},
    ],
    "Binary Search on Answer Range": [
        {"leetcode_id": 875, "title": "Koko Eating Bananas", "difficulty": "Medium", "slug": "koko-eating-bananas"},
        {"leetcode_id": 1011, "title": "Capacity To Ship Packages Within D Days", "difficulty": "Medium", "slug": "capacity-to-ship-packages-within-d-days"},
    ],
    "Divide & Subproblem Recursion": [
        {"leetcode_id": 50, "title": "Pow(x, n)", "difficulty": "Medium", "slug": "powx-n"},
        {"leetcode_id": 779, "title": "K-th Symbol in Grammar", "difficulty": "Medium", "slug": "k-th-symbol-in-grammar"},
    ],
    "Binary Divide & Conquer": [
        {"leetcode_id": 108, "title": "Convert Sorted Array to Binary Search Tree", "difficulty": "Easy", "slug": "convert-sorted-array-to-binary-search-tree"},
        {"leetcode_id": 23, "title": "Merge k Sorted Lists", "difficulty": "Hard", "slug": "merge-k-sorted-lists"},
    ],
    "Disjoint Set Connectivity": [
        {"leetcode_id": 684, "title": "Redundant Connection", "difficulty": "Medium", "slug": "redundant-connection"},
        {"leetcode_id": 547, "title": "Number of Provinces", "difficulty": "Medium", "slug": "number-of-provinces"},
    ],
    "Sliding Window Extrema": [
        {"leetcode_id": 239, "title": "Sliding Window Maximum", "difficulty": "Hard", "slug": "sliding-window-maximum"},
    ],
    "K-th Order Statistic": [
        {"leetcode_id": 215, "title": "Kth Largest Element in an Array", "difficulty": "Medium", "slug": "kth-largest-element-in-an-array"},
        {"leetcode_id": 973, "title": "K Closest Points to Origin", "difficulty": "Medium", "slug": "k-closest-points-to-origin"},
    ],
    "Minimax & Nim Game": [
        {"leetcode_id": 292, "title": "Nim Game", "difficulty": "Easy", "slug": "nim-game"},
        {"leetcode_id": 877, "title": "Stone Game", "difficulty": "Medium", "slug": "stone-game"},
    ],
    "Dijkstra & Weighted Paths": [
        {"leetcode_id": 743, "title": "Network Delay Time", "difficulty": "Medium", "slug": "network-delay-time"},
        {"leetcode_id": 787, "title": "Cheapest Flights Within K Stops", "difficulty": "Medium", "slug": "cheapest-flights-within-k-stops"},
    ],
}

TOPIC_ICONS: dict[str, str] = {
    "array": "ARRAY",
    "string": "STRING",
    "hash-table": "HASH",
    "linked-list": "LIST",
    "stack": "STACK",
    "tree": "TREE",
    "graph": "GRAPH",
    "dynamic-programming": "DP",
    "greedy": "GREEDY",
    "backtracking": "BACKTRACK",
    "heap": "HEAP",
    "trie": "TRIE",
    "bit-manipulation": "BIT",
    "math": "MATH",
    "design": "DESIGN",
    "matrix": "MATRIX",
    "simulation": "SIMULATION",
    "sorting": "SORT",
    "binary-tree": "BIN-TREE",
    "two-pointers": "2-POINTERS",
    "sliding-window": "SLIDING-WIN",
    "binary-search": "BIN-SEARCH",
    "recursion": "RECURSION",
    "divide-and-conquer": "DIV-CONQ",
    "depth-first-search": "DFS",
    "breadth-first-search": "BFS",
    "union-find": "UNION-FIND",
    "monotonic-stack": "MONO-STACK",
    "monotonic-queue": "MONO-QUEUE",
    "quickselect": "QUICKSELECT",
    "game-theory": "GAME",
    "enumeration": "ENUM",
    "rolling-hash": "ROLLING-HASH",
    "ordered-set": "ORDERED-SET",
    "shortest-path": "SHORTEST-PATH",
    "data-stream": "STREAM",
    "randomized": "RANDOM",
    "combinatorics": "COMB",
}


def _mastery_level(count: int) -> str:
    if count >= 10:
        return "Mastered"
    elif count >= 4:
        return "Proficient"
    elif count >= 1:
        return "Practiced"
    return "Untouched"


def compute_taxonomy_explorer(
    username: str,
    solved: list[UserSolvedProblem],
    user: User | None = None,
) -> dict:
    """Computes a nested hierarchy: Topics → Patterns → Solved Problems + Recommendations."""

    # 1. Tally problems per pattern from user solved problems
    pattern_stats: dict[str, dict] = defaultdict(lambda: {
        "solved_count": 0,
        "easy": 0,
        "medium": 0,
        "hard": 0,
        "problems": [],
    })

    # Track which problem slugs are already recorded per pattern
    recorded_slugs: dict[str, set[str]] = defaultdict(set)

    for usp in solved:
        p = usp.problem
        diff = p.difficulty
        prob_dict = {
            "leetcode_id": p.leetcode_id,
            "title": p.title,
            "slug": p.slug,
            "difficulty": p.difficulty.value,
            "url": p.url or f"https://leetcode.com/problems/{p.slug}/",
        }

        # Associate with verified pattern annotations
        for pp in p.patterns:
            name = pp.pattern.name
            if p.slug not in recorded_slugs[name]:
                recorded_slugs[name].add(p.slug)
                pattern_stats[name]["solved_count"] += 1
                if diff == Difficulty.EASY:
                    pattern_stats[name]["easy"] += 1
                elif diff == Difficulty.MEDIUM:
                    pattern_stats[name]["medium"] += 1
                elif diff == Difficulty.HARD:
                    pattern_stats[name]["hard"] += 1
                pattern_stats[name]["problems"].append(prob_dict)

        # Also associate with topic parent patterns from problem.topics
        for pt in p.topics:
            tslug = pt.topic.slug
            if tslug == "hashing":
                tslug = "hash-table"
            elif tslug == "heap-priority-queue":
                tslug = "heap"
            elif tslug == "graph-theory":
                tslug = "graph"

            tax_patterns = [e.pattern for e in TAXONOMY if e.parent == tslug]
            if tax_patterns:
                primary_pname = tax_patterns[0]
                if p.slug not in recorded_slugs[primary_pname]:
                    recorded_slugs[primary_pname].add(p.slug)
                    pattern_stats[primary_pname]["solved_count"] += 1
                    if diff == Difficulty.EASY:
                        pattern_stats[primary_pname]["easy"] += 1
                    elif diff == Difficulty.MEDIUM:
                        pattern_stats[primary_pname]["medium"] += 1
                    elif diff == Difficulty.HARD:
                        pattern_stats[primary_pname]["hard"] += 1
                    pattern_stats[primary_pname]["problems"].append(prob_dict)

    # 2. Correlate with LeetCode verified skills if available
    skill_map: dict[str, int] = {}
    skill_names: dict[str, str] = {}
    if user and user.skill_stats_json:
        try:
            skills = json.loads(user.skill_stats_json)
            for item in skills:
                slug = item.get("tag_slug", "")
                name = item.get("tag_name", "")
                cnt = item.get("problems_solved", 0)
                if slug and cnt > 0:
                    # Normalize alias slugs
                    norm_slug = "hash-table" if slug == "hashing" else ("heap" if slug == "heap-priority-queue" else ("graph" if slug == "graph-theory" else slug))
                    skill_map[norm_slug] = cnt
                    skill_names[norm_slug] = name
        except Exception:
            pass

    # Direct skill tag to pattern mapping
    tag_to_patterns = {
        "two-pointers": ["Opposite-Direction Two Pointers", "Same-Direction Fast & Slow", "Two Pointers", "String Two Pointers"],
        "sliding-window": ["Fixed-Size Sliding Window", "Variable-Size Sliding Window", "Sliding Window", "String Sliding Window"],
        "binary-search": ["Direct Binary Search", "Binary Search on Answer Range", "Binary Search"],
        "monotonic-stack": ["Next Greater Element", "Monotonic Stack"],
        "dynamic-programming": ["1D DP", "2D DP", "Knapsack", "Subsequence DP"],
        "depth-first-search": ["Graph & Tree DFS", "Tree DFS", "Graph DFS"],
        "breadth-first-search": ["Shortest Path BFS", "Tree BFS", "Graph BFS"],
        "union-find": ["Disjoint Set Connectivity", "Union Find"],
        "backtracking": ["Subsets", "Permutations", "Combinations"],
        "trie": ["Prefix Search", "Word Search"],
        "bit-manipulation": ["XOR", "Bit Counting", "Bitmask"],
        "math": ["Number Theory", "Combinatorics"],
        "heap": ["Top-K", "Two Heaps"],
        "greedy": ["Interval Greedy", "Local Choice"],
        "matrix": ["Matrix Traversal", "In-Place Matrix Transformation", "2D Grid Search"],
        "simulation": ["Direct State Simulation", "Rule-Based Grid Walking"],
        "sorting": ["Custom Comparator Sorting", "In-Place & Bucket Sort"],
        "binary-tree": ["Tree DFS Traversal", "Tree Level-Order BFS"],
        "recursion": ["Divide & Subproblem Recursion", "Backtracking Recursion"],
        "divide-and-conquer": ["Binary Divide & Conquer", "Expression & Tree Partition"],
        "monotonic-queue": ["Sliding Window Extrema"],
        "quickselect": ["K-th Order Statistic"],
        "game-theory": ["Minimax & Nim Game"],
    }

    for tag, patterns in tag_to_patterns.items():
        if tag in skill_map:
            total_tag = skill_map[tag]
            for pname in patterns:
                if pname not in pattern_stats or pattern_stats[pname]["solved_count"] < total_tag:
                    pattern_stats[pname]["solved_count"] = max(pattern_stats[pname]["solved_count"], total_tag)

    # 3. Assemble hierarchy based on TOPICS + any extra topics present in skill_map
    topics_out = []
    total_patterns_mastered = 0
    total_patterns_count = 0

    # Build known topics dictionary
    all_topics_dict: dict[str, tuple[str, str, str]] = {}
    for t_slug, t_name, t_desc in TOPICS:
        all_topics_dict[t_slug] = (t_slug, t_name, t_desc)

    # Include any extra verified LeetCode skill tags not in TOPICS
    for s_slug, s_cnt in skill_map.items():
        if s_slug not in all_topics_dict:
            display_name = skill_names.get(s_slug, s_slug.replace("-", " ").title())
            all_topics_dict[s_slug] = (s_slug, display_name, f"Interview problems applying {display_name} techniques")

    for topic_slug, topic_name, topic_desc in all_topics_dict.values():
        # Find all taxonomy patterns belonging to this topic
        topic_patterns_entries = [e for e in TAXONOMY if e.parent == topic_slug]
        patterns_list = []
        topic_solved_sum = 0

        # If topic has no taxonomy entry yet, generate a canonical pattern
        if not topic_patterns_entries:
            canon_pname = f"{topic_name} Patterns"
            p_data = pattern_stats[canon_pname]
            p_count = max(p_data["solved_count"], skill_map.get(topic_slug, 0))
            topic_solved_sum = p_count
            mastery = _mastery_level(p_count)
            if mastery in ("Mastered", "Proficient"):
                total_patterns_mastered += 1
            total_patterns_count += 1
            patterns_list.append({
                "pattern_name": canon_pname,
                "pattern_slug": canon_pname.lower().replace(" ", "-"),
                "description": topic_desc,
                "solved_count": p_count,
                "mastery": mastery,
                "easy": p_data["easy"],
                "medium": p_data["medium"],
                "hard": p_data["hard"],
                "problems": p_data["problems"],
                "recommended_problems": PATTERN_RECOMMENDED_PROBLEMS.get(canon_pname, []),
            })
        else:
            for entry in topic_patterns_entries:
                total_patterns_count += 1
                pname = entry.pattern
                p_data = pattern_stats[pname]
                count = p_data["solved_count"]
                topic_solved_sum += count

                mastery = _mastery_level(count)
                if mastery in ("Mastered", "Proficient"):
                    total_patterns_mastered += 1

                recs = PATTERN_RECOMMENDED_PROBLEMS.get(pname, [])
                solved_slugs = {p["slug"] for p in p_data["problems"]}
                unsolved_recs = [r for r in recs if r["slug"] not in solved_slugs]

                patterns_list.append({
                    "pattern_name": pname,
                    "pattern_slug": entry.pattern.lower().replace(" ", "-").replace("/", "-"),
                    "description": entry.description,
                    "solved_count": count,
                    "mastery": mastery,
                    "easy": p_data["easy"],
                    "medium": p_data["medium"],
                    "hard": p_data["hard"],
                    "problems": p_data["problems"],
                    "recommended_problems": unsolved_recs if unsolved_recs else recs,
                })

        # Check if user has tag stats for this topic slug directly
        direct_tag_solved = skill_map.get(topic_slug, 0)
        final_topic_solved = max(topic_solved_sum, direct_tag_solved)

        # Sort patterns by solved_count descending
        patterns_list.sort(key=lambda p: (p["solved_count"], p["pattern_name"]), reverse=True)

        topics_out.append({
            "topic_slug": topic_slug,
            "topic_name": topic_name,
            "description": topic_desc,
            "icon": TOPIC_ICONS.get(topic_slug, topic_slug[:4].upper()),
            "solved_count": final_topic_solved,
            "patterns_count": len(patterns_list),
            "patterns_mastered": sum(1 for p in patterns_list if p["mastery"] in ("Mastered", "Proficient")),
            "patterns": patterns_list,
        })

    # Prioritize topics where user has solved problems first (descending by solved_count)
    topics_out.sort(key=lambda t: (t["solved_count"] > 0, t["solved_count"], t["topic_name"]), reverse=True)

    return {
        "username": username,
        "total_topics": len(topics_out),
        "total_patterns": total_patterns_count,
        "mastered_patterns": total_patterns_mastered,
        "topics": topics_out,
    }
