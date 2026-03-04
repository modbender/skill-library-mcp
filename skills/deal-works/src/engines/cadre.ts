/**
 * Cadre Engine - 6 tools
 * Agent deployment, management, and monitoring
 */

import { z } from "zod";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "../client.js";

// Input schemas
const CadreListInputSchema = z.object({
  status: z.enum(["RUNNING", "STOPPED", "FAILED", "PENDING"]).optional(),
  limit: z.number().min(1).max(100).default(20),
  offset: z.number().min(0).default(0),
});

const CadreDeployInputSchema = z.object({
  name: z.string().min(1).max(100),
  skillId: z.string().min(1),
  config: z.record(z.unknown()).optional(),
  fundingAmount: z.number().positive().optional(),
  slaConfig: z.object({
    maxLatencyMs: z.number().positive().optional(),
    minUptime: z.number().min(0).max(100).optional(),
  }).optional(),
});

const CadreCommandInputSchema = z.object({
  agentId: z.string().min(1),
  command: z.enum(["START", "STOP", "RESTART", "SCALE_UP", "SCALE_DOWN"]),
  params: z.record(z.unknown()).optional(),
});

const CadreHealthInputSchema = z.object({
  agentId: z.string().min(1),
});

const CadreDelegationsInputSchema = z.object({
  agentId: z.string().optional(),
  status: z.enum(["ACTIVE", "REVOKED", "EXPIRED"]).optional(),
});

const CadreSlaViolationsInputSchema = z.object({
  agentId: z.string().optional(),
  severity: z.enum(["LOW", "MEDIUM", "HIGH", "CRITICAL"]).optional(),
  fromDate: z.string().datetime().optional(),
  limit: z.number().min(1).max(100).default(50),
});

// Tool definitions
export const cadreTools: Tool[] = [
  {
    name: "cadre_list",
    description: "List deployed agents with optional status filter.",
    inputSchema: {
      type: "object",
      properties: {
        status: {
          type: "string",
          enum: ["RUNNING", "STOPPED", "FAILED", "PENDING"],
          description: "Filter by agent status",
        },
        limit: {
          type: "number",
          description: "Max agents to return",
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
    name: "cadre_deploy",
    description: "Deploy a new agent from a skill definition. Optionally fund and configure SLA.",
    inputSchema: {
      type: "object",
      properties: {
        name: {
          type: "string",
          description: "Agent name",
        },
        skillId: {
          type: "string",
          description: "Skill ID from Bourse to deploy",
        },
        config: {
          type: "object",
          description: "Agent configuration overrides",
        },
        fundingAmount: {
          type: "number",
          description: "Initial funding amount in Talers",
        },
        slaConfig: {
          type: "object",
          properties: {
            maxLatencyMs: { type: "number" },
            minUptime: { type: "number" },
          },
          description: "SLA configuration",
        },
      },
      required: ["name", "skillId"],
    },
  },
  {
    name: "cadre_command",
    description: "Send a command to an agent: start, stop, restart, or scale.",
    inputSchema: {
      type: "object",
      properties: {
        agentId: {
          type: "string",
          description: "Agent ID",
        },
        command: {
          type: "string",
          enum: ["START", "STOP", "RESTART", "SCALE_UP", "SCALE_DOWN"],
          description: "Command to execute",
        },
        params: {
          type: "object",
          description: "Command parameters (e.g., scale factor)",
        },
      },
      required: ["agentId", "command"],
    },
  },
  {
    name: "cadre_health",
    description: "Get health status and metrics for a specific agent.",
    inputSchema: {
      type: "object",
      properties: {
        agentId: {
          type: "string",
          description: "Agent ID",
        },
      },
      required: ["agentId"],
    },
  },
  {
    name: "cadre_delegations",
    description: "List permission delegations granted to agents.",
    inputSchema: {
      type: "object",
      properties: {
        agentId: {
          type: "string",
          description: "Filter by agent ID",
        },
        status: {
          type: "string",
          enum: ["ACTIVE", "REVOKED", "EXPIRED"],
          description: "Filter by delegation status",
        },
      },
    },
  },
  {
    name: "cadre_sla_violations",
    description: "List SLA violations for agents. Used for monitoring and alerting.",
    inputSchema: {
      type: "object",
      properties: {
        agentId: {
          type: "string",
          description: "Filter by agent ID",
        },
        severity: {
          type: "string",
          enum: ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
          description: "Filter by severity",
        },
        fromDate: {
          type: "string",
          description: "Start date filter (ISO 8601)",
        },
        limit: {
          type: "number",
          description: "Max violations to return",
          default: 50,
        },
      },
    },
  },
];

// Tool handlers
export async function handleCadreTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = getEngineClient();

  switch (name) {
    case "cadre_list": {
      const input = CadreListInputSchema.parse(args);
      const params = new URLSearchParams();
      if (input.status) params.set("status", input.status);
      params.set("limit", String(input.limit));
      params.set("offset", String(input.offset));
      return client.fetch("cadre", `/agents?${params.toString()}`);
    }

    case "cadre_deploy": {
      const input = CadreDeployInputSchema.parse(args);
      return client.fetch("cadre", "/agents", {
        method: "POST",
        body: input,
        idempotencyKey: `deploy-${input.skillId}-${Date.now()}`,
      });
    }

    case "cadre_command": {
      const input = CadreCommandInputSchema.parse(args);
      return client.fetch("cadre", `/agents/${input.agentId}/command`, {
        method: "POST",
        body: { command: input.command, params: input.params },
        idempotencyKey: `command-${input.agentId}-${input.command}-${Date.now()}`,
      });
    }

    case "cadre_health": {
      const input = CadreHealthInputSchema.parse(args);
      return client.fetch("cadre", `/agents/${input.agentId}/health`);
    }

    case "cadre_delegations": {
      const input = CadreDelegationsInputSchema.parse(args);
      const params = new URLSearchParams();
      if (input.agentId) params.set("agentId", input.agentId);
      if (input.status) params.set("status", input.status);
      return client.fetch("cadre", `/delegations?${params.toString()}`);
    }

    case "cadre_sla_violations": {
      const input = CadreSlaViolationsInputSchema.parse(args);
      const params = new URLSearchParams();
      if (input.agentId) params.set("agentId", input.agentId);
      if (input.severity) params.set("severity", input.severity);
      if (input.fromDate) params.set("fromDate", input.fromDate);
      params.set("limit", String(input.limit));
      return client.fetch("cadre", `/sla-violations?${params.toString()}`);
    }

    default:
      throw new Error(`Unknown cadre tool: ${name}`);
  }
}
