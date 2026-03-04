import fs from "node:fs/promises";
import path from "node:path";

const STORAGE_MODE = 0o600;

function envFlagEnabled(value: string | undefined): boolean {
  if (!value) return false;
  const normalized = value.trim().toLowerCase();
  return normalized === "1" || normalized === "true" || normalized === "yes" || normalized === "on";
}

function authFilePath(rootDir: string, siteId: string): string {
  return path.join(rootDir, "secrets", siteId, "auth.json");
}

export async function ensureSecretsDir(rootDir: string, siteId: string): Promise<string> {
  const dir = path.join(rootDir, "secrets", siteId);
  await fs.mkdir(dir, { recursive: true });
  return dir;
}

export async function saveStorageState(rootDir: string, siteId: string, storageState: unknown): Promise<string> {
  if (envFlagEnabled(process.env.WEBSITES_DISABLE_STORAGE_STATE_WRITE)) {
    throw new Error("STORAGE_STATE_WRITE_DISABLED");
  }
  await ensureSecretsDir(rootDir, siteId);
  const filePath = authFilePath(rootDir, siteId);
  await fs.writeFile(filePath, JSON.stringify(storageState, null, 2), "utf-8");
  await fs.chmod(filePath, STORAGE_MODE);
  return filePath;
}

export async function loadStorageStatePath(rootDir: string, siteId: string): Promise<string> {
  const filePath = authFilePath(rootDir, siteId);
  await fs.access(filePath);
  return filePath;
}
