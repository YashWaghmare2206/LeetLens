/**
 * Utility helpers for formatting and styling.
 */

/** Clamp a number between min and max */
export const clamp = (n: number, min: number, max: number) =>
  Math.max(min, Math.min(max, n));

/** Format a number with locale separators */
export const fmt = (n: number) => n.toLocaleString("en-IN");

/** Get CSS badge class from difficulty string */
export const difficultyClass = (d: string): string => {
  switch (d?.toLowerCase()) {
    case "easy":   return "badge badge-easy";
    case "medium": return "badge badge-medium";
    case "hard":   return "badge badge-hard";
    default:       return "badge";
  }
};

/** Get difficulty color hex */
export const difficultyColor = (d: string): string => {
  switch (d?.toLowerCase()) {
    case "easy":   return "#22c55e";
    case "medium": return "#f59e0b";
    case "hard":   return "#ef4444";
    default:       return "#8080a8";
  }
};

/** Recharts color palette for charts */
export const CHART_COLORS = [
  "#6172f3", "#a855f7", "#06b6d4", "#10b981", "#f59e0b",
  "#ef4444", "#8b5cf6", "#14b8a6", "#f97316", "#84cc16",
];

/** Generate a deterministic color from a string */
export const colorFromString = (str: string): string => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return CHART_COLORS[Math.abs(hash) % CHART_COLORS.length];
};

/** Format percentage */
export const pct = (n: number, total: number): string =>
  total === 0 ? "0%" : `${Math.round((n / total) * 100)}%`;
