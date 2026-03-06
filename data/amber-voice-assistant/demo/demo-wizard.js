#!/usr/bin/env node
// Amber Voice Assistant — Setup Wizard Demo (validation disabled for demo purposes)
// This is a demo version that shows the UX flow without calling real APIs

import { createInterface } from 'node:readline/promises';
import { stdin, stdout } from 'node:process';

const c = {
  reset: '\x1b[0m',
  bold:  '\x1b[1m',
  dim:   '\x1b[2m',
  green: '\x1b[32m',
  red:   '\x1b[31m',
  yellow:'\x1b[33m',
  cyan:  '\x1b[36m',
  magenta:'\x1b[35m',
};
const ok   = (m) => console.log(`${c.green}  ✓ ${m}${c.reset}`);
const warn = (m) => console.log(`${c.yellow}  ⚠ ${m}${c.reset}`);
const info = (m) => console.log(`${c.cyan}  ℹ ${m}${c.reset}`);
const head = (m) => console.log(`\n${c.bold}${c.magenta}─── ${m} ───${c.reset}\n`);

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const spinner = async (label, duration = 800) => {
  const frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'];
  const start = Date.now();
  let i = 0;
  while (Date.now() - start < duration) {
    stdout.write(`\r  ${c.cyan}${frames[i++ % frames.length]} ${label}${c.reset}`);
    await sleep(80);
  }
  stdout.write(`\r${' '.repeat(label.length + 10)}\r`);
};

let rl;
const ask = async (prompt, defaultVal) => {
  const suffix = defaultVal !== undefined ? ` ${c.dim}(${defaultVal})${c.reset}` : '';
  const answer = (await rl.question(`  ${prompt}${suffix}: `)).trim();
  return answer || (defaultVal ?? '');
};

async function main() {
  rl = createInterface({ input: stdin, output: stdout });

  console.log(`
${c.bold}${c.cyan}╔══════════════════════════════════════════════╗
║   ☎️  Amber Voice Assistant — Setup Wizard   ║
╚══════════════════════════════════════════════╝${c.reset}
`);
  info('This wizard will walk you through configuration and generate a .env file.');
  info('Press Enter to accept defaults shown in parentheses.\n');

  const cfg = {};

  // Twilio
  head('Twilio Configuration');
  info('Get credentials at https://console.twilio.com');
  
  cfg.TWILIO_ACCOUNT_SID = await ask('Account SID (starts with AC)');
  cfg.TWILIO_AUTH_TOKEN = await ask('Auth Token');
  
  await spinner('Validating Twilio credentials…');
  ok('Twilio credentials valid');

  cfg.TWILIO_CALLER_ID = await ask('Twilio phone number (E.164, e.g. +15555551234)');
  ok('Phone number format valid');

  // OpenAI
  head('OpenAI Configuration');
  info('Get your API key at https://platform.openai.com/api-keys');

  cfg.OPENAI_API_KEY = await ask('API Key (starts with sk-)');
  await spinner('Validating OpenAI API key…');
  ok('OpenAI API key valid');

  cfg.OPENAI_PROJECT_ID = await ask('Project ID (starts with proj_)');
  ok('Project ID format valid');
  
  cfg.OPENAI_WEBHOOK_SECRET = await ask('Webhook Secret (starts with whsec_)');
  ok('Webhook Secret format valid');
  
  cfg.OPENAI_VOICE = await ask('Voice', 'alloy');
  ok(`Voice: ${cfg.OPENAI_VOICE}`);

  // Server
  head('Server Configuration');
  cfg.PORT = await ask('Port', '8000');
  
  ok('ngrok detected');
  const tunnel = 'https://abc123.ngrok.io';
  ok(`Active ngrok tunnel found: ${tunnel}`);
  
  const useNgrok = await ask(`Use ${tunnel} as PUBLIC_BASE_URL? (y/n)`, 'y');
  if (useNgrok.toLowerCase() === 'y') {
    cfg.PUBLIC_BASE_URL = tunnel;
  } else {
    cfg.PUBLIC_BASE_URL = await ask('Public base URL (e.g. https://your-domain.com)');
  }

  // OpenClaw
  head('OpenClaw Gateway (optional)');
  info('If you have an OpenClaw gateway, the assistant can consult it during calls.');
  
  const wantOC = await ask('Configure OpenClaw integration? (y/n)', 'n');
  if (wantOC.toLowerCase() === 'y') {
    cfg.OPENCLAW_GATEWAY_URL = await ask('Gateway URL', 'http://127.0.0.1:18789');
    cfg.OPENCLAW_GATEWAY_TOKEN = await ask('Gateway Token', '');
  }

  // Personalization
  head('Personalization (optional)');
  
  const wantCustom = await ask('Customize assistant identity? (y/n)', 'y');
  if (wantCustom.toLowerCase() === 'y') {
    cfg.ASSISTANT_NAME = await ask('Assistant name', 'Amber');
    cfg.OPERATOR_NAME = await ask('Operator name (person being assisted)', '');
    cfg.OPERATOR_PHONE = await ask('Operator phone (E.164)', '');
    cfg.OPERATOR_EMAIL = await ask('Operator email', '');
    cfg.ORG_NAME = await ask('Organization name', '');
    cfg.DEFAULT_CALENDAR = await ask('Default calendar name', '');
  }

  // Call screening
  head('Call Screening (optional)');
  const wantGenz = await ask('Configure GenZ-style call screening numbers? (y/n)', 'n');
  if (wantGenz.toLowerCase() === 'y') {
    cfg.GENZ_CALLER_NUMBERS = await ask('Comma-separated E.164 numbers', '');
  }

  // Generate
  head('Generating .env');
  await sleep(500);
  ok('.env written to /tmp/demo/.env');

  // Post-setup
  head('Post-Setup');
  
  const doInstall = await ask('Run npm install? (y/n)', 'y');
  if (doInstall.toLowerCase() === 'y') {
    await spinner('Installing dependencies…', 1500);
    ok('Dependencies installed');
  }

  const doBuild = await ask('Run npm run build? (y/n)', 'y');
  if (doBuild.toLowerCase() === 'y') {
    await spinner('Building…', 1200);
    ok('Build succeeded');
  }

  // Summary
  head('All Done! 🎉');

  const webhookUrl = `${cfg.PUBLIC_BASE_URL}/twilio/inbound`;
  console.log(`
${c.bold}Next steps:${c.reset}

  1. ${c.cyan}Configure Twilio webhook:${c.reset}
     Go to ${c.bold}https://console.twilio.com${c.reset} → Phone Numbers → ${cfg.TWILIO_CALLER_ID}
     Set Voice webhook (HTTP POST) to:
     ${c.green}${c.bold}${webhookUrl}${c.reset}

  2. ${c.cyan}Start the server:${c.reset}
     ${c.bold}npm start${c.reset}

  3. ${c.cyan}Test it:${c.reset}
     Call ${c.bold}${cfg.TWILIO_CALLER_ID}${c.reset} — your voice assistant should answer!

${c.dim}Config saved to: /tmp/demo/.env${c.reset}
`);

  rl.close();
}

main().catch((err) => {
  console.error(`\n${c.red}Setup error: ${err.message}${c.reset}`);
  process.exit(1);
});
