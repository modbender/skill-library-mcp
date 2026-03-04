import {
  Connection,
  Keypair,
  PublicKey,
} from "@solana/web3.js";
import { unpackAccount } from "@solana/spl-token";
import bs58 from "bs58";
import { readTokenHistory, writeTokenHistory, readConfig, writeConfig, getKey } from "./config.mjs";

const RPC_URL = process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com";
const TOTAL_SUPPLY = 1_000_000_000;

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith("--")) {
      const key = argv[i].slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith("--")) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    }
  }
  return args;
}

async function getTokenStats(connection, wallet, token, sdk, pumpAmmSdk, globalState) {
  const mint = new PublicKey(token.mint);

  // Check graduation (always on-chain, never cached)
  const { canonicalPumpPoolPda } = await import("@pump-fun/pump-sdk");
  const poolAddress = canonicalPumpPoolPda(mint);
  const poolAccount = await connection.getAccountInfo(poolAddress);
  const isGraduated = poolAccount !== null;

  const result = {
    name: token.name,
    symbol: token.symbol,
    mint: token.mint,
    createdAt: token.createdAt,
    isGraduated,
  };

  if (isGraduated) {
    // Update pool address in history if not set
    if (!token.poolAddress) {
      token.poolAddress = poolAddress.toBase58();
    }

    try {
      const pool = await pumpAmmSdk.fetchPool(poolAddress);
      const [baseAccountInfo, quoteAccountInfo] = await connection.getMultipleAccountsInfo([
        pool.poolBaseTokenAccount,
        pool.poolQuoteTokenAccount,
      ]);

      if (baseAccountInfo && quoteAccountInfo) {
        const baseAccount = unpackAccount(pool.poolBaseTokenAccount, baseAccountInfo);
        const quoteAccount = unpackAccount(pool.poolQuoteTokenAccount, quoteAccountInfo);

        const baseReserves = Number(baseAccount.amount);
        const quoteReserves = Number(quoteAccount.amount);

        if (baseReserves > 0) {
          const priceInSol = quoteReserves / baseReserves;
          result.priceInSol = priceInSol;
          result.poolReserves = {
            base: baseReserves,
            quote: quoteReserves,
          };
          result.estimatedMcap = priceInSol * TOTAL_SUPPLY;
        }
      }
    } catch (err) {
      result.poolError = err.message;
    }

    result.status = "Graduated (PumpSwap AMM)";
  } else {
    try {
      const bondingCurve = await sdk.fetchBondingCurve(mint);
      const initialRealTokens = Number(globalState.initialRealTokenReserves);
      const currentRealTokens = Number(bondingCurve.realTokenReserves);
      const progressPercent = Math.min(100, Math.max(0, (1 - currentRealTokens / initialRealTokens) * 100));

      const virtualSolReserves = Number(bondingCurve.virtualSolReserves) / 1e9;
      const virtualTokenReserves = Number(bondingCurve.virtualTokenReserves);
      const tokenTotalSupply = Number(bondingCurve.tokenTotalSupply);

      result.bondingCurveProgress = Math.round(progressPercent * 100) / 100;
      result.virtualSolReserves = virtualSolReserves;
      result.estimatedMcap = virtualTokenReserves > 0
        ? (virtualSolReserves / virtualTokenReserves) * tokenTotalSupply
        : 0;
    } catch (err) {
      result.bondingCurveError = err.message;
    }

    result.status = `Bonding curve — ${result.bondingCurveProgress || 0}% graduated`;
  }

  // Per-token claimable fees (only for tokens with fee sharing)
  if (token.feeSharingConfigured) {
    try {
      const feeResult = await sdk.getMinimumDistributableFee(mint);
      result.claimableFees = Number(feeResult.distributableFees) / 1e9;
    } catch {
      result.claimableFees = 0;
    }
  }

  return result;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const isPortfolio = args.portfolio || false;
  const isDailyRecap = args["daily-recap"] || false;

  if (!isPortfolio && !isDailyRecap) {
    console.log(JSON.stringify({
      success: false,
      error: "Usage: --portfolio | --daily-recap"
    }));
    process.exit(1);
  }

  // For daily recap, check if 24h have passed since the last one
  if (isDailyRecap) {
    const config = await readConfig();
    const last = config.lastDailyRecap;
    if (last && Date.now() - new Date(last).getTime() < 24 * 60 * 60 * 1000) {
      console.log(JSON.stringify({ success: true, action: "daily_recap", due: false }));
      return;
    }
  }

  const privateKey = await getKey("SOLANA_PRIVATE_KEY");
  if (!privateKey) {
    console.log(JSON.stringify({ success: false, error: "SOLANA_PRIVATE_KEY not set. Run setup first." }));
    process.exit(1);
  }

  const wallet = Keypair.fromSecretKey(bs58.decode(privateKey));
  const connection = new Connection(RPC_URL, "confirmed");

  const history = await readTokenHistory();
  if (history.tokens.length === 0) {
    console.log(JSON.stringify({
      success: true,
      action: isDailyRecap ? "daily_recap" : "portfolio",
      tokens: [],
      message: "No tokens found."
    }));
    return;
  }

  const { OnlinePumpSdk } = await import("@pump-fun/pump-sdk");
  const { OnlinePumpAmmSdk } = await import("@pump-fun/pump-swap-sdk");
  const sdk = new OnlinePumpSdk(connection);
  const pumpAmmSdk = new OnlinePumpAmmSdk(connection);
  const globalState = await sdk.fetchGlobal();

  const tokenStats = [];
  for (const token of history.tokens) {
    const stats = await getTokenStats(connection, wallet, token, sdk, pumpAmmSdk, globalState);
    tokenStats.push(stats);
  }

  // Save updated history (pool addresses may have been updated)
  await writeTokenHistory(history);

  // Wallet balance and unclaimed fees
  const walletBalance = await connection.getBalance(wallet.publicKey);

  let totalUnclaimedFees = 0;

  // 1. Creator vault balance (fees from tokens WITHOUT fee sharing)
  try {
    const fees = await sdk.getCreatorVaultBalanceBothPrograms(wallet.publicKey);
    totalUnclaimedFees += Number(fees) / 1e9;
  } catch {
    // Creator vault may not exist yet if no fees have been earned
  }

  // 2. Per-token distributable fees (already fetched in getTokenStats)
  for (const stat of tokenStats) {
    if (stat.claimableFees) {
      totalUnclaimedFees += stat.claimableFees;
    }
  }

  // Record timestamp so the next daily recap won't fire for 24h
  if (isDailyRecap) {
    await writeConfig("lastDailyRecap", new Date().toISOString());
  }

  console.log(JSON.stringify({
    success: true,
    action: isDailyRecap ? "daily_recap" : "portfolio",
    date: new Date().toISOString().split("T")[0],
    walletAddress: wallet.publicKey.toBase58(),
    walletBalance: walletBalance / 1e9,
    totalUnclaimedFees,
    tokens: tokenStats,
  }));
}

main().catch((err) => {
  console.log(JSON.stringify({ success: false, error: err.message }));
  process.exit(1);
});
