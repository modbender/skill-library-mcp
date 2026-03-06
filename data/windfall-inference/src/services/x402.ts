import { config } from '../config';

// x402 Payment Protocol support
// Spec: https://x402.org — HTTP 402 with USDC payment on Base

const FACILITATOR_URL = process.env.X402_FACILITATOR_URL || 'https://x402.org/facilitator';
const X402_VERSION = 2;

/**
 * Build the x402 PaymentRequired object for a given price.
 * This gets base64-encoded into the PAYMENT-REQUIRED response header.
 */
export function buildPaymentRequired(priceUsd: number) {
  // USDC has 6 decimals: $0.004 = 4000 atomic units
  const maxAmountRequired = String(Math.round(priceUsd * 1e6));

  return {
    x402Version: X402_VERSION,
    accepts: [
      {
        scheme: 'exact',
        network: 'eip155:8453', // Base mainnet
        maxAmountRequired,
        resource: '/v1/chat/completions',
        description: 'LLM inference via Windfall spatial routing',
        mimeType: 'application/json',
        payTo: config.walletAddress,
        asset: config.usdcAddress, // USDC on Base
        maxTimeoutSeconds: 60,
      },
    ],
  };
}

/**
 * Encode a PaymentRequired object as a base64 header value.
 */
export function encodePaymentRequiredHeader(paymentRequired: object): string {
  return Buffer.from(JSON.stringify(paymentRequired), 'utf-8').toString('base64');
}

/**
 * Decode the payment-signature header from base64 JSON.
 */
export function decodePaymentSignature(headerValue: string): any {
  try {
    const decoded = Buffer.from(headerValue, 'base64').toString('utf-8');
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

/**
 * Encode a settlement response as a base64 header value.
 */
export function encodePaymentResponseHeader(response: object): string {
  return Buffer.from(JSON.stringify(response), 'utf-8').toString('base64');
}

/**
 * Verify and settle an x402 payment via the Coinbase facilitator.
 * Returns the payer address and tx hash on success.
 */
export async function verifyAndSettleX402(
  paymentPayload: any,
  priceUsd: number,
): Promise<{
  valid: boolean;
  payer?: string;
  txHash?: string;
  error?: string;
}> {
  const paymentRequirements = buildPaymentRequired(priceUsd).accepts[0];

  try {
    // Step 1: Verify
    const verifyRes = await fetch(`${FACILITATOR_URL}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        x402Version: paymentPayload.x402Version || X402_VERSION,
        paymentPayload,
        paymentRequirements,
      }),
      signal: AbortSignal.timeout(15000),
    });

    const verifyData = await verifyRes.json() as any;
    if (!verifyRes.ok || !verifyData.isValid) {
      return {
        valid: false,
        error: verifyData.invalidReason || `Verification failed (${verifyRes.status})`,
      };
    }

    // Step 2: Settle
    const settleRes = await fetch(`${FACILITATOR_URL}/settle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        x402Version: paymentPayload.x402Version || X402_VERSION,
        paymentPayload,
        paymentRequirements,
      }),
      signal: AbortSignal.timeout(30000),
    });

    const settleData = await settleRes.json() as any;
    if (!settleRes.ok || !settleData.success) {
      return {
        valid: false,
        error: settleData.errorReason || `Settlement failed (${settleRes.status})`,
      };
    }

    console.log(`[x402] Payment settled: ${settleData.transaction} from ${settleData.payer}`);
    return {
      valid: true,
      payer: settleData.payer,
      txHash: settleData.transaction,
    };
  } catch (err: any) {
    console.error('[x402] Facilitator error:', err.message);
    return {
      valid: false,
      error: 'Facilitator unavailable',
    };
  }
}
