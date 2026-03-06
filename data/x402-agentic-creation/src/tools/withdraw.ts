import { GateX402Client } from "../lib/api-client";
import { Signer } from "../lib/signer";
import { wrapAgentResponse } from "../types";

export interface WithdrawParams {
  network: string;
}

export interface WithdrawCredentials {
  getManagementToken: () => Promise<string>;
  getWalletPrivateKey: () => Promise<string>;
}

/** Sanitized withdraw result: only status and tx identifier. */
interface SanitizedWithdraw {
  status?: string;
  tx_hash?: string;
  message?: string;
}

/**
 * Execute withdrawal. Credentials are injected by the host; only sanitized result returned to agent.
 */
export async function withdrawFunds(
  params: WithdrawParams,
  credentials: WithdrawCredentials
): Promise<string> {
  const [managementToken, walletPrivateKey] = await Promise.all([
    credentials.getManagementToken(),
    credentials.getWalletPrivateKey(),
  ]);
  if (!managementToken) {
    return wrapAgentResponse({
      message: "No management token configured. Provision an API first.",
    });
  }
  const client = new GateX402Client(managementToken);
  const signer = new Signer(walletPrivateKey);

  const { nonce, message } = await client.post("/agent/nonce", {
    wallet_address: signer.getAddress(),
    action: "withdraw",
    network: params.network,
  });

  const signature = await signer.signMessage(message);

  const result = await client.post("/agent/payout/withdraw", {
    wallet_address: signer.getAddress(),
    signature,
    message,
    network: params.network,
  });

  const sanitized: SanitizedWithdraw = {};
  if (typeof result.status === "string") sanitized.status = result.status;
  if (typeof result.tx_hash === "string") sanitized.tx_hash = result.tx_hash;
  if (typeof result.message === "string") sanitized.message = result.message;

  return wrapAgentResponse(sanitized);
}
