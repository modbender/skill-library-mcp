import { Connection, PublicKey } from "@solana/web3.js";
import { TokenMeta } from "../types.js";
import { logger } from "../logger.js";

function conn(): Connection {
  const url = process.env.SOLANA_RPC_URL;
  if (!url) throw new Error("Missing SOLANA_RPC_URL");
  return new Connection(url, "confirmed");
}

export async function fetchMintInfo(mint: string): Promise<{ decimals: number; mintAuthorityActive: boolean; freezeAuthorityActive: boolean }> {
  const c = conn();
  const pk = new PublicKey(mint);
  const info = await c.getParsedAccountInfo(pk, "confirmed");
  const val: any = info.value;
  const parsed = val?.data?.parsed;
  const decimals = parsed?.info?.decimals;
  const mintAuth = parsed?.info?.mintAuthority;
  const freezeAuth = parsed?.info?.freezeAuthority;

  if (typeof decimals !== "number") throw new Error("Unable to parse mint decimals");
  return {
    decimals,
    mintAuthorityActive: !!mintAuth,
    freezeAuthorityActive: !!freezeAuth,
  };
}

export async function fetchHolderConcentration(mint: string): Promise<{ singleHolderPct: number; top10HoldersPct: number }> {
  const c = conn();
  const mintPk = new PublicKey(mint);

  const supply = await c.getTokenSupply(mintPk, "confirmed");
  const supplyUi = supply.value.uiAmount ?? 0;
  if (!Number.isFinite(supplyUi) || supplyUi <= 0) return { singleHolderPct: 0, top10HoldersPct: 0 };

  const largest = await c.getTokenLargestAccounts(mintPk, "confirmed");
  const vals = largest.value || [];
  const uiAmounts = vals.map(v => v.uiAmount ?? 0).filter(x => Number.isFinite(x) && x > 0);

  const top1 = uiAmounts[0] ?? 0;
  const top10 = uiAmounts.slice(0, 10).reduce((a, b) => a + b, 0);

  return {
    singleHolderPct: (top1 / supplyUi) * 100,
    top10HoldersPct: (top10 / supplyUi) * 100,
  };
}

/**
 * Fetch authority flags + holder concentration.
 * Safe default: if any RPC call fails, we return nulls and RiskGate will SKIP.
 */
export async function fetchTokenMeta(mint: string): Promise<TokenMeta> {
  try {
    const mi = await fetchMintInfo(mint);
    const hc = await fetchHolderConcentration(mint);
    return {
      mint,
      mintAuthorityActive: mi.mintAuthorityActive,
      freezeAuthorityActive: mi.freezeAuthorityActive,
      singleHolderPct: hc.singleHolderPct,
      top10HoldersPct: hc.top10HoldersPct,
    };
  } catch (err) {
    logger.warn({ mint, err }, "solanaRpc: meta fetch failed (safe SKIP)");
    return {
      mint,
      mintAuthorityActive: null,
      freezeAuthorityActive: null,
      singleHolderPct: null,
      top10HoldersPct: null,
    };
  }
}
