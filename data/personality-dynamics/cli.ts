#!/usr/bin/env node
/**
 * Persona Evolution Skill - CLI
 * 
 * Main entry point for all persona-evolution commands
 */

import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

const COMMANDS = {
  'init': 'init.ts',
  'onboard': 'onboard.ts',
  'expand': 'expand.ts',
  'generate': 'generate-persona.ts',
  'analyze': 'analyze-session.ts',
  'report': 'weekly-report.ts',
  'mode': 'mode-switcher.ts'
};

function showHelp() {
  console.log(`
🎭 Persona Evolution - Dynamic AI Personality

Usage: persona-evolution <command> [options]

Commands:
  generate          AI-powered rich persona generation (RECOMMENDED)
  onboard           Interactive setup via questions
  init              Initialize with templates (manual)
  expand            Expand personality through guided prompts
  analyze           Analyze recent session for patterns
  report            Generate weekly evolution report
  mode [get|set|detect|list]  Manage personality modes

Quick Start:
  persona-evolution generate       # Create rich AI persona
  persona-evolution expand         # Add depth over time
  persona-evolution report         # Weekly insights

Examples:
  persona-evolution mode get       # Check current mode
  persona-evolution mode set creative
  persona-evolution mode detect "Let's brainstorm ideas"

For more info: https://github.com/openclaw/persona-evolution
`);
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === 'help' || command === '--help' || command === '-h') {
    showHelp();
    return;
  }
  
  const script = COMMANDS[command];
  if (!script) {
    console.error(`❌ Unknown command: ${command}`);
    showHelp();
    process.exit(1);
  }
  
  const scriptPath = join(__dirname, script);
  const remainingArgs = args.slice(1).join(' ');
  
  try {
    execSync(`node --experimental-strip-types ${scriptPath} ${remainingArgs}`, {
      stdio: 'inherit',
      cwd: process.cwd()
    });
  } catch (error) {
    process.exit(error.status || 1);
  }
}

main();
