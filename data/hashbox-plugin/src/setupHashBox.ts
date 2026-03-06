import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const CONFIG_FILENAME = "hashbox_config.json";
const EXCHANGE_TOKEN_URL =
  "https://exchangetoken-vcphors6kq-uc.a.run.app/exchangeToken";

export interface HashBoxConfig {
  token: string;
  customToken?: string;
  userId?: string;
}

/**
 * Exchanges an HB- token with the backend to obtain a Firebase Custom Auth Token
 * and the user's UID. This enables the plugin to authenticate as the user
 * and listen to the agent_commands Firestore collection.
 */
async function exchangeTokenWithBackend(
  token: string,
): Promise<{ customToken: string; userId: string }> {
  const response = await fetch(EXCHANGE_TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as Record<
      string,
      string
    >;
    throw new Error(
      `Token exchange failed (${response.status}): ${body.error || "Unknown error"}`,
    );
  }

  const data = (await response.json()) as {
    customToken: string;
    userId: string;
  };
  return { customToken: data.customToken, userId: data.userId };
}

/**
 * Configures the HashBox plugin with an HB- token.
 *
 * 1. Validates the token format (must start with HB-)
 * 2. Exchanges the token with the backend for a Firebase Custom Auth Token + userId
 * 3. Saves all three values to hashbox_config.json
 */
export async function configureHashBox(token: string): Promise<string> {
  if (!token || !token.startsWith("HB-")) {
    throw new Error(
      "Invalid token: must be a non-empty string with HB- prefix",
    );
  }

  // Exchange token with backend for Custom Auth Token + userId
  const { customToken, userId } = await exchangeTokenWithBackend(token);

  const config: HashBoxConfig = { token, customToken, userId };
  const configPath = join(process.cwd(), CONFIG_FILENAME);
  await writeFile(configPath, JSON.stringify(config, null, 2), "utf-8");

  return `HashBox configured successfully. Connected as user ${userId}. Config saved to ${CONFIG_FILENAME}`;
}

/**
 * Loads the saved config from disk. Returns null if not found.
 */
export async function loadConfig(): Promise<HashBoxConfig | null> {
  const configPath = join(process.cwd(), CONFIG_FILENAME);
  try {
    const raw = await readFile(configPath, "utf-8");
    return JSON.parse(raw) as HashBoxConfig;
  } catch {
    return null;
  }
}

/**
 * Refreshes the Custom Auth Token by re-exchanging the HB- token.
 * Updates the config file with the new token.
 */
export async function refreshCustomToken(
  config: HashBoxConfig,
): Promise<HashBoxConfig> {
  const { customToken, userId } = await exchangeTokenWithBackend(config.token);
  const updated: HashBoxConfig = { ...config, customToken, userId };

  const configPath = join(process.cwd(), CONFIG_FILENAME);
  await writeFile(configPath, JSON.stringify(updated, null, 2), "utf-8");

  return updated;
}
