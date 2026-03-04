import chalk from 'chalk';
import { resolveVault, listDocuments } from '../lib/vault.js';
import { getSession } from '../lib/session.js';

export async function statusCommand(
  options: { vault?: string },
): Promise<void> {
  const config = await resolveVault(options.vault);
  const session = await getSession(config.path);
  const docs = await listDocuments(config.path);

  console.log(chalk.bold(`Memoria: ${config.name}\n`));
  console.log(`  Path:       ${config.path}`);
  console.log(`  Documents:  ${docs.length}`);
  console.log(`  Categories: ${config.categories.length}`);
  console.log(`  Session:    ${session.state === 'active' ? chalk.green('active') : chalk.dim('idle')}`);

  if (session.state === 'active') {
    if (session.startedAt) {
      console.log(`  Started:    ${session.startedAt}`);
    }
    if (session.workingOn) {
      console.log(`  Working on: ${session.workingOn}`);
    }
    if (session.focus) {
      console.log(`  Focus:      ${session.focus}`);
    }
    if (session.lastCheckpoint) {
      console.log(`  Checkpoint: ${session.lastCheckpoint}`);
    }
  }

  if (docs.length > 0) {
    const byCat: Record<string, number> = {};
    for (const doc of docs) {
      byCat[doc.category] = (byCat[doc.category] || 0) + 1;
    }
    console.log(chalk.bold('\n  By category:'));
    for (const [cat, count] of Object.entries(byCat).sort((a, b) => b[1] - a[1])) {
      console.log(`    ${chalk.cyan(cat)}: ${count}`);
    }
  }

  if (config.notion) {
    console.log(chalk.bold('\n  Notion:'));
    console.log(`    Connected: ${chalk.green('yes')}`);
    console.log(`    Root page: ${config.notion.rootPageId}`);
  } else {
    console.log(chalk.dim('\n  Notion: not configured'));
  }
}
