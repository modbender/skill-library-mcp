import chalk from 'chalk';
import { resolveVault } from '../lib/vault.js';
import { createNotionClient } from '../lib/notion-client.js';
import { pushToNotion, pullFromNotion } from '../lib/notion-sync.js';
import type { SyncReport } from '../lib/notion-sync.js';

export async function syncCommand(
  options: {
    push?: boolean;
    pull?: boolean;
    preferNotion?: boolean;
    dryRun?: boolean;
    vault?: string;
  },
): Promise<void> {
  const config = await resolveVault(options.vault);

  if (!config.notion) {
    console.log(chalk.red('Notion not configured. Run "memoria setup-notion" first.'));
    process.exit(1);
  }

  const client = createNotionClient(config.notion.token);
  const doPush = options.push || (!options.push && !options.pull);
  const doPull = options.pull || (!options.push && !options.pull);

  if (options.dryRun) {
    console.log(chalk.dim('Dry run mode -- no changes will be made.\n'));
  }

  if (doPush) {
    console.log(chalk.bold('Pushing to Notion...'));
    const report = await pushToNotion(client, config, { dryRun: options.dryRun });
    printReport('Push', report);
  }

  if (doPull) {
    console.log(chalk.bold('Pulling from Notion...'));
    const report = await pullFromNotion(client, config, {
      preferNotion: options.preferNotion,
      dryRun: options.dryRun,
    });
    printReport('Pull', report);
  }
}

function printReport(direction: string, report: SyncReport): void {
  if (report.pushed.length > 0) {
    console.log(chalk.green(`  ${direction}: ${report.pushed.length} pushed`));
  }
  if (report.pulled.length > 0) {
    console.log(chalk.green(`  ${direction}: ${report.pulled.length} pulled`));
  }
  if (report.conflicts.length > 0) {
    console.log(chalk.yellow(`  ${direction}: ${report.conflicts.length} conflict(s) (local preferred)`));
    for (const c of report.conflicts) {
      console.log(chalk.dim(`    - ${c}`));
    }
  }
  if (report.errors.length > 0) {
    console.log(chalk.red(`  ${direction}: ${report.errors.length} error(s)`));
    for (const e of report.errors) {
      console.log(chalk.dim(`    - ${e}`));
    }
  }
  if (
    report.pushed.length === 0 &&
    report.pulled.length === 0 &&
    report.conflicts.length === 0 &&
    report.errors.length === 0
  ) {
    console.log(chalk.dim(`  ${direction}: everything up to date`));
  }
  console.log();
}
