"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { api, StudentAnalysisResponse } from "@/lib/api";
import { difficultyClass, fmt } from "@/lib/utils";

interface Props { params: Promise<{ username: string }> }

export default function StudentAnalysisPage({ params }: Props) {
  const { username } = use(params);
  const [data, setData] = useState<StudentAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getStudentAnalysis(username)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [username]);

  if (loading) return <AnalysisSkeleton />;
  if (error || !data) return (
    <div style={{ color: "var(--gray-400)", padding: 60, textAlign: "center" }}>
      {error || "Could not load student analysis"}
    </div>
  );

  const { score_breakdown, velocity } = data;

  return (
    <div className="animate-fade-in-up stagger">
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 className="section-title">DSA Student Diagnostic & Readiness</h1>
        <p className="section-subtitle">
          In-depth technical interview readiness report, weakness radar, and personalized practice plan.
        </p>
      </div>

      {/* Hero: Interview Readiness Score */}
      <div
        className="glass-card"
        style={{
          padding: "32px",
          marginBottom: 28,
          background: "linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.08) 100%)",
          border: "1px solid rgba(99, 102, 241, 0.3)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1.8fr", gap: 32, alignItems: "center" }}>
          {/* Left: Big Score & Tier */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", paddingRight: 20, borderRight: "1px solid var(--border-subtle)" }}>
            <span
              style={{
                fontSize: 12,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                color: "var(--brand-500)",
                marginBottom: 10,
              }}
            >
              Interview Readiness Index
            </span>
            <div style={{ position: "relative", display: "inline-block", marginBottom: 12 }}>
              <div
                style={{
                  fontSize: 72,
                  fontWeight: 900,
                  lineHeight: 1,
                  background: "linear-gradient(135deg, #4f46e5 0%, #9333ea 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                {data.readiness_score}
              </div>
              <span style={{ fontSize: 20, color: "var(--text-muted)", fontWeight: 700 }}>/ 100</span>
            </div>

            <div
              style={{
                fontSize: 14,
                fontWeight: 700,
                padding: "6px 18px",
                borderRadius: 20,
                background: "rgba(99, 102, 241, 0.12)",
                border: "1px solid rgba(99, 102, 241, 0.35)",
                color: "var(--brand-500)",
                marginBottom: 10,
              }}
            >
              {data.readiness_badge}
            </div>
            <div style={{ fontSize: 13, color: "var(--text-secondary)", maxWidth: 260 }}>
              Status: <strong style={{ color: "var(--text-primary)" }}>{data.readiness_tier}</strong>
            </div>
          </div>

          {/* Right: 4 Readiness Pillars */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)", marginBottom: 4 }}>
              Evaluation Rubric Breakdown
            </div>

            {Object.entries(score_breakdown).map(([key, val]) => {
              const pct = Math.round((val.score / val.max) * 100);
              return (
                <div key={key}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 6 }}>
                    <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>{val.label}</span>
                    <span style={{ color: "var(--brand-500)", fontWeight: 700 }}>
                      {val.score} / {val.max} pts ({pct}%)
                    </span>
                  </div>
                  <div className="progress-bar" style={{ height: 8 }}>
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${pct}%`,
                        background:
                          pct >= 80 ? "#22c55e" : pct >= 60 ? "linear-gradient(90deg, #6172f3, #a855f7)" : "#f59e0b",
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Two Column Grid: Strengths & Blindspots */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 28 }}>
        {/* Strengths */}
        <div className="glass-card" style={{ padding: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <span style={{ fontSize: 20 }}>💪</span>
            <h2 className="section-title" style={{ fontSize: 17, margin: 0 }}>Proven Interview Strengths</h2>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {data.strengths.map((s, i) => (
              <div
                key={i}
                style={{
                  padding: "14px 16px",
                  borderRadius: 12,
                  background: "rgba(34, 197, 94, 0.05)",
                  border: "1px solid rgba(34, 197, 94, 0.2)",
                  display: "flex",
                  gap: 12,
                  alignItems: "flex-start",
                }}
              >
                <span style={{ fontSize: 22 }}>{s.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                    <span style={{ fontWeight: 700, color: "var(--text-primary)", fontSize: 14 }}>{s.title}</span>
                    <span style={{ fontSize: 12, fontWeight: 700, color: "#16a34a", background: "rgba(34, 197, 94, 0.15)", padding: "2px 8px", borderRadius: 10 }}>
                      {s.metric}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.4 }}>
                    {s.description}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Critical Blindspots */}
        <div className="glass-card" style={{ padding: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <span style={{ fontSize: 20 }}>⚠️</span>
            <h2 className="section-title" style={{ fontSize: 17, margin: 0 }}>High-Priority Blindspots</h2>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {data.blindspots.map((b, i) => (
              <div
                key={i}
                style={{
                  padding: "14px 16px",
                  borderRadius: 12,
                  background: "rgba(239, 68, 68, 0.05)",
                  border: "1px solid rgba(239, 68, 68, 0.25)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <span style={{ fontWeight: 700, color: "var(--text-primary)", fontSize: 13 }}>{b.pattern}</span>
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 800,
                      color: b.priority === "HIGH" ? "#ef4444" : "#f59e0b",
                      background: b.priority === "HIGH" ? "rgba(239, 68, 68, 0.15)" : "rgba(245, 158, 11, 0.15)",
                      padding: "2px 8px",
                      borderRadius: 10,
                      letterSpacing: "0.05em",
                    }}
                  >
                    {b.priority} PRIORITY
                  </span>
                </div>
                <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 8, lineHeight: 1.4 }}>
                  {b.impact}
                </div>
                <div style={{ fontSize: 12, color: "var(--brand-500)", fontWeight: 600 }}>
                  👉 Next step: {b.action}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recommended Problems Action Plan */}
      <div className="glass-card" style={{ padding: 24, marginBottom: 28 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
          <div>
            <h2 className="section-title" style={{ fontSize: 17, margin: 0 }}>
              🎯 Recommended Target Problems (Curated for You)
            </h2>
            <p className="section-subtitle" style={{ margin: 0, marginTop: 4 }}>
              Directly addresses your identified blindspots to elevate your interview score to FAANG readiness.
            </p>
          </div>
          <Link href={`/dashboard/${username}/taxonomy`} className="btn-ghost" style={{ fontSize: 12, padding: "6px 12px" }}>
            Explore All Patterns →
          </Link>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 14 }}>
          {data.recommended_problems.map((rec) => (
            <div
              key={rec.slug}
              style={{
                padding: "16px 18px",
                background: "var(--bg-surface-elevated)",
                border: "1px solid var(--border-subtle)",
                borderRadius: 12,
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: 12,
              }}
            >
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <span style={{ fontSize: 11, color: "var(--brand-500)", fontWeight: 700, textTransform: "uppercase" }}>
                    {rec.topic} · {rec.pattern}
                  </span>
                  <span className={difficultyClass(rec.difficulty)} style={{ fontSize: 11 }}>
                    {rec.difficulty}
                  </span>
                </div>
                <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)", marginBottom: 6 }}>
                  #{rec.leetcode_id} {rec.title}
                </div>
                <div style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.4 }}>
                  {rec.why}
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <a
                  href={`https://leetcode.com/problems/${rec.slug}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary"
                  style={{ fontSize: 12, padding: "6px 14px", textDecoration: "none" }}
                >
                  Solve on LeetCode ↗
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Practice Velocity & Discipline Metrics */}
      <div className="glass-card" style={{ padding: 24 }}>
        <h2 className="section-title" style={{ fontSize: 17, marginBottom: 16 }}>
          ⚡ Practice Velocity & Discipline Summary
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
          <div style={{ background: "var(--bg-surface-elevated)", padding: "16px 18px", borderRadius: 12, border: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: 26, fontWeight: 800, color: "#f59e0b" }}>🔥 {velocity.streak} Days</div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>Current Active Streak</div>
          </div>
          <div style={{ background: "var(--bg-surface-elevated)", padding: "16px 18px", borderRadius: 12, border: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: 26, fontWeight: 800, color: "var(--brand-500)" }}>📅 {velocity.active_days} Days</div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>Total Active Practice Days</div>
          </div>
          <div style={{ background: "var(--bg-surface-elevated)", padding: "16px 18px", borderRadius: 12, border: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: 26, fontWeight: 800, color: "#16a34a" }}>⚡ {velocity.average_per_active_day} / day</div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>Pace per Active Day</div>
          </div>
          <div style={{ background: "var(--bg-surface-elevated)", padding: "16px 18px", borderRadius: 12, border: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: 26, fontWeight: 800, color: "var(--brand-500)" }}>🎯 {velocity.acceptance_rate || 68.3}%</div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>AC Acceptance Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AnalysisSkeleton() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div className="skeleton" style={{ height: 40, width: 340 }} />
      <div className="skeleton" style={{ height: 220, borderRadius: 16 }} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        <div className="skeleton" style={{ height: 260, borderRadius: 14 }} />
        <div className="skeleton" style={{ height: 260, borderRadius: 14 }} />
      </div>
      <div className="skeleton" style={{ height: 280, borderRadius: 14 }} />
    </div>
  );
}
