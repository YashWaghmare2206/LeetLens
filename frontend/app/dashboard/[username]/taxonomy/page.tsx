"use client";

import { use, useEffect, useState, useMemo } from "react";
import { api, TaxonomyExplorerResponse } from "@/lib/api";
import { difficultyClass } from "@/lib/utils";

interface Props { params: Promise<{ username: string }> }

export default function TaxonomyExplorerPage({ params }: Props) {
  const { username } = use(params);
  const [data, setData] = useState<TaxonomyExplorerResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedTopicSlug, setSelectedTopicSlug] = useState<string>("");
  const [expandedPattern, setExpandedPattern] = useState<string | null>(null);
  const [masteryFilter, setMasteryFilter] = useState<string>("All");
  const [topicTabFilter, setTopicTabFilter] = useState<"all" | "solved">("solved");
  const [topicSearch, setTopicSearch] = useState<string>("");
  const [patternSearch, setPatternSearch] = useState<string>("");

  useEffect(() => {
    api.getTaxonomyExplorer(username)
      .then((res) => {
        setData(res);
        if (res.topics.length > 0) {
          // Select the first topic with solved problems, or fallback to first
          const firstWithSolved = res.topics.find((t) => t.solved_count > 0);
          setSelectedTopicSlug(firstWithSolved ? firstWithSolved.topic_slug : res.topics[0].topic_slug);
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [username]);

  const visibleTopics = useMemo(() => {
    if (!data) return [];
    return data.topics.filter((t) => {
      if (topicTabFilter === "solved" && t.solved_count === 0) return false;
      if (topicSearch) {
        const q = topicSearch.toLowerCase();
        return t.topic_name.toLowerCase().includes(q) || t.description.toLowerCase().includes(q);
      }
      return true;
    });
  }, [data, topicTabFilter, topicSearch]);

  if (loading) return <ExplorerSkeleton />;
  if (error || !data) return (
    <div style={{ color: "#94a3b8", padding: 60, textAlign: "center" }}>
      <p style={{ fontSize: 16, color: "#f87171" }}>{error || "Could not load topic & pattern taxonomy"}</p>
    </div>
  );

  const selectedTopic = data.topics.find((t) => t.topic_slug === selectedTopicSlug) || visibleTopics[0] || data.topics[0];

  const filteredPatterns = (selectedTopic?.patterns || []).filter((p) => {
    if (masteryFilter !== "All" && p.mastery !== masteryFilter) return false;
    if (patternSearch) {
      const q = patternSearch.toLowerCase();
      const matchName = p.pattern_name.toLowerCase().includes(q);
      const matchDesc = p.description.toLowerCase().includes(q);
      const matchProb = p.problems.some((pr) => pr.title.toLowerCase().includes(q));
      if (!matchName && !matchDesc && !matchProb) return false;
    }
    return true;
  });

  const solvedTopicsCount = data.topics.filter((t) => t.solved_count > 0).length;

  return (
    <div className="animate-fade-in-up stagger">
      {/* Page Header */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "#818cf8" }}>
            Curriculum & Skill Taxonomy
          </span>
          <span style={{ fontSize: 11, color: "#64748b" }}>•</span>
          <span style={{ fontSize: 12, color: "#94a3b8" }}>
            {solvedTopicsCount} of {data.total_topics} LeetCode Topics Practiced
          </span>
        </div>
        <h1 className="section-title" style={{ fontSize: 24, fontWeight: 800, color: "#ffffff", letterSpacing: "-0.01em" }}>
          Topic & Pattern Breakdown
        </h1>
        <p className="section-subtitle" style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>
          All {data.total_topics} canonical DSA topics tracked on LeetCode with underlying algorithmic patterns, solved problems, and recommended next questions.
        </p>
      </div>

      {/* Topics Control Bar (Search + Solved vs All Filter) */}
      <div
        className="glass-card"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 12,
          padding: "12px 16px",
          borderRadius: 12,
          marginBottom: 16,
        }}
      >
        <div style={{ display: "flex", gap: 8 }}>
          <button
            onClick={() => setTopicTabFilter("solved")}
            className={`btn-ghost ${topicTabFilter === "solved" ? "pill-active" : ""}`}
            style={{ fontSize: 12, padding: "6px 14px", fontWeight: 700 }}
          >
            Practiced on LeetCode ({solvedTopicsCount})
          </button>
          <button
            onClick={() => setTopicTabFilter("all")}
            className={`btn-ghost ${topicTabFilter === "all" ? "pill-active" : ""}`}
            style={{ fontSize: 12, padding: "6px 14px", fontWeight: 700 }}
          >
            All Canonical Topics ({data.total_topics})
          </button>
        </div>

        <input
          type="text"
          className="input-field"
          placeholder="Filter topics by name..."
          value={topicSearch}
          onChange={(e) => setTopicSearch(e.target.value)}
          style={{ width: 220, padding: "6px 12px", fontSize: 12 }}
        />
      </div>

      {/* Topic Horizontal Selector Pills */}
      <div
        style={{
          display: "flex",
          gap: 8,
          overflowX: "auto",
          paddingBottom: 10,
          marginBottom: 20,
          scrollbarWidth: "thin",
        }}
      >
        {visibleTopics.map((t) => {
          const isSelected = t.topic_slug === selectedTopicSlug;
          return (
            <button
              key={t.topic_slug}
              onClick={() => {
                setSelectedTopicSlug(t.topic_slug);
                setExpandedPattern(null);
              }}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "8px 14px",
                borderRadius: 8,
                border: isSelected ? "1px solid var(--brand-500)" : "1px solid var(--border-subtle)",
                background: isSelected ? "var(--bg-surface-elevated)" : "var(--bg-surface)",
                color: isSelected ? "var(--text-primary)" : "var(--text-secondary)",
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.15s ease",
                fontWeight: isSelected ? 700 : 500,
                fontSize: 12,
              }}
            >
              <span>{t.topic_name}</span>
              <span
                style={{
                  fontSize: 11,
                  fontFamily: "'JetBrains Mono', monospace",
                  background: isSelected ? "#4f46e5" : "rgba(255, 255, 255, 0.06)",
                  color: isSelected ? "#ffffff" : "#64748b",
                  padding: "1px 6px",
                  borderRadius: 6,
                  fontWeight: 600,
                }}
              >
                {t.solved_count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Selected Topic Summary Header */}
      {selectedTopic && (
        <div
          className="glass-card"
          style={{
            padding: "20px 24px",
            marginBottom: 20,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 16,
            borderRadius: 12,
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
              <span
                style={{
                  fontSize: 10,
                  fontFamily: "'JetBrains Mono', monospace",
                  fontWeight: 800,
                  padding: "2px 8px",
                  borderRadius: 6,
                  background: "rgba(99, 102, 241, 0.15)",
                  color: "#818cf8",
                  border: "1px solid rgba(99, 102, 241, 0.3)",
                }}
              >
                {selectedTopic.icon}
              </span>
              <h2 style={{ fontSize: 20, fontWeight: 800, color: "#ffffff", margin: 0 }}>
                {selectedTopic.topic_name}
              </h2>
            </div>
            <p style={{ fontSize: 13, color: "#94a3b8", margin: 0 }}>
              {selectedTopic.description}
            </p>
          </div>

          <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 22, fontWeight: 800, color: "#ffffff", fontFamily: "'JetBrains Mono', monospace" }}>
                {selectedTopic.solved_count}
              </div>
              <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 700 }}>
                Solved on LeetCode
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 22, fontWeight: 800, color: "#22c55e", fontFamily: "'JetBrains Mono', monospace" }}>
                {selectedTopic.patterns_mastered} / {selectedTopic.patterns_count}
              </div>
              <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 700 }}>
                Patterns Mastered
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filter by Mastery & Search */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 6 }}>
          {["All", "Mastered", "Proficient", "Practiced", "Untouched"].map((m) => (
            <button
              key={m}
              onClick={() => setMasteryFilter(m)}
              className={`btn-ghost ${masteryFilter === m ? "pill-active" : ""}`}
              style={{
                fontSize: 12,
                padding: "5px 12px",
                fontWeight: masteryFilter === m ? 700 : 500,
              }}
            >
              {m}
            </button>
          ))}
        </div>

        <input
          type="text"
          className="input-field"
          placeholder="Filter patterns or problems..."
          value={patternSearch}
          onChange={(e) => setPatternSearch(e.target.value)}
          style={{ width: 220, padding: "6px 12px", fontSize: 12 }}
        />
      </div>

      {/* Pattern Cards List */}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {filteredPatterns.map((pat) => {
          const isExpanded = expandedPattern === pat.pattern_name;
          const dotColor = {
            Mastered: "#22c55e",
            Proficient: "#818cf8",
            Practiced: "#f59e0b",
            Untouched: "#64748b",
          }[pat.mastery] || "#64748b";

          return (
            <div
              key={pat.pattern_name}
              className="glass-card"
              style={{
                padding: "16px 20px",
                borderRadius: 12,
                transition: "all 0.15s ease",
              }}
            >
              {/* Pattern Card Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
                <div style={{ flex: 1, minWidth: 260 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                    <h3 style={{ fontSize: 15, fontWeight: 700, color: "#ffffff", margin: 0 }}>
                      {pat.pattern_name}
                    </h3>
                    <span
                      style={{
                        fontSize: 11,
                        padding: "2px 8px",
                        borderRadius: 6,
                        background: "rgba(255, 255, 255, 0.04)",
                        border: "1px solid rgba(255, 255, 255, 0.07)",
                        color: dotColor,
                        fontWeight: 600,
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 6,
                      }}
                    >
                      <span style={{ width: 6, height: 6, borderRadius: "50%", background: dotColor }} />
                      {pat.mastery}
                    </span>
                  </div>
                  <p style={{ fontSize: 12, color: "#94a3b8", margin: 0, lineHeight: 1.4 }}>
                    {pat.description}
                  </p>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  {/* Difficulty counts */}
                  {pat.solved_count > 0 && (
                    <div style={{ display: "flex", gap: 8, fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }}>
                      {pat.easy > 0 && <span style={{ color: "#22c55e", fontWeight: 600 }}>{pat.easy}E</span>}
                      {pat.medium > 0 && <span style={{ color: "#f59e0b", fontWeight: 600 }}>{pat.medium}M</span>}
                      {pat.hard > 0 && <span style={{ color: "#ef4444", fontWeight: 600 }}>{pat.hard}H</span>}
                    </div>
                  )}

                  <div style={{ textAlign: "right", minWidth: 44 }}>
                    <span style={{ fontSize: 18, fontWeight: 800, color: pat.solved_count > 0 ? "#ffffff" : "#475569", fontFamily: "'JetBrains Mono', monospace" }}>
                      {pat.solved_count}
                    </span>
                    <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase" }}>solved</div>
                  </div>

                  <button
                    onClick={() => setExpandedPattern(isExpanded ? null : pat.pattern_name)}
                    className="btn-ghost"
                    style={{ fontSize: 12, padding: "6px 12px" }}
                  >
                    {isExpanded ? "Hide Details" : "View Problems"}
                  </button>
                </div>
              </div>

              {/* Expanded Details Section */}
              {isExpanded && (
                <div style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.08)" }}>
                  <div style={{ display: "grid", gridTemplateColumns: pat.problems.length > 0 ? "1fr 1fr" : "1fr", gap: 20 }}>
                    {/* Solved Problems in Pattern */}
                    {pat.problems.length > 0 && (
                      <div>
                        <div style={{ fontSize: 12, fontWeight: 700, color: "#cbd5e1", marginBottom: 8 }}>
                          Solved Problems in this Pattern ({pat.problems.length})
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: 6, maxHeight: 220, overflowY: "auto" }}>
                          {pat.problems.map((p) => (
                            <div
                              key={p.slug}
                              style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                padding: "8px 12px",
                                background: "#0d111a",
                                border: "1px solid rgba(255, 255, 255, 0.06)",
                                borderRadius: 6,
                                fontSize: 12,
                              }}
                            >
                              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <span style={{ color: "#64748b", fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }}>
                                  #{p.leetcode_id || "—"}
                                </span>
                                <span style={{ color: "#f1f5f9", fontWeight: 500 }}>{p.title}</span>
                              </div>
                              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <span className={difficultyClass(p.difficulty)} style={{ fontSize: 11 }}>{p.difficulty}</span>
                                {p.url && (
                                  <a href={p.url} target="_blank" rel="noopener noreferrer" style={{ color: "#818cf8", textDecoration: "none" }}>
                                    ↗
                                  </a>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recommended Next Problems */}
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 700, color: "#cbd5e1", marginBottom: 8 }}>
                        Recommended Interview Problems to Level Up
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        {pat.recommended_problems && pat.recommended_problems.length > 0 ? (
                          pat.recommended_problems.map((rec) => (
                            <div
                              key={rec.slug}
                              style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                padding: "8px 12px",
                                background: "#131a2b",
                                border: "1px solid rgba(99, 102, 241, 0.2)",
                                borderRadius: 6,
                                fontSize: 12,
                              }}
                            >
                              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <span style={{ color: "#818cf8", fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }}>
                                  #{rec.leetcode_id}
                                </span>
                                <span style={{ color: "#ffffff", fontWeight: 600 }}>{rec.title}</span>
                              </div>
                              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <span className={difficultyClass(rec.difficulty)} style={{ fontSize: 11 }}>{rec.difficulty}</span>
                                <a
                                  href={`https://leetcode.com/problems/${rec.slug}/`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{ color: "#818cf8", fontSize: 11, textDecoration: "none", fontWeight: 600 }}
                                >
                                  Solve ↗
                                </a>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div style={{ color: "#64748b", fontSize: 12 }}>All curated recommendations completed.</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {filteredPatterns.length === 0 && (
          <div style={{ padding: 40, textAlign: "center", color: "#64748b", fontSize: 13 }}>
            No patterns match the selected filter.
          </div>
        )}
      </div>
    </div>
  );
}

function ExplorerSkeleton() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div className="skeleton" style={{ height: 32, width: 240 }} />
      <div style={{ display: "flex", gap: 8 }}>
        {[...Array(6)].map((_, i) => <div key={i} className="skeleton" style={{ height: 36, width: 110, borderRadius: 8 }} />)}
      </div>
      <div className="skeleton" style={{ height: 80, borderRadius: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {[...Array(4)].map((_, i) => <div key={i} className="skeleton" style={{ height: 70, borderRadius: 12 }} />)}
      </div>
    </div>
  );
}
