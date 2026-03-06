/**
 * Bourse Engine - 5 tools
 * Marketplace for deal templates, skills, and integrations
 */

import { z } from "zod";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "../client.js";

// Input schemas
const BourseSearchInputSchema = z.object({
  query: z.string().min(1).max(200),
  category: z.enum(["TEMPLATE", "SKILL", "INTEGRATION", "CONNECTOR"]).optional(),
  minQuality: z.number().min(0).max(100).optional(),
  source: z.enum(["OFFICIAL", "COMMUNITY", "ACTIVEPIECES"]).optional(),
  limit: z.number().min(1).max(100).default(20),
});

const BourseGetInputSchema = z.object({
  listingId: z.string().min(1),
});

const BourseForkInputSchema = z.object({
  listingId: z.string().min(1),
  newName: z.string().min(1).max(100).optional(),
});

const BoursePublishInputSchema = z.object({
  type: z.enum(["TEMPLATE", "SKILL", "INTEGRATION"]),
  name: z.string().min(1).max(100),
  description: z.string().max(2000),
  content: z.record(z.unknown()),
  price: z.number().min(0).default(0),
  tags: z.array(z.string()).default([]),
});

const BourseEarningsInputSchema = z.object({
  period: z.enum(["DAY", "WEEK", "MONTH", "ALL"]).default("MONTH"),
});

// Tool definitions
export const bourseTools: Tool[] = [
  {
    name: "bourse_search",
    description: "Search the Bourse marketplace for templates, skills, and integrations.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query",
        },
        category: {
          type: "string",
          enum: ["TEMPLATE", "SKILL", "INTEGRATION", "CONNECTOR"],
          description: "Filter by category",
        },
        minQuality: {
          type: "number",
          description: "Minimum quality score (0-100)",
        },
        source: {
          type: "string",
          enum: ["OFFICIAL", "COMMUNITY", "ACTIVEPIECES"],
          description: "Filter by source",
        },
        limit: {
          type: "number",
          description: "Max results",
          default: 20,
        },
      },
      required: ["query"],
    },
  },
  {
    name: "bourse_get",
    description: "Get detailed information about a Bourse listing including reviews and usage stats.",
    inputSchema: {
      type: "object",
      properties: {
        listingId: {
          type: "string",
          description: "Listing ID",
        },
      },
      required: ["listingId"],
    },
  },
  {
    name: "bourse_fork",
    description: "Fork a Bourse listing to create your own customized version.",
    inputSchema: {
      type: "object",
      properties: {
        listingId: {
          type: "string",
          description: "Listing ID to fork",
        },
        newName: {
          type: "string",
          description: "Name for your forked version",
        },
      },
      required: ["listingId"],
    },
  },
  {
    name: "bourse_publish",
    description: "Publish a new template, skill, or integration to the Bourse marketplace.",
    inputSchema: {
      type: "object",
      properties: {
        type: {
          type: "string",
          enum: ["TEMPLATE", "SKILL", "INTEGRATION"],
          description: "Listing type",
        },
        name: {
          type: "string",
          description: "Listing name",
        },
        description: {
          type: "string",
          description: "Description",
        },
        content: {
          type: "object",
          description: "Listing content/definition",
        },
        price: {
          type: "number",
          description: "Price in Talers (0 for free)",
          default: 0,
        },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Tags for discoverability",
        },
      },
      required: ["type", "name", "description", "content"],
    },
  },
  {
    name: "bourse_earnings",
    description: "View your Bourse earnings from published listings.",
    inputSchema: {
      type: "object",
      properties: {
        period: {
          type: "string",
          enum: ["DAY", "WEEK", "MONTH", "ALL"],
          description: "Time period",
          default: "MONTH",
        },
      },
    },
  },
];

// Tool handlers
export async function handleBourseTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = getEngineClient();

  switch (name) {
    case "bourse_search": {
      const input = BourseSearchInputSchema.parse(args);
      return client.fetch("bourse", "/listings/search", {
        method: "POST",
        body: input,
      });
    }

    case "bourse_get": {
      const input = BourseGetInputSchema.parse(args);
      return client.fetch("bourse", `/listings/${input.listingId}`);
    }

    case "bourse_fork": {
      const input = BourseForkInputSchema.parse(args);
      return client.fetch("bourse", `/listings/${input.listingId}/fork`, {
        method: "POST",
        body: { newName: input.newName },
        idempotencyKey: `fork-${input.listingId}-${Date.now()}`,
      });
    }

    case "bourse_publish": {
      const input = BoursePublishInputSchema.parse(args);
      return client.fetch("bourse", "/listings", {
        method: "POST",
        body: input,
        idempotencyKey: `publish-${Date.now()}`,
      });
    }

    case "bourse_earnings": {
      const input = BourseEarningsInputSchema.parse(args);
      return client.fetch("bourse", `/earnings?period=${input.period}`);
    }

    default:
      throw new Error(`Unknown bourse tool: ${name}`);
  }
}
