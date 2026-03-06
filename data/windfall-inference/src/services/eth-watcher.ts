/**
 * ETH Deposit Watcher
 *
 * Watches for incoming ETH transfers on Base to the Windfall wallet.
 * When detected, converts to USD at market rate and credits the sender's API key balance.
 *
 * Flow:
 * 1. User links their wallet to their API key (POST /api/keys with wallet_address)
 * 2. User sends ETH to Windfall wallet on Base
 * 3. Watcher detects the transfer, converts to USD, finds the API key by wallet address
 * 4. Credits the key's balance with the USD amount
 *
 * Polls every 30 seconds for new transactions.
 */

import { ethers } from 'ethers';
import Database from 'better-sqlite3';
import path from 'path';
import { config } from '../config';

const DB_PATH = path.resolve(__dirname, '../../windfall.db');
const POLL_INTERVAL = 30_000; // 30 seconds
const MIN_ETH_DEPOSIT = 0.0001; // ~$0.25 at current prices, filters dust

let provider: ethers.JsonRpcProvider;
let lastBlockChecked = 0;
let pollTimer: NodeJS.Timeout | null = null;

// ETH price cache
let cachedEthPrice = 2800; // fallback
let priceLastFetched = 0;

async function getEthPrice(): Promise<number> {
  if (Date.now() - priceLastFetched < 5 * 60 * 1000) return cachedEthPrice;
  try {
    const res = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd');
    if (res.ok) {
      const data = (await res.json()) as any;
      cachedEthPrice = data.ethereum.usd;
      priceLastFetched = Date.now();
    }
  } catch {
    // Keep cached price
  }
  return cachedEthPrice;
}

function getDb(): Database.Database {
  const db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');
  db.exec(`
    CREATE TABLE IF NOT EXISTS eth_deposits (
      tx_hash TEXT PRIMARY KEY,
      from_address TEXT NOT NULL,
      amount_eth REAL NOT NULL,
      amount_usd REAL NOT NULL,
      eth_price_usd REAL NOT NULL,
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
  const row = db.prepare('SELECT 1 FROM eth_deposits WHERE tx_hash = ?').get(txHash);
  db.close();
  return !!row;
}

/** Record a processed deposit. */
function recordDeposit(
  txHash: string,
  from: string,
  amountEth: number,
  amountUsd: number,
  ethPriceUsd: number,
  keyId: number | null,
  blockNumber: number,
): void {
  const db = getDb();
  db.prepare(`
    INSERT OR IGNORE INTO eth_deposits (tx_hash, from_address, amount_eth, amount_usd, eth_price_usd, key_id, credited_at, block_number)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).run(txHash, from.toLowerCase(), amountEth, amountUsd, ethPriceUsd, keyId, new Date().toISOString(), blockNumber);
  db.close();
}

/** Poll for new ETH transfers to our wallet. */
async function pollDeposits(): Promise<void> {
  try {
    if (!provider) {
      provider = new ethers.JsonRpcProvider(config.baseRpcUrl);
    }

    const currentBlock = await provider.getBlockNumber();

    // On first run, start from 5 blocks back
    if (lastBlockChecked === 0) {
      lastBlockChecked = currentBlock - 5;
    }

    // Scan up to 10 blocks at a time
    const fromBlock = lastBlockChecked + 1;
    const toBlock = Math.min(currentBlock, fromBlock + 9);

    if (fromBlock > toBlock) return;

    const ethPrice = await getEthPrice();

    for (let blockNum = fromBlock; blockNum <= toBlock; blockNum++) {
      const block = await provider.getBlock(blockNum, true);
      if (!block || !block.prefetchedTransactions) continue;

      for (const tx of block.prefetchedTransactions) {
        // Check if this is a value transfer to our wallet
        if (
          tx.to?.toLowerCase() === config.walletAddress.toLowerCase() &&
          tx.value > 0n
        ) {
          const txHash = tx.hash;
          if (isProcessed(txHash)) continue;

          const amountEth = parseFloat(ethers.formatEther(tx.value));

          // Filter dust
          if (amountEth < MIN_ETH_DEPOSIT) {
            recordDeposit(txHash, tx.from, amountEth, 0, ethPrice, null, blockNum);
            continue;
          }

          const amountUsd = amountEth * ethPrice;

          // Find API key linked to this wallet
          const key = findKeyByWallet(tx.from);

          if (key) {
            creditKey(key.id, amountUsd);
            recordDeposit(txHash, tx.from, amountEth, amountUsd, ethPrice, key.id, blockNum);
            console.log(
              `[eth] Credited $${amountUsd.toFixed(2)} (${amountEth.toFixed(6)} ETH @ $${ethPrice}) to key #${key.id} (${key.label}) from ${tx.from.slice(0, 10)}...`,
            );
          } else {
            recordDeposit(txHash, tx.from, amountEth, amountUsd, ethPrice, null, blockNum);
            console.log(
              `[eth] Received ${amountEth.toFixed(6)} ETH ($${amountUsd.toFixed(2)}) from ${tx.from.slice(0, 10)}... — no linked API key`,
            );
          }
        }
      }
    }

    lastBlockChecked = toBlock;
  } catch (err: any) {
    console.error('[eth] Poll error:', err.message);
  }
}

/** Start the ETH deposit watcher. */
export function startEthWatcher(): void {
  console.log('[eth] Starting ETH deposit watcher');
  pollDeposits();
  pollTimer = setInterval(pollDeposits, POLL_INTERVAL);
}

/** Stop the watcher. */
export function stopEthWatcher(): void {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

/** Get deposit stats. */
export function getEthDepositStats(): {
  totalDeposits: number;
  totalAmountEth: number;
  totalAmountUsd: number;
  credited: number;
  uncredited: number;
} {
  const db = getDb();
  const total = db.prepare(
    'SELECT COUNT(*) as c, COALESCE(SUM(amount_eth), 0) as eth, COALESCE(SUM(amount_usd), 0) as usd FROM eth_deposits'
  ).get() as any;
  const credited = (db.prepare('SELECT COUNT(*) as c FROM eth_deposits WHERE key_id IS NOT NULL').get() as any).c;
  db.close();

  return {
    totalDeposits: total.c,
    totalAmountEth: total.eth,
    totalAmountUsd: total.usd,
    credited,
    uncredited: total.c - credited,
  };
}
