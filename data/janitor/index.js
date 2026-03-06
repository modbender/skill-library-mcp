#!/usr/bin/env node

/**
 * Janitor Skill - CLI Entry Point
 *
 * Usage:
 *   node index.js clean              - Run cleanup
 *   node index.js stats              - Show statistics
 *   node index.js report             - Generate report
 *   node index.js context            - Show context dashboard
 *   node index.js context clean      - Clean context/sessions
 *   node index.js context emergency  - Emergency cleanup
 *   node index.js monitor start      - Start monitoring
 *   node index.js help               - Show help
 */

const Janitor = require('./janitor');

const janitor = new Janitor();

const args = process.argv.slice(2);
const command = args[0] || 'help';
const subcommand = args[1];

(async () => {
  try {
    switch (command) {
      case 'clean':
      case 'cleanup':
        console.log('Running cleanup...\n');
        const result = await janitor.cleanup();
        console.log('\nResult:', JSON.stringify(result, null, 2));
        break;

      case 'stats':
        console.log('Getting statistics...\n');
        const stats = janitor.getStats();
        console.log(JSON.stringify(stats, null, 2));
        break;

      case 'report':
        console.log('Generating report...\n');
        const report = await janitor.report();
        break;

      // Context Management Commands
      case 'context':
        await handleContextCommand(subcommand, args);
        break;

      case 'monitor':
        await handleMonitorCommand(subcommand, args);
        break;

      case 'archives':
        await handleArchivesCommand(subcommand, args);
        break;

      case 'sessions':
        await handleSessionsCommand(subcommand, args);
        break;

      case 'dashboard':
        await janitor.showDashboard();
        break;

      case 'config':
        await handleConfigCommand(subcommand, args);
        break;

      case 'test':
        await handleTestCommand(subcommand, args);
        break;

      case 'help':
      case '--help':
      case '-h':
        showHelp();
        break;

      default:
        console.error(`Unknown command: ${command}`);
        console.log('Run "node index.js help" for usage information.');
        process.exit(1);
    }
  } catch (error) {
    console.error('Error:', error.message);
    if (process.env.DEBUG) {
      console.error(error.stack);
    }
    process.exit(1);
  }
})();

async function handleContextCommand(subcommand, args) {
  switch (subcommand) {
    case 'clean':
    case 'cleanup':
      const strategy = args[2] || 'moderate';
      await janitor.cleanContext(strategy);
      break;

    case 'emergency':
    case 'emergency-clean':
      await janitor.emergencyClean();
      break;

    case 'status':
      await janitor.showContextStatus();
      break;

    case 'dashboard':
      await janitor.showDashboard();
      break;

    default:
      // No subcommand = show dashboard
      await janitor.showDashboard();
      break;
  }
}

async function handleMonitorCommand(subcommand, args) {
  switch (subcommand) {
    case 'start':
      janitor.startMonitoring();
      console.log('\nMonitoring started. Press Ctrl+C to stop.\n');
      // Keep process alive
      process.on('SIGINT', () => {
        janitor.stopMonitoring();
        process.exit(0);
      });
      break;

    case 'stop':
      janitor.stopMonitoring();
      break;

    case 'status':
      const status = janitor.getMonitoringStatus();
      console.log('\nMonitoring Status:');
      console.log(JSON.stringify(status, null, 2));
      console.log('');
      break;

    default:
      console.error('Usage: monitor <start|stop|status>');
      process.exit(1);
  }
}

async function handleArchivesCommand(subcommand, args) {
  switch (subcommand) {
    case 'list':
      await janitor.listArchives();
      break;

    case 'restore':
      const archiveName = args[2];
      if (!archiveName) {
        console.error('Usage: archives restore <archive-name>');
        process.exit(1);
      }
      await janitor.restoreArchive(archiveName);
      break;

    case 'cleanup':
    case 'clean':
      await janitor.cleanupArchives();
      break;

    case 'stats':
      const stats = await janitor.getArchiveStats();
      console.log('\nArchive Statistics:');
      console.log(JSON.stringify(stats, null, 2));
      console.log('');
      break;

    default:
      // No subcommand = list archives
      await janitor.listArchives();
      break;
  }
}

async function handleSessionsCommand(subcommand, args) {
  const sortBy = args[2] || 'size';
  await janitor.listSessions(sortBy);
}

async function handleConfigCommand(subcommand, args) {
  const ConfigManager = require('./src/utils/config-manager');
  const config = new ConfigManager();

  switch (subcommand) {
    case 'get':
      const key = args[2];
      if (!key) {
        console.error('Usage: config get <key>');
        process.exit(1);
      }
      const value = config.get(key);
      console.log(`${key} = ${JSON.stringify(value)}`);
      break;

    case 'set':
      const setKey = args[2];
      const setValue = args[3];
      if (!setKey || setValue === undefined) {
        console.error('Usage: config set <key> <value>');
        process.exit(1);
      }
      config.set(setKey, setValue);
      console.log(`✅ Set ${setKey} = ${setValue}`);
      break;

    case 'delete':
      const delKey = args[2];
      if (!delKey) {
        console.error('Usage: config delete <key>');
        process.exit(1);
      }
      config.delete(delKey);
      console.log(`✅ Deleted ${delKey}`);
      break;

    case 'list':
      const prefix = args[2];
      config.display(prefix);
      break;

    case 'reset':
      config.reset();
      console.log('✅ Configuration reset to defaults');
      break;

    case 'export':
      const exportPath = args[2] || 'janitor-config-export.json';
      config.exportConfig(exportPath);
      console.log(`✅ Configuration exported to ${exportPath}`);
      break;

    case 'import':
      const importPath = args[2];
      if (!importPath) {
        console.error('Usage: config import <file>');
        process.exit(1);
      }
      config.importConfig(importPath);
      console.log(`✅ Configuration imported from ${importPath}`);
      break;

    case 'validate':
      const validation = config.validate();
      if (validation.valid) {
        console.log('✅ Configuration is valid');
      } else {
        console.log('❌ Configuration has errors:');
        validation.errors.forEach(err => console.log(`  - ${err}`));
        process.exit(1);
      }
      break;

    default:
      config.display();
      break;
  }
}

async function handleTestCommand(subcommand, args) {
  switch (subcommand) {
    case 'notifications':
      const Notifier = require('./src/services/notifier');
      const notifier = new Notifier({
        enabled: true,
        channels: args[2] ? [args[2]] : ['log']
      });
      await notifier.test();
      break;

    case 'github':
      const GitHubBackup = require('./src/services/github-backup');
      const github = new GitHubBackup({ enabled: true });
      const result = await github.test();
      console.log(result.message);
      break;

    default:
      console.log('Available tests:');
      console.log('  test notifications [channel]  - Test notification system');
      console.log('  test github                   - Test GitHub backup connection');
      break;
  }
}

function showHelp() {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║              Janitor Skill v1.1.0 - ClawHub.ai               ║
╚══════════════════════════════════════════════════════════════╝

BASIC COMMANDS:
  clean                    Run immediate cleanup (cache, logs, temp)
  stats                    Show cleanup statistics
  report                   Generate cleanup report

SESSION MANAGEMENT COMMANDS:
  context                  Show context usage dashboard
  context status           Show compact context status
  context clean [strategy] Clean context/sessions
                          Strategies: conservative, moderate, aggressive
  context emergency        Emergency cleanup (keep only last 6 hours)

  dashboard               Show full context dashboard

  sessions [sort]         List all sessions
                          Sort by: size (default), age, messages

  monitor start           Start background monitoring
  monitor stop            Stop background monitoring
  monitor status          Show monitoring status

  archives                List all archives
  archives list           List all archives
  archives restore <name> Restore archived sessions
  archives cleanup        Delete old archives (>30 days)
  archives stats          Show archive statistics

CONFIGURATION COMMANDS:
  config                  Show all configuration
  config get <key>        Get configuration value
  config set <key> <val>  Set configuration value
  config delete <key>     Delete configuration key
  config list [prefix]    List configuration (with optional prefix)
  config reset            Reset to default configuration
  config export [file]    Export configuration to file
  config import <file>    Import configuration from file
  config validate         Validate configuration

TEST COMMANDS:
  test notifications [ch] Test notification system (log/telegram/discord)
  test github             Test GitHub backup connection

EXAMPLES:
  node index.js clean
  node index.js context
  node index.js context clean moderate
  node index.js context emergency
  node index.js monitor start
  node index.js archives list
  node index.js sessions age
  node index.js config set sessionManagement.monitoring.alertThreshold 75
  node index.js test notifications telegram

CONFIGURATION:
  Session management is enabled by default.
  Configure via Janitor constructor options or config commands.
  Config file: ~/.openclaw/janitor-config.json

For advanced features and documentation:
  https://github.com/openclaw/janitor
  `);
}
