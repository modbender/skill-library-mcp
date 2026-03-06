import { logger } from "../logger.js";
import bs58 from "bs58";
import { Connection, Keypair, VersionedTransaction } from "@solana/web3.js";
import { buildSwapTx, getQuote, getSolUsdPrice, getPriceDecimals } from "./jupiter.js";
import { fetchMintInfo } from "./solanaRpc.js";

function getConnection(): Connection {
  const url = process.env.SOLANA_RPC_URL;
  if (!url) throw new Error("Missing SOLANA_RPC_URL");
  return new Connection(url, "confirmed");
}

function loadKeypair(): Keypair {
  const b58 = process.env.WALLET_PRIVATE_KEY_BASE58;
  const json = process.env.WALLET_PRIVATE_KEY_JSON;
  if (b58) return Keypair.fromSecretKey(bs58.decode(b58.trim()));
  if (json) return Keypair.fromSecretKey(Uint8Array.from(JSON.parse(json)));
  throw new Error("Missing WALLET_PRIVATE_KEY_BASE58 or WALLET_PRIVATE_KEY_JSON");
}

export async function buySim(mint: string, sizeUsd: number): Promise<{ ok: boolean; txid?: string; fillPriceUsd: number; outAmountRaw?: string }> {
  logger.info({ mint, sizeUsd }, "PAPER BUY");
  return { ok: true, txid: `paper-buy-${Date.now()}`, fillPriceUsd: NaN };
}

export async function sellSim(mint: string, pct: number): Promise<{ ok: boolean; txid?: string }> {
  logger.info({ mint, pct }, "PAPER SELL");
  return { ok: true, txid: `paper-sell-${Date.now()}` };
}

export async function buyLiveByUsd(params: {
  outputMint: string;
  usdAmount: number;
  slippageBps: number;
  restrictIntermediateTokens?: boolean;
  onlyDirectRoutes?: boolean;
}): Promise<{ ok: boolean; txid?: string; inAmountLamports?: string; outAmountRaw?: string; outDecimals?: number }> {
  const jupBase = process.env.JUP_BASE_URL || "https://api.jup.ag";
  const apiKey = process.env.JUP_API_KEY || undefined;

  const solUsd = await getSolUsdPrice(jupBase, apiKey);
  if (!solUsd) throw new Error("Could not fetch SOL USD price from Jupiter Price API");

  const lamports = Math.floor((params.usdAmount / solUsd) * 1e9);
  if (lamports <= 0) throw new Error("usdAmount too small to convert to lamports");

  const inputMint = "So11111111111111111111111111111111111111112"; // wSOL
  const quote = await getQuote({
    jupBase,
    apiKey,
    inputMint,
    outputMint: params.outputMint,
    amount: String(lamports),
    slippageBps: params.slippageBps,
    restrictIntermediateTokens: params.restrictIntermediateTokens ?? true,
    onlyDirectRoutes: params.onlyDirectRoutes ?? false,
  });

  const kp = loadKeypair();
  const user = kp.publicKey.toBase58();

  const priorityMax = Number(process.env.PRIORITY_MAX_LAMPORTS || "1000000");
  const priorityLevel = process.env.PRIORITY_LEVEL || "veryHigh";

  const swap = await buildSwapTx({
    jupBase,
    apiKey,
    quoteResponse: quote,
    userPublicKey: user,
    wrapAndUnwrapSol: true,
    dynamicComputeUnitLimit: true,
    dynamicSlippage: true,
    prioritizationFeeLamports: {
      priorityLevelWithMaxLamports: {
        maxLamports: priorityMax,
        priorityLevel,
      },
    },
  });

  const txB64 = swap.swapTransaction;
  if (!txB64) throw new Error("No swapTransaction returned by Jupiter");

  const tx = VersionedTransaction.deserialize(Buffer.from(txB64, "base64"));
  tx.sign([kp]);

  const c = getConnection();
  const sig = await c.sendRawTransaction(tx.serialize(), { skipPreflight: false, preflightCommitment: "confirmed" });
  logger.info({ sig }, "LIVE BUY sent");

  // confirm
  if (swap.lastValidBlockHeight) {
    const bh = tx.message.recentBlockhash;
    await c.confirmTransaction({ signature: sig, blockhash: bh, lastValidBlockHeight: swap.lastValidBlockHeight }, "confirmed");
  } else {
    await c.confirmTransaction(sig, "confirmed");
  }

  // decimals for output token (prefer RPC mint decimals)
  let outDecimals: number | undefined;
  try {
    outDecimals = (await fetchMintInfo(params.outputMint)).decimals;
  } catch {
    try {
      const d = await getPriceDecimals(jupBase, [params.outputMint], apiKey);
      outDecimals = d?.[params.outputMint]?.decimals;
    } catch {}
  }

  return { ok: true, txid: sig, inAmountLamports: String(lamports), outAmountRaw: quote.outAmount, outDecimals };
}

export async function sellLiveExactIn(params: {
  inputMint: string; // token to sell
  outputMint: string; // usually wSOL
  inAmountRaw: string;
  slippageBps: number;
  restrictIntermediateTokens?: boolean;
  onlyDirectRoutes?: boolean;
}): Promise<{ ok: boolean; txid?: string }> {
  const jupBase = process.env.JUP_BASE_URL || "https://api.jup.ag";
  const apiKey = process.env.JUP_API_KEY || undefined;

  const quote = await getQuote({
    jupBase,
    apiKey,
    inputMint: params.inputMint,
    outputMint: params.outputMint,
    amount: params.inAmountRaw,
    slippageBps: params.slippageBps,
    restrictIntermediateTokens: params.restrictIntermediateTokens ?? true,
    onlyDirectRoutes: params.onlyDirectRoutes ?? false,
  });

  const kp = loadKeypair();
  const user = kp.publicKey.toBase58();

  const priorityMax = Number(process.env.PRIORITY_MAX_LAMPORTS || "1000000");
  const priorityLevel = process.env.PRIORITY_LEVEL || "veryHigh";

  const swap = await buildSwapTx({
    jupBase,
    apiKey,
    quoteResponse: quote,
    userPublicKey: user,
    wrapAndUnwrapSol: true,
    dynamicComputeUnitLimit: true,
    dynamicSlippage: true,
    prioritizationFeeLamports: {
      priorityLevelWithMaxLamports: {
        maxLamports: priorityMax,
        priorityLevel,
      },
    },
  });

  const txB64 = swap.swapTransaction;
  if (!txB64) throw new Error("No swapTransaction returned by Jupiter");

  const tx = VersionedTransaction.deserialize(Buffer.from(txB64, "base64"));
  tx.sign([kp]);

  const c = getConnection();
  const sig = await c.sendRawTransaction(tx.serialize(), { skipPreflight: false, preflightCommitment: "confirmed" });
  logger.info({ sig }, "LIVE SELL sent");

  if (swap.lastValidBlockHeight) {
    const bh = tx.message.recentBlockhash;
    await c.confirmTransaction({ signature: sig, blockhash: bh, lastValidBlockHeight: swap.lastValidBlockHeight }, "confirmed");
  } else {
    await c.confirmTransaction(sig, "confirmed");
  }

  return { ok: true, txid: sig };
}
