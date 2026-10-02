"use client";

import { use, useEffect, useState, useMemo } from "react";
import { api, TopicsResponse } from "@/lib/api";
import { fmt } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

interface Props { params: Promise<{ username: string }> }

export default function TopicsPage({ params }: Props) {
  const { username } = use(params);
  const [data, setData] = useState<TopicsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartLimit, setChartLimit] = useState<number>(20);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.getTopics(username).then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [username]);

  const filteredTopics = useMemo(() => {
    if (!data) return [];
    if (!search) return data.topics;
    const q = search.toLowerCase();
    return data.topics.filter((t) => t.topic.toLowerCase().includes(q));
  }, [data, search]);

  if (loading) return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {[...Array(6)].map((_, i) => <div key={i} className="skeleton" style={{ height: 56, borderRadius: 8 }} />)}
    </div>
  );
  if (error || !data) return <ErrView msg={error} />;

  const chartData = data.topics.slice(0, chartLimit).map((t) => ({
    name: t.topic.length > 14 ? t.topic.slice(0, 14) + "…" : t.topic,
    fullName: t.topic,
    easy: t.easy,
    medium: t.medium,
    hard: t.hard,
  }));

  const totalPairs = data.topics.reduce((a, t) => a + t.solved_count, 0);

  return (
    <div className="animate-fade-in-up stagger">
      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "#818cf8" }}>
            Skill Distribution
          </span>
          <span style={{ fontSize: 11, color: "#64748b" }}>•</span>
          <span style={{ fontSize: 12, color: "#94a3b8" }}>
            {data.topics.length} DSA Topics Tracked
          </span>
        </div>
        <h1 className="section-title" style={{ fontSize: 24, fontWeight: 800, color: "#ffffff", letterSpacing: "-0.01em" }}>
          Topic Distribution & Breakdown
        </h1>
        <p className="section-subtitle" style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>
          {data.topics.length} topics practiced across {fmt(totalPairs)} topic-problem tags from LeetCode.
        </p>
      </div>

      {/* Stacked bar chart */}
      <div
        className="glass-card"
        style={{
          padding: 24,
          marginBottom: 20,
          borderRadius: 12,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, flexWrap: "wrap", gap: 10 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-primary)" }}>
            Solved Problems by Topic (Easy / Medium / Hard)
          </div>

          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <span style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>Show:</span>
            {[10, 20, 35].map((lim) => (
              <button
                key={lim}
                onClick={() => setChartLimit(lim)}
                className={`btn-ghost ${chartLimit === lim ? "pill-active" : ""}`}
                style={{ fontSize: 11, padding: "3px 10px" }}
              >
                Top {lim}
              </button>
            ))}
          </div>
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} margin={{ left: 0, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} angle={-35} textAnchor="end" interval={0} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border-subtle)", borderRadius: 8, fontSize: 12, color: "var(--text-primary)" }}
              itemStyle={{ color: "var(--text-primary)" }}
              cursor={{ fill: "var(--bg-surface-hover)" }}
            />
            <Bar dataKey="easy" stackId="a" fill="#22c55e" radius={[0, 0, 0, 0]} name="Easy" />
            <Bar dataKey="medium" stackId="a" fill="#f59e0b" name="Medium" />
            <Bar dataKey="hard" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} name="Hard" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Topics table search & count */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12, flexWrap: "wrap", gap: 10 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-primary)" }}>
          All {filteredTopics.length} Topics
        </div>
        <input
          type="text"
          className="input-field"
          placeholder="Filter topics..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 220, padding: "6px 12px", fontSize: 12 }}
        />
      </div>

      {/* Topics table */}
      <div
        className="glass-card"
        style={{
          borderRadius: 12,
          overflow: "hidden",
        }}
      >
        <table className="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Topic</th>
              <th>Solved</th>
              <th>Easy</th>
              <th>Medium</th>
              <th>Hard</th>
              <th style={{ minWidth: 160 }}>Distribution</th>
            </tr>
          </thead>
          <tbody>
            {filteredTopics.map((t, i) => {
              const total = t.easy + t.medium + t.hard || 1;
              return (
                <tr key={t.topic_slug}>
                  <td style={{ color: "#64748b", fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }}>{i + 1}</td>
                  <td style={{ fontWeight: 600, color: "#f1f5f9" }}>{t.topic}</td>
                  <td style={{ fontWeight: 700, color: "#ffffff", fontFamily: "'JetBrains Mono', monospace" }}>{t.solved_count}</td>
                  <td><span style={{ color: "#22c55e", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>{t.easy}</span></td>
                  <td><span style={{ color: "#f59e0b", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>{t.medium}</span></td>
                  <td><span style={{ color: "#ef4444", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>{t.hard}</span></td>
                  <td>
                    <div style={{ display: "flex", height: 6, borderRadius: 999, overflow: "hidden", background: "var(--border-subtle)" }}>
                      <div style={{ width: `${(t.easy / total) * 100}%`, background: "#22c55e" }} />
                      <div style={{ width: `${(t.medium / total) * 100}%`, background: "#f59e0b" }} />
                      <div style={{ width: `${(t.hard / total) * 100}%`, background: "#ef4444" }} />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ErrView({ msg }: { msg: string | null }) {
  return <div style={{ textAlign: "center", color: "#94a3b8", padding: 60 }}>{msg || "No data found"}</div>;
}
