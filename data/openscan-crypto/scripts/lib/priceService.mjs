/**
 * On-chain price service — fetches native token prices from DEX pools
 * Uses Uniswap V2 getReserves() to calculate prices. No external APIs.
 * Ported from explorer: src/services/PriceService.ts
 */

import { getPricePoolsForNetwork, getWBTCPools, ETH_NATIVE_CHAINS } from "./priceFeeds.mjs";

const MAINNET_CHAIN_ID = 1;
const GET_RESERVES_SELECTOR = "0x0902f1ac";

/**
 * Decode getReserves() return data
 * Returns: (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)
 */
function decodeReserves(data) {
  if (!data || data === "0x" || data.length < 194) return null;
  const hex = data.slice(2);
  return {
    reserve0: BigInt(`0x${hex.slice(0, 64)}`),
    reserve1: BigInt(`0x${hex.slice(64, 128)}`),
  };
}

/**
 * Calculate price from pool reserves
 */
function calculatePriceFromReserves(reserves, config) {
  const { reserve0, reserve1 } = reserves;
  if (reserve0 === 0n || reserve1 === 0n) return null;

  const nativeReserve = config.isToken0Native ? reserve0 : reserve1;
  const stableReserve = config.isToken0Native ? reserve1 : reserve0;
  const decimalsDiff = config.nativeTokenDecimals - config.stablecoinDecimals;

  if (decimalsDiff >= 0) {
    const adjustedStable = stableReserve * BigInt(10 ** decimalsDiff);
    return Number(adjustedStable) / Number(nativeReserve);
  }
  const adjustedNative = nativeReserve * BigInt(10 ** -decimalsDiff);
  return Number(stableReserve) / Number(adjustedNative);
}

/**
 * Fetch price from a single pool via raw RPC call
 */
async function fetchPriceFromPool(rpcUrl, config) {
  try {
    const response = await fetch(rpcUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "eth_call",
        params: [{ to: config.poolAddress, data: GET_RESERVES_SELECTOR }, "latest"],
        id: 1,
      }),
      signal: AbortSignal.timeout(10000),
    });
    const data = await response.json();
    if (data.error || !data.result) return null;
    const reserves = decodeReserves(data.result);
    if (!reserves) return null;
    return calculatePriceFromReserves(reserves, config);
  } catch {
    return null;
  }
}

/**
 * Median of an array of numbers
 */
function median(values) {
  if (values.length === 0) return 0;
  if (values.length === 1) return values[0];
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0
    ? (sorted[mid - 1] + sorted[mid]) / 2
    : sorted[mid];
}

/**
 * Fetch native token price for a network.
 * Returns { price, pools } with per-pool detail.
 * 
 * @param {number} chainId
 * @param {string} rpcUrl - Primary RPC URL for the target chain
 * @param {string} [mainnetRpcUrl] - Mainnet RPC for L2 ETH price lookups
 * @returns {{ price: number|null, pools: Array<{name: string, price: number|null}> }}
 */
export async function getNativeTokenPrice(chainId, rpcUrl, mainnetRpcUrl) {
  const useMainnet = ETH_NATIVE_CHAINS.has(chainId);
  const targetChainId = useMainnet ? MAINNET_CHAIN_ID : chainId;
  const targetRpcUrl = useMainnet && mainnetRpcUrl ? mainnetRpcUrl : rpcUrl;

  const pools = getPricePoolsForNetwork(targetChainId);
  if (pools.length === 0) return { price: null, pools: [] };

  const results = await Promise.all(
    pools.map(async (pool) => {
      const price = await fetchPriceFromPool(targetRpcUrl, pool);
      return { name: pool.name, price };
    })
  );

  const validPrices = results.filter(r => r.price !== null && r.price > 0).map(r => r.price);
  const price = validPrices.length > 0 ? median(validPrices) : null;

  return { price, pools: results };
}

/**
 * Fetch BTC price from WBTC/stablecoin pools on Ethereum mainnet
 */
export async function getBTCPrice(mainnetRpcUrl) {
  const pools = getWBTCPools();
  if (pools.length === 0) return { price: null, pools: [] };

  const results = await Promise.all(
    pools.map(async (pool) => {
      const price = await fetchPriceFromPool(mainnetRpcUrl, pool);
      return { name: pool.name, price };
    })
  );

  const validPrices = results.filter(r => r.price !== null && r.price > 0).map(r => r.price);
  const price = validPrices.length > 0 ? median(validPrices) : null;

  return { price, pools: results };
}

/**
 * Format price for display
 */
export function formatPrice(price) {
  if (price === null) return "—";
  if (price >= 1000) return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (price >= 1) return `$${price.toFixed(2)}`;
  return `$${price.toPrecision(4)}`;
}
