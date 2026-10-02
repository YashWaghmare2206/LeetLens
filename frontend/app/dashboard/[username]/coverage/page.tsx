"use client";

import { use, useEffect, useState } from "react";
import { api, CoverageResponse } from "@/lib/api";
import { fmt } from "@/lib/utils";

interface Props { params: Promise<{ username: string }> }

export default function CoveragePage({ params }: Props) {
  const { username } = use(params);
  const [data, setData] = useState<CoverageResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [showOnly, setShowOnly] = useState<"all" | "practiced" | "missing">("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getCoverage(username).then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [username]);

  if (loading) return <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
    {[...Array(6)].map((_, i) => <div key={i} className="skeleton" style={{ height: 60 }} />)}
  </div>;
  if (error || !data) return <div style={{ color: "var(--gray-400)", padding: 60, textAlign: "center" }}>{error || "No data"}</div>;

  const filtered = data.items.filter((item) => {
    if (showOnly === "practiced") return item.practiced;
    if (showOnly === "missing") return !item.practiced;
    return true;
  });

  const coveragePct = Math.round(data.coverage_ratio * 100);

  return (
    <div className="animate-fade-in-up stagger">
      <div style={{ marginBottom: 28 }}>
        <h1 className="section-title">Pattern Coverage</h1>
        <p className="section-subtitle">How much of the DSA taxonomy you've practiced</p>
      </div>

      {/* Summary cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 28 }}>
        <div className="glass-card" style={{ padding: "20px 24px" }}>
          <div style={{ fontSize: 40, fontWeight: 800, color: "var(--brand-400)", lineHeight: 1 }}>{coveragePct}%</div>
          <div className="stat-label" style={{ marginTop: 8 }}>Coverage</div>
        </div>
        <div className="glass-card" style={{ padding: "20px 24px" }}>
          <div style={{ fontSize: 40, fontWeight: 800, color: "#22c55e", lineHeight: 1 }}>{data.practiced_count}</div>
          <div className="stat-label" style={{ marginTop: 8 }}>Practiced</div>
        </div>
        <div className="glass-card" style={{ padding: "20px 24px" }}>
          <div style={{ fontSize: 40, fontWeight: 800, color: "#ef4444", lineHeight: 1 }}>
            {data.total_patterns - data.practiced_count}
          </div>
          <div className="stat-label" style={{ marginTop: 8 }}>Not Yet Practiced</div>
        </div>
      </div>

      {/* Big progress bar */}
      <div className="glass-card" style={{ padding: 24, marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
          <span style={{ fontSize: 14, color: "var(--gray-300)" }}>Overall DSA Coverage</span>
          <span style={{ fontSize: 14, fontWeight: 700, color: "var(--brand-400)" }}>{data.practiced_count}/{data.total_patterns}</span>
        </div>
        <div className="progress-bar" style={{ height: 12 }}>
          <div className="progress-bar-fill" style={{
            width: `${coveragePct}%`,
            background: "linear-gradient(90deg, #6172f3 0%, #a855f7 100%)",
          }} />
        </div>
      </div>

      {/* Filter tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {[
          { key: "all", label: `All (${data.total_patterns})` },
          { key: "practiced", label: `✅ Practiced (${data.practiced_count})` },
          { key: "missing", label: `⚠️ Missing (${data.total_patterns - data.practiced_count})` },
        ].map((tab) => (
          <button key={tab.key} id={`coverage-tab-${tab.key}`}
            onClick={() => setShowOnly(tab.key as any)}
            className="btn-ghost"
            style={{
              fontSize: 13,
              background: showOnly === tab.key ? "rgba(97,114,243,0.2)" : undefined,
              borderColor: showOnly === tab.key ? "rgba(97,114,243,0.4)" : undefined,
              color: showOnly === tab.key ? "var(--brand-400)" : undefined,
            }}>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Coverage grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 10 }}>
        {filtered.map((item) => (
          <div
            key={item.pattern_slug}
            className="glass-card"
            style={{
              padding: "14px 16px",
              borderColor: item.practiced ? "rgba(34,197,94,0.2)" : "rgba(239,68,68,0.12)",
              background: item.practiced ? "rgba(34,197,94,0.04)" : "rgba(239,68,68,0.03)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: item.practiced ? "var(--gray-100)" : "var(--gray-500)" }}>
                {item.pattern}
              </span>
              {item.practiced ? (
                <span style={{ fontSize: 13, color: "#22c55e", fontWeight: 700, flexShrink: 0 }}>{item.solved_count}</span>
              ) : (
                <span style={{ fontSize: 18 }}>😴</span>
              )}
            </div>
            {item.practiced && (
              <div className="progress-bar" style={{ marginTop: 8, height: 4 }}>
                <div className="progress-bar-fill" style={{
                  width: `${Math.min((item.solved_count / 10) * 100, 100)}%`,
                  background: "#22c55e",
                }} />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
