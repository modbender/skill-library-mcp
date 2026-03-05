import {
  registerAppTool,
  registerAppResource,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createMcpExpressApp } from "@modelcontextprotocol/sdk/server/express.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import type { CallToolResult, ReadResourceResult } from "@modelcontextprotocol/sdk/types.js";
import cors from "cors";
import fs from "node:fs/promises";
import path from "node:path";
import { z } from "zod";

// Works both from source (server.ts) and compiled (dist/server.js)
const DIST_DIR = import.meta.filename.endsWith(".ts")
  ? path.join(import.meta.dirname, "dist")
  : import.meta.dirname;

const TOOL_NAME = "tool-name";
const toolUIResourceUri = `ui://${TOOL_NAME}/app.html`;

async function fetchData(param: string) {
  return {
    param,
    generatedAt: new Date().toISOString(),
    score: Math.max(1, param.length * 7),
    notes: `Sample data for ${param}`,
  };
}

// Server Factory - CRITICAL: New server per request
export function createServer(): McpServer {
  const server = new McpServer({
    name: "MCP App Template",
    version: "1.0.0",
  });

  registerAppTool(
    server,
    TOOL_NAME,
    {
      title: "Tool Name",
      description: "Describe when to use this tool.",
      inputSchema: {
        param: z.string().describe("Parameter description"),
      },
      _meta: { ui: { resourceUri: toolUIResourceUri } },
    },
    async ({ param }): Promise<CallToolResult> => {
      const result = await fetchData(param);
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        structuredContent: result,
      };
    }
  );

  registerAppResource(
    server,
    toolUIResourceUri,
    toolUIResourceUri,
    { mimeType: RESOURCE_MIME_TYPE },
    async (): Promise<ReadResourceResult> => {
      const html = await fs.readFile(
        path.join(DIST_DIR, TOOL_NAME, `${TOOL_NAME}.html`),
        "utf-8"
      );
      return {
        contents: [
          {
            uri: toolUIResourceUri,
            mimeType: RESOURCE_MIME_TYPE,
            text: html,
          },
        ],
      };
    }
  );

  return server;
}

// HTTP Server - MUST use createMcpExpressApp and app.all
const port = parseInt(process.env.PORT ?? "3001", 10);
const app = createMcpExpressApp({ host: "0.0.0.0" });
app.use(cors());

app.all("/mcp", async (req, res) => {
  const server = createServer();
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
  });

  res.on("close", () => {
    transport.close().catch(() => {});
    server.close().catch(() => {});
  });

  try {
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    console.error("MCP error:", error);
    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: "2.0",
        error: { code: -32603, message: "Internal server error" },
        id: null,
      });
    }
  }
});

app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}/mcp`);
});
