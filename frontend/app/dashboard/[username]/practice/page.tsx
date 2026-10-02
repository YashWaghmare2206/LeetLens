"use client";

import { use, useEffect, useState, useMemo } from "react";
import { api, PatternPracticeResponse, CuratedPracticeProblem } from "@/lib/api";
import { difficultyClass } from "@/lib/utils";

interface Props { params: Promise<{ username: string }> }

const COMPANIES = ["All", "Google", "Meta", "Amazon", "Microsoft", "Uber", "Apple"];
const REVISION_PRESETS = [7, 14, 21, 30];

export default function PatternPracticePage({ params }: Props) {
  const { username } = use(params);
  const [data, setData] = useState<PatternPracticeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedCompany, setSelectedCompany] = useState<string>("All");
  const [filterStatus, setFilterStatus] = useState<"All" | "Unsolved" | "Solved">("All");
  const [onlyRevision, setOnlyRevision] = useState<boolean>(false);
  const [revisionDays, setRevisionDays] = useState<number>(14);
  const [search, setSearch] = useState("");
  const [viewMode, setViewMode] = useState<"topic-groups" | "pattern-browser">("topic-groups");

  // Local refreshed problems overrides (stored for session)
  const [refreshedSlugs, setRefreshedSlugs] = useState<Record<string, number>>({});

  // Expanded state for topic groups and patterns
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});
  const [selectedPatternSlug, setSelectedPatternSlug] = useState<string>("");

  useEffect(() => {
    // Load stored revisionDays preference if exists
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("leetlens_revision_days");
      if (saved) {
        const val = parseInt(saved, 10);
        if (!isNaN(val) && val > 0) setRevisionDays(val);
      }
    }

    api.getPatternPractice(username)
      .then((res) => {
        setData(res);
        if (res.patterns.length > 0) {
          setSelectedPatternSlug(res.patterns[0].pattern_slug);
        }
        if (res.topic_groups && res.topic_groups.length > 0) {
          const initial: Record<string, boolean> = {};
          res.topic_groups.forEach((tg, idx) => {
            initial[tg.topic_group] = idx < 2;
          });
          setExpandedGroups(initial);
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [username]);

  const handleSetRevisionDays = (days: number) => {
    setRevisionDays(days);
    if (typeof window !== "undefined") {
      localStorage.setItem("leetlens_revision_days", String(days));
    }
  };

  const markRefreshed = (slug: string) => {
    setRefreshedSlugs((prev) => ({ ...prev, [slug]: 0 }));
  };

  const toggleGroup = (groupName: string) => {
    setExpandedGroups((prev) => ({ ...prev, [groupName]: !prev[groupName] }));
  };

  const isProblemDueForRevision = (prob: CuratedPracticeProblem) => {
    if (!prob.is_solved) return false;
    const daysAgo = refreshedSlugs[prob.slug] !== undefined ? refreshedSlugs[prob.slug] : prob.days_since_solved;
    if (daysAgo == null) return false;
    return daysAgo >= revisionDays;
  };

  const matchesFilters = (prob: CuratedPracticeProblem) => {
    if (filterStatus === "Solved" && !prob.is_solved) return false;
    if (filterStatus === "Unsolved" && prob.is_solved) return false;
    if (onlyRevision && !isProblemDueForRevision(prob)) return false;

    if (selectedCompany !== "All") {
      const matchComp = prob.companies.some((c) => c.toLowerCase() === selectedCompany.toLowerCase());
      if (!matchComp) return false;
    }
    if (search) {
      const q = search.toLowerCase();
      const matchTitle = prob.title.toLowerCase().includes(q);
      const matchId = String(prob.leetcode_id).includes(q);
      const matchDiff = prob.difficulty.toLowerCase().includes(q);
      const matchTier = prob.tier.toLowerCase().includes(q);
      if (!matchTitle && !matchId && !matchDiff && !matchTier) return false;
    }
    return true;
  };

  const totalDueForRevision = useMemo(() => {
    if (!data) return 0;
    let count = 0;
    data.patterns.forEach((pat) => {
      pat.problems.forEach((prob) => {
        if (isProblemDueForRevision(prob)) count++;
      });
    });
    return count;
  }, [data, revisionDays, refreshedSlugs]);

  if (loading) return <PracticeSkeleton />;
  if (error || !data) return (
    <div style={{ color: "#94a3b8", padding: 60, textAlign: "center" }}>
      <p style={{ fontSize: 16, color: "#f87171" }}>{error || "Could not load pattern practice roadmaps"}</p>
    </div>
  );

  const selectedPattern = data.patterns.find((p) => p.pattern_slug === selectedPatternSlug) || data.patterns[0];
  const filteredBrowserProblems = (selectedPattern?.problems || []).filter(matchesFilters);

  return (
    <div className="animate-fade-in-up stagger">
      {/* Page Header */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "#818cf8" }}>
            Curated SDE Curriculum
          </span>
          <span style={{ fontSize: 11, color: "#64748b" }}>•</span>
          <span style={{ fontSize: 12, color: "#94a3b8" }}>
            Top Core Interview Problems
          </span>
        </div>
        <h1 className="section-title" style={{ fontSize: 24, fontWeight: 800, color: "#ffffff", letterSpacing: "-0.01em" }}>
          Pattern Practice & Company Roadmaps
        </h1>
        <p className="section-subtitle" style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>
          Structured interview problems organized by Topic, verified company recurrence, and customizable Spaced Repetition revisit schedules.
        </p>
      </div>

      {/* Curriculum & Spaced Repetition Control Bar */}
      <div
        className="glass-card"
        style={{
          padding: "18px 22px",
          marginBottom: 20,
          borderRadius: 12,
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        {/* Row 1: Overall Progress & Revision Summary */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: "var(--brand-400)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 2 }}>
              Curated Target Progress
            </div>
            <div style={{ fontSize: 18, fontWeight: 800, color: "var(--text-primary)", fontFamily: "'JetBrains Mono', monospace" }}>
              {data.total_user_solved_curated} / {data.total_curated_problems} Target Problems Solved ({data.overall_completion_pct}%)
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ width: 160 }}>
              <div className="progress-bar" style={{ height: 6, background: "var(--border-subtle)" }}>
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${data.overall_completion_pct}%`,
                    background: "var(--brand-500)",
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Row 2: User-Configurable Spaced Repetition Settings */}
        <div
          style={{
            padding: "12px 16px",
            background: "var(--bg-surface-elevated)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 8,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 14,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: "#cbd5e1", display: "inline-flex", alignItems: "center", gap: 6 }}>
              <span>⏱️</span> Spaced Repetition Interval:
            </span>

            {/* Quick preset buttons */}
            <div style={{ display: "flex", gap: 4 }}>
              {REVISION_PRESETS.map((p) => {
                const isActive = revisionDays === p;
                return (
                  <button
                    key={p}
                    onClick={() => handleSetRevisionDays(p)}
                    style={{
                      fontSize: 11,
                      padding: "3px 9px",
                      borderRadius: 6,
                      cursor: "pointer",
                      border: isActive ? "1px solid #818cf8" : "1px solid rgba(255, 255, 255, 0.08)",
                      background: isActive ? "#1e2538" : "transparent",
                      color: isActive ? "#ffffff" : "#94a3b8",
                      fontWeight: isActive ? 700 : 500,
                    }}
                  >
                    {p}d
                  </button>
                );
              })}
            </div>

            {/* Custom input */}
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <span style={{ fontSize: 11, color: "#64748b" }}>or custom:</span>
              <input
                type="number"
                min="1"
                max="365"
                value={revisionDays}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  if (!isNaN(val) && val > 0) handleSetRevisionDays(val);
                }}
                style={{
                  width: 50,
                  padding: "2px 6px",
                  fontSize: 11,
                  background: "#111522",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  color: "#ffffff",
                  borderRadius: 4,
                  textAlign: "center",
                }}
              />
              <span style={{ fontSize: 11, color: "#64748b" }}>days</span>
            </div>
          </div>

          {/* Toggle Revisit Filter Button */}
          <button
            onClick={() => setOnlyRevision((prev) => !prev)}
            style={{
              fontSize: 12,
              padding: "6px 14px",
              borderRadius: 6,
              cursor: "pointer",
              transition: "all 0.15s ease",
              border: onlyRevision ? "1px solid #f59e0b" : "1px solid rgba(245, 158, 11, 0.4)",
              background: onlyRevision ? "#f59e0b" : "rgba(245, 158, 11, 0.1)",
              color: onlyRevision ? "#000000" : "#fbbf24",
              fontWeight: 700,
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            <span>{onlyRevision ? "✓ Showing Due to Revisit" : "Show Due for Revisit"}</span>
            <span
              style={{
                fontSize: 11,
                padding: "1px 6px",
                borderRadius: 10,
                background: onlyRevision ? "rgba(0,0,0,0.2)" : "rgba(245, 158, 11, 0.2)",
                color: onlyRevision ? "#000000" : "#fbbf24",
                fontWeight: 800,
              }}
            >
              {totalDueForRevision}
            </span>
          </button>
        </div>

        {/* Informational banner when Revisit filter is active */}
        {onlyRevision && (
          <div
            style={{
              padding: "8px 14px",
              background: "rgba(245, 158, 11, 0.08)",
              border: "1px solid rgba(245, 158, 11, 0.2)",
              borderRadius: 6,
              fontSize: 12,
              color: "#fbbf24",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span>
              Showing questions you solved <strong>{revisionDays} or more days ago</strong>. Re-solving them periodically cements algorithmic intuition into permanent memory.
            </span>
            <button
              onClick={() => setOnlyRevision(false)}
              style={{ background: "transparent", border: "none", color: "#94a3b8", cursor: "pointer", fontSize: 11 }}
            >
              ✕ Clear Filter
            </button>
          </div>
        )}
      </div>

      {/* Global Filter Toolbar */}
      <div
        className="glass-card"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 12,
          padding: "14px 18px",
          borderRadius: 12,
          marginBottom: 20,
        }}
      >
        {/* Row 1: View Mode Toggle & Company Chips */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginRight: 4 }}>
              Company:
            </span>
            {COMPANIES.map((comp) => {
              const isActive = selectedCompany === comp;
              return (
                <button
                  key={comp}
                  onClick={() => setSelectedCompany(comp)}
                  className={`btn-ghost ${isActive ? "pill-active" : ""}`}
                  style={{
                    fontSize: 12,
                    padding: "4px 10px",
                    fontWeight: isActive ? 700 : 500,
                  }}
                >
                  {comp}
                </button>
              );
            })}
          </div>

          {/* View Mode Toggle */}
          <div style={{ display: "flex", gap: 4, background: "var(--bg-surface-elevated)", padding: 3, borderRadius: 8, border: "1px solid var(--border-subtle)" }}>
            <button
              onClick={() => setViewMode("topic-groups")}
              style={{
                background: viewMode === "topic-groups" ? "var(--brand-500)" : "transparent",
                color: viewMode === "topic-groups" ? "#ffffff" : "var(--text-secondary)",
                border: "none",
                borderRadius: 6,
                padding: "5px 12px",
                fontSize: 12,
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              Grouped by Topic
            </button>
            <button
              onClick={() => setViewMode("pattern-browser")}
              style={{
                background: viewMode === "pattern-browser" ? "var(--brand-500)" : "transparent",
                color: viewMode === "pattern-browser" ? "#ffffff" : "var(--text-secondary)",
                border: "none",
                borderRadius: 6,
                padding: "5px 12px",
                fontSize: 12,
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              Pattern Browser
            </button>
          </div>
        </div>

        {/* Row 2: Status Filters and Search */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, paddingTop: 6, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginRight: 2 }}>
              Status:
            </span>
            {(["All", "Unsolved", "Solved"] as const).map((st) => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                className={`btn-ghost ${filterStatus === st ? "pill-active" : ""}`}
                style={{ fontSize: 12, padding: "4px 10px", fontWeight: filterStatus === st ? 700 : 500 }}
              >
                {st === "All" && "All"}
                {st === "Unsolved" && "To Solve"}
                {st === "Solved" && "Solved"}
              </button>
            ))}
          </div>

          <input
            type="text"
            className="input-field"
            placeholder="Search questions or patterns..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 220, padding: "6px 12px", fontSize: 12 }}
          />
        </div>
      </div>

      {/* VIEW MODE 1: Topic Groups View (Grouped by Topic and in it all questions) */}
      {viewMode === "topic-groups" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {data.topic_groups.map((tg) => {
            const isExpanded = expandedGroups[tg.topic_group] ?? true;

            // Collect all filtered problems within this topic group
            const patternsWithFilteredProblems = tg.patterns.map((pat) => ({
              ...pat,
              matchingProblems: pat.problems.filter(matchesFilters),
            })).filter((pat) => pat.matchingProblems.length > 0);

            const totalMatchingInGroup = patternsWithFilteredProblems.reduce(
              (acc, p) => acc + p.matchingProblems.length, 0
            );

            // If filters are applied and no questions match this group, hide it
            if ((selectedCompany !== "All" || filterStatus !== "All" || onlyRevision || search) && totalMatchingInGroup === 0) {
              return null;
            }

            return (
              <div
                key={tg.topic_group}
                className="glass-card"
                style={{
                  borderRadius: 12,
                  overflow: "hidden",
                }}
              >
                {/* Topic Group Header (Collapsible) */}
                <div
                  onClick={() => toggleGroup(tg.topic_group)}
                  style={{
                    padding: "16px 20px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    cursor: "pointer",
                    background: "var(--bg-surface-elevated)",
                    borderBottom: isExpanded ? "1px solid var(--border-subtle)" : "none",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "'JetBrains Mono', monospace" }}>
                      {isExpanded ? "▼" : "▶"}
                    </span>
                    <div>
                      <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                        {tg.topic_group}
                      </h3>
                      <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
                        {tg.patterns.length} algorithmic patterns • {tg.solved_count}/{tg.total_problems} completed ({tg.completion_pct}%)
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: tg.completion_pct >= 80 ? "#22c55e" : "#818cf8", fontFamily: "'JetBrains Mono', monospace" }}>
                        {tg.completion_pct}%
                      </span>
                    </div>
                    <div style={{ width: 80 }}>
                      <div className="progress-bar" style={{ height: 5, background: "#090d16" }}>
                        <div
                          className="progress-bar-fill"
                          style={{
                            width: `${tg.completion_pct}%`,
                            background: tg.completion_pct >= 80 ? "#22c55e" : "#4f46e5",
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Patterns & Questions inside this Topic Group */}
                {isExpanded && (
                  <div style={{ padding: "16px 20px", display: "flex", flexDirection: "column", gap: 16 }}>
                    {patternsWithFilteredProblems.map((pat) => (
                      <div key={pat.pattern_slug} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                        {/* Pattern sub-header */}
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "4px 0" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <span style={{ fontSize: 13, fontWeight: 700, color: "var(--text-primary)" }}>
                              {pat.pattern_name}
                            </span>
                            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>•</span>
                            <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>
                              {pat.description}
                            </span>
                          </div>
                          <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "'JetBrains Mono', monospace", fontWeight: 600 }}>
                            {pat.solved_count}/{pat.total_problems} solved
                          </span>
                        </div>

                        {/* Problems list under pattern */}
                        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                          {pat.matchingProblems.map((prob) => (
                            <ProblemRow
                              key={prob.slug}
                              prob={prob}
                              revisionDays={revisionDays}
                              refreshedDaysAgo={refreshedSlugs[prob.slug]}
                              onRefresh={() => markRefreshed(prob.slug)}
                            />
                          ))}
                        </div>
                      </div>
                    ))}

                    {patternsWithFilteredProblems.length === 0 && (
                      <div style={{ padding: 20, textAlign: "center", color: "#64748b", fontSize: 12 }}>
                        No questions in this topic match the active filters.
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* VIEW MODE 2: Pattern Browser (Master / Detail 2-Column) */}
      {viewMode === "pattern-browser" && (
        <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 20, alignItems: "start" }}>
          {/* Pattern List */}
          <div
            style={{
              padding: "12px",
              maxHeight: "calc(100vh - 220px)",
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: 4,
              position: "sticky",
              top: 20,
              background: "#111522",
              border: "1px solid rgba(255, 255, 255, 0.08)",
              borderRadius: 12,
            }}
          >
            <div style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.06em", padding: "6px 8px" }}>
              Patterns ({data.patterns.length})
            </div>

            {data.patterns.map((pat) => {
              const isSelected = pat.pattern_slug === selectedPatternSlug;
              return (
                <button
                  key={pat.pattern_slug}
                  onClick={() => setSelectedPatternSlug(pat.pattern_slug)}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "10px 12px",
                    borderRadius: 8,
                    border: isSelected ? "1px solid rgba(99, 102, 241, 0.8)" : "1px solid transparent",
                    background: isSelected ? "#1e2538" : "transparent",
                    color: isSelected ? "#ffffff" : "#94a3b8",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div>
                    <div style={{ fontSize: 13, fontWeight: isSelected ? 700 : 500, color: isSelected ? "#ffffff" : "#f1f5f9" }}>
                      {pat.pattern_name}
                    </div>
                    <div style={{ fontSize: 11, color: "#64748b" }}>
                      {pat.parent_topic}
                    </div>
                  </div>

                  <span
                    style={{
                      fontSize: 11,
                      fontFamily: "'JetBrains Mono', monospace",
                      fontWeight: 700,
                      color: pat.completion_pct >= 80 ? "#22c55e" : pat.completion_pct > 0 ? "#818cf8" : "#64748b",
                    }}
                  >
                    {pat.solved_count}/{pat.total_problems}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Pattern Questions Checklist */}
          {selectedPattern && (
            <div
              style={{
                padding: "24px",
                background: "#111522",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                borderRadius: 12,
              }}
            >
              {/* Pattern Header */}
              <div style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.07)", paddingBottom: 16, marginBottom: 16 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
                  <div>
                    <div style={{ fontSize: 11, color: "#818cf8", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 2 }}>
                      {selectedPattern.parent_topic}
                    </div>
                    <h2 style={{ fontSize: 20, fontWeight: 800, color: "#ffffff", margin: 0 }}>
                      {selectedPattern.pattern_name}
                    </h2>
                    <p style={{ fontSize: 13, color: "#94a3b8", margin: 0, marginTop: 4 }}>
                      {selectedPattern.description}
                    </p>
                  </div>

                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 22, fontWeight: 800, color: selectedPattern.completion_pct >= 80 ? "#22c55e" : "#ffffff", fontFamily: "'JetBrains Mono', monospace" }}>
                      {selectedPattern.solved_count} / {selectedPattern.total_problems}
                    </div>
                    <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                      Problems Solved ({selectedPattern.completion_pct}%)
                    </div>
                  </div>
                </div>
              </div>

              {/* Questions List */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {filteredBrowserProblems.map((prob) => (
                  <ProblemRow
                    key={prob.slug}
                    prob={prob}
                    revisionDays={revisionDays}
                    refreshedDaysAgo={refreshedSlugs[prob.slug]}
                    onRefresh={() => markRefreshed(prob.slug)}
                  />
                ))}

                {filteredBrowserProblems.length === 0 && (
                  <div style={{ padding: 40, textAlign: "center", color: "#64748b", fontSize: 13 }}>
                    No questions match the selected company or status filter.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ProblemRow({
  prob,
  revisionDays,
  refreshedDaysAgo,
  onRefresh,
}: {
  prob: CuratedPracticeProblem;
  revisionDays: number;
  refreshedDaysAgo?: number;
  onRefresh: () => void;
}) {
  const tierColor = {
    "Warm-up": "#38bdf8",
    "Core Interview": "#818cf8",
    "Advanced Differentiator": "#f43f5e",
  }[prob.tier] || "#94a3b8";

  const effectiveDaysAgo = refreshedDaysAgo !== undefined ? refreshedDaysAgo : prob.days_since_solved;
  const isDue = prob.is_solved && effectiveDaysAgo != null && effectiveDaysAgo >= revisionDays;

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "10px 14px",
        borderRadius: 8,
        border: isDue
          ? "1px solid rgba(245, 158, 11, 0.4)"
          : prob.is_solved
          ? "1px solid rgba(34, 197, 94, 0.25)"
          : "1px solid var(--border-subtle)",
        background: isDue
          ? "rgba(245, 158, 11, 0.08)"
          : prob.is_solved
          ? "rgba(34, 197, 94, 0.05)"
          : "var(--bg-surface)",
        gap: 12,
        flexWrap: "wrap",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
        {/* Status indicator dot / check */}
        <span
          style={{
            width: 18,
            height: 18,
            borderRadius: "50%",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 10,
            fontWeight: 800,
            background: isDue
              ? "rgba(245, 158, 11, 0.2)"
              : prob.is_solved
              ? "rgba(34, 197, 94, 0.15)"
              : "rgba(255, 255, 255, 0.04)",
            color: isDue ? "#fbbf24" : prob.is_solved ? "#22c55e" : "#64748b",
            border: isDue
              ? "1px solid rgba(245, 158, 11, 0.4)"
              : prob.is_solved
              ? "1px solid rgba(34, 197, 94, 0.3)"
              : "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          {prob.is_solved ? (isDue ? "!" : "✓") : ""}
        </span>

        <span style={{ color: "var(--text-muted)", fontSize: 12, fontFamily: "'JetBrains Mono', monospace", fontWeight: 600 }}>
          #{prob.leetcode_id}
        </span>
        <span style={{ color: "var(--text-primary)", fontWeight: 700, fontSize: 14 }}>
          {prob.title}
        </span>

        <span
          style={{
            fontSize: 10,
            fontWeight: 700,
            padding: "1px 6px",
            borderRadius: 4,
            background: "var(--bg-surface-elevated)",
            color: tierColor,
            border: `1px solid ${tierColor}40`,
          }}
        >
          {prob.tier}
        </span>

        {/* Company badges */}
        {prob.companies && prob.companies.slice(0, 3).map((comp) => (
          <span
            key={comp}
            style={{
              fontSize: 10,
              padding: "1px 6px",
              borderRadius: 4,
              background: "var(--bg-surface-elevated)",
              color: "var(--text-secondary)",
              border: "1px solid var(--border-subtle)",
              fontWeight: 500,
            }}
          >
            {comp}
          </span>
        ))}

        {/* Revision status tag */}
        {prob.is_solved && effectiveDaysAgo != null && (
          <span
            style={{
              fontSize: 10,
              fontWeight: 700,
              padding: "2px 8px",
              borderRadius: 4,
              background: isDue ? "rgba(245, 158, 11, 0.15)" : "rgba(34, 197, 94, 0.1)",
              color: isDue ? "#fbbf24" : "#4ade80",
              border: isDue ? "1px solid rgba(245, 158, 11, 0.35)" : "1px solid rgba(34, 197, 94, 0.25)",
            }}
          >
            {isDue
              ? `Due to Revisit (${effectiveDaysAgo}d ago · overdue by ${effectiveDaysAgo - revisionDays}d)`
              : `Fresh (${effectiveDaysAgo}d ago)`}
          </span>
        )}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        {isDue && (
          <button
            onClick={onRefresh}
            title="Mark this question as reviewed today"
            style={{
              fontSize: 11,
              padding: "4px 8px",
              borderRadius: 4,
              cursor: "pointer",
              background: "rgba(34, 197, 94, 0.1)",
              border: "1px solid rgba(34, 197, 94, 0.3)",
              color: "#4ade80",
              fontWeight: 600,
            }}
          >
            Mark Refreshed
          </button>
        )}

        <span className={difficultyClass(prob.difficulty)} style={{ fontSize: 11 }}>
          {prob.difficulty}
        </span>
        <a
          href={prob.url}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            fontSize: 12,
            padding: "4px 10px",
            borderRadius: 6,
            textDecoration: "none",
            fontWeight: 600,
            color: isDue ? "#fbbf24" : prob.is_solved ? "#94a3b8" : "#818cf8",
            background: isDue ? "rgba(245, 158, 11, 0.15)" : prob.is_solved ? "transparent" : "rgba(99, 102, 241, 0.12)",
            border: isDue ? "1px solid rgba(245, 158, 11, 0.4)" : prob.is_solved ? "1px solid rgba(255, 255, 255, 0.08)" : "1px solid rgba(99, 102, 241, 0.3)",
            transition: "all 0.15s ease",
          }}
        >
          {isDue ? "Review Now ↗" : prob.is_solved ? "Review ↗" : "Solve ↗"}
        </a>
      </div>
    </div>
  );
}

function PracticeSkeleton() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div className="skeleton" style={{ height: 32, width: 260 }} />
      <div className="skeleton" style={{ height: 90, borderRadius: 12 }} />
      <div className="skeleton" style={{ height: 70, borderRadius: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {[...Array(4)].map((_, i) => <div key={i} className="skeleton" style={{ height: 80, borderRadius: 12 }} />)}
      </div>
    </div>
  );
}
