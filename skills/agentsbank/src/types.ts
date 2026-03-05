/**
 * AgentsBank SDK Types
 * TypeScript definitions for the AgentsBank API
 */

// ============================================
// CONFIGURATION
// ============================================

export interface RetryConfig {
  /** Maximum retry attempts for transient failures */
  maxAttempts?: number;
  /** Initial delay in milliseconds */
  initialDelayMs?: number;
  /** Maximum delay in milliseconds */
  maxDelayMs?: number;
}

export interface CacheConfig {
  /** Enable response caching */
  enabled?: boolean;
  /** Use Redis for caching (default: fallback to in-memory) */
  useRedis?: boolean;
}

export interface GuardrailsConfig {
  /** Daily spending limit in USD */
  dailyLimitUSD?: number;
  /** Maximum per-transaction limit in USD */
  maxPerTxUSD?: number;
  /** List of whitelisted recipient addresses */
  whitelistedAddresses?: string[];
  /** List of blacklisted recipient addresses */
  blacklistedAddresses?: string[];
  /** Max transactions per hour */
  maxTxPerHour?: number;
  /** Max unique recipients per day */
  maxRecipientsPerDay?: number;
}

export interface WebhookConfig {
  /** Webhook URL for event notifications */
  url?: string;
  /** Secret for HMAC-SHA256 signing */
  secret?: string;
  /** Events to subscribe to */
  events?: WebhookEvent[];
}

export type WebhookEvent =
  | 'transaction.sent'
  | 'transaction.received'
  | 'transaction.confirmed'
  | 'wallet.created'
  | 'balance.changed'
  | 'error.occurred'
  | 'agent.login';

export interface AgentsBankConfig {
  /** Base URL of the AgentsBank API */
  baseUrl?: string;
  /** API key for authentication (alternative to JWT) */
  apiKey?: string;
  /** JWT token for authentication */
  token?: string;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Custom fetch implementation */
  fetch?: typeof fetch;
  /** Retry configuration for transient failures */
  retryConfig?: RetryConfig;
  /** Cache configuration */
  cacheConfig?: CacheConfig;
  /** Guardrails for spending limits and restrictions */
  guardrails?: GuardrailsConfig;
  /** Webhook configuration for events */
  webhooks?: WebhookConfig;
}

// ============================================
// AUTHENTICATION
// ============================================

export interface RegisterAgentRequest {
  /** Human's username */
  human_username: string;
  /** Human's email */
  human_email: string;
  /** Agent owner's first name */
  first_name: string;
  /** Agent owner's last name */
  last_name: string;
  /** Password for agent (min 8 chars, uppercase, number, special char) */
  agent_password: string;
  /** Optional agent capabilities */
  capabilities?: string[];
  /** Optional agent description */
  description?: string;
}

export interface RegisterAgentResponse {
  agent_id: string;
  agent_username: string;
  api_key: string;
  did: string;
  token: string;
  recovery_words: string[];
  wallets: WalletInfo[];
  message: string;
}

export interface LoginRequest {
  agent_username: string;
  agent_password: string;
}

export interface LoginResponse {
  agent_id: string;
  token: string;
}

// ============================================
// WALLETS
// ============================================

export type Chain = 'ethereum' | 'bsc' | 'solana' | 'bitcoin';
export type Currency = 'ETH' | 'BNB' | 'SOL' | 'BTC' | 'USDT' | 'USDC';

export interface WalletInfo {
  wallet_id: string;
  agent_id: string;
  chain: Chain;
  address: string;
  type: 'custodial';
  balance?: WalletBalance;
  created_at: string;
}

export interface WalletBalance {
  [currency: string]: string;
}

export interface CreateWalletRequest {
  chain: Chain;
}

export interface CreateWalletResponse extends WalletInfo {}

export interface GetBalanceResponse {
  wallet_id: string;
  chain: Chain;
  address: string;
  balance: WalletBalance;
}

// ============================================
// TRANSACTIONS
// ============================================

export interface SendTransactionRequest {
  /** Recipient address */
  to_address: string;
  /** Amount to send (as string for precision) */
  amount: string;
  /** Optional: currency (defaults to native token) */
  currency?: Currency;
}

export interface SendTransactionResponse {
  tx_hash: string;
  status: TransactionStatus;
  from_address: string;
  to_address: string;
  amount: string;
  chain: Chain;
}

export type TransactionStatus = 'pending' | 'confirmed' | 'failed';

export interface Transaction {
  tx_id: string;
  wallet_id: string;
  chain: Chain;
  type: TransactionType;
  from_address: string;
  to_address: string;
  amount: string;
  currency: Currency;
  tx_hash: string;
  status: TransactionStatus;
  chain_fee?: string;
  chain_fee_usd?: string;
  bank_fee?: string;
  bank_fee_usd?: string;
  total_fee?: string;
  total_fee_usd?: string;
  timestamp: string;
}

export type TransactionType = 
  | 'deposit' 
  | 'transfer' 
  | 'swap' 
  | 'stake' 
  | 'unstake' 
  | 'withdraw';

export interface TransactionHistoryResponse {
  wallet_id: string;
  transactions: Transaction[];
}

// ============================================
// SIGNING
// ============================================

export interface SignMessageRequest {
  message: string;
}

export interface SignMessageResponse {
  wallet_id: string;
  address: string;
  message: string;
  signature: string;
}

// ============================================
// GAS ESTIMATION
// ============================================

export interface EstimateGasRequest {
  to_address: string;
  amount: string;
}

export interface EstimateGasResponse {
  chain: Chain;
  to_address: string;
  amount: string;
  estimated_gas: string;
}

// ============================================
// HELPER METHODS
// ============================================

export interface SendSafeRequest extends SendTransactionRequest {
  /** Optional: max acceptable gas fee in USD */
  maxGasUSD?: number;
}

export interface SendMultipleRequest {
  /** Array of recipients and amounts */
  recipients: Array<{
    to_address: string;
    amount: string;
    currency?: Currency;
  }>;
}

export interface SendMultipleResponse {
  results: SendTransactionResponse[];
  totalAmount: string;
  totalFees: string;
  timestamp: string;
}

export interface BalanceCheckResponse {
  has_enough_funds: boolean;
  current_balance: string;
  required_amount: string;
  currency?: Currency;
}

// ============================================
// CATALOGUE
// ============================================

export interface ChainInfo {
  id: Chain;
  name: string;
  symbol: string;
  nativeToken: Currency;
  decimals: number;
  tokens: Currency[];
  chainId: number | null;
  explorer: string;
}

export interface CatalogueResponse {
  chains: ChainInfo[];
}

// ============================================
// ERRORS
// ============================================

export interface ApiError {
  error: string;
  code?: string;
  details?: Record<string, unknown>;
}

export class AgentsBankError extends Error {
  public readonly code?: string;
  public readonly status: number;
  public readonly details?: Record<string, unknown>;

  constructor(message: string, status: number, code?: string, details?: Record<string, unknown>) {
    super(message);
    this.name = 'AgentsBankError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// ============================================
// FEE INFORMATION
// ============================================

export interface FeeEstimate {
  chain_fee: string;
  chain_fee_usd: string;
  bank_fee: string;
  bank_fee_usd: string;
  total_fee: string;
  total_fee_usd: string;
}

export interface FeeInfo {
  base_percentage: number;
  min_fee_usd: number;
  max_fee_usd: number;
  chain_multipliers: Record<Chain, number>;
}
