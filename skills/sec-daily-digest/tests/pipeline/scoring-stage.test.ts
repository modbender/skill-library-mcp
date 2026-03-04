import { describe, expect, test } from "bun:test";
import type { AIProvider } from "../../src/ai/providers/types";
import { scoreAndClassifyArticles } from "../../src/pipeline/stages/scoring";
import type { Article } from "../../src/rss/parse";

describe("scoring stage", () => {
  test("scores and classifies in one batched provider call", async () => {
    let calls = 0;
    const provider: AIProvider = {
      id: "openai",
      async call() {
        calls += 1;
        return JSON.stringify({
          results: [
            {
              index: 0,
              relevance: 9,
              quality: 8,
              timeliness: 9,
              security: 10,
              ai: 6,
              category: "security",
              keywords: ["CVE", "RCE", "patch"],
            },
            {
              index: 1,
              relevance: 8,
              quality: 7,
              timeliness: 8,
              security: 6,
              ai: 9,
              category: "ai-ml",
              keywords: ["LLM", "agent", "benchmark"],
            },
          ],
        });
      },
    };

    const articles: Article[] = [
      {
        title: "Critical CVE in model gateway",
        link: "https://example.com/a",
        pubDate: new Date("2026-02-27T10:00:00Z"),
        description: "CVE-2026-00001 allows remote code execution",
        sourceName: "feed-a",
        sourceUrl: "https://example.com",
      },
      {
        title: "New LLM agent benchmark",
        link: "https://example.com/b",
        pubDate: new Date("2026-02-27T09:00:00Z"),
        description: "Benchmark evaluates autonomous coding agents",
        sourceName: "feed-b",
        sourceUrl: "https://example.com",
      },
    ];

    const results = await scoreAndClassifyArticles({
      articles,
      provider,
      weights: {
        security: 0.5,
        ai: 0.5,
      },
      batchSize: 10,
      maxConcurrency: 1,
    });

    expect(calls).toBe(1);
    expect(results.length).toBe(articles.length);
    expect(results[0]?.category).toBeDefined();
    expect(results[0]?.keywords.length).toBeGreaterThan(0);
    expect(results[0]?.score).toBeGreaterThan(0);
  });
});
