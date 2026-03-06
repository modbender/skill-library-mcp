/**
 * Agent Wallet Integration with Coinbase AgentKit
 *
 * Uses Coinbase CDP (Developer Platform) to create and manage
 * wallet for autonomous agents with X402 payment capabilities.
 *
 * ⭐ Per-User Wallet Support:
 * - Each userId gets a unique, persistent wallet
 * - Wallets are stored and retrieved automatically
 * - First time: creates new wallet and stores it
 * - Next time: retrieves existing wallet for same userId
 *
 * References:
 * - AgentKit Docs: https://docs.cdp.coinbase.com/agent-kit/welcome
 * - X402 Protocol: https://docs.cdp.coinbase.com/x402/welcome
 */

import { CdpEvmWalletProvider } from '@coinbase/agentkit';
import { walletStorage } from './wallet-storage';
import * as crypto from 'crypto';
import { generatePrivateKey, privateKeyToAccount } from 'viem/accounts';
import type { PrivateKeyAccount } from 'viem';

export interface AgentWalletConfig {
  userId: string;  // ⭐ Required for per-user wallets
  network?: 'base-mainnet' | 'base-sepolia';
  apiKey?: string;
  privateKey?: string;
}

export interface AgentWalletInfo {
  address: string;
  network: string;
  x402Endpoint?: string;
  balance?: string;
  agentUserId?: number;
}

/**
 * Agent Wallet Manager
 *
 * Creates and manages wallet for autonomous agent using Coinbase AgentKit
 *
 * ⭐ Each user gets a unique, persistent wallet:
 * - User A → Wallet A (address: 0xAAA...)
 * - User B → Wallet B (address: 0xBBB...)
 */
export class AgentWallet {
  private userId: string;  // ⭐ User identifier
  private walletProvider: CdpEvmWalletProvider | null = null;
  private network: 'base-mainnet' | 'base-sepolia';
  private walletAddress: `0x${string}` | null = null;
  private localAccount: PrivateKeyAccount | null = null;  // ⭐ For local wallet signing

  constructor(config: AgentWalletConfig) {
    // ⭐ userId is required for per-user wallets
    if (!config.userId) {
      throw new Error('userId is required for AgentWallet');
    }

    this.userId = config.userId;

    // Default to mainnet for production readiness
    // Use NETWORK env var or config.network to override
    this.network = config.network ||
                   (process.env.NETWORK as 'base-mainnet' | 'base-sepolia') ||
                   'base-mainnet';
  }

  /**
   * Initialize agent wallet
   *
   * ⭐ Per-User Wallet Logic:
   * 1. Check if user already has a wallet (stored)
   * 2. If yes → Import existing wallet
   * 3. If no → Create new wallet and store it
   *
   * ⭐ Performance: 5-second timeout prevents long waits when CDP is unavailable
   */
  async initialize(): Promise<AgentWalletInfo> {
    console.log(`🤖 Initializing Agent Wallet for user ${this.userId} on ${this.network}...`);

    try {
      // ⭐ Add 5-second timeout to prevent long waits
      const result = await this.withTimeout(
        this.initializeWalletInternal(),
        5000,
        'CDP wallet initialization timed out (5s) - falling back to local wallet'
      );
      return result;
    } catch (error) {
      // ⭐ NEW: Fallback to local wallet (real wallet, not mock!)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.debug(`CDP unavailable (${errorMessage}), using local wallet fallback`);

      try {
        const localWallet = await this.createLocalWallet();
        console.log(`✅ Local wallet created: ${localWallet.address}`);
        return localWallet;
      } catch (localError) {
        // Last resort: mock wallet for testing
        console.debug('Local wallet creation failed, using mock wallet');
        const hash = this.simpleHash(this.userId);
        this.walletAddress = ('0x' + hash.substring(0, 40)) as `0x${string}`;
        console.log(`🧪 Mock wallet for ${this.userId}: ${this.walletAddress}`);

        // ⭐ Save mock wallet (so returning users see same wallet address)
        await walletStorage.saveUserWallet(
          this.userId,
          this.walletAddress,
          this.network
          // No privateKey = marks as mock wallet
        );

        return {
          address: this.walletAddress,
          network: this.network,
          x402Endpoint: this.getX402Endpoint(),
        };
      }
    }
  }

  /**
   * Internal wallet initialization logic (wrapped with timeout in initialize())
   */
  private async initializeWalletInternal(): Promise<AgentWalletInfo> {
    // Map network name to CDP format
    const cdpNetwork = this.network === 'base-mainnet' ? 'base' : 'base-sepolia';

    // Get CDP API credentials from environment variables
    const apiKeyId = process.env.CDP_API_KEY_ID;
    const apiKeySecret = process.env.CDP_API_KEY_SECRET;
    const walletSecret = process.env.CDP_WALLET_SECRET;

    // Get RPC URL (with fallback to public endpoints)
    const rpcUrl = process.env.CDP_RPC_URL || this.getDefaultRpcUrl();

    // ⭐ Step 1: Check if user already has a wallet
    const existingWallet = await walletStorage.getUserWallet(this.userId);

    if (existingWallet && existingWallet.network === this.network) {
      // ⭐ Import existing wallet by address
      console.log(`📂 Loading existing wallet for user ${this.userId}...`);

      this.walletProvider = await CdpEvmWalletProvider.configureWithWallet({
        networkId: cdpNetwork,
        apiKeyId,
        apiKeySecret,
        walletSecret,
        rpcUrl,  // ⭐ Add RPC URL
        address: existingWallet.walletAddress as `0x${string}`,  // ⭐ Import by address
      });

      this.walletAddress = this.walletProvider.getAddress() as `0x${string}`;

      // Update last used timestamp
      await walletStorage.updateLastUsed(this.userId);

      console.log(`✅ Existing wallet loaded: ${this.walletAddress}`);

    } else {
      // ⭐ Create new wallet with idempotency key
      console.log(`🆕 Creating new wallet for user ${this.userId}...`);

      this.walletProvider = await CdpEvmWalletProvider.configureWithWallet({
        networkId: cdpNetwork,
        apiKeyId,
        apiKeySecret,
        walletSecret,
        rpcUrl,  // ⭐ Add RPC URL
        idempotencyKey: this.generateDeterministicUUID(this.userId),  // ⭐ UUID v4 from userId
      });

      this.walletAddress = this.walletProvider.getAddress() as `0x${string}`;

      // ⭐ Store wallet address (CDP manages wallet server-side in 0.10.4)
      await walletStorage.saveUserWallet(
        this.userId,
        this.walletAddress,
        this.network
      );

      console.log(`✅ New wallet created and stored: ${this.walletAddress}`);
    }

    // Log wallet count for debugging
    const walletCount = await walletStorage.getWalletCount();
    console.log(`📊 Total wallets in storage: ${walletCount}`);

    return {
      address: this.walletAddress,
      network: this.network,
      x402Endpoint: this.getX402Endpoint(),
    };
  }

  /**
   * Create local wallet using viem (fallback when CDP unavailable)
   *
   * ⭐ Production-ready local wallet implementation
   * - Real EVM wallet (not mock)
   * - Private keys encrypted with AES-256-GCM
   * - Stored locally for persistence
   */
  private async createLocalWallet(): Promise<AgentWalletInfo> {
    console.log(`🏠 Creating local wallet for user ${this.userId}...`);

    // Check if user already has a local wallet
    const existingWallet = await walletStorage.getUserWallet(this.userId);

    if (existingWallet && existingWallet.privateKey) {
      // Load existing local wallet
      console.log(`📂 Loading existing local wallet...`);
      const account = privateKeyToAccount(existingWallet.privateKey as `0x${string}`);
      this.walletAddress = account.address;
      this.localAccount = account;  // ⭐ Store for signing

      // Update last used
      await walletStorage.updateLastUsed(this.userId);

      return {
        address: account.address,
        network: this.network,
        x402Endpoint: this.getX402Endpoint(),
      };
    }

    // Generate new local wallet using viem
    const privateKey = generatePrivateKey();
    const account = privateKeyToAccount(privateKey);
    this.walletAddress = account.address;
    this.localAccount = account;  // ⭐ Store for signing

    // Store wallet locally with AES-256-GCM encryption
    await walletStorage.saveUserWallet(
      this.userId,
      this.walletAddress,
      this.network,
      privateKey  // Encrypted automatically by WalletStorage
    );

    console.log(`✅ Local wallet created and stored: ${this.walletAddress}`);

    return {
      address: this.walletAddress,
      network: this.network,
      x402Endpoint: this.getX402Endpoint(),
    };
  }

  /**
   * Wrap async operation with timeout
   */
  private withTimeout<T>(promise: Promise<T>, timeoutMs: number, timeoutMessage: string): Promise<T> {
    return Promise.race([
      promise,
      new Promise<T>((_, reject) =>
        setTimeout(() => reject(new Error(timeoutMessage)), timeoutMs)
      ),
    ]);
  }

  /**
   * Simple hash function for deterministic mock addresses (testing only)
   */
  private simpleHash(input: string): string {
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(40, '0');
  }

  /**
   * Generate deterministic UUID v4 from userId
   *
   * CDP requires UUID v4 format for idempotency keys
   * We create a deterministic UUID so same user always gets same wallet
   */
  private generateDeterministicUUID(input: string): string {
    const crypto = require('crypto');

    // Create a hash from the input
    const hash = crypto.createHash('sha256').update(input).digest('hex');

    // Format as UUID v4: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
    // Where x is any hexadecimal digit and y is one of 8, 9, A, or B
    const uuid = [
      hash.substr(0, 8),
      hash.substr(8, 4),
      '4' + hash.substr(12, 3), // Version 4
      ((parseInt(hash.substr(16, 1), 16) & 0x3) | 0x8).toString(16) + hash.substr(17, 3), // Variant bits
      hash.substr(20, 12)
    ].join('-');

    return uuid;
  }

  /**
   * Get default RPC URL based on network
   */
  private getDefaultRpcUrl(): string {
    // Public RPC endpoints for Base network
    if (this.network === 'base-mainnet') {
      return 'https://mainnet.base.org';
    } else {
      return 'https://sepolia.base.org';
    }
  }

  /**
   * Get agent's wallet address
   */
  getAddress(): string {
    if (!this.walletAddress) {
      throw new Error('Agent wallet not initialized. Call initialize() first.');
    }
    return this.walletAddress;
  }

  /**
   * Get agent's X402 payment endpoint
   *
   * This endpoint can receive X402 payments from other agents or users
   */
  getX402Endpoint(): string {
    if (!this.walletAddress) {
      throw new Error('Agent wallet not initialized');
    }

    // Format: x402.bloomprotocol.ai/base/{address}
    // Note: This assumes Bloom has registered this agent wallet
    // In production, this should be obtained from Bloom backend after registration
    const networkPath = this.network.includes('sepolia') ? 'base-sepolia' : 'base';
    return `https://x402.bloomprotocol.ai/${networkPath}/${this.walletAddress}`;
  }

  /**
   * Get wallet balance (USDC)
   */
  async getBalance(): Promise<string> {
    if (!this.walletProvider) {
      throw new Error('Agent wallet not initialized');
    }

    try {
      // Note: Balance checking requires additional setup with CDP SDK
      // For MVP, returning '0'
      return '0';
    } catch (error) {
      console.error('❌ Failed to get balance:', error);
      return '0';
    }
  }

  /**
   * Execute X402 payment to another endpoint
   *
   * @param to - X402 endpoint URL (e.g., x402.bloomprotocol.ai/base/123)
   * @param amount - Amount in USDC
   */
  async sendX402Payment(to: string, amount: number): Promise<string> {
    if (!this.walletProvider) {
      throw new Error('Agent wallet not initialized');
    }

    console.log(`💸 Sending ${amount} USDC via X402 to ${to}...`);

    try {
      // Note: X402 payment integration requires additional setup
      // For MVP, this is a placeholder
      throw new Error('X402 payment not yet implemented in MVP');
    } catch (error) {
      console.error('❌ X402 payment failed:', error);
      throw new Error(`X402 payment failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Register agent wallet with Bloom Protocol backend and save identity card
   *
   * This creates an agent user in Bloom system, associates the wallet,
   * and stores the identity card data in one atomic operation
   */
  async registerWithBloom(
    agentName: string,
    identityData?: {
      personalityType: string;
      tagline: string;
      description: string;
      mainCategories: string[];
      subCategories: string[];
      confidence: number;
      mode: 'data' | 'manual';
      dimensions?: {
        conviction: number;
        intuition: number;
        contribution: number;
      };
      recommendations?: Array<{
        skillId: string;
        skillName: string;
        description: string;
        url: string;
        categories: string[];
        matchScore: number;
        creator?: string;
        creatorUserId?: number | string;
        source?: 'ClawHub' | 'ClaudeCode' | 'GitHub';
        stars?: number;
        language?: string;
      }>;
    }
  ): Promise<{ agentUserId: number; x402Endpoint: string }> {
    if (!this.walletAddress) {
      throw new Error('Agent wallet not initialized');
    }

    console.log(`📝 Registering agent with Bloom Protocol...`);

    try {
      // Generate nonce and timestamp for message
      const nonce = crypto.randomUUID();
      const timestamp = Date.now();

      // Sign a message to prove wallet ownership (include nonce and timestamp)
      const message = `Bloom Agent Registration\nAgent: ${agentName}\nNonce: ${nonce}\nTimestamp: ${timestamp}`;
      const signature = await this.signMessage(message);

      // Call Bloom backend API with identity data
      const response = await fetch(`${process.env.BLOOM_API_URL || 'https://api.bloomprotocol.ai'}/x402/agent-claim`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agentName,
          agentType: 'skill-discovery',
          walletAddress: this.walletAddress,
          network: this.network,
          signature,
          message,
          nonce,
          timestamp,
          identityData, // Include identity card data
        }),
      });

      if (!response.ok) {
        if (response.status === 409) {
          // Already registered — extract existing agentUserId from response
          const body = await response.json().catch(() => null);
          if (body?.data?.agentUserId) {
            console.log(`✅ Agent already registered (userId: ${body.data.agentUserId})`);
            return {
              agentUserId: body.data.agentUserId,
              x402Endpoint: body.data.x402Endpoint || '',
            };
          }
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'Registration failed');
      }

      console.log(`✅ Agent registered! User ID: ${result.data.agentUserId}`);

      return {
        agentUserId: result.data.agentUserId,
        x402Endpoint: result.data.x402Endpoint,
      };
    } catch (error) {
      console.debug('Bloom registration failed:', error);
      throw new Error(`Bloom registration failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Sign a message with agent's wallet
   *
   * Supports both CDP wallets and local wallets
   */
  async signMessage(message: string): Promise<string> {
    try {
      // CDP wallet (if available)
      if (this.walletProvider) {
        const signature = await this.walletProvider.signMessage(message);
        return signature;
      }

      // Local wallet (viem)
      if (this.localAccount) {
        const signature = await this.localAccount.signMessage({ message });
        return signature;
      }

      throw new Error('No wallet available for signing (neither CDP nor local)');
    } catch (error) {
      console.debug('Sign message failed:', error);
      throw new Error(`Message signing failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate authentication token for Dashboard login
   *
   * Creates a secure JWT token with signature verification
   * for Agent to access Bloom Dashboard
   */
  async generateAuthToken(options?: {
    agentUserId?: number;
    identityData?: {
      personalityType: string;
      tagline: string;
      description: string;
      mainCategories: string[];
      subCategories: string[];
      confidence: number;
      mode: 'data' | 'manual';
    };
  }): Promise<string> {
    if (!this.walletAddress) {
      throw new Error('Agent wallet not initialized');
    }

    const crypto = await import('crypto');
    const jwtModule = await import('jsonwebtoken');
    const jwt = jwtModule.default;

    const nonce = crypto.randomUUID();
    const timestamp = Date.now();
    const expiresAt = timestamp + 24 * 60 * 60 * 1000; // 24 hours

    // Construct message to sign (EIP-191 standard)
    const message = [
      'Bloom Agent Authentication',
      `Address: ${this.walletAddress}`,
      `Nonce: ${nonce}`,
      `Timestamp: ${timestamp}`,
      `Expires: ${expiresAt}`,
      'Scope: read:identity,read:skills,read:wallet',
    ].join('\n');

    // Sign the message
    const signature = await this.signMessage(message);

    // Create JWT payload with optional identity data
    const payload: any = {
      type: 'agent',
      version: '1.0',
      address: this.walletAddress,
      nonce,
      timestamp,
      expiresAt,
      scope: ['read:identity', 'read:skills', 'read:wallet'],
      signature,
      signedMessage: message,
    };

    // Add optional fields
    if (options?.agentUserId) {
      payload.agentUserId = options.agentUserId;
    }
    if (options?.identityData) {
      payload.identity = {
        personalityType: options.identityData.personalityType,
        tagline: options.identityData.tagline,
        description: options.identityData.description,
        mainCategories: options.identityData.mainCategories,
        subCategories: options.identityData.subCategories,
        confidence: options.identityData.confidence,
        mode: options.identityData.mode,
      };
    }

    // Sign JWT
    const token = jwt.sign(payload, process.env.JWT_SECRET || 'dev-secret-change-in-production', {
      algorithm: 'HS256',
      expiresIn: '24h',
      issuer: 'bloom-protocol',
      audience: 'bloom-dashboard',
    });

    return token;
  }

  /**
   * Save identity to Bloom WITHOUT wallet signature (fallback for wallet-free users)
   * Uses POST /x402/agent-save endpoint
   */
  async saveIdentityWithBloom(
    agentName: string,
    identityData: {
      personalityType: string;
      tagline: string;
      description: string;
      mainCategories: string[];
      subCategories: string[];
      confidence: number;
      mode: 'data' | 'manual';
      dimensions?: {
        conviction: number;
        intuition: number;
        contribution: number;
      };
      recommendations?: Array<{
        skillId: string;
        skillName: string;
        description: string;
        url: string;
        categories: string[];
        matchScore: number;
        creator?: string;
        creatorUserId?: number | string;
        source?: 'ClawHub' | 'ClaudeCode' | 'GitHub';
        stars?: number;
        language?: string;
      }>;
    }
  ): Promise<{ agentUserId: number; dashboardUrl: string }> {
    console.log('📝 Saving identity to Bloom (wallet-free)...');

    const response = await fetch(`${process.env.BLOOM_API_URL || 'https://api.bloomprotocol.ai'}/x402/agent-save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        agentName,
        agentType: 'skill-discovery',
        identityData,
        ...(this.walletAddress ? { walletAddress: this.walletAddress, network: this.network } : {}),
      }),
    });

    if (!response.ok) {
      if (response.status === 409) {
        const body = await response.json().catch(() => null);
        if (body?.data?.agentUserId) {
          console.log(`✅ Identity already saved (userId: ${body.data.agentUserId})`);
          return {
            agentUserId: body.data.agentUserId,
            dashboardUrl: body.data.dashboardUrl || '',
          };
        }
      }
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || 'Save failed');
    }

    console.log(`✅ Identity saved! Agent User ID: ${result.data.agentUserId}`);

    return {
      agentUserId: result.data.agentUserId,
      dashboardUrl: result.data.dashboardUrl,
    };
  }

  /**
   * Get wallet info for display
   */
  async getWalletInfo(): Promise<AgentWalletInfo> {
    let balance: string | undefined;

    try {
      balance = await this.getBalance();
    } catch (error) {
      // Balance check may fail if wallet not fully initialized
      console.debug('Could not fetch balance:', error);
      balance = undefined;
    }

    return {
      address: this.getAddress(),
      network: this.network,
      x402Endpoint: this.getX402Endpoint(),
      balance,
    };
  }
}

/**
 * Create and initialize an agent wallet
 *
 * Convenience function for quick setup
 *
 * ⭐ userId is required for per-user wallet management
 */
export async function createAgentWallet(config: AgentWalletConfig): Promise<AgentWallet> {
  const wallet = new AgentWallet(config);
  await wallet.initialize();
  return wallet;
}
