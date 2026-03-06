/**
 * PRISM OS — Canonical Type Definitions
 * The universal language across all 200+ agent tools
 */

// ─────────────────────────────────────────────
// CANONICAL ASSET — The lock-in schema
// Every tool input/output speaks PRISM-IDs
// ─────────────────────────────────────────────

export type AssetCategory =
  | 'L1'
  | 'L2'
  | 'DeFi'
  | 'Meme'
  | 'RWA'
  | 'LST'         // Liquid Staking Token
  | 'LRT'         // Liquid Restaking Token
  | 'Stablecoin'
  | 'NFT'
  | 'GameFi'
  | 'AI'
  | 'Perp'
  | 'Index'
  | 'Unknown';

export type ChainId =
  | 'ethereum'
  | 'solana'
  | 'arbitrum'
  | 'optimism'
  | 'base'
  | 'polygon'
  | 'bsc'
  | 'avalanche'
  | 'sui'
  | 'aptos'
  | 'ton'
  | 'cosmos'
  | string;      // extensible

export type VenueId =
  | 'binance'
  | 'bybit'
  | 'okx'
  | 'coinbase'
  | 'kraken'
  | 'hyperliquid'
  | 'dydx'
  | 'uniswap'
  | 'jupiter'
  | 'orca'
  | 'raydium'
  | 'curve'
  | 'balancer'
  | 'aerodrome'
  | string;

export interface ContractInfo {
  address: string;
  decimals: number;
  verified: boolean;
  isProxy?: boolean;
  implementation?: string;
}

export interface CanonicalAsset {
  // Core identity
  prismId: string;                          // e.g. "prism:ethereum:eth"
  name: string;                             // "Ethereum"
  symbol: string;                           // "ETH"
  category: AssetCategory;
  tags: string[];                           // ['store-of-value', 'pos', 'evm']

  // Cross-chain presence
  chains: ChainId[];
  contracts: Record<ChainId, ContractInfo>; // chain → contract info
  primaryChain: ChainId;

  // Related assets
  wrappedVersions: string[];                // other PRISM-IDs
  syntheticVersions: string[];
  bridgedVersions: string[];
  relatedAssets: string[];                  // correlated assets

  // Availability
  cexListings: VenueId[];
  dexListings: Array<{ venue: VenueId; chain: ChainId; pool: string }>;

  // Metadata
  coingeckoId?: string;
  coinmarketcapId?: string;
  defilllamaSlug?: string;
  logoUrl?: string;
  website?: string;
  twitter?: string;
  github?: string;

  // Risk signals
  auditStatus?: 'audited' | 'unaudited' | 'partial';
  rugScore?: number;                        // 0-100, higher = riskier

  // Timestamps
  createdAt: string;
  updatedAt: string;
}

// ─────────────────────────────────────────────
// MARKET TYPES
// ─────────────────────────────────────────────

export interface PriceData {
  prismId: string;
  price: number;
  priceUsd: number;
  priceBtc?: number;
  change1h?: number;
  change24h?: number;
  change7d?: number;
  volume24h: number;
  marketCap?: number;
  timestamp: number;
  sources: string[];
  confidence: 'high' | 'medium' | 'low';
}

export interface OHLCVCandle {
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  timestamp: number;
}

export interface OrderBook {
  bids: [price: number, size: number][];
  asks: [price: number, size: number][];
  timestamp: number;
  exchange: VenueId;
}

export interface FundingRate {
  rate: number;
  nextFunding: number;
  interval: string;
  exchange: VenueId;
  timestamp: number;
}

// ─────────────────────────────────────────────
// DEX / EXECUTION TYPES
// ─────────────────────────────────────────────

export interface SwapQuote {
  fromAsset: string;
  toAsset: string;
  fromAmount: string;
  toAmount: string;
  expectedOutput: string;
  minimumOutput: string;
  slippage: number;
  priceImpact: number;
  route: SwapRoute[];
  estimatedGas: string;
  gasUsd: number;
  venue: VenueId;
  chain: ChainId;
  validUntil: number;
  quoteId: string;
}

export interface SwapRoute {
  protocol: string;
  pool: string;
  fromAsset: string;
  toAsset: string;
  share: number;
}

export interface PoolData {
  address: string;
  chain: ChainId;
  protocol: VenueId;
  token0: string;
  token1: string;
  tvl: number;
  volume24h: number;
  fees24h: number;
  feeApy: number;
  totalApy?: number;
  reserves: { token0: string; token1: string };
  createdAt?: number;
}

// ─────────────────────────────────────────────
// PORTFOLIO TYPES
// ─────────────────────────────────────────────

export interface TokenBalance {
  prismId: string;
  symbol: string;
  balance: string;
  balanceUsd: number;
  chain: ChainId;
  contract?: string;
}

export interface Position {
  prismId: string;
  symbol: string;
  size: string;
  sizeUsd: number;
  entryPrice?: number;
  currentPrice: number;
  unrealizedPnl: number;
  unrealizedPnlPct: number;
  chain?: ChainId;
  venue?: VenueId;
  type: 'spot' | 'perp' | 'option' | 'lp';
}

export interface PnLSummary {
  totalValue: number;
  totalCostBasis: number;
  unrealizedPnl: number;
  unrealizedPnlPct: number;
  realizedPnl: number;
  totalPnl: number;
  window: string;
  timestamp: number;
}

// ─────────────────────────────────────────────
// RISK TYPES
// ─────────────────────────────────────────────

export interface TokenRiskScore {
  prismId: string;
  overallScore: number;      // 0-100, higher = riskier
  rugScore: number;
  honeypotRisk: boolean;
  liquidityRisk: 'low' | 'medium' | 'high';
  ownershipRisk: 'renounced' | 'multisig' | 'eoa' | 'unknown';
  holderConcentration: number;
  auditCount: number;
  flags: string[];
  timestamp: number;
}

export interface TxSimulation {
  success: boolean;
  gasUsed: string;
  gasEstimate: string;
  stateChanges: StateChange[];
  events: string[];
  revertReason?: string;
  mevRisk: 'none' | 'low' | 'medium' | 'high';
}

export interface StateChange {
  type: 'transfer' | 'approval' | 'mint' | 'burn';
  asset: string;
  from: string;
  to: string;
  amount: string;
}

// ─────────────────────────────────────────────
// PREDICTION MARKET TYPES
// ─────────────────────────────────────────────

export interface PredictionMarket {
  marketId: string;
  platform: 'polymarket' | 'kalshi' | 'manifold' | 'drift';
  title: string;
  description: string;
  category: string;
  relatedAssets?: string[];
  yesPrice: number;
  noPrice: number;
  volume24h: number;
  totalVolume: number;
  liquidity: number;
  expiresAt: string;
  status: 'open' | 'closed' | 'resolved';
  resolution?: boolean;
}

// ─────────────────────────────────────────────
// SIGNAL TYPES
// ─────────────────────────────────────────────

export interface SentimentScore {
  prismId: string;
  score: number;           // -100 to 100
  magnitude: number;       // 0 to 100 (strength)
  socialVolume: number;
  sources: { twitter: number; reddit: number; news: number };
  window: string;
  timestamp: number;
}

export interface TechnicalIndicator {
  name: string;
  value: number | number[];
  signal: 'buy' | 'sell' | 'neutral';
  strength: number;         // 0-100
  timestamp: number;
}

export interface OnChainSignal {
  prismId: string;
  type: 'whale_buy' | 'whale_sell' | 'exchange_inflow' | 'exchange_outflow' | 'dev_activity' | 'unlock';
  magnitude: number;
  details: Record<string, unknown>;
  timestamp: number;
}

// ─────────────────────────────────────────────
// AGENT EXECUTION TYPES
// ─────────────────────────────────────────────

export type OrderSide = 'buy' | 'sell';
export type OrderType = 'market' | 'limit' | 'stop' | 'stop_limit';

export interface OrderParams {
  prismId: string;
  side: OrderSide;
  type: OrderType;
  amount: string;
  price?: number;
  stopPrice?: number;
  slippage?: number;
  chain?: ChainId;
  venue: VenueId;
  timeInForce?: 'GTC' | 'IOC' | 'FOK';
}

export interface OrderResult {
  orderId: string;
  status: 'filled' | 'partial' | 'pending' | 'failed';
  filledAmount?: string;
  filledPrice?: number;
  txHash?: string;
  fee?: number;
  timestamp: number;
}

export interface BatchOperation {
  id: string;
  module: string;
  method: string;
  params: Record<string, unknown>;
  dependsOn?: string[];      // operation IDs this depends on
  condition?: string;        // JS expression evaluated at runtime
}

// ─────────────────────────────────────────────
// SDK CONFIG
// ─────────────────────────────────────────────

export interface PrismConfig {
  apiKey: string;
  environment?: 'production' | 'staging' | 'mock';
  defaultChain?: ChainId;
  defaultVenue?: VenueId;
  timeout?: number;
  rateLimit?: number;
  cache?: {
    enabled: boolean;
    ttl: number;            // seconds
  };
  webhookUrl?: string;
}
