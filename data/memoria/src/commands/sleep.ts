import chalk from 'chalk';
import { resolveVault } from '../lib/vault.js';
import { getSession, endSession } from '../lib/session.js';

export async function sleepCommand(
  summary: string,
  options: { next?: string; vault?: string },
): Promise<void> {
  const config = await resolveVault(options.vault);
  const session = await getSession(config.path);

  if (session.state !== 'active') {
    console.log(chalk.yellow('No active session. Run "memoria wake" first.'));
    return;
  }

  const handoff = await endSession(config.path, summary, options.next);

  console.log(chalk.green('Session ended. Handoff saved.'));
  console.log(chalk.dim(`Summary: ${summary}`));
  if (options.next) {
    console.log(chalk.dim(`Next steps: ${options.next}`));
  }
  console.log(chalk.dim(`Handoff: sessions/handoffs/${handoff.created.slice(0, 10)}.md`));
}
