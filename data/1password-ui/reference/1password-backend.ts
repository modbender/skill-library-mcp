/**
 * 1Password UI - Gateway RPC Handlers
 * 
 * Provides backend methods for the 1Password UI tab.
 * Supports both CLI (op) and Connect API modes.
 * 
 * Place at: src/gateway/server-methods/1password.ts
 */

import { exec, spawn } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import { promisify } from "node:util";

import type { GatewayRequestHandlers } from "./types.js";

const execAsync = promisify(exec);

// Config paths
const CONFIG_DIR = path.join(os.homedir(), "clawd", "config");
const MAPPINGS_FILE = path.join(CONFIG_DIR, "1password-mappings.json");

// Connect API config (for Docker mode)
const OP_CONNECT_HOST = process.env.OP_CONNECT_HOST;
const OP_CONNECT_TOKEN = process.env.OP_CONNECT_TOKEN;

// Session state (in-memory, per gateway process)
let sessionState: {
  signedIn: boolean;
  account?: string;
  email?: string;
  lastCheck?: number;
} = { signedIn: false };

// ============================================
// Helpers
// ============================================

function isConnectMode(): boolean {
  return !!(OP_CONNECT_HOST && OP_CONNECT_TOKEN);
}

function which(cmd: string): string | null {
  const paths = (process.env.PATH || "").split(path.delimiter);
  for (const dir of paths) {
    const fullPath = path.join(dir, cmd);
    try {
      fs.accessSync(fullPath, fs.constants.X_OK);
      return fullPath;
    } catch {
      // continue
    }
  }
  return null;
}

async function opCommand(args: string[], timeout = 30000): Promise<{ stdout: string; stderr: string }> {
  const opPath = which("op");
  if (!opPath) {
    throw new Error("1Password CLI (op) not found in PATH");
  }

  return execAsync(`"${opPath}" ${args.join(" ")}`, { timeout });
}

async function connectApiCall(
  method: string,
  endpoint: string,
  body?: unknown
): Promise<unknown> {
  if (!OP_CONNECT_HOST || !OP_CONNECT_TOKEN) {
    throw new Error("1Password Connect not configured");
  }

  const url = `${OP_CONNECT_HOST}/v1${endpoint}`;
  const response = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${OP_CONNECT_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Connect API error ${response.status}: ${text}`);
  }

  return response.json();
}

function readMappings(): Record<string, {
  item: string;
  vault: string;
  fields: Record<string, string>;
}> {
  try {
    if (fs.existsSync(MAPPINGS_FILE)) {
      return JSON.parse(fs.readFileSync(MAPPINGS_FILE, "utf-8"));
    }
  } catch {
    // ignore
  }
  return {};
}

function writeMappings(mappings: Record<string, unknown>): void {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
  fs.writeFileSync(MAPPINGS_FILE, JSON.stringify(mappings, null, 2), { mode: 0o600 });
}

// ============================================
// CLI Mode Functions
// ============================================

async function checkCliStatus(): Promise<{
  installed: boolean;
  signedIn: boolean;
  account?: string;
  email?: string;
}> {
  const opPath = which("op");
  if (!opPath) {
    return { installed: false, signedIn: false };
  }

  try {
    const { stdout } = await opCommand(["whoami", "--format=json"], 5000);
    const info = JSON.parse(stdout);
    sessionState = {
      signedIn: true,
      account: info.account_uuid || info.url,
      email: info.email,
      lastCheck: Date.now(),
    };
    return {
      installed: true,
      signedIn: true,
      account: info.url || info.account_uuid,
      email: info.email,
    };
  } catch {
    sessionState = { signedIn: false };
    return { installed: true, signedIn: false };
  }
}

async function cliSignin(account?: string): Promise<{ success: boolean; error?: string }> {
  try {
    // Attempt non-interactive signin (relies on 1Password app integration)
    const args = ["signin"];
    if (account) args.push("--account", account);
    args.push("--force"); // Don't output eval script, just authenticate

    await opCommand(args, 60000);
    
    // Verify it worked
    const status = await checkCliStatus();
    if (status.signedIn) {
      return { success: true };
    }
    return { success: false, error: "Sign-in completed but verification failed" };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    
    // Check for specific error patterns
    if (msg.includes("authorization denied") || msg.includes("user interaction")) {
      return {
        success: false,
        error: "Authorization required. Please authorize in the 1Password app, or run 'op signin' in a terminal.",
      };
    }
    
    return { success: false, error: msg };
  }
}

async function cliSignout(): Promise<{ success: boolean }> {
  try {
    await opCommand(["signout"], 5000);
  } catch {
    // Ignore errors, just clear state
  }
  sessionState = { signedIn: false };
  return { success: true };
}

async function cliListVaults(): Promise<Array<{ id: string; name: string }>> {
  const { stdout } = await opCommand(["vault", "list", "--format=json"]);
  return JSON.parse(stdout);
}

async function cliListItems(vault?: string, category?: string): Promise<Array<{
  id: string;
  title: string;
  category: string;
  vault: { id: string; name: string };
}>> {
  const args = ["item", "list", "--format=json"];
  if (vault) args.push("--vault", vault);
  if (category) args.push("--categories", category);
  
  const { stdout } = await opCommand(args);
  return JSON.parse(stdout);
}

async function cliGetItem(itemRef: string, vault?: string): Promise<{
  id: string;
  title: string;
  category: string;
  fields: Array<{ id: string; label: string; type: string; value?: string }>;
}> {
  const args = ["item", "get", itemRef, "--format=json"];
  if (vault) args.push("--vault", vault);
  
  const { stdout } = await opCommand(args);
  const item = JSON.parse(stdout);
  
  // Strip values from fields for safety (only return structure)
  const safeFields = (item.fields || []).map((f: { id: string; label: string; type: string }) => ({
    id: f.id,
    label: f.label,
    type: f.type,
    // value intentionally omitted
  }));
  
  return {
    id: item.id,
    title: item.title,
    category: item.category,
    fields: safeFields,
  };
}

async function cliReadSecret(itemRef: string, field: string, vault?: string): Promise<string> {
  const args = ["read", `op://${vault || "Private"}/${itemRef}/${field}`];
  const { stdout } = await opCommand(args, 10000);
  return stdout.trim();
}

// ============================================
// Connect Mode Functions
// ============================================

async function connectListVaults(): Promise<Array<{ id: string; name: string }>> {
  const result = await connectApiCall("GET", "/vaults") as Array<{ id: string; name: string }>;
  return result;
}

async function connectListItems(vaultId: string): Promise<Array<{
  id: string;
  title: string;
  category: string;
  vault: { id: string };
}>> {
  const result = await connectApiCall("GET", `/vaults/${vaultId}/items`) as Array<{
    id: string;
    title: string;
    category: string;
    vault: { id: string };
  }>;
  return result;
}

async function connectGetItem(vaultId: string, itemId: string): Promise<{
  id: string;
  title: string;
  category: string;
  fields: Array<{ id: string; label: string; type: string }>;
}> {
  const result = await connectApiCall("GET", `/vaults/${vaultId}/items/${itemId}`) as {
    id: string;
    title: string;
    category: string;
    fields: Array<{ id: string; label: string; type: string; value?: string }>;
  };
  
  // Strip values
  const safeFields = (result.fields || []).map((f) => ({
    id: f.id,
    label: f.label,
    type: f.type,
  }));
  
  return { ...result, fields: safeFields };
}

async function connectReadSecret(vaultId: string, itemId: string, field: string): Promise<string> {
  const result = await connectApiCall("GET", `/vaults/${vaultId}/items/${itemId}`) as {
    fields: Array<{ id: string; label: string; value?: string }>;
  };
  
  const f = result.fields.find((f) => f.id === field || f.label === field);
  if (!f || !f.value) {
    throw new Error(`Field "${field}" not found or empty`);
  }
  return f.value;
}

// ============================================
// RPC Handlers
// ============================================

export const onePasswordHandlers: GatewayRequestHandlers = {
  "1password.status": async ({ respond }) => {
    try {
      if (isConnectMode()) {
        // Connect mode - just check if we can reach the API
        try {
          await connectListVaults();
          respond(true, {
            mode: "connect",
            connected: true,
            host: OP_CONNECT_HOST,
          }, undefined);
        } catch (e) {
          respond(true, {
            mode: "connect",
            connected: false,
            error: e instanceof Error ? e.message : String(e),
          }, undefined);
        }
        return;
      }

      // CLI mode
      const status = await checkCliStatus();
      respond(true, {
        mode: "cli",
        ...status,
      }, undefined);
    } catch (e) {
      respond(true, {
        mode: "cli",
        installed: false,
        signedIn: false,
        error: e instanceof Error ? e.message : String(e),
      }, undefined);
    }
  },

  "1password.signin": async ({ params, respond }) => {
    try {
      if (isConnectMode()) {
        respond(true, { success: true, message: "Connect mode - no sign-in required" }, undefined);
        return;
      }

      const { account } = params as { account?: string };
      const result = await cliSignin(account);
      respond(true, result, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "1password.signout": async ({ respond }) => {
    try {
      if (isConnectMode()) {
        respond(true, { success: true, message: "Connect mode - no sign-out needed" }, undefined);
        return;
      }

      const result = await cliSignout();
      respond(true, result, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "1password.vaults": async ({ respond }) => {
    try {
      let vaults: Array<{ id: string; name: string }>;
      
      if (isConnectMode()) {
        vaults = await connectListVaults();
      } else {
        vaults = await cliListVaults();
      }
      
      respond(true, { vaults }, undefined);
    } catch (e) {
      respond(true, { vaults: [], error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "1password.items": async ({ params, respond }) => {
    try {
      const { vault, category } = params as { vault?: string; category?: string };
      
      let items: Array<{ id: string; title: string; category: string; vault: unknown }>;
      
      if (isConnectMode()) {
        if (!vault) {
          respond(true, { items: [], error: "vault required for Connect mode" }, undefined);
          return;
        }
        items = await connectListItems(vault);
      } else {
        items = await cliListItems(vault, category);
      }
      
      respond(true, { items }, undefined);
    } catch (e) {
      respond(true, { items: [], error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "1password.getItem": async ({ params, respond }) => {
    try {
      const { item, vault } = params as { item: string; vault?: string };
      
      let result: { id: string; title: string; category: string; fields: unknown[] };
      
      if (isConnectMode()) {
        if (!vault) {
          respond(true, { error: "vault required for Connect mode" }, undefined);
          return;
        }
        result = await connectGetItem(vault, item);
      } else {
        result = await cliGetItem(item, vault);
      }
      
      respond(true, result, undefined);
    } catch (e) {
      respond(true, { error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "1password.readSecret": async ({ params, respond }) => {
    // This is backend-only - used by skills, not exposed to UI directly
    try {
      const { item, field, vault } = params as { item: string; field: string; vault?: string };
      
      let value: string;
      
      if (isConnectMode()) {
        if (!vault) {
          respond(true, { error: "vault required for Connect mode" }, undefined);
          return;
        }
        value = await connectReadSecret(vault, item, field);
      } else {
        value = await cliReadSecret(item, field, vault);
      }
      
      respond(true, { value }, undefined);
    } catch (e) {
      respond(true, { error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "1password.mappings.list": async ({ respond }) => {
    try {
      const mappings = readMappings();
      respond(true, { mappings }, undefined);
    } catch (e) {
      respond(true, { mappings: {}, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "1password.mappings.set": async ({ params, respond }) => {
    try {
      const { skillId, item, vault, fields } = params as {
        skillId: string;
        item: string;
        vault: string;
        fields: Record<string, string>;
      };
      
      const mappings = readMappings();
      mappings[skillId] = { item, vault, fields };
      writeMappings(mappings);
      
      respond(true, { success: true }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "1password.mappings.delete": async ({ params, respond }) => {
    try {
      const { skillId } = params as { skillId: string };
      
      const mappings = readMappings();
      delete mappings[skillId];
      writeMappings(mappings);
      
      respond(true, { success: true }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "1password.mappings.test": async ({ params, respond }) => {
    try {
      const { skillId } = params as { skillId: string };
      
      const mappings = readMappings();
      const mapping = mappings[skillId];
      
      if (!mapping) {
        respond(true, { success: false, error: "No mapping found for skill" }, undefined);
        return;
      }
      
      // Try to read one field to verify it works
      const firstField = Object.values(mapping.fields)[0];
      if (!firstField) {
        respond(true, { success: false, error: "No fields in mapping" }, undefined);
        return;
      }
      
      if (isConnectMode()) {
        await connectReadSecret(mapping.vault, mapping.item, firstField);
      } else {
        await cliReadSecret(mapping.item, firstField, mapping.vault);
      }
      
      respond(true, { success: true, message: "Mapping verified successfully" }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },
};
