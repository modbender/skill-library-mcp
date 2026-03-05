// Shared config for GhostBot Sepolia scripts
import { createPublicClient, createWalletClient, http, formatEther, parseEther, keccak256, encodeAbiParameters } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { sepolia } from "viem/chains";

// Deployed contract addresses on Sepolia
export const CONTRACTS = {
  oracle: "0x300Fa0Af86201A410bEBD511Ca7FB81548a0f027",
  hook: "0xbD2802B7215530894d5696ab8450115f56b1fAC0",
  poolManager: "0xE03A1074c86CFeDd5C142C4F04F1a1536e203543",
  currency0: "0x07B55AfA83169093276898f789A27a4e2d511F36", // GBB (sorted lower)
  currency1: "0xB960eD7FC078037608615a0b62a1a0295493f26E", // GBA (sorted higher)
};

// Pool config
export const POOL_CONFIG = {
  fee: 0x800000, // DYNAMIC_FEE_FLAG
  tickSpacing: 60,
};

const RPC_URL = process.env.RPC_URL || "https://eth-sepolia.g.alchemy.com/v2/3TD4Qp-ol2qGp69d3LBv3lBWlHrvaynY";
const PRIVATE_KEY = process.env.DEPLOYER_PRIVATE_KEY || "0x47f30914312ed58125bfa35b836e5787e5829a7e7db7abd146625b4b15ca6d9e";

export const account = privateKeyToAccount(PRIVATE_KEY);

export const publicClient = createPublicClient({
  chain: sepolia,
  transport: http(RPC_URL),
});

export const walletClient = createWalletClient({
  account,
  chain: sepolia,
  transport: http(RPC_URL),
});

export { formatEther, parseEther };

// Compute pool ID from pool key
export function computePoolId() {
  return keccak256(
    encodeAbiParameters(
      [
        { type: "address" },
        { type: "address" },
        { type: "uint24" },
        { type: "int24" },
        { type: "address" },
      ],
      [CONTRACTS.currency0, CONTRACTS.currency1, POOL_CONFIG.fee, POOL_CONFIG.tickSpacing, CONTRACTS.hook]
    )
  );
}

// Minimal ERC20 ABI
export const ERC20_ABI = [
  { type: "function", name: "name", inputs: [], outputs: [{ type: "string" }], stateMutability: "view" },
  { type: "function", name: "symbol", inputs: [], outputs: [{ type: "string" }], stateMutability: "view" },
  { type: "function", name: "balanceOf", inputs: [{ name: "account", type: "address" }], outputs: [{ type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "allowance", inputs: [{ name: "owner", type: "address" }, { name: "spender", type: "address" }], outputs: [{ type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "approve", inputs: [{ name: "spender", type: "address" }, { name: "amount", type: "uint256" }], outputs: [{ type: "bool" }], stateMutability: "nonpayable" },
  { type: "function", name: "mint", inputs: [{ name: "to", type: "address" }, { name: "amount", type: "uint256" }], outputs: [], stateMutability: "nonpayable" },
];

// Oracle ABI
export const ORACLE_ABI = [
  { type: "function", name: "owner", inputs: [], outputs: [{ type: "address" }], stateMutability: "view" },
  { type: "function", name: "bot", inputs: [], outputs: [{ type: "address" }], stateMutability: "view" },
  { type: "function", name: "hook", inputs: [], outputs: [{ type: "address" }], stateMutability: "view" },
  { type: "function", name: "signalTTL", inputs: [], outputs: [{ type: "uint256" }], stateMutability: "view" },
  {
    type: "function", name: "getPositionsNeedingRebalance",
    inputs: [{ name: "poolId", type: "bytes32" }],
    outputs: [{
      name: "", type: "tuple[]",
      components: [
        { name: "positionId", type: "uint256" },
        { name: "newTickLower", type: "int24" },
        { name: "newTickUpper", type: "int24" },
        { name: "confidence", type: "uint8" },
        { name: "timestamp", type: "uint256" },
      ],
    }],
    stateMutability: "view",
  },
  {
    type: "function", name: "getDynamicFee",
    inputs: [{ name: "poolId", type: "bytes32" }],
    outputs: [{ name: "fee", type: "uint24" }, { name: "confidence", type: "uint8" }],
    stateMutability: "view",
  },
  {
    type: "function", name: "postRebalanceSignal",
    inputs: [
      { name: "poolId", type: "bytes32" },
      { name: "signal", type: "tuple", components: [
        { name: "positionId", type: "uint256" },
        { name: "newTickLower", type: "int24" },
        { name: "newTickUpper", type: "int24" },
        { name: "confidence", type: "uint8" },
        { name: "timestamp", type: "uint256" },
      ]},
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function", name: "postFeeRecommendation",
    inputs: [
      { name: "poolId", type: "bytes32" },
      { name: "rec", type: "tuple", components: [
        { name: "fee", type: "uint24" },
        { name: "confidence", type: "uint8" },
        { name: "timestamp", type: "uint256" },
      ]},
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
];

// Hook ABI
export const HOOK_ABI = [
  { type: "function", name: "owner", inputs: [], outputs: [{ type: "address" }], stateMutability: "view" },
  { type: "function", name: "paused", inputs: [], outputs: [{ type: "bool" }], stateMutability: "view" },
  { type: "function", name: "minConfidence", inputs: [], outputs: [{ type: "uint8" }], stateMutability: "view" },
  { type: "function", name: "rebalanceCooldown", inputs: [], outputs: [{ type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "positionCounter", inputs: [], outputs: [{ type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "orderCounter", inputs: [], outputs: [{ type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "oracle", inputs: [], outputs: [{ type: "address" }], stateMutability: "view" },
  {
    type: "function", name: "poolKey", inputs: [],
    outputs: [{ name: "", type: "tuple", components: [
      { name: "currency0", type: "address" },
      { name: "currency1", type: "address" },
      { name: "fee", type: "uint24" },
      { name: "tickSpacing", type: "int24" },
      { name: "hooks", type: "address" },
    ]}],
    stateMutability: "view",
  },
  {
    type: "function", name: "getUserPositions",
    inputs: [{ name: "user", type: "address" }],
    outputs: [{ name: "", type: "uint256[]" }],
    stateMutability: "view",
  },
  {
    type: "function", name: "getPosition",
    inputs: [{ name: "positionId", type: "uint256" }],
    outputs: [{ name: "", type: "tuple", components: [
      { name: "owner", type: "address" },
      { name: "tickLower", type: "int24" },
      { name: "tickUpper", type: "int24" },
      { name: "liquidity", type: "uint128" },
      { name: "autoRebalance", type: "bool" },
      { name: "lastRebalanceTime", type: "uint256" },
      { name: "salt", type: "bytes32" },
    ]}],
    stateMutability: "view",
  },
  {
    type: "function", name: "getPoolStats",
    inputs: [{ name: "poolId", type: "bytes32" }],
    outputs: [{ name: "", type: "tuple", components: [
      { name: "cumulativeVolume", type: "uint256" },
      { name: "lastVolumeUpdate", type: "uint256" },
      { name: "volatility", type: "uint256" },
      { name: "currentFee", type: "uint24" },
      { name: "lastTick", type: "int24" },
    ]}],
    stateMutability: "view",
  },
  {
    type: "function", name: "addLiquidity",
    inputs: [{ name: "params", type: "tuple", components: [
      { name: "amount0Desired", type: "uint256" },
      { name: "amount1Desired", type: "uint256" },
      { name: "amount0Min", type: "uint256" },
      { name: "amount1Min", type: "uint256" },
      { name: "deadline", type: "uint256" },
      { name: "tickLower", type: "int24" },
      { name: "tickUpper", type: "int24" },
      { name: "userInputSalt", type: "bytes32" },
    ]}],
    outputs: [{ name: "delta", type: "int256" }],
    stateMutability: "payable",
  },
  {
    type: "function", name: "removeLiquidity",
    inputs: [{ name: "params", type: "tuple", components: [
      { name: "positionId", type: "uint256" },
      { name: "liquidity", type: "uint128" },
      { name: "amount0Min", type: "uint256" },
      { name: "amount1Min", type: "uint256" },
      { name: "deadline", type: "uint256" },
    ]}],
    outputs: [{ name: "delta", type: "int256" }],
    stateMutability: "nonpayable",
  },
  {
    type: "function", name: "getUserLimitOrders",
    inputs: [{ name: "user", type: "address" }],
    outputs: [{ name: "", type: "uint256[]" }],
    stateMutability: "view",
  },
  {
    type: "function", name: "getLimitOrder",
    inputs: [{ name: "orderId", type: "uint256" }],
    outputs: [{ name: "", type: "tuple", components: [
      { name: "owner", type: "address" },
      { name: "zeroForOne", type: "bool" },
      { name: "triggerTick", type: "int24" },
      { name: "amountIn", type: "uint128" },
      { name: "amountOutMin", type: "uint128" },
      { name: "orderType", type: "uint8" },
      { name: "linkedPositionId", type: "uint256" },
      { name: "executed", type: "bool" },
      { name: "cancelled", type: "bool" },
      { name: "claimCurrency", type: "address" },
      { name: "claimAmount", type: "uint256" },
    ]}],
    stateMutability: "view",
  },
];
