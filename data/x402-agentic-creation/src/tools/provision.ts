import { GateX402Client } from "../lib/api-client";
import { Signer } from "../lib/signer";
import { wrapAgentResponse } from "../types";

export interface ProvisionParams {
  api_name: string;
  /** CAIP-2 network ID, e.g. eip155:8453 (Base) or solana:5eykt4UsFv8P8NJdTREpY1vzqAQZSSfL */
  network: string;
  /** Origin URL of the API being monetized (e.g. https://api.example.com) */
  origin_url: string;
  routes: Array<{
    path_pattern: string;
    method: "GET" | "POST" | "PUT" | "DELETE";
    price_usdc: number;
  }>;
}

export interface ProvisionCredentials {
  getWalletPrivateKey: () => Promise<string>;
  storeManagementToken?: (token: string) => void | Promise<void>;
}

/**
 * Provision a new API. Credentials are injected by the host; the management token
 * is passed to storeManagementToken and never returned to the agent.
 */
export async function provisionApi(
  params: ProvisionParams,
  credentials: ProvisionCredentials
): Promise<string> {
  const walletPrivateKey = await credentials.getWalletPrivateKey();
  const client = new GateX402Client();
  const signer = new Signer(walletPrivateKey);
  const walletAddress = signer.getAddress();

  const { nonce, message } = await client.post("/agent/nonce", {
    wallet_address: walletAddress,
    action: "provision",
    network: params.network,
    origin_url: params.origin_url,
  });

  const walletSignature = await signer.signMessage(message);

  const body = {
    wallet_address: walletAddress,
    wallet_signature: walletSignature,
    message,
    network: params.network,
    api: {
      name: params.api_name,
      origin_base_url: params.origin_url,
    },
    routes: params.routes.map((r) => ({
      method: r.method,
      path_pattern: r.path_pattern,
      price_usdc: r.price_usdc,
      network: params.network,
    })),
  };

  const result = await client.post("/agent/provision", body);

  const data = result as {
    management_token?: string;
    provider_id?: string;
    provider?: { id: string };
    api?: { slug: string };
  };
  const management_token = data.management_token ?? "";
  const provider_id = data.provider_id ?? data.provider?.id ?? "";
  const api_slug = data.api?.slug ?? "";

  if (credentials.storeManagementToken) {
    await Promise.resolve(credentials.storeManagementToken(management_token));
  }

  // Agent response contains only api_slug, provider_id, and message; management_token is never returned.
  const agentSafe = {
    api_slug,
    provider_id,
    message:
      "Management token stored by runtime. Use this API slug for get_earnings and withdraw_funds.",
  };
  return wrapAgentResponse(agentSafe);
}
