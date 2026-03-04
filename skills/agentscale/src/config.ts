import "dotenv/config";
import { readFileSync, writeFileSync, mkdirSync, chmodSync } from "node:fs";
import path from "node:path";
import os from "node:os";

export const API_URL = process.env.AGENTSCALE_API_URL ?? "https://api.agentscale.co";

const CONFIG_DIR = path.join(os.homedir(), ".agentscale");
const CONFIG_FILE = path.join(CONFIG_DIR, "config.json");

export function saveApiKey(apiKey: string): void {
  mkdirSync(CONFIG_DIR, { recursive: true });
  chmodSync(CONFIG_DIR, 0o700);
  writeFileSync(CONFIG_FILE, JSON.stringify({ apiKey }), { mode: 0o600 });
  chmodSync(CONFIG_FILE, 0o600);
}

export function loadApiKey(): string | null {
  try {
    const data = JSON.parse(readFileSync(CONFIG_FILE, "utf-8"));
    return data.apiKey ?? null;
  } catch {
    return null;
  }
}
