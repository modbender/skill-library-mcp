import { clampScore, gradeFromScore, toNumber } from "./utils.mjs";
import { pickSectorBenchmarks } from "./data.mjs";

export function buildScorecard(payload, benchmarks, market) {
  const f = payload.fundamentals?.parsed || {};
  const t = payload.technicals?.parsed || {};
  const s = payload.sentiment?.parsed || {};
  const x = payload.x_sentiment?.parsed || {};
  const b = pickSectorBenchmarks(benchmarks, market);

  let valuation = 50;
  if (f.pe != null && b.pe_median) {
    const ratio = f.pe / b.pe_median;
    if (ratio <= 0.7) valuation += 25;
    else if (ratio <= 0.9) valuation += 15;
    else if (ratio <= 1.1) valuation += 5;
    else if (ratio >= 1.5) valuation -= 20;
    else valuation -= 8;
  }
  if (f.pb != null && b.pb_median) {
    const ratio = f.pb / b.pb_median;
    if (ratio <= 0.7) valuation += 18;
    else if (ratio <= 0.9) valuation += 10;
    else if (ratio <= 1.1) valuation += 3;
    else if (ratio >= 1.6) valuation -= 18;
    else valuation -= 8;
  }

  let quality = 50;
  const margin = f.profitMargin != null ? f.profitMargin : f.revenue && f.netProfit ? f.netProfit / f.revenue : null;
  if (margin != null && b.profit_margin_benchmark != null) quality += margin >= b.profit_margin_benchmark ? 12 : -8;
  if (f.totalAssets != null && f.totalLiabilities != null && f.totalAssets > 0) {
    const debtRatio = f.totalLiabilities / f.totalAssets;
    quality += debtRatio <= (b.debt_ratio_warn ?? 0.6) ? 12 : -10;
  }
  if (f.operatingCashflow != null) quality += f.operatingCashflow > 0 ? 15 : -12;

  let growth = 50;
  if (f.revenueGrowthYoy != null) {
    if (f.revenueGrowthYoy >= 20) growth += 22;
    else if (f.revenueGrowthYoy >= 10) growth += 14;
    else if (f.revenueGrowthYoy >= 0) growth += 6;
    else growth -= 12;
  }
  if (f.earningsGrowthYoy != null) growth += f.earningsGrowthYoy >= 0 ? 8 : -8;

  let technicals = 50;
  if (t.rsi != null) {
    if (t.rsi >= 40 && t.rsi <= 65) technicals += 12;
    else if (t.rsi > 70) technicals -= 8;
    else if (t.rsi < 30) technicals += 5;
  }
  if (t.changeRatio != null) technicals += t.changeRatio > 0 ? 6 : -4;
  if (t.change5d != null) technicals += t.change5d > 0 ? 8 : -6;

  let sentiment = 50;
  if (s.itemCount != null) sentiment += Math.min(10, s.itemCount * 2);
  if (s.latestTickerSentiment != null && typeof s.latestTickerSentiment === "number") sentiment += s.latestTickerSentiment > 0 ? 8 : -6;
  if (x.itemCount != null) sentiment += Math.min(8, x.itemCount);

  const weights = { valuation: 0.3, quality: 0.25, growth: 0.2, technicals: 0.15, sentiment: 0.1 };
  const score = {
    valuation: clampScore(valuation),
    quality: clampScore(quality),
    growth: clampScore(growth),
    technicals: clampScore(technicals),
    sentiment: clampScore(sentiment),
  };
  const composite = clampScore(
    score.valuation * weights.valuation +
      score.quality * weights.quality +
      score.growth * weights.growth +
      score.technicals * weights.technicals +
      score.sentiment * weights.sentiment,
  );
  return { weights, score, composite, grade: gradeFromScore(composite) };
}

export function buildFinancialQuality(payload, benchmarks, market) {
  const f = payload.fundamentals?.parsed || {};
  const b = pickSectorBenchmarks(benchmarks, market);
  const debtRatio = f.totalAssets > 0 ? toNumber(f.totalLiabilities) / toNumber(f.totalAssets) : null;
  const margin = f.profitMargin != null ? f.profitMargin : f.revenue && f.netProfit ? f.netProfit / f.revenue : null;
  const ocfConsistency =
    f.operatingCashflow != null && f.netProfit != null
      ? f.operatingCashflow >= 0 && f.netProfit >= 0
        ? "strong"
        : f.operatingCashflow < 0 && f.netProfit > 0
          ? "weak"
          : "mixed"
      : "unknown";
  return {
    debtRatio,
    debtRisk:
      debtRatio == null ? "unknown" : debtRatio > (b.debt_ratio_warn ?? 0.6) ? "high" : debtRatio > (b.debt_ratio_warn ?? 0.6) * 0.85 ? "medium" : "low",
    profitMargin: margin,
    marginVsBenchmark: margin == null || b.profit_margin_benchmark == null ? "unknown" : margin >= b.profit_margin_benchmark ? "above" : "below",
    cashflowConsistency: ocfConsistency,
  };
}

export function buildValuationFrame(payload, scorecard, benchmarks, market) {
  const q = payload.quote?.parsed || {};
  const f = payload.fundamentals?.parsed || {};
  const b = pickSectorBenchmarks(benchmarks, market);

  const peRatio = f.pe != null && b.pe_median ? f.pe / b.pe_median : null;
  const pbRatio = f.pb != null && b.pb_median ? f.pb / b.pb_median : null;
  const verdictScore = scorecard?.score?.valuation ?? 50;
  const verdict =
    verdictScore >= 75
      ? "undervalued"
      : verdictScore >= 58
        ? "fair"
        : verdictScore >= 45
          ? "slightly_overvalued"
          : "overvalued";

  const currentPrice = q.price;
  let conservativeValue = null;
  if (currentPrice != null && f.pe != null && f.pe > 0 && b.pe_median) {
    conservativeValue = currentPrice * (b.pe_median / f.pe) * 0.8;
  }
  const marginOfSafety =
    conservativeValue && conservativeValue > 0 ? ((conservativeValue - currentPrice) / conservativeValue) * 100 : null;

  return {
    relative: {
      pe: { current: f.pe ?? null, industryMedian: b.pe_median ?? null, ratioToMedian: peRatio },
      pb: { current: f.pb ?? null, industryMedian: b.pb_median ?? null, ratioToMedian: pbRatio },
      ps: { current: f.ps ?? null, industryMedian: null, ratioToMedian: null },
    },
    intrinsic: {
      currentPrice: currentPrice ?? null,
      conservativeValue,
      marginOfSafety,
    },
    verdict,
    confidence: scorecard?.composite >= 70 ? "high" : scorecard?.composite >= 55 ? "medium" : "low",
  };
}

export function detectChaseRisk(payload) {
  const q = payload.quote?.parsed || {};
  const t = payload.technicals?.parsed || {};
  const s = payload.sentiment?.parsed || {};
  const change5d = t.change5d;
  const change1d = q.percentChange;
  const volumeRatio = t.volumeRatio;
  let classification = "事件驱动型";
  let signal = "可买入";
  let risk = "low";
  if ((change5d != null && change5d >= 10) || (change1d != null && change1d >= 5) || (volumeRatio != null && volumeRatio >= 1.8)) {
    classification = "交易回踩型";
    signal = "需谨慎/回避";
    risk = "high";
  } else if ((change5d != null && change5d >= 5) || (change1d != null && change1d >= 3) || (volumeRatio != null && volumeRatio >= 1.5)) {
    classification = "交易回踩型-轻度";
    signal = "需谨慎，可关注回踩机会";
    risk = "medium";
  }
  const hasEvent = (s.itemCount || 0) > 0;
  return { classification, signal, risk, hasEvent, metrics: { change5d, change1d, volumeRatio, newsCount: s.itemCount ?? 0 } };
}

export function buildThesis(payload, market, scorecard, valuationFrame, financialQuality, eventRadar) {
  const f = payload.fundamentals?.parsed || {};
  const t = payload.technicals?.parsed || {};
  const keyDrivers = [];
  const keyRisks = [];
  if (f.revenueGrowthYoy != null) {
    keyDrivers.push({
      factor: "营收增长动能",
      evidence: `营收同比 ${f.revenueGrowthYoy}`,
      trackingKPI: "季度营收同比增速",
      invalidationCondition: "营收同比连续两个季度转负",
    });
  }
  if (t.change5d != null && t.change5d > 0) {
    keyDrivers.push({
      factor: "短期趋势改善",
      evidence: `近5日涨跌 ${t.change5d.toFixed(2)}%`,
      trackingKPI: "20日趋势与成交量配合",
      invalidationCondition: "趋势破位且放量下跌",
    });
  }
  if (financialQuality.debtRisk === "high") {
    keyRisks.push({
      category: "financial",
      description: "资产负债结构承压，杠杆风险偏高",
      severity: "high",
      mitigationPossible: false,
    });
  }
  if (valuationFrame.verdict.includes("overvalued")) {
    keyRisks.push({
      category: "valuation",
      description: "估值偏高，安全边际不足",
      severity: "medium",
      mitigationPossible: true,
    });
  }
  if ((eventRadar?.events || []).length > 0) {
    keyRisks.push({
      category: "event",
      description: "事件驱动波动增强，消息面变化可能快速影响价格",
      severity: "medium",
      mitigationPossible: true,
    });
  }
  const composite = scorecard?.composite ?? 50;
  return {
    market,
    businessSummary: {
      industry: f.industry || "N/A",
      mainBusiness: f.mainBusiness || "N/A",
      tags: f.tags || [],
    },
    keyDrivers,
    keyRisks,
    scenarios: {
      bull: {
        condition: "盈利增速修复+估值扩张",
        probability: composite >= 70 ? "medium-high" : "medium",
      },
      base: {
        condition: "盈利稳定+估值中枢维持",
        probability: "high",
      },
      bear: {
        condition: "业绩不及预期或宏观流动性收紧",
        probability: composite < 55 ? "medium-high" : "medium",
      },
    },
    trackingKPIs: [
      "营收同比",
      "净利润同比",
      "经营现金流",
      "PE/PB 相对行业",
      "趋势强弱与量能",
      "重点事件进展",
    ],
  };
}

