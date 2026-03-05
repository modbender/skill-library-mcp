import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import type { GatewayRequestHandlers } from "./types.js";

// ── Vault (secrets.json) ──────────────────────────────────────────────────────

const VAULT_PATH = path.join(os.homedir(), ".openclaw", "secrets.json");
const VAULT_KEY_CLIENT_ID     = "PIPEDREAM_CLIENT_ID";
const VAULT_KEY_CLIENT_SECRET = "PIPEDREAM_CLIENT_SECRET";

function readVault(): Record<string, string> {
  try {
    if (fs.existsSync(VAULT_PATH)) {
      return JSON.parse(fs.readFileSync(VAULT_PATH, "utf-8")) as Record<string, string>;
    }
  } catch { /* ignore */ }
  return {};
}

function writeVault(data: Record<string, string>): void {
  fs.mkdirSync(path.dirname(VAULT_PATH), { recursive: true });
  fs.writeFileSync(VAULT_PATH, JSON.stringify(data, null, 2) + "\n", { mode: 0o600 });
}

function vaultGet(key: string): string | null {
  return readVault()[key] ?? null;
}

function vaultSet(pairs: Record<string, string>): void {
  const vault = readVault();
  Object.assign(vault, pairs);
  writeVault(vault);
}

function vaultDel(keys: string[]): void {
  const vault = readVault();
  for (const k of keys) delete vault[k];
  writeVault(vault);
}

// ── Pipedream config (non-secret fields only) ─────────────────────────────────

interface PipedreamConfig {
  projectId: string;
  environment: string;
  externalUserId: string;
}

// Full credential shape used internally — secrets resolved from vault at runtime
interface PipedreamCredentials extends PipedreamConfig {
  clientId: string;
  clientSecret: string;
}

function getPipedreamCredentialsPath(): string {
  return path.join(os.homedir(), ".openclaw", "workspace", "config", "pipedream-credentials.json");
}

function readPipedreamConfig(): PipedreamConfig | null {
  const credPath = getPipedreamCredentialsPath();
  try {
    if (fs.existsSync(credPath)) {
      return JSON.parse(fs.readFileSync(credPath, "utf-8")) as PipedreamConfig;
    }
  } catch { /* ignore */ }
  return null;
}

function writePipedreamConfig(cfg: PipedreamConfig): boolean {
  const credPath = getPipedreamCredentialsPath();
  try {
    fs.mkdirSync(path.dirname(credPath), { recursive: true });
    // Strip any secrets that may have leaked in — only save non-sensitive fields
    const safe: PipedreamConfig = {
      projectId: cfg.projectId,
      environment: cfg.environment,
      externalUserId: cfg.externalUserId,
    };
    fs.writeFileSync(credPath, JSON.stringify(safe, null, 2), { mode: 0o600 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Read full credentials: config file for non-secrets, vault for clientId/clientSecret.
 * Auto-migrates legacy plaintext credentials.json to vault on first read.
 */
function readPipedreamCredentials(): PipedreamCredentials | null {
  const cfg = readPipedreamConfig();

  // Resolve secrets from vault
  let clientId     = vaultGet(VAULT_KEY_CLIENT_ID);
  let clientSecret = vaultGet(VAULT_KEY_CLIENT_SECRET);

  // ── Auto-migration: if vault is missing secrets but credentials.json has them ──
  if ((!clientId || !clientSecret) && cfg) {
    const raw = (() => {
      try { return JSON.parse(fs.readFileSync(getPipedreamCredentialsPath(), "utf-8")); }
      catch { return null; }
    })() as Record<string, string> | null;

    if (raw?.clientId || raw?.clientSecret) {
      const migPairs: Record<string, string> = {};
      if (raw.clientId)     { migPairs[VAULT_KEY_CLIENT_ID]     = raw.clientId;     clientId     = raw.clientId; }
      if (raw.clientSecret) { migPairs[VAULT_KEY_CLIENT_SECRET] = raw.clientSecret; clientSecret = raw.clientSecret; }
      vaultSet(migPairs);
      // Rewrite credentials.json without secrets
      writePipedreamConfig(cfg);
      console.log("[pipedream] Auto-migrated clientId/clientSecret to vault (~/.openclaw/secrets.json)");
    }
  }

  if (!cfg || !clientId || !clientSecret) return null;

  return { ...cfg, clientId, clientSecret };
}

// ── Pipedream OAuth token ─────────────────────────────────────────────────────

async function getPipedreamAccessToken(clientId: string, clientSecret: string): Promise<string> {
  const response = await fetch("https://api.pipedream.com/v1/oauth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      grant_type: "client_credentials",
      client_id: clientId,
      client_secret: clientSecret,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Pipedream auth failed: ${errorText}`);
  }

  const data = await response.json();
  if (!data.access_token) throw new Error("No access_token in Pipedream response");
  return data.access_token;
}

// ── mcporter config ───────────────────────────────────────────────────────────

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

function readMcporterConfig(): { servers: Record<string, unknown> } | null {
  const configPath = findMcporterConfig();
  if (!configPath) return null;
  try {
    const config = JSON.parse(fs.readFileSync(configPath, "utf-8"));
    return { servers: config.mcpServers || {} };
  } catch {
    return null;
  }
}

function writeMcporterConfig(servers: Record<string, unknown>): boolean {
  const configPath = findMcporterConfig();
  const defaultPath = path.join(os.homedir(), ".openclaw", "workspace", "config", "mcporter.json");
  const target = configPath ?? defaultPath;

  try {
    if (!configPath) {
      fs.mkdirSync(path.dirname(defaultPath), { recursive: true });
      fs.writeFileSync(defaultPath, JSON.stringify({ mcpServers: servers, imports: [] }, null, 2));
      return true;
    }
    const content = fs.readFileSync(target, "utf-8");
    const config = JSON.parse(content);
    config.mcpServers = servers;
    fs.writeFileSync(target, JSON.stringify(config, null, 2));
    return true;
  } catch {
    return false;
  }
}

/**
 * Build a safe mcporter server entry for a Pipedream app connection.
 * - Access token goes in Authorization header (short-lived JWT, acceptable)
 * - clientSecret is NOT stored in mcporter.json env (only in vault)
 * - clientId, projectId, env, agentId are non-sensitive identifiers
 */
function buildMcporterEntry(params: {
  accessToken: string;
  credentials: PipedreamCredentials;
  externalUserId: string;
  appSlug: string;
}): Record<string, unknown> {
  const { accessToken, credentials, externalUserId, appSlug } = params;
  const mcpAppSlug = appSlug.replace(/-/g, "_");
  return {
    baseUrl: "https://remote.mcp.pipedream.net",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "x-pd-project-id": credentials.projectId,
      "x-pd-environment": credentials.environment,
      "x-pd-external-user-id": externalUserId,
      "x-pd-app-slug": mcpAppSlug,
      Accept: "application/json, text/event-stream",
      "Content-Type": "application/json",
    },
    env: {
      // Non-sensitive identifiers only — clientSecret stays in vault
      PIPEDREAM_CLIENT_ID:  credentials.clientId,
      PIPEDREAM_PROJECT_ID: credentials.projectId,
      PIPEDREAM_ENVIRONMENT: credentials.environment,
      PIPEDREAM_AGENT_ID:   externalUserId,
      PIPEDREAM_APP_SLUG:   mcpAppSlug,
    },
  };
}

// ── Global handlers ───────────────────────────────────────────────────────────

export const pipedreamHandlers: GatewayRequestHandlers = {
  "pipedream.status": async ({ respond }) => {
    try {
      const config = readMcporterConfig();
      const apps: Array<{ slug: string; name: string; serverName: string }> = [];

      // readPipedreamCredentials() auto-migrates plaintext → vault on first call
      const credentials = readPipedreamCredentials();

      if (config) {
        for (const [name, server] of Object.entries(config.servers)) {
          if (name.startsWith("pipedream-")) {
            const srv = server as { env?: Record<string, string>; headers?: Record<string, string> };
            const env = srv.env || {};
            const headers = srv.headers || {};
            const appSlug = env.PIPEDREAM_APP_SLUG || headers["x-pd-app-slug"];
            if (appSlug) {
              apps.push({ slug: appSlug, name: appSlugToName(appSlug), serverName: name });
            }
          }
        }
      }

      respond(true, {
        configured: !!credentials,
        credentials: credentials
          ? {
              clientId: credentials.clientId,
              hasSecret: !!credentials.clientSecret,
              projectId: credentials.projectId,
              environment: credentials.environment,
              externalUserId: credentials.externalUserId,
            }
          : null,
        apps,
      }, undefined);
    } catch (e) {
      respond(true, { error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "pipedream.saveCredentials": async ({ params, respond }) => {
    try {
      const { clientId, projectId, environment, externalUserId } = params as {
        clientId: string;
        clientSecret?: string;
        projectId: string;
        environment: string;
        externalUserId: string;
      };

      // If clientSecret omitted (placeholder dots sent), keep existing stored secret from vault
      const existingSecret = vaultGet(VAULT_KEY_CLIENT_SECRET);
      const resolvedSecret = (params as { clientSecret?: string }).clientSecret?.trim() || existingSecret || "";

      if (!resolvedSecret) {
        respond(true, { success: false, error: "Client Secret is required" }, undefined);
        return;
      }

      // Validate by getting an access token from Pipedream
      let accessToken: string;
      try {
        accessToken = await getPipedreamAccessToken(clientId, resolvedSecret);
      } catch (e) {
        respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
        return;
      }

      // Write secrets to vault — NOT to pipedream-credentials.json
      vaultSet({
        [VAULT_KEY_CLIENT_ID]:     clientId,
        [VAULT_KEY_CLIENT_SECRET]: resolvedSecret,
      });

      // Write non-secret config to pipedream-credentials.json
      const stored = writePipedreamConfig({ projectId, environment, externalUserId });
      if (!stored) {
        respond(true, { success: false, error: "Failed to store config" }, undefined);
        return;
      }

      respond(true, { success: true, accessToken }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "pipedream.getToken": async ({ respond }) => {
    try {
      const credentials = readPipedreamCredentials();
      if (!credentials) {
        respond(true, { success: false, error: "No credentials configured" }, undefined);
        return;
      }
      const accessToken = await getPipedreamAccessToken(credentials.clientId, credentials.clientSecret);
      respond(true, {
        success: true,
        accessToken,
        credentials: {
          clientId: credentials.clientId,
          projectId: credentials.projectId,
          environment: credentials.environment,
          externalUserId: credentials.externalUserId,
        },
      }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "pipedream.getConnectUrl": async ({ params, respond }) => {
    try {
      const { appSlug } = params as { appSlug: string };
      const credentials = readPipedreamCredentials();
      if (!credentials) {
        respond(true, { success: false, error: "No credentials configured" }, undefined);
        return;
      }
      const accessToken = await getPipedreamAccessToken(credentials.clientId, credentials.clientSecret);
      const connectResponse = await fetch(
        `https://api.pipedream.com/v1/connect/${credentials.projectId}/tokens`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
            "x-pd-environment": credentials.environment,
          },
          body: JSON.stringify({
            external_user_id: credentials.externalUserId,
            app: appSlug.replace(/-/g, "_"),
          }),
        },
      );
      if (!connectResponse.ok) {
        const errorText = await connectResponse.text();
        respond(true, { success: false, error: `Failed to create connect token: ${errorText}` }, undefined);
        return;
      }
      const connectData = await connectResponse.json();
      const appParam = appSlug.replace(/-/g, "_");
      const connectUrl = connectData.connect_link_url.includes("?")
        ? `${connectData.connect_link_url}&app=${appParam}`
        : `${connectData.connect_link_url}?app=${appParam}`;
      respond(true, { success: true, connectUrl, token: connectData.token, expiresAt: connectData.expires_at }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "pipedream.connectApp": async ({ params, respond }) => {
    try {
      const { appSlug, accessToken, agentId } = params as {
        appSlug: string;
        accessToken: string;
        agentId?: string;
      };
      const credentials = readPipedreamCredentials();
      if (!credentials) {
        respond(true, { success: false, error: "No credentials configured" }, undefined);
        return;
      }
      const externalUserId = agentId
        ? (resolveAgentExternalUserId(agentId) ?? agentId)
        : credentials.externalUserId;

      const config = readMcporterConfig() || { servers: {} };
      const serverName = `pipedream-${externalUserId}-${appSlug}`.replace(/[^a-z0-9-]/g, "-");
      config.servers[serverName] = buildMcporterEntry({ accessToken, credentials, externalUserId, appSlug });
      const success = writeMcporterConfig(config.servers);
      respond(true, { success, serverName }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "pipedream.disconnectApp": async ({ params, respond }) => {
    try {
      const { serverName } = params as { serverName: string };
      const config = readMcporterConfig();
      if (!config) {
        respond(true, { success: false, error: "No config found" }, undefined);
        return;
      }
      delete config.servers[serverName];
      const success = writeMcporterConfig(config.servers);
      respond(true, { success }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "pipedream.refreshToken": async ({ params, respond }) => {
    try {
      const { serverName, accessToken } = params as { serverName: string; accessToken: string };
      const config = readMcporterConfig();
      if (!config) {
        respond(true, { success: false, error: "No config found" }, undefined);
        return;
      }
      const server = config.servers[serverName] as { headers?: Record<string, string> } | undefined;
      if (!server) {
        respond(true, { success: false, error: "Server not found" }, undefined);
        return;
      }
      if (!server.headers) server.headers = {};
      server.headers.Authorization = `Bearer ${accessToken}`;
      const success = writeMcporterConfig(config.servers);
      respond(true, { success }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function appSlugToName(slug: string): string {
  const names: Record<string, string> = {
    gmail: "Gmail",
    "google-calendar": "Google Calendar",
    "google-sheets": "Google Sheets",
    "google-drive": "Google Drive",
    slack: "Slack",
    notion: "Notion",
    github: "GitHub",
    linear: "Linear",
    discord: "Discord",
    twitter: "Twitter/X",
    airtable: "Airtable",
    hubspot: "HubSpot",
    asana: "Asana",
    trello: "Trello",
    dropbox: "Dropbox",
    openai: "OpenAI",
  };
  return names[slug] || slug.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

// ── Per-Agent config ──────────────────────────────────────────────────────────

interface AgentPipedreamConfig {
  externalUserId: string;
  enabledApps: string[];
  connectedApps: string[];
}

function getAgentPipedreamDir(): string {
  return path.join(os.homedir(), ".openclaw", "workspace", "config", "integrations", "pipedream");
}

function getAgentPipedreamPath(agentId: string): string {
  const safe = agentId.replace(/[^a-zA-Z0-9_-]/g, "_");
  return path.join(getAgentPipedreamDir(), `${safe}.json`);
}

function readAgentPipedreamConfig(agentId: string): AgentPipedreamConfig | null {
  try {
    const configPath = getAgentPipedreamPath(agentId);
    if (fs.existsSync(configPath)) {
      return JSON.parse(fs.readFileSync(configPath, "utf-8")) as AgentPipedreamConfig;
    }
  } catch { /* ignore */ }
  return null;
}

function writeAgentPipedreamConfig(agentId: string, config: AgentPipedreamConfig): boolean {
  try {
    fs.mkdirSync(getAgentPipedreamDir(), { recursive: true });
    fs.writeFileSync(getAgentPipedreamPath(agentId), JSON.stringify(config, null, 2));
    return true;
  } catch {
    return false;
  }
}

export function resolveAgentExternalUserId(agentId: string): string | null {
  const agentConfig = readAgentPipedreamConfig(agentId);
  return agentConfig?.externalUserId ?? agentId ?? null;
}

async function ensureMcporterServer(params: {
  appSlug: string;
  externalUserId: string;
  credentials: PipedreamCredentials;
}): Promise<{ serverName: string; created: boolean }> {
  const { appSlug, externalUserId, credentials } = params;
  const serverName = `pipedream-${externalUserId}-${appSlug}`.replace(/[^a-z0-9-]/g, "-");
  const config = readMcporterConfig() || { servers: {} };

  if (config.servers[serverName]) return { serverName, created: false };

  const accessToken = await getPipedreamAccessToken(credentials.clientId, credentials.clientSecret);
  config.servers[serverName] = buildMcporterEntry({ accessToken, credentials, externalUserId, appSlug });
  writeMcporterConfig(config.servers);
  return { serverName, created: true };
}

// ── Per-Agent handlers ────────────────────────────────────────────────────────

export const pipedreamAgentHandlers: GatewayRequestHandlers = {
  "pipedream.agent.status": async ({ respond, params }) => {
    try {
      const agentId = (params as { agentId?: string }).agentId;
      if (!agentId) { respond(false, { error: "agentId is required" }); return; }

      const config = readAgentPipedreamConfig(agentId);
      const globalCreds = readPipedreamCredentials();
      const externalUserId = config?.externalUserId ?? agentId;

      let connectedApps: Array<{ slug: string; name: string; icon: string; accountName?: string }> = [];
      if (globalCreds) {
        try {
          const accessToken = await getPipedreamAccessToken(globalCreds.clientId, globalCreds.clientSecret);
          const accountsRes = await fetch(
            `https://api.pipedream.com/v1/connect/${globalCreds.projectId}/accounts?external_user_id=${encodeURIComponent(externalUserId)}&include_credentials=false`,
            { headers: { Authorization: `Bearer ${accessToken}`, "x-pd-environment": globalCreds.environment } },
          );
          if (accountsRes.ok) {
            const data = await accountsRes.json();
            const accounts: Array<{ app: { name_slug: string; name: string; img_src?: string }; name?: string }> = data.data ?? [];
            connectedApps = accounts
              .map((acct) => ({ slug: acct.app?.name_slug ?? "", name: acct.app?.name ?? acct.app?.name_slug ?? "", icon: "🔌", accountName: acct.name ?? undefined }))
              .filter((a) => a.slug);
          }
        } catch {
          connectedApps = (config?.connectedApps ?? []).map((s: string) => ({ slug: s, name: s, icon: "🔌" }));
        }
      }

      const mcConfig = readMcporterConfig();
      const mcServers = mcConfig?.servers ?? {};
      const appsWithStatus = connectedApps.map((app) => {
        const serverName = `pipedream-${externalUserId}-${app.slug}`.replace(/[^a-z0-9-]/g, "-");
        const slugSuffix = `-${app.slug.replace(/[^a-z0-9-]/g, "-")}`;
        const hasServer = !!mcServers[serverName] || Object.keys(mcServers).some((k) => k.startsWith("pipedream-") && k.endsWith(slugSuffix));
        return { ...app, active: hasServer };
      });

      respond(true, {
        configured: !!config,
        globalConfigured: !!globalCreds,
        environment: globalCreds?.environment ?? "development",
        externalUserId,
        enabledApps: config?.enabledApps ?? [],
        connectedApps: appsWithStatus,
      });
    } catch (err) {
      respond(false, { error: String(err) });
    }
  },

  "pipedream.agent.save": async ({ respond, params }) => {
    try {
      const { agentId, externalUserId, enabledApps, connectedApps } = params as {
        agentId?: string; externalUserId?: string; enabledApps?: string[]; connectedApps?: string[];
      };
      if (!agentId) { respond(false, { error: "agentId is required" }); return; }
      const existing = readAgentPipedreamConfig(agentId);
      const config: AgentPipedreamConfig = {
        externalUserId: externalUserId ?? existing?.externalUserId ?? agentId,
        enabledApps: enabledApps ?? existing?.enabledApps ?? [],
        connectedApps: connectedApps ?? existing?.connectedApps ?? [],
      };
      const ok = writeAgentPipedreamConfig(agentId, config);
      respond(ok, ok ? { success: true, config } : { error: "Failed to write config" });
    } catch (err) {
      respond(false, { error: String(err) });
    }
  },

  "pipedream.agent.delete": async ({ respond, params }) => {
    try {
      const agentId = (params as { agentId?: string }).agentId;
      if (!agentId) { respond(false, { error: "agentId is required" }); return; }
      const configPath = getAgentPipedreamPath(agentId);
      if (fs.existsSync(configPath)) fs.unlinkSync(configPath);
      respond(true, { success: true });
    } catch (err) {
      respond(false, { error: String(err) });
    }
  },

  "pipedream.connect": async ({ params, respond }) => {
    try {
      const { agentId, appSlug } = params as { agentId?: string; appSlug?: string };
      if (!agentId || !appSlug) { respond(false, { error: "agentId and appSlug are required" }); return; }
      const credentials = readPipedreamCredentials();
      if (!credentials) {
        respond(false, { error: "No Pipedream credentials configured. Set them up in the Pipedream tab first." });
        return;
      }
      const externalUserId = resolveAgentExternalUserId(agentId) ?? agentId;
      const accessToken = await getPipedreamAccessToken(credentials.clientId, credentials.clientSecret);
      const connectResponse = await fetch(
        `https://api.pipedream.com/v1/connect/${credentials.projectId}/tokens`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}`, "x-pd-environment": credentials.environment },
          body: JSON.stringify({ external_user_id: externalUserId, app: appSlug.replace(/-/g, "_") }),
        },
      );
      if (!connectResponse.ok) {
        const errorText = await connectResponse.text();
        respond(false, { error: `Failed to create connect token: ${errorText}` });
        return;
      }
      const connectData = await connectResponse.json();
      const appParam = appSlug.replace(/-/g, "_");
      const connectUrl = connectData.connect_link_url.includes("?")
        ? `${connectData.connect_link_url}&app=${appParam}`
        : `${connectData.connect_link_url}?app=${appParam}`;
      respond(true, { connectUrl, token: connectData.token, expiresAt: connectData.expires_at });
    } catch (err) {
      respond(false, { error: String(err) });
    }
  },

  "pipedream.activate": async ({ params, respond }) => {
    try {
      const { agentId, appSlug } = params as { agentId?: string; appSlug?: string };
      if (!agentId || !appSlug) { respond(false, { error: "agentId and appSlug are required" }); return; }
      const credentials = readPipedreamCredentials();
      if (!credentials) { respond(false, { error: "No Pipedream credentials configured" }); return; }
      const externalUserId = resolveAgentExternalUserId(agentId) ?? agentId;

      const accessToken = await getPipedreamAccessToken(credentials.clientId, credentials.clientSecret);
      const accountsRes = await fetch(
        `https://api.pipedream.com/v1/connect/${credentials.projectId}/accounts?external_user_id=${encodeURIComponent(externalUserId)}&include_credentials=false`,
        { headers: { Authorization: `Bearer ${accessToken}`, "x-pd-environment": credentials.environment } },
      );
      if (!accountsRes.ok) {
        respond(true, { ok: false, error: "Failed to verify connection with Pipedream API" });
        return;
      }
      const data = (await accountsRes.json()) as { data?: Array<{ app?: { name_slug?: string } }> };
      const normalizedSlug = appSlug.replace(/-/g, "_");
      const found = (data.data ?? []).some((a) => a.app?.name_slug === appSlug || a.app?.name_slug === normalizedSlug);
      if (!found) {
        respond(true, { ok: false, error: `No Pipedream connection found for ${appSlug}. Complete OAuth first.` });
        return;
      }

      const { serverName } = await ensureMcporterServer({ appSlug, externalUserId, credentials });

      const { execSync } = await import("node:child_process");
      const pathMod = await import("node:path");
      const nodeBinDir = pathMod.dirname(process.execPath);
      const brewBinDir = "/home/linuxbrew/.linuxbrew/bin";
      const execEnv = { ...process.env, PATH: `${nodeBinDir}:${brewBinDir}:${process.env.PATH ?? ""}` };
      let toolCount = 0;
      let tools: Array<{ name: string; description?: string }> = [];
      try {
        const result = execSync(`mcporter list ${serverName} --schema --json 2>/dev/null`, {
          timeout: 15000, encoding: "utf-8", env: execEnv,
          cwd: process.env.HOME ? `${process.env.HOME}/.openclaw/workspace` : undefined,
        });
        const parsed = JSON.parse(result) as Record<string, unknown>;
        if (parsed.tools && Array.isArray(parsed.tools)) {
          tools = (parsed.tools as Array<{ name: string; description?: string }>).map((t) => ({ name: t.name, description: t.description }));
          toolCount = tools.length;
        }
      } catch (mcpErr) {
        console.error("[pipedream.activate] mcporter list failed:", String(mcpErr));
      }

      respond(true, { ok: true, serverName, toolCount, tools });
    } catch (err) {
      respond(false, { error: String(err) });
    }
  },

  "pipedream.disconnect": async ({ params, respond }) => {
    try {
      const { agentId, appSlug } = params as { agentId?: string; appSlug?: string };
      if (!agentId || !appSlug) { respond(false, { error: "agentId and appSlug are required" }); return; }
      const externalUserId = resolveAgentExternalUserId(agentId) ?? agentId;
      const globalCreds = readPipedreamCredentials();

      if (globalCreds) {
        try {
          const accessToken = await getPipedreamAccessToken(globalCreds.clientId, globalCreds.clientSecret);
          const accountsRes = await fetch(
            `https://api.pipedream.com/v1/connect/${globalCreds.projectId}/accounts?external_user_id=${encodeURIComponent(externalUserId)}&include_credentials=false`,
            { headers: { Authorization: `Bearer ${accessToken}`, "x-pd-environment": globalCreds.environment } },
          );
          if (accountsRes.ok) {
            const data = (await accountsRes.json()) as { data?: Array<{ id: string; app?: { name_slug?: string } }> };
            const normalizedSlug = appSlug.replace(/-/g, "_");
            const account = (data.data ?? []).find((a) => a.app?.name_slug === appSlug || a.app?.name_slug === normalizedSlug);
            if (account) {
              const delRes = await fetch(
                `https://api.pipedream.com/v1/connect/${globalCreds.projectId}/accounts/${account.id}`,
                { method: "DELETE", headers: { Authorization: `Bearer ${accessToken}`, "x-pd-environment": globalCreds.environment } },
              );
              if (!delRes.ok && delRes.status !== 204 && delRes.status !== 404) {
                const errBody = await delRes.text().catch(() => "");
                respond(true, { success: false, error: `Pipedream API delete failed (${delRes.status}): ${errBody}` });
                return;
              }
            }
          }
        } catch { /* log but continue — clean up local config even if API fails */ }
      }

      const config = readMcporterConfig() || { servers: {} };
      const expectedName = `pipedream-${externalUserId}-${appSlug}`.replace(/[^a-z0-9-]/g, "-");
      const slugSuffix = `-${appSlug.replace(/[^a-z0-9-]/g, "-")}`;
      const foundName = config.servers[expectedName]
        ? expectedName
        : Object.keys(config.servers).find((k) => k.startsWith("pipedream-") && k.endsWith(slugSuffix));
      if (foundName) {
        delete config.servers[foundName];
        writeMcporterConfig(config.servers);
      }

      const agentConfig = readAgentPipedreamConfig(agentId);
      if (agentConfig) {
        agentConfig.connectedApps = (agentConfig.connectedApps ?? []).filter((s: string) => s !== appSlug);
        writeAgentPipedreamConfig(agentId, agentConfig);
      }

      respond(true, { success: true });
    } catch (err) {
      respond(false, { error: String(err) });
    }
  },

  "pipedream.test": async ({ params, respond }) => {
    try {
      const { agentId, appSlug } = params as { agentId?: string; appSlug?: string };
      if (!agentId || !appSlug) { respond(false, { error: "agentId and appSlug are required" }); return; }
      const externalUserId = resolveAgentExternalUserId(agentId) ?? agentId;
      const expectedName = `pipedream-${externalUserId}-${appSlug}`.replace(/[^a-z0-9-]/g, "-");
      const config = readMcporterConfig();
      const servers = config?.servers ?? {};
      const slugSuffix = `-${appSlug.replace(/[^a-z0-9-]/g, "-")}`;
      const foundName = servers[expectedName]
        ? expectedName
        : Object.keys(servers).find((k) => k.startsWith("pipedream-") && k.endsWith(slugSuffix));

      let serverToTest = foundName;
      if (!serverToTest) {
        const credentials = readPipedreamCredentials();
        if (!credentials) {
          respond(true, { ok: false, message: `No mcporter server found for ${appSlug} and no Pipedream credentials configured` });
          return;
        }
        try {
          const result = await ensureMcporterServer({ appSlug, externalUserId, credentials });
          serverToTest = result.serverName;
        } catch (err) {
          respond(true, { ok: false, message: `Failed to create mcporter server for ${appSlug}: ${String(err)}` });
          return;
        }
      }

      const { execSync } = await import("node:child_process");
      const pathMod = await import("node:path");
      const nodeBinDir = pathMod.dirname(process.execPath);
      const brewBinDir = "/home/linuxbrew/.linuxbrew/bin";
      const execEnv = { ...process.env, PATH: `${nodeBinDir}:${brewBinDir}:${process.env.PATH ?? ""}` };
      let tools: Array<{ name: string; description?: string }> = [];
      try {
        const result = execSync(`mcporter list ${serverToTest} --schema --json 2>/dev/null`, {
          timeout: 15000, encoding: "utf-8", env: execEnv,
          cwd: process.env.HOME ? `${process.env.HOME}/.openclaw/workspace` : undefined,
        });
        const parsed = JSON.parse(result) as Record<string, unknown> | Array<unknown>;
        if (Array.isArray(parsed)) {
          tools = parsed as Array<{ name: string; description?: string }>;
        } else if ((parsed as Record<string, unknown>).servers) {
          const srvs = (parsed as { servers: Array<{ name: string; tools?: Array<{ name: string; description?: string }> }> }).servers;
          const match = srvs.find((s) => s.name === serverToTest);
          tools = match?.tools ?? [];
        } else if ((parsed as Record<string, unknown>).tools) {
          tools = ((parsed as { tools: Array<{ name: string; description?: string }> }).tools).map((t) => ({ name: t.name, description: t.description }));
        }
      } catch (mcpErr) {
        console.error("[pipedream.test] mcporter list failed:", String(mcpErr));
      }

      respond(true, {
        ok: true,
        message: `${appSlug} is configured as ${serverToTest}`,
        serverName: serverToTest,
        toolCount: tools.length,
        tools: tools.map((t) => ({ name: t.name, description: t.description })),
      });
    } catch (err) {
      respond(false, { error: String(err) });
    }
  },
};
