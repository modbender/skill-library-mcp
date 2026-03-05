import { API_URL, loadApiKey } from "../config.js";

function formatTimeRemaining(hours: number): string {
  if (hours > 24) {
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `~${days}d ${remainingHours}h`;
  }
  return `~${hours}h`;
}

export async function list(): Promise<void> {
  const apiKey = loadApiKey();
  if (!apiKey) {
    console.log("No API key found. Run `agentscale register` first.");
    process.exit(1);
  }

  const res = await fetch(`${API_URL}/list`, {
    headers: { "x-api-key": apiKey }
  });
  const data = await res.json();

  if (!res.ok) {
    console.error("Failed to list services:", data.error);
    process.exit(1);
  }

  if (data.services.length === 0) {
    console.log("No services yet. Run `agentscale deploy` to create one.");
    return;
  }

  console.log("Your services:");
  for (const svc of data.services) {
    let info = svc.status;
    if (svc.status === "running" && svc.expires_at) {
      const mins = Math.max(0, Math.round((new Date(svc.expires_at).getTime() - Date.now()) / 60000));
      info = `expires in ${mins}m`;
    }
    console.log(`  ${svc.name}  [${info}]  (created ${new Date(svc.created_at).toLocaleDateString()})`);
    if (svc.domains?.length) {
      for (const d of svc.domains) {
        console.log(`    https://${d}`);
      }
    }
  }

  if (data.cost_per_hour > 0 && data.credits != null) {
    const activeCount = data.services.filter((s: any) => s.status === "active").length;
    const creditsStr = `$${(data.credits / 100).toFixed(2)}`;
    const costStr = `$${(data.cost_per_hour / 100).toFixed(2)}/hr`;
    const serviceLabel = activeCount === 1 ? "1 service" : `${activeCount} services`;
    const timeStr = data.hours_remaining != null ? formatTimeRemaining(data.hours_remaining) : "N/A";
    console.log(`\nCredits: ${creditsStr} | ${costStr} (${serviceLabel}) | ${timeStr} remaining`);
  }
}
