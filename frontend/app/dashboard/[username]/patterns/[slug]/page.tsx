"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, PatternStat } from "@/lib/api";
import { difficultyClass, fmt } from "@/lib/utils";

interface Props { params: Promise<{ username: string; slug: string }> }

export default function PatternDetailPage({ params }: Props) {
  const { username, slug } = use(params);
  const router = useRouter();
  const [data, setData] = useState<PatternStat | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("All");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getPatternDetail(username, slug)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [username, slug]);

  if (loading) return <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
    <div className="skeleton" style={{ height: 40, width: 200 }} />
    <div className="skeleton" style={{ height: 100 }} />
    <div className="skeleton" style={{ height: 300 }} />
  </div>;
  if (error || !data) return (
    <div style={{ textAlign: "center", color: "var(--gray-400)", padding: 60 }}>
      <p>{error || `Pattern not found`}</p>
      <button className="btn-ghost" style={{ marginTop: 16 }} onClick={() => router.back()}>← Back</button>
    </div>
  );

  const filtered = data.problems.filter((p) =>
    filter === "All" || p.difficulty === filter
  );

  return (
    <div className="animate-fade-in-up stagger">
      {/* Breadcrumb */}
      <div style={{ marginBottom: 20, fontSize: 13, color: "var(--gray-500)" }}>
        <Link href={`/dashboard/${username}/patterns`} style={{ color: "var(--brand-400)", textDecoration: "none" }}>
          Patterns
        </Link>
        {" › "}{data.pattern}
      </div>

      {/* Header */}
      <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 4 }}>{data.pattern}</h1>
      <p style={{ fontSize: 14, color: "var(--gray-500)", marginBottom: 28 }}>
        {data.solved_count} problems solved in this pattern
      </p>

      {/* Stat row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 28 }}>
        {[
          { label: "Total", val: data.solved_count, color: "var(--brand-400)" },
          { label: "Easy", val: data.easy, color: "#22c55e" },
          { label: "Medium", val: data.medium, color: "#f59e0b" },
          { label: "Hard", val: data.hard, color: "#ef4444" },
        ].map((s) => (
          <div key={s.label} className="glass-card" style={{ padding: "16px 20px" }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: s.color, lineHeight: 1 }}>{s.val}</div>
            <div className="stat-label" style={{ marginTop: 6 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {["All", "Easy", "Medium", "Hard"].map((d) => (
          <button
            key={d}
            id={`filter-${d.toLowerCase()}`}
            onClick={() => setFilter(d)}
            className="btn-ghost"
            style={{
              fontSize: 13,
              padding: "6px 16px",
              background: filter === d ? "rgba(97,114,243,0.2)" : undefined,
              borderColor: filter === d ? "rgba(97,114,243,0.4)" : undefined,
              color: filter === d ? "var(--brand-400)" : undefined,
            }}
          >
            {d}
          </button>
        ))}
      </div>

      {/* Problems table */}
      <div className="glass-card" style={{ overflow: "hidden" }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Problem</th>
              <th>Difficulty</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p) => (
              <tr key={p.slug}>
                <td style={{ color: "var(--gray-500)", fontSize: 13, fontFamily: "'JetBrains Mono', monospace" }}>
                  {p.leetcode_id || "—"}
                </td>
                <td style={{ fontWeight: 500, color: "var(--gray-100)" }}>{p.title}</td>
                <td><span className={difficultyClass(p.difficulty)}>{p.difficulty}</span></td>
                <td>
                  {p.url ? (
                    <a href={p.url} target="_blank" rel="noopener noreferrer"
                      style={{ color: "var(--brand-400)", fontSize: 13, textDecoration: "none" }}>
                      Open ↗
                    </a>
                  ) : "—"}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--gray-500)", padding: 32 }}>
                No {filter !== "All" ? filter : ""} problems in this pattern.
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
