import { gradeEmoji, riskEmoji } from "./emoji.mjs";

export function buildSignalSummary(result) {
  const grade = result?.analysis?.scorecard?.grade || "N/A";
  const signal = result?.analysis?.recommendation?.signal || "N/A";
  const risk = result?.analysis?.chaseRisk?.risk || "unknown";
  return `${gradeEmoji(grade)} ${result.symbol} | 评级 ${grade} | 信号 ${signal} | 风险 ${riskEmoji(risk)} ${risk}`;
}

export function buildQuoteSegment(result) {
  const q = result?.data?.quote?.parsed || {};
  return `行情: 现价 ${q.price ?? "N/A"}，涨跌 ${q.percentChange ?? "N/A"}%，量 ${q.volume ?? "N/A"}`;
}

export function buildFundamentalsSegment(result) {
  const f = result?.data?.fundamentals?.parsed || {};
  return `基本面: PE ${f.pe ?? "N/A"}，PB ${f.pb ?? "N/A"}，营收 ${f.revenue ?? "N/A"}，净利 ${f.netProfit ?? "N/A"}`;
}

export function buildSentimentSegment(result) {
  const s = result?.data?.sentiment?.parsed || {};
  const x = result?.data?.x_sentiment?.parsed || {};
  return `情绪: 新闻 ${s.itemCount ?? 0} 条，X 热度 ${x.itemCount ?? 0}`;
}

export function buildRecommendationSegment(result) {
  const r = result?.analysis?.recommendation || {};
  return `策略: ${r.signal || "N/A"}，周期 ${r.horizon || "N/A"}`;
}
