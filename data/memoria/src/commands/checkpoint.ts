import chalk from 'chalk';
import { resolveVault } from '../lib/vault.js';
import { getSession, updateCheckpoint } from '../lib/session.js';

export async function checkpointCommand(
  options: { workingOn?: string; focus?: string; vault?: string },
): Promise<void> {
  const config = await resolveVault(options.vault);
  const session = await getSession(config.path);

  if (session.state !== 'active') {
    console.log(chalk.yellow('No active session. Run "memoria wake" first.'));
    return;
  }

  const updated = await updateCheckpoint(
    config.path,
    options.workingOn,
    options.focus,
  );

  console.log(chalk.green('Checkpoint saved.'));
  if (updated.workingOn) {
    console.log(chalk.dim(`Working on: ${updated.workingOn}`));
  }
  if (updated.focus) {
    console.log(chalk.dim(`Focus: ${updated.focus}`));
  }
  console.log(chalk.dim(`Time: ${updated.lastCheckpoint}`));
}
