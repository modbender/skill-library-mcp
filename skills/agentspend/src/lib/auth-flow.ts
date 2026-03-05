import bcrypt from "bcryptjs";
import crypto from "node:crypto";
import { ApiError, AgentspendApiClient } from "./api.js";
import {
  clearPendingConfigureToken,
  readCredentials,
  readPendingConfigureToken,
  saveCredentials,
} from "./credentials.js";
import type { ConfigureStatusResponse } from "../types.js";

function generateApiKey(): string {
  return `sk_agent_${crypto.randomBytes(32).toString("hex")}`;
}

async function getConfigureStatusOrNull(
  apiClient: AgentspendApiClient,
  token: string,
): Promise<ConfigureStatusResponse | null> {
  try {
    return await apiClient.configureStatus(token);
  } catch (error) {
    if (error instanceof ApiError && (error.status === 401 || error.status === 404 || error.status === 410)) {
      return null;
    }

    throw error;
  }
}

export async function claimConfigureToken(apiClient: AgentspendApiClient, token: string): Promise<string> {
  const apiKey = generateApiKey();
  const apiKeyHash = await bcrypt.hash(apiKey, 12);

  await apiClient.claimConfigure(token, apiKeyHash);
  await saveCredentials(apiKey);
  await clearPendingConfigureToken();

  return apiKey;
}

export async function getPendingConfigureStatus(
  apiClient: AgentspendApiClient,
): Promise<{ token: string; status: ConfigureStatusResponse } | null> {
  const token = await readPendingConfigureToken();

  if (!token) {
    return null;
  }

  const status = await getConfigureStatusOrNull(apiClient, token);

  if (!status || status.claim_status === "expired") {
    await clearPendingConfigureToken();
    return null;
  }

  return { token, status };
}

export async function resolveApiKeyWithAutoClaim(apiClient: AgentspendApiClient): Promise<string> {
  const credentials = await readCredentials();

  if (credentials) {
    return credentials.api_key;
  }

  const pending = await getPendingConfigureStatus(apiClient);

  if (!pending) {
    throw new Error("No API key found. Run `agentspend configure` first.");
  }

  if (pending.status.claim_status === "ready_to_claim") {
    return claimConfigureToken(apiClient, pending.token);
  }

  if (pending.status.claim_status === "awaiting_card") {
    throw new Error(`Card setup required. Open this URL:\n${pending.status.configure_url}`);
  }

  await clearPendingConfigureToken();
  throw new Error("Configure session already claimed. Run `agentspend configure` again.");
}
