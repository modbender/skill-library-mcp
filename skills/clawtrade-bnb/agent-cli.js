#!/usr/bin/env node
/**
 * Agent CLI - Control Panel
 * Monitor performance, switch networks, apply learning, view metrics
 */

const NetworkSwitcher = require('./network-switcher');
const PerformanceAnalytics = require('./performance-analytics');
const ReinforcedLearning = require('./reinforced-learning');

class AgentCLI {
  constructor() {
    this.networkSwitcher = new NetworkSwitcher();
    this.analytics = new PerformanceAnalytics();
    this.learning = new ReinforcedLearning();
  }

  /**
   * Display main menu
   */
  showMenu() {
    console.log(`
╔════════════════════════════════════════════════════════════════╗
║                   🤖 YIELD FARMING AGENT - CLI                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  NETWORK MANAGEMENT                                             ║
║    network status     - Show current network & config           ║
║    network testnet    - Switch to BNB Testnet (97)             ║
║    network mainnet    - Switch to BNB Mainnet (56)             ║
║                                                                  ║
║  PERFORMANCE MONITORING                                         ║
║    perf summary       - Overall performance summary             ║
║    perf report        - Detailed performance analysis            ║
║    perf vaults        - Per-vault breakdown                     ║
║    perf strategies    - Strategy effectiveness analysis         ║
║                                                                  ║
║  REINFORCED LEARNING                                            ║
║    learn now          - Analyze history & optimize parameters   ║
║    learn report       - Show learning improvements              ║
║    learn reset        - Reset learning state (use with care)    ║
║                                                                  ║
║  UTILITIES                                                       ║
║    help               - Show this menu                          ║
║    exit               - Quit CLI                                ║
║                                                                  ║
╚════════════════════════════════════════════════════════════════╝
    `);
  }

  /**
   * Execute command
   */
  async execute(command) {
    const [cmd, ...args] = command.toLowerCase().split(' ');

    switch (cmd) {
      // Network commands
      case 'network':
        return this.handleNetwork(args[0]);

      // Performance commands
      case 'perf':
        return this.handlePerformance(args[0]);

      // Learning commands
      case 'learn':
        return this.handleLearning(args[0]);

      // Utility commands
      case 'help':
        return this.showMenu();
      
      case 'exit':
      case 'quit':
        console.log('\n👋 Goodbye!');
        process.exit(0);

      default:
        console.log(`\n❌ Unknown command: ${cmd}`);
        console.log('   Type "help" for available commands');
    }
  }

  /**
   * Network management
   */
  handleNetwork(subcommand) {
    switch (subcommand) {
      case 'status':
        this.networkSwitcher.printNetworkStatus();
        break;

      case 'testnet':
        const testnetInfo = this.networkSwitcher.switchNetwork('testnet');
        console.log(`\n✅ Switched to: ${testnetInfo.name}`);
        break;

      case 'mainnet':
        console.log('\n⚠️  MAINNET MODE - Use with caution!');
        const mainnetInfo = this.networkSwitcher.switchNetwork('mainnet');
        console.log(`✅ Switched to: ${mainnetInfo.name}`);
        console.log(`   Harvest threshold: $${mainnetInfo.harvestThreshold} (increased for safety)`);
        console.log(`   Gas multiplier: ${mainnetInfo.gasSettings.gasMultiplier}x (conservative)`);
        break;

      default:
        console.log('\n❌ Unknown network command');
        console.log('   Use: network {status|testnet|mainnet}');
    }
  }

  /**
   * Performance analytics
   */
  handlePerformance(subcommand) {
    switch (subcommand) {
      case 'summary':
        const summary = this.analytics.getPerformanceSummary();
        console.log(`
📊 PERFORMANCE SUMMARY
──────────────────────────────────────────────────────────
Total Actions:          ${summary.totalActions}
Successful:             ${summary.successfulActions} (${(summary.successRate * 100).toFixed(1)}%)
Failed:                 ${summary.failedActions}

💰 FINANCIAL METRICS
──────────────────────────────────────────────────────────
Total Harvested:        $${summary.totalHarvested.toFixed(2)}
Total Compounded:       $${summary.totalCompounded.toFixed(2)}
Realized APR:           ${summary.realizedAPR.toFixed(2)}%

⏱️  UPTIME
──────────────────────────────────────────────────────────
${summary.uptime}
        `);
        break;

      case 'report':
        this.analytics.generateReport();
        break;

      case 'vaults':
        const vaults = this.analytics.getVaultPerformance();
        console.log('\n📊 VAULT PERFORMANCE BREAKDOWN\n');
        Object.entries(vaults).forEach(([vault, stats]) => {
          console.log(`${vault}`);
          console.log(`  Actions:    ${stats.actions}`);
          console.log(`  Harvested:  $${stats.harvested.toFixed(2)}`);
          console.log(`  Compounded: $${stats.compounded.toFixed(2)}`);
          console.log(`  Errors:     ${stats.errors}`);
          console.log();
        });
        break;

      case 'strategies':
        const strategies = this.analytics.getStrategyAnalysis();
        console.log('\n🎯 STRATEGY EFFECTIVENESS\n');
        Object.entries(strategies).forEach(([strat, stats]) => {
          const success = stats.count > 0 ? ((stats.success / stats.count) * 100).toFixed(1) : '0.0';
          console.log(`${strat}`);
          console.log(`  Executed:   ${stats.count}`);
          console.log(`  Success:    ${success}%`);
          console.log(`  Total Value: $${stats.rewards.toFixed(2)}`);
          console.log();
        });
        break;

      default:
        console.log('\n❌ Unknown performance command');
        console.log('   Use: perf {summary|report|vaults|strategies}');
    }
  }

  /**
   * Reinforced learning
   */
  handleLearning(subcommand) {
    switch (subcommand) {
      case 'now':
        console.log('\n🧠 Starting learning cycle...\n');
        const optimized = this.learning.learn();
        console.log('\n✅ Learning complete!');
        console.log('\n📋 Optimized Configuration:');
        console.log(JSON.stringify(optimized, null, 2));
        break;

      case 'report':
        this.learning.printReport();
        break;

      case 'reset':
        console.log('\n⚠️  Resetting learning state...');
        const fs = require('fs');
        fs.unlinkSync('learning-state.json');
        console.log('✅ Learning state reset');
        break;

      default:
        console.log('\n❌ Unknown learning command');
        console.log('   Use: learn {now|report|reset}');
    }
  }
}

// Interactive CLI mode
async function runInteractive() {
  const cli = new AgentCLI();
  const readline = require('readline');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: '> ',
  });

  cli.showMenu();
  rl.prompt();

  rl.on('line', async (line) => {
    if (line.trim()) {
      await cli.execute(line.trim());
    }
    rl.prompt();
  });

  rl.on('close', () => {
    process.exit(0);
  });
}

// Command-line argument mode
async function runCommand() {
  const cli = new AgentCLI();
  const command = process.argv.slice(2).join(' ');

  if (!command) {
    return runInteractive();
  }

  await cli.execute(command);
}

// Main
if (require.main === module) {
  runCommand().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
}

module.exports = AgentCLI;
