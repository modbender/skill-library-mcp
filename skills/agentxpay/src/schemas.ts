import type { ToolDefinition, SkillMetadata } from "./types";

// ─── Tool Schemas (JSON Schema for Function Calling / MCP) ──

export const TOOL_DISCOVER_SERVICES: ToolDefinition = {
  name: "agentxpay_discover_services",
  description:
    "Discover available AI services registered on the Monad blockchain. Supports filtering by category (LLM, Image, Code, etc.) and maximum price per call.",
  parameters: {
    type: "object",
    properties: {
      category: {
        type: "string",
        description:
          'Service category filter, e.g., "LLM", "Image", "Code"',
      },
      maxPrice: {
        type: "string",
        description:
          'Maximum price per call in MON, e.g., "0.05"',
      },
    },
    required: [],
  },
};

export const TOOL_PAY_AND_CALL: ToolDefinition = {
  name: "agentxpay_pay_and_call",
  description:
    "Call an AI service endpoint with automatic x402 payment handling. If the server returns HTTP 402 (Payment Required), the agent automatically pays on-chain and retries the request.",
  parameters: {
    type: "object",
    properties: {
      url: {
        type: "string",
        description: "AI service endpoint URL",
      },
      method: {
        type: "string",
        enum: ["GET", "POST", "PUT", "DELETE"],
        description: "HTTP method (default: POST)",
      },
      body: {
        type: "object",
        description: "Request body (will be JSON-serialized)",
      },
      headers: {
        type: "object",
        description: "Additional HTTP headers",
        additionalProperties: { type: "string" },
      },
    },
    required: ["url"],
  },
};

export const TOOL_MANAGE_WALLET: ToolDefinition = {
  name: "agentxpay_manage_wallet",
  description:
    "Create and manage an Agent smart contract wallet on Monad. Supports creating wallets with daily spending limits, funding, querying info, updating limits, authorizing/revoking agent addresses, and paying for services using the wallet balance.",
  parameters: {
    type: "object",
    properties: {
      action: {
        type: "string",
        enum: ["create", "fund", "get_info", "set_limit", "authorize_agent", "revoke_agent", "pay"],
        description:
          "Wallet management action. 'authorize_agent' grants an address permission to spend from this wallet. 'revoke_agent' removes that permission. 'pay' executes a payment to a service using the wallet balance via PaymentManager.",
      },
      dailyLimit: {
        type: "string",
        description:
          'Daily spending limit in MON (for create/set_limit), e.g., "0.5"',
      },
      amount: {
        type: "string",
        description: 'Amount in MON (for fund/pay), e.g., "1.0"',
      },
      walletAddress: {
        type: "string",
        description:
          "Wallet contract address (required for fund/get_info/set_limit/authorize_agent/revoke_agent/pay)",
      },
      agentAddress: {
        type: "string",
        description:
          "Agent address to authorize or revoke (required for authorize_agent/revoke_agent)",
      },
      serviceId: {
        type: "number",
        description: "On-chain service ID (required for pay action)",
      },
    },
    required: ["action"],
  },
};

export const TOOL_SUBSCRIBE_SERVICE: ToolDefinition = {
  name: "agentxpay_subscribe",
  description:
    "Subscribe to an AI service's recurring plan on-chain. Automatically selects the first available plan if planId is not specified.",
  parameters: {
    type: "object",
    properties: {
      serviceId: {
        type: "number",
        description: "On-chain service ID",
      },
      planId: {
        type: "number",
        description:
          "Subscription plan ID (auto-selects first plan if omitted)",
      },
    },
    required: ["serviceId"],
  },
};

export const TOOL_CREATE_ESCROW: ToolDefinition = {
  name: "agentxpay_create_escrow",
  description:
    "Create an on-chain escrow for a custom AI job. Funds are locked in the smart contract until the job is completed or the deadline passes.",
  parameters: {
    type: "object",
    properties: {
      serviceId: {
        type: "number",
        description: "On-chain service ID",
      },
      amount: {
        type: "string",
        description: 'Escrow amount in MON, e.g., "0.1"',
      },
      deadlineDays: {
        type: "number",
        description: "Deadline in days from now",
      },
      description: {
        type: "string",
        description: "Job description",
      },
    },
    required: ["serviceId", "amount", "deadlineDays", "description"],
  },
};

export const TOOL_SMART_CALL: ToolDefinition = {
  name: "agentxpay_smart_call",
  description:
    "Intelligently discover the best matching AI service on-chain, then automatically pay and call it in one step. Combines service discovery + selection + x402 payment into a single operation.",
  parameters: {
    type: "object",
    properties: {
      task: {
        type: "string",
        description:
          'Task description, e.g., "Generate a cyberpunk cat image"',
      },
      category: {
        type: "string",
        description: 'Preferred service category, e.g., "Image", "LLM"',
      },
      maxBudget: {
        type: "string",
        description:
          'Maximum budget in MON, e.g., "0.05"',
      },
      preferCheapest: {
        type: "boolean",
        description: "If true, selects the cheapest matching service",
      },
    },
    required: ["task"],
  },
};

export const TOOL_GET_AGENT_INFO: ToolDefinition = {
  name: "agentxpay_get_agent_info",
  description:
    "Get the current agent's wallet address, MON balance, and connected network information.",
  parameters: {
    type: "object",
    properties: {},
    required: [],
  },
};

// ─── All Tools ─────────────────────────────────────────────

export const ALL_TOOLS: ToolDefinition[] = [
  TOOL_DISCOVER_SERVICES,
  TOOL_PAY_AND_CALL,
  TOOL_MANAGE_WALLET,
  TOOL_SUBSCRIBE_SERVICE,
  TOOL_CREATE_ESCROW,
  TOOL_SMART_CALL,
  TOOL_GET_AGENT_INFO,
];

// ─── Skill Metadata ────────────────────────────────────────

export const SKILL_METADATA: SkillMetadata = {
  name: "agentxpay",
  version: "0.1.0",
  description:
    "AgentXPay Skill — enables AI Agents to autonomously discover, pay for, and consume AI services on the Monad blockchain via the x402 protocol.",
  author: "jasonruan",
  chain: "monad",
  protocol: "x402",
  capabilities: [
    "service_discovery",
    "auto_payment",
    "wallet_management",
    "subscription",
    "escrow",
    "smart_call",
  ],
  tools: ALL_TOOLS,
};
