"""
Tests for the analysis engine — the core of LeetLens.
These are pure-logic tests (no DB, no HTTP).
"""
import pytest
from unittest.mock import MagicMock
from app.models.problem import Difficulty, UserSolvedProblem, Problem, ProblemPattern, Pattern, ProblemTopic, Topic
from app.analysis.overview import compute_overview
from app.analysis.topics import compute_topics
from app.analysis.patterns import compute_patterns, compute_pattern_detail
from app.analysis.coverage import compute_coverage


def _make_problem(
    lid: int,
    title: str,
    slug: str,
    difficulty: Difficulty = Difficulty.MEDIUM,
    patterns: list[str] = None,
    topics: list[str] = None,
) -> Problem:
    p = MagicMock(spec=Problem)
    p.leetcode_id = lid
    p.title = title
    p.slug = slug
    p.difficulty = difficulty
    p.url = f"https://leetcode.com/problems/{slug}/"

    # Build patterns
    p.patterns = []
    for pname in (patterns or []):
        pp = MagicMock(spec=ProblemPattern)
        pat = MagicMock(spec=Pattern)
        pat.name = pname
        pat.slug = pname.lower().replace(" ", "-")
        pp.pattern = pat
        p.patterns.append(pp)

    # Build topics
    p.topics = []
    for tname in (topics or []):
        pt = MagicMock(spec=ProblemTopic)
        top = MagicMock(spec=Topic)
        top.name = tname
        top.slug = tname.lower().replace(" ", "-")
        pt.topic = top
        p.topics.append(pt)

    return p


def _make_usp(problem: Problem) -> UserSolvedProblem:
    usp = MagicMock(spec=UserSolvedProblem)
    usp.problem = problem
    return usp



class TestOverview:
    def test_empty_solved(self):
        result = compute_overview("alice", [])
        assert result["total_solved"] == 0
        assert result["easy"] == 0
        assert result["medium"] == 0
        assert result["hard"] == 0

    def test_counts_each_problem_once(self):
        """Problems must be counted once in total, even if they belong to multiple patterns."""
        p1 = _make_problem(3, "Longest Substring", "longest-substring", Difficulty.MEDIUM,
                           patterns=["Sliding Window", "Frequency Map"])
        p2 = _make_problem(121, "Best Time to Buy", "best-time", Difficulty.EASY,
                           patterns=["Sliding Window"])
        solved = [_make_usp(p1), _make_usp(p2)]
        result = compute_overview("alice", solved)
        assert result["total_solved"] == 2  # NOT 3 (not summed from patterns)
        assert result["easy"] == 1
        assert result["medium"] == 1
        assert result["hard"] == 0

    def test_difficulty_breakdown(self):
        problems = [
            _make_usp(_make_problem(1, "E1", "e1", Difficulty.EASY)),
            _make_usp(_make_problem(2, "M1", "m1", Difficulty.MEDIUM)),
            _make_usp(_make_problem(3, "M2", "m2", Difficulty.MEDIUM)),
            _make_usp(_make_problem(4, "H1", "h1", Difficulty.HARD)),
        ]
        result = compute_overview("bob", problems)
        assert result["total_solved"] == 4
        assert result["easy"] == 1
        assert result["medium"] == 2
        assert result["hard"] == 1

    def test_includes_user_metadata(self):
        result = compute_overview("carol", [], ranking=500, real_name="Carol", avatar_url="https://x.com/avatar")
        assert result["username"] == "carol"
        assert result["ranking"] == 500
        assert result["real_name"] == "Carol"



class TestTopics:
    def test_empty(self):
        result = compute_topics("alice", [])
        assert result["topics"] == []

    def test_basic_topics(self):
        p1 = _make_problem(3, "LSW", "lsw", Difficulty.MEDIUM, topics=["String", "Hash Table"])
        p2 = _make_problem(1, "Two Sum", "two-sum", Difficulty.EASY, topics=["Hash Table"])
        solved = [_make_usp(p1), _make_usp(p2)]
        result = compute_topics("alice", solved)
        topic_map = {t["topic"]: t for t in result["topics"]}
        assert topic_map["Hash Table"]["solved_count"] == 2
        assert topic_map["String"]["solved_count"] == 1

    def test_topic_difficulty_breakdown(self):
        p_easy = _make_problem(1, "T1", "t1", Difficulty.EASY, topics=["Array"])
        p_medium = _make_problem(2, "T2", "t2", Difficulty.MEDIUM, topics=["Array"])
        p_hard = _make_problem(3, "T3", "t3", Difficulty.HARD, topics=["Array"])
        result = compute_topics("bob", [_make_usp(p_easy), _make_usp(p_medium), _make_usp(p_hard)])
        arr = result["topics"][0]
        assert arr["easy"] == 1
        assert arr["medium"] == 1
        assert arr["hard"] == 1



class TestPatterns:
    def test_empty(self):
        result = compute_patterns("alice", [])
        assert result["patterns"] == []

    def test_multi_pattern_problem(self):
        """#209: counts toward Sliding Window, Two Pointers, and Prefix Sum separately."""
        p209 = _make_problem(
            209, "Min Size Subarray Sum", "minimum-size-subarray-sum", Difficulty.MEDIUM,
            patterns=["Sliding Window", "Two Pointers", "Prefix Sum"]
        )
        result = compute_patterns("alice", [_make_usp(p209)])
        pattern_map = {p["pattern"]: p for p in result["patterns"]}
        assert "Sliding Window" in pattern_map
        assert "Two Pointers" in pattern_map
        assert "Prefix Sum" in pattern_map
        # Each pattern gets count=1 (problem counted per pattern, not in total)
        assert pattern_map["Sliding Window"]["solved_count"] == 1
        assert pattern_map["Two Pointers"]["solved_count"] == 1

    def test_pattern_accumulates_correctly(self):
        """Multiple problems in same pattern should accumulate."""
        p1 = _make_problem(3, "LSW", "lsw", Difficulty.MEDIUM, patterns=["Sliding Window"])
        p2 = _make_problem(438, "FAA", "faa", Difficulty.MEDIUM, patterns=["Sliding Window"])
        p3 = _make_problem(76, "MWS", "mws", Difficulty.HARD, patterns=["Sliding Window"])
        result = compute_patterns("alice", [_make_usp(p1), _make_usp(p2), _make_usp(p3)])
        sw = next(p for p in result["patterns"] if p["pattern"] == "Sliding Window")
        assert sw["solved_count"] == 3
        assert sw["easy"] == 0
        assert sw["medium"] == 2
        assert sw["hard"] == 1

    def test_sorted_by_count_descending(self):
        p1 = _make_problem(1, "P1", "p1", Difficulty.EASY, patterns=["A", "B"])
        p2 = _make_problem(2, "P2", "p2", Difficulty.EASY, patterns=["B"])
        result = compute_patterns("alice", [_make_usp(p1), _make_usp(p2)])
        assert result["patterns"][0]["pattern"] == "B"  # B has 2, A has 1

    def test_problem_list_in_pattern(self):
        p = _make_problem(3, "LSW", "lsw", Difficulty.MEDIUM, patterns=["Sliding Window"])
        result = compute_patterns("alice", [_make_usp(p)])
        sw = result["patterns"][0]
        assert len(sw["problems"]) == 1
        assert sw["problems"][0]["leetcode_id"] == 3

    def test_pattern_detail_found(self):
        p = _make_problem(3, "LSW", "lsw", Difficulty.MEDIUM, patterns=["Sliding Window"])
        result = compute_pattern_detail("alice", [_make_usp(p)], "sliding-window")
        assert result is not None
        assert result["pattern"] == "Sliding Window"

    def test_pattern_detail_not_found(self):
        p = _make_problem(3, "LSW", "lsw", Difficulty.MEDIUM, patterns=["Sliding Window"])
        result = compute_pattern_detail("alice", [_make_usp(p)], "does-not-exist")
        assert result is None



class TestCoverage:
    def _make_pattern(self, name: str, pid: int = 1) -> Pattern:
        p = MagicMock(spec=Pattern)
        p.name = name
        p.slug = name.lower().replace(" ", "-")
        p.id = pid
        p.parent_id = None
        return p

    def test_no_solved_all_unpracticed(self):
        patterns = [self._make_pattern("Sliding Window"), self._make_pattern("BFS")]
        result = compute_coverage("alice", [], patterns)
        assert result["practiced_count"] == 0
        assert result["coverage_ratio"] == 0.0
        assert all(not i["practiced"] for i in result["items"])

    def test_full_coverage(self):
        patterns = [self._make_pattern("Sliding Window")]
        p = _make_problem(3, "LSW", "lsw", Difficulty.MEDIUM, patterns=["Sliding Window"])
        result = compute_coverage("alice", [_make_usp(p)], patterns)
        assert result["practiced_count"] == 1
        assert result["coverage_ratio"] == 1.0

    def test_partial_coverage(self):
        patterns = [self._make_pattern("Sliding Window"), self._make_pattern("BFS")]
        p = _make_problem(3, "LSW", "lsw", Difficulty.MEDIUM, patterns=["Sliding Window"])
        result = compute_coverage("alice", [_make_usp(p)], patterns)
        assert result["total_patterns"] == 2
        assert result["practiced_count"] == 1
        assert result["coverage_ratio"] == 0.5

    def test_double_count_does_not_inflate_coverage(self):
        """Multi-pattern problem should not count the same pattern twice."""
        patterns = [self._make_pattern("Sliding Window"), self._make_pattern("Two Pointers")]
        p = _make_problem(209, "MSAS", "msas", Difficulty.MEDIUM,
                          patterns=["Sliding Window", "Two Pointers"])
        result = compute_coverage("alice", [_make_usp(p)], patterns)
        # Both patterns practiced once
        assert result["practiced_count"] == 2
        sw = next(i for i in result["items"] if i["pattern"] == "Sliding Window")
        assert sw["practiced"] is True
        assert sw["solved_count"] == 1  # One problem solved, not two
