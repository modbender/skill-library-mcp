/**
 * Skill Creator Tipping Module
 *
 * Uses existing X402 infrastructure from Bloom Protocol Backend
 * Does NOT modify the original X402 system (reserved for Bloom Mission Bot)
 *
 * References:
 * - Backend: /bloom-protocol-be/src/modules/x402/x402-client.service.ts
 * - CDP SDK: x402-axios (already installed)
 * - Network: Base (TestPaymentNetwork.BASE)
 */

import axios, { AxiosInstance } from 'axios';

export interface SkillCreatorTipRequest {
  skillId: string;
  skillName: string;
  creatorUserId: number;  // Bloom Protocol user ID
  amount: number;         // USDT amount
}

export interface TipResult {
  skillId: string;
  skillName: string;
  creatorUserId: number;
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

/**
 * Skill Creator Tipping Service
 *
 * Sends tips to skill creators using x402 protocol on Base network
 * Reuses the existing Bloom Protocol X402 infrastructure
 */
export class SkillCreatorTip {
  private readonly x402WorkerBaseUrl: string;
  private readonly network = 'base'; // Always use Base for skill tipping

  constructor(config?: { x402WorkerUrl?: string }) {
    // Use existing X402 worker endpoint
    this.x402WorkerBaseUrl = config?.x402WorkerUrl ||
                              process.env.X402_WORKER_BASE_URL ||
                              'https://x402.bloomprotocol.ai';
  }

  /**
   * Execute batch tips to multiple skill creators
   *
   * Uses the existing X402 CDP SDK client from backend
   * Endpoint format: /{network}/{userId}?amount={amount}
   */
  async batchTip(
    tipRequests: SkillCreatorTipRequest[]
  ): Promise<BatchTipResult> {
    console.log(`💰 Processing ${tipRequests.length} skill creator tips...`);

    const results: TipResult[] = [];
    let totalAmount = 0;

    for (const tip of tipRequests) {
      try {
        console.log(`  → Tipping ${tip.amount} USDT to ${tip.skillName} creator (userId: ${tip.creatorUserId})`);

        const result = await this.executeSingleTip(
          tip.creatorUserId,
          tip.amount
        );

        results.push({
          skillId: tip.skillId,
          skillName: tip.skillName,
          creatorUserId: tip.creatorUserId,
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
          creatorUserId: tip.creatorUserId,
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
   *
   * Calls the existing X402 worker endpoint
   * The backend handles:
   * - CDP SDK initialization
   * - Base network client
   * - x402 payment interceptor
   * - Transaction signing and broadcasting
   */
  private async executeSingleTip(
    creatorUserId: number,
    amount: number
  ): Promise<{ transactionHash: string }> {
    // Use the same endpoint pattern as existing X402 system
    // Format: /{network}/{userId}?amount={amount}
    const endpoint = `${this.x402WorkerBaseUrl}/${this.network}/${creatorUserId}`;

    try {
      // Make request to X402 worker
      // The CDP SDK client (already initialized in backend) will:
      // 1. Detect 402 Payment Required response
      // 2. Sign and send payment transaction on Base
      // 3. Retry request with X-PAYMENT header
      // 4. Return X-PAYMENT-RESPONSE with transaction hash
      const response = await axios.get(endpoint, {
        params: { amount },
        headers: {
          'Access-Control-Expose-Headers': 'X-PAYMENT-RESPONSE',
        },
      });

      // Extract transaction hash from X-PAYMENT-RESPONSE header
      const paymentResponseHeader = response.headers['x-payment-response'];
      if (paymentResponseHeader) {
        const paymentResponse = this.decodePaymentResponse(paymentResponseHeader);
        return {
          transactionHash: paymentResponse.transaction || 'pending',
        };
      }

      // Fallback: payment completed but no response header
      return {
        transactionHash: 'completed',
      };
    } catch (error: any) {
      // Enhanced error handling
      const errorMessage = error.response?.data?.error?.message ||
                          error.response?.data?.message ||
                          error.message ||
                          'Payment failed';

      throw new Error(errorMessage);
    }
  }

  /**
   * Decode X-PAYMENT-RESPONSE header
   * Format: base64 encoded JSON
   */
  private decodePaymentResponse(header: string): any {
    try {
      const decoded = Buffer.from(header, 'base64').toString('utf-8');
      return JSON.parse(decoded);
    } catch (error) {
      console.warn('Failed to decode payment response header');
      return {};
    }
  }

  /**
   * Validate tip request before execution
   */
  static validateTipRequest(request: SkillCreatorTipRequest): { valid: boolean; error?: string } {
    // Check user ID
    if (!request.creatorUserId || request.creatorUserId <= 0) {
      return { valid: false, error: 'Invalid creator user ID' };
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
    requests: SkillCreatorTipRequest[],
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
   * Format tip results for user display
   */
  static formatTipResults(result: BatchTipResult): string {
    const { successfulTips, failedTips, totalAmount, totalSkills } = result;

    let message = `💰 Skill Creator Tipping Complete!\n\n`;
    message += `✅ ${successfulTips.length}/${totalSkills} tips successful\n`;
    message += `💵 Total tipped: $${totalAmount} USDT\n`;
    message += `⛓️  Network: Base\n\n`;

    if (successfulTips.length > 0) {
      message += `**Successful Tips:**\n`;
      successfulTips.forEach(tip => {
        message += `  • ${tip.skillName}: $${tip.amount}\n`;
        message += `    Creator: userId ${tip.creatorUserId}\n`;
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

/**
 * Helper: Convert skill recommendations to tip requests
 */
export function prepareTipRequests(
  selectedSkills: Array<{ skillId: string; amount: number }>,
  allSkills: Array<{
    skillId: string;
    skillName: string;
    creator: string;
    creatorUserId?: number;
  }>
): SkillCreatorTipRequest[] {
  return selectedSkills
    .map(selection => {
      const skill = allSkills.find(s => s.skillId === selection.skillId);
      if (!skill || !skill.creatorUserId) {
        console.warn(`⚠️  Skill ${selection.skillId} not found or missing creator userId`);
        return null;
      }

      return {
        skillId: skill.skillId,
        skillName: skill.skillName,
        creatorUserId: skill.creatorUserId,
        amount: selection.amount,
      };
    })
    .filter((req): req is SkillCreatorTipRequest => req !== null);
}
