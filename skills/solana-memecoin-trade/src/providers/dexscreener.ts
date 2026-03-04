import { httpGetJson } from "./http.js";
import { DexMetrics } from "../types.js";

/**
 * DexScreener public API.
 * We resolve by token mint address for Solana pairs.
 */
type DsTokenPairs = {
  pairs?: Array<{
    chainId: string;
    pairAddress: string;
    liquidity?: { usd?: number };
    volume?: { m5?: number };
    txns?: { m5?: { buys?: number; sells?: number } };
    priceChange?: { m5?: number };
    pairCreatedAt?: number;
    priceUsd?: string;
  }>;
};

export async function resolveDexScreener(mint: string): Promise<DexMetrics | null> {
  const url = `https://api.dexscreener.com/latest/dex/tokens/${mint}`;
  const data = await httpGetJson<DsTokenPairs>(url);
  const pair = (data.pairs || []).find(p => (p.chainId || "").toLowerCase() === "solana");
  if (!pair) return null;

  const liqUsd = pair.liquidity?.usd ?? 0;
  const vol5mUsd = pair.volume?.m5 ?? 0;
  const buys = pair.txns?.m5?.buys ?? 0;
  const sells = pair.txns?.m5?.sells ?? 0;
  const tx5m = buys + sells;
  const priceChange5mPct = pair.priceChange?.m5 ?? 0;
  const createdAt = pair.pairCreatedAt ? Math.floor((Date.now() - pair.pairCreatedAt) / 60000) : 0;
  const currentPriceUsd = pair.priceUsd ? Number(pair.priceUsd) : undefined;

  return {
    mint,
    pairAddress: pair.pairAddress,
    liqUsd,
    vol5mUsd,
    tx5m,
    priceChange5mPct,
    pairAgeMin: createdAt,
    currentPriceUsd,
  };
}
