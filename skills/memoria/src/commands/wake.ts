import chalk from 'chalk';
import { resolveVault, listDocuments } from '../lib/vault.js';
import { getSession, startSession, getRecentHandoffs } from '../lib/session.js';

export async function wakeCommand(
  options: { vault?: string },
): Promise<void> {
  const config = await resolveVault(options.vault);
  const session = await getSession(config.path);

  if (session.state === 'active') {
    console.log(chalk.yellow('Session already active.'));
    console.log(chalk.dim(`Started: ${session.startedAt}`));
    if (session.workingOn) {
      console.log(chalk.dim(`Working on: ${session.workingOn}`));
    }
    return;
  }

  await startSession(config.path);
  console.log(chalk.green(`Memoria vault "${config.name}" is awake.\n`));

  const handoffs = await getRecentHandoffs(config.path);
  if (handoffs.length > 0) {
    console.log(chalk.bold('Recent handoffs:'));
    for (const h of handoffs) {
      console.log(chalk.dim(`  [${h.created.slice(0, 10)}]`));
      const lines = h.summary.split('\n').filter((l) => l.trim());
      for (const line of lines.slice(0, 3)) {
        console.log(`    ${line}`);
      }
    }
    console.log();
  }

  const docs = await listDocuments(config.path);
  const recent = docs
    .sort((a, b) => b.updated.localeCompare(a.updated))
    .slice(0, 5);

  if (recent.length > 0) {
    console.log(chalk.bold('Recent memories:'));
    for (const doc of recent) {
      console.log(`  ${chalk.cyan(doc.category)}/${chalk.white(doc.title)}`);
    }
  }
}
