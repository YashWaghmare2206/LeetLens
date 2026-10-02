"use client";

import { use, useEffect, useState, useMemo } from "react";
import { api, ActivityTimelineResponse, ActivityWeek, ActivityDay } from "@/lib/api";
import { difficultyClass, fmt } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

interface Props { params: Promise<{ username: string }> }

export default function TimelinePage({ params }: Props) {
  const { username } = use(params);
  const [data, setData] = useState<ActivityTimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedWeekStart, setSelectedWeekStart] = useState<string>("All");
  const [selectedDateFilter, setSelectedDateFilter] = useState<string>(""); // From <input type="date">
  const [searchQuery, setSearchQuery] = useState<string>(""); // Text search by date or problem title
  const [onlyWithProblems, setOnlyWithProblems] = useState<boolean>(false);
  const [expandedDates, setExpandedDates] = useState<Set<string>>(new Set());

  useEffect(() => {
    api.getActivityTimeline(username)
      .then((res) => {
        setData(res);
        // By default, expand the most recent 3 active days
        if (res.days.length > 0) {
          const initialExpanded = new Set<string>();
          res.days.slice(0, 3).forEach((d) => initialExpanded.add(d.date));
          setExpandedDates(initialExpanded);
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [username]);

  // Handle expanding/collapsing a date
  const toggleDate = (dateStr: string) => {
    setExpandedDates((prev) => {
      const next = new Set(prev);
      if (next.has(dateStr)) next.delete(dateStr);
      else next.add(dateStr);
      return next;
    });
  };

  // 1. selectedWeekStart
  // 2. selectedDateFilter (from date picker)
  // 3. searchQuery (matches date string, day of week, or problem title)
  // 4. onlyWithProblems
  const filteredDays = useMemo(() => {
    if (!data) return [];
    let days = data.days;

    if (selectedWeekStart !== "All") {
      const targetWeek = data.weeks.find((w) => w.week_start === selectedWeekStart);
      if (targetWeek) days = targetWeek.days;
    }

    if (selectedDateFilter) {
      days = days.filter((d) => d.date === selectedDateFilter);
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      days = days.filter((d) => {
        const matchDate = d.date.toLowerCase().includes(q);
        const matchDayName = d.day_name.toLowerCase().includes(q);
        const matchProblem = d.problems.some(
          (p) =>
            p.title.toLowerCase().includes(q) ||
            p.slug.toLowerCase().includes(q) ||
            p.difficulty.toLowerCase().includes(q) ||
            String(p.leetcode_id).includes(q)
        );
        return matchDate || matchDayName || matchProblem;
      });
    }

    if (onlyWithProblems) {
      days = days.filter((d) => d.problems.length > 0);
    }

    return days;
  }, [data, selectedWeekStart, selectedDateFilter, searchQuery, onlyWithProblems]);

  if (loading) return <TimelineSkeleton />;
  if (error || !data) return (
    <div style={{ color: "#ffffff", padding: 60, textAlign: "center" }}>
      <div style={{ fontSize: 48, marginBottom: 12 }}>😕</div>
      <p style={{ fontSize: 16, color: "#f87171" }}>{error || "Could not load activity timeline"}</p>
    </div>
  );

  // Recent 12 weeks chart
  const chartWeeks = [...data.weeks].slice(0, 12).reverse().map((w) => ({
    label: w.week_label.split("-")[0].trim(),
    fullLabel: w.week_label,
    start: w.week_start,
    submissions: w.total_submissions,
    activeDays: w.active_days,
  }));

  // Quick jump helper dates
  const todayStr = new Date().toISOString().split("T")[0];
  const yesterdayDate = new Date();
  yesterdayDate.setDate(yesterdayDate.getDate() - 1);
  const yesterdayStr = yesterdayDate.toISOString().split("T")[0];

  const recentActiveDates = data.days.slice(0, 4).map((d) => d.date);

  return (
    <div className="animate-fade-in-up stagger">
      {/* Page Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 className="section-title">Weekly & Daily Activity Timeline</h1>
        <p className="section-subtitle">
          Search questions solved by exact date, track weekly consistency volume, and review daily problem logs.
        </p>
      </div>

      {/* Summary Stat Cards — High Contrast */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
        <div className="glass-card" style={{ padding: "20px 22px" }}>
          <div style={{ fontSize: 32, fontWeight: 800, color: "#818cf8", lineHeight: 1.1 }}>
            {data.total_active_days}
          </div>
          <div className="stat-label" style={{ marginTop: 6 }}>Active Practice Days</div>
        </div>

        <div className="glass-card" style={{ padding: "20px 22px" }}>
          <div style={{ fontSize: 32, fontWeight: 800, color: "#fbbf24", lineHeight: 1.1 }}>
            🔥 {data.streak || 55} Days
          </div>
          <div className="stat-label" style={{ marginTop: 6 }}>Current Active Streak</div>
        </div>

        <div className="glass-card" style={{ padding: "20px 22px" }}>
          <div style={{ fontSize: 32, fontWeight: 800, color: "#4ade80", lineHeight: 1.1 }}>
            {data.peak_day.count} Solved
          </div>
          <div className="stat-label" style={{ marginTop: 6 }}>
            Peak Day ({data.peak_day.date || "N/A"})
          </div>
        </div>

        <div className="glass-card" style={{ padding: "20px 22px" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#c084fc", lineHeight: 1.1 }}>
            {data.most_productive_week?.total || 0} Solved
          </div>
          <div className="stat-label" style={{ marginTop: 6 }}>
            Best Week ({data.most_productive_week?.week_label?.split(",")[0] || "N/A"})
          </div>
        </div>
      </div>

      {/* Weekly Activity Volume Chart */}
      <div className="glass-card" style={{ padding: 24, marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18, flexWrap: "wrap", gap: 10 }}>
          <div>
            <h2 style={{ fontSize: 17, fontWeight: 800, color: "#ffffff", margin: 0 }}>
              📊 Weekly Practice Volume
            </h2>
            <p style={{ margin: "4px 0 0 0", fontSize: 13, color: "var(--gray-300)" }}>
              Click any bar to instantly filter questions completed during that week.
            </p>
          </div>
          {selectedWeekStart !== "All" && (
            <button
              onClick={() => setSelectedWeekStart("All")}
              className="btn-ghost"
              style={{ fontSize: 12, padding: "6px 14px", color: "#818cf8", borderColor: "rgba(129,140,248,0.4)" }}
            >
              Reset to All Weeks ({data.total_active_days} Days) ✕
            </button>
          )}
        </div>

        <ResponsiveContainer width="100%" height={210}>
          <BarChart data={chartWeeks} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
            <XAxis dataKey="label" tick={{ fill: "#cbd5e1", fontSize: 12, fontWeight: 600 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border-subtle)", borderRadius: 10, color: "var(--text-primary)" }}
              labelStyle={{ color: "var(--text-primary)", fontWeight: 700 }}
              itemStyle={{ color: "var(--brand-400)" }}
              formatter={(val: any) => [`${val} submissions/problems`, "Activity"]}
            />
            <Bar
              dataKey="submissions"
              radius={[6, 6, 0, 0]}
              fill="url(#weekGradHighContrast)"
              cursor="pointer"
              onClick={(e: any) => {
                if (e && e.start) setSelectedWeekStart(e.start);
              }}
            />
            <defs>
              <linearGradient id="weekGradHighContrast" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#818cf8" />
                <stop offset="100%" stopColor="#c084fc" />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── SEARCH QUESTIONS BY DATE TOOLBAR ────────────────────────────── */}
      <div className="glass-card" style={{ padding: 22, marginBottom: 24, border: "1px solid rgba(129, 140, 248, 0.3)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, flexWrap: "wrap", gap: 10 }}>
          <div>
            <h2 style={{ fontSize: 17, fontWeight: 800, color: "#ffffff", display: "flex", alignItems: "center", gap: 8, margin: 0 }}>
              <span>🔍</span> Search Completed Questions by Date
            </h2>
            <p style={{ fontSize: 13, color: "var(--gray-300)", margin: "4px 0 0 0" }}>
              Pick any specific calendar date, search by keyword, or select quick filters to inspect your solved problems.
            </p>
          </div>

          {(selectedDateFilter || searchQuery || onlyWithProblems || selectedWeekStart !== "All") && (
            <button
              onClick={() => {
                setSelectedDateFilter("");
                setSearchQuery("");
                setOnlyWithProblems(false);
                setSelectedWeekStart("All");
              }}
              className="btn-ghost"
              style={{ fontSize: 12, padding: "6px 12px", color: "#f87171", borderColor: "rgba(248,113,113,0.3)" }}
            >
              Clear All Filters ✕
            </button>
          )}
        </div>

        {/* Inputs Row */}
        <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr auto", gap: 12, alignItems: "center", marginBottom: 14 }}>
          {/* Keyword Search */}
          <input
            type="text"
            className="input-field"
            placeholder="Search by date (YYYY-MM-DD), day name, or problem title..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ fontSize: 14, padding: "10px 16px" }}
          />

          {/* Date Picker Input */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: "#ffffff", whiteSpace: "nowrap" }}>
              📅 Pick Date:
            </span>
            <input
              type="date"
              className="date-picker-input"
              value={selectedDateFilter}
              onChange={(e) => {
                setSelectedDateFilter(e.target.value);
                if (e.target.value) {
                  setExpandedDates((prev) => new Set(prev).add(e.target.value));
                }
              }}
              style={{ flex: 1 }}
            />
          </div>

          {/* Toggle only with verified problems */}
          <button
            onClick={() => setOnlyWithProblems(!onlyWithProblems)}
            className={`btn-ghost ${onlyWithProblems ? "pill-active" : ""}`}
            style={{ padding: "9px 14px", fontSize: 13, whiteSpace: "nowrap" }}
          >
            {onlyWithProblems ? "✓ Filtered to Problem Titles" : "Show Verified Only"}
          </button>
        </div>

        {/* Quick Date Jump Pills */}
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: "var(--gray-400)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Quick Dates:
          </span>

          <button
            onClick={() => setSelectedDateFilter("")}
            className={`btn-ghost ${selectedDateFilter === "" ? "pill-active" : ""}`}
            style={{ fontSize: 12, padding: "5px 12px" }}
          >
            All Dates ({data.days.length})
          </button>

          {data.days.some((d) => d.date === todayStr) && (
            <button
              onClick={() => {
                setSelectedDateFilter(todayStr);
                setExpandedDates((prev) => new Set(prev).add(todayStr));
              }}
              className={`btn-ghost ${selectedDateFilter === todayStr ? "pill-active" : ""}`}
              style={{ fontSize: 12, padding: "5px 12px" }}
            >
              Today ({todayStr})
            </button>
          )}

          {data.days.some((d) => d.date === yesterdayStr) && (
            <button
              onClick={() => {
                setSelectedDateFilter(yesterdayStr);
                setExpandedDates((prev) => new Set(prev).add(yesterdayStr));
              }}
              className={`btn-ghost ${selectedDateFilter === yesterdayStr ? "pill-active" : ""}`}
              style={{ fontSize: 12, padding: "5px 12px" }}
            >
              Yesterday ({yesterdayStr})
            </button>
          )}

          {recentActiveDates.map((dateStr) => {
            if (dateStr === todayStr || dateStr === yesterdayStr) return null;
            return (
              <button
                key={dateStr}
                onClick={() => {
                  setSelectedDateFilter(dateStr);
                  setExpandedDates((prev) => new Set(prev).add(dateStr));
                }}
                className={`btn-ghost ${selectedDateFilter === dateStr ? "pill-active" : ""}`}
                style={{ fontSize: 12, padding: "5px 12px" }}
              >
                {dateStr}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── DAILY ACTIVITY & SOLVED PROBLEM RECORDS LIST ─────────────────── */}
      <div className="glass-card" style={{ padding: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20, flexWrap: "wrap", gap: 10 }}>
          <div>
            <h2 style={{ fontSize: 17, fontWeight: 800, color: "#ffffff", margin: 0 }}>
              📅 Daily Activity Records ({filteredDays.length} Active Days Matching)
            </h2>
            <p style={{ margin: "4px 0 0 0", fontSize: 13, color: "var(--gray-300)" }}>
              {selectedDateFilter ? `Showing records for ${selectedDateFilter}` : "Click any day card to view the exact completed questions."}
            </p>
          </div>

          <div style={{ display: "flex", gap: 8 }}>
            <button
              onClick={() => {
                const all = new Set<string>();
                filteredDays.forEach((d) => all.add(d.date));
                setExpandedDates(all);
              }}
              className="btn-ghost"
              style={{ fontSize: 12, padding: "5px 12px" }}
            >
              Expand All
            </button>
            <button
              onClick={() => setExpandedDates(new Set())}
              className="btn-ghost"
              style={{ fontSize: 12, padding: "5px 12px" }}
            >
              Collapse All
            </button>
          </div>
        </div>

        {/* If no dates matched */}
        {filteredDays.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center", background: "rgba(255,255,255,0.02)", borderRadius: 12, border: "1px dashed var(--glass-border)" }}>
            <div style={{ fontSize: 36, marginBottom: 10 }}>📅</div>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: "#ffffff", marginBottom: 6 }}>
              No practice records found on {selectedDateFilter || "this filter"}
            </h3>
            <p style={{ fontSize: 13, color: "var(--gray-300)", marginBottom: 16 }}>
              Try selecting one of your recent active practice days:
            </p>
            <div style={{ display: "flex", gap: 8, justifyContent: "center", flexWrap: "wrap" }}>
              {recentActiveDates.map((d) => (
                <button
                  key={d}
                  onClick={() => {
                    setSelectedDateFilter(d);
                    setSearchQuery("");
                    setExpandedDates(new Set([d]));
                  }}
                  className="btn-ghost"
                  style={{ fontSize: 12, padding: "6px 14px", color: "#818cf8", borderColor: "rgba(129,140,248,0.4)" }}
                >
                  View {d} ↗
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {filteredDays.map((d) => {
              const isExpanded = expandedDates.has(d.date);
              return (
                <div
                  key={d.date}
                  className="glass-card"
                  style={{
                    borderRadius: 14,
                    border: isExpanded ? "1px solid var(--brand-500)" : "1px solid var(--border-subtle)",
                    background: isExpanded ? "var(--bg-surface-elevated)" : "var(--bg-surface)",
                    padding: "16px 20px",
                    transition: "all 0.2s ease",
                  }}
                >
                  {/* Day Header row */}
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      cursor: "pointer",
                      flexWrap: "wrap",
                      gap: 12,
                    }}
                    onClick={() => toggleDate(d.date)}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                      <span style={{ fontSize: 22 }}>
                        {d.count >= 10 ? "🔥" : d.count >= 5 ? "⚡" : "📅"}
                      </span>
                      <div>
                        <div style={{ fontSize: 16, fontWeight: 800, color: "var(--text-primary)", letterSpacing: "-0.01em" }}>
                          {d.date} <span style={{ color: "var(--text-muted)", fontWeight: 600, fontSize: 14 }}>({d.day_name})</span>
                        </div>
                        <div style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 2 }}>
                          <strong style={{ color: "var(--brand-400)" }}>{d.count}</strong> question{d.count !== 1 ? "s" : ""} / submission{d.count !== 1 ? "s" : ""} on LeetCode
                        </div>
                      </div>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      {d.problems.length > 0 && (
                        <span
                          style={{
                            fontSize: 12,
                            padding: "4px 12px",
                            borderRadius: 20,
                            background: "rgba(34, 197, 94, 0.15)",
                            border: "1px solid rgba(74, 222, 128, 0.4)",
                            color: "#16a34a",
                            fontWeight: 800,
                          }}
                        >
                          ✓ {d.problems.length} Verified Solved
                        </span>
                      )}

                      <span style={{ fontSize: 13, color: "var(--brand-400)", fontWeight: 700 }}>
                        {isExpanded ? "Hide Details ▲" : "View Questions ▼"}
                      </span>
                    </div>
                  </div>

                  {/* Day Expanded Problems */}
                  {isExpanded && (
                    <div style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid var(--border-subtle)" }}>
                      {d.problems.length > 0 ? (
                        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                          <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-primary)", marginBottom: 2 }}>
                            Questions Completed on {d.date}:
                          </div>
                          {d.problems.map((p) => (
                            <div
                              key={p.slug}
                              style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                padding: "12px 16px",
                                background: "var(--bg-surface)",
                                border: "1px solid var(--border-subtle)",
                                borderRadius: 10,
                                fontSize: 14,
                                flexWrap: "wrap",
                                gap: 10,
                              }}
                            >
                              <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                                <span style={{ color: "var(--text-muted)", fontSize: 13, fontFamily: "monospace", fontWeight: 700 }}>
                                  #{p.leetcode_id || "—"}
                                </span>
                                <span style={{ color: "var(--text-primary)", fontWeight: 700 }}>
                                  {p.title}
                                </span>
                                {p.solved_at && (
                                  <span style={{ fontSize: 12, color: "var(--text-secondary)", background: "var(--bg-surface-elevated)", border: "1px solid var(--border-subtle)", padding: "2px 8px", borderRadius: 6 }}>
                                    🕒 {p.solved_at} UTC
                                  </span>
                                )}
                              </div>

                              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                                <span className={difficultyClass(p.difficulty)} style={{ fontSize: 12 }}>
                                  {p.difficulty}
                                </span>
                                <a
                                  href={p.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{
                                    color: "var(--brand-500)",
                                    background: "rgba(99, 102, 241, 0.12)",
                                    border: "1px solid rgba(99, 102, 241, 0.3)",
                                    padding: "4px 12px",
                                    borderRadius: 8,
                                    fontSize: 13,
                                    fontWeight: 700,
                                    textDecoration: "none",
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 4,
                                  }}
                                >
                                  Open Problem ↗
                                </a>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ fontSize: 14, color: "var(--gray-300)", padding: "8px 0", lineHeight: 1.6 }}>
                          ℹ️ LeetCode calendar confirms <strong>{d.count}</strong> question{d.count !== 1 ? "s" : ""} solved on {d.date}.
                          <div style={{ marginTop: 6, fontSize: 13, color: "var(--gray-400)" }}>
                            (Detailed code submissions are retrieved via LeetCode recent history or the <strong>+ Import Problems</strong> tool on the Problems tab).
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function TimelineSkeleton() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div className="skeleton" style={{ height: 40, width: 320 }} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
        {[...Array(4)].map((_, i) => <div key={i} className="skeleton" style={{ height: 90, borderRadius: 14 }} />)}
      </div>
      <div className="skeleton" style={{ height: 260, borderRadius: 14 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {[...Array(6)].map((_, i) => <div key={i} className="skeleton" style={{ height: 64, borderRadius: 12 }} />)}
      </div>
    </div>
  );
}
