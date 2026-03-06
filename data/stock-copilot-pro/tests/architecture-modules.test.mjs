import test from "node:test";
import assert from "node:assert/strict";

import { applyCapabilityDegradation } from "../scripts/lib/data/fallback.mjs";
import { resolveToolPayload, resolveToolPayloadSync } from "../scripts/lib/infra/qveris-client.mjs";
import { formatForChat } from "../scripts/lib/output/chat/formatter.mjs";
import { buildDecisionCard } from "../scripts/lib/output/decision-card.mjs";

test("HK fundamentals degradation should add warning", () => {
  const parsed = { revenue: null, netProfit: null, operatingCashflow: null, pe: 18.2 };
  const result = applyCapabilityDegradation("fundamentals", "HK", parsed);
  assert.ok(Array.isArray(result.warnings));
  assert.equal(result.warnings.length, 1);
  assert.equal(result.parsed.pe, 18.2);
});

test("chat formatter returns segmented output", () => {
  const sample = {
    symbol: "AAPL",
    market: "US",
    data: {
      quote: { parsed: { price: 200, percentChange: 1.2, volume: 1000 } },
      fundamentals: { parsed: { pe: 30, pb: 10, revenue: 100, netProfit: 20 } },
      sentiment: { parsed: { itemCount: 5 } },
      x_sentiment: { parsed: { itemCount: 8 } },
    },
    analysis: {
      scorecard: { grade: "B+" },
      recommendation: { signal: "买入" },
      chaseRisk: { risk: "low" },
    },
  };
  const chat = formatForChat(sample);
  assert.ok(chat.segments.length >= 3);
  assert.equal(chat.symbol, "AAPL");
});

test("decision card should output light signal text", () => {
  const sample = {
    symbol: "NVDA",
    market: "US",
    analysis: {
      scorecard: { composite: 81, grade: "B+" },
      recommendation: { signal: "买入" },
      chaseRisk: { risk: "medium" },
    },
  };
  const card = buildDecisionCard(sample);
  assert.ok(card.asText.includes("NVDA"));
  assert.equal(card.light, "偏积极");
});

test("resolveToolPayloadSync should parse truncated_content JSON", () => {
  const raw = {
    result: {
      truncated_content: "{\"items\":[1,2,3]}",
      full_content_file_url: "https://example.com/full.json",
    },
  };
  const resolved = resolveToolPayloadSync(raw);
  assert.equal(resolved.meta.contentMode, "truncated_content");
  assert.equal(resolved.meta.hasTruncatedContent, true);
  assert.deepEqual(resolved.content, { items: [1, 2, 3] });
});

test("resolveToolPayload should fallback to full_content_file_url when truncated invalid", async () => {
  const raw = {
    result: {
      truncated_content: "{\"items\":[1,2,3}",
      full_content_file_url: "https://qveris.ai/mock/full.json",
    },
  };
  const fakeFetch = async () => ({
    ok: true,
    async json() {
      return { items: [9, 8, 7] };
    },
  });
  const resolved = await resolveToolPayload(raw, { fetchImpl: fakeFetch, timeoutMs: 1000 });
  assert.equal(resolved.meta.contentMode, "full_content_file_url");
  assert.equal(resolved.meta.hasTruncatedContent, true);
  assert.deepEqual(resolved.content, { items: [9, 8, 7] });
});

test("resolveToolPayload should block non-qveris full_content_file_url host", async () => {
  const raw = {
    result: {
      truncated_content: "{\"items\":[1,2,3}",
      full_content_file_url: "https://example.com/full.json",
    },
  };
  let called = false;
  const fakeFetch = async () => {
    called = true;
    return { ok: true, async json() { return { items: [0] }; } };
  };
  const resolved = await resolveToolPayload(raw, { fetchImpl: fakeFetch, timeoutMs: 1000 });
  assert.equal(called, false);
  assert.equal(resolved.meta.contentMode, "payload");
  assert.equal(resolved.meta.hasTruncatedContent, true);
  assert.match(String(resolved.meta.fetchError || ""), /blocked host/i);
});
