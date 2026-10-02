/**
 * Client-Side Problem History Manager
 * Accumulates confirmed solved problems in browser localStorage across visits and manual imports.
 * 100% private, client-owned, and zero-server storage.
 */

import { ProblemInPattern } from "./api";

const STORAGE_PREFIX = "leetlens_history_v1_";

function getStorageKey(username: string): string {
  return `${STORAGE_PREFIX}${username.trim().toLowerCase()}`;
}

export function getStoredProblems(username: string): ProblemInPattern[] {
  if (typeof window === "undefined" || !username) return [];
  try {
    const raw = localStorage.getItem(getStorageKey(username));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    console.warn("Failed to load stored problems from localStorage:", err);
    return [];
  }
}

export function saveStoredProblems(username: string, problems: ProblemInPattern[]): void {
  if (typeof window === "undefined" || !username) return;
  try {
    localStorage.setItem(getStorageKey(username), JSON.stringify(problems));
  } catch (err) {
    console.warn("Failed to save problems to localStorage:", err);
  }
}

/**
 * Merges incoming problems with existing localStorage problems.
 * Deduplicates by problem `slug` (or `leetcode_id` if slug is missing).
 * Keeps the most recent metadata if updated.
 */
export function mergeStoredProblems(
  username: string,
  incoming: ProblemInPattern[]
): { merged: ProblemInPattern[]; newlyAdded: number; totalStored: number } {
  if (typeof window === "undefined" || !username) {
    return { merged: incoming, newlyAdded: 0, totalStored: incoming.length };
  }

  const existing = getStoredProblems(username);
  const problemMap = new Map<string, ProblemInPattern>();

  // Load existing records into map
  for (const p of existing) {
    const key = p.slug ? p.slug.toLowerCase() : String(p.leetcode_id);
    problemMap.set(key, p);
  }

  const initialCount = problemMap.size;

  // Merge incoming records
  for (const p of incoming) {
    const key = p.slug ? p.slug.toLowerCase() : String(p.leetcode_id);
    const prev = problemMap.get(key);
    if (!prev) {
      problemMap.set(key, p);
    } else {
      // Update with fresher date or more complete metadata if available
      problemMap.set(key, {
        ...prev,
        ...p,
        difficulty: p.difficulty === "Unknown" ? prev.difficulty : p.difficulty,
        leetcode_id: p.leetcode_id || prev.leetcode_id,
        solved_at: p.solved_at || prev.solved_at,
        topics: p.topics && p.topics.length > 0 ? p.topics : prev.topics,
      });
    }
  }

  const merged = Array.from(problemMap.values()).sort((a, b) => {
    // Sort descending by date if available, then by leetcode_id
    if (a.solved_at && b.solved_at) {
      return new Date(b.solved_at).getTime() - new Date(a.solved_at).getTime();
    }
    return (b.leetcode_id || 0) - (a.leetcode_id || 0);
  });

  const newlyAdded = problemMap.size - initialCount;
  saveStoredProblems(username, merged);

  return {
    merged,
    newlyAdded,
    totalStored: merged.length,
  };
}

/**
 * Clears stored problems for a user.
 */
export function clearStoredProblems(username: string): void {
  if (typeof window === "undefined" || !username) return;
  try {
    localStorage.removeItem(getStorageKey(username));
  } catch (err) {
    console.warn("Failed to clear stored problems:", err);
  }
}
