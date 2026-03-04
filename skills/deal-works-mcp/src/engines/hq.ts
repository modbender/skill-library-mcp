/**
 * HQ Engine - 2 tools
 * Platform administration and system health
 */

import { z } from "zod";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "../client.js";

// Input schemas
const HqDashboardInputSchema = z.object({
  period: z.enum(["DAY", "WEEK", "MONTH", "QUARTER"]).default("WEEK"),
});

const HqHealthInputSchema = z.object({
  detailed: z.boolean().default(false),
});

// Tool definitions
export const hqTools: Tool[] = [
  {
    name: "hq_dashboard",
    description: "Get dashboard metrics including deal volume, transaction totals, and agent activity.",
    inputSchema: {
      type: "object",
      properties: {
        period: {
          type: "string",
          enum: ["DAY", "WEEK", "MONTH", "QUARTER"],
          description: "Time period for metrics",
          default: "WEEK",
        },
      },
    },
  },
  {
    name: "hq_health",
    description: "Check system health status across all engines.",
    inputSchema: {
      type: "object",
      properties: {
        detailed: {
          type: "boolean",
          description: "Include detailed per-service metrics",
          default: false,
        },
      },
    },
  },
];

// Tool handlers
export async function handleHqTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = getEngineClient();

  switch (name) {
    case "hq_dashboard": {
      const input = HqDashboardInputSchema.parse(args);
      return client.fetch("hq", `/dashboard?period=${input.period}`);
    }

    case "hq_health": {
      const input = HqHealthInputSchema.parse(args);
      const params = input.detailed ? "?detailed=true" : "";
      return client.fetch("hq", `/health${params}`);
    }

    default:
      throw new Error(`Unknown hq tool: ${name}`);
  }
}
