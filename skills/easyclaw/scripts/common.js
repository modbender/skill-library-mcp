#!/usr/bin/env node
require("dotenv").config();

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {
  Connection,
  Keypair,
  PublicKey,
  SystemProgram,
  Transaction,
  TransactionInstruction
} = require("@solana/web3.js");
const {
  ASSOCIATED_TOKEN_PROGRAM_ID,
  TOKEN_PROGRAM_ID,
  createAssociatedTokenAccountIdempotentInstruction,
  getAssociatedTokenAddressSync
} = require("@solana/spl-token");

const DEFAULT_PROGRAM_IDS = {
  ORDER_ENGINE: "GpMobZUKPtEE1eiZQAADo2ecD54JXhNHPNts5kPGwLtb",
  MARKET_REGISTRY: "BsA8fuyw8XqBMiUfpLbdiBwbKg8MZMHB1jdZzjs7c46q"
};

const DISCRIMINATORS = {
  CREATE_MARGIN_ACCOUNT: Buffer.from([98, 114, 213, 184, 129, 89, 90, 185]),
  CREATE_USER_MARKET_POSITION: Buffer.from([
    184, 183, 182, 125, 240, 234, 69, 166
  ]),
  DEPOSIT_COLLATERAL: Buffer.from([156, 131, 142, 116, 146, 247, 162, 120]),
  PLACE_ORDER: Buffer.from([51, 194, 155, 175, 109, 130, 96, 106]),
  ENGINE_CONFIG_ACCOUNT: Buffer.from([10, 197, 172, 236, 51, 169, 22, 207]),
  USER_MARGIN_ACCOUNT: Buffer.from([198, 202, 205, 196, 42, 177, 76, 75]),
  ORDER_ACCOUNT: Buffer.from([134, 173, 223, 185, 77, 86, 28, 51])
};

function usageNumberToBigInt(name, value) {
  const raw = String(value).trim();
  if (!/^\d+$/.test(raw)) {
    throw new Error(`Invalid numeric value for ${name}: ${value}`);
  }
  return BigInt(raw);
}

function usageSignedToBigInt(name, value) {
  const raw = String(value).trim();
  if (!/^-?\d+$/.test(raw)) {
    throw new Error(`Invalid signed numeric value for ${name}: ${value}`);
  }
  return BigInt(raw);
}

function u64Le(value) {
  let n = typeof value === "bigint" ? value : usageNumberToBigInt("u64", value);
  if (n < 0n || n > 18446744073709551615n) {
    throw new Error(`u64 out of range: ${value}`);
  }
  const out = Buffer.alloc(8);
  out.writeBigUInt64LE(n, 0);
  return out;
}

function i64Le(value) {
  let n = typeof value === "bigint" ? value : usageSignedToBigInt("i64", value);
  if (n < -9223372036854775808n || n > 9223372036854775807n) {
    throw new Error(`i64 out of range: ${value}`);
  }
  const out = Buffer.alloc(8);
  out.writeBigInt64LE(n, 0);
  return out;
}

function readU64Le(data, offset) {
  return data.readBigUInt64LE(offset);
}

function readI64Le(data, offset) {
  return data.readBigInt64LE(offset);
}

function pubkeyFromEnv(name, fallback) {
  const raw = process.env[name];
  const value = raw && raw.trim().length > 0 ? raw.trim() : fallback;
  if (!value) {
    throw new Error(`Missing required env: ${name}`);
  }
  return new PublicKey(value);
}

function readSigner() {
  const keypairPath =
    process.env.KEYPAIR_PATH ||
    process.env.ANCHOR_WALLET ||
    path.join(os.homedir(), ".config/solana/id.json");

  const absolute = path.resolve(keypairPath);
  if (!fs.existsSync(absolute)) {
    throw new Error(`Signer keypair not found: ${absolute}`);
  }
  const content = fs.readFileSync(absolute, "utf8");
  const secret = Uint8Array.from(JSON.parse(content));
  return { signer: Keypair.fromSecretKey(secret), keypairPath: absolute };
}

function getConnection() {
  const rpc =
    process.env.SOLANA_RPC_URL ||
    process.env.ANCHOR_PROVIDER_URL ||
    "http://127.0.0.1:8899";
  return { connection: new Connection(rpc, { commitment: "confirmed" }), rpc };
}

function deriveEngineConfigPda(orderEngineProgramId) {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("engine-config")],
    orderEngineProgramId
  )[0];
}

function deriveUserMarginPda(user, orderEngineProgramId) {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("user-margin"), user.toBuffer()],
    orderEngineProgramId
  )[0];
}

function deriveUserMarketPositionPda(userMargin, marketId, orderEngineProgramId) {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("user-market-pos"), userMargin.toBuffer(), u64Le(marketId)],
    orderEngineProgramId
  )[0];
}

function deriveMarketPda(marketId, marketRegistryProgramId) {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("market"), u64Le(marketId)],
    marketRegistryProgramId
  )[0];
}

function deriveGlobalConfigPda(marketRegistryProgramId) {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("global-config")],
    marketRegistryProgramId
  )[0];
}

function deriveOrderPda(userMargin, nonce, orderEngineProgramId) {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("order"), userMargin.toBuffer(), u64Le(nonce)],
    orderEngineProgramId
  )[0];
}

function decodeEngineConfig(data) {
  if (data.length < 8 + 32 * 3) {
    throw new Error("Invalid EngineConfig account length");
  }
  if (!data.subarray(0, 8).equals(DISCRIMINATORS.ENGINE_CONFIG_ACCOUNT)) {
    throw new Error("EngineConfig discriminator mismatch");
  }
  let offset = 8;
  const admin = new PublicKey(data.subarray(offset, offset + 32));
  offset += 32;
  const usdcMint = new PublicKey(data.subarray(offset, offset + 32));
  offset += 32;
  const collateralVault = new PublicKey(data.subarray(offset, offset + 32));
  return { admin, usdcMint, collateralVault };
}

function decodeUserMargin(data) {
  if (data.length < 8 + 32 + 8 + 8 + 8 + 1) {
    throw new Error("Invalid UserMargin account length");
  }
  if (!data.subarray(0, 8).equals(DISCRIMINATORS.USER_MARGIN_ACCOUNT)) {
    throw new Error("UserMargin discriminator mismatch");
  }
  let offset = 8;
  const owner = new PublicKey(data.subarray(offset, offset + 32));
  offset += 32;
  const collateralBalance = readU64Le(data, offset);
  offset += 8;
  const nextOrderNonce = readU64Le(data, offset);
  offset += 8;
  const totalNotional = readU64Le(data, offset);
  offset += 8;
  const bump = data.readUInt8(offset);
  return { owner, collateralBalance, nextOrderNonce, totalNotional, bump };
}

function decodeOrder(data, pubkey) {
  if (data.length < 133) {
    throw new Error("Invalid Order account length");
  }
  if (!data.subarray(0, 8).equals(DISCRIMINATORS.ORDER_ACCOUNT)) {
    throw new Error("Order discriminator mismatch");
  }
  let offset = 8;
  const id = readU64Le(data, offset);
  offset += 8;
  const userMargin = new PublicKey(data.subarray(offset, offset + 32));
  offset += 32;
  const user = new PublicKey(data.subarray(offset, offset + 32));
  offset += 32;
  const marketId = readU64Le(data, offset);
  offset += 8;
  const side = data.readUInt8(offset);
  offset += 1;
  const orderType = data.readUInt8(offset);
  offset += 1;
  const reduceOnly = data.readUInt8(offset) === 1;
  offset += 1;
  const margin = readU64Le(data, offset);
  offset += 8;
  const price = readU64Le(data, offset);
  offset += 8;
  const createdAt = readI64Le(data, offset);
  offset += 8;
  const expiresAt = readI64Le(data, offset);
  offset += 8;
  const clientOrderId = readU64Le(data, offset);
  offset += 8;
  const status = data.readUInt8(offset);
  offset += 1;
  const bump = data.readUInt8(offset);

  return {
    pubkey,
    id,
    userMargin,
    user,
    marketId,
    side,
    orderType,
    reduceOnly,
    margin,
    price,
    createdAt,
    expiresAt,
    clientOrderId,
    status,
    bump
  };
}

function sideName(side) {
  return side === 0 ? "buy" : "sell";
}

function orderTypeName(orderType) {
  return orderType === 0 ? "market" : "limit";
}

function orderStatusName(status) {
  if (status === 0) return "open";
  if (status === 1) return "executed";
  if (status === 2) return "cancelled";
  if (status === 3) return "expired";
  return `unknown(${status})`;
}

function boolByte(value) {
  return Buffer.from([value ? 1 : 0]);
}

function orderData({
  marketId,
  side,
  orderType,
  reduceOnly,
  margin,
  price,
  ttlSecs,
  clientOrderId
}) {
  return Buffer.concat([
    DISCRIMINATORS.PLACE_ORDER,
    u64Le(marketId),
    Buffer.from([side]),
    Buffer.from([orderType]),
    boolByte(reduceOnly),
    u64Le(margin),
    u64Le(price),
    i64Le(ttlSecs),
    u64Le(clientOrderId)
  ]);
}

function instruction(programId, keys, data) {
  return new TransactionInstruction({ programId, keys, data });
}

async function sendInstructions(connection, signer, instructions) {
  if (instructions.length === 0) {
    return null;
  }
  const latestBlockhash = await connection.getLatestBlockhash("confirmed");
  const tx = new Transaction({
    feePayer: signer.publicKey,
    recentBlockhash: latestBlockhash.blockhash
  });
  tx.add(...instructions);
  tx.sign(signer);
  const signature = await connection.sendRawTransaction(tx.serialize(), {
    skipPreflight: false
  });
  await connection.confirmTransaction(
    { signature, ...latestBlockhash },
    "confirmed"
  );
  return signature;
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) {
      continue;
    }
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

async function ensureAtaExists(connection, signer, owner, mint) {
  const ata = getAssociatedTokenAddressSync(
    mint,
    owner,
    false,
    TOKEN_PROGRAM_ID,
    ASSOCIATED_TOKEN_PROGRAM_ID
  );
  const info = await connection.getAccountInfo(ata);
  if (info) {
    return { ata, createInstruction: null };
  }
  return {
    ata,
    createInstruction: createAssociatedTokenAccountIdempotentInstruction(
      signer.publicKey,
      ata,
      owner,
      mint,
      TOKEN_PROGRAM_ID,
      ASSOCIATED_TOKEN_PROGRAM_ID
    )
  };
}

function programIdsFromEnv() {
  return {
    orderEngine: pubkeyFromEnv(
      "ORDER_ENGINE_PROGRAM_ID",
      DEFAULT_PROGRAM_IDS.ORDER_ENGINE
    ),
    marketRegistry: pubkeyFromEnv(
      "MARKET_REGISTRY_PROGRAM_ID",
      DEFAULT_PROGRAM_IDS.MARKET_REGISTRY
    )
  };
}

module.exports = {
  ASSOCIATED_TOKEN_PROGRAM_ID,
  DISCRIMINATORS,
  DEFAULT_PROGRAM_IDS,
  PublicKey,
  SystemProgram,
  TOKEN_PROGRAM_ID,
  decodeEngineConfig,
  decodeOrder,
  decodeUserMargin,
  deriveEngineConfigPda,
  deriveGlobalConfigPda,
  deriveMarketPda,
  deriveOrderPda,
  deriveUserMarginPda,
  deriveUserMarketPositionPda,
  ensureAtaExists,
  getConnection,
  instruction,
  orderData,
  orderStatusName,
  orderTypeName,
  parseArgs,
  programIdsFromEnv,
  readSigner,
  sendInstructions,
  sideName,
  u64Le,
  usageNumberToBigInt
};
