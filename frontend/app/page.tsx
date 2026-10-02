"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";
import { api, ApiError } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [stageText, setStageText] = useState("");
  const progressTimersRef = useRef<NodeJS.Timeout[]>([]);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      progressTimersRef.current.forEach((t) => clearTimeout(t));
      progressTimersRef.current = [];
    };
  }, []);

  const clearTimers = () => {
    progressTimersRef.current.forEach((t) => clearTimeout(t));
    progressTimersRef.current = [];
  };

  const handleAnalyze = async (e: React.FormEvent, customUsername?: string) => {
    if (e) e.preventDefault();
    const raw = (customUsername || input).trim();
    if (!raw) return;

    setError(null);
    setLoading(true);
    setProgress(15);
    setStageText("Connecting to LeetCode API...");
    clearTimers();

    // Schedule progressive stage updates: 30%, 45%, 68%, 88%
    const t1 = setTimeout(() => {
      setProgress(30);
      setStageText("Fetching problem solved stats & submission history...");
    }, 400);

    const t2 = setTimeout(() => {
      setProgress(45);
      setStageText("Classifying DSA taxonomy & 71+ algorithmic patterns...");
    }, 1000);

    const t3 = setTimeout(() => {
      setProgress(68);
      setStageText("Calculating blindspot radar & topic mastery...");
    }, 1800);

    const t4 = setTimeout(() => {
      setProgress(88);
      setStageText("Computing Technical Interview Readiness Index...");
    }, 2700);

    progressTimersRef.current = [t1, t2, t3, t4];

    try {
      await api.triggerSync(raw);
      clearTimers();

      const usernameMatch = raw.match(/leetcode\.com\/(?:u\/)?([^/?#]+)/);
      const username = usernameMatch ? usernameMatch[1] : raw;

      // Completion stage: 100%
      setProgress(100);
      setStageText("Done! Loading dashboard...");

      // Smooth brief pause so the user sees 100% completion before navigating
      setTimeout(() => {
        router.push(`/dashboard/${username}`);
      }, 450);
    } catch (err) {
      clearTimers();
      setLoading(false);
      setProgress(0);
      setStageText("");
      if (err instanceof ApiError) {
        setError(err.status === 400 ? "Invalid username. Please check and try again." : err.message);
      } else {
        setError("Could not connect to backend. Make sure the server is running.");
      }
    }
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "48px 24px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Top right controls */}
      <div style={{ position: "absolute", top: 24, right: 24, zIndex: 10 }}>
        <ThemeToggle />
      </div>

      {/* Decorative ambient blobs */}
      <div style={{
        position: "absolute", top: "-10%", left: "-5%",
        width: 550, height: 550,
        background: "radial-gradient(circle, rgba(97,114,243,0.15) 0%, transparent 70%)",
        borderRadius: "50%", pointerEvents: "none",
      }} />
      <div style={{
        position: "absolute", bottom: "-10%", right: "-5%",
        width: 650, height: 650,
        background: "radial-gradient(circle, rgba(168,85,247,0.1) 0%, transparent 70%)",
        borderRadius: "50%", pointerEvents: "none",
      }} />

      {/* Hero Container */}
      <div style={{ maxWidth: 840, width: "100%", textAlign: "center", position: "relative", zIndex: 1 }}>
        {/* Logo mark */}
        <div
          className="animate-float"
          style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: 76, height: 76,
            background: "linear-gradient(135deg, #6172f3 0%, #a855f7 100%)",
            borderRadius: 22, marginBottom: 24,
            boxShadow: "0 16px 48px rgba(97,114,243,0.35)",
            fontSize: 34,
          }}
        >
          🔬
        </div>

        <h1
          style={{ fontSize: "clamp(42px, 6vw, 68px)", fontWeight: 900, lineHeight: 1.08, marginBottom: 16, letterSpacing: "-0.03em" }}
          className="animate-fade-in-up"
        >
          <span className="gradient-text">LeetLens</span>
        </h1>

        <p
          style={{ fontSize: "clamp(18px, 2.5vw, 22px)", color: "var(--gray-200)", marginBottom: 10, lineHeight: 1.5 }}
          className="animate-fade-in-up"
        >
          Deep DSA Pattern Analyzer & Technical Interview Readiness
        </p>
        <p
          style={{ fontSize: 15, color: "var(--gray-400)", marginBottom: 36, maxWidth: 620, margin: "0 auto 36px" }}
          className="animate-fade-in-up"
        >
          Move beyond raw solved counts. Segregate your practice by <strong>Topics → Patterns</strong>, detect interview blindspots, and measure your exact readiness for top-tier tech screens.
        </p>

        {/* Global Taxonomy Stats Bar */}
        <div
          className="glass-card"
          style={{
            padding: "14px 20px",
            marginBottom: 32,
            display: "flex",
            justifyContent: "space-around",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 16,
            background: "rgba(255, 255, 255, 0.02)",
            border: "1px solid var(--glass-border)",
          }}
        >
          <div>
            <div style={{ fontSize: 20, fontWeight: 800, color: "var(--brand-400)" }}>15</div>
            <div style={{ fontSize: 11, color: "var(--gray-400)", textTransform: "uppercase" }}>Core Topics</div>
          </div>
          <div style={{ width: 1, height: 24, background: "var(--glass-border)" }} />
          <div>
            <div style={{ fontSize: 20, fontWeight: 800, color: "#a855f7" }}>71+</div>
            <div style={{ fontSize: 11, color: "var(--gray-400)", textTransform: "uppercase" }}>Interview Patterns</div>
          </div>
          <div style={{ width: 1, height: 24, background: "var(--glass-border)" }} />
          <div>
            <div style={{ fontSize: 20, fontWeight: 800, color: "#22c55e" }}>0 - 100</div>
            <div style={{ fontSize: 11, color: "var(--gray-400)", textTransform: "uppercase" }}>Readiness Score</div>
          </div>
          <div style={{ width: 1, height: 24, background: "var(--glass-border)" }} />
          <div>
            <div style={{ fontSize: 20, fontWeight: 800, color: "#f59e0b" }}>Top 75+</div>
            <div style={{ fontSize: 11, color: "var(--gray-400)", textTransform: "uppercase" }}>Curated Problems</div>
          </div>
        </div>

        {/* Search form */}
        <form onSubmit={handleAnalyze} style={{ position: "relative", marginBottom: 32 }} className="animate-fade-in-up">
          <div style={{ display: "flex", gap: 12, alignItems: "stretch" }}>
            <input
              id="username-input"
              type="text"
              className="input-field"
              placeholder="Enter LeetCode username or profile URL..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              autoFocus
              style={{ flex: 1, fontSize: 15, padding: "14px 20px" }}
            />
            <button
              id="analyze-btn"
              type="submit"
              className="btn-primary"
              disabled={loading || !input.trim()}
              style={{ whiteSpace: "nowrap", minWidth: 160, fontSize: 15 }}
            >
              {loading ? (
                <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                  <span
                    className="animate-spin-slow"
                    style={{
                      width: 16,
                      height: 16,
                      border: "2px solid rgba(255,255,255,0.3)",
                      borderTopColor: "#ffffff",
                      borderRadius: "50%",
                      display: "inline-block",
                    }}
                  />
                  <span>Analyzing...</span>
                </span>
              ) : (
                <>⚡ Analyze Profile</>
              )}
            </button>
          </div>

          {/* Dynamic Sync Progress Bar */}
          {loading && (
            <div style={{ marginTop: 20, textAlign: "left" }} className="animate-fade-in">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span
                    className="animate-spin-slow"
                    style={{
                      width: 14,
                      height: 14,
                      border: "2px solid rgba(99, 102, 241, 0.25)",
                      borderTopColor: "var(--brand-400)",
                      borderRadius: "50%",
                      display: "inline-block",
                    }}
                  />
                  <span style={{ fontSize: 13, color: "var(--text-secondary)", fontWeight: 500 }}>
                    {stageText || "Analyzing profile..."}
                  </span>
                </div>
                <span
                  style={{
                    fontSize: 14,
                    color: "var(--brand-400)",
                    fontWeight: 700,
                    fontFamily: "var(--font-mono, monospace)",
                  }}
                >
                  {progress}%
                </span>
              </div>
              <div className="progress-bar" style={{ height: 10 }}>
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${progress}%`,
                    background: "linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)",
                  }}
                />
              </div>

              {/* Stage indicator milestones */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginTop: 8,
                  fontSize: 11,
                  color: "var(--text-muted)",
                  flexWrap: "wrap",
                  gap: 4,
                }}
              >
                <span style={{ color: progress >= 30 ? "var(--brand-400)" : "inherit", fontWeight: progress >= 30 ? 600 : 400 }}>
                  {progress >= 30 ? "✓" : "○"} Profile Stats (30%)
                </span>
                <span style={{ color: progress >= 45 ? "var(--brand-400)" : "inherit", fontWeight: progress >= 45 ? 600 : 400 }}>
                  {progress >= 45 ? "✓" : "○"} Topics (45%)
                </span>
                <span style={{ color: progress >= 68 ? "var(--brand-400)" : "inherit", fontWeight: progress >= 68 ? 600 : 400 }}>
                  {progress >= 68 ? "✓" : "○"} DSA Patterns (68%)
                </span>
                <span style={{ color: progress >= 100 ? "#22c55e" : "inherit", fontWeight: progress >= 100 ? 600 : 400 }}>
                  {progress >= 100 ? "✓ Ready (100%)" : "○ Readiness (100%)"}
                </span>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div style={{
              marginTop: 14, padding: "12px 16px",
              background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)",
              borderRadius: 10, color: "#fca5a5", fontSize: 14, textAlign: "left",
            }} className="animate-fade-in">
              ⚠️ {error}
            </div>
          )}
        </form>

        {/* Feature pillars */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }} className="animate-fade-in-up">
          <div className="glass-card" style={{ padding: "18px 20px", textAlign: "left" }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>🗂️</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: "var(--gray-200)", marginBottom: 4 }}>
              Hierarchical Topic Explorer
            </div>
            <div style={{ fontSize: 12, color: "var(--gray-400)", lineHeight: 1.4 }}>
              Drill down from Array into Two Pointers & Sliding Window, or Tree into DFS/BFS.
            </div>
          </div>

          <div className="glass-card" style={{ padding: "18px 20px", textAlign: "left" }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>🎯</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: "var(--gray-200)", marginBottom: 4 }}>
              Readiness Index (0-100)
            </div>
            <div style={{ fontSize: 12, color: "var(--gray-400)", lineHeight: 1.4 }}>
              Objectively measures Topic Breadth, Medium/Hard Depth, and Practice Consistency.
            </div>
          </div>

          <div className="glass-card" style={{ padding: "18px 20px", textAlign: "left" }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>⚠️</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: "var(--gray-200)", marginBottom: 4 }}>
              Interview Blindspot Radar
            </div>
            <div style={{ fontSize: 12, color: "var(--gray-400)", lineHeight: 1.4 }}>
              Pinpoints high-frequency interview patterns you haven&apos;t solved enough of.
            </div>
          </div>
        </div>

        {/* Footer with Legal Disclaimer */}
        <footer
          style={{
            marginTop: 64,
            paddingTop: 28,
            paddingBottom: 20,
            borderTop: "1px solid rgba(255, 255, 255, 0.08)",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--gray-300)", marginBottom: 6 }}>
            LeetLens — Open-Source DSA Pattern & Spaced Review Analytics
          </div>
          <p
            style={{
              fontSize: 11,
              color: "#64748b",
              lineHeight: 1.6,
              maxWidth: 720,
              margin: "0 auto",
            }}
          >
            <strong>Disclaimer:</strong> LeetLens is an independent open-source project and is not affiliated with, endorsed by, or sponsored by LeetCode LLC. All problem names, trademarks, and logos belong to LeetCode LLC and their respective owners.
          </p>
        </footer>
      </div>
    </main>
  );
}
