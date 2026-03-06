/**
 * LendaSwapSkill - Swap USDC/USDT from/to Arkade via LendaSwap.
 *
 * This skill provides stablecoin swap capabilities for Arkade wallets
 * using the LendaSwap SDK for non-custodial BTC/stablecoin exchanges.
 *
 * @module skills/lendaswap
 */

import type { Wallet } from "@arkade-os/sdk";
import type {
  StablecoinSwapSkill,
  StablecoinToken,
  EvmChain,
  BtcToStablecoinParams,
  StablecoinToBtcParams,
  StablecoinSwapResult,
  StablecoinSwapInfo,
  StablecoinSwapStatus,
  StablecoinQuote,
  StablecoinPair,
} from "./types";

/**
 * Default LendaSwap API URL.
 */
const DEFAULT_API_URL = "https://apilendaswap.lendasat.com/";

/**
 * Token decimals for stablecoins.
 */
const TOKEN_DECIMALS: Record<string, number> = {
  usdc_pol: 6,
  usdc_eth: 6,
  usdc_arb: 6,
  usdt_pol: 6,
  usdt_eth: 6,
  usdt_arb: 6,
};

function parseExpiry(raw: unknown, fallbackMs: number): Date {
  if (raw === null || raw === undefined) {
    return new Date(Date.now() + fallbackMs);
  }
  if (typeof raw === "string") {
    const parsed = new Date(raw);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed;
    }
  }
  if (typeof raw === "number") {
    const ms = raw < 1_000_000_000_000 ? raw * 1000 : raw;
    return new Date(ms);
  }
  return new Date(Date.now() + fallbackMs);
}

/**
 * Configuration for the LendaSwapSkill.
 */
export interface LendaSwapSkillConfig {
  /** The Arkade wallet to use */
  wallet: Wallet;
  /** Optional API key (LendaSwap API is publicly accessible) */
  apiKey?: string;
  /** Optional custom API URL (default: https://apilendaswap.lendasat.com/) */
  apiUrl?: string;
  /** Optional Esplora URL for Bitcoin queries */
  esploraUrl?: string;
  /** Optional mnemonic for HD wallet key derivation */
  mnemonic?: string;
  /** Optional referral code for fee discounts */
  referralCode?: string;
}

/**
 * Internal swap storage entry.
 */
interface StoredSwap {
  swapId: string;
  direction: "btc_to_stablecoin" | "stablecoin_to_btc";
  status: StablecoinSwapStatus;
  sourceToken: string;
  targetToken: string;
  sourceAmount: number;
  targetAmount: number;
  exchangeRate: number;
  createdAt: number;
  completedAt?: number;
  txid?: string;
  response?: any;
}

/**
 * LendaSwapSkill provides stablecoin swap capabilities for Arkade wallets
 * using the LendaSwap SDK.
 *
 * This skill enables:
 * - Swapping BTC from Arkade to USDC/USDT on Polygon, Ethereum, or Arbitrum
 * - Receiving USDC/USDT and converting to BTC in your Arkade wallet
 *
 * @example
 * ```typescript
 * import { Wallet, SingleKey } from "@arkade-os/sdk";
 * import { LendaSwapSkill } from "@arkade-os/skill";
 *
 * // Create a wallet
 * const wallet = await Wallet.create({
 *   identity: SingleKey.fromHex(privateKeyHex),
 *   arkServerUrl: "https://arkade.computer",
 * });
 *
 * // Create the LendaSwap skill
 * const lendaswap = new LendaSwapSkill({ wallet });
 *
 * // Get a quote for BTC to USDC
 * const quote = await lendaswap.getQuoteBtcToStablecoin(100000, "usdc_pol");
 * console.log("You'll receive:", quote.targetAmount, "USDC");
 *
 * // Execute the swap
 * const result = await lendaswap.swapBtcToStablecoin({
 *   targetAddress: "0x...",
 *   targetToken: "usdc_pol",
 *   targetChain: "polygon",
 *   sourceAmount: 100000,
 * });
 * console.log("Swap created:", result.swapId);
 * ```
 */
export class LendaSwapSkill implements StablecoinSwapSkill {
  readonly name = "lendaswap";
  readonly description =
    "Swap USDC/USDT from/to Arkade via LendaSwap non-custodial exchange";
  readonly version = "1.0.0";

  private readonly wallet: Wallet;
  private readonly apiUrl: string;
  private readonly apiKey?: string;
  private readonly referralCode?: string;
  private readonly swapStorage: Map<string, StoredSwap> = new Map();

  /**
   * Creates a new LendaSwapSkill instance.
   *
   * @param config - Configuration options
   */
  constructor(config: LendaSwapSkillConfig) {
    this.wallet = config.wallet;
    this.apiUrl = config.apiUrl || DEFAULT_API_URL;
    this.apiKey = config.apiKey;
    this.referralCode = config.referralCode;
  }

  /**
   * Check if the skill is available and properly configured.
   */
  async isAvailable(): Promise<boolean> {
    try {
      const response = await this.fetchApi("/pairs");
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Get a quote for swapping BTC to stablecoins.
   */
  async getQuoteBtcToStablecoin(
    sourceAmount: number,
    targetToken: StablecoinToken,
  ): Promise<StablecoinQuote> {
    const response = await this.fetchApi("/quote", {
      method: "POST",
      body: JSON.stringify({
        from: "btc_arkade",
        to: targetToken,
        amount: sourceAmount,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to get quote: ${response.statusText}`);
    }

    const data = (await response.json()) as Record<string, any>;

    return {
      sourceToken: "btc_arkade",
      targetToken,
      sourceAmount,
      targetAmount: data.targetAmount,
      exchangeRate: data.exchangeRate,
      fee: {
        amount: data.fee?.amount || 0,
        percentage: data.fee?.percentage || 0,
      },
      expiresAt: parseExpiry(data.expiresAt, 60000),
    };
  }

  /**
   * Get a quote for swapping stablecoins to BTC.
   */
  async getQuoteStablecoinToBtc(
    sourceAmount: number,
    sourceToken: StablecoinToken,
  ): Promise<StablecoinQuote> {
    const response = await this.fetchApi("/quote", {
      method: "POST",
      body: JSON.stringify({
        from: sourceToken,
        to: "btc_arkade",
        amount: sourceAmount,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to get quote: ${response.statusText}`);
    }

    const data = (await response.json()) as Record<string, any>;

    return {
      sourceToken,
      targetToken: "btc_arkade",
      sourceAmount,
      targetAmount: data.targetAmount,
      exchangeRate: data.exchangeRate,
      fee: {
        amount: data.fee?.amount || 0,
        percentage: data.fee?.percentage || 0,
      },
      expiresAt: parseExpiry(data.expiresAt, 60000),
    };
  }

  /**
   * Swap BTC from Arkade to stablecoins on EVM.
   */
  async swapBtcToStablecoin(
    params: BtcToStablecoinParams,
  ): Promise<StablecoinSwapResult> {
    const arkAddress = await this.wallet.getAddress();

    const response = await this.fetchApi("/swap/btc-to-evm", {
      method: "POST",
      body: JSON.stringify({
        sourceAddress: arkAddress,
        targetAddress: params.targetAddress,
        targetToken: params.targetToken,
        targetChain: params.targetChain,
        sourceAmount: params.sourceAmount,
        targetAmount: params.targetAmount,
        referralCode: params.referralCode || this.referralCode,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create swap: ${response.statusText}`);
    }

    const data = (await response.json()) as Record<string, any>;

    const resolvedSourceAmount =
      params.sourceAmount ?? data.sourceAmount ?? 0;

    // Store swap locally
    const storedSwap: StoredSwap = {
      swapId: data.swapId,
      direction: "btc_to_stablecoin",
      status: "awaiting_funding",
      sourceToken: "btc_arkade",
      targetToken: params.targetToken,
      sourceAmount: resolvedSourceAmount,
      targetAmount: data.targetAmount || 0,
      exchangeRate: data.exchangeRate || 0,
      createdAt: Date.now(),
      response: data,
    };
    this.swapStorage.set(data.swapId, storedSwap);

    return {
      swapId: data.swapId,
      status: "awaiting_funding",
      sourceAmount: resolvedSourceAmount,
      targetAmount: data.targetAmount || 0,
      exchangeRate: data.exchangeRate || 0,
      fee: {
        amount: data.fee?.amount || 0,
        percentage: data.fee?.percentage || 0,
      },
      expiresAt: new Date(data.expiresAt || Date.now() + 3600000),
      paymentDetails: {
        address: data.paymentAddress,
      },
    };
  }

  /**
   * Swap stablecoins from EVM to BTC on Arkade.
   */
  async swapStablecoinToBtc(
    params: StablecoinToBtcParams,
  ): Promise<StablecoinSwapResult> {
    const arkAddress = await this.wallet.getAddress();
    const targetAddress = params.targetAddress || arkAddress;

    const response = await this.fetchApi("/swap/evm-to-arkade", {
      method: "POST",
      body: JSON.stringify({
        sourceChain: params.sourceChain,
        sourceToken: params.sourceToken,
        sourceAmount: params.sourceAmount,
        targetAddress,
        userAddress: params.userAddress,
        referralCode: params.referralCode || this.referralCode,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create swap: ${response.statusText}`);
    }

    const data = (await response.json()) as Record<string, any>;

    // Store swap locally
    const storedSwap: StoredSwap = {
      swapId: data.swapId,
      direction: "stablecoin_to_btc",
      status: "awaiting_funding",
      sourceToken: params.sourceToken,
      targetToken: "btc_arkade",
      sourceAmount: params.sourceAmount,
      targetAmount: data.targetAmount || 0,
      exchangeRate: data.exchangeRate || 0,
      createdAt: Date.now(),
      response: data,
    };
    this.swapStorage.set(data.swapId, storedSwap);

    return {
      swapId: data.swapId,
      status: "awaiting_funding",
      sourceAmount: params.sourceAmount,
      targetAmount: data.targetAmount || 0,
      exchangeRate: data.exchangeRate || 0,
      fee: {
        amount: data.fee?.amount || 0,
        percentage: data.fee?.percentage || 0,
      },
      expiresAt: new Date(data.expiresAt || Date.now() + 3600000),
      paymentDetails: {
        address: data.htlcAddress,
        callData: data.fundingCallData,
      },
    };
  }

  /**
   * Get the status of a swap.
   */
  async getSwapStatus(swapId: string): Promise<StablecoinSwapInfo> {
    const response = await this.fetchApi(`/swap/${swapId}`);

    if (!response.ok) {
      throw new Error(`Failed to get swap status: ${response.statusText}`);
    }

    const data = (await response.json()) as Record<string, any>;

    // Update local storage
    const stored = this.swapStorage.get(swapId);
    if (stored) {
      stored.status = data.status;
      stored.txid = data.txid;
      if (data.status === "completed") {
        stored.completedAt = Date.now();
      }
    }

    return {
      id: swapId,
      direction: data.direction || stored?.direction || "btc_to_stablecoin",
      status: data.status,
      sourceToken: data.sourceToken || stored?.sourceToken || "",
      targetToken: data.targetToken || stored?.targetToken || "",
      sourceAmount: data.sourceAmount || stored?.sourceAmount || 0,
      targetAmount: data.targetAmount || stored?.targetAmount || 0,
      exchangeRate: data.exchangeRate || stored?.exchangeRate || 0,
      createdAt: new Date(data.createdAt || stored?.createdAt || Date.now()),
      completedAt: data.completedAt ? new Date(data.completedAt) : undefined,
      txid: data.txid,
    };
  }

  /**
   * Get pending stablecoin swaps.
   */
  async getPendingSwaps(): Promise<StablecoinSwapInfo[]> {
    const pending: StablecoinSwapInfo[] = [];

    for (const [id, swap] of this.swapStorage) {
      if (
        swap.status !== "completed" &&
        swap.status !== "expired" &&
        swap.status !== "refunded" &&
        swap.status !== "failed"
      ) {
        try {
          const status = await this.getSwapStatus(id);
          pending.push(status);
        } catch {
          // Swap might not exist on server anymore
          pending.push({
            id,
            direction: swap.direction,
            status: swap.status,
            sourceToken: swap.sourceToken,
            targetToken: swap.targetToken,
            sourceAmount: swap.sourceAmount,
            targetAmount: swap.targetAmount,
            exchangeRate: swap.exchangeRate,
            createdAt: new Date(swap.createdAt),
          });
        }
      }
    }

    return pending;
  }

  /**
   * Get stablecoin swap history.
   */
  async getSwapHistory(): Promise<StablecoinSwapInfo[]> {
    const history: StablecoinSwapInfo[] = [];

    for (const [id, swap] of this.swapStorage) {
      history.push({
        id,
        direction: swap.direction,
        status: swap.status,
        sourceToken: swap.sourceToken,
        targetToken: swap.targetToken,
        sourceAmount: swap.sourceAmount,
        targetAmount: swap.targetAmount,
        exchangeRate: swap.exchangeRate,
        createdAt: new Date(swap.createdAt),
        completedAt: swap.completedAt ? new Date(swap.completedAt) : undefined,
        txid: swap.txid,
      });
    }

    return history.sort(
      (a, b) => b.createdAt.getTime() - a.createdAt.getTime(),
    );
  }

  /**
   * Get available trading pairs.
   */
  async getAvailablePairs(): Promise<StablecoinPair[]> {
    const response = await this.fetchApi("/pairs");

    if (!response.ok) {
      throw new Error(`Failed to get pairs: ${response.statusText}`);
    }

    const data = (await response.json()) as Record<string, any>;

    return (data.pairs || data || []).map((pair: any) => ({
      from: pair.from || pair.source,
      to: pair.to || pair.target,
      minAmount: pair.minAmount || pair.min || 0,
      maxAmount: pair.maxAmount || pair.max || 0,
      feePercentage: pair.feePercentage || pair.fee || 0,
    }));
  }

  /**
   * Claim funds from a completed swap.
   */
  async claimSwap(swapId: string): Promise<{ txid: string }> {
    const response = await this.fetchApi(`/swap/${swapId}/claim`, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error(`Failed to claim swap: ${response.statusText}`);
    }

    const data = (await response.json()) as Record<string, any>;

    // Update local storage
    const stored = this.swapStorage.get(swapId);
    if (stored) {
      stored.status = "completed";
      stored.completedAt = Date.now();
      stored.txid = data.txid;
    }

    return { txid: data.txid };
  }

  /**
   * Refund an expired or failed swap.
   */
  async refundSwap(swapId: string): Promise<{ txid: string }> {
    const response = await this.fetchApi(`/swap/${swapId}/refund`, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error(`Failed to refund swap: ${response.statusText}`);
    }

    const data = (await response.json()) as Record<string, any>;

    // Update local storage
    const stored = this.swapStorage.get(swapId);
    if (stored) {
      stored.status = "refunded";
      stored.txid = data.txid;
    }

    return { txid: data.txid };
  }

  /**
   * Get the underlying wallet instance.
   */
  getWallet(): Wallet {
    return this.wallet;
  }

  /**
   * Get token decimals for a stablecoin.
   */
  getTokenDecimals(token: StablecoinToken): number {
    return TOKEN_DECIMALS[token] || 6;
  }

  /**
   * Helper to fetch from LendaSwap API.
   */
  private async fetchApi(
    path: string,
    options: RequestInit = {},
  ): Promise<Response> {
    const url = `${this.apiUrl.replace(/\/$/, "")}${path}`;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (this.apiKey) {
      headers["X-API-Key"] = this.apiKey;
    }

    return fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...(options.headers as Record<string, string>),
      },
    });
  }
}

/**
 * Create a LendaSwapSkill from a wallet.
 *
 * @param wallet - The Arkade wallet to use
 * @param options - Optional configuration
 * @returns A new LendaSwapSkill instance
 */
export function createLendaSwapSkill(
  wallet: Wallet,
  options?: Partial<Omit<LendaSwapSkillConfig, "wallet">>,
): LendaSwapSkill {
  return new LendaSwapSkill({
    wallet,
    ...options,
  });
}
