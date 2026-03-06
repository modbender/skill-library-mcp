import * as api from "../api/client.js";

const MOCK_TOKEN_PREFIX = "pc_v1_sand";

function getMockDisclosure(scope = "BROWSE"): string {
  return `This agent is using PayClaw Badge: Agent Intent for Ecommerce. The principal user token is a SHA-256 starting ${MOCK_TOKEN_PREFIX}***. Intent has been expressly user-authorized for this session for [${scope}]. For inquiries, please message agent_identity@payclaw.io`;
}

export interface IdentityResult {
  product_name: string;
  status: string;
  agent_disclosure?: string;
  verification_token?: string;
  trust_url?: string;
  contact?: string;
  principal_verified?: boolean;
  mfa_confirmed?: boolean;
  spend_available?: boolean;
  spend_cta?: string;
  merchant?: string;
  instructions?: string;
  message?: string;
}

export async function getAgentIdentity(merchant?: string): Promise<IdentityResult> {
  if (!process.env.PAYCLAW_API_KEY) {
    return {
      product_name: "PayClaw Badge",
      status: "error",
      message:
        "PAYCLAW_API_KEY is not set. Get your key at payclaw.io/dashboard/badge",
    };
  }

  if (!api.isApiMode()) {
    // Mock mode — return sandbox identity for local testing
    return {
      product_name: "PayClaw Badge",
      status: "active",
      agent_disclosure: getMockDisclosure(),
      verification_token: `${MOCK_TOKEN_PREFIX}********************`,
      trust_url: "https://payclaw.io/trust",
      contact: "agent_identity@payclaw.io",
      principal_verified: true,
      merchant: merchant || undefined,
      instructions:
        "You're running in mock mode — no API connected. Generate your real agent disclosure at payclaw.io/dashboard/badge to get a live verification token.",
    };
  }

  try {
    const result = await api.getAgentIdentity(undefined, merchant);
    return {
      product_name: "PayClaw Badge",
      status: "active",
      merchant: merchant || undefined,
      ...result,
    };
  } catch (err) {
    return {
      product_name: "PayClaw Badge",
      status: "error",
      message: err instanceof Error ? err.message : String(err),
    };
  }
}

/**
 * Format identity result as human-readable text for CLI/agent display.
 * Claude reads this and relays key info naturally to the user.
 */
export function formatIdentityResponse(r: IdentityResult): string {
  if (r.status === "error") {
    return `✗ BADGE ERROR\n\n  ${r.message}`;
  }

  const lines = [
    `✓ DECLARED — Your agent is now an authorized actor`,
    ``,
    `  Token:       ${r.verification_token ? r.verification_token.slice(0, 10) + '**' : 'N/A'}`,
    `  Principal:   ${r.principal_verified ? 'Verified ✓' : 'Unverified'}`,
    `  Scope:       [BROWSE]`,
  ];

  if (r.merchant) {
    lines.push(`  Merchant:    ${r.merchant}`);
  }

  lines.push(
    `  Status:      ACTIVE`,
    `  Trust:       ${r.trust_url || 'https://payclaw.io/trust'}`,
    ``,
    `  Disclosure (present to merchants):`,
    `  "${r.agent_disclosure}"`,
  );

  if (r.spend_available) {
    lines.push(``, `  💳 Spend is available — call payclaw_getCard when ready to pay.`);
  } else if (r.spend_cta) {
    lines.push(``, `  ℹ️  ${r.spend_cta}`);
  } else {
    lines.push(``, `  ℹ️  Identity only. Fund your wallet at payclaw.io to enable payments.`);
  }

  return lines.join('\n');
}
