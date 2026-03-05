import { mkdir, readFile, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

export interface AppConfig {
  defaultZip: string;
  defaultStores: string[];
}

const DEFAULT_CONFIG: AppConfig = {
  defaultZip: "85540",
  defaultStores: ["Aldi", "Lidl", "REWE", "EDEKA", "ALDI SÜD", "ALDI NORD", "Kaufland"],
};

const CONFIG_DIR = path.join(os.homedir(), ".supermarket-deals");
const CONFIG_PATH = path.join(CONFIG_DIR, "config.json");

function normalizeConfig(raw: Partial<AppConfig> | undefined): AppConfig {
  const source = raw ?? {};
  return {
    defaultZip: typeof source.defaultZip === "string" && source.defaultZip.trim() ? source.defaultZip.trim() : DEFAULT_CONFIG.defaultZip,
    defaultStores: Array.isArray(source.defaultStores) && source.defaultStores.length > 0
      ? source.defaultStores.map((s) => String(s).trim()).filter(Boolean)
      : [...DEFAULT_CONFIG.defaultStores],
  };
}

export async function ensureConfigDir(): Promise<void> {
  await mkdir(CONFIG_DIR, { recursive: true });
}

export async function loadConfig(): Promise<AppConfig> {
  await ensureConfigDir();
  try {
    const data = await readFile(CONFIG_PATH, "utf8");
    const parsed = JSON.parse(data) as Partial<AppConfig>;
    return normalizeConfig(parsed);
  } catch {
    await saveConfig(DEFAULT_CONFIG);
    return { ...DEFAULT_CONFIG };
  }
}

export async function saveConfig(config: AppConfig): Promise<void> {
  await ensureConfigDir();
  await writeFile(CONFIG_PATH, `${JSON.stringify(config, null, 2)}\n`, "utf8");
}

export function getConfigPath(): string {
  return CONFIG_PATH;
}

export function parseCsvStores(input?: string): string[] | undefined {
  if (!input) {
    return undefined;
  }
  const values = input
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);
  return values.length > 0 ? values : undefined;
}

export function defaults(): AppConfig {
  return { ...DEFAULT_CONFIG };
}
