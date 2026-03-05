/**
 * x402 Payment Protocol Integration for OpenClaw Smart Router
 *
 * Enables AI agents to autonomously pay for Pro tier (unlimited routing decisions)
 * via the x402 HTTP payment protocol
 *
 * Pricing: 0.5 USDT/month on Base chain
 *
 * Tiers:
 * - Free: 100 routing decisions/day
 * - Pro: Unlimited decisions + ML-enhanced pattern learning
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

    // Quota limits
    this.quotaLimits = {
      free: 100,      // 100 decisions per day
      pro: -1         // -1 = unlimited
    };
  }

  /**
   * Generate x402 payment request
   * For agents to pay for Pro tier (unlimited routing decisions)
   */
  async createPaymentRequest(agentWallet, tier = 'pro_monthly') {
    const pricing = this.pricing[tier];

    if (!pricing) {
      throw new Error(`Invalid tier: ${tier}`);
    }

    const requestId = randomUUID();

    // Store payment request
    const stmt = this.storage.db.prepare(`
      INSERT INTO payment_requests (request_id, agent_wallet, amount_requested, token, status)
      VALUES (?, ?, ?, ?, 'pending')
    `);

    stmt.run(requestId, agentWallet, pricing.amount, pricing.token);

    // x402 payment request format
    return {
      protocol: 'x402',
      version: '1.0',
      request_id: requestId,
      recipient: process.env.PAYMENT_WALLET || 'YOUR_WALLET_ADDRESS',
      amount: pricing.amount,
      token: pricing.token,
      chain: pricing.chain,
      description: `OpenClaw Smart Router - Pro tier (unlimited routing + ML enhancements)`,
      callback_url: process.env.PAYMENT_CALLBACK_URL || 'http://localhost:9091/api/x402/verify',
      expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours
    };
  }

  /**
   * Verify x402 payment and grant Pro tier
   * Called when agent reports payment completion
   */
  async verifyPayment(requestId, txHash, agentWallet) {
    // Get payment request
    const request = this.storage.db.prepare(`
      SELECT * FROM payment_requests WHERE request_id = ?
    `).get(requestId);

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
    this.storage.db.prepare(`
      UPDATE payment_requests
      SET status = 'completed', completed_at = datetime('now'), tx_hash = ?
      WHERE request_id = ?
    `).run(txHash, requestId);

    // Record transaction
    this.storage.db.prepare(`
      INSERT INTO payment_transactions
      (agent_wallet, tx_hash, amount, token, chain, verified, tier_granted, duration_months)
      VALUES (?, ?, ?, ?, ?, 1, 'pro', 1)
    `).run(agentWallet, txHash, request.amount_requested, request.token, 'base');

    // Grant or extend license (unlimited decisions)
    await this.grantLicense(agentWallet, 'pro', 1);

    return {
      success: true,
      tier: 'pro',
      valid_until: this.getLicenseExpiry(agentWallet),
      message: 'Pro tier activated - unlimited routing decisions + ML enhancements'
    };
  }

  /**
   * Grant or extend Pro license with unlimited decisions
   */
  async grantLicense(agentWallet, tier, durationMonths) {
    const existing = this.storage.db.prepare(`
      SELECT * FROM agent_router_quotas WHERE agent_wallet = ?
    `).get(agentWallet);

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

    if (existing) {
      this.storage.db.prepare(`
        UPDATE agent_router_quotas
        SET tier = ?, decisions_limit = -1, paid_until = ?, updated_at = datetime('now')
        WHERE agent_wallet = ?
      `).run(tier, paidUntil.toISOString(), agentWallet);
    } else {
      this.storage.db.prepare(`
        INSERT INTO agent_router_quotas (agent_wallet, tier, decisions_limit, paid_until)
        VALUES (?, ?, -1, ?)
      `).run(agentWallet, tier, paidUntil.toISOString());
    }

    console.log(`[x402] Granted Pro license to ${agentWallet} until ${paidUntil.toISOString()}`);
    return paidUntil;
  }

  /**
   * Check if agent has valid Pro license
   */
  hasValidLicense(agentWallet) {
    const quota = this.storage.db.prepare(`
      SELECT * FROM agent_router_quotas WHERE agent_wallet = ?
    `).get(agentWallet);

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
    const quota = this.storage.db.prepare(`
      SELECT paid_until FROM agent_router_quotas WHERE agent_wallet = ?
    `).get(agentWallet);

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
   * Check quota and increment if available
   */
  checkAndIncrementQuota(agentWallet) {
    // Get or create quota record
    let quota = this.storage.db.prepare(`
      SELECT * FROM agent_router_quotas WHERE agent_wallet = ?
    `).get(agentWallet);

    if (!quota) {
      // Create new free tier quota
      this.storage.db.prepare(`
        INSERT INTO agent_router_quotas
        (agent_wallet, tier, decisions_limit, decisions_today, last_reset_date)
        VALUES (?, 'free', 100, 0, date('now'))
      `).run(agentWallet);

      quota = this.storage.db.prepare(`
        SELECT * FROM agent_router_quotas WHERE agent_wallet = ?
      `).get(agentWallet);
    }

    // Check if quota needs to be reset (new day)
    const today = new Date().toISOString().split('T')[0];
    const lastReset = quota.last_reset_date;

    if (lastReset !== today) {
      // Reset daily counter
      this.storage.db.prepare(`
        UPDATE agent_router_quotas
        SET decisions_today = 0, last_reset_date = date('now')
        WHERE agent_wallet = ?
      `).run(agentWallet);
      quota.decisions_today = 0;
    }

    // Check if quota available
    const hasProLicense = this.hasValidLicense(agentWallet);

    if (hasProLicense.valid) {
      // Pro tier: unlimited
      this.storage.db.prepare(`
        UPDATE agent_router_quotas
        SET decisions_today = decisions_today + 1
        WHERE agent_wallet = ?
      `).run(agentWallet);

      return {
        available: true,
        tier: 'pro',
        remaining: -1,
        decisions_today: quota.decisions_today + 1
      };
    }

    // Free tier: check limit
    if (quota.decisions_today >= quota.decisions_limit) {
      return {
        available: false,
        tier: 'free',
        remaining: 0,
        decisions_today: quota.decisions_today,
        limit: quota.decisions_limit,
        message: `Daily quota exceeded (${quota.decisions_limit}/day). Upgrade to Pro for unlimited decisions.`
      };
    }

    // Increment counter
    this.storage.db.prepare(`
      UPDATE agent_router_quotas
      SET decisions_today = decisions_today + 1
      WHERE agent_wallet = ?
    `).run(agentWallet);

    return {
      available: true,
      tier: 'free',
      remaining: quota.decisions_limit - quota.decisions_today - 1,
      decisions_today: quota.decisions_today + 1,
      limit: quota.decisions_limit
    };
  }

  /**
   * Get quota status for an agent
   */
  getQuotaStatus(agentWallet) {
    let quota = this.storage.db.prepare(`
      SELECT * FROM agent_router_quotas WHERE agent_wallet = ?
    `).get(agentWallet);

    if (!quota) {
      return {
        tier: 'free',
        decisions_today: 0,
        decisions_limit: 100,
        remaining: 100
      };
    }

    // Check if quota needs to be reset (new day)
    const today = new Date().toISOString().split('T')[0];
    const lastReset = quota.last_reset_date;

    if (lastReset !== today) {
      quota.decisions_today = 0;
    }

    const hasProLicense = this.hasValidLicense(agentWallet);

    return {
      tier: hasProLicense.valid ? 'pro' : 'free',
      decisions_today: quota.decisions_today,
      decisions_limit: hasProLicense.valid ? -1 : quota.decisions_limit,
      remaining: hasProLicense.valid ? -1 : Math.max(0, quota.decisions_limit - quota.decisions_today),
      license: hasProLicense
    };
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
      FROM agent_router_quotas
      WHERE tier = 'pro' AND paid_until > datetime('now')
    `).get();

    return {
      ...totalRevenue,
      active_subscriptions: activeSubscriptions.count
    };
  }

  /**
   * Get payment history for an agent
   */
  getPaymentHistory(agentWallet) {
    return this.storage.db.prepare(`
      SELECT * FROM payment_transactions
      WHERE agent_wallet = ?
      ORDER BY timestamp DESC
    `).all(agentWallet);
  }
}
