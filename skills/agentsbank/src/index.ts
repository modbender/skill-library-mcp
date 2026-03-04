/**
 * AgentsBank SDK
 * Official TypeScript/JavaScript SDK for AgentsBank.ai
 * 
 * @packageDocumentation
 */

// Main client
export { AgentsBank, createClient } from './client.js';

// Types
export type {
  // Config
  AgentsBankConfig,
  RetryConfig,
  CacheConfig,
  GuardrailsConfig,
  WebhookConfig,
  WebhookEvent,
  
  // Auth
  RegisterAgentRequest,
  RegisterAgentResponse,
  LoginRequest,
  LoginResponse,
  
  // Wallets
  Chain,
  Currency,
  WalletInfo,
  WalletBalance,
  CreateWalletRequest,
  CreateWalletResponse,
  GetBalanceResponse,
  
  // Transactions
  SendTransactionRequest,
  SendTransactionResponse,
  Transaction,
  TransactionStatus,
  TransactionType,
  TransactionHistoryResponse,
  
  // Signing
  SignMessageRequest,
  SignMessageResponse,
  
  // Gas
  EstimateGasRequest,
  EstimateGasResponse,
  
  // Helper Methods
  SendSafeRequest,
  SendMultipleRequest,
  SendMultipleResponse,
  BalanceCheckResponse,
  
  // Catalogue
  ChainInfo,
  CatalogueResponse,
  
  // Fees
  FeeEstimate,
  FeeInfo,
  
  // Errors
  ApiError,
} from './types.js';

// Error classes
export { AgentsBankError, ErrorCode, createError, errorCodeFromStatus } from './errors.js';
export type { } from './errors.js';

// Version
export const VERSION = '1.0.5';

// Supported chains constant
export const SUPPORTED_CHAINS: readonly string[] = [
  'ethereum',
  'bsc', 
  'solana',
  'bitcoin'
] as const;

// Supported currencies constant
export const SUPPORTED_CURRENCIES: readonly string[] = [
  'ETH',
  'BNB',
  'SOL', 
  'BTC',
  'USDT',
  'USDC'
] as const;
