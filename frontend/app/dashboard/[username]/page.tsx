"use client";

import { use, useEffect, useState } from "react";
import { api, Overview, PatternsResponse, TopicsResponse } from "@/lib/api";
import { fmt, CHART_COLORS } from "@/lib/utils";
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
} from "recharts";

interface Props { params: Promise<{ username: string }> }

export default function OverviewPage({ params }: Props) {
  const { username } = use(params);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [patterns, setPatterns] = useState<PatternsResponse | null>(null);
  const [topics, setTopics] = useState<TopicsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.getOverview(username),
      api.getPatterns(username),
      api.getTopics(username),
    ])
      .then(([ov, pat, top]) => {
        setOverview(ov);
        setPatterns(pat);
        setTopics(top);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [username]);

  if (loading) return <OverviewSkeleton />;
  if (error || !overview) return (
    <div style={{ padding: 40, textAlign: "center", color: "var(--gray-400)" }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>😕</div>
      <p style={{ fontSize: 16 }}>{error || "Failed to load overview"}</p>
    </div>
  );

  const diffData = [
    { name: "Easy", value: overview.easy, color: "#22c55e" },
    { name: "Medium", value: overview.medium, color: "#f59e0b" },
    { name: "Hard", value: overview.hard, color: "#ef4444" },
  ];

  const topPatterns = (patterns?.patterns || []).slice(0, 10);
  const topTopics = (topics?.topics || []).slice(0, 8).map((t) => ({
    name: t.topic,
    solved: t.solved_count,
  }));

  return (
    <div className="animate-fade-in-up stagger">
      {/* Page header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 12, flexWrap: "wrap" }}>
          {overview.avatar_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={overview.avatar_url}
              alt={username}
              style={{
                width: 64,
                height: 64,
                borderRadius: "50%",
                border: "2px solid rgba(99, 102, 241, 0.4)",
                boxShadow: "0 0 20px rgba(99, 102, 241, 0.2)",
              }}
            />
          )}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <h1 style={{ fontSize: 28, fontWeight: 800, color: "var(--gray-100)", margin: 0 }}>
                {overview.real_name || `@${username}`}
              </h1>
              <span style={{ fontSize: 13, color: "var(--gray-400)", fontFamily: "monospace" }}>
                @{overview.username}
              </span>
            </div>
            <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap", alignItems: "center" }}>
              {overview.ranking && (
                <span style={{ fontSize: 12, background: "rgba(255, 255, 255, 0.06)", color: "var(--gray-300)", padding: "4px 12px", borderRadius: 20, border: "1px solid var(--glass-border)" }}>
                  🏆 Rank #{fmt(overview.ranking)}
                </span>
              )}
              {overview.streak ? (
                <span style={{ fontSize: 12, background: "rgba(245, 158, 11, 0.15)", color: "#f59e0b", padding: "4px 12px", borderRadius: 20, border: "1px solid rgba(245, 158, 11, 0.3)" }}>
                  🔥 <strong>{overview.streak} Day Streak</strong>
                </span>
              ) : null}
              {overview.total_active_days ? (
                <span style={{ fontSize: 12, background: "rgba(99, 102, 241, 0.15)", color: "var(--brand-300)", padding: "4px 12px", borderRadius: 20, border: "1px solid rgba(99, 102, 241, 0.3)" }}>
                  📅 <strong>{overview.total_active_days} Active Days</strong>
                </span>
              ) : null}
              {overview.acceptance_rate ? (
                <span style={{ fontSize: 12, background: "rgba(34, 197, 94, 0.15)", color: "#22c55e", padding: "4px 12px", borderRadius: 20, border: "1px solid rgba(34, 197, 94, 0.3)" }}>
                  ⚡ <strong>{overview.acceptance_rate}% Acceptance</strong> ({overview.total_submissions} submissions)
                </span>
              ) : null}
            </div>
          </div>
        </div>
      </div>

      {/* Stat cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
        <StatCard label="Total Solved" value={overview.total_solved} color="var(--brand-400)" subtext={`All ${overview.total_solved} Verified`} />
        <StatCard label="Easy" value={overview.easy} color="#22c55e" subtext={overview.beats_easy ? `Beats ${overview.beats_easy}%` : undefined} />
        <StatCard label="Medium" value={overview.medium} color="#f59e0b" subtext={overview.beats_medium ? `Beats ${overview.beats_medium}%` : undefined} />
        <StatCard label="Hard" value={overview.hard} color="#ef4444" subtext={overview.beats_hard ? `Beats ${overview.beats_hard}%` : undefined} />
      </div>

      {/* Badges & Languages Row */}
      {((overview.badges && overview.badges.length > 0) || (overview.languages && overview.languages.length > 0)) && (
        <div style={{ display: "grid", gridTemplateColumns: overview.badges && overview.badges.length > 0 ? "1.4fr 1fr" : "1fr", gap: 20, marginBottom: 24 }}>
          {/* Badges */}
          {overview.badges && overview.badges.length > 0 && (
            <div className="glass-card" style={{ padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                <div className="section-title" style={{ fontSize: 15, margin: 0 }}>
                  🏅 LeetCode Badges ({overview.badges.length})
                </div>
                {overview.upcoming_badges && overview.upcoming_badges.length > 0 && (
                  <span style={{ fontSize: 11, color: "var(--gray-400)" }}>
                    In Progress: {overview.upcoming_badges[0].name} ({overview.upcoming_badges[0].progress}%)
                  </span>
                )}
              </div>
              <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
                {overview.badges.map((b) => (
                  <div
                    key={b.id || b.displayName}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid var(--glass-border)",
                      borderRadius: 12,
                      padding: "8px 14px",
                    }}
                  >
                    {b.icon ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={b.icon.startsWith("http") ? b.icon : `https://leetcode.com${b.icon}`} alt={b.displayName} style={{ width: 40, height: 40, objectFit: "contain" }} />
                    ) : (
                      <div style={{ fontSize: 28 }}>🏅</div>
                    )}
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 700, color: "var(--gray-100)" }}>{b.displayName}</div>
                      {b.creationDate && (
                        <div style={{ fontSize: 11, color: "var(--gray-500)" }}>Earned: {b.creationDate}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Languages */}
          {overview.languages && overview.languages.length > 0 && (
            <div className="glass-card" style={{ padding: 20 }}>
              <div className="section-title" style={{ fontSize: 15, marginBottom: 14 }}>
                💻 Language Mastery
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {overview.languages.map((lang) => {
                  const pct = Math.round((lang.problemsSolved / overview.total_solved) * 100);
                  return (
                    <div key={lang.languageName}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
                        <span style={{ fontWeight: 600, color: "var(--gray-200)" }}>{lang.languageName}</span>
                        <span style={{ color: "var(--brand-300)" }}>{lang.problemsSolved} solved ({pct}%)</span>
                      </div>
                      <div className="progress-bar" style={{ height: 6 }}>
                        <div className="progress-bar-fill" style={{ width: `${pct}%`, background: "linear-gradient(90deg, #6172f3, #a855f7)" }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Charts row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.6fr", gap: 20, marginBottom: 24 }}>
        {/* Difficulty Pie */}
        <div className="glass-card" style={{ padding: 24 }}>
          <div className="section-title" style={{ fontSize: 16, marginBottom: 20 }}>Difficulty Split</div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={diffData} cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                paddingAngle={4} dataKey="value">
                {diffData.map((d) => <Cell key={d.name} fill={d.color} />)}
              </Pie>
              <Tooltip
                contentStyle={{ background: "var(--gray-850)", border: "1px solid var(--glass-border)", borderRadius: 10 }}
                labelStyle={{ color: "var(--gray-300)" }} itemStyle={{ color: "var(--gray-200)" }}
              />
              <Legend iconType="circle" iconSize={8}
                formatter={(v) => <span style={{ color: "var(--gray-300)", fontSize: 13 }}>{v}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Topics Bar */}
        <div className="glass-card" style={{ padding: 24 }}>
          <div className="section-title" style={{ fontSize: 16, marginBottom: 20 }}>Top Topics Solved</div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={topTopics} layout="vertical" margin={{ left: 10, right: 24, top: 4, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fill: "#cbd5e1", fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} width={135} />
              <Tooltip
                contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border-subtle)", borderRadius: 10, color: "var(--text-primary)" }}
                itemStyle={{ color: "var(--text-primary)" }} cursor={{ fill: "rgba(99,102,241,0.06)" }}
              />
              <Bar dataKey="solved" radius={[0, 6, 6, 0]} fill="#6366f1" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top patterns */}
      {topPatterns.length > 0 && (
        <div className="glass-card" style={{ padding: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div className="section-title" style={{ fontSize: 16, margin: 0 }}>Top DSA Patterns Practiced</div>
            <a href={`/dashboard/${username}/patterns`} style={{ fontSize: 13, color: "var(--brand-400)", textDecoration: "none" }}>
              View all patterns →
            </a>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {topPatterns.map((p, i) => {
              const maxC = topPatterns[0]?.solved_count || 1;
              const pct = Math.round((p.solved_count / maxC) * 100);
              return (
                <div key={p.pattern_slug} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ width: 24, fontSize: 11, color: "var(--gray-500)", fontWeight: 600, flexShrink: 0, textAlign: "right" }}>
                    #{i + 1}
                  </span>
                  <span style={{ width: 160, fontSize: 13, color: "var(--gray-200)", flexShrink: 0 }}>{p.pattern}</span>
                  <div style={{ flex: 1 }}>
                    <div className="progress-bar">
                      <div className="progress-bar-fill" style={{ width: `${pct}%`, background: CHART_COLORS[i % CHART_COLORS.length] }} />
                    </div>
                  </div>
                  <span style={{ width: 44, fontSize: 13, color: "var(--gray-300)", fontWeight: 600, textAlign: "right", flexShrink: 0 }}>
                    {p.solved_count}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color, subtext }: { label: string; value: number; color: string; subtext?: string }) {
  return (
    <div className="glass-card" style={{ padding: "20px 24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <div className="stat-number" style={{ color }}>{fmt(value)}</div>
        {subtext && (
          <span style={{ fontSize: 11, fontWeight: 600, color: "var(--gray-400)", background: "rgba(255,255,255,0.06)", padding: "2px 8px", borderRadius: 12 }}>
            {subtext}
          </span>
        )}
      </div>
      <div className="stat-label" style={{ marginTop: 6 }}>{label}</div>
    </div>
  );
}

function OverviewSkeleton() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div className="skeleton" style={{ height: 60, width: 300 }} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16 }}>
        {[...Array(4)].map((_, i) => <div key={i} className="skeleton" style={{ height: 90 }} />)}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.6fr", gap: 20 }}>
        <div className="skeleton" style={{ height: 260 }} />
        <div className="skeleton" style={{ height: 260 }} />
      </div>
      <div className="skeleton" style={{ height: 300 }} />
    </div>
  );
}
