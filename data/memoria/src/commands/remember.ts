import chalk from 'chalk';
import { resolveVault, storeDocument } from '../lib/vault.js';
import { autoSyncIfEnabled } from '../lib/auto-sync.js';
import { MEMORY_TYPES, TYPE_TO_CATEGORY } from '../types.js';
import type { MemoryType } from '../types.js';

export async function rememberCommand(
  type: string,
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
  if (!MEMORY_TYPES.includes(type as MemoryType)) {
    console.log(chalk.red(`Invalid memory type: "${type}"`));
    console.log(chalk.dim(`Valid types: ${MEMORY_TYPES.join(', ')}`));
    process.exit(1);
  }

  const memType = type as MemoryType;
  const category = TYPE_TO_CATEGORY[memType];
  const config = await resolveVault(options.vault);
  const tags = options.tags ? options.tags.split(',').map((t) => t.trim()) : [];

  const doc = await storeDocument(config.path, {
    category,
    title,
    content: options.content || '',
    frontmatter: { type: memType, ...(tags.length > 0 ? { tags } : {}) },
    overwrite: options.overwrite,
  });

  console.log(chalk.green(`Remembered ${memType}: ${doc.title}`));
  console.log(chalk.dim(`Stored in: ${doc.path}`));

  const syncFlag = options.noSync ? false : options.sync;
  await autoSyncIfEnabled(config, syncFlag);
}
