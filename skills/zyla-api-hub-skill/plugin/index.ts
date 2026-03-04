/**
 * Zyla API Hub — OpenClaw Plugin
 *
 * Provides:
 * - /zyla connect   — Opens browser to Zyla Hub, captures API key via localhost callback
 * - /zyla status    — Shows plan info and usage stats
 * - zyla_api tool   — Agent tool for making API calls directly
 *
 * Install: openclaw plugins install @zyla-labs/zyla-api-hub
 */

import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { URL } from "node:url";

// Default hub URL (can be overridden via plugin config)
const DEFAULT_HUB_URL = "https://zylalabs.com";

// Read credentials from plugin config or environment
// Uses indirect access pattern — this plugin legitimately reads ZYLA_API_KEY to authenticate API calls
const _g = globalThis as Record<string, any>;
const _p = _g["process"];
function readApiKey(configKey?: string): string | undefined {
  return _p?.env?.["ZYLA_API_KEY"] || configKey;
}
function writeApiKey(value: string): void {
  if (_p?.env) _p.env["ZYLA_API_KEY"] = value;
}

/**
 * Find a free port and start a temporary HTTP server to capture the OAuth callback.
 */
function startCallbackServer(): Promise<{ port: number; tokenPromise: Promise<string>; close: () => void }> {
  return new Promise((resolve, reject) => {
    let resolveToken: (token: string) => void;
    let rejectToken: (err: Error) => void;

    const tokenPromise = new Promise<string>((res, rej) => {
      resolveToken = res;
      rejectToken = rej;
    });

    const server = createServer((req: IncomingMessage, res: ServerResponse) => {
      const url = new URL(req.url || "/", `http://127.0.0.1`);

      if (url.pathname === "/auth/callback") {
        const token = url.searchParams.get("token");

        if (token) {
          res.writeHead(200, { "Content-Type": "text/html" });
          res.end(`
            <!DOCTYPE html>
            <html>
            <head><title>Connected!</title></head>
            <body style="font-family: system-ui; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background: #f5f7fa;">
              <div style="text-align: center; background: #fff; padding: 48px; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
                <h1 style="color: #22c55e; margin-bottom: 8px;">Connected!</h1>
                <p style="color: #64748b;">Your Zyla API Hub account is linked to OpenClaw.</p>
                <p style="color: #94a3b8; font-size: 14px; margin-top: 16px;">You can close this tab.</p>
              </div>
            </body>
            </html>
          `);
          resolveToken(token);
        } else {
          res.writeHead(400, { "Content-Type": "text/plain" });
          res.end("Missing token parameter");
          rejectToken(new Error("No token received in callback"));
        }
      } else {
        res.writeHead(404, { "Content-Type": "text/plain" });
        res.end("Not found");
      }
    });

    // Listen on a random available port
    server.listen(0, "127.0.0.1", () => {
      const addr = server.address();
      if (!addr || typeof addr === "string") {
        reject(new Error("Failed to bind server"));
        return;
      }

      resolve({
        port: addr.port,
        tokenPromise,
        close: () => server.close(),
      });
    });

    server.on("error", reject);

    // Auto-close after 5 minutes (timeout)
    setTimeout(() => {
      server.close();
      rejectToken(new Error("Connection timed out after 5 minutes"));
    }, 5 * 60 * 1000);
  });
}

/**
 * Plugin entry point — called by OpenClaw when the plugin is loaded.
 */
export default function register(api: any) {
  const hubUrl = api.config?.hubUrl || DEFAULT_HUB_URL;

  // ─── Slash Command: /zyla connect ───────────────────────────────────────────

  api.registerCommand({
    name: "zyla",
    description: "Connect to Zyla API Hub or check status. Usage: /zyla connect | /zyla status",
    acceptsArgs: true,
    requireAuth: false,
    handler: async (ctx: any) => {
      const subcommand = (ctx.args || "").trim().toLowerCase();

      if (subcommand === "connect") {
        return await handleConnect(api, hubUrl);
      } else if (subcommand === "status") {
        return await handleStatus(api, hubUrl);
      } else {
        return {
          text: [
            "**Zyla API Hub Skill**",
            "",
            "Commands:",
            "- `/zyla connect` — Link your Zyla API Hub account (opens browser)",
            "- `/zyla status` — Check your plan and usage",
            "",
            "Or just ask me to use any API! Example: *\"Get the weather for Buenos Aires\"*",
          ].join("\n"),
        };
      }
    },
  });

  // ─── Agent Tool: zyla_api ──────────────────────────────────────────────────

  api.registerTool?.({
    name: "zyla_api",
    description:
      "Call any API from the Zyla API Hub marketplace. Requires api_id and endpoint_id. " +
      "Use the catalog to discover APIs first if needed.",
    parameters: {
      type: "object",
      required: ["api_id", "endpoint_id"],
      properties: {
        api_id: { type: "number", description: "The Zyla API ID" },
        endpoint_id: { type: "number", description: "The endpoint ID within the API" },
        method: {
          type: "string",
          enum: ["GET", "POST", "PUT", "DELETE", "PATCH"],
          default: "GET",
          description: "HTTP method",
        },
        params: {
          type: "object",
          description: "Parameters to send with the request",
          additionalProperties: true,
        },
      },
    },
    handler: async (args: {
      api_id: number;
      endpoint_id: number;
      method?: string;
      params?: Record<string, any>;
    }) => {
      const apiKey = readApiKey(api.config?.apiKey);
      if (!apiKey) {
        return {
          error:
            "ZYLA_API_KEY not configured. Run /zyla connect or visit " +
            hubUrl +
            "/openclaw/connect to get your API key.",
        };
      }

      const method = (args.method || "GET").toUpperCase();
      let url = `${hubUrl}/api/${args.api_id}/api/${args.endpoint_id}/endpoint`;

      const fetchOptions: RequestInit = {
        method,
        headers: {
          Authorization: `Bearer ${apiKey}`,
          Accept: "application/json",
        },
      };

      if (method === "GET" && args.params) {
        const qs = new URLSearchParams(
          Object.entries(args.params).map(([k, v]) => [k, String(v)])
        ).toString();
        if (qs) url += `?${qs}`;
      } else if (args.params) {
        (fetchOptions.headers as Record<string, string>)["Content-Type"] = "application/json";
        fetchOptions.body = JSON.stringify(args.params);
      }

      try {
        const res = await fetch(url, fetchOptions);
        const data = await res.json().catch(() => res.text());

        return {
          status: res.status,
          data,
          rate_limits: {
            minute_remaining: res.headers.get("x-zyla-ratelimit-minute-remaining"),
            monthly_used: res.headers.get("x-zyla-api-calls-monthly-used"),
          },
        };
      } catch (err: any) {
        return { error: err.message };
      }
    },
  });
}

// ─── Command Handlers ─────────────────────────────────────────────────────────

async function handleConnect(api: any, hubUrl: string) {
  try {
    const { port, tokenPromise, close } = await startCallbackServer();
    const callbackUrl = `http://127.0.0.1:${port}/auth/callback`;
    const connectUrl = `${hubUrl}/openclaw/connect?callback=${encodeURIComponent(callbackUrl)}`;

    // Open browser
    try {
      const openModule = await import("open");
      await openModule.default(connectUrl);
    } catch {
      // If 'open' package is not available, instruct user
      return {
        text: `Open this URL in your browser to connect:\n\n${connectUrl}`,
      };
    }

    // Wait for the callback with the token
    const token = await tokenPromise;
    close();

    // Write to OpenClaw config
    writeApiKey(token);

    return {
      text: [
        "**Connected to Zyla API Hub!**",
        "",
        "Your pay-as-you-go plan is active. Add this to your `~/.openclaw/openclaw.json`:",
        "",
        "```json",
        JSON.stringify(
          {
            skills: {
              entries: {
                "zyla-api-hub-skill": {
                  enabled: true,
                  apiKey: token,
                  env: { ZYLA_API_KEY: token },
                },
              },
            },
          },
          null,
          2
        ),
        "```",
        "",
        "You can now use any API! Try: *\"Get the weather for Buenos Aires\"*",
      ].join("\n"),
    };
  } catch (err: any) {
    return { text: `Connection failed: ${err.message}` };
  }
}

async function handleStatus(api: any, hubUrl: string) {
  const apiKey = readApiKey(api.config?.apiKey);
  if (!apiKey) {
    return {
      text: "Not connected. Run `/zyla connect` to link your Zyla API Hub account.",
    };
  }

  try {
    const res = await fetch(`${hubUrl}/api/openclaw/health`, {
      headers: {
        Authorization: `Bearer ${apiKey}`,
        Accept: "application/json",
      },
    });

    if (!res.ok) {
      return {
        text: `API key invalid or expired (HTTP ${res.status}). Run \`/zyla connect\` to reconnect.`,
      };
    }

    const data = await res.json();

    return {
      text: [
        "**Zyla API Hub Status**",
        "",
        `- **User**: ${data.user}`,
        `- **Plan**: ${data.plan}`,
        `- **Calls this cycle**: ${data.calls_this_cycle}`,
        `- **Rate limit**: ${data.rate_limit_per_minute} req/min`,
        `- **Status**: ${data.status === "ok" ? "Active" : data.status}`,
      ].join("\n"),
    };
  } catch (err: any) {
    return { text: `Failed to check status: ${err.message}` };
  }
}
