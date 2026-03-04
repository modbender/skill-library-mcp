import chalk from 'chalk';
import { resolveVault } from '../lib/vault.js';
import { writeConfig } from '../lib/config.js';
import { createNotionClient } from '../lib/notion-client.js';

export async function setupNotionCommand(
  options: { token: string; page: string; vault?: string },
): Promise<void> {
  if (!options.token || !options.page) {
    console.log(chalk.red('Both --token and --page are required.'));
    console.log(chalk.dim('Usage: memoria setup-notion --token <token> --page <root-page-id>'));
    process.exit(1);
  }

  const config = await resolveVault(options.vault);

  const client = createNotionClient(options.token);
  try {
    await client.pages.retrieve({ page_id: options.page });
  } catch (err) {
    console.log(chalk.red('Failed to access Notion page. Check your token and page ID.'));
    console.log(chalk.dim(err instanceof Error ? err.message : String(err)));
    process.exit(1);
  }

  config.notion = {
    token: options.token,
    rootPageId: options.page,
  };
  config.autoSync = true;

  await writeConfig(config);
  console.log(chalk.green('Notion integration configured.'));
  console.log(chalk.dim(`Root page: ${options.page}`));
  console.log(chalk.dim('Auto-sync enabled. Memories will push to Notion automatically.'));
  console.log(chalk.dim('Disable with: memoria config --no-auto-sync'));
}
