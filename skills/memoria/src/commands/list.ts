import chalk from 'chalk';
import { resolveVault, listDocuments } from '../lib/vault.js';

export async function listCommand(
  category: string | undefined,
  options: { tags?: string; vault?: string },
): Promise<void> {
  const config = await resolveVault(options.vault);
  let docs = await listDocuments(config.path, category);

  if (options.tags) {
    const filterTags = options.tags.split(',').map((t) => t.trim().toLowerCase());
    docs = docs.filter((doc) =>
      filterTags.some((ft) => doc.tags.map((t) => t.toLowerCase()).includes(ft)),
    );
  }

  if (docs.length === 0) {
    console.log(chalk.dim('No documents found.'));
    return;
  }

  console.log(chalk.bold(`${docs.length} document(s):\n`));
  for (const doc of docs) {
    const tags = doc.tags.length > 0 ? chalk.dim(` [${doc.tags.join(', ')}]`) : '';
    console.log(`  ${chalk.cyan(doc.category)}/${chalk.white(doc.title)}${tags}`);
  }
}
