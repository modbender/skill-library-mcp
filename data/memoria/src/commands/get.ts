import chalk from 'chalk';
import { resolveVault, getDocument } from '../lib/vault.js';

export async function getCommand(
  id: string,
  options: { vault?: string },
): Promise<void> {
  const config = await resolveVault(options.vault);

  try {
    const doc = await getDocument(config.path, id);
    console.log(chalk.bold(doc.title));
    console.log(chalk.dim(`Category: ${doc.category} | Created: ${doc.created}`));
    if (doc.tags.length > 0) {
      console.log(chalk.dim(`Tags: ${doc.tags.join(', ')}`));
    }
    console.log();
    console.log(doc.content);
  } catch {
    console.log(chalk.red(`Document not found: ${id}`));
    process.exit(1);
  }
}
