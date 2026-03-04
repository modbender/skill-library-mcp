import test from "node:test";
import assert from "node:assert/strict";

import { formatMarkdown } from "./stock_copilot_pro.mjs";

function minimalResultWithOriginal(original) {
  return {
    symbol: "TEST",
    market: "US",
    mode: "basic",
    data: {
      quote: { parsed: {} },
      fundamentals: { parsed: {} },
      technicals: { parsed: {} },
      sentiment: { parsed: {} },
      x_sentiment: { parsed: {} },
    },
    quality: { confidence: 0.5, warnings: [] },
    evolution: { route_source: {}, template_hits: 0, new_tools_learned: [] },
    analysis: { scorecard: {}, safetyMargin: {}, chaseRisk: {}, recommendation: {} },
    runtime: { includeSourceUrls: false, resolvedInput: { original } },
  };
}

test("reportify-custom blocks are rendered as fenced code blocks (not raw HTML)", () => {
  const original =
    "hello <reportify-custom><img src=x onerror=alert(1)><script>alert(1)</script></reportify-custom> bye";
  const out = formatMarkdown(minimalResultWithOriginal(original));

  // Previously it was: "## reportify-custom\n<reportify-custom...>"
  assert.ok(!out.includes("## reportify-custom\n<reportify-custom"), "custom block should not be emitted raw");
  assert.ok(out.includes("## reportify-custom（安全呈现）"), "should include safe custom section header");
  assert.ok(out.includes("```reportify-custom"), "should include fenced code block with info string");
});

test("fence length expands when content contains triple backticks", () => {
  const original =
    "<reportify-custom>some content with ``` inside</reportify-custom>";
  const out = formatMarkdown(minimalResultWithOriginal(original));

  // We expect at least 4 backticks fence in this case to avoid premature closing.
  assert.ok(out.includes("````reportify-custom"), "should use a longer fence when content contains ```");
});

