/**
 * Parler Engine - 4 tools
 * Dispute resolution and governance
 */

import { z } from "zod";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "../client.js";

// Input schemas
const ParlerDisputeFileInputSchema = z.object({
  dealId: z.string().min(1),
  reason: z.enum([
    "NON_DELIVERY",
    "QUALITY_ISSUE",
    "LATE_DELIVERY",
    "PAYMENT_DISPUTE",
    "BREACH_OF_TERMS",
    "OTHER",
  ]),
  description: z.string().min(10).max(5000),
  evidence: z.array(z.object({
    type: z.string(),
    url: z.string().url().optional(),
    hash: z.string().optional(),
    description: z.string(),
  })).optional(),
  requestedResolution: z.enum(["REFUND", "PARTIAL_REFUND", "COMPLETION", "ARBITRATION"]).optional(),
});

const ParlerDisputeListInputSchema = z.object({
  status: z.enum(["OPEN", "IN_REVIEW", "RESOLVED", "ESCALATED"]).optional(),
  role: z.enum(["CLAIMANT", "RESPONDENT", "ARBITRATOR"]).optional(),
  limit: z.number().min(1).max(100).default(20),
});

const ParlerProposalsInputSchema = z.object({
  disputeId: z.string().min(1),
});

const ParlerVoteInputSchema = z.object({
  proposalId: z.string().min(1),
  vote: z.enum(["APPROVE", "REJECT", "ABSTAIN"]),
  comment: z.string().max(1000).optional(),
});

// Tool definitions
export const parlerTools: Tool[] = [
  {
    name: "parler_dispute_file",
    description: "File a dispute against a deal. Initiates the resolution process.",
    inputSchema: {
      type: "object",
      properties: {
        dealId: {
          type: "string",
          description: "Deal ID to dispute",
        },
        reason: {
          type: "string",
          enum: [
            "NON_DELIVERY",
            "QUALITY_ISSUE",
            "LATE_DELIVERY",
            "PAYMENT_DISPUTE",
            "BREACH_OF_TERMS",
            "OTHER",
          ],
          description: "Dispute reason",
        },
        description: {
          type: "string",
          description: "Detailed description of the dispute",
        },
        evidence: {
          type: "array",
          items: {
            type: "object",
            properties: {
              type: { type: "string" },
              url: { type: "string" },
              hash: { type: "string" },
              description: { type: "string" },
            },
          },
          description: "Supporting evidence",
        },
        requestedResolution: {
          type: "string",
          enum: ["REFUND", "PARTIAL_REFUND", "COMPLETION", "ARBITRATION"],
          description: "Requested resolution outcome",
        },
      },
      required: ["dealId", "reason", "description"],
    },
  },
  {
    name: "parler_dispute_list",
    description: "List disputes you're involved in as claimant, respondent, or arbitrator.",
    inputSchema: {
      type: "object",
      properties: {
        status: {
          type: "string",
          enum: ["OPEN", "IN_REVIEW", "RESOLVED", "ESCALATED"],
          description: "Filter by status",
        },
        role: {
          type: "string",
          enum: ["CLAIMANT", "RESPONDENT", "ARBITRATOR"],
          description: "Filter by your role",
        },
        limit: {
          type: "number",
          description: "Max disputes to return",
          default: 20,
        },
      },
    },
  },
  {
    name: "parler_proposals",
    description: "List resolution proposals for a dispute.",
    inputSchema: {
      type: "object",
      properties: {
        disputeId: {
          type: "string",
          description: "Dispute ID",
        },
      },
      required: ["disputeId"],
    },
  },
  {
    name: "parler_vote",
    description: "Vote on a resolution proposal. Requires arbitrator role for binding votes.",
    inputSchema: {
      type: "object",
      properties: {
        proposalId: {
          type: "string",
          description: "Proposal ID to vote on",
        },
        vote: {
          type: "string",
          enum: ["APPROVE", "REJECT", "ABSTAIN"],
          description: "Your vote",
        },
        comment: {
          type: "string",
          description: "Optional comment explaining your vote",
        },
      },
      required: ["proposalId", "vote"],
    },
  },
];

// Tool handlers
export async function handleParlerTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = getEngineClient();

  switch (name) {
    case "parler_dispute_file": {
      const input = ParlerDisputeFileInputSchema.parse(args);
      return client.fetch("parler", "/disputes", {
        method: "POST",
        body: input,
        idempotencyKey: `dispute-${input.dealId}-${Date.now()}`,
      });
    }

    case "parler_dispute_list": {
      const input = ParlerDisputeListInputSchema.parse(args);
      const params = new URLSearchParams();
      if (input.status) params.set("status", input.status);
      if (input.role) params.set("role", input.role);
      params.set("limit", String(input.limit));
      return client.fetch("parler", `/disputes?${params.toString()}`);
    }

    case "parler_proposals": {
      const input = ParlerProposalsInputSchema.parse(args);
      return client.fetch("parler", `/disputes/${input.disputeId}/proposals`);
    }

    case "parler_vote": {
      const input = ParlerVoteInputSchema.parse(args);
      return client.fetch("parler", `/proposals/${input.proposalId}/vote`, {
        method: "POST",
        body: { vote: input.vote, comment: input.comment },
        idempotencyKey: `vote-${input.proposalId}-${Date.now()}`,
      });
    }

    default:
      throw new Error(`Unknown parler tool: ${name}`);
  }
}
