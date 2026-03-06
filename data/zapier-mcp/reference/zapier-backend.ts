import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";

import type { GatewayRequestHandlers } from "./types.js";

const ZAPIER_SERVER_NAME = "zapier-mcp";

// Find mcporter config file (same logic as pipedream.ts)
function findMcporterConfig(): string | null {
  const candidates = [
    path.join(os.homedir(), "clawd", "config", "mcporter.json"),
    path.join(os.homedir(), "clawdbot", "config", "mcporter.json"),
    path.join(os.homedir(), ".config", "mcporter", "config.json"),
    path.join(os.homedir(), ".mcporter.json"),
  ];

  for (const configPath of candidates) {
    if (fs.existsSync(configPath)) {
      return configPath;
    }
  }
  return null;
}

type McpServerEntry = {
  baseUrl?: string;
  command?: string;
  headers?: Record<string, string>;
  env?: Record<string, string>;
};

type McporterConfig = {
  mcpServers?: Record<string, McpServerEntry>;
  imports?: unknown[];
};

function readMcporterConfig(): McporterConfig | null {
  const configPath = findMcporterConfig();
  if (!configPath) return null;

  try {
    const content = fs.readFileSync(configPath, "utf-8");
    return JSON.parse(content) as McporterConfig;
  } catch {
    return null;
  }
}

function writeMcporterConfig(config: McporterConfig): boolean {
  let configPath = findMcporterConfig();

  if (!configPath) {
    // Create default path
    configPath = path.join(os.homedir(), "clawd", "config", "mcporter.json");
    const dir = path.dirname(configPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  try {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    return true;
  } catch {
    return false;
  }
}

function getZapierConfig(): { configured: boolean; mcpUrl: string | null; serverName: string } {
  const config = readMcporterConfig();
  if (!config?.mcpServers) {
    return { configured: false, mcpUrl: null, serverName: ZAPIER_SERVER_NAME };
  }

  const zapierEntry = config.mcpServers[ZAPIER_SERVER_NAME];
  if (!zapierEntry?.baseUrl) {
    return { configured: false, mcpUrl: null, serverName: ZAPIER_SERVER_NAME };
  }

  return {
    configured: true,
    mcpUrl: zapierEntry.baseUrl,
    serverName: ZAPIER_SERVER_NAME,
  };
}

/**
 * Parse SSE response from Zapier MCP.
 * Zapier returns responses in Server-Sent Events format:
 *   event: message
 *   data: {"result":...,"jsonrpc":"2.0","id":1}
 */
function parseSseResponse(text: string): unknown {
  const lines = text.split("\n");
  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const jsonStr = line.slice(6).trim();
      if (jsonStr) {
        return JSON.parse(jsonStr);
      }
    }
  }
  // Fallback: try parsing the whole thing as JSON
  return JSON.parse(text);
}

async function testZapierUrl(
  mcpUrl: string,
): Promise<{ success: boolean; toolCount?: number; error?: string }> {
  try {
    const response = await fetch(mcpUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json, text/event-stream",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "tools/list",
      }),
    });

    if (!response.ok) {
      return { success: false, error: `HTTP ${response.status}: ${response.statusText}` };
    }

    const text = await response.text();
    const data = parseSseResponse(text) as {
      error?: { message?: string };
      result?: { tools?: unknown[] };
    };

    if (data.error) {
      return { success: false, error: data.error.message || "API error" };
    }

    const toolCount = data.result?.tools?.length || 0;
    return { success: true, toolCount };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { success: false, error: message };
  }
}

export const zapierHandlers: GatewayRequestHandlers = {
  "zapier.status": async ({ respond }) => {
    try {
      const status = getZapierConfig();

      let toolCount: number | undefined;
      let testError: string | undefined;

      // If configured, test the connection
      if (status.configured && status.mcpUrl) {
        const testResult = await testZapierUrl(status.mcpUrl);
        if (testResult.success) {
          toolCount = testResult.toolCount;
        } else {
          testError = testResult.error;
        }
      }

      respond(true, {
        configured: status.configured,
        mcpUrl: status.mcpUrl,
        serverName: status.serverName,
        toolCount,
        testError,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { configured: false, error: message });
    }
  },

  "zapier.save": async ({ respond, params }) => {
    try {
      const mcpUrl = typeof params?.mcpUrl === "string" ? params.mcpUrl.trim() : "";

      if (!mcpUrl) {
        respond(true, { success: false, error: "MCP URL is required" });
        return;
      }

      // Validate URL format
      if (!mcpUrl.startsWith("https://")) {
        respond(true, { success: false, error: "MCP URL must use HTTPS" });
        return;
      }

      // Test the URL first
      const testResult = await testZapierUrl(mcpUrl);
      if (!testResult.success) {
        respond(true, { success: false, error: `Connection test failed: ${testResult.error}` });
        return;
      }

      // Read existing config
      let config = readMcporterConfig();
      if (!config) {
        config = { mcpServers: {}, imports: [] };
      }
      if (!config.mcpServers) {
        config.mcpServers = {};
      }

      // Add/update Zapier server entry
      // Zapier MCP uses SSE transport, needs Accept header for text/event-stream
      config.mcpServers[ZAPIER_SERVER_NAME] = {
        baseUrl: mcpUrl,
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json, text/event-stream",
        },
      };

      // Write config
      const written = writeMcporterConfig(config);
      if (!written) {
        respond(true, { success: false, error: "Failed to write config file" });
        return;
      }

      respond(true, {
        success: true,
        toolCount: testResult.toolCount,
        serverName: ZAPIER_SERVER_NAME,
        message: `Zapier MCP connected with ${testResult.toolCount} tools available`,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "zapier.test": async ({ respond, params }) => {
    try {
      let mcpUrl = typeof params?.mcpUrl === "string" ? params.mcpUrl.trim() : "";

      if (!mcpUrl) {
        // Use saved URL if not provided
        const status = getZapierConfig();
        if (!status.mcpUrl) {
          respond(true, { success: false, error: "No URL configured" });
          return;
        }
        mcpUrl = status.mcpUrl;
      }

      const testResult = await testZapierUrl(mcpUrl);
      respond(true, testResult);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "zapier.disconnect": async ({ respond }) => {
    try {
      const config = readMcporterConfig();
      if (!config?.mcpServers?.[ZAPIER_SERVER_NAME]) {
        respond(true, { success: true, message: "Already disconnected" });
        return;
      }

      delete config.mcpServers[ZAPIER_SERVER_NAME];

      const written = writeMcporterConfig(config);
      if (!written) {
        respond(true, { success: false, error: "Failed to write config file" });
        return;
      }

      respond(true, { success: true, message: "Zapier MCP disconnected" });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "zapier.tools": async ({ respond }) => {
    try {
      const status = getZapierConfig();
      if (!status.configured || !status.mcpUrl) {
        respond(true, { success: false, error: "Not configured", tools: [] });
        return;
      }

      const response = await fetch(status.mcpUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json, text/event-stream",
        },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: 1,
          method: "tools/list",
        }),
      });

      if (!response.ok) {
        respond(true, { success: false, error: `HTTP ${response.status}`, tools: [] });
        return;
      }

      const text = await response.text();
      const data = parseSseResponse(text) as {
        error?: { message?: string };
        result?: { tools?: Array<{ name: string; description?: string }> };
      };

      if (data.error) {
        respond(true, { success: false, error: data.error.message, tools: [] });
        return;
      }

      const tools = data.result?.tools || [];
      respond(true, { success: true, tools });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message, tools: [] });
    }
  },
};
