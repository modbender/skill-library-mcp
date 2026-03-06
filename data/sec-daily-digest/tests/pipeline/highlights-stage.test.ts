import { describe, expect, test } from "bun:test";
import type { AIProvider } from "../../src/ai/providers/types";
import { generateTrendHighlights } from "../../src/pipeline/stages/highlights";
import type { FinalArticle } from "../../src/pipeline/types";

describe("highlights stage", () => {
  test("generates macro trend highlights", async () => {
    const provider: AIProvider = {
      id: "openai",
      async call() {
        return "今天的趋势是 AI 系统供应链风险上升，以及漏洞披露节奏加快。";
      },
    };

    const articles: FinalArticle[] = [
      {
        index: 0,
        title: "Critical CVE in model gateway",
        titleZh: "模型网关高危漏洞",
        link: "https://example.com/a",
        pubDate: new Date("2026-02-27T10:00:00Z"),
        description: "CVE-2026-00001 allows remote code execution",
        sourceName: "feed-a",
        sourceUrl: "https://example.com",
        relevance: 9,
        quality: 8,
        timeliness: 9,
        security: 10,
        ai: 6,
        category: "security",
        keywords: ["CVE", "RCE", "patch"],
        score: 8.9,
        summaryZh: "披露了可远程执行漏洞并附带缓解建议。",
        reasonZh: "直接影响生产网关安全边界。",
      },
    ];

    const highlights = await generateTrendHighlights({
      articles,
      provider,
      lang: "zh",
    });

    expect(highlights).toContain("趋势");
  });
});
