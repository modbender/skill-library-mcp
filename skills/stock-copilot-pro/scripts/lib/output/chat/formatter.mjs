import {
  buildFundamentalsSegment,
  buildQuoteSegment,
  buildRecommendationSegment,
  buildSentimentSegment,
  buildSignalSummary,
} from "./segments.mjs";

export function formatForChat(result, options = {}) {
  const segments = [];
  segments.push({ type: "summary", content: buildSignalSummary(result), canExpand: true });
  if (options.includeDetails !== false) {
    segments.push({ type: "quote", content: buildQuoteSegment(result) });
    segments.push({ type: "fundamentals", content: buildFundamentalsSegment(result) });
    segments.push({ type: "sentiment", content: buildSentimentSegment(result) });
    segments.push({ type: "recommendation", content: buildRecommendationSegment(result) });
  }
  return {
    symbol: result?.symbol || "N/A",
    market: result?.market || "GLOBAL",
    segments,
  };
}
