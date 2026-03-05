import { WalletEvent } from "../types.js";
import { logger } from "../logger.js";
import fs from "node:fs";
import { startHeliusPolling } from "./heliusWalletPoller.js";
import { loadConfig } from "../config.js";

/**
 * Wallet event provider.
 * Priority:
 * 1) MOCK_WALLET_EVENTS_JSONL (paper testing)
 * 2) Helius Enhanced Transactions polling (requires HELIUS_API_KEY)
 * 3) stub no-op
 */
export function startWalletStream(wallets: string[], onEvent: (e: WalletEvent) => void): () => void {
  const cfg = loadConfig();
  const jsonl = process.env.MOCK_WALLET_EVENTS_JSONL;
  const heliusKey = process.env.HELIUS_API_KEY;

  logger.info({ wallets: wallets.length, jsonl: !!jsonl, helius: !!heliusKey }, "walletStream: start");

  if (jsonl && fs.existsSync(jsonl)) {
    let offset = 0;
    const lines = fs.readFileSync(jsonl, "utf-8").split(/\r?\n/).filter(Boolean);
    const timer = setInterval(() => {
      if (offset >= lines.length) return;
      try {
        const e = JSON.parse(lines[offset++]) as WalletEvent;
        if (!wallets.includes(e.wallet)) return;
        onEvent(e);
      } catch (err) {
        logger.warn({ err }, "walletStream: bad JSONL line");
      }
    }, 1500);
    return () => clearInterval(timer);
  }

  if (heliusKey) {
    return startHeliusPolling(wallets, cfg, onEvent);
  }

  const timer = setInterval(() => {}, 10_000);
  return () => clearInterval(timer);
}
