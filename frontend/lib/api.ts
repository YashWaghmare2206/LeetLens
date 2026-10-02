/**
 * LeetLens API client — all backend calls isolated here.
 * Frontend never calls LeetCode directly (per architecture rules).
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, err.detail || "Unknown error");
  }
  return res.json();
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}


export interface UserProfile {
  id: number;
  username: string;
  leetcode_url: string | null;
  real_name: string | null;
  avatar_url: string | null;
  ranking: number | null;
  created_at: string;
  updated_at: string;
}

export interface LCBadge {
  id?: string;
  displayName: string;
  icon: string;
  creationDate?: string;
}

export interface UpcomingBadge {
  name: string;
  icon: string;
  progress: number;
}

export interface LanguageStat {
  languageName: string;
  problemsSolved: number;
}

export interface Overview {
  username: string;
  total_solved: number;
  easy: number;
  medium: number;
  hard: number;
  total_submissions?: number;
  acceptance_rate?: number | null;
  ranking: number | null;
  real_name: string | null;
  avatar_url: string | null;
  reputation?: number | null;
  streak?: number | null;
  total_active_days?: number | null;
  beats_easy?: number | null;
  beats_medium?: number | null;
  beats_hard?: number | null;
  recent_solved_count?: number;
  badges?: LCBadge[];
  upcoming_badges?: UpcomingBadge[];
  languages?: LanguageStat[];
  submission_calendar?: Record<string, number> | null;
}

export interface TopicStat {
  topic: string;
  topic_slug: string;
  solved_count: number;
  easy: number;
  medium: number;
  hard: number;
}

export interface TopicsResponse {
  username: string;
  topics: TopicStat[];
}

export interface ProblemInPattern {
  leetcode_id: number;
  title: string;
  slug: string;
  difficulty: "Easy" | "Medium" | "Hard" | "Unknown";
  url: string | null;
  solved_at?: string | null;
  topics?: string[];
  source?: "imported";
}

export interface PatternStat {
  pattern: string;
  pattern_slug: string;
  solved_count: number;
  easy: number;
  medium: number;
  hard: number;
  problems: ProblemInPattern[];
}

export interface PatternsResponse {
  username: string;
  patterns: PatternStat[];
}

export interface CoverageItem {
  pattern: string;
  pattern_slug: string;
  parent: string | null;
  solved_count: number;
  practiced: boolean;
}

export interface CoverageResponse {
  username: string;
  total_patterns: number;
  practiced_count: number;
  coverage_ratio: number;
  items: CoverageItem[];
}

export interface ProblemsResponse {
  username: string;
  total: number;
  total_confirmed?: number;
  problems: ProblemInPattern[];
}

export interface PatternExplorerItem {
  pattern_name: string;
  pattern_slug: string;
  description: string;
  solved_count: number;
  mastery: "Mastered" | "Proficient" | "Practiced" | "Untouched";
  easy: number;
  medium: number;
  hard: number;
  problems: ProblemInPattern[];
  recommended_problems: Array<{
    leetcode_id: number;
    title: string;
    difficulty: string;
    slug: string;
  }>;
}

export interface TopicExplorerItem {
  topic_slug: string;
  topic_name: string;
  description: string;
  icon: string;
  solved_count: number;
  patterns_count: number;
  patterns_mastered: number;
  patterns: PatternExplorerItem[];
}

export interface TaxonomyExplorerResponse {
  username: string;
  total_topics: number;
  total_patterns: number;
  mastered_patterns: number;
  topics: TopicExplorerItem[];
}

export interface StrengthItem {
  title: string;
  metric: string;
  description: string;
  icon: string;
}

export interface BlindspotItem {
  pattern: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  current_solved: number;
  target: number;
  impact: string;
  action: string;
}

export interface RecommendedProblem {
  pattern: string;
  topic: string;
  leetcode_id: number;
  title: string;
  difficulty: string;
  slug: string;
  why: string;
}

export interface StudentAnalysisResponse {
  username: string;
  readiness_score: number;
  readiness_tier: string;
  readiness_color: string;
  readiness_badge: string;
  score_breakdown: {
    breadth: { score: number; max: number; label: string };
    depth: { score: number; max: number; label: string };
    mastery: { score: number; max: number; label: string };
    consistency: { score: number; max: number; label: string };
  };
  strengths: StrengthItem[];
  blindspots: BlindspotItem[];
  recommended_problems: RecommendedProblem[];
  velocity: {
    active_days: number;
    streak: number;
    total_solved: number;
    easy: number;
    medium: number;
    hard: number;
    acceptance_rate: number | null;
    average_per_active_day: number;
  };
}


const enrichPromises: Record<string, Promise<string | null> | undefined> = {};
const currentHistoryKeys: Record<string, string | null> = {};

export async function ensureEnriched(username: string): Promise<string | null> {
  const norm = username.toLowerCase();
  if (enrichPromises[norm]) {
    return enrichPromises[norm];
  }
  const promise = (async () => {
    try {
      const { getStoredProblems } = await import("./history");
      const history = getStoredProblems(username);
      if (history.length > 0) {
        const res = await api.enrichHistory(username, history);
        currentHistoryKeys[norm] = res.history_key || null;
        return res.history_key || null;
      }
    } catch (err) {
      console.warn("Failed to enrich history:", err);
    }
    return null;
  })();
  enrichPromises[norm] = promise;
  return promise;
}

async function analyticsRequest<T>(path: string, username: string): Promise<T> {
  let hKey = await ensureEnriched(username);
  const norm = username.toLowerCase();
  
  const doReq = async (key: string | null) => {
    const p = key ? (path.includes("?") ? `${path}&history_key=${key}` : `${path}?history_key=${key}`) : path;
    return request<T>(p);
  };

  try {
    return await doReq(hKey);
  } catch (err: unknown) {
    if ((err as { status?: number }).status === 409) {
      // Re-enrich
      delete enrichPromises[norm];
      hKey = await ensureEnriched(username);
      return await doReq(hKey);
    }
    throw err;
  }
}

export const api = {
  enrichHistory: (username: string, history: ProblemInPattern[]) =>
    request<{ history_key?: string, problems: ProblemInPattern[] }>(`/api/v1/users/${encodeURIComponent(username)}/enrich`, {
      method: "POST",
      body: JSON.stringify({ history }),
    }),

  getUser: (username: string) =>
    analyticsRequest<UserProfile>(`/api/v1/users/${encodeURIComponent(username)}`, username),

  getOverview: (username: string) =>
    analyticsRequest<Overview>(`/api/v1/users/${encodeURIComponent(username)}/overview`, username),

  getTopics: (username: string) =>
    analyticsRequest<TopicsResponse>(`/api/v1/users/${encodeURIComponent(username)}/topics`, username),

  getPatterns: (username: string) =>
    analyticsRequest<PatternsResponse>(`/api/v1/users/${encodeURIComponent(username)}/patterns`, username),

  getPatternDetail: (username: string, patternSlug: string) =>
    analyticsRequest<PatternStat>(`/api/v1/users/${encodeURIComponent(username)}/patterns/${patternSlug}`, username),

  getCoverage: (username: string) =>
    analyticsRequest<CoverageResponse>(`/api/v1/users/${encodeURIComponent(username)}/gaps`, username),

  getProblems: (username: string, difficulty?: string) => {
    const params = difficulty ? `?difficulty=${difficulty}` : "";
    return analyticsRequest<ProblemsResponse>(`/api/v1/users/${encodeURIComponent(username)}/problems${params}`, username);
  },

  getTaxonomyExplorer: (username: string) =>
    analyticsRequest<TaxonomyExplorerResponse>(`/api/v1/users/${encodeURIComponent(username)}/taxonomy-explorer`, username),

  getStudentAnalysis: (username: string) =>
    analyticsRequest<StudentAnalysisResponse>(`/api/v1/users/${encodeURIComponent(username)}/student-analysis`, username),

  getActivityTimeline: (username: string) =>
    analyticsRequest<ActivityTimelineResponse>(`/api/v1/users/${encodeURIComponent(username)}/activity-timeline`, username),

  getPatternPractice: (username: string) =>
    analyticsRequest<PatternPracticeResponse>(`/api/v1/users/${encodeURIComponent(username)}/pattern-practice`, username),
};

export interface ActivityDayProblem {
  leetcode_id: number;
  title: string;
  slug: string;
  difficulty: string;
  url: string;
  solved_at?: string | null;
}

export interface ActivityDay {
  date: string;
  day_name: string;
  timestamp: number;
  count: number;
  problems_count: number;
  problems: ActivityDayProblem[];
}

export interface ActivityWeek {
  week_start: string;
  week_label: string;
  total_submissions: number;
  active_days: number;
  problems_logged: number;
  days: ActivityDay[];
}

export interface ActivityTimelineResponse {
  username: string;
  total_active_days: number;
  total_submissions_tracked: number;
  streak: number | null;
  peak_day: { date: string | null; count: number };
  most_productive_week: { week_label: string; total: number } | null;
  weeks: ActivityWeek[];
  days: ActivityDay[];
}

export interface CuratedPracticeProblem {
  leetcode_id: number;
  title: string;
  difficulty: string;
  slug: string;
  url: string;
  tier: string;
  companies: string[];
  is_solved: boolean;
  needs_revision?: boolean;
  revision_status?: string;
  days_since_solved?: number | null;
}

export interface PatternPracticeItem {
  pattern_name: string;
  pattern_slug: string;
  parent_topic: string;
  description: string;
  total_problems: number;
  solved_count: number;
  completion_pct: number;
  problems: CuratedPracticeProblem[];
}

export interface TopicGroupPractice {
  topic_group: string;
  patterns: PatternPracticeItem[];
  total_problems: number;
  solved_count: number;
  completion_pct: number;
}

export interface PatternPracticeResponse {
  username: string;
  total_patterns: number;
  total_curated_problems: number;
  total_user_solved_curated: number;
  overall_completion_pct: number;
  total_needs_revision: number;
  revision_queue: {
    leetcode_id: number;
    title: string;
    difficulty: string;
    slug: string;
    pattern: string;
    days_ago: number;
    url: string;
  }[];
  topic_groups: TopicGroupPractice[];
  patterns: PatternPracticeItem[];
}
