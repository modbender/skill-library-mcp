#!/usr/bin/env node
/**
 * PMP-Agentclaw CLI Main Entry
 * Usage: pmp-agentclaw <command> [args...]
 */

const commands: Record<string, string> = {
  'calc-evm': './calc-evm',
  'evm': './calc-evm',
  'score-risks': './score-risks',
  'risk': './score-risks',
  'calc-velocity': './calc-velocity',
  'velocity': './calc-velocity',
  'health-check': './health-check',
  'health': './health-check',
};

function showHelp() {
  console.log(`
PMP-Agentclaw — Project Management CLI

Usage: pmp-agentclaw <command> [options]
   or: pm-evm, pm-risk, pm-velocity, pm-health (direct aliases)

Commands:
  calc-evm <BAC> <PV> <EV> <AC>     Calculate earned value metrics
  score-risks <P> <I>             Score a risk (probability × impact)
  calc-velocity <points...>       Calculate sprint velocity
  health-check [<dir>]            Run project health check

Options:
  --json                          Output as JSON (default)
  --markdown                      Output as Markdown
  --file <path>                  Read from file (for batch operations)
  --forecast <points>            Forecast remaining work (velocity only)

Examples:
  pmp-agentclaw calc-evm 10000 5000 4500 4800 --markdown
  pmp-agentclaw score-risks 3 4
  pmp-agentclaw calc-velocity 34 28 42 --forecast 200
  pmp-agentclaw health-check ./my-project

  # Direct command aliases (faster):
  pm-evm 10000 5000 4500 4800
  pm-risk 3 4
  pm-velocity 34 28 42 --forecast 200
  pm-health ./my-project
`);
}

function main() {
  const [cmd, ...args] = process.argv.slice(2);
  
  if (!cmd || cmd === '--help' || cmd === '-h') {
    showHelp();
    process.exit(0);
  }
  
  const script = commands[cmd];
  if (!script) {
    console.error(`Unknown command: ${cmd}`);
    showHelp();
    process.exit(1);
  }
  
  // Re-execute with the specific script
  // In actual compiled code, this would require the specific module
  const alias = script.replace('./', 'pm-').replace('-check', '');
  console.log(`Run: ${alias} ${args.join(' ')}`);
}

main();
