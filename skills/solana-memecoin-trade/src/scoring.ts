import { DexMetrics, TokenMeta } from "./types.js";

export function riskScore(metrics: DexMetrics, meta: TokenMeta): number {
  // 0..100 higher is worse
  let score = 0;

  // Liquidity penalty (0..25)
  if (metrics.liqUsd < 200_000) score += Math.min(25, (200_000 - metrics.liqUsd) / 8_000);

  // Holder concentration (0..25)
  if (meta.singleHolderPct !== null) score += Math.min(15, Math.max(0, meta.singleHolderPct - 5) * 1.5);
  if (meta.top10HoldersPct !== null) score += Math.min(10, Math.max(0, meta.top10HoldersPct - 35) * 0.5);

  // Slippage/impact proxy via vol/tx and price change (0..20)
  const volPerTx = metrics.tx5m > 0 ? metrics.vol5mUsd / metrics.tx5m : metrics.vol5mUsd;
  score += Math.min(10, Math.max(0, (volPerTx - 800) / 200));
  score += Math.min(10, Math.max(0, Math.abs(metrics.priceChange5mPct) - 15) * 0.5);

  // Age penalty (0..10)
  if (metrics.pairAgeMin < 60) score += Math.min(10, (60 - metrics.pairAgeMin) / 6);

  // Tx anomaly (0..15)
  if (metrics.tx5m < 50) score += Math.min(15, (50 - metrics.tx5m) / 3);

  return Math.max(0, Math.min(100, Math.round(score)));
}

export function aiSignal(metrics: DexMetrics, cfg: any): { buy: boolean; reason: string } {
  const s = cfg.ai_signal;
  const volPerTx = metrics.tx5m > 0 ? metrics.vol5mUsd / metrics.tx5m : metrics.vol5mUsd;

  if (metrics.tx5m < s.min_tx5m) return { buy: false, reason: "txTooLow" };
  if (volPerTx > s.max_vol_per_tx_usd) return { buy: false, reason: "whalePrintLikely" };
  if (Math.abs(metrics.priceChange5mPct) > s.max_price_change_5m_pct) return { buy: false, reason: "tooSpiky" };

  return { buy: true, reason: "stableFlow" };
}
