/**
 * Type definitions for Arkade SDK skills.
 *
 * These types define the interfaces for Bitcoin and Lightning skills
 * designed for agent integration.
 *
 * @module skills/types
 */

import type { ArkTransaction, SettlementEvent, FeeInfo } from "@arkade-os/sdk";

/**
 * Base interface for all skills.
 * Skills are modular capabilities that can be added to wallets.
 */
export interface Skill {
  /** Unique identifier for the skill */
  readonly name: string;
  /** Human-readable description of the skill's capabilities */
  readonly description: string;
  /** Version of the skill implementation */
  readonly version: string;
}

/**
 * Represents a Bitcoin address with its type and purpose.
 */
export interface BitcoinAddress {
  /** The encoded address string */
  address: string;
  /** Type of address */
  type: "ark" | "boarding" | "onchain";
  /** Description of the address purpose */
  description: string;
}

/**
 * Parameters for sending Bitcoin.
 */
export interface SendParams {
  /** Destination address (Ark address for offchain, Bitcoin address for onchain) */
  address: string;
  /** Amount in satoshis */
  amount: number;
  /** Optional fee rate in sat/vB */
  feeRate?: number;
  /** Optional memo for the transaction */
  memo?: string;
}

/**
 * Parameters for onboarding Bitcoin from onchain to offchain (Ark).
 */
export interface OnboardParams {
  /** Fee information for the settlement */
  feeInfo: FeeInfo;
  /** Optional specific amount to onboard (defaults to all available) */
  amount?: bigint;
  /** Optional callback for settlement events */
  eventCallback?: (event: SettlementEvent) => void;
}

/**
 * Parameters for offboarding Bitcoin from offchain (Ark) to onchain.
 */
export interface OffboardParams {
  /** Destination onchain Bitcoin address */
  destinationAddress: string;
  /** Fee information for the settlement */
  feeInfo: FeeInfo;
  /** Optional specific amount to offboard (defaults to all available) */
  amount?: bigint;
  /** Optional callback for settlement events */
  eventCallback?: (event: SettlementEvent) => void;
}

/**
 * Result of a send operation.
 */
export interface SendResult {
  /** Transaction identifier */
  txid: string;
  /** Type of transaction */
  type: "ark" | "onchain" | "lightning";
  /** Amount sent in satoshis */
  amount: number;
  /** Fee paid in satoshis (if known) */
  fee?: number;
}

/**
 * Result of an onboard/offboard operation.
 */
export interface RampResult {
  /** Commitment transaction ID */
  commitmentTxid: string;
  /** Amount moved in satoshis */
  amount: bigint;
}

/**
 * Balance information with breakdown by type.
 */
export interface BalanceInfo {
  /** Total available balance in satoshis */
  total: number;
  /** Offchain (Ark) balance breakdown */
  offchain: {
    /** Settled VTXOs */
    settled: number;
    /** Pending VTXOs awaiting confirmation */
    preconfirmed: number;
    /** Total offchain available */
    available: number;
    /** Recoverable funds (swept or subdust) */
    recoverable: number;
  };
  /** Onchain balance breakdown */
  onchain: {
    /** Confirmed boarding UTXOs */
    confirmed: number;
    /** Unconfirmed boarding UTXOs */
    unconfirmed: number;
    /** Total boarding balance */
    total: number;
  };
}

/**
 * Incoming funds notification.
 */
export interface IncomingFundsEvent {
  /** Type of incoming funds */
  type: "utxo" | "vtxo";
  /** Amount received in satoshis */
  amount: number;
  /** Transaction or VTXO IDs */
  ids: string[];
}

/**
 * Interface for Bitcoin skills that can send and receive Bitcoin.
 */
export interface BitcoinSkill extends Skill {
  /**
   * Get addresses for receiving Bitcoin.
   * @returns Array of available addresses with their types
   */
  getReceiveAddresses(): Promise<BitcoinAddress[]>;

  /**
   * Get the primary Ark address for receiving offchain Bitcoin.
   * @returns The Ark address string
   */
  getArkAddress(): Promise<string>;

  /**
   * Get the boarding address for receiving onchain Bitcoin (to be onboarded).
   * @returns The boarding address string
   */
  getBoardingAddress(): Promise<string>;

  /**
   * Get the current balance with breakdown.
   * @returns Balance information
   */
  getBalance(): Promise<BalanceInfo>;

  /**
   * Send Bitcoin to an address.
   * @param params Send parameters
   * @returns Result of the send operation
   */
  send(params: SendParams): Promise<SendResult>;

  /**
   * Get transaction history.
   * @returns Array of transactions
   */
  getTransactionHistory(): Promise<ArkTransaction[]>;

  /**
   * Wait for incoming funds (blocking).
   * @param timeoutMs Optional timeout in milliseconds
   * @returns Information about the incoming funds
   */
  waitForIncomingFunds(timeoutMs?: number): Promise<IncomingFundsEvent>;
}

/**
 * Interface for skills that support on/off ramping between onchain and offchain.
 */
export interface RampSkill extends Skill {
  /**
   * Onboard Bitcoin from onchain to offchain (Ark).
   * @param params Onboard parameters
   * @returns Result of the onboard operation
   */
  onboard(params: OnboardParams): Promise<RampResult>;

  /**
   * Offboard Bitcoin from offchain (Ark) to onchain.
   * @param params Offboard parameters
   * @returns Result of the offboard operation
   */
  offboard(params: OffboardParams): Promise<RampResult>;
}

/**
 * Lightning Network invoice for receiving payments.
 */
export interface LightningInvoice {
  /** BOLT11 encoded invoice string */
  bolt11: string;
  /** Payment hash */
  paymentHash: string;
  /** Amount in satoshis */
  amount: number;
  /** Invoice description */
  description?: string;
  /** Expiry time in seconds */
  expirySeconds: number;
  /** Creation timestamp */
  createdAt: Date;
  /** Preimage (available after payment or when creating) */
  preimage?: string;
}

/**
 * Parameters for creating a Lightning invoice.
 */
export interface CreateInvoiceParams {
  /** Amount in satoshis */
  amount: number;
  /** Invoice description */
  description?: string;
}

/**
 * Parameters for paying a Lightning invoice.
 */
export interface PayInvoiceParams {
  /** BOLT11 encoded invoice string */
  bolt11: string;
}

/**
 * Result of a Lightning payment.
 */
export interface PaymentResult {
  /** Payment preimage (proof of payment) */
  preimage: string;
  /** Amount paid in satoshis */
  amount: number;
  /** Transaction ID (Ark txid for the swap) */
  txid: string;
}

/**
 * Fee information for Lightning swaps.
 */
export interface LightningFees {
  /** Submarine swap fees (send to Lightning) */
  submarine: {
    /** Percentage fee (e.g., 0.01 = 0.01%) */
    percentage: number;
    /** Miner fees in satoshis */
    minerFees: number;
  };
  /** Reverse swap fees (receive from Lightning) */
  reverse: {
    /** Percentage fee (e.g., 0.01 = 0.01%) */
    percentage: number;
    /** Miner fees in satoshis */
    minerFees: {
      lockup: number;
      claim: number;
    };
  };
}

/**
 * Limits for Lightning swaps.
 */
export interface LightningLimits {
  /** Minimum swap amount in satoshis */
  min: number;
  /** Maximum swap amount in satoshis */
  max: number;
}

/**
 * Status of a Lightning swap.
 */
export type SwapStatus =
  | "pending"
  | "invoice.set"
  | "invoice.pending"
  | "invoice.paid"
  | "invoice.settled"
  | "invoice.expired"
  | "invoice.failedToPay"
  | "swap.created"
  | "swap.expired"
  | "transaction.mempool"
  | "transaction.confirmed"
  | "transaction.claimed"
  | "transaction.refunded"
  | "transaction.failed"
  | "transaction.lockupFailed"
  | "transaction.claim.pending";

/**
 * Information about a pending swap.
 */
export interface SwapInfo {
  /** Swap ID */
  id: string;
  /** Swap type */
  type: "submarine" | "reverse";
  /** Current status */
  status: SwapStatus;
  /** Amount in satoshis */
  amount: number;
  /** Creation timestamp */
  createdAt: Date;
  /** Invoice (if applicable) */
  invoice?: string;
}

/**
 * Interface for Lightning Network skills.
 */
export interface LightningSkill extends Skill {
  /**
   * Create a Lightning invoice for receiving payment.
   * Uses Boltz reverse swap to receive Lightning into Arkade.
   * @param params Invoice parameters
   * @returns The created invoice
   */
  createInvoice(params: CreateInvoiceParams): Promise<LightningInvoice>;

  /**
   * Pay a Lightning invoice.
   * Uses Boltz submarine swap to send from Arkade to Lightning.
   * @param params Payment parameters
   * @returns Result of the payment
   */
  payInvoice(params: PayInvoiceParams): Promise<PaymentResult>;

  /**
   * Check if the Lightning skill is available and configured.
   * @returns true if Lightning is available
   */
  isAvailable(): Promise<boolean>;

  /**
   * Get fee information for Lightning swaps.
   * @returns Fee structure for swaps
   */
  getFees(): Promise<LightningFees>;

  /**
   * Get limits for Lightning swaps.
   * @returns Min/max limits for swaps
   */
  getLimits(): Promise<LightningLimits>;

  /**
   * Get pending swaps.
   * @returns Array of pending swap information
   */
  getPendingSwaps(): Promise<SwapInfo[]>;

  /**
   * Get swap history.
   * @returns Array of all swaps (pending and completed)
   */
  getSwapHistory(): Promise<SwapInfo[]>;
}

// =============================================================================
// LendaSwap Types - USDC/USDT Stablecoin Swaps
// =============================================================================

/**
 * Supported EVM chains for stablecoin swaps.
 */
export type EvmChain = "polygon" | "ethereum" | "arbitrum";

/**
 * Supported stablecoin tokens.
 * Format: {asset}_{network}
 */
export type StablecoinToken =
  | "usdc_pol" // USDC on Polygon
  | "usdc_eth" // USDC on Ethereum
  | "usdc_arb" // USDC on Arbitrum
  | "usdt_pol" // USDT on Polygon
  | "usdt_eth" // USDT on Ethereum
  | "usdt_arb"; // USDT on Arbitrum

/**
 * Bitcoin source types for swaps.
 */
export type BtcSource = "btc_arkade" | "btc_lightning" | "btc_onchain";

/**
 * Parameters for swapping BTC to stablecoins.
 */
export interface BtcToStablecoinParams {
  /** EVM address to receive stablecoins */
  targetAddress: string;
  /** Target stablecoin token */
  targetToken: StablecoinToken;
  /** Target EVM chain */
  targetChain: EvmChain;
  /** Amount in satoshis to swap */
  sourceAmount?: number;
  /** Expected target amount (for quotes) */
  targetAmount?: number;
  /** Optional referral code for fee discounts */
  referralCode?: string;
}

/**
 * Parameters for swapping stablecoins to BTC.
 */
export interface StablecoinToBtcParams {
  /** Source EVM chain */
  sourceChain: EvmChain;
  /** Source stablecoin token */
  sourceToken: StablecoinToken;
  /** Amount of stablecoins to swap (use proper decimals, e.g., 6 for USDC) */
  sourceAmount: number;
  /** Arkade address to receive BTC */
  targetAddress: string;
  /** EVM wallet address (for token allowance) */
  userAddress: string;
  /** Optional referral code for fee discounts */
  referralCode?: string;
}

/**
 * Result of a stablecoin swap creation.
 */
export interface StablecoinSwapResult {
  /** Unique swap ID */
  swapId: string;
  /** Swap status */
  status: StablecoinSwapStatus;
  /** Source amount */
  sourceAmount: number;
  /** Target amount (expected) */
  targetAmount: number;
  /** Exchange rate used */
  exchangeRate: number;
  /** Fee information */
  fee: {
    amount: number;
    percentage: number;
  };
  /** Expiry timestamp */
  expiresAt: Date;
  /** Payment details (for funding the swap) */
  paymentDetails?: {
    /** Address to send funds to */
    address: string;
    /** Call data for EVM transactions (if applicable) */
    callData?: string;
  };
  /** Transaction ID of the VHTL funding (for Arkade-to-EVM swaps) */
  fundingTxid?: string;
}

/**
 * Status of a stablecoin swap.
 */
export type StablecoinSwapStatus =
  | "pending"
  | "awaiting_funding"
  | "funded"
  | "processing"
  | "completed"
  | "expired"
  | "refunded"
  | "failed";

/**
 * Information about a stablecoin swap.
 */
export interface StablecoinSwapInfo {
  /** Swap ID */
  id: string;
  /** Swap direction */
  direction: "btc_to_stablecoin" | "stablecoin_to_btc";
  /** Current status */
  status: StablecoinSwapStatus;
  /** Source token/asset */
  sourceToken: string;
  /** Target token/asset */
  targetToken: string;
  /** Source amount */
  sourceAmount: number;
  /** Target amount */
  targetAmount: number;
  /** Exchange rate */
  exchangeRate: number;
  /** Creation timestamp */
  createdAt: Date;
  /** Completion timestamp (if completed) */
  completedAt?: Date;
  /** Transaction ID (if completed) */
  txid?: string;
}

/**
 * Quote for a stablecoin swap.
 */
export interface StablecoinQuote {
  /** Source token */
  sourceToken: string;
  /** Target token */
  targetToken: string;
  /** Source amount */
  sourceAmount: number;
  /** Target amount (after fees) */
  targetAmount: number;
  /** Exchange rate */
  exchangeRate: number;
  /** Fee breakdown */
  fee: {
    amount: number;
    percentage: number;
  };
  /** Quote expiry */
  expiresAt: Date;
}

/**
 * Available trading pair for stablecoin swaps.
 */
export interface StablecoinPair {
  /** Source token */
  from: string;
  /** Target token */
  to: string;
  /** Minimum swap amount in satoshis */
  minAmount: number;
  /** Maximum swap amount in satoshis */
  maxAmount: number;
  /** Protocol fee rate (decimal, e.g. 0.0025 = 0.25%) */
  feePercentage: number;
}

/**
 * EVM HTLC funding call data for EVM-to-BTC swaps.
 */
export interface EvmFundingCallData {
  /** ERC-20 approve call data */
  approve: { to: string; data: string };
  /** HTLC createSwap call data */
  createSwap: { to: string; data: string };
}

/**
 * EVM HTLC refund call data.
 */
export interface EvmRefundCallData {
  /** HTLC contract address */
  to: string;
  /** Encoded refundSwap call data */
  data: string;
  /** Whether the timelock has expired and refund is available */
  timelockExpired: boolean;
  /** Unix timestamp when refund becomes available */
  timelockExpiry: number;
}

/**
 * Result of a claim operation.
 */
export interface ClaimSwapResult {
  /** Whether the claim was successful */
  success: boolean;
  /** Human-readable message */
  message: string;
  /** Transaction hash (for Gelato/Polygon/Arbitrum claims) */
  txHash?: string;
  /** Chain the claim targets */
  chain?: string;
}

/**
 * Result of a refund operation.
 */
export interface RefundSwapResult {
  /** Whether the refund was successful */
  success: boolean;
  /** Human-readable message */
  message: string;
  /** Transaction ID (for on-chain/Arkade refunds) */
  txId?: string;
  /** Amount refunded in satoshis */
  refundAmount?: number;
}

/**
 * Interface for stablecoin swap skills.
 */
export interface StablecoinSwapSkill extends Skill {
  /**
   * Check if the skill is available and properly configured.
   * @returns true if available
   */
  isAvailable(): Promise<boolean>;

  /**
   * Get a quote for swapping BTC to stablecoins.
   * @param sourceAmount Amount in satoshis
   * @param targetToken Target stablecoin
   * @returns Quote with exchange rate and fees
   */
  getQuoteBtcToStablecoin(
    sourceAmount: number,
    targetToken: StablecoinToken,
  ): Promise<StablecoinQuote>;

  /**
   * Get a quote for swapping stablecoins to BTC.
   * @param sourceAmount Amount of stablecoins
   * @param sourceToken Source stablecoin
   * @returns Quote with exchange rate and fees
   */
  getQuoteStablecoinToBtc(
    sourceAmount: number,
    sourceToken: StablecoinToken,
  ): Promise<StablecoinQuote>;

  /**
   * Swap BTC from Arkade to stablecoins on EVM.
   * @param params Swap parameters
   * @returns Swap result with ID and status
   */
  swapBtcToStablecoin(
    params: BtcToStablecoinParams,
  ): Promise<StablecoinSwapResult>;

  /**
   * Swap stablecoins from EVM to BTC on Arkade.
   * @param params Swap parameters
   * @returns Swap result with ID and payment details
   */
  swapStablecoinToBtc(
    params: StablecoinToBtcParams,
  ): Promise<StablecoinSwapResult>;

  /**
   * Get the status of a swap.
   * @param swapId Swap ID
   * @returns Current swap information
   */
  getSwapStatus(swapId: string): Promise<StablecoinSwapInfo>;

  /**
   * Get pending stablecoin swaps.
   * @returns Array of pending swaps
   */
  getPendingSwaps(): Promise<StablecoinSwapInfo[]>;

  /**
   * Get stablecoin swap history.
   * @returns Array of all swaps
   */
  getSwapHistory(): Promise<StablecoinSwapInfo[]>;

  /**
   * Get available trading pairs.
   * @returns Array of trading pairs with limits
   */
  getAvailablePairs(): Promise<StablecoinPair[]>;

  /**
   * Claim funds from a completed swap.
   * Uses Gelato relay for gasless claims on Polygon/Arbitrum.
   * @param swapId Swap ID
   * @returns Claim result
   */
  claimSwap(swapId: string): Promise<ClaimSwapResult>;

  /**
   * Refund an expired or failed swap.
   * @param swapId Swap ID
   * @param options Refund options (destination address for Arkade/on-chain refunds)
   * @returns Refund result
   */
  refundSwap(
    swapId: string,
    options?: { destinationAddress?: string },
  ): Promise<RefundSwapResult>;

  /**
   * Get EVM HTLC funding call data for EVM-to-BTC swaps.
   * Returns approve + createSwap call data for EVM transactions.
   * @param swapId Swap ID
   * @param tokenDecimals Decimals of the source token (e.g., 6 for USDC)
   * @returns Funding call data
   */
  getEvmFundingCallData(
    swapId: string,
    tokenDecimals: number,
  ): Promise<EvmFundingCallData>;

  /**
   * Get EVM HTLC refund call data for timed-out EVM-to-BTC swaps.
   * @param swapId Swap ID
   * @returns Refund call data
   */
  getEvmRefundCallData(swapId: string): Promise<EvmRefundCallData>;
}
