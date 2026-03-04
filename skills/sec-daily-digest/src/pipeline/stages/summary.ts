import { parseSummaryResults } from "../../ai/parse";
import { buildSummaryPrompt } from "../../ai/prompts";
import type { AIProvider } from "../../ai/providers/types";
import type { FinalArticle, ScoredArticle } from "../types";

interface SummarizeSelectedOptions {
  articles: ScoredArticle[];
  provider: AIProvider | null;
  lang: "zh" | "en";
  batchSize?: number;
  maxConcurrency?: number;
}

function toFallbackSummary(text: string): string {
  const trimmed = text.trim();
  if (trimmed.length <= 220) {
    return trimmed;
  }
  return `${trimmed.slice(0, 220)}...`;
}

function buildBatches<T>(items: T[], batchSize: number): T[][] {
  const batches: T[][] = [];
  for (let i = 0; i < items.length; i += batchSize) {
    batches.push(items.slice(i, i + batchSize));
  }
  return batches;
}

export async function summarizeSelectedArticles(options: SummarizeSelectedOptions): Promise<FinalArticle[]> {
  const batchSize = Math.max(1, options.batchSize ?? 10);
  const maxConcurrency = Math.max(1, options.maxConcurrency ?? 2);
  const indexed = options.articles.map((article, index) => ({
    index,
    article,
  }));
  const byIndex = new Map<number, { titleZh: string; summaryZh: string; reasonZh: string }>();

  if (options.provider) {
    const batches = buildBatches(indexed, batchSize);
    for (let i = 0; i < batches.length; i += maxConcurrency) {
      const group = batches.slice(i, i + maxConcurrency);
      await Promise.all(
        group.map(async (batch) => {
          try {
            const prompt = buildSummaryPrompt(
              batch.map(({ index, article }) => ({
                index,
                title: article.title,
                description: article.description,
                sourceName: article.sourceName,
                link: article.link,
                category: article.category,
                keywords: article.keywords,
              })),
              options.lang,
            );
            const response = await options.provider!.call(prompt);
            const parsed = parseSummaryResults(response);
            for (const item of parsed) {
              byIndex.set(item.index, {
                titleZh: item.titleZh,
                summaryZh: item.summaryZh,
                reasonZh: item.reasonZh,
              });
            }
          } catch {
            // Fall back below.
          }
        }),
      );
    }
  }

  return indexed.map(({ index, article }) => {
    const parsed = byIndex.get(index);
    const fallbackSummary = toFallbackSummary(article.description || article.title);
    return {
      ...article,
      index,
      titleZh: parsed?.titleZh?.trim() || article.title,
      summaryZh: parsed?.summaryZh?.trim() || fallbackSummary,
      reasonZh: parsed?.reasonZh?.trim() || "",
    };
  });
}
