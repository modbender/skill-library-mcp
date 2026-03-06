import chalk from 'chalk';
import { resolveVault, storeDocument } from '../lib/vault.js';
import { autoSyncIfEnabled } from '../lib/auto-sync.js';

export async function storeCommand(
  category: string,
  title: string,
  options: {
    content?: string;
    tags?: string;
    vault?: string;
    overwrite?: boolean;
    sync?: boolean;
    noSync?: boolean;
  },
): Promise<void> {
  const config = await resolveVault(options.vault);
  const tags = options.tags ? options.tags.split(',').map((t) => t.trim()) : [];

  const doc = await storeDocument(config.path, {
    category,
    title,
    content: options.content || '',
    frontmatter: tags.length > 0 ? { tags } : undefined,
    overwrite: options.overwrite,
  });

  console.log(chalk.green(`Stored: ${doc.path}`));
  console.log(chalk.dim(`Category: ${doc.category} | Title: ${doc.title}`));

  const syncFlag = options.noSync ? false : options.sync;
  await autoSyncIfEnabled(config, syncFlag);
}
