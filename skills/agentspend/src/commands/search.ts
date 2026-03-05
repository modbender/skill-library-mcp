import { AgentspendApiClient } from "../lib/api.js";
import { resolveApiKeyWithAutoClaim } from "../lib/auth-flow.js";

export async function runSearch(apiClient: AgentspendApiClient, query: string): Promise<void> {
  const apiKey = await resolveApiKeyWithAutoClaim(apiClient);
  const response = await apiClient.search(apiKey, query);

  if (response.services.length === 0) {
    console.log(`No services matched "${response.query}".`);
    return;
  }

  for (const service of response.services) {
    console.log(service.name);
    console.log(`Description: ${service.description}`);
    console.log(`Domain: ${service.domain}`);
    console.log(`Skill URL: ${service.skill_url ?? "n/a"}`);
    console.log("");
  }
}
