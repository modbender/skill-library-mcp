import chalk from 'chalk';
import { resolveVault, listDocuments } from '../lib/vault.js';
import { searchDocuments } from '../lib/search.js';

export async function searchCommand(
  query: string,
  options: { category?: string; limit?: string; vault?: string },
): Promise<void> {
  const config = await resolveVault(options.vault);
  const docs = await listDocuments(config.path);
  const limit = options.limit ? parseInt(options.limit, 10) : 10;

  const results = searchDocuments(docs, query, {
    limit,
    category: options.category,
  });

  if (results.length === 0) {
    console.log(chalk.dim(`No results for "${query}"`));
    return;
  }

  console.log(chalk.bold(`${results.length} result(s) for "${query}":\n`));
  for (const result of results) {
    const score = (result.score * 100).toFixed(0);
    console.log(
      `  ${chalk.cyan(result.document.category)}/${chalk.white(result.document.title)} ${chalk.dim(`(${score}%)`)}`,
    );
    console.log(chalk.dim(`    ${result.snippet}`));
    console.log();
  }
}
