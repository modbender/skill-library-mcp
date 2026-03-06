import { Position } from "./types.js";
import { resolveDexScreener } from "./providers/dexscreener.js";
import { logger } from "./logger.js";
import { sellSim, sellLiveExactIn } from "./providers/swapExecutor.js";

export type CloseResult = { closed: boolean; reason?: string; txid?: string; pctSold?: number };

function pctChange(a: number, b: number): number {
  if (!Number.isFinite(a) || a === 0) return 0;
  return ((b - a) / a) * 100;
}

export async function monitorPositions(
  positions: Map<string, Position>,
  cfg: any,
  mode: "paper" | "live",
  // For rug alarm deltas, we store last seen liquidity per mint
  liqSnapshot: Map<string, { liqUsd: number; ts: number }>
): Promise<Array<{ mint: string; reason: string }>> {
  const events: Array<{ mint: string; reason: string }> = [];
  const now = Date.now();

  for (const [mint, pos] of positions.entries()) {
    const m = await resolveDexScreener(mint);
    if (!m || !Number.isFinite(m.currentPriceUsd ?? NaN)) continue;

    const price = m.currentPriceUsd as number;

    // Update peak for trailing
    if (price > pos.peakPriceUsd) pos.peakPriceUsd = price;

    // Rug alarms: liquidity drop in window
    const prev = liqSnapshot.get(mint);
    liqSnapshot.set(mint, { liqUsd: m.liqUsd, ts: now });
    if (prev) {
      const ageMin = (now - prev.ts) / 60000;
      if (ageMin <= cfg.rug_alarms.lp_drop_window_min) {
        const dropPct = -pctChange(prev.liqUsd, m.liqUsd);
        if (dropPct >= cfg.rug_alarms.lp_drop_pct) {
          // Exit all
          if (mode === "paper") {
            await sellSim(mint, pos.remainingPct);
          } else {
            if (pos.tokenAmountRaw) {
              const amt = BigInt(pos.tokenAmountRaw);
              const sellAmt = (amt * BigInt(Math.round(pos.remainingPct))) / BigInt(100);
              await sellLiveExactIn({
                inputMint: mint,
                outputMint: "So11111111111111111111111111111111111111112",
                inAmountRaw: sellAmt.toString(),
                slippageBps: cfg.execution_live?.slippage_bps ?? 80,
                restrictIntermediateTokens: cfg.execution_live?.restrict_intermediate_tokens ?? true,
                onlyDirectRoutes: cfg.execution_live?.only_direct_routes ?? false,
              });
            } else {
              logger.warn({ mint }, "LIVE EXIT skipped: missing tokenAmountRaw");
            }
          }
          positions.delete(mint);
          events.push({ mint, reason: `RUG_ALARM_LP_DROP_${dropPct.toFixed(1)}%` });
          logger.warn({ mint, dropPct }, "RUG_ALARM: LP drop => EXIT ALL");
          continue;
        }
      }
    }

    // Stop loss
    if (price <= pos.stopLossUsd) {
      if (mode === "paper") {
        await sellSim(mint, pos.remainingPct);
      } else {
        if (pos.tokenAmountRaw) {
          const amt = BigInt(pos.tokenAmountRaw);
          const sellAmt = (amt * BigInt(Math.round(pos.remainingPct))) / BigInt(100);
          await sellLiveExactIn({
            inputMint: mint,
            outputMint: "So11111111111111111111111111111111111111112",
            inAmountRaw: sellAmt.toString(),
            slippageBps: cfg.execution_live?.slippage_bps ?? 80,
            restrictIntermediateTokens: cfg.execution_live?.restrict_intermediate_tokens ?? true,
            onlyDirectRoutes: cfg.execution_live?.only_direct_routes ?? false,
          });
        } else {
          logger.warn({ mint }, "LIVE EXIT skipped: missing tokenAmountRaw");
        }
      }
      positions.delete(mint);
      events.push({ mint, reason: "STOP_LOSS" });
      logger.info({ mint }, "STOP_LOSS => EXIT");
      continue;
    }

    // TP1 / TP2 partials
    if (pos.remainingPct > 0) {
      if (price >= pos.tp2Usd && pos.remainingPct > (100 - cfg.exits.tp1_sell_pct - cfg.exits.tp2_sell_pct)) {
        // sell TP2 chunk once
        const pct = cfg.exits.tp2_sell_pct;
        if (mode === "paper") await sellSim(mint, pct);
        pos.remainingPct = Math.max(0, pos.remainingPct - pct);
        events.push({ mint, reason: "TAKE_PROFIT_2" });
        logger.info({ mint, pct }, "TP2 partial sell");
      } else if (price >= pos.tp1Usd && pos.remainingPct === 100) {
        const pct = cfg.exits.tp1_sell_pct;
        if (mode === "paper") await sellSim(mint, pct);
        pos.remainingPct = Math.max(0, pos.remainingPct - pct);
        events.push({ mint, reason: "TAKE_PROFIT_1" });
        logger.info({ mint, pct }, "TP1 partial sell");
      }
    }

    // Trailing stop on remaining
    if (pos.remainingPct > 0) {
      const trailStop = pos.peakPriceUsd * (1 - pos.trailingStopPct / 100);
      if (price <= trailStop && pos.peakPriceUsd > pos.entryPriceUsd) {
        if (mode === "paper") await sellSim(mint, pos.remainingPct);
        positions.delete(mint);
        events.push({ mint, reason: "TRAILING_STOP" });
        logger.info({ mint }, "TRAILING_STOP => EXIT");
        continue;
      }
    }
  }

  return events;
}
