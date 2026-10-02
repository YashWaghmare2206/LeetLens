"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, PatternsResponse } from "@/lib/api";
import { fmt, CHART_COLORS } from "@/lib/utils";

interface Props { params: Promise<{ username: string }> }

export default function PatternsPage({ params }: Props) {
  const { username } = use(params);
  const router = useRouter();
  const [data, setData] = useState<PatternsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getPatterns(username).then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [username]);

  if (loading) return <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
    {[...Array(8)].map((_, i) => <div key={i} className="skeleton" style={{ height: 64 }} />)}
  </div>;
  if (error || !data) return <div style={{ color: "var(--gray-400)", padding: 60, textAlign: "center" }}>{error || "No data"}</div>;

  const filtered = data.patterns.filter((p) =>
    p.pattern.toLowerCase().includes(search.toLowerCase())
  );
  const maxCount = data.patterns[0]?.solved_count || 1;

  return (
    <div className="animate-fade-in-up stagger">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 className="section-title">DSA Patterns</h1>
          <p className="section-subtitle">{data.patterns.length} patterns practiced • Click any pattern to see exact problems</p>
        </div>
        <input
          id="pattern-search"
          type="text"
          className="input-field"
          placeholder="Search patterns..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 240, padding: "10px 16px", fontSize: 14 }}
        />
      </div>

      {/* Pattern cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {filtered.map((p, i) => {
          const pct = Math.round((p.solved_count / maxCount) * 100);
          const color = CHART_COLORS[i % CHART_COLORS.length];
          return (
            <div
              key={p.pattern_slug}
              id={`pattern-${p.pattern_slug}`}
              className="glass-card"
              style={{ padding: "16px 20px", cursor: "pointer", display: "flex", alignItems: "center", gap: 16 }}
              onClick={() => router.push(`/dashboard/${username}/patterns/${p.pattern_slug}`)}
            >
              {/* Rank */}
              <span style={{ width: 28, fontSize: 12, color: "var(--gray-600)", fontWeight: 700, flexShrink: 0, textAlign: "center" }}>
                #{i + 1}
              </span>

              {/* Name + bar */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <span style={{ fontWeight: 600, fontSize: 14, color: "var(--gray-100)" }}>{p.pattern}</span>
                  <span style={{ fontSize: 13, color, fontWeight: 700 }}>{p.solved_count}</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-bar-fill" style={{ width: `${pct}%`, background: color }} />
                </div>
              </div>

              {/* Difficulty split */}
              <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
                {p.easy > 0 && <span style={{ fontSize: 12, color: "#22c55e" }}>E:{p.easy}</span>}
                {p.medium > 0 && <span style={{ fontSize: 12, color: "#f59e0b" }}>M:{p.medium}</span>}
                {p.hard > 0 && <span style={{ fontSize: 12, color: "#ef4444" }}>H:{p.hard}</span>}
              </div>

              {/* Arrow */}
              <span style={{ color: "var(--gray-600)", fontSize: 14 }}>›</span>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div style={{ textAlign: "center", color: "var(--gray-500)", padding: 40 }}>
            No patterns matching &quot;{search}&quot;
          </div>
        )}
      </div>
    </div>
  );
}
