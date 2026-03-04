/**
 * PayRail402 OpenClaw Skill
 *
 * Installable skill for AI agent frameworks (OpenClaw/ClawHub).
 * Provides tools for transaction tracking, budget checking, and agent registration.
 *
 * Zero dependencies. All network requests go to the PayRail402 API over HTTPS only.
 * No filesystem access, no shell commands, no third-party calls.
 *
 * Install via ClawHub:
 *   claw install payrail402
 *
 * Or import directly:
 *   import { payrail402Skill } from "@payrail402/sdk/openclaw-skill";
 */

// All API requests go to this single HTTPS endpoint
const DEFAULT_BASE_URL = "https://payrail402-production-2a69.up.railway.app";

export const payrail402Skill = {
  name: "payrail402",
  version: "1.0.0",
  description: "Track AI agent spending across payment rails — Visa IC, Mastercard Agent Pay, Stripe ACP, x402, and more.",
  author: "PayRail402",
  homepage: "https://payrail402.com",

  // Environment variables this skill reads.
  // webhookToken: per-agent secret, used in URL path for transaction ingest.
  // apiKey: pr4_xxx format, sent in x-agent-key header for status checks.
  // agentId: public CUID, identifies the agent when using API key auth.
  config: {
    apiKey: {
      type: "string",
      description: "PayRail402 agent API key (starts with pr4_)",
      required: false,
    },
    webhookToken: {
      type: "string",
      description: "PayRail402 webhook token for this agent",
      required: false,
    },
    agentId: {
      type: "string",
      description: "Agent ID (required when using apiKey auth)",
      required: false,
    },
    baseUrl: {
      type: "string",
      description: "API base URL",
      default: DEFAULT_BASE_URL,
    },
  },

  tools: [
    {
      name: "payrail402_track",
      description: "Track a financial transaction made by this agent. Call this after any purchase, payment, or financial operation.",
      inputSchema: {
        type: "object",
        properties: {
          amount: { type: "number", description: "Transaction amount (positive number)" },
          description: { type: "string", description: "What the agent did (max 500 chars)" },
          merchant: { type: "string", description: "Merchant or service name" },
          category: { type: "string", description: "Category: shopping, finance, devops, research, travel, api, other" },
          rail: { type: "string", description: "Payment rail: visa_ic, mc_agent, stripe_acp, x402, ach, manual" },
          mandate: { type: "string", description: "Authorization or mandate reference" },
          proofHash: { type: "string", description: "On-chain transaction hash" },
        },
        required: ["amount", "description"],
      },
    },
    {
      name: "payrail402_register",
      description: "Self-register this agent with PayRail402 to get tracking credentials.",
      inputSchema: {
        type: "object",
        properties: {
          name: { type: "string", description: "Agent name" },
          description: { type: "string", description: "What this agent does" },
          type: { type: "string", description: "Agent type: shopping, finance, devops, research, travel, api, general" },
          contactEmail: { type: "string", description: "Developer/owner email for notifications" },
          callbackUrl: { type: "string", description: "Webhook URL for alerts and events" },
        },
        required: ["name", "contactEmail"],
      },
    },
    {
      name: "payrail402_status",
      description: "Check this agent's status, claim state, and configuration on PayRail402.",
      inputSchema: {
        type: "object",
        properties: {
          agentAccountId: { type: "string", description: "Agent account ID from registration" },
        },
        required: ["agentAccountId"],
      },
    },
  ],

  async execute(toolName, input, config) {
    const baseUrl = (config.baseUrl || DEFAULT_BASE_URL).replace(/\/$/, "");

    switch (toolName) {
      case "payrail402_track":
        return handleTrack(input, config, baseUrl);
      case "payrail402_register":
        return handleRegister(input, baseUrl);
      case "payrail402_status":
        return handleStatus(input, config, baseUrl);
      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }
  },
};

// --- Tool handlers ---

async function handleTrack(input, config, baseUrl) {
  if (!input.amount || input.amount <= 0) {
    return { error: "amount must be a positive number" };
  }

  const payload = {
    amount: input.amount,
    description: input.description,
    merchant: input.merchant,
    category: input.category,
    rail: input.rail || "manual",
    mandate: input.mandate,
    proofHash: input.proofHash,
  };

  // Auth path 1: webhook token embedded in URL path (per-agent, simplest)
  if (config.webhookToken) {
    return fetchJSON(`${baseUrl}/api/ingest/webhook/${config.webhookToken}`, {
      method: "POST",
      body: payload,
    });
  }

  // Auth path 2: API key in header (multi-agent, also needed for status checks)
  if (config.apiKey) {
    return fetchJSON(`${baseUrl}/api/transactions`, {
      method: "POST",
      body: { ...payload, agentId: config.agentId },
      headers: { "x-api-key": config.apiKey },
    });
  }

  return { error: "No credentials configured. Set webhookToken or apiKey in skill config." };
}

// Registration is public — no credentials needed
async function handleRegister(input, baseUrl) {
  return fetchJSON(`${baseUrl}/api/v1/agents/register`, {
    method: "POST",
    body: {
      name: input.name,
      description: input.description,
      type: input.type || "general",
      contactEmail: input.contactEmail,
      callbackUrl: input.callbackUrl,
    },
  });
}

// Status check requires API key auth (sent via x-agent-key header)
async function handleStatus(input, config, baseUrl) {
  if (!config.apiKey) {
    return { error: "apiKey is required in skill config to check status" };
  }

  return fetchJSON(`${baseUrl}/api/v1/agents/${input.agentAccountId}`, {
    method: "GET",
    headers: { "x-agent-key": config.apiKey },
  });
}

// --- HTTP helper ---
// All requests use HTTPS with JSON content type.
// Credentials go in headers or URL path — never query strings.
async function fetchJSON(url, { method = "GET", body, headers = {} }) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json", ...headers },
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    return { error: data.error || `HTTP ${res.status}`, status: res.status };
  }
  return data;
}

export default payrail402Skill;
