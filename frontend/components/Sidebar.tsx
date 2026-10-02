/**
 * Sidebar navigation — Professional, clutter-free developer navigation.
 * 5 core destinations with clean SVG vector iconography.
 */
"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import ThemeToggle from "./ThemeToggle";
import { api } from "@/lib/api";

interface SidebarProps {
  username: string;
}

const navItems = [
  {
    label: "Overview",
    segment: "",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect width="7" height="9" x="3" y="3" rx="1" />
        <rect width="7" height="5" x="14" y="3" rx="1" />
        <rect width="7" height="9" x="14" y="12" rx="1" />
        <rect width="7" height="5" x="3" y="16" rx="1" />
      </svg>
    ),
  },
  {
    label: "Topic & Patterns",
    segment: "taxonomy",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="12 2 2 7 12 12 22 7 12 2" />
        <polyline points="2 17 12 22 22 17" />
        <polyline points="2 12 12 17 22 12" />
      </svg>
    ),
  },
  {
    label: "Pattern Practice",
    segment: "practice",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="m9 12 2 2 4-4" />
      </svg>
    ),
  },
  {
    label: "Spaced Revisit",
    segment: "revisit",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
        <path d="M3 3v5h5" />
        <path d="M12 7v5l4 2" />
      </svg>
    ),
  },
  {
    label: "Activity Timeline",
    segment: "timeline",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect width="18" height="18" x="3" y="4" rx="2" />
        <path d="M16 2v4" />
        <path d="M8 2v4" />
        <path d="M3 10h18" />
      </svg>
    ),
  },
  {
    label: "Interview Readiness",
    segment: "analysis",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />
      </svg>
    ),
  },
];

export default function Sidebar({ username }: SidebarProps) {
  const pathname = usePathname();
  const base = `/dashboard/${username}`;

  return (
    <aside
      style={{
        width: 230,
        flexShrink: 0,
        background: "var(--bg-surface)",
        borderRight: "1px solid var(--border-subtle)",
        display: "flex",
        flexDirection: "column",
        padding: "20px 14px",
        gap: 4,
        position: "sticky",
        top: 0,
        height: "100vh",
        overflowY: "auto",
        zIndex: 40,
      }}
    >
      {/* Brand Header */}
      <Link
        href="/"
        style={{
          textDecoration: "none",
          marginBottom: 20,
          padding: "4px 8px",
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        <span
          style={{
            width: 30,
            height: 30,
            borderRadius: 7,
            background: "#4f46e5",
            color: "#ffffff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 800,
            fontSize: 14,
            boxShadow: "0 2px 8px rgba(79, 70, 229, 0.4)",
          }}
        >
          L
        </span>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span style={{ fontWeight: 700, fontSize: 15, color: "var(--text-primary)", letterSpacing: "-0.01em" }}>
            LeetLens
          </span>
          <span style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 500 }}>
            DSA Pattern Intelligence
          </span>
        </div>
      </Link>

      {/* Target User Badge */}
      <div
        style={{
          padding: "10px 12px",
          background: "var(--bg-surface-elevated)",
          border: "1px solid var(--border-subtle)",
          borderRadius: 8,
          marginBottom: 16,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ minWidth: 0, overflow: "hidden" }}>
          <div style={{ fontSize: 10, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-muted)", fontWeight: 600 }}>
            Analyzing
          </div>
          <div
            style={{
              fontSize: 13,
              fontWeight: 600,
              color: "var(--text-primary)",
              fontFamily: "'JetBrains Mono', monospace",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            @{username}
          </div>
        </div>
        <span
          style={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            background: "#10b981",
            boxShadow: "0 0 6px #10b981",
          }}
        />
      </div>

      {/* Navigation Section */}
      <div style={{ fontSize: 11, fontWeight: 600, color: "#475569", textTransform: "uppercase", letterSpacing: "0.06em", padding: "0 8px 6px" }}>
        Navigation
      </div>
      <nav style={{ display: "flex", flexDirection: "column", gap: 3 }}>
        {navItems.map((item) => {
          const href = item.segment ? `${base}/${item.segment}` : base;
          const isActive = item.segment === ""
            ? pathname === base
            : pathname.startsWith(`${base}/${item.segment}`);
          return (
            <Link
              key={item.label}
              href={href}
              id={`nav-${item.segment || "overview"}`}
              className={`nav-link ${isActive ? "active" : ""}`}
            >
              <span style={{ opacity: isActive ? 1 : 0.75 }}>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Utilities / Bottom Section */}
      <div style={{ marginTop: "auto", paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.07)" }}>
        <Link
          href={`${base}/problems`}
          className={`nav-link ${pathname === `${base}/problems` ? "active" : ""}`}
          style={{ marginBottom: 6, fontSize: 12 }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
          </svg>
          <span>All Solved Problems</span>
        </Link>

        <div style={{ marginBottom: 10, display: "flex", justifyContent: "center" }}>
          <ThemeToggle />
        </div>

        <Link href="/" style={{ textDecoration: "none" }}>
          <div
            className="btn-ghost"
            style={{
              width: "100%",
              justifyContent: "center",
              fontSize: 12,
              padding: "7px 12px",
              color: "#94a3b8",
            }}
          >
            ← Switch Profile
          </div>
        </Link>

        <div style={{ marginTop: 12, padding: "0 4px", fontSize: 10, color: "#475569", lineHeight: 1.4, textAlign: "center" }}>
          Independent open-source tool. Not affiliated with LeetCode LLC.
        </div>
      </div>
    </aside>
  );
}
