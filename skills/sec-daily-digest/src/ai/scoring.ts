export interface ScoreInput {
  security: number;
  ai: number;
  quality: number;
  timeliness: number;
}

export interface ScoreOutput {
  relevance: number;
  quality: number;
  timeliness: number;
  security: number;
  ai: number;
  composite: number;
}

function clampScore(value: number): number {
  return Math.min(10, Math.max(1, Math.round(value)));
}

const SECURITY_TERMS = [
  "cve",
  "vulnerability",
  "exploit",
  "rce",
  "xss",
  "security",
  "malware",
  "breach",
  "patch",
  "zero-day",
];

const AI_TERMS = [
  "ai",
  "llm",
  "agent",
  "model",
  "inference",
  "gemini",
  "openai",
  "claude",
  "embedding",
  "rag",
];

function keywordScore(text: string, terms: string[]): number {
  const lower = text.toLowerCase();
  let hits = 0;
  for (const term of terms) {
    if (lower.includes(term)) {
      hits += 1;
    }
  }
  return hits;
}

export function inferTopicSignals(title: string, description: string): { security: number; ai: number } {
  const text = `${title} ${description}`;
  const securityHits = keywordScore(text, SECURITY_TERMS);
  const aiHits = keywordScore(text, AI_TERMS);

  return {
    security: clampScore(4 + securityHits),
    ai: clampScore(4 + aiHits),
  };
}

export function computeCompositeScore(input: ScoreInput): number {
  const topic = 0.5 * input.security + 0.5 * input.ai;
  const qualityBlend = 0.5 * input.quality + 0.5 * input.timeliness;
  return Number((0.7 * topic + 0.3 * qualityBlend).toFixed(2));
}

export function fallbackScoreFromText(article: {
  title: string;
  description: string;
  pubDate: Date;
}): ScoreOutput {
  const signals = inferTopicSignals(article.title, article.description);
  const hoursAge = Math.max(0, (Date.now() - article.pubDate.getTime()) / (1000 * 60 * 60));
  const timeliness = clampScore(10 - Math.floor(hoursAge / 12));
  const quality = clampScore(5 + Math.min(3, Math.floor(article.description.length / 180)));
  const relevance = clampScore(Math.round(0.5 * signals.security + 0.5 * signals.ai));
  const composite = computeCompositeScore({
    security: signals.security,
    ai: signals.ai,
    quality,
    timeliness,
  });

  return {
    relevance,
    quality,
    timeliness,
    security: signals.security,
    ai: signals.ai,
    composite,
  };
}
