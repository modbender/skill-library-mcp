import { resolve } from 'node:path';
import chalk from 'chalk';
import { initVault } from '../lib/vault.js';
import { configExists } from '../lib/config.js';

export async function initCommand(
  targetPath: string,
  options: { name?: string },
): Promise<void> {
  const vaultPath = resolve(targetPath);
  const name = options.name || targetPath.split('/').pop() || 'memoria';

  if (await configExists(vaultPath)) {
    console.log(chalk.yellow(`Vault already exists at ${vaultPath}`));
    return;
  }

  const config = await initVault(vaultPath, name);
  console.log(chalk.green(`Initialized Memoria vault "${config.name}" at ${vaultPath}`));
  console.log(chalk.dim(`Categories: ${config.categories.join(', ')}`));
}
