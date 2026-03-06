import { httpGetJson } from "./http.js";
import { WalletEvent } from "../types.js";
import { logger } from "../logger.js";

type EnhancedTx = any;

function heliusBase(): string {
  return process.env.HELIUS_BASE_URL || "https://api-mainnet.helius-rpc.com";
}
function heliusKey(): string {
  const k = process.env.HELIUS_API_KEY;
  if (!k) throw new Error("Missing HELIUS_API_KEY");
  return k;
}

function isIgnoredMint(mint: string, cfg: any): boolean {
  const ign: string[] = cfg.ignore_mints || [];
  return ign.includes(mint);
}

function pickSwapEvents(wallet: string, tx: EnhancedTx, cfg: any): WalletEvent[] {
  const out: WalletEvent[] = [];
  const ev = tx?.events?.swap;
  if (!ev) return out;

  // tokenInputs => wallet spent tokens (SELL of that mint)
  const tokenInputs = Array.isArray(ev.tokenInputs) ? ev.tokenInputs : [];
  for (const ti of tokenInputs) {
    if (ti?.userAccount === wallet && ti?.mint && !isIgnoredMint(ti.mint, cfg)) {
      out.push({ wallet, side: "SELL", mint: ti.mint, ts: (tx.timestamp ?? Math.floor(Date.now()/1000)) * 1000 });
    }
  }

  // tokenOutputs => wallet received tokens (BUY of that mint)
  const tokenOutputs = Array.isArray(ev.tokenOutputs) ? ev.tokenOutputs : [];
  for (const to of tokenOutputs) {
    if (to?.userAccount === wallet && to?.mint && !isIgnoredMint(to.mint, cfg)) {
      out.push({ wallet, side: "BUY", mint: to.mint, ts: (tx.timestamp ?? Math.floor(Date.now()/1000)) * 1000 });
    }
  }

  return out;
}

export async function pollWalletOnce(wallet: string, cfg: any, cursorAfterSig: string | null): Promise<{ events: WalletEvent[]; newestSig: string | null }> {
  const base = heliusBase();
  const key = heliusKey();
  const limit = 20;

  const qs = new URLSearchParams();
  qs.set("api-key", key);
  qs.set("limit", String(limit));
  qs.set("commitment", "confirmed");
  if (cursorAfterSig) qs.set("after-signature", cursorAfterSig);

  const url = `${base}/v0/addresses/${wallet}/transactions?${qs.toString()}`;
  const txs = await httpGetJson<EnhancedTx[]>(url);

  if (!Array.isArray(txs) || txs.length === 0) return { events: [], newestSig: cursorAfterSig };

  // API returns transactions in reverse chronological by default; we handle both just in case:
  const sigs = txs.map(t => t.signature).filter(Boolean);
  const newestSig = sigs[0] ?? cursorAfterSig;

  const events: WalletEvent[] = [];
  for (const tx of txs) {
    // ignore failed tx
    if (tx?.transactionError?.error) continue;
    for (const e of pickSwapEvents(wallet, tx, cfg)) events.push(e);
  }

  // De-duplicate per (side,mint,ts)
  const seen = new Set<string>();
  const dedup = events.filter(e => {
    const k2 = `${e.side}:${e.mint}:${e.ts}`;
    if (seen.has(k2)) return false;
    seen.add(k2);
    return true;
  });

  return { events: dedup, newestSig };
}

export function startHeliusPolling(wallets: string[], cfg: any, onEvent: (e: WalletEvent) => void): () => void {
  const pollMs = 2000;
  const cursors = new Map<string, string | null>();
  for (const w of wallets) cursors.set(w, null);

  logger.info({ wallets: wallets.length, pollMs }, "Helius polling: start");

  const timer = setInterval(async () => {
    for (const wallet of wallets) {
      try {
        const { events, newestSig } = await pollWalletOnce(wallet, cfg, cursors.get(wallet) ?? null);
        cursors.set(wallet, newestSig);
        for (const e of events) onEvent(e);
      } catch (err) {
        logger.warn({ wallet, err }, "Helius polling error");
      }
    }
  }, pollMs);

  return () => clearInterval(timer);
}
