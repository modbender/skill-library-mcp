/**
 * USDC Deposit Watcher
 *
 * Watches for incoming USDC transfers on Base to the Windfall wallet.
 * When detected, credits the sender's API key balance.
 *
 * Flow:
 * 1. User links their wallet to their API key (POST /api/keys with wallet_address)
 * 2. User sends USDC to Windfall wallet on Base
 * 3. Watcher detects the transfer, finds the API key by wallet address
 * 4. Credits the key's balance with the USD amount
 *
 * Polls every 30 seconds for new Transfer events.
 */

import { ethers } from 'ethers';
import Database from 'better-sqlite3';
import path from 'path';
import { config } from '../config';

const DB_PATH = path.resolve(__dirname, '../../windfall.db');
const POLL_INTERVAL = 30_000; // 30 seconds
const USDC_DECIMALS = 6;

// USDC Transfer event ABI
const USDC_ABI = [
  'event Transfer(address indexed from, address indexed to, uint256 value)',
  'function balanceOf(address) view returns (uint256)',
];

let provider: ethers.JsonRpcProvider;
let usdcContract: ethers.Contract;
let lastBlockChecked = 0;
let pollTimer: NodeJS.Timeout | null = null;

function getDb(): Database.Database {
  const db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');
  // Track processed deposits to avoid double-crediting
  db.exec(`
    CREATE TABLE IF NOT EXISTS usdc_deposits (
      tx_hash TEXT PRIMARY KEY,
      from_address TEXT NOT NULL,
      amount_usd REAL NOT NULL,
      key_id INTEGER,
      credited_at TEXT NOT NULL,
      block_number INTEGER
    )
  `);
  return db;
}

/** Find an API key by wallet address. */
function findKeyByWallet(walletAddress: string): { id: number; label: string } | null {
  const db = getDb();
  const row = db.prepare(
    'SELECT id, label FROM api_keys WHERE LOWER(wallet_address) = LOWER(?)'
  ).get(walletAddress) as any;
  db.close();
  return row ? { id: row.id, label: row.label } : null;
}

/** Credit an API key balance. */
function creditKey(keyId: number, amountUsd: number): void {
  const db = getDb();
  db.prepare('UPDATE api_keys SET balance_usd = balance_usd + ? WHERE id = ?')
    .run(amountUsd, keyId);
  db.close();
}

/** Check if a deposit was already processed. */
function isProcessed(txHash: string): boolean {
  const db = getDb();
  const row = db.prepare('SELECT 1 FROM usdc_deposits WHERE tx_hash = ?').get(txHash);
  db.close();
  return !!row;
}

/** Record a processed deposit. */
function recordDeposit(txHash: string, from: string, amountUsd: number, keyId: number | null, blockNumber: number): void {
  const db = getDb();
  db.prepare(`
    INSERT OR IGNORE INTO usdc_deposits (tx_hash, from_address, amount_usd, key_id, credited_at, block_number)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(txHash, from.toLowerCase(), amountUsd, keyId, new Date().toISOString(), blockNumber);
  db.close();
}

/** Poll for new USDC transfers to our wallet. */
async function pollDeposits(): Promise<void> {
  try {
    if (!provider) {
      provider = new ethers.JsonRpcProvider(config.baseRpcUrl);
      usdcContract = new ethers.Contract(config.usdcAddress, USDC_ABI, provider);
    }

    const currentBlock = await provider.getBlockNumber();

    // On first run, start from 5 blocks back
    if (lastBlockChecked === 0) {
      lastBlockChecked = currentBlock - 5;
    }

    // Alchemy free tier: max 10 blocks per eth_getLogs query
    const fromBlock = lastBlockChecked + 1;
    const toBlock = Math.min(currentBlock, fromBlock + 9);

    if (fromBlock > toBlock) return;

    // Query Transfer events TO our wallet
    const filter = usdcContract.filters.Transfer(null, config.walletAddress);
    const events = await usdcContract.queryFilter(filter, fromBlock, toBlock);

    for (const event of events) {
      const log = event as ethers.EventLog;
      const txHash = log.transactionHash;

      if (isProcessed(txHash)) continue;

      const from = log.args[0] as string;
      const value = log.args[2] as bigint;
      const amountUsd = Number(value) / (10 ** USDC_DECIMALS);

      // Minimum $0.01 to avoid dust
      if (amountUsd < 0.01) {
        recordDeposit(txHash, from, amountUsd, null, log.blockNumber);
        continue;
      }

      // Find API key linked to this wallet
      const key = findKeyByWallet(from);

      if (key) {
        creditKey(key.id, amountUsd);
        recordDeposit(txHash, from, amountUsd, key.id, log.blockNumber);
        console.log(`[usdc] Credited $${amountUsd.toFixed(2)} to key #${key.id} (${key.label}) from ${from.slice(0, 10)}...`);
      } else {
        // No linked key — record but don't credit. User can link later.
        recordDeposit(txHash, from, amountUsd, null, log.blockNumber);
        console.log(`[usdc] Received $${amountUsd.toFixed(2)} from ${from.slice(0, 10)}... — no linked API key`);
      }
    }

    lastBlockChecked = toBlock;
  } catch (err: any) {
    console.error('[usdc] Poll error:', err.message);
  }
}

/** Start the USDC deposit watcher. */
export function startUsdcWatcher(): void {
  console.log('[usdc] Starting USDC deposit watcher');
  // Initial poll
  pollDeposits();
  // Recurring poll
  pollTimer = setInterval(pollDeposits, POLL_INTERVAL);
}

/** Stop the watcher. */
export function stopUsdcWatcher(): void {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

/** Get deposit stats. */
export function getDepositStats(): {
  totalDeposits: number;
  totalAmountUsd: number;
  credited: number;
  uncredited: number;
} {
  const db = getDb();
  const total = (db.prepare('SELECT COUNT(*) as c, COALESCE(SUM(amount_usd), 0) as a FROM usdc_deposits').get() as any);
  const credited = (db.prepare('SELECT COUNT(*) as c FROM usdc_deposits WHERE key_id IS NOT NULL').get() as any).c;
  db.close();

  return {
    totalDeposits: total.c,
    totalAmountUsd: total.a,
    credited,
    uncredited: total.c - credited,
  };
}
