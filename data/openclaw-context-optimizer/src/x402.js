/**
 * x402 Payment Protocol Integration for OpenClaw Context Optimizer
 *
 * Enables AI agents to autonomously pay for Pro tier (unlimited compressions)
 * via the x402 HTTP payment protocol
 *
 * Pricing: 0.5 USDT/month on Base chain
 */

import { randomUUID } from 'crypto';

export class X402PaymentHandler {
  constructor(storage) {
    this.storage = storage;

    // Pricing configuration
    this.pricing = {
      pro_monthly: {
        amount: 0.5,
        token: 'USDT',
        chain: 'base',
        duration_months: 1
      }
    };

    // Supported tokens and chains
    this.supportedTokens = ['USDT', 'USDC', 'SOL'];
    this.supportedChains = ['base', 'solana', 'ethereum'];
  }

  /**
   * Generate x402 payment request
   * For agents to pay for Pro tier (unlimited compressions)
   */
  async createPaymentRequest(agentWallet, tier = 'pro_monthly') {
    const pricing = this.pricing[tier];

    if (!pricing) {
      throw new Error(`Invalid tier: ${tier}`);
    }

    const requestId = randomUUID();

    // Store payment request using storage method
    this.storage.recordPaymentRequest(requestId, agentWallet, pricing.amount, pricing.token);

    // x402 payment request format
    return {
      protocol: 'x402',
      version: '1.0',
      request_id: requestId,
      recipient: process.env.PAYMENT_WALLET || 'YOUR_WALLET_ADDRESS',
      amount: pricing.amount,
      token: pricing.token,
      chain: pricing.chain,
      description: `OpenClaw Context Optimizer - Pro tier (unlimited compressions)`,
      callback_url: process.env.PAYMENT_CALLBACK_URL || 'http://localhost:9092/api/x402/verify',
      expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours
    };
  }

  /**
   * Verify x402 payment and grant Pro tier
   * Called when agent reports payment completion
   */
  async verifyPayment(requestId, txHash, agentWallet) {
    // Get payment request
    const request = this.storage.getPaymentRequest(requestId);

    if (!request) {
      throw new Error('Payment request not found');
    }

    if (request.status === 'completed') {
      throw new Error('Payment already processed');
    }

    // In production, verify transaction on-chain
    // For MVP, we'll trust the agent (could add on-chain verification via RPC)
    const verified = await this.verifyTransactionOnChain(txHash);

    if (!verified) {
      throw new Error('Transaction verification failed');
    }

    // Update payment request
    this.storage.updatePaymentRequest(requestId, 'completed', txHash);

    // Record transaction
    this.storage.recordPaymentTransaction({
      agent_wallet: agentWallet,
      tx_hash: txHash,
      amount: request.amount_requested,
      token: request.token,
      chain: 'base',
      verified: true,
      tier_granted: 'pro',
      duration_months: 1
    });

    // Grant or extend license (unlimited compressions)
    await this.grantLicense(agentWallet, 'pro', 1);

    return {
      success: true,
      tier: 'pro',
      valid_until: this.getLicenseExpiry(agentWallet),
      message: 'Pro tier activated - unlimited compressions'
    };
  }

  /**
   * Grant or extend Pro license with unlimited compressions
   */
  async grantLicense(agentWallet, tier, durationMonths) {
    const existing = this.storage.getQuota(agentWallet);

    const now = new Date();
    let paidUntil;

    if (existing && existing.paid_until && new Date(existing.paid_until) > now) {
      // Extend existing license
      paidUntil = new Date(existing.paid_until);
      paidUntil.setMonth(paidUntil.getMonth() + durationMonths);
    } else {
      // New license
      paidUntil = new Date(now);
      paidUntil.setMonth(paidUntil.getMonth() + durationMonths);
    }

    // Update agent tier using storage method
    this.storage.updateAgentTier(agentWallet, tier, paidUntil.toISOString());

    return paidUntil;
  }

  /**
   * Check if agent has valid Pro license
   */
  hasValidLicense(agentWallet) {
    const quota = this.storage.getQuota(agentWallet);

    if (!quota) {
      return { valid: false, tier: 'free' };
    }

    if (quota.tier === 'free' || !quota.paid_until) {
      return { valid: false, tier: 'free' };
    }

    const now = new Date();
    const expiry = new Date(quota.paid_until);

    if (expiry > now) {
      return {
        valid: true,
        tier: quota.tier,
        expires: expiry.toISOString(),
        days_remaining: Math.ceil((expiry - now) / (1000 * 60 * 60 * 24))
      };
    }

    return { valid: false, tier: 'expired', expired: true };
  }

  /**
   * Get license expiry date
   */
  getLicenseExpiry(agentWallet) {
    const quota = this.storage.getQuota(agentWallet);
    return quota?.paid_until || null;
  }

  /**
   * Verify transaction on-chain
   * In production, this would check the actual blockchain
   */
  async verifyTransactionOnChain(txHash) {
    // TODO: Implement actual on-chain verification via RPC
    // For MVP, we'll accept any transaction hash
    //
    // In production:
    // 1. Connect to Base RPC
    // 2. Query transaction by hash
    // 3. Verify recipient, amount, token
    // 4. Check confirmation status

    console.log(`[x402] Verifying transaction: ${txHash}`);
    console.log('[x402] Note: On-chain verification not implemented in MVP');

    // For MVP, trust any valid-looking transaction hash
    return txHash && txHash.length > 32;
  }

  /**
   * Get payment statistics
   */
  getPaymentStats() {
    const totalRevenue = this.storage.db.prepare(`
      SELECT
        COUNT(*) as transaction_count,
        SUM(amount) as total_revenue,
        COUNT(DISTINCT agent_wallet) as unique_payers
      FROM payment_transactions
      WHERE verified = 1
    `).get();

    const activeSubscriptions = this.storage.db.prepare(`
      SELECT COUNT(*) as count
      FROM agent_optimizer_quotas
      WHERE tier = 'pro' AND paid_until > datetime('now')
    `).get();

    return {
      ...totalRevenue,
      active_subscriptions: activeSubscriptions.count
    };
  }
}
