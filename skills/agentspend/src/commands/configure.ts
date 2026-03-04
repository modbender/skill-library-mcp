import { ApiError, AgentspendApiClient } from "../lib/api.js";
import {
  clearPendingConfigureToken,
  readCredentials,
  savePendingConfigureToken,
} from "../lib/credentials.js";
import { claimConfigureToken, getPendingConfigureStatus } from "../lib/auth-flow.js";
import type { ConfigureStatusResponse } from "../types.js";

async function tryAuthenticatedConfigure(
  apiClient: AgentspendApiClient,
  apiKey: string,
): Promise<ConfigureStatusResponse | null> {
  try {
    return await apiClient.configure(undefined, apiKey);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }

    throw error;
  }
}

export async function runConfigure(apiClient: AgentspendApiClient): Promise<void> {
  const credentials = await readCredentials();

  if (credentials) {
    const authenticatedResponse = await tryAuthenticatedConfigure(apiClient, credentials.api_key);
    if (authenticatedResponse) {
      console.log(`Open this URL to configure settings:\n${authenticatedResponse.configure_url}`);
      return;
    }
  }

  const pending = await getPendingConfigureStatus(apiClient);

  if (pending) {
    if (pending.status.claim_status === "awaiting_card") {
      console.log(`Open this URL to configure settings:\n${pending.status.configure_url}`);
      return;
    }

    if (pending.status.claim_status === "ready_to_claim") {
      const apiKey = await claimConfigureToken(apiClient, pending.token);
      const claimedResponse = await tryAuthenticatedConfigure(apiClient, apiKey);

      if (claimedResponse) {
        console.log(`Open this URL to configure settings:\n${claimedResponse.configure_url}`);
        return;
      }

      throw new Error("API key was claimed, but configure session could not be created. Run agentspend configure again.");
    }

    await clearPendingConfigureToken();
  }

  const created = await apiClient.configure();
  await savePendingConfigureToken(created.token);
  console.log(`Open this URL to configure settings:\n${created.configure_url}`);
}
