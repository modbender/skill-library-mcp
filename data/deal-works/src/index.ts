/**
 * deal.works MCP Server
 *
 * Model Context Protocol server exposing 39 tools across 9 engines
 * for deal management, escrow, agents, attestations, and more.
 *
 * Usage:
 *   npx @goettelman/deal-works-mcp
 *
 * Environment Variables:
 *   DEAL_WORKS_API_KEY - API key for authentication (required)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Engine imports
import { dealTools, handleDealTool } from "./engines/deal.js";
import { fundTools, handleFundTool } from "./engines/fund.js";
import { bourseTools, handleBourseTool } from "./engines/bourse.js";
import { cadreTools, handleCadreTool } from "./engines/cadre.js";
import { oathTools, handleOathTool } from "./engines/oath.js";
import { parlerTools, handleParlerTool } from "./engines/parler.js";
import { academyTools, handleAcademyTool } from "./engines/academy.js";
import { hqTools, handleHqTool } from "./engines/hq.js";
import { clauseTools, handleClauseTool } from "./engines/clause.js";

// Resources and prompts
import { resources, readResource } from "./resources.js";
import { prompts, getPromptMessages } from "./prompts.js";

// Combine all tools
const allTools = [
  ...dealTools,
  ...fundTools,
  ...bourseTools,
  ...cadreTools,
  ...oathTools,
  ...parlerTools,
  ...academyTools,
  ...hqTools,
  ...clauseTools,
];

// Tool name to handler mapping
const toolHandlers: Record<string, (name: string, args: Record<string, unknown>) => Promise<unknown>> = {
  // Deal tools
  deal_list: handleDealTool,
  deal_create: handleDealTool,
  deal_get: handleDealTool,
  deal_action: handleDealTool,
  deal_search: handleDealTool,
  deal_timeline: handleDealTool,
  deal_attachments: handleDealTool,
  // Fund tools
  fund_balance: handleFundTool,
  fund_transfer: handleFundTool,
  fund_transactions: handleFundTool,
  fund_escrow: handleFundTool,
  fund_cashout: handleFundTool,
  fund_agent_fund: handleFundTool,
  // Bourse tools
  bourse_search: handleBourseTool,
  bourse_get: handleBourseTool,
  bourse_fork: handleBourseTool,
  bourse_publish: handleBourseTool,
  bourse_earnings: handleBourseTool,
  // Cadre tools
  cadre_list: handleCadreTool,
  cadre_deploy: handleCadreTool,
  cadre_command: handleCadreTool,
  cadre_health: handleCadreTool,
  cadre_delegations: handleCadreTool,
  cadre_sla_violations: handleCadreTool,
  // Oath tools
  oath_attest: handleOathTool,
  oath_verify: handleOathTool,
  oath_vault_upload: handleOathTool,
  oath_vault_seal: handleOathTool,
  oath_trust_tier: handleOathTool,
  // Parler tools
  parler_dispute_file: handleParlerTool,
  parler_dispute_list: handleParlerTool,
  parler_proposals: handleParlerTool,
  parler_vote: handleParlerTool,
  // Academy tools
  academy_courses: handleAcademyTool,
  academy_enroll: handleAcademyTool,
  academy_tip: handleAcademyTool,
  // HQ tools
  hq_dashboard: handleHqTool,
  hq_health: handleHqTool,
  // Clause tools
  clause_render: handleClauseTool,
};

/**
 * Create and configure the MCP server
 */
async function createServer(): Promise<Server> {
  const server = new Server(
    {
      name: "deal-works-mcp",
      version: "0.1.0",
    },
    {
      capabilities: {
        tools: {},
        resources: {},
        prompts: {},
      },
    }
  );

  // List all tools
  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: allTools,
  }));

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    const handler = toolHandlers[name];

    if (!handler) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: `Unknown tool: ${name}` }),
          },
        ],
        isError: true,
      };
    }

    try {
      const result = await handler(name, (args ?? {}) as Record<string, unknown>);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: errorMessage }),
          },
        ],
        isError: true,
      };
    }
  });

  // List resources
  server.setRequestHandler(ListResourcesRequestSchema, async () => ({
    resources,
  }));

  // Read resources
  server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
    const { uri } = request.params;
    try {
      const content = await readResource(uri);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: content,
          },
        ],
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      throw new Error(`Failed to read resource ${uri}: ${errorMessage}`);
    }
  });

  // List prompts
  server.setRequestHandler(ListPromptsRequestSchema, async () => ({
    prompts,
  }));

  // Get prompt
  server.setRequestHandler(GetPromptRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    const prompt = prompts.find((p) => p.name === name);

    if (!prompt) {
      throw new Error(`Unknown prompt: ${name}`);
    }

    const messages = getPromptMessages(name, (args ?? {}) as Record<string, string>);

    return {
      description: prompt.description,
      messages: messages.map((m) => ({
        role: m.role,
        content: {
          type: "text" as const,
          text: m.content,
        },
      })),
    };
  });

  return server;
}

/**
 * Main entry point
 */
async function main(): Promise<void> {
  // Check for API key
  if (!process.env.DEAL_WORKS_API_KEY) {
    console.error("Warning: DEAL_WORKS_API_KEY not set. API calls will fail.");
    console.error("Set it via: export DEAL_WORKS_API_KEY=your_key");
  }

  const server = await createServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);

  console.error("deal.works MCP Server running");
  console.error(`Tools: ${allTools.length}`);
  console.error(`Resources: ${resources.length}`);
  console.error(`Prompts: ${prompts.length}`);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
