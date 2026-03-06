// ═══════════════════════════════════════════════════════════════════
// SolPaw — OpenClaw Agent Skill
// Drop-in skill for OpenClaw agents to launch tokens on Pump.fun.
// Install: openclaw skills install solpaw-launcher
//
// Launch flow:
//   1. Agent sends 0.1 SOL to platform wallet
//   2. Agent calls launchToken() with the tx signature
//   3. Server verifies the payment onchain, then launches
//   4. No ongoing fees ever.
// ═══════════════════════════════════════════════════════════════════

interface SolPawConfig {
  apiEndpoint: string;
  apiKey: string;
  defaultCreatorWallet: string;
}

interface TokenLaunchParams {
  name: string;
  symbol: string;
  description: string;
  launch_fee_signature: string; // tx sig of 0.1 SOL payment to platform wallet
  image_url?: string;
  creator_wallet?: string;
  twitter?: string;
  telegram?: string;
  website?: string;
  initial_buy_sol?: number;
  slippage?: number;
  priority_fee?: number;
}

interface LaunchResult {
  success: boolean;
  mint?: string;
  signature?: string;
  pumpfun_url?: string;
  solscan_url?: string;
  error?: string;
  launch_fee?: {
    amount_sol: number;
    platform_wallet: string;
    payment_signature: string;
  };
}

interface PlatformInfo {
  platform_wallet: string;
  launch_fee_sol: number;
  daily_limit: number;
}

/**
 * SolPaw Launch Skill for OpenClaw Agents
 *
 * Usage in agent config:
 *   skills:
 *     - name: solpaw-launcher
 *       config:
 *         api_endpoint: https://api.solpaw.fun/api/v1
 *         api_key: ${SOLPAW_API_KEY}
 *         default_creator_wallet: ${CREATOR_WALLET}
 *
 * Launch flow:
 *   1. Call getPlatformInfo() to get the platform wallet address
 *   2. Send 0.1 SOL to the platform wallet (agent handles this via Solana SDK)
 *   3. Call launchToken() with the payment tx signature + token details
 *   4. Server verifies payment onchain → launches token on Pump.fun
 *
 * Agent can then call:
 *   !launch name: MyToken symbol: MTK description: "A cool token" fee_sig: 5xK...
 */
export class SolPawSkill {
  private config: SolPawConfig;
  private csrfToken: string | null = null;
  private csrfExpiresAt: number = 0;

  // Platform wallet cached from /info endpoint
  static readonly PLATFORM_WALLET = "6SoPUBp68Eqhvs3fdx6GdKu5EP44ykqsjh359LyY3ZiS";
  static readonly LAUNCH_FEE_SOL = 0.1;

  constructor(config: SolPawConfig) {
    if (!config.apiEndpoint) throw new Error("SolPaw: apiEndpoint is required");
    if (!config.apiKey) throw new Error("SolPaw: apiKey is required");
    if (!config.defaultCreatorWallet)
      throw new Error("SolPaw: defaultCreatorWallet is required");

    this.config = {
      ...config,
      apiEndpoint: config.apiEndpoint.replace(/\/$/, ""),
    };
  }

  /**
   * Make an authenticated request to the SolPaw API.
   * API key is sent in the Authorization header — never in query params or body.
   */
  private async request<T>(
    method: string,
    path: string,
    body?: Record<string, unknown>,
    headers?: Record<string, string>
  ): Promise<T> {
    const url = `${this.config.apiEndpoint}${path}`;

    const response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.config.apiKey}`,
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(120000), // 2 min timeout for launches
    });

    const data = (await response.json()) as {
      success: boolean;
      data: T;
      error?: { message: string };
    };

    if (!response.ok || !data.success) {
      throw new Error(
        data.error?.message ||
          `API error: ${response.status} ${response.statusText}`
      );
    }

    return data.data;
  }

  /**
   * Get a fresh CSRF token (cached for 25 minutes).
   * Called automatically before any state-changing operation.
   */
  private async getCsrfToken(): Promise<string> {
    // Return cached token if still valid (with 5 min buffer)
    if (this.csrfToken && this.csrfExpiresAt > Date.now() + 5 * 60 * 1000) {
      return this.csrfToken;
    }

    const result = await this.request<{
      csrf_token: string;
      expires_in: number;
    }>("GET", "/agents/csrf");

    this.csrfToken = result.csrf_token;
    this.csrfExpiresAt = Date.now() + result.expires_in * 1000;

    return this.csrfToken;
  }

  /**
   * Get platform info — wallet address, launch fee, and daily limit.
   * Use this to know where to send the 0.1 SOL launch fee.
   */
  async getPlatformInfo(): Promise<PlatformInfo> {
    const result = await this.request<{
      platform_wallet: string;
      launch_fee: {
        amount_sol: number;
        amount_lamports: number;
      };
      guardrails: {
        daily_launch_limit: string;
      };
    }>("GET", "/info");

    return {
      platform_wallet: result.platform_wallet,
      launch_fee_sol: result.launch_fee.amount_sol,
      daily_limit: parseInt(result.guardrails.daily_launch_limit) || 1,
    };
  }

  /**
   * Launch a token on Pump.fun via the SolPaw API.
   *
   * IMPORTANT: Before calling this, the agent must:
   *   1. Send 0.1 SOL to the platform wallet (6SoPUBp68Eqhvs3fdx6GdKu5EP44ykqsjh359LyY3ZiS)
   *   2. Wait for transaction confirmation
   *   3. Pass the transaction signature as launch_fee_signature
   *
   * The server verifies the payment onchain before proceeding.
   * Each signature can only be used once.
   *
   * Fee: 0.1 SOL one-time per launch. No ongoing fees ever.
   */
  async launchToken(params: TokenLaunchParams): Promise<LaunchResult> {
    try {
      // Validate required fields
      if (!params.name || params.name.length < 2) {
        return { success: false, error: "Token name required (min 2 chars)" };
      }
      if (!params.symbol || params.symbol.length < 2) {
        return { success: false, error: "Token symbol required (min 2 chars)" };
      }
      if (!params.description || params.description.length < 10) {
        return {
          success: false,
          error: "Description required (min 10 chars)",
        };
      }
      if (!params.launch_fee_signature) {
        return {
          success: false,
          error:
            "launch_fee_signature is required. Send 0.1 SOL to " +
            SolPawSkill.PLATFORM_WALLET +
            " and pass the tx signature.",
        };
      }

      // Get fresh CSRF token
      const csrfToken = await this.getCsrfToken();

      // Launch via Lightning API
      const result = await this.request<{
        mint: string;
        signature: string;
        pumpfun_url: string;
        solscan_url: string;
        launch_fee: {
          amount_sol: number;
          platform_wallet: string;
          payment_signature: string;
        };
      }>("POST", "/tokens/launch", {
        name: params.name,
        symbol: params.symbol.toUpperCase(),
        description: params.description,
        image_url: params.image_url,
        creator_wallet:
          params.creator_wallet || this.config.defaultCreatorWallet,
        twitter: params.twitter,
        telegram: params.telegram,
        website: params.website,
        initial_buy_sol: params.initial_buy_sol || 0,
        slippage: params.slippage || 10,
        priority_fee: params.priority_fee || 0.0005,
        launch_fee_signature: params.launch_fee_signature,
        csrf_token: csrfToken,
      });

      // Invalidate CSRF token (it's single-use)
      this.csrfToken = null;
      this.csrfExpiresAt = 0;

      return {
        success: true,
        mint: result.mint,
        signature: result.signature,
        pumpfun_url: result.pumpfun_url,
        solscan_url: result.solscan_url,
        launch_fee: result.launch_fee,
      };
    } catch (err) {
      return {
        success: false,
        error: (err as Error).message,
      };
    }
  }

  /**
   * Get the agent's launched tokens.
   */
  async getMyTokens(
    page: number = 1,
    limit: number = 20
  ): Promise<{
    tokens: Array<{
      mint: string;
      name: string;
      symbol: string;
      created_at: string;
      pumpfun_url: string;
    }>;
    total: number;
  }> {
    return this.request("GET", `/tokens?page=${page}&limit=${limit}`);
  }

  /**
   * Get fee summary for the agent's launches.
   */
  async getFeeSummary(): Promise<{
    total_fees_sol: number;
    platform_share_sol: number;
    token_count: number;
  }> {
    return this.request("GET", "/tokens/fees/summary");
  }

  /**
   * Get public platform stats.
   */
  async getPlatformStats(): Promise<Record<string, unknown>> {
    return this.request("GET", "/tokens/stats/platform");
  }
}

// ── Default Export for OpenClaw Skill Loader ─────────────────────
export default SolPawSkill;

// ── Example Usage ───────────────────────────────────────────────
/*
import SolPawSkill from './solpaw-skill';
import { Connection, Keypair, SystemProgram, Transaction, sendAndConfirmTransaction } from '@solana/web3.js';

const solpaw = new SolPawSkill({
  apiEndpoint: 'https://api.solpaw.fun/api/v1',
  apiKey: process.env.SOLPAW_API_KEY!,
  defaultCreatorWallet: 'YourSolanaWallet...',
});

// Step 1: Send 0.1 SOL launch fee to platform wallet
const connection = new Connection('https://api.mainnet-beta.solana.com');
const payer = Keypair.fromSecretKey(...); // your agent's keypair
const feeTx = new Transaction().add(
  SystemProgram.transfer({
    fromPubkey: payer.publicKey,
    toPubkey: new PublicKey(SolPawSkill.PLATFORM_WALLET),
    lamports: 100_000_000, // 0.1 SOL
  })
);
const feeSig = await sendAndConfirmTransaction(connection, feeTx, [payer]);

// Step 2: Launch token with the fee signature
const result = await solpaw.launchToken({
  name: 'CoolToken',
  symbol: 'COOL',
  description: 'The coolest token on Solana, launched by an AI agent',
  image_url: 'https://example.com/cool-token.png',
  twitter: 'https://x.com/cooltoken',
  launch_fee_signature: feeSig, // tx sig from step 1
  initial_buy_sol: 0.5,
});

if (result.success) {
  console.log(`Token launched: ${result.pumpfun_url}`);
  console.log(`Mint: ${result.mint}`);
  console.log(`Launch fee: 0.1 SOL (one-time, no ongoing fees)`);
} else {
  console.error(`Launch failed: ${result.error}`);
}
*/
