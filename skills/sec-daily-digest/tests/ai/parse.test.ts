import { describe, expect, test } from "bun:test";
import { parseJsonBlock, validateScoringResult, validateSummaryResult } from "../../src/ai/parse";

describe("ai parse", () => {
  test("parseJsonBlock handles fenced json", () => {
    const parsed = parseJsonBlock<{ a: number }>("```json\n{\"a\":1}\n```");
    expect(parsed).toEqual({ a: 1 });
  });

  test("validateScoringResult rejects invalid payload", () => {
    const invalid = validateScoringResult({
      index: 0,
      relevance: 9,
      quality: 8,
      timeliness: 7,
      security: 8,
      ai: 7,
      category: "unknown",
      keywords: ["a"],
    });
    expect(invalid).toBeNull();
  });

  test("validateSummaryResult accepts valid payload", () => {
    const valid = validateSummaryResult({
      index: 0,
      title_zh: "中文标题",
      summary_zh: "一句。二句。三句。四句。",
      reason_zh: "值得读。",
    });

    expect(valid).not.toBeNull();
    expect(valid?.reasonZh).toBeDefined();
  });
});
