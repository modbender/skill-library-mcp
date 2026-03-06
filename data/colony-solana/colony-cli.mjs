#!/usr/bin/env node

/**
 * Colony Game CLI — self-contained Node.js tool for OpenClaw agents.
 * All output is JSON. Reads SOLANA_PRIVATE_KEY and SOLANA_RPC_URL from env.
 *
 * Usage: node colony-cli.mjs <command> [options]
 *
 * Commands:
 *   status                   Full wallet + game overview
 *   game-state               Global game state
 *   buy-land --land-id <id>  Buy a land plot (burns 10k $OLO)
 *   find-land [--count N]    Find N available (unowned) land IDs
 *   upgrade-land --land-id <id>  Upgrade land to next level
 *   claim --land-id <id>     Claim earnings from one land
 *   claim-all                Claim earnings from all owned lands
 *   land-info --land-id <id> Detailed land info with ROI analysis
 *   swap-quote --sol-amount <amt>  Jupiter swap quote (SOL -> $OLO)
 *   swap --sol-amount <amt>  Execute Jupiter swap (SOL -> $OLO)
 *   recommend                AI-friendly next-best-action recommendation
 *   price                    Get $OLO token price via Jupiter
 *   generate-wallet          Generate a new Solana keypair for the bot
 */

import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import {
  Connection,
  PublicKey,
  Keypair,
  SystemProgram,
  Transaction,
  ComputeBudgetProgram,
  VersionedTransaction,
} from "@solana/web3.js";
import {
  getAssociatedTokenAddressSync,
  TOKEN_2022_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
} from "@solana/spl-token";
import pkg from "@coral-xyz/anchor";
const { Program, AnchorProvider, BN, Wallet } = pkg;
import bs58 from "bs58";

// ============================================================================
// CONSTANTS
// ============================================================================

const PROGRAM_ID = "BCVGJ5YoKMftBrt5fgDYhtvY7HVBccFofFiGqJtoRjqE";
const GAME_TOKEN_MINT = "2pXjxbdHnYWtH2gtDN495Ve1jm8bs1zoUL6XsUi3pump";
const SOL_MINT = "So11111111111111111111111111111111111111112";

const MAX_LAND_ID = 21000;
const MIN_LAND_ID = 1;
const MAX_LEVEL = 10;
const MAX_LANDS_PER_USER = 10;
const TOKEN_DECIMALS = 6;
const TOKEN_MULTIPLIER = 1_000_000;
const LAND_PRICE_TOKENS = 10_000 * TOKEN_MULTIPLIER;
const SECONDS_PER_DAY = 86400;
const MINING_START_TIME = 1771340400;
const MAX_CLAIMS_PER_TX = 10;

const UPGRADE_COSTS = [
  1_000 * TOKEN_MULTIPLIER,
  2_000 * TOKEN_MULTIPLIER,
  4_000 * TOKEN_MULTIPLIER,
  8_000 * TOKEN_MULTIPLIER,
  16_000 * TOKEN_MULTIPLIER,
  32_000 * TOKEN_MULTIPLIER,
  64_000 * TOKEN_MULTIPLIER,
  128_000 * TOKEN_MULTIPLIER,
  152_000 * TOKEN_MULTIPLIER,
];

const EARNING_SPEEDS = [
  1_000 * TOKEN_MULTIPLIER,
  2_000 * TOKEN_MULTIPLIER,
  3_000 * TOKEN_MULTIPLIER,
  5_000 * TOKEN_MULTIPLIER,
  8_000 * TOKEN_MULTIPLIER,
  13_000 * TOKEN_MULTIPLIER,
  21_000 * TOKEN_MULTIPLIER,
  34_000 * TOKEN_MULTIPLIER,
  45_000 * TOKEN_MULTIPLIER,
  79_000 * TOKEN_MULTIPLIER,
];

// ============================================================================
// SETUP
// ============================================================================

function out(data) {
  console.log(JSON.stringify(data, null, 2));
}

function fail(message, details) {
  out({ ok: false, error: message, ...(details && { details }) });
  process.exit(1);
}

function tokensToDisplay(raw) {
  if (typeof raw === "number") return raw / TOKEN_MULTIPLIER;
  if (BN.isBN(raw)) return raw.toNumber() / TOKEN_MULTIPLIER;
  return Number(raw) / TOKEN_MULTIPLIER;
}

function lamportsToSol(lamports) {
  return lamports / 1_000_000_000;
}

// Load env
const SOLANA_PRIVATE_KEY = process.env.SOLANA_PRIVATE_KEY;
const SOLANA_RPC_URL = process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com";
const JUPITER_API_KEY = process.env.JUPITER_API_KEY || "";

function requireKeypair() {
  if (!SOLANA_PRIVATE_KEY) {
    fail("SOLANA_PRIVATE_KEY env var is required");
  }
  try {
    return Keypair.fromSecretKey(bs58.decode(SOLANA_PRIVATE_KEY));
  } catch {
    fail("Invalid SOLANA_PRIVATE_KEY — must be base58-encoded secret key");
  }
}

// Load IDL
const __dirname = dirname(fileURLToPath(import.meta.url));
const idl = JSON.parse(readFileSync(join(__dirname, "idl.json"), "utf8"));

// ============================================================================
// PDA DERIVATION
// ============================================================================

const encoder = new TextEncoder();
const programId = new PublicKey(PROGRAM_ID);

function u16ToLeBytes(value) {
  const bytes = new Uint8Array(2);
  bytes[0] = value & 0xff;
  bytes[1] = (value >> 8) & 0xff;
  return bytes;
}

const [gameStateAddress] = PublicKey.findProgramAddressSync(
  [encoder.encode("game_state")],
  programId
);
const [vaultAddress] = PublicKey.findProgramAddressSync(
  [encoder.encode("vault")],
  programId
);
const [tokenVaultAddress] = PublicKey.findProgramAddressSync(
  [encoder.encode("token_vault")],
  programId
);

function landDataPda(landId) {
  return PublicKey.findProgramAddressSync(
    [encoder.encode("land_data"), u16ToLeBytes(landId)],
    programId
  );
}

function userProfilePda(user) {
  return PublicKey.findProgramAddressSync(
    [encoder.encode("user_profile"), user.toBuffer()],
    programId
  );
}

// ============================================================================
// ANCHOR PROGRAM SETUP
// ============================================================================

function createProgram(keypairOrNull) {
  const connection = new Connection(SOLANA_RPC_URL, "confirmed");

  let provider;
  if (keypairOrNull) {
    const wallet = new Wallet(keypairOrNull);
    provider = new AnchorProvider(connection, wallet, {
      commitment: "confirmed",
      preflightCommitment: "confirmed",
    });
  } else {
    provider = {
      connection,
      publicKey: null,
    };
  }

  const program = new Program(idl, provider);
  return { program, connection, provider };
}

// ============================================================================
// EARNINGS CALCULATION
// ============================================================================

function calculateEarnings(land, currentTime) {
  if (currentTime < MINING_START_TIME) {
    return land.fixedEarnings;
  }
  const timePassed = new BN(currentTime).sub(land.lastCheckout);
  const speed = new BN(EARNING_SPEEDS[land.level - 1]);
  return speed.mul(timePassed).div(new BN(SECONDS_PER_DAY)).add(land.fixedEarnings);
}

function getUpgradeCost(currentLevel) {
  if (currentLevel < 1 || currentLevel >= MAX_LEVEL) return new BN(0);
  return new BN(UPGRADE_COSTS[currentLevel - 1]);
}

function getEarningSpeed(level) {
  if (level < 1 || level > MAX_LEVEL) return new BN(0);
  return new BN(EARNING_SPEEDS[level - 1]);
}

// ============================================================================
// READ HELPERS
// ============================================================================

async function fetchGameState(program) {
  try {
    return await program.account.gameState.fetch(gameStateAddress);
  } catch {
    return null;
  }
}

async function fetchLandData(program, landId) {
  try {
    const [addr] = landDataPda(landId);
    return await program.account.landData.fetch(addr);
  } catch {
    return null;
  }
}

async function fetchUserProfile(program, user) {
  try {
    const [addr] = userProfilePda(user);
    return await program.account.userProfile.fetch(addr);
  } catch {
    return null;
  }
}

function getUserTokenAccountAddress(mint, user) {
  return getAssociatedTokenAddressSync(mint, user, true, TOKEN_2022_PROGRAM_ID);
}

async function getUserTokenBalance(connection, gameState, user) {
  try {
    const ata = getAssociatedTokenAddressSync(
      gameState.tokenMint,
      user,
      true,
      TOKEN_2022_PROGRAM_ID
    );
    const balance = await connection.getTokenAccountBalance(ata);
    return new BN(balance.value.amount);
  } catch {
    return new BN(0);
  }
}

async function getTokenVaultBalance(connection) {
  try {
    const balance = await connection.getTokenAccountBalance(tokenVaultAddress);
    return new BN(balance.value.amount);
  } catch {
    return new BN(0);
  }
}

function uint8ArrayToBase64(bytes) {
  let binary = "";
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

async function getUserLandIds(connection, user) {
  const landDataDiscriminator = new Uint8Array([188, 85, 52, 43, 52, 142, 58, 79]);
  const accounts = await connection.getProgramAccounts(programId, {
    filters: [
      {
        memcmp: {
          offset: 0,
          bytes: uint8ArrayToBase64(landDataDiscriminator),
          encoding: "base64",
        },
      },
      {
        memcmp: {
          offset: 10,
          bytes: user.toBase58(),
        },
      },
    ],
    dataSlice: { offset: 8, length: 2 },
  });

  const landIds = [];
  for (const account of accounts) {
    const data = account.account.data;
    const landId = data[0] | (data[1] << 8);
    landIds.push(landId);
  }
  return landIds.sort((a, b) => a - b);
}

async function getAllSoldLandIds(connection) {
  const landDataDiscriminator = new Uint8Array([188, 85, 52, 43, 52, 142, 58, 79]);
  const accounts = await connection.getProgramAccounts(programId, {
    filters: [
      {
        memcmp: {
          offset: 0,
          bytes: uint8ArrayToBase64(landDataDiscriminator),
          encoding: "base64",
        },
      },
    ],
    dataSlice: { offset: 8, length: 2 },
  });

  const landIds = [];
  for (const account of accounts) {
    const data = account.account.data;
    const landId = data[0] | (data[1] << 8);
    landIds.push(landId);
  }
  return landIds.sort((a, b) => a - b);
}

// ============================================================================
// TX HELPERS
// ============================================================================

async function sendAndConfirmTx(connection, signedTx) {
  const rawTx = signedTx.serialize();
  const signature = await connection.sendRawTransaction(rawTx, {
    skipPreflight: false,
    maxRetries: 5,
  });

  const timeout = 60_000;
  const start = Date.now();
  while (Date.now() - start < timeout) {
    const status = await connection.getSignatureStatus(signature);
    if (
      status?.value?.confirmationStatus === "confirmed" ||
      status?.value?.confirmationStatus === "finalized"
    ) {
      if (status.value.err) {
        throw new Error(`Transaction failed: ${JSON.stringify(status.value.err)}`);
      }
      return signature;
    }
    await new Promise((r) => setTimeout(r, 2000));
  }

  const finalStatus = await connection.getSignatureStatus(signature);
  if (finalStatus?.value?.confirmationStatus) {
    if (finalStatus.value.err) {
      throw new Error(`Transaction failed: ${JSON.stringify(finalStatus.value.err)}`);
    }
    return signature;
  }
  throw new Error(`Transaction confirmation timeout for ${signature}`);
}

async function sendVersionedTx(connection, keypair, vtx) {
  vtx.sign([keypair]);
  const rawTx = vtx.serialize();
  const signature = await connection.sendRawTransaction(rawTx, {
    skipPreflight: false,
    maxRetries: 5,
  });

  const timeout = 60_000;
  const start = Date.now();
  while (Date.now() - start < timeout) {
    const status = await connection.getSignatureStatus(signature);
    if (
      status?.value?.confirmationStatus === "confirmed" ||
      status?.value?.confirmationStatus === "finalized"
    ) {
      if (status.value.err) {
        throw new Error(`Transaction failed: ${JSON.stringify(status.value.err)}`);
      }
      return signature;
    }
    await new Promise((r) => setTimeout(r, 2000));
  }

  const finalStatus = await connection.getSignatureStatus(signature);
  if (finalStatus?.value?.confirmationStatus) {
    if (finalStatus.value.err) {
      throw new Error(`Transaction failed: ${JSON.stringify(finalStatus.value.err)}`);
    }
    return signature;
  }
  throw new Error(`Transaction confirmation timeout for ${signature}`);
}

// ============================================================================
// JUPITER HELPERS
// ============================================================================

function jupiterHeaders() {
  const headers = { "Content-Type": "application/json" };
  if (JUPITER_API_KEY) {
    headers["x-api-key"] = JUPITER_API_KEY;
  }
  return headers;
}

function requireJupiterKey() {
  if (!JUPITER_API_KEY) {
    fail(
      "JUPITER_API_KEY env var is required for swap/price commands. Get a free key at https://portal.jup.ag"
    );
  }
}

async function jupiterQuote(solAmount) {
  requireJupiterKey();
  const lamports = Math.round(solAmount * 1_000_000_000);
  const url = `https://api.jup.ag/swap/v1/quote?inputMint=${SOL_MINT}&outputMint=${GAME_TOKEN_MINT}&amount=${lamports}&slippageBps=100`;
  const resp = await fetch(url, { headers: jupiterHeaders() });
  if (!resp.ok) {
    throw new Error(`Jupiter quote failed: ${resp.status} ${await resp.text()}`);
  }
  return await resp.json();
}

async function jupiterSwap(keypair, solAmount) {
  requireJupiterKey();
  const quote = await jupiterQuote(solAmount);

  const swapResp = await fetch("https://api.jup.ag/swap/v1/swap", {
    method: "POST",
    headers: jupiterHeaders(),
    body: JSON.stringify({
      quoteResponse: quote,
      userPublicKey: keypair.publicKey.toBase58(),
      dynamicComputeUnitLimit: true,
      prioritizationFeeLamports: "auto",
    }),
  });

  if (!swapResp.ok) {
    throw new Error(`Jupiter swap failed: ${swapResp.status} ${await swapResp.text()}`);
  }

  const swapData = await swapResp.json();
  const txBuf = Buffer.from(swapData.swapTransaction, "base64");
  const vtx = VersionedTransaction.deserialize(txBuf);

  const connection = new Connection(SOLANA_RPC_URL, "confirmed");
  const signature = await sendVersionedTx(connection, keypair, vtx);

  return {
    signature,
    inputAmount: solAmount,
    outputAmount: tokensToDisplay(Number(quote.outAmount)),
    priceImpact: quote.priceImpactPct,
  };
}

async function jupiterPrice() {
  requireJupiterKey();
  const USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";

  // Derive price from 1 SOL -> $OLO quote + 1 SOL -> USDC quote
  const [oloQuoteResp, usdcQuoteResp] = await Promise.all([
    fetch(
      `https://api.jup.ag/swap/v1/quote?inputMint=${SOL_MINT}&outputMint=${GAME_TOKEN_MINT}&amount=1000000000&slippageBps=100`,
      { headers: jupiterHeaders() }
    ),
    fetch(
      `https://api.jup.ag/swap/v1/quote?inputMint=${SOL_MINT}&outputMint=${USDC_MINT}&amount=1000000000&slippageBps=100`,
      { headers: jupiterHeaders() }
    ),
  ]);

  if (!oloQuoteResp.ok) throw new Error(`OLO quote failed: ${oloQuoteResp.status}`);
  if (!usdcQuoteResp.ok) throw new Error(`USDC quote failed: ${usdcQuoteResp.status}`);

  const oloQuote = await oloQuoteResp.json();
  const usdcQuote = await usdcQuoteResp.json();

  const oloPerSol = Number(oloQuote.outAmount) / TOKEN_MULTIPLIER;
  const usdPerSol = Number(usdcQuote.outAmount) / 1_000_000;
  const priceUsd = usdPerSol / oloPerSol;

  return {
    priceUsd,
    oloPerSol: Math.round(oloPerSol),
    solPriceUsd: Math.round(usdPerSol * 100) / 100,
    mint: GAME_TOKEN_MINT,
    symbol: "$OLO",
  };
}

// ============================================================================
// COMMANDS
// ============================================================================

async function cmdStatus() {
  const keypair = requireKeypair();
  const { program, connection } = createProgram(keypair);
  const user = keypair.publicKey;

  const [gameState, solBalance, landIds, profile, tokenBalance] = await Promise.all([
    fetchGameState(program),
    connection.getBalance(user),
    getUserLandIds(connection, user),
    fetchUserProfile(program, user),
    (async () => {
      const gs = await fetchGameState(program);
      return gs ? getUserTokenBalance(connection, gs, user) : new BN(0);
    })(),
  ]);

  if (!gameState) fail("Game not initialized");

  // Fetch land details + earnings
  const now = Math.floor(Date.now() / 1000);
  const lands = [];
  let totalPending = new BN(0);

  for (const landId of landIds) {
    const land = await fetchLandData(program, landId);
    if (land) {
      const pending = calculateEarnings(land, now);
      totalPending = totalPending.add(pending);
      lands.push({
        landId: land.landId,
        level: land.level,
        earningsPerDay: tokensToDisplay(EARNING_SPEEDS[land.level - 1]),
        pendingEarnings: tokensToDisplay(pending),
        upgradeCost:
          land.level < MAX_LEVEL
            ? tokensToDisplay(UPGRADE_COSTS[land.level - 1])
            : null,
      });
    }
  }

  out({
    ok: true,
    wallet: {
      address: user.toBase58(),
      solBalance: lamportsToSol(solBalance),
      oloBalance: tokensToDisplay(tokenBalance),
    },
    game: {
      isActive: gameState.isActive,
      totalLandsSold: gameState.totalLandsSold.toNumber(),
    },
    lands: {
      count: lands.length,
      maxLands: MAX_LANDS_PER_USER,
      totalPendingEarnings: tokensToDisplay(totalPending),
      items: lands,
    },
  });
}

async function cmdGameState() {
  const { program, connection } = createProgram(null);
  const [gameState, vaultBal, tokenVaultBal] = await Promise.all([
    fetchGameState(program),
    connection.getBalance(vaultAddress),
    getTokenVaultBalance(connection),
  ]);

  if (!gameState) fail("Game not initialized");

  out({
    ok: true,
    gameState: {
      authority: gameState.authority.toBase58(),
      isActive: gameState.isActive,
      totalLandsSold: gameState.totalLandsSold.toNumber(),
      totalSolCollected: lamportsToSol(gameState.totalSolCollected.toNumber()),
      tokenMint: gameState.tokenMint.toBase58(),
    },
    vault: {
      solBalance: lamportsToSol(vaultBal),
      tokenVaultBalance: tokensToDisplay(tokenVaultBal),
    },
    addresses: {
      programId: PROGRAM_ID,
      gameState: gameStateAddress.toBase58(),
      vault: vaultAddress.toBase58(),
      tokenVault: tokenVaultAddress.toBase58(),
    },
  });
}

async function cmdBuyLand(landId) {
  if (!landId || landId < MIN_LAND_ID || landId > MAX_LAND_ID) {
    fail(`Invalid land ID. Must be ${MIN_LAND_ID}-${MAX_LAND_ID}`);
  }

  const keypair = requireKeypair();
  const { program, connection } = createProgram(keypair);
  const user = keypair.publicKey;

  const gameState = await fetchGameState(program);
  if (!gameState) fail("Game not initialized");
  if (!gameState.isActive) fail("Game is paused");

  // Check land is available
  const existing = await fetchLandData(program, landId);
  if (existing) fail(`Land #${landId} is already owned by ${existing.owner.toBase58()}`);

  // Check user hasn't hit max
  const profile = await fetchUserProfile(program, user);
  if (profile && profile.landsOwned >= MAX_LANDS_PER_USER) {
    fail(`Max lands reached (${MAX_LANDS_PER_USER})`);
  }

  // Check token balance
  const tokenBalance = await getUserTokenBalance(connection, gameState, user);
  if (tokenBalance.lt(new BN(LAND_PRICE_TOKENS))) {
    fail(
      `Insufficient $OLO. Need ${tokensToDisplay(LAND_PRICE_TOKENS)}, have ${tokensToDisplay(tokenBalance)}`
    );
  }

  const [landDataAddress] = landDataPda(landId);
  const [userProfileAddress] = userProfilePda(user);
  const userTokenAccount = getUserTokenAccountAddress(gameState.tokenMint, user);

  const ix = await program.methods
    .buyLand(landId)
    .accounts({
      user,
      gameState: gameStateAddress,
      landData: landDataAddress,
      userProfile: userProfileAddress,
      tokenMint: gameState.tokenMint,
      userTokenAccount,
      tokenProgram: TOKEN_2022_PROGRAM_ID,
      systemProgram: SystemProgram.programId,
    })
    .instruction();

  const tx = new Transaction().add(
    ComputeBudgetProgram.setComputeUnitLimit({ units: 400_000 }),
    ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100_000 }),
    ix
  );

  const { blockhash } = await connection.getLatestBlockhash("confirmed");
  tx.recentBlockhash = blockhash;
  tx.feePayer = user;
  tx.sign(keypair);

  const signature = await sendAndConfirmTx(connection, tx);

  out({
    ok: true,
    action: "buy_land",
    landId,
    cost: tokensToDisplay(LAND_PRICE_TOKENS),
    signature,
  });
}

async function cmdFindLand(count) {
  const { connection } = createProgram(null);
  const soldIds = new Set(await getAllSoldLandIds(connection));

  const available = [];
  for (let id = MIN_LAND_ID; id <= MAX_LAND_ID && available.length < count; id++) {
    if (!soldIds.has(id)) {
      available.push(id);
    }
  }

  out({
    ok: true,
    totalSold: soldIds.size,
    totalAvailable: MAX_LAND_ID - soldIds.size,
    landIds: available,
  });
}

async function cmdUpgradeLand(landId) {
  if (!landId || landId < MIN_LAND_ID || landId > MAX_LAND_ID) {
    fail(`Invalid land ID. Must be ${MIN_LAND_ID}-${MAX_LAND_ID}`);
  }

  const keypair = requireKeypair();
  const { program, connection } = createProgram(keypair);
  const user = keypair.publicKey;

  const gameState = await fetchGameState(program);
  if (!gameState) fail("Game not initialized");
  if (!gameState.isActive) fail("Game is paused");

  const land = await fetchLandData(program, landId);
  if (!land) fail(`Land #${landId} not found`);
  if (!land.owner.equals(user)) fail(`You don't own land #${landId}`);
  if (land.level >= MAX_LEVEL) fail(`Land #${landId} is already at max level (${MAX_LEVEL})`);

  const cost = getUpgradeCost(land.level);
  const tokenBalance = await getUserTokenBalance(connection, gameState, user);
  if (tokenBalance.lt(cost)) {
    fail(
      `Insufficient $OLO. Need ${tokensToDisplay(cost)}, have ${tokensToDisplay(tokenBalance)}`
    );
  }

  const [landDataAddress] = landDataPda(landId);
  const userTokenAccount = getUserTokenAccountAddress(gameState.tokenMint, user);

  const ix = await program.methods
    .upgradeLand(landId)
    .accounts({
      user,
      gameState: gameStateAddress,
      landData: landDataAddress,
      tokenMint: gameState.tokenMint,
      userTokenAccount,
      tokenProgram: TOKEN_2022_PROGRAM_ID,
    })
    .instruction();

  const tx = new Transaction().add(
    ComputeBudgetProgram.setComputeUnitLimit({ units: 400_000 }),
    ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100_000 }),
    ix
  );

  const { blockhash } = await connection.getLatestBlockhash("confirmed");
  tx.recentBlockhash = blockhash;
  tx.feePayer = user;
  tx.sign(keypair);

  const signature = await sendAndConfirmTx(connection, tx);

  out({
    ok: true,
    action: "upgrade_land",
    landId,
    fromLevel: land.level,
    toLevel: land.level + 1,
    cost: tokensToDisplay(cost),
    newEarningsPerDay: tokensToDisplay(EARNING_SPEEDS[land.level]),
    signature,
  });
}

async function cmdClaim(landId) {
  if (!landId || landId < MIN_LAND_ID || landId > MAX_LAND_ID) {
    fail(`Invalid land ID. Must be ${MIN_LAND_ID}-${MAX_LAND_ID}`);
  }

  const keypair = requireKeypair();
  const { program, connection } = createProgram(keypair);
  const user = keypair.publicKey;

  const gameState = await fetchGameState(program);
  if (!gameState) fail("Game not initialized");

  const land = await fetchLandData(program, landId);
  if (!land) fail(`Land #${landId} not found`);
  if (!land.owner.equals(user)) fail(`You don't own land #${landId}`);

  const now = Math.floor(Date.now() / 1000);
  const pending = calculateEarnings(land, now);

  const [landDataAddress] = landDataPda(landId);
  const userTokenAccount = getUserTokenAccountAddress(gameState.tokenMint, user);

  const ix = await program.methods
    .claimEarnings(landId)
    .accounts({
      user,
      gameState: gameStateAddress,
      landData: landDataAddress,
      tokenMint: gameState.tokenMint,
      tokenVault: tokenVaultAddress,
      userTokenAccount,
      tokenProgram: TOKEN_2022_PROGRAM_ID,
      associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
      systemProgram: SystemProgram.programId,
    })
    .instruction();

  const tx = new Transaction().add(
    ComputeBudgetProgram.setComputeUnitLimit({ units: 400_000 }),
    ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100_000 }),
    ix
  );

  const { blockhash } = await connection.getLatestBlockhash("confirmed");
  tx.recentBlockhash = blockhash;
  tx.feePayer = user;
  tx.sign(keypair);

  const signature = await sendAndConfirmTx(connection, tx);

  out({
    ok: true,
    action: "claim",
    landId,
    claimed: tokensToDisplay(pending),
    signature,
  });
}

async function cmdClaimAll() {
  const keypair = requireKeypair();
  const { program, connection } = createProgram(keypair);
  const user = keypair.publicKey;

  const gameState = await fetchGameState(program);
  if (!gameState) fail("Game not initialized");

  const landIds = await getUserLandIds(connection, user);
  if (landIds.length === 0) fail("You don't own any lands");

  const now = Math.floor(Date.now() / 1000);
  const pendingByLand = new Map();

  // Fetch pending earnings for all lands
  await Promise.all(
    landIds.map(async (landId) => {
      const land = await fetchLandData(program, landId);
      if (land) {
        pendingByLand.set(landId, calculateEarnings(land, now));
      }
    })
  );

  // Batch into transactions
  const batches = [];
  for (let i = 0; i < landIds.length; i += MAX_CLAIMS_PER_TX) {
    batches.push(landIds.slice(i, i + MAX_CLAIMS_PER_TX));
  }

  const results = {
    successfulLandIds: [],
    failedLandIds: [],
    totalClaimed: new BN(0),
    signatures: [],
  };

  for (const batch of batches) {
    try {
      const instructions = [
        ComputeBudgetProgram.setComputeUnitLimit({
          units: Math.min(300_000 * batch.length, 1_400_000),
        }),
        ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100_000 }),
      ];

      for (const landId of batch) {
        const [landDataAddress] = landDataPda(landId);
        const userTokenAccount = getUserTokenAccountAddress(gameState.tokenMint, user);

        const ix = await program.methods
          .claimEarnings(landId)
          .accounts({
            user,
            gameState: gameStateAddress,
            landData: landDataAddress,
            tokenMint: gameState.tokenMint,
            tokenVault: tokenVaultAddress,
            userTokenAccount,
            tokenProgram: TOKEN_2022_PROGRAM_ID,
            associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
            systemProgram: SystemProgram.programId,
          })
          .instruction();

        instructions.push(ix);
      }

      const tx = new Transaction().add(...instructions);
      const { blockhash } = await connection.getLatestBlockhash("confirmed");
      tx.recentBlockhash = blockhash;
      tx.feePayer = user;
      tx.sign(keypair);

      const signature = await sendAndConfirmTx(connection, tx);
      results.signatures.push(signature);

      for (const landId of batch) {
        results.successfulLandIds.push(landId);
        const pending = pendingByLand.get(landId) ?? new BN(0);
        results.totalClaimed = results.totalClaimed.add(pending);
      }
    } catch (err) {
      for (const landId of batch) {
        results.failedLandIds.push(landId);
      }
    }
  }

  out({
    ok: true,
    action: "claim_all",
    totalClaimed: tokensToDisplay(results.totalClaimed),
    successfulLandIds: results.successfulLandIds,
    failedLandIds: results.failedLandIds,
    signatures: results.signatures,
  });
}

async function cmdLandInfo(landId) {
  if (!landId || landId < MIN_LAND_ID || landId > MAX_LAND_ID) {
    fail(`Invalid land ID. Must be ${MIN_LAND_ID}-${MAX_LAND_ID}`);
  }

  const { program } = createProgram(null);
  const land = await fetchLandData(program, landId);

  if (!land) {
    out({
      ok: true,
      landId,
      owned: false,
      message: "Land is available for purchase",
      purchaseCost: tokensToDisplay(LAND_PRICE_TOKENS),
    });
    return;
  }

  const now = Math.floor(Date.now() / 1000);
  const pending = calculateEarnings(land, now);
  const earningsPerDay = EARNING_SPEEDS[land.level - 1];

  const info = {
    ok: true,
    landId: land.landId,
    owned: true,
    owner: land.owner.toBase58(),
    level: land.level,
    earningsPerDay: tokensToDisplay(earningsPerDay),
    pendingEarnings: tokensToDisplay(pending),
  };

  if (land.level < MAX_LEVEL) {
    const upgCost = UPGRADE_COSTS[land.level - 1];
    const nextSpeed = EARNING_SPEEDS[land.level];
    const extraPerDay = nextSpeed - earningsPerDay;
    const roiDays = tokensToDisplay(upgCost) / tokensToDisplay(extraPerDay);

    info.upgrade = {
      nextLevel: land.level + 1,
      cost: tokensToDisplay(upgCost),
      newEarningsPerDay: tokensToDisplay(nextSpeed),
      extraEarningsPerDay: tokensToDisplay(extraPerDay),
      roiDays: Math.round(roiDays * 100) / 100,
    };
  } else {
    info.upgrade = null;
  }

  out(info);
}

async function cmdSwapQuote(solAmount) {
  if (!solAmount || solAmount <= 0) fail("--sol-amount must be > 0");

  try {
    const quote = await jupiterQuote(solAmount);

    out({
      ok: true,
      inputMint: SOL_MINT,
      outputMint: GAME_TOKEN_MINT,
      inputAmount: solAmount,
      outputAmount: tokensToDisplay(Number(quote.outAmount)),
      priceImpactPct: quote.priceImpactPct,
      routePlan: quote.routePlan?.map((r) => ({
        swapInfo: r.swapInfo?.label,
        percent: r.percent,
      })),
    });
  } catch (err) {
    fail(`Swap quote failed: ${err.message}`);
  }
}

async function cmdSwap(solAmount) {
  if (!solAmount || solAmount <= 0) fail("--sol-amount must be > 0");

  const keypair = requireKeypair();

  try {
    const result = await jupiterSwap(keypair, solAmount);

    out({
      ok: true,
      action: "swap",
      inputSol: result.inputAmount,
      outputOlo: result.outputAmount,
      priceImpact: result.priceImpact,
      signature: result.signature,
    });
  } catch (err) {
    fail(`Swap failed: ${err.message}`);
  }
}

async function cmdPrice() {
  try {
    const price = await jupiterPrice();
    out({
      ok: true,
      ...price,
    });
  } catch (err) {
    fail(`Price fetch failed: ${err.message}`);
  }
}

async function cmdRecommend() {
  const keypair = requireKeypair();
  const { program, connection } = createProgram(keypair);
  const user = keypair.publicKey;

  const [gameState, solBalance, tokenBalance, landIds] = await Promise.all([
    fetchGameState(program),
    connection.getBalance(user),
    (async () => {
      const gs = await fetchGameState(program);
      return gs ? getUserTokenBalance(connection, gs, user) : new BN(0);
    })(),
    getUserLandIds(connection, user),
  ]);

  if (!gameState) fail("Game not initialized");

  const now = Math.floor(Date.now() / 1000);
  const actions = [];

  // Fetch land details
  const lands = [];
  let totalPending = new BN(0);

  for (const landId of landIds) {
    const land = await fetchLandData(program, landId);
    if (land) {
      const pending = calculateEarnings(land, now);
      totalPending = totalPending.add(pending);
      lands.push({ ...land, pending, landId: land.landId });
    }
  }

  // Action 1: Claim if pending > 1000 tokens
  const pendingDisplay = tokensToDisplay(totalPending);
  if (pendingDisplay > 1000) {
    actions.push({
      action: "claim-all",
      priority: 0,
      reason: `${Math.round(pendingDisplay)} $OLO pending across ${lands.length} lands`,
      command: "node colony-cli.mjs claim-all",
      roiDays: 0,
    });
  }

  // Action 2: Upgrade existing lands (ROI-sorted)
  const oloBalance = tokensToDisplay(tokenBalance) + pendingDisplay;

  for (const land of lands) {
    if (land.level >= MAX_LEVEL) continue;

    const upgCost = UPGRADE_COSTS[land.level - 1];
    const upgCostDisplay = tokensToDisplay(upgCost);
    const currentSpeed = EARNING_SPEEDS[land.level - 1];
    const nextSpeed = EARNING_SPEEDS[land.level];
    const extraPerDay = tokensToDisplay(nextSpeed - currentSpeed);
    const roiDays = upgCostDisplay / extraPerDay;

    if (oloBalance >= upgCostDisplay) {
      actions.push({
        action: "upgrade-land",
        landId: land.landId,
        priority: 1,
        reason: `Upgrade land #${land.landId} L${land.level}->L${land.level + 1} (${upgCostDisplay} $OLO, +${extraPerDay}/day, ROI ${Math.round(roiDays * 10) / 10}d)`,
        command: `node colony-cli.mjs upgrade-land --land-id ${land.landId}`,
        roiDays,
      });
    }
  }

  // Action 3: Buy new land if have room and tokens
  if (
    lands.length < MAX_LANDS_PER_USER &&
    oloBalance >= tokensToDisplay(LAND_PRICE_TOKENS)
  ) {
    const newLandRoi = tokensToDisplay(LAND_PRICE_TOKENS) / tokensToDisplay(EARNING_SPEEDS[0]);
    actions.push({
      action: "buy-land",
      priority: 2,
      reason: `Buy new land (${tokensToDisplay(LAND_PRICE_TOKENS)} $OLO, +${tokensToDisplay(EARNING_SPEEDS[0])}/day, ROI ${Math.round(newLandRoi * 10) / 10}d)`,
      command: "node colony-cli.mjs find-land --count 1  # then buy the returned ID",
      roiDays: newLandRoi,
    });
  }

  // Action 4: Swap SOL for $OLO if low on tokens but have SOL
  const solBal = lamportsToSol(solBalance);
  if (oloBalance < tokensToDisplay(LAND_PRICE_TOKENS) && solBal > 0.05) {
    actions.push({
      action: "swap",
      priority: 3,
      reason: `Low $OLO (${Math.round(oloBalance)}). Consider swapping SOL for $OLO (have ${Math.round(solBal * 1000) / 1000} SOL)`,
      command: "node colony-cli.mjs swap-quote --sol-amount 0.1  # adjust amount",
      roiDays: null,
    });
  }

  // Sort: priority 0 first, then by ROI (lowest = best)
  actions.sort((a, b) => {
    if (a.priority !== b.priority) return a.priority - b.priority;
    if (a.roiDays === null) return 1;
    if (b.roiDays === null) return -1;
    return a.roiDays - b.roiDays;
  });

  out({
    ok: true,
    wallet: {
      solBalance: Math.round(solBal * 10000) / 10000,
      oloBalance: Math.round(oloBalance),
    },
    lands: {
      count: lands.length,
      maxLands: MAX_LANDS_PER_USER,
      totalPendingEarnings: Math.round(pendingDisplay),
    },
    recommendations: actions.length > 0 ? actions : [{ action: "wait", reason: "No actions available. Wait for earnings to accumulate." }],
  });
}

async function cmdGenerateWallet() {
  const newKeypair = Keypair.generate();
  const secretKeyBase58 = bs58.encode(newKeypair.secretKey);

  out({
    ok: true,
    action: "generate_wallet",
    publicKey: newKeypair.publicKey.toBase58(),
    privateKey: secretKeyBase58,
    instructions: [
      "Save the privateKey as SOLANA_PRIVATE_KEY environment variable — keep it secret!",
      `Send SOL to ${newKeypair.publicKey.toBase58()} to fund the wallet for transaction fees.`,
      "Minimum recommended: 0.05 SOL for tx fees + SOL for swapping to $OLO.",
      "Then run: node colony-cli.mjs status",
    ],
  });
}

// ============================================================================
// CLI ENTRY
// ============================================================================

function parseArgs(args) {
  const parsed = { command: args[0], flags: {} };
  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      const val = args[i + 1];
      parsed.flags[key] = val;
      i++;
    }
  }
  return parsed;
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    out({
      ok: false,
      error: "No command provided",
      commands: [
        "status",
        "game-state",
        "buy-land --land-id <id>",
        "find-land [--count N]",
        "upgrade-land --land-id <id>",
        "claim --land-id <id>",
        "claim-all",
        "land-info --land-id <id>",
        "swap-quote --sol-amount <amt>",
        "swap --sol-amount <amt>",
        "recommend",
        "price",
        "generate-wallet",
      ],
    });
    process.exit(1);
  }

  const { command, flags } = parseArgs(args);

  try {
    switch (command) {
      case "status":
        await cmdStatus();
        break;
      case "game-state":
        await cmdGameState();
        break;
      case "buy-land":
        await cmdBuyLand(Number(flags["land-id"]));
        break;
      case "find-land":
        await cmdFindLand(Number(flags.count) || 5);
        break;
      case "upgrade-land":
        await cmdUpgradeLand(Number(flags["land-id"]));
        break;
      case "claim":
        await cmdClaim(Number(flags["land-id"]));
        break;
      case "claim-all":
        await cmdClaimAll();
        break;
      case "land-info":
        await cmdLandInfo(Number(flags["land-id"]));
        break;
      case "swap-quote":
        await cmdSwapQuote(Number(flags["sol-amount"]));
        break;
      case "swap":
        await cmdSwap(Number(flags["sol-amount"]));
        break;
      case "recommend":
        await cmdRecommend();
        break;
      case "price":
        await cmdPrice();
        break;
      case "generate-wallet":
        await cmdGenerateWallet();
        break;
      default:
        fail(`Unknown command: ${command}`);
    }
  } catch (err) {
    fail(err.message, err.stack);
  }
}

main();
