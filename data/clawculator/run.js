#!/usr/bin/env node
'use strict';

const { runAnalysis } = require('./analyzer');
const { generateTerminalReport } = require('./reporter');
const { generateMarkdownReport } = require('./mdReport');
const path = require('path');
const os = require('os');
const fs = require('fs');

const args = process.argv.slice(2);
const flags = {
  json:   args.includes('--json'),
  md:     args.includes('--md'),
  help:   args.includes('--help') || args.includes('-h'),
  config: args.find(a => a.startsWith('--config='))?.split('=')[1],
  out:    args.find(a => a.startsWith('--out='))?.split('=')[1],
};

const BANNER = `
\x1b[36m
   ██████╗██╗      █████╗ ██╗    ██╗ ██████╗ █████╗ ██╗      ██████╗
  ██╔════╝██║     ██╔══██╗██║    ██║██╔════╝██╔══██╗██║     ██╔════╝
  ██║     ██║     ███████║██║ █╗ ██║██║     ███████║██║     ██║     
  ██║     ██║     ██╔══██║██║███╗██║██║     ██╔══██║██║     ██║     
  ╚██████╗███████╗██║  ██║╚███╔███╔╝╚██████╗██║  ██║███████╗╚██████╗
   ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝  ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝
\x1b[0m
  \x1b[33mYour friendly penny pincher.\x1b[0m
  \x1b[90m100% offline · Zero AI · Pure deterministic logic · Your data never leaves your machine\x1b[0m
`;

const HELP = `
Usage: node run.js [options]

Options:
  (no flags)        Full terminal analysis
  --md              Save markdown report to ./clawculator-report.md
  --json            Output raw JSON to stdout
  --out=PATH        Custom output path for --md
  --config=PATH     Path to openclaw.json (auto-detected by default)
  --help, -h        Show this help

Files read (read-only):
  ~/.openclaw/openclaw.json
  ~/.openclaw/agents/main/sessions/sessions.json
  ~/clawd/ (file count only, no contents)
  /tmp/openclaw (if present)

Files written (only when --md is used):
  ./clawculator-report.md (or --out path)

No network requests are made. No data leaves your machine.
Session keys are truncated in all output to protect sensitive identifiers.
`;

async function main() {
  if (flags.help) {
    console.log(BANNER);
    console.log(HELP);
    process.exit(0);
  }

  console.log(BANNER);
  console.log('\x1b[90mScanning your setup...\x1b[0m\n');

  const configPath   = flags.config || path.join(os.homedir(), '.openclaw', 'openclaw.json');
  const sessionsPath = path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions', 'sessions.json');
  const logsDir      = '/tmp/openclaw';

  let analysis;
  try {
    analysis = await runAnalysis({ configPath, sessionsPath, logsDir });
  } catch (err) {
    console.error('\x1b[31mError:\x1b[0m', err.message);
    process.exit(1);
  }

  if (flags.json) {
    console.log(JSON.stringify(analysis, null, 2));
    process.exit(0);
  }

  if (flags.md) {
    const outPath = flags.out || path.join(process.cwd(), 'clawculator-report.md');
    fs.writeFileSync(outPath, generateMarkdownReport(analysis), 'utf8');
    console.log(`\x1b[32m✓ Markdown report saved:\x1b[0m ${outPath}`);
    generateTerminalReport(analysis);
    process.exit(0);
  }

  generateTerminalReport(analysis);
  console.log('\x1b[90m────────────────────────────────────────────────────\x1b[0m');
  console.log('\x1b[36mClawculator\x1b[0m · github.com/echoudhry/clawculator · Your friendly penny pincher.');
  console.log('\x1b[90mTip: --md saves a report your AI agent can read directly\x1b[0m');
  console.log('\x1b[90m────────────────────────────────────────────────────\x1b[0m\n');
}

main().catch(err => {
  console.error('\x1b[31mFatal:\x1b[0m', err.message);
  process.exit(1);
});
