"""Tests for the LeetCode provider parser (no network calls)."""
import pytest
from app.providers.leetcode.parser import (
    parse_profile, parse_solved_stats, parse_recent_submissions, parse_problem_list
)


class TestParseProfile:
    def test_valid_profile(self):
        data = {
            "data": {
                "matchedUser": {
                    "username": "testuser",
                    "profile": {
                        "realName": "Test User",
                        "userAvatar": "https://example.com/avatar.jpg",
                        "ranking": 12345,
                    }
                }
            }
        }
        result = parse_profile(data)
        assert result is not None
        assert result.username == "testuser"
        assert result.real_name == "Test User"
        assert result.ranking == 12345

    def test_user_not_found(self):
        data = {"data": {"matchedUser": None}}
        result = parse_profile(data)
        assert result is None

    def test_empty_data(self):
        result = parse_profile({})
        assert result is None


class TestParseSolvedStats:
    def test_valid_stats(self):
        data = {
            "data": {
                "matchedUser": {
                    "submitStats": {
                        "acSubmissionNum": [
                            {"difficulty": "All", "count": 300, "submissions": 1000},
                            {"difficulty": "Easy", "count": 100, "submissions": 200},
                            {"difficulty": "Medium", "count": 160, "submissions": 600},
                            {"difficulty": "Hard", "count": 40, "submissions": 200},
                        ]
                    }
                }
            }
        }
        result = parse_solved_stats(data)
        assert result is not None
        assert result.total == 300
        assert result.easy == 100
        assert result.medium == 160
        assert result.hard == 40

    def test_missing_user(self):
        result = parse_solved_stats({"data": {"matchedUser": None}})
        assert result is None


class TestParseRecentSubmissions:
    def test_valid_submissions(self):
        data = {
            "data": {
                "recentAcSubmissionList": [
                    {"id": "111", "title": "Two Sum", "titleSlug": "two-sum", "timestamp": "1700000000"},
                    {"id": "222", "title": "Valid Parentheses", "titleSlug": "valid-parentheses", "timestamp": "1700001000"},
                ]
            }
        }
        result = parse_recent_submissions(data)
        assert len(result) == 2
        assert result[0].slug == "two-sum"
        assert result[1].slug == "valid-parentheses"

    def test_empty_list(self):
        data = {"data": {"recentAcSubmissionList": []}}
        result = parse_recent_submissions(data)
        assert result == []


class TestParseProblemList:
    def test_valid_list(self):
        data = {
            "data": {
                "problemsetQuestionList": {
                    "total": 2,
                    "questions": [
                        {
                            "frontendQuestionId": "1",
                            "title": "Two Sum",
                            "titleSlug": "two-sum",
                            "difficulty": "Easy",
                            "isPaidOnly": False,
                            "topicTags": [{"name": "Array", "slug": "array"}, {"name": "Hash Table", "slug": "hash-table"}],
                        },
                        {
                            "frontendQuestionId": "42",
                            "title": "Trapping Rain Water",
                            "titleSlug": "trapping-rain-water",
                            "difficulty": "Hard",
                            "isPaidOnly": False,
                            "topicTags": [{"name": "Array", "slug": "array"}],
                        },
                    ],
                }
            }
        }
        total, problems = parse_problem_list(data)
        assert total == 2
        assert len(problems) == 2
        assert problems[0].frontend_id == 1
        assert problems[0].difficulty == "Easy"
        assert "Array" in problems[0].topic_tags
        assert "Hash Table" in problems[0].topic_tags
        assert problems[1].frontend_id == 42
        assert problems[1].difficulty == "Hard"

    def test_empty(self):
        data = {"data": {"problemsetQuestionList": None}}
        total, problems = parse_problem_list(data)
        assert total == 0
        assert problems == []
