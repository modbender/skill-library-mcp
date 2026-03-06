import { isStale } from "./utils.mjs";

export function pickSectorBenchmarks(benchmarks, market) {
  if (market === "CN" || market === "HK") return benchmarks.electrical_equipment || benchmarks.default;
  if (market === "US") return benchmarks.semiconductor || benchmarks.default;
  return benchmarks.default;
}

export function summarizeQuality(payload) {
  const warnings = [];
  const quote = payload.quote?.parsed;
  const fundamentals = payload.fundamentals?.parsed;
  const technicals = payload.technicals?.parsed;
  const sentiment = payload.sentiment?.parsed;

  if (!quote?.price) warnings.push("行情缺少最新价格字段");
  if (!fundamentals?.pe && !fundamentals?.marketCap) warnings.push("基本面关键估值字段缺失");
  if (technicals && technicals.rsi == null && technicals.changeRatio == null) warnings.push("技术指标缺少 RSI/趋势字段");
  if (sentiment && !sentiment.itemCount) warnings.push("情绪数据缺少新闻条目");

  if (isStale(quote?.timestamp, 5)) warnings.push("行情数据可能已过期（超过 5 天）");
  if (isStale(fundamentals?.latestQuarter, 220)) warnings.push("基本面季度数据较旧");

  let confidence = "high";
  if (warnings.length >= 2) confidence = "medium";
  if (warnings.length >= 4) confidence = "low";
  return { confidence, warnings };
}

