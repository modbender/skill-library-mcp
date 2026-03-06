import { buildHighlightsPrompt } from "../../ai/prompts";
import type { AIProvider } from "../../ai/providers/types";
import type { FinalArticle } from "../types";

interface GenerateHighlightsOptions {
  articles: FinalArticle[];
  provider: AIProvider | null;
  lang: "zh" | "en";
}

function fallbackHighlights(articles: FinalArticle[], lang: "zh" | "en"): string {
  if (articles.length === 0) {
    return "";
  }
  const securityCount = articles.filter((item) => item.security >= item.ai).length;
  const aiCount = articles.length - securityCount;
  const topKeywords = new Map<string, number>();
  for (const article of articles) {
    for (const keyword of article.keywords) {
      const normalized = keyword.toLowerCase();
      topKeywords.set(normalized, (topKeywords.get(normalized) ?? 0) + 1);
    }
  }
  const keywordList = [...topKeywords.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([keyword]) => keyword)
    .join("、");

  if (lang === "en") {
    return `Today's trend: security-focused stories ${securityCount} and AI-focused stories ${aiCount}. Key topics concentrate on ${keywordList || "incident response, model security, and governance"}.`;
  }

  return `今日趋势：安全向议题 ${securityCount} 篇、AI向议题 ${aiCount} 篇。高频话题集中在 ${keywordList || "漏洞响应、模型安全与治理"}，显示安全与智能系统正在快速收敛。`;
}

export async function generateTrendHighlights(options: GenerateHighlightsOptions): Promise<string> {
  const seeds = options.articles.slice(0, 10).map((article, index) => ({
    index,
    category: article.category,
    titleZh: article.titleZh,
    summaryZh: article.summaryZh,
  }));

  if (!options.provider) {
    return fallbackHighlights(options.articles, options.lang);
  }

  try {
    const prompt = buildHighlightsPrompt(seeds, options.lang);
    const response = await options.provider.call(prompt);
    const trimmed = response.trim();
    if (trimmed.length > 0) {
      return trimmed;
    }
  } catch {
    // Fall back to deterministic trends.
  }

  return fallbackHighlights(options.articles, options.lang);
}
