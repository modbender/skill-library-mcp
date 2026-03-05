import type { CategoryId, ScoringResultItem, SummaryResultItem } from "../pipeline/types";

const VALID_CATEGORIES: ReadonlySet<CategoryId> = new Set(["ai-ml", "security", "engineering", "tools", "opinion", "other"]);

function clampScore(value: number): number {
  return Math.max(1, Math.min(10, Math.round(value)));
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function asString(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function asStringArray(value: unknown): string[] | null {
  if (!Array.isArray(value)) {
    return null;
  }
  const list = value.filter((item): item is string => typeof item === "string").map((item) => item.trim()).filter(Boolean);
  return list.length > 0 ? list : null;
}

export function parseJsonBlock<T>(text: string): T {
  let raw = text.trim();
  if (raw.startsWith("```")) {
    raw = raw.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  }
  return JSON.parse(raw) as T;
}

export function validateScoringResult(payload: unknown): ScoringResultItem | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  const obj = payload as Record<string, unknown>;
  const index = asNumber(obj.index);
  const relevance = asNumber(obj.relevance);
  const quality = asNumber(obj.quality);
  const timeliness = asNumber(obj.timeliness);
  const security = asNumber(obj.security);
  const ai = asNumber(obj.ai);
  const categoryRaw = asString(obj.category);
  const keywordsRaw = asStringArray(obj.keywords);

  if (
    index === null ||
    relevance === null ||
    quality === null ||
    timeliness === null ||
    security === null ||
    ai === null ||
    !categoryRaw ||
    !VALID_CATEGORIES.has(categoryRaw as CategoryId) ||
    !keywordsRaw
  ) {
    return null;
  }

  return {
    index: Math.max(0, Math.floor(index)),
    relevance: clampScore(relevance),
    quality: clampScore(quality),
    timeliness: clampScore(timeliness),
    security: clampScore(security),
    ai: clampScore(ai),
    category: categoryRaw as CategoryId,
    keywords: keywordsRaw.slice(0, 4),
  };
}

export function validateSummaryResult(payload: unknown): SummaryResultItem | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  const obj = payload as Record<string, unknown>;
  const index = asNumber(obj.index);
  const titleZh = asString(obj.title_zh);
  const summaryZh = asString(obj.summary_zh);
  const reasonZh = asString(obj.reason_zh);

  if (index === null || !titleZh || !summaryZh || !reasonZh) {
    return null;
  }

  return {
    index: Math.max(0, Math.floor(index)),
    titleZh: titleZh.trim(),
    summaryZh: summaryZh.trim(),
    reasonZh: reasonZh.trim(),
  };
}

export function parseScoringResults(text: string): ScoringResultItem[] {
  try {
    const parsed = parseJsonBlock<{ results?: unknown[] }>(text);
    if (!Array.isArray(parsed.results)) {
      return [];
    }
    return parsed.results.map(validateScoringResult).filter((item): item is ScoringResultItem => item !== null);
  } catch {
    return [];
  }
}

export function parseSummaryResults(text: string): SummaryResultItem[] {
  try {
    const parsed = parseJsonBlock<{ results?: unknown[] }>(text);
    if (!Array.isArray(parsed.results)) {
      return [];
    }
    return parsed.results.map(validateSummaryResult).filter((item): item is SummaryResultItem => item !== null);
  } catch {
    return [];
  }
}
