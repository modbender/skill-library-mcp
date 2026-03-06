import { API_URL, loadApiKey } from "../config.js";

function formatTimeRemaining(hours: number): string {
  if (hours > 24) {
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `~${days}d ${remainingHours}h`;
  }
  return `~${hours}h`;
}

export async function account(): Promise<void> {
  const apiKey = loadApiKey();
  if (!apiKey) {
    console.log("No API key found. Run `agentscale register` first.");
    process.exit(1);
  }

  const res = await fetch(`${API_URL}/account`, {
    headers: { "x-api-key": apiKey }
  });
  const data = await res.json();

  if (!res.ok) {
    console.error("Failed to get account info:", data.error);
    process.exit(1);
  }

  console.log(`Tier: ${data.tier}`);
  console.log(`Credits: $${(data.credits / 100).toFixed(2)}`);

  if (data.cost_per_hour > 0) {
    const serviceLabel = data.active_services === 1 ? "1 active service" : `${data.active_services} active services`;
    console.log(`Burn rate: $${(data.cost_per_hour / 100).toFixed(2)}/hr (${serviceLabel})`);
    if (data.hours_remaining != null) {
      console.log(`Time remaining: ${formatTimeRemaining(data.hours_remaining)}`);
    }
  }

  console.log(`\nTo add credits, pay ${API_URL}/add-credits`);
  console.log("Use agentspend skill (credit card or crypto) or any x402 wallet.");
}
