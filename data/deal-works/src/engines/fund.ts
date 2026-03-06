/**
 * Fund Engine - 6 tools
 * Manages wallets, transfers, escrow, and agent funding
 */

import { z } from "zod";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "../client.js";

// Input schemas
const FundBalanceInputSchema = z.object({
  walletId: z.string().optional(),
});

const FundTransferInputSchema = z.object({
  toWalletId: z.string().min(1),
  amount: z.number().positive(),
  currency: z.string().default("TALER"),
  memo: z.string().max(500).optional(),
  idempotencyKey: z.string().optional(),
});

const FundTransactionsInputSchema = z.object({
  walletId: z.string().optional(),
  type: z.enum(["CREDIT", "DEBIT", "ESCROW_LOCK", "ESCROW_RELEASE"]).optional(),
  limit: z.number().min(1).max(100).default(50),
  offset: z.number().min(0).default(0),
});

const FundEscrowInputSchema = z.object({
  dealId: z.string().min(1),
  amount: z.number().positive(),
  currency: z.string().default("TALER"),
  releaseConditions: z.array(z.string()).optional(),
});

const FundCashoutInputSchema = z.object({
  amount: z.number().positive(),
  destinationAddress: z.string().min(1),
  network: z.enum(["BASE", "BASE_SEPOLIA"]).default("BASE_SEPOLIA"),
});

const FundAgentFundInputSchema = z.object({
  agentId: z.string().min(1),
  amount: z.number().positive(),
  purpose: z.string().max(200).optional(),
});

// Tool definitions
export const fundTools: Tool[] = [
  {
    name: "fund_balance",
    description: "Get wallet balance including available, locked (in escrow), and pending amounts.",
    inputSchema: {
      type: "object",
      properties: {
        walletId: {
          type: "string",
          description: "Wallet ID (optional, defaults to user's primary wallet)",
        },
      },
    },
  },
  {
    name: "fund_transfer",
    description: "Transfer funds between wallets. Supports Taler tokens on Base.",
    inputSchema: {
      type: "object",
      properties: {
        toWalletId: {
          type: "string",
          description: "Destination wallet ID",
        },
        amount: {
          type: "number",
          description: "Amount to transfer",
        },
        currency: {
          type: "string",
          description: "Currency (default: TALER)",
        },
        memo: {
          type: "string",
          description: "Transfer memo/note",
        },
        idempotencyKey: {
          type: "string",
          description: "Idempotency key to prevent duplicate transfers",
        },
      },
      required: ["toWalletId", "amount"],
    },
  },
  {
    name: "fund_transactions",
    description: "List transaction history with optional type filter.",
    inputSchema: {
      type: "object",
      properties: {
        walletId: {
          type: "string",
          description: "Wallet ID (optional)",
        },
        type: {
          type: "string",
          enum: ["CREDIT", "DEBIT", "ESCROW_LOCK", "ESCROW_RELEASE"],
          description: "Filter by transaction type",
        },
        limit: {
          type: "number",
          description: "Max transactions to return",
          default: 50,
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
    name: "fund_escrow",
    description: "Lock funds in escrow for a deal. Funds are released when deal conditions are met.",
    inputSchema: {
      type: "object",
      properties: {
        dealId: {
          type: "string",
          description: "Deal ID to escrow funds for",
        },
        amount: {
          type: "number",
          description: "Amount to lock",
        },
        currency: {
          type: "string",
          description: "Currency (default: TALER)",
        },
        releaseConditions: {
          type: "array",
          items: { type: "string" },
          description: "Conditions that must be met to release funds",
        },
      },
      required: ["dealId", "amount"],
    },
  },
  {
    name: "fund_cashout",
    description: "Cash out Taler tokens to external wallet address on Base network.",
    inputSchema: {
      type: "object",
      properties: {
        amount: {
          type: "number",
          description: "Amount to cash out",
        },
        destinationAddress: {
          type: "string",
          description: "Destination wallet address (0x...)",
        },
        network: {
          type: "string",
          enum: ["BASE", "BASE_SEPOLIA"],
          description: "Network (default: BASE_SEPOLIA for testnet)",
        },
      },
      required: ["amount", "destinationAddress"],
    },
  },
  {
    name: "fund_agent_fund",
    description: "Fund an agent's operational wallet for autonomous transactions.",
    inputSchema: {
      type: "object",
      properties: {
        agentId: {
          type: "string",
          description: "Agent ID to fund",
        },
        amount: {
          type: "number",
          description: "Amount to allocate",
        },
        purpose: {
          type: "string",
          description: "Purpose/reason for funding",
        },
      },
      required: ["agentId", "amount"],
    },
  },
];

// Tool handlers
export async function handleFundTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = getEngineClient();

  switch (name) {
    case "fund_balance": {
      const input = FundBalanceInputSchema.parse(args);
      const path = input.walletId
        ? `/wallets/${input.walletId}/balance`
        : "/wallets/me/balance";
      return client.fetch("fund", path);
    }

    case "fund_transfer": {
      const input = FundTransferInputSchema.parse(args);
      return client.fetch("fund", "/transfers", {
        method: "POST",
        body: input,
        idempotencyKey: input.idempotencyKey ?? `transfer-${Date.now()}`,
      });
    }

    case "fund_transactions": {
      const input = FundTransactionsInputSchema.parse(args);
      const params = new URLSearchParams();
      if (input.walletId) params.set("walletId", input.walletId);
      if (input.type) params.set("type", input.type);
      params.set("limit", String(input.limit));
      params.set("offset", String(input.offset));
      return client.fetch("fund", `/transactions?${params.toString()}`);
    }

    case "fund_escrow": {
      const input = FundEscrowInputSchema.parse(args);
      return client.fetch("fund", "/escrow", {
        method: "POST",
        body: input,
        idempotencyKey: `escrow-${input.dealId}-${Date.now()}`,
      });
    }

    case "fund_cashout": {
      const input = FundCashoutInputSchema.parse(args);
      return client.fetch("fund", "/cashout", {
        method: "POST",
        body: input,
        idempotencyKey: `cashout-${Date.now()}`,
      });
    }

    case "fund_agent_fund": {
      const input = FundAgentFundInputSchema.parse(args);
      return client.fetch("fund", `/agents/${input.agentId}/fund`, {
        method: "POST",
        body: { amount: input.amount, purpose: input.purpose },
        idempotencyKey: `agent-fund-${input.agentId}-${Date.now()}`,
      });
    }

    default:
      throw new Error(`Unknown fund tool: ${name}`);
  }
}
