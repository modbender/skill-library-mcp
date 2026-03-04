#!/usr/bin/env node

const { Command } = require('commander');
const chalk = require('chalk');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const RSS = require('../lib/rss');
const Fetcher = require('../lib/fetch');
const Summarizer = require('../lib/summarize');
const Digest = require('../lib/digest');

const program = new Command();
const CONFIG_DIR = path.join(os.homedir(), '.config', 'content-watcher');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

async function ensureConfig() {
  try {
    await fs.mkdir(CONFIG_DIR, { recursive: true });
    try {
      await fs.access(CONFIG_FILE);
    } catch {
      await fs.writeFile(CONFIG_FILE, JSON.stringify({
        sources: [],
        delivery: 'console',
        summaryStyle: 'bullet',
        maxItemsPerSource: 5,
        seenUrls: []
      }, null, 2));
    }
  } catch (e) {
    console.error(chalk.red('Failed to create config:', e.message));
    process.exit(1);
  }
}

async function loadConfig() {
  await ensureConfig();
  const data = await fs.readFile(CONFIG_FILE, 'utf8');
  return JSON.parse(data);
}

async function saveConfig(config) {
  await fs.writeFile(CONFIG_FILE, JSON.stringify(config, null, 2));
}

program
  .name('content-watcher')
  .description('AI-powered content monitoring and summarization')
  .version('1.0.0');

program
  .command('add <url>')
  .description('Add a source to monitor')
  .option('-n, --name <name>', 'Source name')
  .option('-t, --type <type>', 'Source type (rss|url)', 'rss')
  .action(async (url, options) => {
    const config = await loadConfig();
    const source = {
      id: Date.now().toString(),
      url,
      name: options.name || url,
      type: options.type,
      addedAt: new Date().toISOString()
    };
    config.sources.push(source);
    await saveConfig(config);
    console.log(chalk.green('✓ Added source:'), chalk.bold(source.name));
  });

program
  .command('remove <id>')
  .description('Remove a source by ID')
  .action(async (id) => {
    const config = await loadConfig();
    const idx = config.sources.findIndex(s => s.id === id);
    if (idx === -1) {
      console.log(chalk.red('Source not found:', id));
      return;
    }
    const removed = config.sources.splice(idx, 1)[0];
    await saveConfig(config);
    console.log(chalk.green('✓ Removed:'), removed.name);
  });

program
  .command('list')
  .description('List all monitored sources')
  .action(async () => {
    const config = await loadConfig();
    if (config.sources.length === 0) {
      console.log(chalk.yellow('No sources configured.'));
      return;
    }
    console.log(chalk.bold('\nMonitored Sources:'));
    console.log(chalk.gray('─'.repeat(60)));
    config.sources.forEach(s => {
      console.log(`${chalk.cyan(s.id)} ${chalk.white(s.name)}`);
      console.log(`  ${chalk.gray(s.url)}`);
      console.log();
    });
  });

program
  .command('run')
  .description('Run monitoring once and generate digest')
  .option('-o, --output <file>', 'Output file (default: console)')
  .option('--all', 'Include all articles, not just new ones')
  .action(async (options) => {
    const config = await loadConfig();
    if (config.sources.length === 0) {
      console.log(chalk.yellow('No sources configured. Use: content-watcher add <url>'));
      return;
    }

    const rss = new RSS();
    const fetcher = new Fetcher();
    const summarizer = new Summarizer();
    const digest = new Digest(config);

    console.log(chalk.blue('🔍 Fetching sources...\n'));

    const allArticles = [];
    for (const source of config.sources) {
      try {
        console.log(chalk.gray(`Fetching: ${source.name}`));
        const articles = await rss.parse(source.url, config.maxItemsPerSource);
        
        for (const article of articles) {
          if (!options.all && config.seenUrls.includes(article.link)) {
            continue;
          }
          
          try {
            const content = await fetcher.extract(article.link);
            const summary = await summarizer.summarize(content || article.contentSnippet || '');
            
            allArticles.push({
              ...article,
              source: source.name,
              summary,
              fetchedAt: new Date().toISOString()
            });

            if (!config.seenUrls.includes(article.link)) {
              config.seenUrls.push(article.link);
            }
          } catch (e) {
            console.log(chalk.red(`  Failed to process: ${article.title}`));
          }
        }
      } catch (e) {
        console.log(chalk.red(`Failed to fetch ${source.name}: ${e.message}`));
      }
    }

    // Save seen URLs
    await saveConfig(config);

    if (allArticles.length === 0) {
      console.log(chalk.yellow('\nNo new articles found.'));
      return;
    }

    const markdown = digest.generate(allArticles);

    if (options.output) {
      await fs.writeFile(options.output, markdown);
      console.log(chalk.green(`\n✓ Digest saved to: ${options.output}`));
    } else {
      console.log(chalk.bold('\n' + '═'.repeat(60)));
      console.log(chalk.bold('📰 DAILY DIGEST'));
      console.log(chalk.bold('═'.repeat(60)) + '\n');
      console.log(markdown);
    }

    console.log(chalk.gray(`\nProcessed ${allArticles.length} articles from ${config.sources.length} sources`));
  });

program
  .command('config')
  .description('Show current configuration')
  .action(async () => {
    const config = await loadConfig();
    console.log(chalk.bold('Configuration:'));
    console.log(chalk.gray(CONFIG_FILE));
    console.log(JSON.stringify(config, null, 2));
  });

program.parse();
