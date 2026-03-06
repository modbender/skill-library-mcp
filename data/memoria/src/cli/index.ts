import { Command } from 'commander';
import { initCommand } from '../commands/init.js';
import { storeCommand } from '../commands/store.js';
import { rememberCommand } from '../commands/remember.js';
import { listCommand } from '../commands/list.js';
import { getCommand } from '../commands/get.js';
import { searchCommand } from '../commands/search.js';
import { wakeCommand } from '../commands/wake.js';
import { sleepCommand } from '../commands/sleep.js';
import { checkpointCommand } from '../commands/checkpoint.js';
import { statusCommand } from '../commands/status.js';
import { setupNotionCommand } from '../commands/setup-notion.js';
import { syncCommand } from '../commands/sync.js';

export function createProgram(): Command {
  const program = new Command();

  program
    .name('memoria')
    .description('Structured memory system for AI agents with Notion sync')
    .version('0.1.0');

  program
    .command('init <path>')
    .description('Initialize a new Memoria vault')
    .option('-n, --name <name>', 'Vault name')
    .action(initCommand);

  program
    .command('store <category> <title>')
    .description('Store a document in an explicit category')
    .option('-c, --content <content>', 'Document content')
    .option('-t, --tags <tags>', 'Comma-separated tags')
    .option('-v, --vault <path>', 'Vault path')
    .option('--overwrite', 'Overwrite existing document')
    .option('--sync', 'Push to Notion after storing')
    .option('--no-sync', 'Skip auto-sync even if enabled')
    .action(storeCommand);

  program
    .command('remember <type> <title>')
    .description('Store a typed memory (fact, decision, lesson, etc.)')
    .option('-c, --content <content>', 'Memory content')
    .option('-t, --tags <tags>', 'Comma-separated tags')
    .option('-v, --vault <path>', 'Vault path')
    .option('--overwrite', 'Overwrite existing document')
    .option('--sync', 'Push to Notion after storing')
    .option('--no-sync', 'Skip auto-sync even if enabled')
    .action(rememberCommand);

  program
    .command('list [category]')
    .description('List documents in the vault')
    .option('-t, --tags <tags>', 'Filter by comma-separated tags')
    .option('-v, --vault <path>', 'Vault path')
    .action(listCommand);

  program
    .command('get <id>')
    .description('Get a specific document by ID (category/slug)')
    .option('-v, --vault <path>', 'Vault path')
    .action(getCommand);

  program
    .command('search <query>')
    .description('Search documents by text query')
    .option('--category <category>', 'Filter by category')
    .option('-l, --limit <n>', 'Max results', '10')
    .option('-v, --vault <path>', 'Vault path')
    .action(searchCommand);

  program
    .command('wake')
    .description('Start a new session, load recent context')
    .option('-v, --vault <path>', 'Vault path')
    .action(wakeCommand);

  program
    .command('sleep <summary>')
    .description('End the current session with a handoff summary')
    .option('--next <steps>', 'Next steps for the following session')
    .option('-v, --vault <path>', 'Vault path')
    .action(sleepCommand);

  program
    .command('checkpoint')
    .description('Save a mid-session checkpoint')
    .option('--working-on <task>', 'What you are working on')
    .option('--focus <focus>', 'Current focus area')
    .option('-v, --vault <path>', 'Vault path')
    .action(checkpointCommand);

  program
    .command('status')
    .description('Show vault stats and session state')
    .option('-v, --vault <path>', 'Vault path')
    .action(statusCommand);

  program
    .command('setup-notion')
    .description('Configure Notion integration')
    .requiredOption('--token <token>', 'Notion integration token')
    .requiredOption('--page <pageId>', 'Root Notion page ID')
    .option('-v, --vault <path>', 'Vault path')
    .action(setupNotionCommand);

  program
    .command('sync')
    .description('Sync vault with Notion (push and/or pull)')
    .option('--push', 'Push local changes to Notion')
    .option('--pull', 'Pull Notion changes to local')
    .option('--prefer-notion', 'On conflict, prefer Notion version')
    .option('--dry-run', 'Show what would change without modifying anything')
    .option('-v, --vault <path>', 'Vault path')
    .action(syncCommand);

  return program;
}

export async function run(): Promise<void> {
  const program = createProgram();
  await program.parseAsync(process.argv);
}
