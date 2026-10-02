"use client";

import { use, useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { api, ProblemsResponse, TaxonomyExplorerResponse } from "@/lib/api";
import { difficultyClass } from "@/lib/utils";

interface Props { params: Promise<{ username: string }> }

const PRESETS = [3, 7, 14, 21, 30];

interface RevisitProblemItem {
  id: number;
  title: string;
  slug: string;
  difficulty: string;
  url: string;
  solved_at?: string | null;
  days_ago: number;
  topics: string[];
  pattern?: string;
  tier?: string;
}

export default function RevisitQueuePage({ params }: Props) {
  const { username } = use(params);

  const [problemsData, setProblemsData] = useState<ProblemsResponse | null>(null);
  const [taxonomyData, setTaxonomyData] = useState<TaxonomyExplorerResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // User-configurable revisit interval in days (default 14, saved to localStorage)
  const [revisionDays, setRevisionDays] = useState<number>(14);

  const [urgencyFilter, setUrgencyFilter] = useState<"all_due" | "due_soon" | "fresh" | "all_solved">("all_due");
  const [diffFilter, setDiffFilter] = useState<string>("All");
  const [selectedTopic, setSelectedTopic] = useState<string>("All"); // Default: All topics
  const [search, setSearch] = useState<string>("");

  // Local state for problems marked as refreshed today
  const [refreshedSlugs, setRefreshedSlugs] = useState<Record<string, number>>({});

  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("leetlens_revision_days");
      if (saved) {
        const val = parseInt(saved, 10);
        if (!isNaN(val) && val > 0) setRevisionDays(val);
      }
      const savedRefreshed = localStorage.getItem(`leetlens_refreshed_${username}`);
      if (savedRefreshed) {
        try {
          setRefreshedSlugs(JSON.parse(savedRefreshed));
        } catch {}
      }
    }

    Promise.all([
      api.getProblems(username),
      api.getTaxonomyExplorer(username).catch(() => null),
    ])
      .then(([probs, tax]) => {
        setProblemsData(probs);
        setTaxonomyData(tax);
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

  const markProblemRefreshed = (slug: string) => {
    const next = { ...refreshedSlugs, [slug]: 0 };
    setRefreshedSlugs(next);
    if (typeof window !== "undefined") {
      localStorage.setItem(`leetlens_refreshed_${username}`, JSON.stringify(next));
    }
  };

  const slugToTopicsMap = useMemo(() => {
    const map = new Map<string, Set<string>>();
    if (!taxonomyData) return map;

    taxonomyData.topics.forEach((t) => {
      t.patterns.forEach((pat) => {
        pat.problems.forEach((prob) => {
          if (!map.has(prob.slug)) {
            map.set(prob.slug, new Set());
          }
          map.get(prob.slug)!.add(t.topic_name);
        });
      });
    });

    return map;
  }, [taxonomyData]);

  const allSolvedItems: RevisitProblemItem[] = useMemo(() => {
    if (!problemsData) return [];

    const now = Date.now();

    return problemsData.problems.map((p) => {
      let daysAgo = 0;
      if (p.solved_at) {
        const t = new Date(p.solved_at).getTime();
        if (!isNaN(t)) {
          daysAgo = Math.max(0, Math.floor((now - t) / (1000 * 60 * 60 * 24)));
        }
      }

      if (refreshedSlugs[p.slug] !== undefined) {
        daysAgo = refreshedSlugs[p.slug];
      }

      // Get topics from taxonomy explorer or backend problem topics
      const topicsSet = slugToTopicsMap.get(p.slug) || new Set<string>();
      if (p.topics) {
        p.topics.forEach((top: string) => topicsSet.add(top));
      }
      const topicsList = Array.from(topicsSet);

      return {
        id: p.leetcode_id || 0,
        title: p.title,
        slug: p.slug,
        difficulty: p.difficulty,
        url: p.url || `https://leetcode.com/problems/${p.slug}/`,
        solved_at: p.solved_at || null,
        days_ago: daysAgo,
        topics: topicsList.length > 0 ? topicsList : ["General DSA"],
      };
    });
  }, [problemsData, slugToTopicsMap, refreshedSlugs]);

  // Extract all unique topics that have solved questions
  const availableTopics = useMemo(() => {
    const set = new Set<string>();
    allSolvedItems.forEach((item) => {
      item.topics.forEach((t) => set.add(t));
    });
    return Array.from(set).sort();
  }, [allSolvedItems]);

  // Buckets based on user-set revisionDays
  const { overdueItems, dueSoonItems, freshItems } = useMemo(() => {
    const overdue: RevisitProblemItem[] = [];
    const dueSoon: RevisitProblemItem[] = [];
    const fresh: RevisitProblemItem[] = [];

    allSolvedItems.forEach((item) => {
      if (item.days_ago >= revisionDays) {
        overdue.push(item);
      } else if (item.days_ago >= Math.max(1, revisionDays - 3)) {
        dueSoon.push(item);
      } else {
        fresh.push(item);
      }
    });

    overdue.sort((a, b) => b.days_ago - a.days_ago);
    dueSoon.sort((a, b) => b.days_ago - a.days_ago);
    fresh.sort((a, b) => a.days_ago - b.days_ago);

    return { overdueItems: overdue, dueSoonItems: dueSoon, freshItems: fresh };
  }, [allSolvedItems, revisionDays]);

  const filteredItems = useMemo(() => {
    let source: RevisitProblemItem[] = [];
    if (urgencyFilter === "all_due") source = overdueItems;
    else if (urgencyFilter === "due_soon") source = dueSoonItems;
    else if (urgencyFilter === "fresh") source = freshItems;
    else source = allSolvedItems;

    return source.filter((item) => {
      if (diffFilter !== "All" && item.difficulty !== diffFilter) return false;
      if (selectedTopic !== "All" && !item.topics.includes(selectedTopic)) {
        return false;
      }
      if (search) {
        const q = search.toLowerCase();
        const matchTitle = item.title.toLowerCase().includes(q);
        const matchId = String(item.id).includes(q);
        const matchSlug = item.slug.toLowerCase().includes(q);
        if (!matchTitle && !matchId && !matchSlug) return false;
      }
      return true;
    });
  }, [allSolvedItems, overdueItems, dueSoonItems, freshItems, urgencyFilter, diffFilter, selectedTopic, search]);

  if (loading) return <RevisitSkeleton />;
  if (error) return (
    <div style={{ color: "#94a3b8", padding: 60, textAlign: "center" }}>
      <p style={{ fontSize: 16, color: "#f87171" }}>{error || "Could not load spaced repetition revisit queue"}</p>
    </div>
  );

  return (
    <div className="animate-fade-in-up stagger">
      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "#818cf8" }}>
            Spaced Repetition & Retention
          </span>
          <span style={{ fontSize: 11, color: "#64748b" }}>•</span>
          <span style={{ fontSize: 12, color: "#94a3b8" }}>
            Review Schedule & Topic Filter
          </span>
        </div>
        <h1 className="section-title" style={{ fontSize: 24, fontWeight: 800, color: "#ffffff", letterSpacing: "-0.01em" }}>
          Spaced Repetition Revisit Hub
        </h1>
        <p className="section-subtitle" style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>
          Set your preferred memory interval. Problems you solved previously will automatically appear here when they are due for an interview refresher.
        </p>
      </div>

      {/* Revisit Schedule Controller Banner */}
      <div
        className="glass-card"
        style={{
          padding: "20px 24px",
          borderRadius: 12,
          marginBottom: 20,
          display: "flex",
          flexDirection: "column",
          gap: 16,
        }}
      >
        {/* Row 1: Retention Health & Setting */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: 12,
                background: "rgba(99, 102, 241, 0.15)",
                border: "1px solid rgba(99, 102, 241, 0.3)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 22,
              }}
            >
              ⏱️
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: "var(--brand-400)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 2 }}>
                Custom Review Interval
              </div>
              <div style={{ fontSize: 18, fontWeight: 800, color: "var(--text-primary)", fontFamily: "'JetBrains Mono', monospace" }}>
                Revisit Every {revisionDays} Days
              </div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                Questions older than {revisionDays} days are flagged for an interview refresher
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 24, fontWeight: 800, color: overdueItems.length > 0 ? "#fbbf24" : "#22c55e", fontFamily: "'JetBrains Mono', monospace" }}>
                {overdueItems.length}
              </div>
              <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 700 }}>
                Problems Due Now
              </div>
            </div>
          </div>
        </div>

        {/* Row 2: Preset Buttons & Custom Input */}
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
            gap: 12,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-primary)" }}>
              Change Schedule:
            </span>

            <div style={{ display: "flex", gap: 4 }}>
              {PRESETS.map((p) => {
                const isActive = revisionDays === p;
                return (
                  <button
                    key={p}
                    onClick={() => handleSetRevisionDays(p)}
                    style={{
                      fontSize: 11,
                      padding: "4px 10px",
                      borderRadius: 6,
                      cursor: "pointer",
                      border: isActive ? "1px solid var(--brand-500)" : "1px solid var(--border-subtle)",
                      background: isActive ? "var(--brand-500)" : "transparent",
                      color: isActive ? "#ffffff" : "var(--text-secondary)",
                      fontWeight: isActive ? 700 : 500,
                    }}
                  >
                    {p} Days {p === 7 ? "(Weekly)" : p === 14 ? "(Bi-weekly)" : p === 30 ? "(Monthly)" : ""}
                  </button>
                );
              })}
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 11, color: "var(--text-muted)" }}>or custom:</span>
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
                  width: 52,
                  padding: "3px 6px",
                  fontSize: 12,
                  background: "var(--bg-surface)",
                  border: "1px solid var(--border-subtle)",
                  color: "var(--text-primary)",
                  borderRadius: 4,
                  textAlign: "center",
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              />
              <span style={{ fontSize: 11, color: "var(--text-muted)" }}>days</span>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Tabs Toolbar */}
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
        {/* Row 1: Urgency Category Tabs */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <button
              onClick={() => setUrgencyFilter("all_due")}
              className={`btn-ghost ${urgencyFilter === "all_due" ? "pill-active" : ""}`}
              style={{
                fontSize: 12,
                padding: "6px 14px",
                fontWeight: urgencyFilter === "all_due" ? 700 : 500,
                color: urgencyFilter === "all_due" ? "#fbbf24" : undefined,
                borderColor: urgencyFilter === "all_due" ? "rgba(245, 158, 11, 0.5)" : undefined,
              }}
            >
              ⚠ Due to Revisit ({overdueItems.length})
            </button>

            <button
              onClick={() => setUrgencyFilter("due_soon")}
              className={`btn-ghost ${urgencyFilter === "due_soon" ? "pill-active" : ""}`}
              style={{ fontSize: 12, padding: "6px 14px", fontWeight: urgencyFilter === "due_soon" ? 700 : 500 }}
            >
              Due Soon ({dueSoonItems.length})
            </button>

            <button
              onClick={() => setUrgencyFilter("fresh")}
              className={`btn-ghost ${urgencyFilter === "fresh" ? "pill-active" : ""}`}
              style={{ fontSize: 12, padding: "6px 14px", fontWeight: urgencyFilter === "fresh" ? 700 : 500 }}
            >
              ✓ Fresh ({freshItems.length})
            </button>

            <button
              onClick={() => setUrgencyFilter("all_solved")}
              className={`btn-ghost ${urgencyFilter === "all_solved" ? "pill-active" : ""}`}
              style={{ fontSize: 12, padding: "6px 14px", fontWeight: urgencyFilter === "all_solved" ? 700 : 500 }}
            >
              All Solved ({allSolvedItems.length})
            </button>
          </div>

          <input
            type="text"
            className="input-field"
            placeholder="Search problems in revisit queue..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 230, padding: "6px 12px", fontSize: 12 }}
          />
        </div>

        {/* Row 2: Secondary Difficulty & Topic Selector Dropdown */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, paddingTop: 6, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            {/* Difficulty Tabs */}
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginRight: 2 }}>
                Difficulty:
              </span>
              {["All", "Easy", "Medium", "Hard"].map((d) => (
                <button
                  key={d}
                  onClick={() => setDiffFilter(d)}
                  className={`btn-ghost ${diffFilter === d ? "pill-active" : ""}`}
                  style={{ fontSize: 11, padding: "3px 8px" }}
                >
                  {d}
                </button>
              ))}
            </div>

            {/* Topic Selector Dropdown (Default: All) */}
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: "#818cf8", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Topic:
              </span>
              <select
                id="topic-selector-dropdown"
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                style={{
                  background: "var(--bg-surface-elevated)",
                  color: "var(--text-primary)",
                  border: "1px solid var(--border-medium)",
                  borderRadius: 6,
                  padding: "4px 10px",
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: "pointer",
                  outline: "none",
                }}
              >
                <option value="All">All Topics ({allSolvedItems.length})</option>
                {availableTopics.map((topName) => {
                  const count = allSolvedItems.filter((it) => it.topics.includes(topName)).length;
                  return (
                    <option key={topName} value={topName}>
                      {topName} ({count})
                    </option>
                  );
                })}
              </select>
            </div>
          </div>

          <div style={{ fontSize: 11, color: "#64748b" }}>
            Showing {filteredItems.length} questions {selectedTopic !== "All" ? `in ${selectedTopic}` : ""}
          </div>
        </div>
      </div>

      {/* Problems Revisit List */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {filteredItems.map((item) => {
          const isOverdue = item.days_ago >= revisionDays;
          const overdueBy = item.days_ago - revisionDays;

          return (
            <div
              key={item.slug}
              className="glass-card"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "12px 18px",
                borderRadius: 10,
                border: isOverdue ? "1px solid rgba(245, 158, 11, 0.4)" : "1px solid var(--border-subtle)",
                background: isOverdue ? "rgba(245, 158, 11, 0.08)" : "var(--bg-surface)",
                gap: 12,
                flexWrap: "wrap",
                transition: "all 0.15s ease",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                {/* Status Dot */}
                <span
                  style={{
                    width: 20,
                    height: 20,
                    borderRadius: "50%",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 11,
                    fontWeight: 800,
                    background: isOverdue ? "rgba(245, 158, 11, 0.2)" : "rgba(34, 197, 94, 0.15)",
                    color: isOverdue ? "#fbbf24" : "#22c55e",
                    border: isOverdue ? "1px solid rgba(245, 158, 11, 0.4)" : "1px solid rgba(34, 197, 94, 0.3)",
                  }}
                >
                  {isOverdue ? "!" : "✓"}
                </span>

                <span style={{ color: "var(--text-muted)", fontSize: 12, fontFamily: "'JetBrains Mono', monospace", fontWeight: 600 }}>
                  #{item.id || "—"}
                </span>

                <span style={{ color: "var(--text-primary)", fontWeight: 700, fontSize: 14 }}>
                  {item.title}
                </span>

                <span className={difficultyClass(item.difficulty)} style={{ fontSize: 11 }}>
                  {item.difficulty}
                </span>

                {/* Topic tags (replaces company tags) */}
                {item.topics && item.topics.map((t) => (
                  <span
                    key={t}
                    style={{
                      fontSize: 10,
                      padding: "2px 7px",
                      borderRadius: 4,
                      background: "var(--bg-surface-elevated)",
                      color: "var(--brand-400)",
                      border: "1px solid var(--border-subtle)",
                      fontWeight: 600,
                    }}
                  >
                    {t}
                  </span>
                ))}

                {/* Overdue / Fresh Status Badge */}
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: 4,
                    background: isOverdue ? "rgba(245, 158, 11, 0.15)" : "rgba(34, 197, 94, 0.1)",
                    color: isOverdue ? "#fbbf24" : "#4ade80",
                    border: isOverdue ? "1px solid rgba(245, 158, 11, 0.35)" : "1px solid rgba(34, 197, 94, 0.25)",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                  }}
                >
                  {isOverdue
                    ? `Due to Revisit (${item.days_ago}d ago • overdue by ${overdueBy}d)`
                    : `Fresh (${item.days_ago}d ago)`}
                </span>
              </div>

              {/* Action Buttons */}
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                {isOverdue && (
                  <button
                    onClick={() => markProblemRefreshed(item.slug)}
                    title="Mark this question as reviewed today to reset its timer"
                    style={{
                      fontSize: 11,
                      padding: "5px 10px",
                      borderRadius: 6,
                      cursor: "pointer",
                      background: "rgba(34, 197, 94, 0.1)",
                      border: "1px solid rgba(34, 197, 94, 0.3)",
                      color: "#4ade80",
                      fontWeight: 600,
                      transition: "all 0.15s ease",
                    }}
                  >
                    Mark Refreshed ✓
                  </button>
                )}

                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    fontSize: 12,
                    padding: "5px 12px",
                    borderRadius: 6,
                    textDecoration: "none",
                    fontWeight: 600,
                    color: isOverdue ? "#fbbf24" : "#818cf8",
                    background: isOverdue ? "rgba(245, 158, 11, 0.15)" : "rgba(99, 102, 241, 0.12)",
                    border: isOverdue ? "1px solid rgba(245, 158, 11, 0.4)" : "1px solid rgba(99, 102, 241, 0.3)",
                    transition: "all 0.15s ease",
                  }}
                >
                  {isOverdue ? "Solve Again ↗" : "Review ↗"}
                </a>
              </div>
            </div>
          );
        })}

        {filteredItems.length === 0 && (
          <div
            className="glass-card"
            style={{
              padding: 60,
              textAlign: "center",
              borderRadius: 12,
            }}
          >
            <div style={{ fontSize: 32, marginBottom: 12 }}>🎉</div>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", marginBottom: 6 }}>
              {urgencyFilter === "all_due"
                ? `All Caught Up! No problems in ${selectedTopic !== "All" ? selectedTopic : "any topic"} are due for revision based on your ${revisionDays}-day schedule.`
                : "No problems match your selected filters."}
            </h3>
            <p style={{ fontSize: 13, color: "var(--text-secondary)", maxWidth: 440, margin: "0 auto" }}>
              {urgencyFilter === "all_due"
                ? `You've practiced these problems within the last ${revisionDays} days. Try shortening your interval above if you want more aggressive review cycles.`
                : "Try selecting another topic, urgency tab, or clearing your search filter."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function RevisitSkeleton() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div className="skeleton" style={{ height: 32, width: 260 }} />
      <div className="skeleton" style={{ height: 110, borderRadius: 12 }} />
      <div className="skeleton" style={{ height: 60, borderRadius: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {[...Array(6)].map((_, i) => <div key={i} className="skeleton" style={{ height: 52, borderRadius: 8 }} />)}
      </div>
    </div>
  );
}
