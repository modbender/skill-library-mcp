import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";

import type { GatewayRequestHandlers } from "./types.js";
import {
  readConfigFileSnapshot,
  writeConfigFile,
} from "../../config/io.js";
import { applyMergePatch } from "../../config/merge-patch.js";
import { scheduleGatewaySigusr1Restart } from "../../infra/restart.js";

const MATON_BASE_URL = "https://ctrl.maton.ai";

// Supported Maton apps (partial list based on docs)
const SUPPORTED_APPS = [
  "airtable",
  "apollo",
  "calendly",
  "chargebee",
  "gmail",
  "google-ads",
  "google-analytics-admin",
  "google-analytics-data",
  "google-calendar",
  "google-docs",
  "google-drive",
  "google-search-console",
  "google-sheets",
  "google-slides",
  "hubspot",
  "jira",
  "notion",
  "outlook",
  "slack",
  "youtube",
] as const;

type MatonConnection = {
  connection_id: string;
  status: "ACTIVE" | "PENDING" | "FAILED";
  creation_time: string;
  last_updated_time: string;
  url: string | null;
  app: string;
  metadata: Record<string, unknown>;
};

type MatonConnectionsResponse = {
  connections: MatonConnection[];
};

type MatonCreateResponse = {
  connection_Id: string;
  url?: string;
};

type MatonErrorResponse = {
  error?: {
    message?: string;
    type?: string;
    code?: number;
  };
};

/**
 * Read the Maton API key from the config file
 */
async function getMatonApiKey(): Promise<string | null> {
  try {
    const snapshot = await readConfigFileSnapshot();
    if (!snapshot.exists || !snapshot.config) return null;
    
    const env = (snapshot.config as { env?: Record<string, string> })?.env;
    return env?.MATON_API_KEY ?? null;
  } catch {
    return null;
  }
}

/**
 * Save the Maton API key to the config file
 */
async function setMatonApiKey(apiKey: string | null): Promise<boolean> {
  try {
    const snapshot = await readConfigFileSnapshot();
    const existingConfig = snapshot.config ?? {};
    
    // Apply merge patch to set env.MATON_API_KEY
    const patch = { env: { MATON_API_KEY: apiKey } };
    const newConfig = applyMergePatch(existingConfig as Record<string, unknown>, patch);
    
    // Write the config back
    await writeConfigFile(newConfig as Parameters<typeof writeConfigFile>[0]);
    
    // Schedule restart to pick up the new config
    scheduleGatewaySigusr1Restart({ delayMs: 2000, reason: "Maton API key update" });
    
    return true;
  } catch {
    return false;
  }
}

async function matonRequest<T>(
  endpoint: string,
  apiKey: string,
  options: RequestInit = {},
): Promise<{ data?: T; error?: string }> {
  try {
    const response = await fetch(`${MATON_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    const text = await response.text();
    let data: T | MatonErrorResponse;

    try {
      data = JSON.parse(text) as T | MatonErrorResponse;
    } catch {
      return { error: `Invalid JSON response: ${text.slice(0, 200)}` };
    }

    if (!response.ok) {
      const errorData = data as MatonErrorResponse;
      return {
        error: errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    return { data: data as T };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { error: message };
  }
}

async function testApiKey(apiKey: string): Promise<{ success: boolean; connectionCount?: number; error?: string }> {
  const result = await matonRequest<MatonConnectionsResponse>("/connections", apiKey);

  if (result.error) {
    return { success: false, error: result.error };
  }

  const connectionCount = result.data?.connections?.length ?? 0;
  return { success: true, connectionCount };
}

function formatAppName(app: string): string {
  return app
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export const matonHandlers: GatewayRequestHandlers = {
  "maton.status": async ({ respond }) => {
    try {
      const apiKey = await getMatonApiKey();

      if (!apiKey) {
        respond(true, {
          configured: false,
          connectionCount: 0,
          error: null,
        });
        return;
      }

      const testResult = await testApiKey(apiKey);

      respond(true, {
        configured: true,
        connectionCount: testResult.connectionCount ?? 0,
        testError: testResult.error ?? null,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { configured: false, error: message });
    }
  },

  "maton.save": async ({ respond, params }) => {
    try {
      const apiKey = typeof params?.apiKey === "string" ? params.apiKey.trim() : "";

      if (!apiKey) {
        respond(true, { success: false, error: "API key is required" });
        return;
      }

      // Test the API key first
      const testResult = await testApiKey(apiKey);
      if (!testResult.success) {
        respond(true, { success: false, error: `Invalid API key: ${testResult.error}` });
        return;
      }

      // Save the API key
      const saved = await setMatonApiKey(apiKey);
      if (!saved) {
        respond(true, { success: false, error: "Failed to save API key" });
        return;
      }

      respond(true, {
        success: true,
        connectionCount: testResult.connectionCount,
        message: `Maton configured with ${testResult.connectionCount} connections`,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "maton.test": async ({ respond }) => {
    try {
      const apiKey = await getMatonApiKey();

      if (!apiKey) {
        respond(true, { success: false, error: "Not configured" });
        return;
      }

      const testResult = await testApiKey(apiKey);
      respond(true, testResult);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "maton.disconnect": async ({ respond }) => {
    try {
      const saved = await setMatonApiKey(null);
      if (!saved) {
        respond(true, { success: false, error: "Failed to remove API key" });
        return;
      }

      respond(true, { success: true, message: "Maton disconnected" });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "maton.connections": async ({ respond, params }) => {
    try {
      const apiKey = await getMatonApiKey();

      if (!apiKey) {
        respond(true, { success: false, error: "Not configured", connections: [] });
        return;
      }

      // Build query string
      const queryParams = new URLSearchParams();
      if (params?.app && typeof params.app === "string") {
        queryParams.set("app", params.app);
      }
      if (params?.status && typeof params.status === "string") {
        queryParams.set("status", params.status);
      }

      const queryString = queryParams.toString();
      const endpoint = queryString ? `/connections?${queryString}` : "/connections";

      const result = await matonRequest<MatonConnectionsResponse>(endpoint, apiKey);

      if (result.error) {
        respond(true, { success: false, error: result.error, connections: [] });
        return;
      }

      respond(true, {
        success: true,
        connections: result.data?.connections ?? [],
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message, connections: [] });
    }
  },

  "maton.connect": async ({ respond, params }) => {
    try {
      const apiKey = await getMatonApiKey();

      if (!apiKey) {
        respond(true, { success: false, error: "Not configured" });
        return;
      }

      const app = typeof params?.app === "string" ? params.app : "";
      if (!app) {
        respond(true, { success: false, error: "App name is required" });
        return;
      }

      const result = await matonRequest<MatonCreateResponse>("/connections", apiKey, {
        method: "POST",
        body: JSON.stringify({ app }),
      });

      if (result.error) {
        respond(true, { success: false, error: result.error });
        return;
      }

      respond(true, {
        success: true,
        connectionId: result.data?.connection_Id,
        oauthUrl: result.data?.url,
        message: result.data?.url
          ? "Complete the OAuth flow at the provided URL"
          : "Connection created",
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "maton.delete": async ({ respond, params }) => {
    try {
      const apiKey = await getMatonApiKey();

      if (!apiKey) {
        respond(true, { success: false, error: "Not configured" });
        return;
      }

      const connectionId = typeof params?.connectionId === "string" ? params.connectionId : "";
      if (!connectionId) {
        respond(true, { success: false, error: "Connection ID is required" });
        return;
      }

      const result = await matonRequest<Record<string, unknown>>(
        `/connections/${encodeURIComponent(connectionId)}`,
        apiKey,
        { method: "DELETE" },
      );

      if (result.error) {
        respond(true, { success: false, error: result.error });
        return;
      }

      respond(true, { success: true, message: "Connection deleted" });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },

  "maton.apps": async ({ respond }) => {
    try {
      // Return the list of supported apps
      respond(true, {
        success: true,
        apps: SUPPORTED_APPS.map((app) => ({
          id: app,
          name: formatAppName(app),
        })),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message, apps: [] });
    }
  },

  "maton.refresh": async ({ respond, params }) => {
    try {
      const apiKey = await getMatonApiKey();

      if (!apiKey) {
        respond(true, { success: false, error: "Not configured" });
        return;
      }

      const connectionId = typeof params?.connectionId === "string" ? params.connectionId : "";
      if (!connectionId) {
        respond(true, { success: false, error: "Connection ID is required" });
        return;
      }

      // Fetch the specific connection to get its current status
      const result = await matonRequest<{ connection: MatonConnection }>(
        `/connections/${encodeURIComponent(connectionId)}`,
        apiKey,
      );

      if (result.error) {
        respond(true, { success: false, error: result.error });
        return;
      }

      respond(true, {
        success: true,
        connection: result.data?.connection,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { success: false, error: message });
    }
  },
};
