import { describe, expect, test } from "bun:test";
import { buildHighlightsPrompt, buildScoringPrompt, buildSummaryPrompt } from "../../src/ai/prompts";

describe("ai prompts", () => {
  test("buildScoringPrompt includes rubric and output schema", () => {
    const prompt = buildScoringPrompt([
      {
        index: 0,
        title: "Critical CVE in AI gateway",
        description: "CVE-2026-12345 remote code execution details",
        sourceName: "feed-a",
        link: "https://example.com/a",
      },
    ]);

    expect(prompt).toContain("评分维度");
    expect(prompt).toContain("category");
    expect(prompt).toContain("keywords");
    expect(prompt).toContain("\"results\"");
  });

  test("buildSummaryPrompt requests structured zh summary and reason", () => {
    const prompt = buildSummaryPrompt(
      [
        {
          index: 0,
          title: "Agent hardening guide",
          description: "Security controls for autonomous agent deployments",
          sourceName: "feed-a",
          link: "https://example.com/a",
          category: "security",
          keywords: ["agent", "hardening"],
        },
      ],
      "zh",
    );

    expect(prompt).toContain("4-6");
    expect(prompt).toContain("title_zh");
    expect(prompt).toContain("summary_zh");
    expect(prompt).toContain("reason_zh");
  });

  test("buildHighlightsPrompt asks for macro trends", () => {
    const prompt = buildHighlightsPrompt(
      [
        {
          index: 0,
          category: "security",
          titleZh: "AI 网关高危漏洞",
          summaryZh: "多个厂商发布紧急补丁并建议隔离部署。",
        },
      ],
      "zh",
    );

    expect(prompt).toContain("2-3");
    expect(prompt).toContain("3-5");
    expect(prompt).toContain("不要逐篇列举");
  });
});
