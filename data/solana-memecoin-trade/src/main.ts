import minimist from "minimist";
import { loadConfig, loadSmartWallets } from "./config.js";
import { logger } from "./logger.js";
import { fetchPumpfunCandidates } from "./providers/pumpfun.js";
import { resolveDexScreener } from "./providers/dexscreener.js";
import { fetchTokenMeta } from "./providers/solanaRpc.js";
import { startWalletStream } from "./providers/walletStream.js";
import { riskGate } from "./riskGate.js";
import { aiSignal, riskScore } from "./scoring.js";
import { computeSizeUsd, openPosition } from "./position.js";
import { buySim, sellSim, buyLiveByUsd, sellLiveExactIn } from "./providers/swapExecutor.js";
import { halted } from "./vaultRules.js";
import { engineHalted } from "./budget.js";
import { monitorPositions } from "./monitor.js";
import { NarrativeTracker, loadNarratives } from "./narrative.js";
import { startXFilteredStream, xAddRules } from "./providers/xFilteredStream.js";
import type { Mode, Position, WalletEvent } from "./types.js";

function sleep(ms: number) { return new Promise(res => setTimeout(res, ms)); }
function randInt(min: number, max: number) { return Math.floor(Math.random() * (max - min + 1)) + min; }

function priceChaseTooHigh(ref: number | undefined, now: number | undefined, maxPct: number): boolean {
  if (!ref || !now || !Number.isFinite(ref) || !Number.isFinite(now)) return false;
  const pct = ((now - ref) / ref) * 100;
  return pct > maxPct;
}

async function run() {
  const args = minimist(process.argv.slice(2));
  const mode = (args.mode || "paper") as Mode;
  const minutes = Number(args.minutes || 10);
  const cfg = loadConfig();
  const sw = loadSmartWallets();

  const narrativesCfg = loadNarratives();
  const narrativeTracker = new NarrativeTracker(cfg, narrativesCfg.narratives || []);

  let stopX: null | (() => void) = null;
  if (cfg.narrative?.enabled && cfg.narrative?.x_stream?.enabled && process.env.X_BEARER_TOKEN) {
    const ruleValues: Array<{ value: string; tag?: string }> = [];
    if (cfg.narrative.x_stream.rules_from_config) {
      for (const n of (narrativesCfg.narratives || [])) {
        for (const r of (n.x_rules || [])) ruleValues.push({ value: r, tag: n.id });
      }
    }
    for (const r of (cfg.narrative.x_stream.extra_rules || [])) ruleValues.push({ value: r, tag: "extra" });
    try { await xAddRules(ruleValues); } catch (err) { logger.warn({ err }, "X: add rules failed (continue)"); }

    stopX = startXFilteredStream({
      onEvent: (e) => narrativeTracker.ingestX(e),
      reconnectMinSeconds: cfg.narrative.x_stream.reconnect_min_seconds ?? 5,
      reconnectMaxSeconds: cfg.narrative.x_stream.reconnect_max_seconds ?? 60,
    });
  }


  logger.info({ mode, minutes }, "Starting Solana Memecoin Guardian v2 (COPY + AI + MONITOR)");

  const state = {
    dailyPnlPct: 0,
    tradesToday: 0,
    openPositions: new Map<string, Position>(),
    // separate engine PnL budgets (paper mode tracks realized as 0 in this skeleton)
    budgets: { pnlCopyPct: 0, pnlAiPct: 0 },
    // track wallet buy frequency per hour
    walletBuyTimestamps: new Map<string, number[]>(),
    // liquidity snapshots for rug alarms
    liqSnapshot: new Map<string, { liqUsd: number; ts: number }>(),
  };

  // COPY-TRADE handler
  const onWalletEvent = async (e: WalletEvent) => {
    if (!cfg.engines?.copy_trade) return;
    if (!cfg.smart_wallets.enabled) return;

    const hBudget = engineHalted("COPY", state.budgets, cfg);
    if (hBudget.stop) {
      logger.warn({ reason: hBudget.reason }, "COPY engine halted by budget");
      return;
    }

    // Global vault rules also apply
    const h = halted({ dailyPnlPct: state.dailyPnlPct, tradesToday: state.tradesToday, openPositions: state.openPositions.size }, cfg);
    if (h.stop) return;

    if (e.side === "SELL") {
      const pos = state.openPositions.get(e.mint);
      if (!pos) return;

      if (mode === "paper") {
        await sellSim(e.mint, pos.remainingPct);
      } else {
        if (!pos.tokenAmountRaw) {
          logger.warn({ mint: e.mint }, "LIVE SELL skipped: missing tokenAmountRaw");
        } else {
          const amt = BigInt(pos.tokenAmountRaw);
          const sellAmt = (amt * BigInt(Math.round(pos.remainingPct))) / BigInt(100);
          await sellLiveExactIn({
            inputMint: e.mint,
            outputMint: "So11111111111111111111111111111111111111112",
            inAmountRaw: sellAmt.toString(),
            slippageBps: cfg.execution_live?.slippage_bps ?? 80,
            restrictIntermediateTokens: cfg.execution_live?.restrict_intermediate_tokens ?? true,
            onlyDirectRoutes: cfg.execution_live?.only_direct_routes ?? false,
          });
        }
      }
      state.openPositions.delete(e.mint);
      logger.info({ mint: e.mint, wallet: e.wallet }, "COPY: wallet SOLD -> EXIT position");
      return;
    }

    if (e.side !== "BUY") return;
    if (state.openPositions.has(e.mint)) return;
    if (state.openPositions.size >= cfg.portfolio.max_open_positions) return;

    // Enforce max wallet buys/hour (anti spray)
    const arr = state.walletBuyTimestamps.get(e.wallet) ?? [];
    const cutoff = Date.now() - 60 * 60 * 1000;
    const filtered = arr.filter(ts => ts >= cutoff);
    filtered.push(Date.now());
    state.walletBuyTimestamps.set(e.wallet, filtered);
    if (filtered.length > cfg.copy_trade_rules.max_wallet_buys_per_hour) {
      logger.info({ wallet: e.wallet, n: filtered.length }, "COPY: wallet buying too frequently -> SKIP");
      return;
    }

    // Delay
    const delay = randInt(cfg.smart_wallets.copy_delay_sec_min, cfg.smart_wallets.copy_delay_sec_max) * 1000;
    await sleep(delay);

    const m = await resolveDexScreener(e.mint);
    if (!m) return;

    // anti chase
    if (priceChaseTooHigh(e.priceRefUsd, m.currentPriceUsd, cfg.smart_wallets.max_price_chase_pct)) {
      logger.info({ mint: e.mint }, "COPY: price chased too high -> SKIP");
      return;
    }

    // extra copy filters: age & tx count
    if (m.pairAgeMin < cfg.copy_trade_rules.min_age_min) {
      logger.info({ mint: e.mint, ageMin: m.pairAgeMin }, "COPY: token too new -> SKIP");
      return;
    }
    if (m.tx5m < cfg.copy_trade_rules.require_trade_count_5m) {
      logger.info({ mint: e.mint, tx5m: m.tx5m }, "COPY: tx5m too low -> SKIP");
      return;
    }

    const meta = await fetchTokenMeta(e.mint);
    const gate = riskGate(m, meta, cfg);
    if (gate.reject) {
      logger.info({ mint: e.mint, reason: gate.reason }, "COPY: RiskGate reject -> SKIP");
      return;
    }

    // size for COPY engine
    const bankroll = cfg.portfolio.bankroll_usd as number;
    const riskPct = cfg.portfolio.risk_per_trade_pct_copy as number;
    const sizeUsdRaw = computeSizeUsd(bankroll, riskPct, cfg.exits.stop_loss_pct);
    const cap = (cfg.portfolio.max_position_liquidity_pct / 100) * m.liqUsd;
    const sizeUsd = Math.min(sizeUsdRaw, cap);

    if (sizeUsd <= 5) {
      logger.info({ mint: e.mint, sizeUsd }, "COPY: size too small -> SKIP");
      return;
    }

    const entryPrice = m.currentPriceUsd ?? NaN;
    if (!Number.isFinite(entryPrice)) {
      logger.info({ mint: e.mint }, "COPY: missing price -> SKIP");
      return;
    }

    if (mode === "paper") {
      await buySim(e.mint, sizeUsd);
    } else {
      logger.warn("LIVE mode not implemented yet. Wire swap executor.");
      return;
    }

    const pos = openPosition({ mint: e.mint, tag: "COPY", entryPriceUsd: entryPrice, sizeUsd, exits: cfg.exits });
    state.openPositions.set(e.mint, pos);
    state.tradesToday += 1;
    logger.info({ mint: e.mint, sizeUsd, entryPrice, wallet: e.wallet }, "COPY: OPEN_POSITION");
  };

  // Start wallet stream (can be fed by MOCK_WALLET_EVENTS_JSONL in paper mode)
  const stopWallet = startWalletStream(sw.wallets.map(w => w.address), onWalletEvent);

  const t0 = Date.now();
  while ((Date.now() - t0) < minutes * 60_000) {
    const h = halted({ dailyPnlPct: state.dailyPnlPct, tradesToday: state.tradesToday, openPositions: state.openPositions.size }, cfg);
    if (h.stop) {
      logger.warn({ reason: h.reason }, "HALT");
      break;
    }

    // MONITOR positions (exits + rug alarms)
    await monitorPositions(state.openPositions, cfg, mode, state.liqSnapshot);

    // AI discovery loop
    if (cfg.engines?.ai_trade) {
      const hAi = engineHalted("AI", state.budgets, cfg);
      if (!hAi.stop) {
        const candidates = await fetchPumpfunCandidates(); // stub by default
        const hot = narrativeTracker.getHotMints();
        for (const hm of hot) {
          candidates.unshift({ mint: hm.mint, sourceTags: ["narrative"] });
        }
        for (const c of candidates.slice(0, 50)) {
          const h2 = halted({ dailyPnlPct: state.dailyPnlPct, tradesToday: state.tradesToday, openPositions: state.openPositions.size }, cfg);
          if (h2.stop) break;
          if (state.openPositions.has(c.mint)) continue;

          const m = await resolveDexScreener(c.mint);
          if (!m) continue;

          const meta = await fetchTokenMeta(c.mint);
          const gate = riskGate(m, meta, cfg);
          if (gate.reject) continue;

          const rs = riskScore(m, meta);
          if (rs > cfg.ai_signal.riskScore_threshold) continue;

          const sig = aiSignal(m, cfg);
          if (!sig.buy) continue;

          const entryPrice = m.currentPriceUsd ?? NaN;
          if (!Number.isFinite(entryPrice)) continue;

          const bankroll = cfg.portfolio.bankroll_usd as number;
          const riskPct = cfg.portfolio.risk_per_trade_pct_ai as number;
          const sizeUsdRaw = computeSizeUsd(bankroll, riskPct, cfg.exits.stop_loss_pct);
          const cap = (cfg.portfolio.max_position_liquidity_pct / 100) * m.liqUsd;
          const sizeUsd = Math.min(sizeUsdRaw, cap);

          if (sizeUsd <= 5) continue;

          if (mode === "paper") {
            await buySim(c.mint, sizeUsd);
            const pos = openPosition({ mint: c.mint, tag: "AI", entryPriceUsd: entryPrice, sizeUsd, exits: cfg.exits });
            state.openPositions.set(c.mint, pos);
          } else {
            const live = await buyLiveByUsd({
              outputMint: c.mint,
              usdAmount: sizeUsd,
              slippageBps: cfg.execution_live?.slippage_bps ?? 80,
              restrictIntermediateTokens: cfg.execution_live?.restrict_intermediate_tokens ?? true,
              onlyDirectRoutes: cfg.execution_live?.only_direct_routes ?? false,
            });
            const pos = openPosition({
              mint: c.mint,
              tag: "AI",
              entryPriceUsd: entryPrice,
              sizeUsd,
              exits: cfg.exits,
              tokenAmountRaw: live.outAmountRaw,
              tokenDecimals: live.outDecimals,
            });
            state.openPositions.set(c.mint, pos);
          }

          state.tradesToday += 1;
          logger.info({ mint: c.mint, sizeUsd, entryPrice }, "AI: OPEN_POSITION");
          state.openPositions.set(c.mint, pos);
          state.tradesToday += 1;
          logger.info({ mint: c.mint, sizeUsd, entryPrice }, "AI: OPEN_POSITION");
        }
      } else {
        logger.warn({ reason: hAi.reason }, "AI engine halted by budget");
      }
    }

    await sleep((cfg.monitor?.poll_seconds ?? 10) * 1000);
  }

  stopWallet();
  if (stopX) stopX();
  logger.info("Done.");
}

run().catch(err => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});
