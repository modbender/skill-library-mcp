import axios, { AxiosInstance } from 'axios';

// Based on ping-checkout-example + Actual API Response
export interface CheckoutAsset {
  chain: string;  // e.g., "NEAR", "Base", "ETH"
  symbol: string; // e.g., "USDC", "NEAR", "ETH"
}

export interface CreateCheckoutSessionInput {
  amount: string;           // Amount in smallest unit (e.g., "100000" for 0.1 USDC)
  asset: CheckoutAsset;     // Chain and symbol (API resolves to assetId)
  successUrl?: string;      // Redirect URL after successful payment
  cancelUrl?: string;       // Redirect URL if payment cancelled
  metadata?: Record<string, unknown>; // Optional metadata (orderId, etc.)
  expiresAt?: string;       // Optional: ISO 8601 timestamp for expiration
  expiresInSeconds?: number; // Optional: Seconds until expiration (alternative to expiresAt)
  // NOTE: Recipient is configured in organization settings, NOT in request!
}

// Actual response structure from PingPay API
export interface CheckoutAmount {
  assetId: string;  // e.g., "nep141:base-0x833...913.omft.near"
  amount: string;   // Amount in smallest unit
  decimals: number; // Token decimals (e.g., 6 for USDC)
}

export interface CheckoutRecipient {
  address: string;  // Recipient NEAR address from org settings
}

export interface CheckoutSession {
  sessionId: string;
  status: string;              // "CREATED", "COMPLETED", "EXPIRED", etc.
  paymentId: string | null;    // Null until payment completed
  amount: CheckoutAmount;
  recipient: CheckoutRecipient;
  successUrl?: string;
  cancelUrl?: string;
  createdAt: string;           // ISO 8601 timestamp
  expiresAt?: string;          // ISO 8601 timestamp (default: 1 hour)
  metadata?: Record<string, unknown>;
}

export interface CreateCheckoutSessionResponse {
  session: CheckoutSession;
  sessionUrl: string;       // Full checkout URL to redirect user to
}

export interface PingPayError {
  message: string;
  code?: string;
}

export class PingPayClient {
  private client: AxiosInstance;
  private apiKey: string;
  private baseURL: string;

  constructor(apiKey: string, baseURL: string = 'https://pay.pingpay.io') {
    this.apiKey = apiKey;
    this.baseURL = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL;
    
    this.client = axios.create({
      baseURL: this.baseURL + '/api', // Add /api prefix
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey
      },
      timeout: 30000
    });
  }

  /**
   * Create a new checkout session
   * 
   * Creates a payment link that can be shared with users.
   * Recipient address is configured in your PingPay organization settings.
   * 
   * Example:
   * ```typescript
   * const response = await client.createCheckoutSession({
   *   amount: '1000000', // 1 USDC (6 decimals)
   *   asset: { chain: 'NEAR', symbol: 'USDC' },
   *   expiresInSeconds: 31536000, // 1 year
   *   successUrl: 'https://example.com/success',
   *   cancelUrl: 'https://example.com/cancel',
   *   metadata: { orderId: 'order_123' }
   * });
   * 
   * // Share the payment link
   * console.log(response.sessionUrl);
   * // https://pay.pingpay.io/checkout?sessionId=cs_xxx
   * ```
   * 
   * @param input - Checkout session parameters
   * @returns Checkout session with sessionUrl
   */
  async createCheckoutSession(input: CreateCheckoutSessionInput): Promise<CreateCheckoutSessionResponse> {
    try {
      const response = await this.client.post('/checkout/sessions', input);
      return response.data;
    } catch (error: any) {
      const errorMsg = this.formatError(error, 'create checkout session');
      throw new Error(errorMsg);
    }
  }

  /**
   * Get checkout session details by ID
   * 
   * @param sessionId - The session ID
   * @returns Checkout session details
   */
  async getCheckoutSession(sessionId: string): Promise<CheckoutSession> {
    try {
      const response = await this.client.get(`/checkout/sessions/${sessionId}`);
      return response.data.session || response.data;
    } catch (error: any) {
      const errorMsg = this.formatError(error, 'get checkout session');
      throw new Error(errorMsg);
    }
  }

  /**
   * Test API connection
   */
  async testConnection(): Promise<{ success: boolean; message: string; sessionUrl?: string }> {
    try {
      const testInput: CreateCheckoutSessionInput = {
        amount: "1000000", // 1 USDC
        asset: { chain: "NEAR", symbol: "USDC" },
        metadata: { test: true }
      };
      
      const response = await this.client.post('/checkout/sessions', testInput);
      return { 
        success: true, 
        message: `API connection successful! Session: ${response.data.session.sessionId}`,
        sessionUrl: response.data.sessionUrl
      };
    } catch (error: any) {
      return { 
        success: false, 
        message: this.formatError(error, 'test connection')
      };
    }
  }

  /**
   * Helper: Convert decimal USDC to smallest unit (6 decimals)
   */
  static usdcToSmallestUnit(amount: number): string {
    return Math.floor(amount * 1_000_000).toString();
  }

  /**
   * Helper: Convert decimal NEAR to smallest unit (24 decimals)
   */
  static nearToSmallestUnit(amount: number): string {
    const yocto = BigInt(Math.floor(amount * 1e24));
    return yocto.toString();
  }

  /**
   * Helper: Convert smallest unit back to decimal
   */
  static fromSmallestUnit(amount: string, decimals: number): number {
    return parseInt(amount) / Math.pow(10, decimals);
  }

  /**
   * Helper: Format checkout amount for display
   */
  static formatAmount(checkoutAmount: CheckoutAmount): string {
    const decimal = this.fromSmallestUnit(checkoutAmount.amount, checkoutAmount.decimals);
    return `${decimal.toFixed(checkoutAmount.decimals)}`;
  }

  /**
   * Helper: Calculate expiration timestamp
   * @param durationSeconds - Duration in seconds (e.g., 31536000 for 1 year)
   * @returns ISO 8601 timestamp
   */
  static getExpirationTimestamp(durationSeconds: number): string {
    const now = new Date();
    const expiresAt = new Date(now.getTime() + durationSeconds * 1000);
    return expiresAt.toISOString();
  }

  /**
   * Format error messages with useful debugging info
   */
  private formatError(error: any, operation: string): string {
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      const url = error.config?.url || 'unknown';
      
      // PingPay error format
      if (data?.message) {
        return `Failed to ${operation}: ${data.message}${data.code ? ` (${data.code})` : ''}`;
      }
      
      return `Failed to ${operation}: HTTP ${status} from ${url}\n` +
             `Response: ${JSON.stringify(data, null, 2)}`;
    } else if (error.request) {
      return `Failed to ${operation}: No response from server\n` +
             `Check API endpoint: ${this.baseURL}/api`;
    } else {
      return `Failed to ${operation}: ${error.message}`;
    }
  }
}
