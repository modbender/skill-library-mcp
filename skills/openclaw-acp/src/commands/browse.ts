// =============================================================================
// acp browse <query> — Search and discover agents
// =============================================================================

import client from "../lib/client.js";
import * as output from "../lib/output.js";

interface JobOffering {
  name: string;
  description?: string;
  price: number;
  priceType: string;
  requiredFunds?: boolean;
  requirement: Record<string, unknown> | string;
  [key: string]: unknown;
}

interface Resource {
  name: string;
  description?: string;
  url?: string;
  params?: Record<string, unknown>;
  [key: string]: unknown;
}

interface Agent {
  id: string;
  name: string;
  walletAddress: string;
  description: string;
  jobOfferings?: JobOffering[];
  resources?: Resource[];
  [key: string]: unknown;
}

function formatPrice(price: number, priceType?: string): string {
  if (priceType === "fixed") return `${price} USDC`;
  if (priceType === "percentage") return `${(price * 100).toFixed(1)}%`;
  return String(price);
}

export async function browse(query: string): Promise<void> {
  if (!query.trim()) {
    output.fatal("Usage: acp browse <query>");
  }

  try {
    const agents = await client.get<{ data: Agent[] }>(
      `/acp/agents?query=${encodeURIComponent(query)}`
    );

    if (!agents.data.data || agents.data.data.length === 0) {
      output.fatal("No agents found.");
    }

    const data = agents.data.data;

    output.output(data, (agents) => {
      output.heading(`Agents matching "${query}"`);
      for (const agent of agents) {
        output.log(`\n  ${agent.name}`);
        output.field("  Wallet", agent.walletAddress);
        if (agent.description) {
          output.field("  Description", agent.description);
        }

        const offerings = agent.jobOfferings || [];
        if (offerings.length > 0) {
          output.log("    Offerings:");
          for (const o of offerings) {
            const fee = formatPrice(o.price, o.priceType);
            const funds = o.requiredFunds ? " [requires funds]" : "";
            output.log(`      - ${o.name} (${fee}${funds})`);
            if (o.description) {
              output.log(`        ${o.description}`);
            }
            if (o.requirement) {
              const req =
                typeof o.requirement === "string"
                  ? o.requirement
                  : JSON.stringify(o.requirement, null, 2)
                      .split("\n")
                      .join("\n          ");
              output.log(`        Requirement: ${req}`);
            }
          }
        }

        const resources = agent.resources || [];
        if (resources.length > 0) {
          output.log("    Resources:");
          for (const r of resources) {
            output.log(`      - ${r.name}`);
            if (r.description) {
              output.log(`        ${r.description}`);
            }
            if (r.url) {
              output.log(`        URL: ${r.url}`);
            }
            if (r.params) {
              const params = JSON.stringify(r.params, null, 2)
                .split("\n")
                .join("\n          ");
              output.log(`        Params: ${params}`);
            }
          }
        }
      }
      output.log("");
    });
  } catch (e) {
    output.fatal(
      `Browse failed: ${e instanceof Error ? e.message : String(e)}`
    );
  }
}
