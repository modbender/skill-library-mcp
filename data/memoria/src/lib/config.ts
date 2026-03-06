import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import type { VaultConfig } from '../types.js';

const CONFIG_FILE = '.memoria.json';

export function configPath(vaultPath: string): string {
  return join(vaultPath, CONFIG_FILE);
}

export async function readConfig(vaultPath: string): Promise<VaultConfig> {
  const raw = await readFile(configPath(vaultPath), 'utf-8');
  return JSON.parse(raw) as VaultConfig;
}

export async function writeConfig(config: VaultConfig): Promise<void> {
  const filePath = configPath(config.path);
  await writeFile(filePath, JSON.stringify(config, null, 2) + '\n', 'utf-8');
}

export async function configExists(vaultPath: string): Promise<boolean> {
  try {
    await readFile(configPath(vaultPath));
    return true;
  } catch {
    return false;
  }
}
