import chalk from 'chalk';
import type { VaultConfig } from '../types.js';
import { createNotionClient } from './notion-client.js';
import { pushToNotion } from './notion-sync.js';

export async function autoSyncIfEnabled(
  config: VaultConfig,
  syncFlag?: boolean,
): Promise<void> {
  const shouldSync = syncFlag ?? config.autoSync ?? false;

  if (!shouldSync) return;
  if (!config.notion) return;

  try {
    const client = createNotionClient(config.notion.token);
    const report = await pushToNotion(client, config);

    if (report.pushed.length > 0) {
      console.log(chalk.dim(`Synced ${report.pushed.length} document(s) to Notion.`));
    }
    if (report.errors.length > 0) {
      console.log(chalk.yellow(`Sync warnings: ${report.errors.length} error(s)`));
      for (const e of report.errors) {
        console.log(chalk.dim(`  - ${e}`));
      }
    }
  } catch (err) {
    console.log(chalk.yellow(`Auto-sync failed: ${err instanceof Error ? err.message : String(err)}`));
  }
}
