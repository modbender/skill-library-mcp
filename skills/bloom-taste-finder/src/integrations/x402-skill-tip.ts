/**
 * x402 Skill Tipping Integration
 *
 * Handles batch tipping to skill creators using x402 payment protocol on Base network
 * Reuses existing x402 infrastructure from Bloom Protocol
 */

import { SkillRecommendation } from '../recommender/skill-discovery';

export interface TipRequest {
  skillId: string;
  skillName: string;
  creatorWallet: string;
  amount: number; // in USD
}

export interface TipResult {
  skillId: string;
  skillName: string;
  creatorWallet: string;
  amount: number;
  transactionHash: string;
  status: 'success' | 'failed';
  error?: string;
}

export interface BatchTipResult {
  success: boolean;
  totalAmount: number;
  totalSkills: number;
  successfulTips: TipResult[];
  failedTips: TipResult[];
}

export class X402SkillTip {
  private baseRpcUrl: string;
  private usdtContractAddress: string;
  private x402ApiBase: string;

  constructor(config?: {
    baseRpcUrl?: string;
    usdtContract?: string;
    x402ApiBase?: string;
  }) {
    // Base Sepolia testnet configuration
    this.baseRpcUrl = config?.baseRpcUrl || 'https://sepolia.base.org';
    this.usdtContractAddress = config?.usdtContract || '0x...' // TODO: Add Base USDT contract
    this.x402ApiBase = config?.x402ApiBase || process.env.X402_API_BASE || 'https://api.x402.org';
  }

  /**
   * Execute batch tips to multiple skill creators
   */
  async batchTip(
    userId: string,
    userWalletAddress: string,
    tipRequests: TipRequest[]
  ): Promise<BatchTipResult> {
    console.log(`💰 Processing ${tipRequests.length} skill tips for user ${userId}...`);

    const results: TipResult[] = [];
    let totalAmount = 0;

    for (const tip of tipRequests) {
      try {
        console.log(`  → Tipping ${tip.amount} USD to ${tip.skillName} (${tip.creatorWallet})`);

        const result = await this.executeSingleTip(
          userWalletAddress,
          tip.creatorWallet,
          tip.amount
        );

        results.push({
          skillId: tip.skillId,
          skillName: tip.skillName,
          creatorWallet: tip.creatorWallet,
          amount: tip.amount,
          transactionHash: result.transactionHash,
          status: 'success',
        });

        totalAmount += tip.amount;
        console.log(`  ✅ Tip successful: ${result.transactionHash}`);
      } catch (error) {
        console.error(`  ❌ Tip failed for ${tip.skillName}:`, error);
        results.push({
          skillId: tip.skillId,
          skillName: tip.skillName,
          creatorWallet: tip.creatorWallet,
          amount: tip.amount,
          transactionHash: '',
          status: 'failed',
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }

    const successfulTips = results.filter(r => r.status === 'success');
    const failedTips = results.filter(r => r.status === 'failed');

    console.log(`✅ Batch tip complete: ${successfulTips.length}/${tipRequests.length} successful`);

    return {
      success: successfulTips.length > 0,
      totalAmount,
      totalSkills: tipRequests.length,
      successfulTips,
      failedTips,
    };
  }

  /**
   * Execute a single tip transaction
   */
  private async executeSingleTip(
    fromWallet: string,
    toWallet: string,
    amountUSD: number
  ): Promise<{ transactionHash: string }> {
    // TODO: Integrate with actual x402 payment flow
    // This would:
    // 1. Convert USD to USDT amount (using price oracle)
    // 2. Construct USDT transfer transaction on Base
    // 3. Sign and broadcast transaction
    // 4. Wait for confirmation
    // 5. Record payment via x402 protocol

    // For development, simulate the transaction
    await this.simulatePayment(amountUSD);

    // Mock transaction hash
    const mockTxHash = `0x${Math.random().toString(16).substring(2, 66)}`;

    return {
      transactionHash: mockTxHash,
    };
  }

  /**
   * Convert user's skill selections to tip requests
   */
  static prepareTipRequests(
    selectedSkills: Array<{ skillId: string; amount: number }>,
    allSkills: SkillRecommendation[]
  ): TipRequest[] {
    return selectedSkills
      .map(selection => {
        const skill = allSkills.find(s => s.skillId === selection.skillId);
        if (!skill || !skill.creatorWallet) {
          console.warn(`⚠️  Skill ${selection.skillId} not found or missing wallet`);
          return null;
        }

        return {
          skillId: skill.skillId,
          skillName: skill.skillName,
          creatorWallet: skill.creatorWallet,
          amount: selection.amount,
        };
      })
      .filter((req): req is TipRequest => req !== null);
  }

  /**
   * Validate tip request before execution
   */
  static validateTipRequest(request: TipRequest): { valid: boolean; error?: string } {
    // Check wallet address format
    if (!request.creatorWallet.match(/^0x[a-fA-F0-9]{40}$/)) {
      return { valid: false, error: 'Invalid wallet address format' };
    }

    // Check amount range
    if (request.amount < 1 || request.amount > 10) {
      return { valid: false, error: 'Tip amount must be between $1 and $10' };
    }

    return { valid: true };
  }

  /**
   * Validate batch tip request
   */
  static validateBatchTipRequest(
    requests: TipRequest[],
    maxTotalAmount: number = 20
  ): { valid: boolean; error?: string } {
    if (requests.length === 0) {
      return { valid: false, error: 'No tips selected' };
    }

    if (requests.length > 10) {
      return { valid: false, error: 'Maximum 10 skills per batch' };
    }

    const totalAmount = requests.reduce((sum, req) => sum + req.amount, 0);
    if (totalAmount > maxTotalAmount) {
      return { valid: false, error: `Total amount exceeds $${maxTotalAmount} limit` };
    }

    // Validate each individual request
    for (const request of requests) {
      const validation = this.validateTipRequest(request);
      if (!validation.valid) {
        return { valid: false, error: `${request.skillName}: ${validation.error}` };
      }
    }

    return { valid: true };
  }

  /**
   * Simulate payment delay for development
   */
  private async simulatePayment(amount: number): Promise<void> {
    // Simulate blockchain transaction time
    await new Promise(resolve => setTimeout(resolve, 1500));
  }

  /**
   * Format tip results for user display
   */
  static formatTipResults(result: BatchTipResult): string {
    const { successfulTips, failedTips, totalAmount, totalSkills } = result;

    let message = `💰 Skill Tipping Complete!\n\n`;
    message += `✅ ${successfulTips.length}/${totalSkills} tips successful\n`;
    message += `💵 Total tipped: $${totalAmount}\n\n`;

    if (successfulTips.length > 0) {
      message += `**Successful Tips:**\n`;
      successfulTips.forEach(tip => {
        message += `  • ${tip.skillName}: $${tip.amount}\n`;
        message += `    TX: ${tip.transactionHash.slice(0, 10)}...${tip.transactionHash.slice(-8)}\n`;
      });
    }

    if (failedTips.length > 0) {
      message += `\n**Failed Tips:**\n`;
      failedTips.forEach(tip => {
        message += `  ✗ ${tip.skillName}: ${tip.error}\n`;
      });
    }

    return message;
  }
}
