import { ethers } from 'ethers';
import { config } from '../config';
import { PaymentMethod } from '../types';

const provider = new ethers.JsonRpcProvider(config.baseRpcUrl);

// USDC on Base (6 decimals)
const USDC_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'event Transfer(address indexed from, address indexed to, uint256 value)',
];
const usdcContract = new ethers.Contract(config.usdcAddress, USDC_ABI, provider);

// ERC-20 Transfer event topic
const TRANSFER_TOPIC = ethers.id('Transfer(address,address,uint256)');

// Track used transaction hashes to prevent replay attacks
const usedTxHashes = new Set<string>();

// --- x402: Verify onchain payment (ETH or USDC) ---

export interface OnchainPaymentResult {
  valid: boolean;
  token: 'ETH' | 'USDC' | 'unknown';
  amountUsd: number;
  from: string;
  error?: string;
}

/**
 * Verify an onchain payment tx hash for x402.
 * Checks for both native ETH transfer and USDC Transfer event to our wallet.
 */
export async function verifyOnchainPayment(
  txHash: string,
  expectedAmountUsd: number,
): Promise<OnchainPaymentResult> {
  // Prevent transaction replay
  const normalizedHash = txHash.toLowerCase();
  if (usedTxHashes.has(normalizedHash)) {
    return { valid: false, token: 'unknown', amountUsd: 0, from: '', error: 'Transaction already used' };
  }

  try {
    const tx = await provider.getTransaction(txHash);
    if (!tx) return { valid: false, token: 'unknown', amountUsd: 0, from: '', error: 'Transaction not found' };

    // Wait for confirmation
    const receipt = await tx.wait(1);
    if (!receipt || receipt.status !== 1) {
      return { valid: false, token: 'unknown', amountUsd: 0, from: tx.from, error: 'Transaction failed' };
    }

    // --- Try USDC first (check logs for Transfer to our wallet) ---
    const usdcResult = checkUsdcTransfer(receipt, tx.from);
    if (usdcResult) {
      if (usdcResult.amountUsd < expectedAmountUsd * 0.95) {
        return {
          valid: false,
          token: 'USDC',
          amountUsd: usdcResult.amountUsd,
          from: tx.from,
          error: `USDC payment too low: $${usdcResult.amountUsd.toFixed(4)} < $${expectedAmountUsd.toFixed(4)} required`,
        };
      }
      usedTxHashes.add(normalizedHash);
      return { valid: true, token: 'USDC', amountUsd: usdcResult.amountUsd, from: tx.from };
    }

    // --- Try ETH (native value transfer to our wallet) ---
    if (tx.to?.toLowerCase() === config.walletAddress.toLowerCase() && tx.value > 0n) {
      const amountEth = parseFloat(ethers.formatEther(tx.value));
      const ethPriceUsd = await getEthPrice();
      const valueUsd = amountEth * ethPriceUsd;

      // Lenient on ETH price (50% threshold) since price fluctuates between send and verify
      if (valueUsd < expectedAmountUsd * 0.5) {
        return {
          valid: false,
          token: 'ETH',
          amountUsd: valueUsd,
          from: tx.from,
          error: `ETH payment too low: $${valueUsd.toFixed(4)} < $${expectedAmountUsd.toFixed(4)} required`,
        };
      }
      usedTxHashes.add(normalizedHash);
      return { valid: true, token: 'ETH', amountUsd: valueUsd, from: tx.from };
    }

    return {
      valid: false,
      token: 'unknown',
      amountUsd: 0,
      from: tx.from,
      error: 'Transaction does not contain ETH or USDC transfer to Windfall wallet',
    };
  } catch (err) {
    return { valid: false, token: 'unknown', amountUsd: 0, from: '', error: String(err) };
  }
}

/** Check a tx receipt for a USDC Transfer event to our wallet. */
function checkUsdcTransfer(
  receipt: ethers.TransactionReceipt,
  _from: string,
): { amountUsd: number } | null {
  for (const log of receipt.logs) {
    // Must be from USDC contract
    if (log.address.toLowerCase() !== config.usdcAddress.toLowerCase()) continue;
    // Must be a Transfer event
    if (log.topics[0] !== TRANSFER_TOPIC) continue;
    // Topic 2 (index 1) = `to` address (padded to 32 bytes)
    if (log.topics.length < 3) continue;
    const to = ethers.getAddress('0x' + log.topics[2].slice(26));
    if (to.toLowerCase() !== config.walletAddress.toLowerCase()) continue;

    // Decode the value (USDC has 6 decimals)
    const value = BigInt(log.data);
    const amountUsd = Number(value) / 1e6;
    return { amountUsd };
  }
  return null;
}

// --- Legacy: keep verifyEthPayment for backwards compatibility ---

export async function verifyEthPayment(
  txHash: string,
  expectedAmountUsd: number,
): Promise<{ valid: boolean; amountEth: number; from: string; error?: string }> {
  const result = await verifyOnchainPayment(txHash, expectedAmountUsd);
  return {
    valid: result.valid,
    amountEth: result.token === 'ETH' ? result.amountUsd / (await getEthPrice()) : 0,
    from: result.from,
    error: result.error,
  };
}

// --- ETH price ---

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

// --- Balance checks ---

export async function getUsdcBalance(): Promise<number> {
  try {
    const balance = await usdcContract.balanceOf(config.walletAddress);
    return parseFloat(ethers.formatUnits(balance, 6));
  } catch {
    return 0;
  }
}

export async function getEthBalance(): Promise<number> {
  try {
    const balance = await provider.getBalance(config.walletAddress);
    return parseFloat(ethers.formatEther(balance));
  } catch {
    return 0;
  }
}

// --- Payment result types ---

export interface PaymentResult {
  method: PaymentMethod;
  walletAddress: string;
  amountUsd: number;
  txHash?: string;
}

export function extractWalletFromHeaders(headers: Record<string, string | string[] | undefined>): string | null {
  const wallet = headers['x-wallet-address'] || headers['x-payer-address'];
  if (typeof wallet === 'string' && ethers.isAddress(wallet)) return wallet;
  return null;
}
