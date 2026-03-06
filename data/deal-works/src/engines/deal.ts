/**
 * Deal Engine - 7 tools
 * Manages deal lifecycle: creation, actions, search, timeline
 */

import { z } from "zod";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "../client.js";

// Input schemas
const DealListInputSchema = z.object({
  status: z.enum(["DRAFT", "ACTIVE", "COMPLETED", "CANCELLED"]).optional(),
  limit: z.number().min(1).max(100).default(20),
  offset: z.number().min(0).default(0),
});

const DealCreateInputSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(5000).optional(),
  counterpartyEmail: z.string().email().optional(),
  templateId: z.string().optional(),
  amount: z.number().positive().optional(),
  currency: z.string().default("USD"),
  dueDate: z.string().datetime().optional(),
});

const DealGetInputSchema = z.object({
  dealId: z.string().min(1),
});

const DealActionInputSchema = z.object({
  dealId: z.string().min(1),
  action: z.enum(["SIGN", "APPROVE", "REJECT", "CANCEL", "COMPLETE", "ARCHIVE"]),
  comment: z.string().max(1000).optional(),
});

const DealSearchInputSchema = z.object({
  query: z.string().min(1).max(200),
  status: z.enum(["DRAFT", "ACTIVE", "COMPLETED", "CANCELLED"]).optional(),
  fromDate: z.string().datetime().optional(),
  toDate: z.string().datetime().optional(),
  limit: z.number().min(1).max(100).default(20),
});

const DealTimelineInputSchema = z.object({
  dealId: z.string().min(1),
  limit: z.number().min(1).max(100).default(50),
});

const DealAttachmentsInputSchema = z.object({
  dealId: z.string().min(1),
});

// Tool definitions
export const dealTools: Tool[] = [
  {
    name: "deal_list",
    description: "List deals with optional status filter. Returns paginated list of deals for the authenticated user.",
    inputSchema: {
      type: "object",
      properties: {
        status: {
          type: "string",
          enum: ["DRAFT", "ACTIVE", "COMPLETED", "CANCELLED"],
          description: "Filter by deal status",
        },
        limit: {
          type: "number",
          description: "Number of deals to return (max 100)",
          default: 20,
        },
        offset: {
          type: "number",
          description: "Pagination offset",
          default: 0,
        },
      },
    },
  },
  {
    name: "deal_create",
    description: "Create a new deal. Can optionally use a template and specify counterparty.",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Deal title (required)",
        },
        description: {
          type: "string",
          description: "Deal description",
        },
        counterpartyEmail: {
          type: "string",
          description: "Email of the counterparty to invite",
        },
        templateId: {
          type: "string",
          description: "Template ID to base the deal on",
        },
        amount: {
          type: "number",
          description: "Deal amount",
        },
        currency: {
          type: "string",
          description: "Currency code (default: USD)",
        },
        dueDate: {
          type: "string",
          description: "Due date in ISO 8601 format",
        },
      },
      required: ["title"],
    },
  },
  {
    name: "deal_get",
    description: "Get detailed information about a specific deal including parties, terms, and current status.",
    inputSchema: {
      type: "object",
      properties: {
        dealId: {
          type: "string",
          description: "Deal ID",
        },
      },
      required: ["dealId"],
    },
  },
  {
    name: "deal_action",
    description: "Perform an action on a deal: sign, approve, reject, cancel, complete, or archive.",
    inputSchema: {
      type: "object",
      properties: {
        dealId: {
          type: "string",
          description: "Deal ID",
        },
        action: {
          type: "string",
          enum: ["SIGN", "APPROVE", "REJECT", "CANCEL", "COMPLETE", "ARCHIVE"],
          description: "Action to perform",
        },
        comment: {
          type: "string",
          description: "Optional comment for the action",
        },
      },
      required: ["dealId", "action"],
    },
  },
  {
    name: "deal_search",
    description: "Search deals by text query across titles, descriptions, and party names.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query",
        },
        status: {
          type: "string",
          enum: ["DRAFT", "ACTIVE", "COMPLETED", "CANCELLED"],
          description: "Filter by status",
        },
        fromDate: {
          type: "string",
          description: "Start date filter (ISO 8601)",
        },
        toDate: {
          type: "string",
          description: "End date filter (ISO 8601)",
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
    name: "deal_timeline",
    description: "Get the activity timeline for a deal showing all events and state changes.",
    inputSchema: {
      type: "object",
      properties: {
        dealId: {
          type: "string",
          description: "Deal ID",
        },
        limit: {
          type: "number",
          description: "Max events to return",
          default: 50,
        },
      },
      required: ["dealId"],
    },
  },
  {
    name: "deal_attachments",
    description: "List all attachments (documents, files) associated with a deal.",
    inputSchema: {
      type: "object",
      properties: {
        dealId: {
          type: "string",
          description: "Deal ID",
        },
      },
      required: ["dealId"],
    },
  },
];

// Tool handlers
export async function handleDealTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = getEngineClient();

  switch (name) {
    case "deal_list": {
      const input = DealListInputSchema.parse(args);
      const params = new URLSearchParams();
      if (input.status) params.set("status", input.status);
      params.set("limit", String(input.limit));
      params.set("offset", String(input.offset));
      return client.fetch("deal", `/deals?${params.toString()}`);
    }

    case "deal_create": {
      const input = DealCreateInputSchema.parse(args);
      return client.fetch("deal", "/deals", {
        method: "POST",
        body: input,
        idempotencyKey: `create-${Date.now()}`,
      });
    }

    case "deal_get": {
      const input = DealGetInputSchema.parse(args);
      return client.fetch("deal", `/deals/${input.dealId}`);
    }

    case "deal_action": {
      const input = DealActionInputSchema.parse(args);
      return client.fetch("deal", `/deals/${input.dealId}/actions`, {
        method: "POST",
        body: { action: input.action, comment: input.comment },
        idempotencyKey: `action-${input.dealId}-${input.action}-${Date.now()}`,
      });
    }

    case "deal_search": {
      const input = DealSearchInputSchema.parse(args);
      return client.fetch("deal", "/deals/search", {
        method: "POST",
        body: input,
      });
    }

    case "deal_timeline": {
      const input = DealTimelineInputSchema.parse(args);
      const params = new URLSearchParams({ limit: String(input.limit) });
      return client.fetch("deal", `/deals/${input.dealId}/timeline?${params.toString()}`);
    }

    case "deal_attachments": {
      const input = DealAttachmentsInputSchema.parse(args);
      return client.fetch("deal", `/deals/${input.dealId}/attachments`);
    }

    default:
      throw new Error(`Unknown deal tool: ${name}`);
  }
}
