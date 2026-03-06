import {
  Connection,
  Keypair,
  PublicKey,
  TransactionMessage,
  VersionedTransaction,
  ComputeBudgetProgram,
} from "@solana/web3.js";
import BN from "bn.js";
import bs58 from "bs58";
import { execFile } from "child_process";
import { randomBytes } from "crypto";
import { mkdir, readFile, readdir, unlink, rmdir } from "fs/promises";
import { tmpdir } from "os";
import { join } from "path";
import { readTokenHistory, writeTokenHistory, getKey } from "./config.mjs";

const SHIPMYTOKEN_WALLET = new PublicKey("7Z9vCDFzwe2DsTq4zvmrurScehUYAgUifiycgD6ZYa6T");
const RPC_URL = process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com";
const IPFS_ENDPOINT = "https://pump.fun/api/ipfs";
const MAX_RETRIES = 3;
const BASE58_CHARS = /^[1-9A-HJ-NP-Za-km-z]+$/;
const VANITY_TIMEOUT_MS = 120_000;
const MAX_VANITY_LEN = 5;

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

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function validateVanityPattern(prefix, suffix) {
  for (const [label, value] of [["Prefix", prefix], ["Suffix", suffix]]) {
    if (!value) continue;
    if (!BASE58_CHARS.test(value)) {
      return `${label} "${value}" contains invalid characters. Only Base58 characters are allowed (no 0, O, I, or l).`;
    }
    if (value.length > MAX_VANITY_LEN) {
      return `${label} is too long (${value.length} chars). Maximum is ${MAX_VANITY_LEN} characters.`;
    }
  }
  return null;
}

async function grindVanityKeypair(prefix, suffix, { ignoreCase = true } = {}) {
  const tempDir = join(tmpdir(), `smt-grind-${randomBytes(8).toString("hex")}`);
  await mkdir(tempDir, { recursive: true });

  try {
    const args = ["grind"];
    if (prefix && suffix) {
      args.push("--starts-and-ends-with", `${prefix}:${suffix}`);
    } else if (prefix) {
      args.push("--starts-with", prefix);
    } else {
      args.push("--ends-with", suffix);
    }
    if (ignoreCase) args.push("--ignore-case");

    const keypairBytes = await new Promise((resolve, reject) => {
      execFile("solana-keygen", args, { cwd: tempDir, timeout: VANITY_TIMEOUT_MS }, (error) => {
        if (error) {
          if (error.code === "ENOENT") {
            reject(new Error(
              "solana-keygen not found. Install the Solana CLI: https://docs.solanalabs.com/cli/install"
            ));
          } else if (error.killed) {
            reject(new Error(
              `Vanity address search timed out after ${VANITY_TIMEOUT_MS / 1000}s. Try a shorter prefix/suffix.`
            ));
          } else {
            reject(new Error(`Vanity grind failed: ${error.message}`));
          }
          return;
        }
        resolve(null);
      });
    }).then(async () => {
      const files = await readdir(tempDir);
      const jsonFile = files.find((f) => f.endsWith(".json"));
      if (!jsonFile) throw new Error("Vanity grind produced no keypair file.");
      const raw = await readFile(join(tempDir, jsonFile), "utf-8");
      return JSON.parse(raw);
    });

    return Keypair.fromSecretKey(Uint8Array.from(keypairBytes));
  } finally {
    try {
      const files = await readdir(tempDir);
      for (const f of files) await unlink(join(tempDir, f));
      await rmdir(tempDir);
    } catch {}
  }
}

async function uploadMetadata({ name, symbol, description, image, twitter, telegram, website }) {
  const { default: fetch } = await import("node-fetch").catch(() => ({ default: globalThis.fetch }));

  let imageBlob;
  if (image.startsWith("http://") || image.startsWith("https://")) {
    const resp = await globalThis.fetch(image);
    imageBlob = await resp.blob();
  } else {
    const { readFile } = await import("fs/promises");
    const buf = await readFile(image);
    const ext = image.split(".").pop().toLowerCase();
    const mimeTypes = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp" };
    imageBlob = new Blob([buf], { type: mimeTypes[ext] || "image/png" });
  }

  const form = new FormData();
  form.append("file", imageBlob, "token-image");
  form.append("name", name);
  form.append("symbol", symbol);
  if (description) form.append("description", description);
  if (twitter) form.append("twitter", twitter);
  if (telegram) form.append("telegram", telegram);
  if (website) form.append("website", website);
  form.append("showName", "true");

  let lastError;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const resp = await globalThis.fetch(IPFS_ENDPOINT, { method: "POST", body: form });
      if (!resp.ok) throw new Error(`IPFS upload failed: ${resp.status} ${resp.statusText}`);
      const data = await resp.json();
      return data.metadataUri;
    } catch (err) {
      lastError = err;
      if (attempt < MAX_RETRIES) await sleep(1000 * Math.pow(2, attempt - 1));
    }
  }
  throw new Error(`IPFS upload failed after ${MAX_RETRIES} attempts: ${lastError.message}`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.name || !args.symbol || !args.image) {
    console.log(JSON.stringify({
      success: false,
      error: "Missing required args. Usage: --name <name> --symbol <symbol> --image <path|url> [--description <desc>] [--twitter <url>] [--telegram <url>] [--website <url>] [--initial-buy <sol_amount>] [--vanity-prefix <prefix>] [--vanity-suffix <suffix>]"
    }));
    process.exit(1);
  }

  const privateKey = await getKey("SOLANA_PRIVATE_KEY");
  if (!privateKey) {
    console.log(JSON.stringify({ success: false, error: "SOLANA_PRIVATE_KEY not set. Run setup first." }));
    process.exit(1);
  }

  const wallet = Keypair.fromSecretKey(bs58.decode(privateKey));
  const connection = new Connection(RPC_URL, "confirmed");

  // Generate or grind mint keypair (before IPFS upload so we don't waste resources on failure)
  let mintKeypair;
  const vanityPrefix = typeof args["vanity-prefix"] === "string" ? args["vanity-prefix"] : null;
  const vanitySuffix = typeof args["vanity-suffix"] === "string" ? args["vanity-suffix"] : null;

  if (vanityPrefix || vanitySuffix) {
    const err = validateVanityPattern(vanityPrefix, vanitySuffix);
    if (err) {
      console.log(JSON.stringify({ success: false, error: err }));
      process.exit(1);
    }
    mintKeypair = await grindVanityKeypair(vanityPrefix, vanitySuffix);
  } else if (args["skip-pump-suffix"]) {
    mintKeypair = Keypair.generate();
  } else {
    // Default: grind for "pump" suffix to match pump.fun native addresses
    try {
      mintKeypair = await grindVanityKeypair(null, "pump", { ignoreCase: false });
    } catch {
      // solana-keygen not available or timed out — fall back to random keypair
      mintKeypair = Keypair.generate();
    }
  }

  // Check balance (network fees + optional initial buy)
  const initialBuyAmount = parseFloat(args["initial-buy"] || "0");
  const requiredLamports = 20_000_000 + Math.floor(Math.max(0, initialBuyAmount) * 1e9);
  const balance = await connection.getBalance(wallet.publicKey);
  if (balance < requiredLamports) {
    const required = requiredLamports / 1e9;
    const have = balance / 1e9;
    const breakdown = initialBuyAmount > 0
      ? `~0.02 SOL for network fees + ${initialBuyAmount} SOL for initial buy`
      : `~0.02 SOL for network fees`;
    console.log(JSON.stringify({
      success: false,
      error: `Insufficient SOL balance. Have ${have} SOL, need at least ~${required} SOL (${breakdown}).`,
      publicKey: wallet.publicKey.toBase58()
    }));
    process.exit(1);
  }

  // Upload metadata to IPFS
  const metadataUri = await uploadMetadata({
    name: args.name,
    symbol: args.symbol,
    description: args.description || "",
    image: args.image,
    twitter: args.twitter || "",
    telegram: args.telegram || "",
    website: args.website || "",
  });

  // Import pump SDK
  const { PumpSdk, OnlinePumpSdk } = await import("@pump-fun/pump-sdk");
  const sdk = new PumpSdk();
  const onlineSdk = new OnlinePumpSdk(connection);

  let instructions;
  if (initialBuyAmount > 0) {
    const { getBuyTokenAmountFromSolAmount, newBondingCurve } = await import("@pump-fun/pump-sdk");
    const global = await onlineSdk.fetchGlobal();
    const feeConfig = await onlineSdk.fetchFeeConfig();
    const solAmountBN = new BN(Math.floor(initialBuyAmount * 1e9));
    const bondingCurve = newBondingCurve(global);
    const tokenAmount = getBuyTokenAmountFromSolAmount({
      global,
      feeConfig,
      mintSupply: null,
      bondingCurve,
      amount: solAmountBN,
    });
    const result = await sdk.createV2AndBuyInstructions({
      global,
      creator: wallet.publicKey,
      mint: mintKeypair.publicKey,
      name: args.name,
      symbol: args.symbol,
      uri: metadataUri,
      user: wallet.publicKey,
      mayhemMode: false,
      amount: tokenAmount,
      solAmount: solAmountBN,
    });
    instructions = Array.isArray(result) ? result : [result];
  } else {
    const ix = await sdk.createV2Instruction({
      creator: wallet.publicKey,
      mint: mintKeypair.publicKey,
      name: args.name,
      symbol: args.symbol,
      uri: metadataUri,
      user: wallet.publicKey,
      mayhemMode: false,
    });
    instructions = Array.isArray(ix) ? ix : [ix];
  }

  // Add priority fee
  instructions.unshift(
    ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100_000 })
  );

  // Build versioned transaction
  const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash("confirmed");
  const message = new TransactionMessage({
    payerKey: wallet.publicKey,
    recentBlockhash: blockhash,
    instructions,
  }).compileToV0Message();

  const tx = new VersionedTransaction(message);
  tx.sign([wallet, mintKeypair]);

  // Send and confirm
  const signature = await connection.sendTransaction(tx, { skipPreflight: false });
  await connection.confirmTransaction(
    { signature, blockhash, lastValidBlockHeight },
    "confirmed"
  );

  // Configure fee sharing
  let feeSharingConfigured = false;
  try {
    const feeConfigIx = await sdk.createFeeSharingConfig({
      creator: wallet.publicKey,
      mint: mintKeypair.publicKey,
      pool: null,
    });
    const updateSharesIx = await sdk.updateFeeShares({
      authority: wallet.publicKey,
      mint: mintKeypair.publicKey,
      currentShareholders: [wallet.publicKey],
      newShareholders: [
        { address: wallet.publicKey, shareBps: 9000 },
        { address: SHIPMYTOKEN_WALLET, shareBps: 1000 },
      ],
    });

    const feeInstructions = [
      ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100_000 }),
      ...(Array.isArray(feeConfigIx) ? feeConfigIx : [feeConfigIx]),
      ...(Array.isArray(updateSharesIx) ? updateSharesIx : [updateSharesIx]),
    ];

    const { blockhash: feeBlockhash, lastValidBlockHeight: feeBlockHeight } =
      await connection.getLatestBlockhash("confirmed");
    const feeMessage = new TransactionMessage({
      payerKey: wallet.publicKey,
      recentBlockhash: feeBlockhash,
      instructions: feeInstructions,
    }).compileToV0Message();

    const feeTx = new VersionedTransaction(feeMessage);
    feeTx.sign([wallet]);

    const feeSig = await connection.sendTransaction(feeTx, { skipPreflight: false });
    await connection.confirmTransaction(
      { signature: feeSig, blockhash: feeBlockhash, lastValidBlockHeight: feeBlockHeight },
      "confirmed"
    );
    feeSharingConfigured = true;
  } catch (err) {
    console.error(`Fee sharing config failed (will retry next interaction): ${err.message}`);
  }

  // Save token to history
  const history = await readTokenHistory();
  const tokenEntry = {
    name: args.name,
    symbol: args.symbol,
    mint: mintKeypair.publicKey.toBase58(),
    createdAt: new Date().toISOString(),
    poolAddress: null,
    feeSharingConfigured,
    shareholders: feeSharingConfigured
      ? [
          { address: wallet.publicKey.toBase58(), shareBps: 9000, label: "creator" },
          { address: SHIPMYTOKEN_WALLET.toBase58(), shareBps: 1000, label: "shipmytoken" },
        ]
      : [],
  };
  history.tokens.push(tokenEntry);
  await writeTokenHistory(history);

  console.log(JSON.stringify({
    success: true,
    token: {
      name: args.name,
      symbol: args.symbol,
      mint: mintKeypair.publicKey.toBase58(),
      url: `https://pump.fun/coin/${mintKeypair.publicKey.toBase58()}`,
      feeSharingConfigured,
      signature,
    },
  }));
}

main().catch((err) => {
  console.log(JSON.stringify({ success: false, error: err.message }));
  process.exit(1);
});
