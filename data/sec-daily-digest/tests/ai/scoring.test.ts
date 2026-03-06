import { describe, expect, test } from "bun:test";
import { computeCompositeScore, fallbackScoreFromText, inferTopicSignals } from "../../src/ai/scoring";

describe("ai scoring helpers", () => {
  test("applies balanced 50/50 security-ai weighting", () => {
    const score = computeCompositeScore({
      security: 8,
      ai: 6,
      quality: 7,
      timeliness: 7,
    });
    expect(score).toBe(7);
  });

  test("infers topic signals from title/description", () => {
    const signals = inferTopicSignals("CVE exploit in model server", "AI inference endpoint vulnerability");
    expect(signals.security).toBeGreaterThan(6);
    expect(signals.ai).toBeGreaterThan(6);
  });

  test("fallback score keeps value in [1, 10]", () => {
    const score = fallbackScoreFromText({
      title: "Monthly changelog",
      description: "Routine updates for multiple modules",
      pubDate: new Date(),
    });
    expect(score.relevance).toBeGreaterThanOrEqual(1);
    expect(score.relevance).toBeLessThanOrEqual(10);
  });
});
