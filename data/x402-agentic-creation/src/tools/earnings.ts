import { GateX402Client } from "../lib/api-client";
import { wrapAgentResponse } from "../types";

/** Sanitized balance shape: only numeric/string and known keys (API may return numbers as strings). */
interface SanitizedBalance {
  total_balance_usdc_6?: number | string;
  total_balance_usdc?: string;
  by_network?: Record<string, { balance_usdc_6?: string; balance_usdc?: string }>;
  status?: string;
}

export interface GetEarningsCredentials {
  getManagementToken: () => Promise<string>;
}

/**
 * Get current USDC balance. Response is sanitized and wrapped to mitigate prompt injection.
 */
export async function getEarnings(
  credentials: GetEarningsCredentials
): Promise<string> {
  if (!credentials.getManagementToken) {
    return wrapAgentResponse({
      message: "No management token configured. Provision an API first.",
    });
  }
  const managementToken = await credentials.getManagementToken();
  if (!managementToken) {
    return wrapAgentResponse({
      message: "No management token configured. Provision an API first.",
    });
  }
  const client = new GateX402Client(managementToken);
  const raw = await client.get("/agent/payout/balance");

  const sanitized: SanitizedBalance = {};
  if (typeof raw.total_balance_usdc_6 === "number" || typeof raw.total_balance_usdc_6 === "string") {
    sanitized.total_balance_usdc_6 = raw.total_balance_usdc_6;
  }
  if (typeof raw.total_balance_usdc === "string") {
    sanitized.total_balance_usdc = raw.total_balance_usdc;
  }
  if (raw.balances_by_network && typeof raw.balances_by_network === "object") {
    sanitized.by_network = {};
    for (const [k, v] of Object.entries(raw.balances_by_network)) {
      if (v && typeof v === "object" && !Array.isArray(v)) {
        const entry = v as Record<string, unknown>;
        sanitized.by_network![k] = {
          ...(typeof entry.balance_usdc_6 === "string" && { balance_usdc_6: entry.balance_usdc_6 }),
          ...(typeof entry.balance_usdc === "string" && { balance_usdc: entry.balance_usdc }),
        };
      }
    }
  }
  if (typeof raw.status === "string") {
    sanitized.status = raw.status;
  }

  return wrapAgentResponse(sanitized);
}
