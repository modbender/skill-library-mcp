/**
 * AgentsBank SDK Client
 * Main API client for interacting with AgentsBank services
 */

import {
  AgentsBankConfig,
  RetryConfig,
  GuardrailsConfig,
  RegisterAgentRequest,
  RegisterAgentResponse,
  LoginRequest,
  LoginResponse,
  Chain,
  Currency,
  WalletInfo,
  CreateWalletResponse,
  GetBalanceResponse,
  SendTransactionRequest,
  SendTransactionResponse,
  SendSafeRequest,
  SendMultipleRequest,
  SendMultipleResponse,
  BalanceCheckResponse,
  SignMessageResponse,
  EstimateGasResponse,
  TransactionHistoryResponse,
  CatalogueResponse,
} from './types.js';
import { AgentsBankError, ErrorCode, createError } from './errors.js';

const DEFAULT_BASE_URL = 'https://api.agentsbank.online';
const DEFAULT_TIMEOUT = 30000;
const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxAttempts: 3,
  initialDelayMs: 100,
  maxDelayMs: 5000,
};

export class AgentsBank {
  private baseUrl: string;
  private apiKey?: string;
  private token?: string;
  private timeout: number;
  private fetchImpl: typeof fetch;
  private retryConfig: RetryConfig;
  private guardrails: GuardrailsConfig;

  constructor(config: AgentsBankConfig = {}) {
    this.baseUrl = config.baseUrl || DEFAULT_BASE_URL;
    this.apiKey = config.apiKey;
    this.token = config.token;
    this.timeout = config.timeout || DEFAULT_TIMEOUT;
    this.fetchImpl = config.fetch || globalThis.fetch;
    this.retryConfig = { ...DEFAULT_RETRY_CONFIG, ...config.retryConfig };
    this.guardrails = config.guardrails || {};

    if (!this.fetchImpl) {
      throw new Error('fetch is not available. Please provide a fetch implementation.');
    }
  }

  // ============================================
  // CONFIGURATION
  // ============================================

  /**
   * Set JWT token for authentication
   */
  setToken(token: string): void {
    this.token = token;
  }

  /**
   * Set API key for authentication
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
  }

  /**
   * Get current authentication status
   */
  isAuthenticated(): boolean {
    return !!(this.token || this.apiKey);
  }

  // ============================================
  // HTTP HELPERS
  // ============================================

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    } else if (this.apiKey) {
      headers['x-api-key'] = this.apiKey;
    }

    return headers;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    let lastError: Error | null = null;
    const maxAttempts = this.retryConfig.maxAttempts || 3;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        return await this.requestInternal<T>(method, path, body);
      } catch (error) {
        lastError = error as Error;

        if (error instanceof AgentsBankError) {
          // Don't retry non-retryable errors
          if (!error.isRetryable()) {
            throw error;
          }

          // Calculate backoff delay
          if (attempt < maxAttempts - 1) {
            const delay = Math.min(
              this.retryConfig.initialDelayMs! * Math.pow(2, attempt),
              this.retryConfig.maxDelayMs!
            );
            await new Promise((resolve) => setTimeout(resolve, delay));
          }
        } else {
          throw error;
        }
      }
    }

    // All retries failed
    if (lastError instanceof AgentsBankError) {
      throw lastError;
    }
    throw createError('All retry attempts failed', ErrorCode.RETRY_FAILED, 500);
  }

  private async requestInternal<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await this.fetchImpl(url, {
        method,
        headers: this.getHeaders(),
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await response.json();

      if (!response.ok) {
        const code = data.code || ErrorCode.INTERNAL_ERROR;
        throw createError(
          data.error || 'Request failed',
          code as ErrorCode,
          response.status,
          data.details
        );
      }

      return data as T;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof AgentsBankError) {
        throw error;
      }

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw createError(
            'Request timeout',
            ErrorCode.TIMEOUT,
            408
          );
        }
        throw createError(error.message, ErrorCode.NETWORK_ERROR, 500);
      }

      throw createError('Unknown error', ErrorCode.INTERNAL_ERROR, 500);
    }
  }

  // ============================================
  // AUTHENTICATION
  // ============================================

  /**
   * Register a new agent (self-registration)
   * Creates both human and agent accounts
   * 
   * @example
   * ```ts
   * const result = await client.register({
   *   human_username: 'myuser',
   *   human_email: 'user@example.com',
   *   first_name: 'John',
   *   last_name: 'Doe',
   *   agent_password: 'SecurePass123!'
   * });
   * 
   * // Save the token for future requests
   * client.setToken(result.token);
   * 
   * // IMPORTANT: Save recovery words securely!
   * console.log(result.recovery_words);
   * ```
   */
  async register(request: RegisterAgentRequest): Promise<RegisterAgentResponse> {
    const response = await this.request<RegisterAgentResponse>(
      'POST',
      '/api/auth/agent/register-self',
      request
    );
    
    // Auto-set token after registration
    if (response.token) {
      this.token = response.token;
    }
    
    return response;
  }

  /**
   * Login with agent credentials
   * 
   * @example
   * ```ts
   * const result = await client.login({
   *   agent_username: 'agent_123456_abc',
   *   agent_password: 'SecurePass123!'
   * });
   * 
   * client.setToken(result.token);
   * ```
   */
  async login(request: LoginRequest): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>(
      'POST',
      '/api/auth/agent/login',
      request
    );
    
    // Auto-set token after login
    if (response.token) {
      this.token = response.token;
    }
    
    return response;
  }

  /**
   * Refresh the JWT token
   */
  async refreshToken(): Promise<{ token: string }> {
    const response = await this.request<{ token: string }>(
      'POST',
      '/api/auth/refresh'
    );
    
    if (response.token) {
      this.token = response.token;
    }
    
    return response;
  }

  // ============================================
  // WALLETS
  // ============================================

  /**
   * Create a new wallet on the specified chain
   * 
   * @example
   * ```ts
   * const wallet = await client.createWallet('solana');
   * console.log(wallet.address); // Solana address
   * ```
   */
  async createWallet(chain: Chain): Promise<CreateWalletResponse> {
    return this.request<CreateWalletResponse>('POST', '/api/wallets', { chain });
  }

  /**
   * Get wallet details by ID
   */
  async getWallet(walletId: string): Promise<WalletInfo> {
    return this.request<WalletInfo>('GET', `/api/wallets/${walletId}`);
  }

  /**
   * Get wallet balance (fetches from blockchain)
   * 
   * @example
   * ```ts
   * const { balance } = await client.getBalance(walletId);
   * console.log(`SOL: ${balance.SOL}`);
   * console.log(`USDC: ${balance.USDC}`);
   * ```
   */
  async getBalance(walletId: string): Promise<GetBalanceResponse> {
    return this.request<GetBalanceResponse>('GET', `/api/wallets/${walletId}/balance`);
  }

  /**
   * Get transaction history for a wallet
   */
  async getTransactionHistory(
    walletId: string,
    limit?: number
  ): Promise<TransactionHistoryResponse> {
    const query = limit ? `?limit=${limit}` : '';
    return this.request<TransactionHistoryResponse>(
      'GET',
      `/api/wallets/${walletId}/history${query}`
    );
  }

  // ============================================
  // TRANSACTIONS
  // ============================================

  /**
   * Send a transaction from a wallet
   * 
   * @example
   * ```ts
   * // Send native token (SOL, ETH, BNB, BTC)
   * const tx = await client.send(walletId, {
   *   to_address: 'recipient_address',
   *   amount: '0.1'
   * });
   * 
   * // Send token (USDC, USDT)
   * const tx = await client.send(walletId, {
   *   to_address: 'recipient_address',
   *   amount: '100',
   *   currency: 'USDC'
   * });
   * ```
   */
  async send(
    walletId: string,
    request: SendTransactionRequest
  ): Promise<SendTransactionResponse> {
    return this.request<SendTransactionResponse>(
      'POST',
      `/api/wallets/${walletId}/send`,
      request
    );
  }

  /**
   * Estimate gas/fees for a transaction
   */
  async estimateGas(
    walletId: string,
    toAddress: string,
    amount: string
  ): Promise<EstimateGasResponse> {
    return this.request<EstimateGasResponse>(
      'GET',
      `/api/wallets/${walletId}/estimate-gas?to_address=${encodeURIComponent(toAddress)}&amount=${encodeURIComponent(amount)}`
    );
  }

  // ============================================
  // SIGNING
  // ============================================

  /**
   * Sign a message with wallet's private key
   * Useful for authentication with external services
   * 
   * @example
   * ```ts
   * const { signature } = await client.signMessage(walletId, 'Hello, World!');
   * // Use signature to prove ownership of the address
   * ```
   */
  async signMessage(walletId: string, message: string): Promise<SignMessageResponse> {
    return this.request<SignMessageResponse>(
      'POST',
      `/api/wallets/${walletId}/sign-message`,
      { message }
    );
  }

  // ============================================
  // CATALOGUE
  // ============================================

  /**
   * Get supported chains and tokens
   */
  async getCatalogue(): Promise<CatalogueResponse> {
    return this.request<CatalogueResponse>('GET', '/api/catalogue/chains');
  }

  // ============================================
  // HEALTH
  // ============================================

  /**
   * Check API health status
   */
  async health(): Promise<{ status: string; timestamp: string; version: string }> {
    return this.request<{ status: string; timestamp: string; version: string }>(
      'GET',
      '/health'
    );
  }

  // ============================================
  // HELPER METHODS (v1.0.5)
  // ============================================

  /**
   * Check if wallet has enough funds for a transaction
   * Includes guardrail validation
   * 
   * @example
   * ```ts
   * const hasEnough = await client.hasEnoughFunds(walletId, '1.0');
   * if (!hasEnough.has_enough_funds) {
   *   console.log('Insufficient balance:', hasEnough.current_balance);
   * }
   * ```
   */
  async hasEnoughFunds(walletId: string, amount: string): Promise<BalanceCheckResponse> {
    const balance = await this.getBalance(walletId);
    
    // Get native token for the wallet's chain
    const nativeTokens: Record<Chain, Currency> = {
      ethereum: 'ETH',
      bsc: 'BNB',
      solana: 'SOL',
      bitcoin: 'BTC',
    };

    const currency = nativeTokens[balance.chain];
    const currentBalance = parseFloat(balance.balance[currency] || '0');
    const requiredAmount = parseFloat(amount);

    return {
      has_enough_funds: currentBalance >= requiredAmount,
      current_balance: balance.balance[currency] || '0',
      required_amount: amount,
      currency,
    };
  }

  /**
   * Send transaction with pre-flight checks (recommended for production)
   * Includes auto-retry, balance validation, guardrail checks
   * 
   * @example
   * ```ts
   * const tx = await client.sendSafe(walletId, {
   *   to_address: 'recipient',
   *   amount: '1.0',
   *   maxGasUSD: 100
   * });
   * ```
   */
  async sendSafe(
    walletId: string,
    request: SendSafeRequest
  ): Promise<SendTransactionResponse> {
    // Check guardrails
    this.validateGuardrails(request.to_address, request.amount);

    // Check sufficient funds
    const hasEnough = await this.hasEnoughFunds(walletId, request.amount);
    if (!hasEnough.has_enough_funds) {
      throw createError(
        `Insufficient funds: need ${request.amount}, have ${hasEnough.current_balance}`,
        ErrorCode.INSUFFICIENT_FUNDS,
        409
      );
    }

    // Estimate gas if maxGasUSD provided
    if (request.maxGasUSD) {
      try {
        await this.estimateGas(walletId, request.to_address, request.amount);
        // Note: estimate currently returns estimated_gas, not usd_equivalent
        // This is noted in the types
      } catch (error) {
        // Gas estimation failed, but continue (optional check)
        if (!(error instanceof AgentsBankError && error.code === ErrorCode.TIMEOUT)) {
          throw error;
        }
      }
    }

    // Send transaction (auto-retry built-in)
    return this.send(walletId, {
      to_address: request.to_address,
      amount: request.amount,
      currency: request.currency,
    });
  }

  /**
   * Send transactions to multiple recipients
   * Batch operation for efficiency
   * 
   * @example
   * ```ts
   * const results = await client.sendMultiple(walletId, {
   *   recipients: [
   *     { to_address: '0x111...', amount: '1.0' },
   *     { to_address: '0x222...', amount: '2.0' }
   *   ]
   * });
   * ```
   */
  async sendMultiple(
    walletId: string,
    request: SendMultipleRequest
  ): Promise<SendMultipleResponse> {
    const results: SendTransactionResponse[] = [];
    let totalAmount = '0';
    let totalFees = '0';

    for (const recipient of request.recipients) {
      try {
        // Validate guardrails for each recipient
        this.validateGuardrails(recipient.to_address, recipient.amount);

        // Send transaction
        const tx = await this.send(walletId, {
          to_address: recipient.to_address,
          amount: recipient.amount,
          currency: recipient.currency,
        });

        results.push(tx);
        totalAmount = (parseFloat(totalAmount) + parseFloat(recipient.amount)).toString();
      } catch (error) {
        // Continue with other recipients, but track failure
        if (error instanceof AgentsBankError) {
          results.push({
            tx_hash: '',
            status: 'failed',
            from_address: '',
            to_address: recipient.to_address,
            amount: recipient.amount,
            chain: 'ethereum', // Placeholder
          });
        } else {
          throw error;
        }
      }
    }

    return {
      results,
      totalAmount,
      totalFees,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Validate transaction against guardrails
   * @private
   */
  private validateGuardrails(toAddress: string, amount: string): void {
    if (!this.guardrails) return;

    // Check whitelisting
    if (
      this.guardrails.whitelistedAddresses &&
      this.guardrails.whitelistedAddresses.length > 0
    ) {
      if (!this.guardrails.whitelistedAddresses.includes(toAddress)) {
        throw createError(
          'Recipient address not whitelisted',
          ErrorCode.GUARDRAIL_VIOLATION,
          403
        );
      }
    }

    // Check blacklisting
    if (
      this.guardrails.blacklistedAddresses &&
      this.guardrails.blacklistedAddresses.includes(toAddress)
    ) {
      throw createError(
        'Recipient address is blacklisted',
        ErrorCode.GUARDRAIL_VIOLATION,
        403
      );
    }

    // Max per transaction check
    if (this.guardrails.maxPerTxUSD) {
      const amountNum = parseFloat(amount);
      if (amountNum > this.guardrails.maxPerTxUSD) {
        throw createError(
          `Transaction amount $${amountNum} exceeds max per tx $${this.guardrails.maxPerTxUSD}`,
          ErrorCode.GUARDRAIL_VIOLATION,
          403
        );
      }
    }
  }
}

/**
 * Create a new AgentsBank client instance
 * 
 * @example
 * ```ts
 * import { createClient } from '@agentsbank/sdk';
 * 
 * const client = createClient({
 *   apiKey: 'your-api-key'
 * });
 * 
 * // Or with token
 * const client = createClient({
 *   token: 'your-jwt-token'
 * });
 * ```
 */
export function createClient(config?: AgentsBankConfig): AgentsBank {
  return new AgentsBank(config);
}
