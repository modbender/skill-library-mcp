import { DexMetrics, TokenMeta } from "./types.js";

export type GateResult = { reject: boolean; reason?: string };

export function riskGate(metrics: DexMetrics, meta: TokenMeta, cfg: any): GateResult {
  const g = cfg.risk_gates;

  if (metrics.liqUsd < g.min_liquidity_usd) return { reject: true, reason: "liquidityTooLow" };
  if (metrics.pairAgeMin < g.cooldown_token_age_min) return { reject: true, reason: "tokenTooNew" };

  // Missing critical data => reject (safe default)
  if (g.reject_if_mint_authority && meta.mintAuthorityActive === null) return { reject: true, reason: "mintAuthorityUnknown" };
  if (g.reject_if_freeze_authority && meta.freezeAuthorityActive === null) return { reject: true, reason: "freezeAuthorityUnknown" };
  if (meta.singleHolderPct === null) return { reject: true, reason: "holdersUnknown" };
  if (meta.top10HoldersPct === null) return { reject: true, reason: "holdersUnknown" };

  if (g.reject_if_mint_authority && meta.mintAuthorityActive) return { reject: true, reason: "mintAuthorityActive" };
  if (g.reject_if_freeze_authority && meta.freezeAuthorityActive) return { reject: true, reason: "freezeAuthorityActive" };

  if (meta.singleHolderPct > g.max_single_holder_pct) return { reject: true, reason: "singleHolderTooHigh" };
  if (meta.top10HoldersPct > g.max_top10_holders_pct) return { reject: true, reason: "top10TooHigh" };

  if (g.reject_if_tx_anomaly) {
    // simple anomaly proxy: high volume but too few tx
    const volPerTx = metrics.tx5m > 0 ? metrics.vol5mUsd / metrics.tx5m : metrics.vol5mUsd;
    if (metrics.tx5m < 10 && metrics.vol5mUsd > 10_000) return { reject: true, reason: "txAnomalyFewTxHighVol" };
    if (volPerTx > 5_000) return { reject: true, reason: "txAnomalyWhalePrints" };
  }

  return { reject: false };
}
