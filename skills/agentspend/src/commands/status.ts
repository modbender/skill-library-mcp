import { AgentspendApiClient } from "../lib/api.js";
import { resolveApiKeyWithAutoClaim } from "../lib/auth-flow.js";
import { printStatus } from "../lib/output.js";

export async function runStatus(apiClient: AgentspendApiClient): Promise<void> {
  const apiKey = await resolveApiKeyWithAutoClaim(apiClient);
  const status = await apiClient.status(apiKey);
  printStatus(status);
}
