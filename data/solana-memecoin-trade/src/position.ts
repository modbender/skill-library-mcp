import { Position, PositionTag } from "./types.js";

export function computeSizeUsd(bankrollUsd: number, riskPerTradePct: number, stopLossPct: number): number {
  const riskUsd = bankrollUsd * (riskPerTradePct / 100);
  const sizeUsd = (riskUsd / stopLossPct) * 100;
  return Math.max(0, sizeUsd);
}

export function openPosition(opts: {
  mint: string;
  tag: PositionTag;
  entryPriceUsd: number;
  sizeUsd: number;
  exits: any;
  tokenAmountRaw?: string;
  tokenDecimals?: number;
}): Position {
  const { stop_loss_pct, tp1_pct, tp2_pct, trailing_stop_pct } = opts.exits;
  const stopLossUsd = opts.entryPriceUsd * (1 - stop_loss_pct / 100);
  const tp1Usd = opts.entryPriceUsd * (1 + tp1_pct / 100);
  const tp2Usd = opts.entryPriceUsd * (1 + tp2_pct / 100);

  return {
    mint: opts.mint,
    tag: opts.tag,
    entryPriceUsd: opts.entryPriceUsd,
    sizeUsd: opts.sizeUsd,
    openTs: Date.now(),
    stopLossUsd,
    tp1Usd,
    tp2Usd,
    trailingStopPct: trailing_stop_pct,
    remainingPct: 100,
    peakPriceUsd: opts.entryPriceUsd,
    tokenAmountRaw: opts.tokenAmountRaw,
    tokenDecimals: opts.tokenDecimals,
  };
}
