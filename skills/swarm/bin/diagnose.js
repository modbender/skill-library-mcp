#!/usr/bin/env node
/**
 * Swarm Diagnostics CLI
 * Run system checks and tests
 * 
 * Usage:
 *   node bin/diagnose.js [--json] [--skip-e2e] [--verbose]
 */

const { runDiagnostics, printReport } = require('../lib/diagnostics');

async function main() {
  const args = process.argv.slice(2);
  const jsonOutput = args.includes('--json');
  const skipE2e = args.includes('--skip-e2e');
  const verbose = args.includes('--verbose');
  
  if (!jsonOutput) {
    console.log('\n🐝 Running Swarm diagnostics...\n');
  }
  
  const report = await runDiagnostics({
    runTests: true,
    skipE2e,
    verbose,
  });
  
  if (jsonOutput) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    printReport(report);
  }
  
  // Exit with appropriate code
  process.exit(report.status === 'error' ? 1 : 0);
}

main().catch(err => {
  console.error('Diagnostics failed:', err.message);
  process.exit(1);
});
