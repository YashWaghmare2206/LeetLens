"use client";

import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem("leetlens_theme") as "dark" | "light" | null;
    const initial = saved || "dark";
    setTheme(initial);
    document.documentElement.setAttribute("data-theme", initial);
    document.documentElement.style.colorScheme = initial;
  }, []);

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    localStorage.setItem("leetlens_theme", next);
    document.documentElement.setAttribute("data-theme", next);
    document.documentElement.style.colorScheme = next;
  };

  if (!mounted) {
    return (
      <div
        style={{
          width: 84,
          height: 32,
          borderRadius: 8,
          background: "rgba(255, 255, 255, 0.05)",
        }}
      />
    );
  }

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle Theme"
      title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "6px 12px",
        borderRadius: 8,
        fontSize: 12,
        fontWeight: 600,
        cursor: "pointer",
        border: theme === "dark" ? "1px solid rgba(255, 255, 255, 0.12)" : "1px solid #cbd5e1",
        background: theme === "dark" ? "#161c2d" : "#ffffff",
        color: theme === "dark" ? "#f1f5f9" : "#0f172a",
        boxShadow: theme === "dark" ? "none" : "0 1px 2px rgba(0, 0, 0, 0.05)",
        transition: "all 0.2s ease",
      }}
    >
      <span>{theme === "dark" ? "☀️" : "🌙"}</span>
      <span>{theme === "dark" ? "Light" : "Dark"}</span>
    </button>
  );
}
