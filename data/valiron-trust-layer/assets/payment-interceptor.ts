import { ValironSDK } from '@valiron/sdk';

export type Route = 'prod' | 'prod_throttled' | 'sandbox' | 'sandbox_only';

export type PaymentRequest = {
  requestId: string;
  counterpartyAgentId?: string;
  counterpartyWallet?: string;
  amount: number;
  currency: string;
  rail: 'prod' | 'sandbox';
};

export type PolicyRow = {
  route: Route;
  authorization: 'allow' | 'allow_with_limits' | 'restricted' | 'deny';
  allowedRails: Array<'prod' | 'sandbox'>;
  maxAmountPerPayment: number;
  fallbackMode: 'fail-open-guarded' | 'fail-closed';
};

export type Decision = {
  allow: boolean;
  outcome: PolicyRow['authorization'];
  route: Route | 'unknown';
  reason: string;
};

export async function authorizeOutgoingPayment(
  req: PaymentRequest,
  policy: PolicyRow[],
  sdk = new ValironSDK({ timeout: 5000 }),
): Promise<Decision> {
  try {
    let route: Route;

    if (req.counterpartyAgentId) {
      route = (await sdk.checkAgent(req.counterpartyAgentId)) as Route;
    } else if (req.counterpartyWallet) {
      const profile = await sdk.getWalletProfile(req.counterpartyWallet);
      route = profile.routing.finalRoute as Route;
    } else {
      return { allow: false, outcome: 'deny', route: 'unknown', reason: 'missing counterparty identity' };
    }

    const row = policy.find((p) => p.route === route);
    if (!row) return { allow: false, outcome: 'deny', route, reason: 'no policy for route' };
    if (!row.allowedRails.includes(req.rail)) {
      return { allow: false, outcome: 'deny', route, reason: 'rail not allowed for route' };
    }
    if (req.amount > row.maxAmountPerPayment) {
      return { allow: false, outcome: 'deny', route, reason: 'amount exceeds maxAmountPerPayment' };
    }

    return {
      allow: row.authorization === 'allow' || row.authorization === 'allow_with_limits',
      outcome: row.authorization,
      route,
      reason: 'policy match',
    };
  } catch {
    // Real implementation should branch by error type and endpoint class.
    return { allow: false, outcome: 'deny', route: 'unknown', reason: 'trust lookup unavailable (fail-closed)' };
  }
}
