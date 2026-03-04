/**
 * MCP Resources - 7 resources
 * Read-only data resources for AI agents
 */

import type { Resource } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "./client.js";

// Resource definitions
export const resources: Resource[] = [
  {
    uri: "dealworks://profile",
    name: "User Profile",
    description: "Current user's profile including trust tier, verification status, and preferences",
    mimeType: "application/json",
  },
  {
    uri: "dealworks://wallet",
    name: "Wallet Summary",
    description: "Wallet balances across all currencies including locked/available breakdown",
    mimeType: "application/json",
  },
  {
    uri: "dealworks://deals",
    name: "Active Deals",
    description: "List of active deals with summary status",
    mimeType: "application/json",
  },
  {
    uri: "dealworks://agents",
    name: "Deployed Agents",
    description: "List of deployed agents with health status",
    mimeType: "application/json",
  },
  {
    uri: "dealworks://templates",
    name: "Deal Templates",
    description: "Available deal templates from Bourse",
    mimeType: "application/json",
  },
  {
    uri: "dealworks://disputes",
    name: "Open Disputes",
    description: "Active disputes requiring attention",
    mimeType: "application/json",
  },
  {
    uri: "dealworks://dashboard",
    name: "Dashboard Metrics",
    description: "Key metrics and KPIs from HQ dashboard",
    mimeType: "application/json",
  },
];

// Resource handlers
export async function readResource(uri: string): Promise<string> {
  const client = getEngineClient();

  switch (uri) {
    case "dealworks://profile": {
      const result = await client.fetch("hq", "/users/me/profile");
      return JSON.stringify(result.data ?? result, null, 2);
    }

    case "dealworks://wallet": {
      const result = await client.fetch("fund", "/wallets/me/summary");
      return JSON.stringify(result.data ?? result, null, 2);
    }

    case "dealworks://deals": {
      const result = await client.fetch("deal", "/deals?status=ACTIVE&limit=50");
      return JSON.stringify(result.data ?? result, null, 2);
    }

    case "dealworks://agents": {
      const result = await client.fetch("cadre", "/agents?status=RUNNING&limit=50");
      return JSON.stringify(result.data ?? result, null, 2);
    }

    case "dealworks://templates": {
      const result = await client.fetch("bourse", "/listings?category=TEMPLATE&limit=50");
      return JSON.stringify(result.data ?? result, null, 2);
    }

    case "dealworks://disputes": {
      const result = await client.fetch("parler", "/disputes?status=OPEN&limit=20");
      return JSON.stringify(result.data ?? result, null, 2);
    }

    case "dealworks://dashboard": {
      const result = await client.fetch("hq", "/dashboard?period=WEEK");
      return JSON.stringify(result.data ?? result, null, 2);
    }

    default:
      throw new Error(`Unknown resource: ${uri}`);
  }
}
