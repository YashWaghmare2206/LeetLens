"""
LeetCode provider response parser.
Converts raw LeetCode API JSON → internal Python dicts/dataclasses.
The rest of the backend never needs to know the LeetCode response shape.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LCProfile:
    username: str
    real_name: str | None
    avatar_url: str | None
    ranking: int | None


@dataclass
class LCSolvedStats:
    total: int
    easy: int
    medium: int
    hard: int


@dataclass
class LCProblem:
    frontend_id: int
    title: str
    slug: str
    difficulty: str  # "Easy" | "Medium" | "Hard"
    is_paid_only: bool
    topic_tags: list[str]  # tag names


@dataclass
class LCRecentSubmission:
    submission_id: str
    title: str
    slug: str
    timestamp: datetime


def parse_profile(data: dict) -> LCProfile | None:
    matched = data.get("data", {}).get("matchedUser")
    if not matched:
        return None
    profile = matched.get("profile", {})
    return LCProfile(
        username=matched.get("username", ""),
        real_name=profile.get("realName") or None,
        avatar_url=profile.get("userAvatar") or None,
        ranking=profile.get("ranking") or None,
    )


def parse_solved_stats(data: dict) -> LCSolvedStats | None:
    matched = data.get("data", {}).get("matchedUser")
    if not matched:
        return None
    ac_list = matched.get("submitStats", {}).get("acSubmissionNum", [])
    counts: dict[str, int] = {}
    for item in ac_list:
        counts[item["difficulty"]] = item["count"]
    return LCSolvedStats(
        total=counts.get("All", 0),
        easy=counts.get("Easy", 0),
        medium=counts.get("Medium", 0),
        hard=counts.get("Hard", 0),
    )


def parse_recent_submissions(data: dict) -> list[LCRecentSubmission]:
    submissions = data.get("data", {}).get("recentAcSubmissionList", []) or []
    result = []
    for s in submissions:
        try:
            ts = datetime.fromtimestamp(int(s["timestamp"]))
        except Exception:
            ts = datetime.utcnow()
        result.append(LCRecentSubmission(
            submission_id=str(s.get("id", "")),
            title=s.get("title", ""),
            slug=s.get("titleSlug", ""),
            timestamp=ts,
        ))
    return result


def parse_problem_list(data: dict) -> tuple[int, list[LCProblem]]:
    """Returns (total, problems)."""
    pset = data.get("data", {}).get("problemsetQuestionList", {})
    if not pset:
        return 0, []
    total = pset.get("total", 0)
    problems = []
    for q in pset.get("questions", []) or []:
        try:
            fid = int(q.get("frontendQuestionId", 0))
        except (ValueError, TypeError):
            continue
        diff_raw = q.get("difficulty", "Unknown")
        diff = diff_raw if diff_raw in ("Easy", "Medium", "Hard") else "Unknown"
        tags = [t["name"] for t in (q.get("topicTags") or [])]
        problems.append(LCProblem(
            frontend_id=fid,
            title=q.get("title", ""),
            slug=q.get("titleSlug", ""),
            difficulty=diff,
            is_paid_only=bool(q.get("isPaidOnly", False)),
            topic_tags=tags,
        ))
    return total, problems


@dataclass
class LCTagProblemCount:
    tag_name: str
    tag_slug: str
    problems_solved: int
    category: str  # "fundamental" | "intermediate" | "advanced"


@dataclass
class LCFullUserData:
    username: str
    real_name: str | None
    avatar_url: str | None
    ranking: int | None
    total_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int
    total_submissions: int
    streak: int | None
    total_active_days: int | None
    beats_easy: float | None
    beats_medium: float | None
    beats_hard: float | None
    tag_problem_counts: list[LCTagProblemCount]
    badges: list[dict]
    upcoming_badges: list[dict]
    languages: list[dict]
    submission_calendar: str | None
    acceptance_rate: float | None
    reputation: int | None


def parse_full_user_data(data: dict) -> LCFullUserData | None:
    data_dict = data.get("data", {})
    matched = data_dict.get("matchedUser")
    if not matched:
        return None
    profile = matched.get("profile", {})
    
    # Solved counts
    ac_list = matched.get("submitStats", {}).get("acSubmissionNum", [])
    counts: dict[str, int] = {}
    sub_counts: dict[str, int] = {}
    for item in ac_list:
        diff = item.get("difficulty", "")
        counts[diff] = item.get("count", 0)
        sub_counts[diff] = item.get("submissions", 0)

    # Calendar
    cal = matched.get("userCalendar") or {}
    streak = cal.get("streak")
    active_days = cal.get("totalActiveDays")
    submission_calendar = cal.get("submissionCalendar")

    # Beats percentages
    beats_data = data_dict.get("userProfileUserQuestionProgressV2", {}).get("userSessionBeatsPercentage", []) or []
    beats_map: dict[str, float] = {}
    for b in beats_data:
        diff = b.get("difficulty", "").title()
        pct = b.get("percentage")
        try:
            beats_map[diff] = float(pct) if pct is not None else 0.0
        except (ValueError, TypeError):
            beats_map[diff] = 0.0

    # Tag problem counts
    tags_raw = matched.get("tagProblemCounts") or {}
    tag_counts: list[LCTagProblemCount] = []
    for cat in ("fundamental", "intermediate", "advanced"):
        for item in tags_raw.get(cat, []) or []:
            tag_counts.append(LCTagProblemCount(
                tag_name=item.get("tagName", ""),
                tag_slug=item.get("tagSlug", ""),
                problems_solved=item.get("problemsSolved", 0),
                category=cat,
            ))

    # Languages, badges, upcoming badges
    languages = matched.get("languageProblemCount") or []
    badges = matched.get("badges") or []
    upcoming_badges = matched.get("upcomingBadges") or []
    reputation = profile.get("reputation")

    total_s = counts.get("All", 0)
    total_sub = sub_counts.get("All", 0)
    ac_rate = round((total_s / total_sub * 100), 1) if total_sub > 0 else None

    return LCFullUserData(
        username=matched.get("username", ""),
        real_name=profile.get("realName") or None,
        avatar_url=profile.get("userAvatar") or None,
        ranking=profile.get("ranking") or None,
        total_solved=total_s,
        easy_solved=counts.get("Easy", 0),
        medium_solved=counts.get("Medium", 0),
        hard_solved=counts.get("Hard", 0),
        total_submissions=total_sub,
        streak=streak,
        total_active_days=active_days,
        beats_easy=beats_map.get("Easy"),
        beats_medium=beats_map.get("Medium"),
        beats_hard=beats_map.get("Hard"),
        tag_problem_counts=tag_counts,
        badges=badges,
        upcoming_badges=upcoming_badges,
        languages=languages,
        submission_calendar=submission_calendar,
        acceptance_rate=ac_rate,
        reputation=reputation,
    )


def parse_all_recent_submissions(data: dict) -> list[LCRecentSubmission]:
    """Parse recent submissions list, returning only Accepted ones."""
    submissions = data.get("data", {}).get("recentSubmissionList", []) or []
    result = []
    for s in submissions:
        if s.get("statusDisplay") != "Accepted":
            continue
        try:
            ts = datetime.fromtimestamp(int(s["timestamp"]))
        except Exception:
            ts = datetime.utcnow()
        result.append(LCRecentSubmission(
            submission_id="",
            title=s.get("title", "").strip(),
            slug=s.get("titleSlug", "").strip(),
            timestamp=ts,
        ))
    return result


def parse_question_data(data: dict) -> LCProblem | None:
    q = data.get("data", {}).get("question")
    if not q:
        return None
    try:
        fid = int(q.get("questionFrontendId") or q.get("questionId") or 0)
    except (ValueError, TypeError):
        fid = 0
    diff_raw = q.get("difficulty", "Unknown")
    diff = diff_raw if diff_raw in ("Easy", "Medium", "Hard") else "Unknown"
    tags = [t["name"] for t in (q.get("topicTags") or [])]
    return LCProblem(
        frontend_id=fid,
        title=q.get("title", ""),
        slug=q.get("titleSlug", ""),
        difficulty=diff,
        is_paid_only=bool(q.get("isPaidOnly", False)),
        topic_tags=tags,
    )
