/**
 * Price feed configuration for on-chain native token price fetching
 * Uses Uniswap V2-style DEX pools to calculate price from reserves
 * Ported from explorer: src/config/priceFeeds.ts
 */

/**
 * @typedef {Object} PricePoolConfig
 * @property {string} poolAddress
 * @property {number} stablecoinDecimals
 * @property {number} nativeTokenDecimals
 * @property {boolean} isToken0Native - Is wrapped native token token0 in the pair?
 * @property {string} name
 */

/** @type {Record<number, PricePoolConfig[]>} */
export const PRICE_POOLS = {
  // Ethereum Mainnet
  1: [
    {
      poolAddress: "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc", // USDC/WETH Uniswap V2
      stablecoinDecimals: 6,
      nativeTokenDecimals: 18,
      isToken0Native: false, // USDC is token0, WETH is token1
      name: "Uniswap V2 USDC/WETH",
    },
    {
      poolAddress: "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", // WETH/USDT Uniswap V2
      stablecoinDecimals: 6,
      nativeTokenDecimals: 18,
      isToken0Native: true, // WETH is token0, USDT is token1
      name: "Uniswap V2 WETH/USDT",
    },
  ],

  // Polygon
  137: [
    {
      poolAddress: "0x6e7a5FAFcec6BB1e78bAE2A1F0B612012BF14827", // WMATIC/USDC QuickSwap
      stablecoinDecimals: 6,
      nativeTokenDecimals: 18,
      isToken0Native: true,
      name: "QuickSwap WMATIC/USDC",
    },
  ],

  // BNB Chain
  56: [
    {
      poolAddress: "0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE", // USDT/WBNB PancakeSwap V2
      stablecoinDecimals: 18, // BSC-USD (USDT) has 18 decimals on BNB
      nativeTokenDecimals: 18,
      isToken0Native: false, // USDT is token0, WBNB is token1
      name: "PancakeSwap V2 USDT/WBNB",
    },
  ],
};

// Chain IDs that use ETH as native token (L2s) → price fetched from mainnet
export const ETH_NATIVE_CHAINS = new Set([
  42161, // Arbitrum
  10,    // Optimism
  8453,  // Base
  11155111, // Sepolia
]);

/** WBTC/stablecoin pools on Ethereum mainnet (WBTC = 8 decimals) */
export const WBTC_POOLS = [
  {
    poolAddress: "0x004375Dff511095CC5A197A54140a24eFEF3A416", // WBTC/USDC Uniswap V2
    stablecoinDecimals: 6,
    nativeTokenDecimals: 8,
    isToken0Native: true,
    name: "Uniswap V2 WBTC/USDC",
  },
  {
    poolAddress: "0x0de845955E2bF089012F682fE9bC81dD5f11B372", // WBTC/USDT Uniswap V2
    stablecoinDecimals: 6,
    nativeTokenDecimals: 8,
    isToken0Native: true,
    name: "Uniswap V2 WBTC/USDT",
  },
];

export function getPricePoolsForNetwork(chainId) {
  return PRICE_POOLS[chainId] || [];
}

export function getWBTCPools() {
  return WBTC_POOLS;
}

export function hasPriceFeeds(chainId) {
  const pools = PRICE_POOLS[chainId];
  return pools !== undefined && pools.length > 0;
}
