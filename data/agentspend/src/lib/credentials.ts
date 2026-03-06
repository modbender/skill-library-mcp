import { mkdir, readFile, writeFile, chmod, unlink } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import type { Credentials } from "../types.js";

const CREDENTIALS_DIR = path.join(os.homedir(), ".agentspend");
const CREDENTIALS_FILE = path.join(CREDENTIALS_DIR, "credentials.json");
const PENDING_CONFIGURE_FILE = path.join(CREDENTIALS_DIR, "pending-configure.json");

export async function readCredentials(): Promise<Credentials | null> {
  try {
    const raw = await readFile(CREDENTIALS_FILE, "utf-8");
    const parsed = JSON.parse(raw) as Credentials;

    if (!parsed.api_key || !parsed.api_key.startsWith("sk_agent_")) {
      return null;
    }

    return parsed;
  } catch {
    return null;
  }
}

export async function saveCredentials(apiKey: string): Promise<void> {
  const payload: Credentials = {
    api_key: apiKey,
    created_at: new Date().toISOString(),
  };

  await mkdir(CREDENTIALS_DIR, { recursive: true, mode: 0o700 });
  await writeFile(CREDENTIALS_FILE, `${JSON.stringify(payload, null, 2)}\n`, "utf-8");

  try {
    await chmod(CREDENTIALS_FILE, 0o600);
  } catch {
    // no-op when chmod is not available on the host filesystem
  }
}

export async function requireApiKey(): Promise<string> {
  const credentials = await readCredentials();

  if (!credentials) {
    throw new Error(`No API key found at ${CREDENTIALS_FILE}. Run \`agentspend configure\` first.`);
  }

  return credentials.api_key;
}

export async function readPendingConfigureToken(): Promise<string | null> {
  try {
    const raw = await readFile(PENDING_CONFIGURE_FILE, "utf-8");
    const parsed = JSON.parse(raw) as { token?: string };

    if (!parsed.token || !parsed.token.startsWith("cfs_")) {
      return null;
    }

    return parsed.token;
  } catch {
    return null;
  }
}

export async function savePendingConfigureToken(token: string): Promise<void> {
  await mkdir(CREDENTIALS_DIR, { recursive: true, mode: 0o700 });
  await writeFile(
    PENDING_CONFIGURE_FILE,
    `${JSON.stringify({ token, created_at: new Date().toISOString() }, null, 2)}\n`,
    "utf-8",
  );
}

export async function clearPendingConfigureToken(): Promise<void> {
  try {
    await unlink(PENDING_CONFIGURE_FILE);
  } catch {
    // no-op
  }
}
