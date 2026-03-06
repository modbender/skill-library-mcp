/**
 * Session Management Examples
 *
 * Demonstrates how to use Janitor's session management features
 */

const Janitor = require('../janitor');

// ============================================================
// EXAMPLE 1: Basic Usage
// ============================================================
async function basicUsage() {
  console.log('=== EXAMPLE 1: Basic Usage ===\n');

  const janitor = new Janitor();

  // Check current context usage
  const usage = await janitor.getContextUsage();
  console.log(`Context Usage: ${usage.utilizationPercent.toFixed(1)}%`);
  console.log(`Tokens: ${usage.currentTokens}/${usage.maxTokens}`);
  console.log(`Sessions: ${usage.sessions.length}`);
  console.log(`Status: ${usage.status.emoji} ${usage.status.level}\n`);
}

// ============================================================
// EXAMPLE 2: View Dashboard
// ============================================================
async function viewDashboard() {
  console.log('=== EXAMPLE 2: View Dashboard ===\n');

  const janitor = new Janitor();

  // Show full dashboard
  await janitor.showDashboard();
}

// ============================================================
// EXAMPLE 3: Manual Cleanup
// ============================================================
async function manualCleanup() {
  console.log('=== EXAMPLE 3: Manual Cleanup ===\n');

  const janitor = new Janitor();

  // Show status before cleanup
  console.log('Before cleanup:');
  await janitor.showContextStatus();

  // Clean with moderate strategy
  console.log('\nRunning cleanup...');
  const result = await janitor.cleanContext('moderate');

  console.log('\nCleanup Results:');
  console.log(`  Pruned: ${result.pruned} sessions`);
  console.log(`  Freed: ${result.tokensFreed} tokens`);
  console.log(`  Before: ${result.before.utilizationPercent.toFixed(1)}%`);
  console.log(`  After: ${result.after.utilizationPercent.toFixed(1)}%`);
}

// ============================================================
// EXAMPLE 4: Background Monitoring
// ============================================================
async function backgroundMonitoring() {
  console.log('=== EXAMPLE 4: Background Monitoring ===\n');

  const janitor = new Janitor({
    sessionManagement: {
      monitoring: {
        intervalMinutes: 1,  // Check every minute for demo
        alertThreshold: 70,
        emergencyThreshold: 90
      }
    }
  });

  // Start monitoring
  janitor.startMonitoring();

  console.log('Monitoring started. Will check every minute.');
  console.log('Press Ctrl+C to stop.\n');

  // Keep process alive
  process.on('SIGINT', () => {
    console.log('\nStopping monitoring...');
    janitor.stopMonitoring();
    process.exit(0);
  });

  // Show status every 30 seconds
  setInterval(async () => {
    const status = janitor.getMonitoringStatus();
    console.log(`\n[${new Date().toLocaleTimeString()}] Monitoring Status:`);
    console.log(`  Running: ${status.running}`);
    console.log(`  Checks: ${status.checkCount}`);
    console.log(`  Cleanups: ${status.cleanupCount}`);
    console.log(`  Last Check: ${status.lastCheck ? status.lastCheck.toLocaleTimeString() : 'Never'}`);
  }, 30000);
}

// ============================================================
// EXAMPLE 5: Emergency Cleanup
// ============================================================
async function emergencyCleanup() {
  console.log('=== EXAMPLE 5: Emergency Cleanup ===\n');

  const janitor = new Janitor();

  // Check if emergency is needed
  const usage = await janitor.getContextUsage();

  if (usage.utilizationPercent >= 95) {
    console.log('Emergency cleanup required!\n');
    const result = await janitor.emergencyClean();

    console.log('\nEmergency Cleanup Results:');
    console.log(`  Success: ${result.success}`);
    console.log(`  Before: ${result.beforeUsage.percent.toFixed(1)}% (${result.beforeUsage.sessions} sessions)`);
    console.log(`  After: ${result.afterUsage.percent.toFixed(1)}% (${result.afterUsage.sessions} sessions)`);
  } else {
    console.log(`Current usage: ${usage.utilizationPercent.toFixed(1)}%`);
    console.log('Emergency cleanup not needed.');
  }
}

// ============================================================
// EXAMPLE 6: Session Management
// ============================================================
async function sessionManagement() {
  console.log('=== EXAMPLE 6: Session Management ===\n');

  const janitor = new Janitor();

  // List sessions by size
  console.log('Sessions by size:');
  await janitor.listSessions('size');

  console.log('\nSessions by age:');
  await janitor.listSessions('age');

  console.log('\nSessions by message count:');
  await janitor.listSessions('messages');
}

// ============================================================
// EXAMPLE 7: Archive Management
// ============================================================
async function archiveManagement() {
  console.log('=== EXAMPLE 7: Archive Management ===\n');

  const janitor = new Janitor();

  // List all archives
  console.log('Current archives:');
  const archives = await janitor.listArchives();

  if (archives.length > 0) {
    // Show archive stats
    console.log('\nArchive statistics:');
    const stats = await janitor.getArchiveStats();
    console.log(`  Total archives: ${stats.totalArchives}`);
    console.log(`  Total sessions: ${stats.totalSessions}`);
    console.log(`  Total size: ${stats.totalSize}`);

    // Restore an archive (example)
    // await janitor.restoreArchive(archives[0].archiveName);
  }

  // Cleanup old archives
  console.log('\nCleaning up old archives...');
  await janitor.cleanupArchives();
}

// ============================================================
// EXAMPLE 8: Custom Configuration
// ============================================================
async function customConfiguration() {
  console.log('=== EXAMPLE 8: Custom Configuration ===\n');

  // Aggressive cleanup for Raspberry Pi
  const janitor = new Janitor({
    sessionManagement: {
      monitoring: {
        intervalMinutes: 5,
        alertThreshold: 70,
        emergencyThreshold: 85
      },
      pruning: {
        maxSessionAge: 3,
        keepRecentHours: 12,
        keepMinimumSessions: 3
      },
      archiving: {
        retentionDays: 14
      }
    }
  });

  console.log('Using aggressive cleanup configuration:');
  console.log('  Alert at 70% usage');
  console.log('  Emergency at 85% usage');
  console.log('  Delete sessions after 3 days');
  console.log('  Keep only last 12 hours in emergency\n');

  await janitor.showContextStatus();
}

// ============================================================
// EXAMPLE 9: Complete Workflow
// ============================================================
async function completeWorkflow() {
  console.log('=== EXAMPLE 9: Complete Workflow ===\n');

  const janitor = new Janitor();

  // Step 1: Check current status
  console.log('Step 1: Check current status');
  await janitor.showContextStatus();

  // Step 2: Start monitoring
  console.log('\nStep 2: Start background monitoring');
  janitor.startMonitoring();

  // Step 3: Manual cleanup if needed
  const usage = await janitor.getContextUsage();
  if (usage.utilizationPercent > 80) {
    console.log('\nStep 3: Running cleanup (usage > 80%)');
    await janitor.cleanContext('moderate');
  } else {
    console.log('\nStep 3: Cleanup not needed (usage < 80%)');
  }

  // Step 4: View dashboard
  console.log('\nStep 4: Final dashboard');
  await janitor.showDashboard();

  // Step 5: Cleanup archives
  console.log('\nStep 5: Cleanup old archives');
  await janitor.cleanupArchives();

  console.log('\nWorkflow complete!');

  // Stop monitoring
  janitor.stopMonitoring();
}

// ============================================================
// RUN EXAMPLES
// ============================================================

async function main() {
  const examples = {
    '1': basicUsage,
    '2': viewDashboard,
    '3': manualCleanup,
    '4': backgroundMonitoring,
    '5': emergencyCleanup,
    '6': sessionManagement,
    '7': archiveManagement,
    '8': customConfiguration,
    '9': completeWorkflow
  };

  const choice = process.argv[2] || '1';

  if (examples[choice]) {
    await examples[choice]();
  } else {
    console.log('Available examples:');
    console.log('  1 - Basic Usage');
    console.log('  2 - View Dashboard');
    console.log('  3 - Manual Cleanup');
    console.log('  4 - Background Monitoring');
    console.log('  5 - Emergency Cleanup');
    console.log('  6 - Session Management');
    console.log('  7 - Archive Management');
    console.log('  8 - Custom Configuration');
    console.log('  9 - Complete Workflow');
    console.log('\nUsage: node examples/session-management.js [1-9]');
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  basicUsage,
  viewDashboard,
  manualCleanup,
  backgroundMonitoring,
  emergencyCleanup,
  sessionManagement,
  archiveManagement,
  customConfiguration,
  completeWorkflow
};
