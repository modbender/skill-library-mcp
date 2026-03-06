#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import path from 'path';
import { initConfig, loadConfig, saveConfig } from './config.js';
import { syncWorkspace } from './sync.js';

const program = new Command();

program
  .name('notion-sync')
  .description('Sync any workspace or directory to Notion')
  .version('0.1.0');

// ── INIT ─────────────────────────────────────────────────────────────────────
program
  .command('init')
  .description('Initialize notion-sync in the current directory')
  .requiredOption('--token <token>', 'Notion API token (ntn_...)')
  .requiredOption('--page <id>', 'Root Notion page ID to sync into')
  .option('--dir <path>', 'Directory to sync (default: current dir)', process.cwd())
  .action(({ token, page, dir }) => {
    const absDir = path.resolve(dir);
    initConfig(absDir, token, page);
    console.log(chalk.green('✅ notion-sync initialized!'));
    console.log(chalk.dim(`Config saved to: ${absDir}/.notion-sync.json`));
    console.log(chalk.dim('Run: notion-sync sync'));
  });

// ── SYNC ─────────────────────────────────────────────────────────────────────
program
  .command('sync')
  .description('Sync workspace to Notion')
  .option('--dir <path>', 'Directory to sync (default: current dir)', process.cwd())
  .option('--dry-run', 'Preview what would be synced without making changes')
  .option('--diff', 'Only sync files that changed since last sync')
  .action(async ({ dir, dryRun, diff }) => {
    const absDir = path.resolve(dir);
    const config = loadConfig(absDir);

    console.log(chalk.bold(`Syncing ${absDir} to Notion...`));
    if (dryRun) console.log(chalk.yellow('Dry run — no changes will be made'));

    const result = await syncWorkspace(config, { dryRun, diffOnly: diff });

    if (result.pushed.length > 0) {
      console.log(chalk.green(`\n✅ ${dryRun ? 'Would sync' : 'Synced'} ${result.pushed.length} file(s):`));
      for (const f of result.pushed) console.log(chalk.dim(`  ${f}`));
    }
    if (result.skipped.length > 0) {
      console.log(chalk.dim(`\n⏭  Skipped ${result.skipped.length} unchanged file(s)`));
    }
    if (result.errors.length > 0) {
      console.log(chalk.red(`\n❌ ${result.errors.length} error(s):`));
      for (const e of result.errors) console.log(chalk.red(`  ${e}`));
    }

    if (!dryRun) saveConfig(absDir, config);
  });

// ── IGNORE ───────────────────────────────────────────────────────────────────
program
  .command('ignore')
  .description('Manage ignore patterns')
  .argument('<action>', 'add or list')
  .argument('[pattern]', 'Pattern to add')
  .option('--dir <path>', 'Directory (default: current dir)', process.cwd())
  .action((action, pattern, { dir }) => {
    const absDir = path.resolve(dir);
    const config = loadConfig(absDir);

    if (action === 'list') {
      console.log(chalk.bold('Ignored patterns:'));
      for (const p of config.ignore) console.log(chalk.dim(`  ${p}`));
    } else if (action === 'add' && pattern) {
      if (!config.ignore.includes(pattern)) {
        config.ignore.push(pattern);
        saveConfig(absDir, config);
        console.log(chalk.green(`✅ Added: ${pattern}`));
      } else {
        console.log(chalk.yellow('Pattern already exists'));
      }
    } else {
      console.log(chalk.red('Usage: notion-sync ignore add <pattern>'));
    }
  });

// ── STATUS ────────────────────────────────────────────────────────────────────
program
  .command('status')
  .description('Show sync status')
  .option('--dir <path>', 'Directory (default: current dir)', process.cwd())
  .action(({ dir }) => {
    const absDir = path.resolve(dir);
    const config = loadConfig(absDir);
    const synced = Object.keys(config.checksums).length;
    console.log(chalk.bold('notion-sync status'));
    console.log(`  Directory:  ${absDir}`);
    console.log(`  Root page:  ${config.notion.rootPageId}`);
    console.log(`  Synced:     ${synced} file(s)`);
    console.log(`  Ignored:    ${config.ignore.join(', ')}`);
  });

program.parse();
