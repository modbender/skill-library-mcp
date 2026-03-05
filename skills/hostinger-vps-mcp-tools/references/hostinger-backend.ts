import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { exec } from "node:child_process";
import { promisify } from "node:util";
import type { GatewayRequestHandlers } from "./types.js";

const execAsync = promisify(exec);

const HOSTINGER_SERVER_NAME = "hostinger-api";
const HOSTINGER_CONFIG_PATH = path.join(os.homedir(), ".openclaw", "workspace", "config", "hostinger.json");
const VAULT_PATH = path.join(os.homedir(), ".openclaw", "secrets.json");
const VAULT_KEY = "HOSTINGER_API_TOKEN";

function readVault(): Record<string, string> {
  try {
    if (fs.existsSync(VAULT_PATH)) {
      return JSON.parse(fs.readFileSync(VAULT_PATH, "utf-8")) as Record<string, string>;
    }
  } catch { /* ignore */ }
  return {};
}

function writeVaultToken(token: string): void {
  const vault = readVault();
  vault[VAULT_KEY] = token;
  fs.mkdirSync(path.dirname(VAULT_PATH), { recursive: true });
  fs.writeFileSync(VAULT_PATH, JSON.stringify(vault, null, 2) + "\n", { mode: 0o600 });
}

function deleteVaultToken(): void {
  const vault = readVault();
  delete vault[VAULT_KEY];
  fs.writeFileSync(VAULT_PATH, JSON.stringify(vault, null, 2) + "\n", { mode: 0o600 });
}

function getTokenFromVault(): string | null {
  return readVault()[VAULT_KEY] ?? null;
}

function findMcporterConfig(): string | null {
  const candidates = [
    path.join(os.homedir(), ".openclaw", "workspace", "config", "mcporter.json"),
    path.join(os.homedir(), ".config", "mcporter", "config.json"),
    path.join(os.homedir(), ".mcporter.json"),
  ];
  for (const configPath of candidates) {
    if (fs.existsSync(configPath)) return configPath;
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
    return JSON.parse(fs.readFileSync(configPath, "utf-8")) as McporterConfig;
  } catch {
    return null;
  }
}

function writeMcporterConfig(config: McporterConfig): boolean {
  let configPath = findMcporterConfig();
  if (!configPath) {
    configPath = path.join(os.homedir(), ".openclaw", "workspace", "config", "mcporter.json");
    fs.mkdirSync(path.dirname(configPath), { recursive: true });
  }
  try {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    return true;
  } catch {
    return false;
  }
}

function readHostingerConfig(): { githubRepo: string } {
  try {
    if (fs.existsSync(HOSTINGER_CONFIG_PATH)) {
      return JSON.parse(fs.readFileSync(HOSTINGER_CONFIG_PATH, "utf-8")) as { githubRepo: string };
    }
  } catch { /* ignore */ }
  return { githubRepo: "" };
}

function writeHostingerConfig(data: { githubRepo: string }): void {
  fs.mkdirSync(path.dirname(HOSTINGER_CONFIG_PATH), { recursive: true });
  fs.writeFileSync(HOSTINGER_CONFIG_PATH, JSON.stringify(data, null, 2));
}

function maskToken(token: string): string {
  if (!token || token.length <= 4) return "••••";
  return "••••" + token.slice(-4);
}

function getHostingerToken(): string | null {
  // Primary: vault. Fallback: mcporter.json env (backwards compat)
  const vaultToken = getTokenFromVault();
  if (vaultToken) return vaultToken;
  const cfg = readMcporterConfig();
  return cfg?.mcpServers?.[HOSTINGER_SERVER_NAME]?.env?.["API_TOKEN"] ?? null;
}

export const hostingerHandlers: GatewayRequestHandlers = {
  "hostinger.status": async ({ respond }) => {
    try {
      const token = getHostingerToken();
      const { githubRepo } = readHostingerConfig();
      respond(true, {
        configured: !!token,
        apiToken: token ? maskToken(token) : "",
        githubRepo,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { configured: false, error: message });
    }
  },

  "hostinger.save": async ({ respond, params }) => {
    try {
      const apiToken = typeof params?.apiToken === "string" ? params.apiToken.trim() : "";
      const githubRepo = typeof params?.githubRepo === "string" ? params.githubRepo.trim() : "";

      if (!apiToken) {
        respond(true, { success: false, error: "API token is required" });
        return;
      }

      let config = readMcporterConfig();
      if (!config) config = { mcpServers: {}, imports: [] };
      if (!config.mcpServers) config.mcpServers = {};

      // Store token in vault (secrets.json) — not plaintext in mcporter
      writeVaultToken(apiToken);

      // mcporter entry uses a SecretRef so the plaintext isn't duplicated
      // The gateway resolves vault refs when needed; mcporter itself is given the token via env at call time
      config.mcpServers[HOSTINGER_SERVER_NAME] = {
        command: "hostinger-api-mcp",
        env: { API_TOKEN: { source: "file", provider: "default", id: `/${VAULT_KEY}` } as unknown as string },
      };

      if (!writeMcporterConfig(config)) {
        respond(true, { success: false, error: "Failed to write mcporter config" });
        return;
      }

      writeHostingerConfig({ githubRepo });

      respond(true, { success: true, message: "Hostinger API configured successfully" });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "hostinger.disconnect": async ({ respond }) => {
    try {
      const config = readMcporterConfig();
      if (!config?.mcpServers?.[HOSTINGER_SERVER_NAME]) {
        respond(true, { success: true, message: "Already disconnected" });
        return;
      }
      delete config.mcpServers[HOSTINGER_SERVER_NAME];
      writeMcporterConfig(config);
      deleteVaultToken();
      respond(true, { success: true, message: "Hostinger API disconnected" });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "hostinger.tools": async ({ respond }) => {
    try {
      const token = getHostingerToken();
      if (!token) {
        respond(true, { success: false, error: "Not configured", tools: [] });
        return;
      }

      const { stdout } = await execAsync("mcporter list hostinger-api --schema", {
        env: { ...process.env, API_TOKEN: token, HOSTINGER_API_TOKEN: token },
        timeout: 30000,
      });

      // Parse mcporter list output — tools are listed as lines
      const lines = stdout.split("\n").filter(Boolean);
      const tools: Array<{ name: string; description?: string }> = [];

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith("#") || trimmed.startsWith("Server:")) continue;
        // Lines look like: "  tool_name  Description here"
        const match = trimmed.match(/^(\S+)\s*(.*)?$/);
        if (match) {
          tools.push({ name: match[1], description: match[2]?.trim() || undefined });
        }
      }

      respond(true, { success: true, tools });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message, tools: [] });
    }
  },
};
