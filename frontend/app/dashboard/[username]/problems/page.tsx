"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { api, ProblemsResponse } from "@/lib/api";
import { difficultyClass, fmt } from "@/lib/utils";

interface Props { params: Promise<{ username: string }> }

const REVISION_PRESETS = [7, 14, 21, 30];

export default function ProblemsPage({ params }: Props) {
  const { username } = use(params);
  const [data, setData] = useState<ProblemsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [dateSearch, setDateSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Spaced Repetition Revisit State
  const [onlyRevisit, setOnlyRevisit] = useState(false);
  const [revisionDays, setRevisionDays] = useState(14);

  // Import modal state
  const [showImport, setShowImport] = useState(false);
  const [importInput, setImportInput] = useState("");
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<string | null>(null);

  const fetchProblems = () => {
    const diff = filter !== "All" ? filter : undefined;
    api.getProblems(username, diff)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProblems();
  }, [username, filter]);

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    const items = importInput
      .split(/[\n,]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    if (items.length === 0) return;

    setImporting(true);
    setImportResult(null);
    try {
      const res = await api.importProblems(username, items);
      setImportResult(`Successfully imported ${res.added} problem(s)!`);
      setImportInput("");
      fetchProblems();
    } catch (err: any) {
      setImportResult(`Import failed: ${err.message || "Unknown error"}`);
    } finally {
      setImporting(false);
    }
  };

  const getDaysAgo = (solvedAt?: string | null) => {
    if (!solvedAt) return null;
    const t = new Date(solvedAt).getTime();
    if (isNaN(t)) return null;
    return Math.max(0, Math.floor((Date.now() - t) / (1000 * 60 * 60 * 24)));
  };

  const filtered = (data?.problems || []).filter((p) => {
    const q = search.toLowerCase().trim();
    const matchSearch =
      !q ||
      p.title.toLowerCase().includes(q) ||
      String(p.leetcode_id).includes(q) ||
      p.slug.toLowerCase().includes(q);

    const matchDate = !dateSearch || (p.solved_at && p.solved_at.includes(dateSearch));

    const daysAgo = getDaysAgo(p.solved_at);
    const matchRevisit = !onlyRevisit || (daysAgo != null && daysAgo >= revisionDays);

    return matchSearch && matchDate && matchRevisit;
  });

  const totalDueForRevisit = (data?.problems || []).filter((p) => {
    const d = getDaysAgo(p.solved_at);
    return d != null && d >= revisionDays;
  }).length;

  return (
    <div className="animate-fade-in-up stagger">
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 16, marginBottom: 20 }}>
        <div>
          <h1 className="section-title">Solved Problems</h1>
          <p className="section-subtitle">
            Showing <strong style={{ color: "#ffffff" }}>{filtered.length}</strong> verified problem records {data?.total ? `· ${fmt(data.total)} total solved on LeetCode` : ""}
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          {/* Text Search */}
          <input
            id="problem-search"
            type="text"
            className="input-field"
            placeholder="Search by title, #, or slug..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 230, padding: "9px 14px", fontSize: 13 }}
          />

          {/* Date Search */}
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: "var(--gray-300)" }}>📅 Date:</span>
            <input
              type="date"
              className="date-picker-input"
              value={dateSearch}
              onChange={(e) => setDateSearch(e.target.value)}
              style={{ padding: "7px 10px", fontSize: 12 }}
            />
            {dateSearch && (
              <button
                onClick={() => setDateSearch("")}
                className="btn-ghost"
                style={{ fontSize: 11, padding: "5px 8px", color: "#f87171" }}
                title="Clear date"
              >
                ✕
              </button>
            )}
          </div>

          <button
            onClick={() => setShowImport(true)}
            className="btn-primary"
            style={{ fontSize: 13, padding: "9px 18px", whiteSpace: "nowrap" }}
          >
            + Import Problems
          </button>
        </div>
      </div>

      {/* Spaced Repetition Revisit Controller Bar */}
      <div
        className="glass-card"
        style={{
          padding: "12px 18px",
          borderRadius: 12,
          marginBottom: 16,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-primary)" }}>
            ⏱️ Revisit Schedule:
          </span>

          <div style={{ display: "flex", gap: 4 }}>
            {REVISION_PRESETS.map((p) => {
              const isActive = revisionDays === p;
              return (
                <button
                  key={p}
                  onClick={() => setRevisionDays(p)}
                  style={{
                    fontSize: 11,
                    padding: "3px 9px",
                    borderRadius: 6,
                    cursor: "pointer",
                    border: isActive ? "1px solid var(--brand-500)" : "1px solid var(--border-subtle)",
                    background: isActive ? "var(--brand-500)" : "transparent",
                    color: isActive ? "#ffffff" : "var(--text-secondary)",
                    fontWeight: isActive ? 700 : 500,
                  }}
                >
                  {p}d
                </button>
              );
            })}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>or custom:</span>
            <input
              type="number"
              min="1"
              max="365"
              value={revisionDays}
              onChange={(e) => {
                const val = parseInt(e.target.value, 10);
                if (!isNaN(val) && val > 0) setRevisionDays(val);
              }}
              style={{
                width: 48,
                padding: "2px 6px",
                fontSize: 11,
                background: "var(--bg-surface)",
                border: "1px solid var(--border-subtle)",
                color: "var(--text-primary)",
                borderRadius: 4,
                textAlign: "center",
              }}
            />
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>days</span>
          </div>
        </div>

        <button
          onClick={() => setOnlyRevisit((prev) => !prev)}
          style={{
            fontSize: 12,
            padding: "5px 12px",
            borderRadius: 6,
            cursor: "pointer",
            transition: "all 0.15s ease",
            border: onlyRevisit ? "1px solid #f59e0b" : "1px solid rgba(245, 158, 11, 0.4)",
            background: onlyRevisit ? "#f59e0b" : "rgba(245, 158, 11, 0.1)",
            color: onlyRevisit ? "#000000" : "#fbbf24",
            fontWeight: 700,
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <span>{onlyRevisit ? "✓ Filter: Due to Revisit" : "Filter: Due to Revisit"}</span>
          <span
            style={{
              fontSize: 11,
              padding: "1px 6px",
              borderRadius: 10,
              background: onlyRevisit ? "rgba(0,0,0,0.2)" : "rgba(245, 158, 11, 0.2)",
              color: onlyRevisit ? "#000000" : "#fbbf24",
              fontWeight: 800,
            }}
          >
            {totalDueForRevisit}
          </span>
        </button>
      </div>

      {/* Difficulty Filter Tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {["All", "Easy", "Medium", "Hard"].map((d) => (
          <button
            key={d}
            onClick={() => setFilter(d)}
            className={`btn-ghost ${filter === d ? "pill-active" : ""}`}
            style={{ fontSize: 12, padding: "6px 14px" }}
          >
            {d}
          </button>
        ))}
      </div>

      {/* Import Modal */}
      {showImport && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.75)",
          display: "flex", alignItems: "center", justifyContent: "center",
          zIndex: 1000, padding: 20,
        }}>
          <div className="glass-card" style={{ maxWidth: 520, width: "100%", padding: 28 }}>
            <h2 style={{ fontSize: 18, fontWeight: 800, marginBottom: 8, color: "var(--text-primary)" }}>Import Solved Problems</h2>
            <p style={{ fontSize: 13, color: "var(--gray-400)", marginBottom: 16, lineHeight: 1.5 }}>
              Paste problem IDs or slugs (comma or newline separated).
            </p>
            <form onSubmit={handleImport}>
              <textarea
                rows={5}
                className="input-field"
                placeholder="1, 15, 206, two-sum, valid-anagram..."
                value={importInput}
                onChange={(e) => setImportInput(e.target.value)}
                style={{ width: "100%", padding: 12, fontSize: 13, fontFamily: "monospace", resize: "vertical", marginBottom: 14 }}
              />
              {importResult && (
                <div style={{ fontSize: 13, fontWeight: 700, color: importResult.includes("Success") ? "#4ade80" : "#f87171", marginBottom: 14 }}>
                  {importResult}
                </div>
              )}
              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                <button
                  type="button"
                  onClick={() => { setShowImport(false); setImportResult(null); }}
                  className="btn-ghost"
                  style={{ fontSize: 13, padding: "8px 18px" }}
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={importing || !importInput.trim()}
                  className="btn-primary"
                  style={{ fontSize: 13, padding: "8px 22px" }}
                >
                  {importing ? "Importing..." : "Add to Solved"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Table */}
      {loading ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {[...Array(8)].map((_, i) => <div key={i} className="skeleton" style={{ height: 48, borderRadius: 10 }} />)}
        </div>
      ) : error ? (
        <div style={{ color: "#f87171", padding: 40, textAlign: "center", fontWeight: 700 }}>{error}</div>
      ) : (
        <div className="glass-card" style={{ overflow: "hidden" }}>
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 80 }}>#</th>
                <th>Title</th>
                <th style={{ width: 130 }}>Difficulty</th>
                <th style={{ width: 220 }}>Solved Date & Revisit Status</th>
                <th style={{ width: 110 }}>Link</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p) => {
                const daysAgo = getDaysAgo(p.solved_at);
                const isDue = daysAgo != null && daysAgo >= revisionDays;

                return (
                  <tr key={p.slug} style={{ background: isDue && onlyRevisit ? "rgba(245, 158, 11, 0.04)" : undefined }}>
                    <td style={{ color: "#94a3b8", fontSize: 13, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>
                      #{p.leetcode_id || "—"}
                    </td>
                    <td style={{ fontWeight: 700, color: "#ffffff", fontSize: 14 }}>
                      {p.title}
                    </td>
                    <td>
                      <span className={difficultyClass(p.difficulty)} style={{ fontSize: 12 }}>
                        {p.difficulty}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                        <span style={{ color: "#cbd5e1", fontSize: 12, fontWeight: 500 }}>
                          {p.solved_at ? p.solved_at.split("T")[0] : "—"}
                        </span>
                        {daysAgo != null && (
                          <span
                            style={{
                              fontSize: 10,
                              fontWeight: 700,
                              color: isDue ? "#fbbf24" : "#4ade80",
                            }}
                          >
                            {isDue
                              ? `Due to revisit (${daysAgo}d ago · overdue by ${daysAgo - revisionDays}d)`
                              : `Fresh (${daysAgo}d ago)`}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      {p.url ? (
                        <a
                          href={p.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            color: isDue ? "#fbbf24" : "#818cf8",
                            fontWeight: 700,
                            fontSize: 13,
                            textDecoration: "none",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 4,
                          }}
                        >
                          {isDue ? "Review ↗" : "Solve ↗"}
                        </a>
                      ) : "—"}
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: "center", color: "var(--gray-400)", padding: 36 }}>
                    No problems matching your filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
