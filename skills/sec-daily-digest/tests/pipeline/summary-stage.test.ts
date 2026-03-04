import { describe, expect, test } from "bun:test";
import type { AIProvider } from "../../src/ai/providers/types";
import { summarizeSelectedArticles } from "../../src/pipeline/stages/summary";
import type { ScoredArticle } from "../../src/pipeline/types";

describe("summary stage", () => {
  test("summarizes selected articles with structured zh output", async () => {
    let calls = 0;
    const provider: AIProvider = {
      id: "openai",
      async call() {
        calls += 1;
        return JSON.stringify({
          results: [
            {
              index: 0,
              title_zh: "Agent 安全加固指南",
              summary_zh: "面向生产环境的 agent 威胁模型。重点覆盖身份、沙箱、工具权限和审计策略。比较了集中式与最小权限两种方案。给出落地检查清单。",
              reason_zh: "给出了可执行的安全控制清单。",
            },
          ],
        });
      },
    };

    const articles: ScoredArticle[] = [
      {
        index: 0,
        title: "Agent hardening guide",
        link: "https://example.com/a",
        pubDate: new Date("2026-02-27T10:00:00Z"),
        description: "Security controls for autonomous agent deployments",
        sourceName: "feed-a",
        sourceUrl: "https://example.com",
        relevance: 9,
        quality: 8,
        timeliness: 8,
        security: 8,
        ai: 9,
        category: "security",
        keywords: ["agent", "hardening", "sandbox"],
        score: 8.5,
      },
    ];

    const summaries = await summarizeSelectedArticles({
      articles,
      provider,
      lang: "zh",
      batchSize: 10,
      maxConcurrency: 1,
    });

    expect(calls).toBe(1);
    expect(summaries.length).toBe(1);
    expect((summaries[0]?.summaryZh.split("。").filter(Boolean).length ?? 0)).toBeGreaterThanOrEqual(3);
    expect((summaries[0]?.reasonZh.length ?? 0)).toBeGreaterThan(0);
  });
});
