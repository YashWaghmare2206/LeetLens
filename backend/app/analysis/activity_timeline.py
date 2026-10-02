"""
Analysis Engine — Activity Timeline (Week-wise & Day-wise questions analysis)
Parses user submission calendar, groups activity into weekly buckets,
and matches specific problems solved on each individual day.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import TYPE_CHECKING
from app.schemas.stateless import StatelessSolved

if TYPE_CHECKING:
    from app.schemas.stateless import StatelessUser


def compute_activity_timeline(
    username: str,
    solved: list[StatelessSolved],
    user: StatelessUser | None = None,
) -> dict:
    """
    Computes:
    - week_wise: list of weekly buckets with submission totals, active days, and daily breakdown
    - day_wise: list of all active days with the exact problems solved on that day
    - summary: total active days, current streak, peak day, most productive week
    """
    # 1. Map problems by solved date (YYYY-MM-DD)
    problems_by_date: dict[str, list[dict]] = defaultdict(list)
    for usp in solved:
        p = usp.problem
        dt = usp.last_solved_at
        if dt:
            # Format to UTC date string
            date_str = dt.strftime("%Y-%m-%d")
            problems_by_date[date_str].append({
                "leetcode_id": p.leetcode_id,
                "title": p.title,
                "slug": p.slug,
                "difficulty": p.difficulty.value,
                "url": p.url or f"https://leetcode.com/problems/{p.slug}/",
                "solved_at": dt.strftime("%H:%M:%S") if hasattr(dt, "strftime") else None,
            })

    # 2. Parse calendar submissions from user
    cal_data: dict[str, int] = {}
    if user and user.submission_calendar_json:
        try:
            cal_data = json.loads(user.submission_calendar_json)
        except Exception:
            cal_data = {}

    # Sort timestamps descending
    all_ts = sorted([int(k) for k in cal_data.keys()], reverse=True)

    day_entries = []
    weeks_map: dict[str, dict] = {}
    peak_day = {"date": None, "count": 0}

    for ts in all_ts:
        count = cal_data.get(str(ts), 0)
        dt = datetime.fromtimestamp(ts, timezone.utc)
        date_str = dt.strftime("%Y-%m-%d")
        day_name = dt.strftime("%A")

        if count > peak_day["count"]:
            peak_day = {"date": date_str, "count": count}

        # Check for confirmed solved problem titles on this date
        day_problems = problems_by_date.get(date_str, [])

        day_obj = {
            "date": date_str,
            "day_name": day_name,
            "timestamp": ts,
            "count": count,
            "problems_count": len(day_problems),
            "problems": day_problems,
        }
        day_entries.append(day_obj)

        # Weekly aggregation: ISO calendar week or Monday start
        # Monday of current week
        monday = dt - timedelta(days=dt.weekday())
        week_key = monday.strftime("%Y-%m-%d")
        sunday = monday + timedelta(days=6)
        week_label = f"{monday.strftime('%b %d')} - {sunday.strftime('%b %d, %Y')}"

        if week_key not in weeks_map:
            weeks_map[week_key] = {
                "week_start": week_key,
                "week_label": week_label,
                "total_submissions": 0,
                "active_days": 0,
                "problems_logged": 0,
                "days": [],
            }

        weeks_map[week_key]["total_submissions"] += count
        weeks_map[week_key]["active_days"] += 1
        weeks_map[week_key]["problems_logged"] += len(day_problems)
        weeks_map[week_key]["days"].append(day_obj)

    # Sort weeks descending
    sorted_weeks = sorted(weeks_map.values(), key=lambda w: w["week_start"], reverse=True)

    # Find most productive week
    best_week = None
    if sorted_weeks:
        best_week = max(sorted_weeks, key=lambda w: w["total_submissions"])

    return {
        "username": username,
        "total_active_days": len(day_entries),
        "total_submissions_tracked": sum(d["count"] for d in day_entries),
        "streak": user.streak if user else None,
        "peak_day": peak_day,
        "most_productive_week": {
            "week_label": best_week["week_label"] if best_week else "N/A",
            "total": best_week["total_submissions"] if best_week else 0,
        } if best_week else None,
        "weeks": sorted_weeks,
        "days": day_entries,
    }
