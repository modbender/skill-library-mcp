#!/usr/bin/env node
// Amber Voice Assistant — Interactive Setup Wizard
// Usage: npm run setup  (or:  node setup-wizard.js)

import { createInterface } from 'node:readline/promises';
import { stdin, stdout, env } from 'node:process';
import { existsSync, copyFileSync, writeFileSync, readFileSync } from 'node:fs';
import { execSync, spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

// ── Colours ──────────────────────────────────────────────────────────
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
const fail = (m) => console.log(`${c.red}  ✗ ${m}${c.reset}`);
const warn = (m) => console.log(`${c.yellow}  ⚠ ${m}${c.reset}`);
const info = (m) => console.log(`${c.cyan}  ℹ ${m}${c.reset}`);
const head = (m) => console.log(`\n${c.bold}${c.magenta}─── ${m} ───${c.reset}\n`);

// ── Helpers ──────────────────────────────────────────────────────────
const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath   = resolve(__dirname, '.env');

let rl;
const ask = async (prompt, defaultVal) => {
  const suffix = defaultVal !== undefined ? ` ${c.dim}(${defaultVal})${c.reset}` : '';
  const answer = (await rl.question(`  ${prompt}${suffix}: `)).trim();
  return answer || (defaultVal ?? '');
};

const yesNo = async (prompt, defaultYes = true) => {
  const hint = defaultYes ? 'Y/n' : 'y/N';
  const answer = (await rl.question(`  ${prompt} ${c.dim}[${hint}]${c.reset} `)).trim().toLowerCase();
  if (!answer) return defaultYes;
  return answer.startsWith('y');
};

const spinner = (label) => {
  const frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'];
  let i = 0;
  const id = setInterval(() => {
    stdout.write(`\r  ${c.cyan}${frames[i++ % frames.length]} ${label}${c.reset}`);
  }, 80);
  return { stop: (msg) => { clearInterval(id); stdout.write(`\r${' '.repeat(label.length + 10)}\r`); if (msg) console.log(msg); } };
};

// ── Validators ───────────────────────────────────────────────────────
const isE164 = (v) => /^\+[1-9]\d{6,14}$/.test(v);
const VOICES = ['alloy','echo','fable','onyx','nova','shimmer'];

async function validateTwilio(sid, token) {
  const s = spinner('Validating Twilio credentials…');
  try {
    const res = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${sid}.json`, {
      headers: { Authorization: 'Basic ' + Buffer.from(`${sid}:${token}`).toString('base64') },
    });
    s.stop();
    if (res.ok) { ok('Twilio credentials valid'); return true; }
    fail(`Twilio auth failed (HTTP ${res.status})`);
    return false;
  } catch (e) {
    s.stop();
    fail(`Twilio network error: ${e.message}`);
    return false;
  }
}

async function validateOpenAI(key) {
  const s = spinner('Validating OpenAI API key…');
  try {
    const res = await fetch('https://api.openai.com/v1/models', {
      headers: { Authorization: `Bearer ${key}` },
    });
    s.stop();
    if (res.ok) { ok('OpenAI API key valid'); return true; }
    fail(`OpenAI auth failed (HTTP ${res.status})`);
    return false;
  } catch (e) {
    s.stop();
    fail(`OpenAI network error: ${e.message}`);
    return false;
  }
}

function detectNgrok() {
  // Security: hardcoded command, no user input involved
  try { execSync('which ngrok', { stdio: 'pipe' }); return true; } catch { return false; }
}

async function getActiveNgrokTunnel() {
  try {
    const res = await fetch('http://127.0.0.1:4040/api/tunnels', { signal: AbortSignal.timeout(2000) });
    if (!res.ok) return null;
    const data = await res.json();
    const https = data.tunnels?.find(t => t.proto === 'https');
    return https?.public_url ?? data.tunnels?.[0]?.public_url ?? null;
  } catch { return null; }
}

async function startNgrok(port) {
  info('Starting ngrok…');
  // Security: 'ngrok' is a hardcoded binary name; port is coerced to string from a numeric config value
  const proc = spawn('ngrok', ['http', String(port)], { stdio: 'ignore', detached: true });
  proc.unref();
  // wait up to 5s for tunnel
  for (let i = 0; i < 10; i++) {
    await new Promise(r => setTimeout(r, 500));
    const url = await getActiveNgrokTunnel();
    if (url) { ok(`ngrok tunnel: ${url}`); return url; }
  }
  warn('ngrok started but no tunnel detected yet — you may need to set PUBLIC_BASE_URL manually.');
  return null;
}

// ── Main ─────────────────────────────────────────────────────────────
async function main() {
  rl = createInterface({ input: stdin, output: stdout });

  console.log(`
${c.bold}${c.cyan}╔══════════════════════════════════════════════╗
║   ☎️  Amber Voice Assistant — Setup Wizard    ║
╚══════════════════════════════════════════════╝${c.reset}
`);
  info('This wizard will walk you through configuration and generate a .env file.');
  info('Press Enter to accept defaults shown in parentheses.\n');

  const cfg = {};

  // ── Twilio ─────────────────────────────────────────────────────────
  head('Twilio Configuration');
  info('Get credentials at https://console.twilio.com');

  while (true) {
    cfg.TWILIO_ACCOUNT_SID = await ask('Account SID (starts with AC)');
    if (!cfg.TWILIO_ACCOUNT_SID.startsWith('AC') || cfg.TWILIO_ACCOUNT_SID.length < 34) {
      fail('Account SID must start with "AC" and be 34 characters'); continue;
    }
    cfg.TWILIO_AUTH_TOKEN = await ask('Auth Token');
    if (!cfg.TWILIO_AUTH_TOKEN) { fail('Auth Token is required'); continue; }
    if (await validateTwilio(cfg.TWILIO_ACCOUNT_SID, cfg.TWILIO_AUTH_TOKEN)) break;
    if (!(await yesNo('Try again?'))) break;
  }

  while (true) {
    cfg.TWILIO_CALLER_ID = await ask('Twilio phone number (E.164, e.g. +15555551234)');
    if (isE164(cfg.TWILIO_CALLER_ID)) { ok('Phone number format valid'); break; }
    fail('Must be E.164 format: +<country><number>');
  }

  // ── OpenAI ─────────────────────────────────────────────────────────
  head('OpenAI Configuration');
  info('Get your API key at https://platform.openai.com/api-keys');

  while (true) {
    cfg.OPENAI_API_KEY = await ask('API Key (starts with sk-)');
    if (!cfg.OPENAI_API_KEY.startsWith('sk-')) { fail('API key should start with "sk-"'); continue; }
    if (await validateOpenAI(cfg.OPENAI_API_KEY)) break;
    if (!(await yesNo('Try again?'))) break;
  }

  while (true) {
    cfg.OPENAI_PROJECT_ID = await ask('Project ID (starts with proj_)');
    if (!cfg.OPENAI_PROJECT_ID) {
      warn('Project ID is required');
      continue;
    }
    if (!cfg.OPENAI_PROJECT_ID.startsWith('proj_')) {
      warn('Project ID usually starts with "proj_" — using as-is');
    }
    break;
  }

  while (true) {
    cfg.OPENAI_WEBHOOK_SECRET = await ask('Webhook Secret (starts with whsec_)');
    if (!cfg.OPENAI_WEBHOOK_SECRET) {
      warn('Webhook Secret is required');
      continue;
    }
    if (!cfg.OPENAI_WEBHOOK_SECRET.startsWith('whsec_')) {
      warn('Webhook secret usually starts with "whsec_" — using as-is');
    }
    break;
  }

  while (true) {
    cfg.OPENAI_VOICE = (await ask('Voice', 'alloy')).toLowerCase();
    if (VOICES.includes(cfg.OPENAI_VOICE)) { ok(`Voice: ${cfg.OPENAI_VOICE}`); break; }
    fail(`Must be one of: ${VOICES.join(', ')}`);
  }

  // ── Server ─────────────────────────────────────────────────────────
  head('Server Configuration');

  cfg.PORT = await ask('Port', '8000');

  // ngrok detection
  const ngrokInstalled = detectNgrok();
  let publicUrl = null;

  if (ngrokInstalled) {
    ok('ngrok detected');
    const tunnel = await getActiveNgrokTunnel();
    if (tunnel) {
      ok(`Active ngrok tunnel found: ${tunnel}`);
      if (await yesNo(`Use ${tunnel} as PUBLIC_BASE_URL?`)) publicUrl = tunnel;
    } else {
      info('No active ngrok tunnel found.');
      if (await yesNo(`Start ngrok on port ${cfg.PORT}?`)) {
        publicUrl = await startNgrok(cfg.PORT);
      }
    }
  } else {
    info('ngrok not detected. You\'ll need a public URL for webhooks.');
  }

  if (!publicUrl) {
    cfg.PUBLIC_BASE_URL = await ask('Public base URL (e.g. https://your-domain.com)');
  } else {
    cfg.PUBLIC_BASE_URL = publicUrl;
  }

  // ── Optional: OpenClaw ─────────────────────────────────────────────
  head('OpenClaw Gateway (optional)');
  info('If you have an OpenClaw gateway, the assistant can consult it during calls.');

  if (await yesNo('Configure OpenClaw integration?', false)) {
    cfg.OPENCLAW_GATEWAY_URL = await ask('Gateway URL', 'http://127.0.0.1:18789');
    cfg.OPENCLAW_GATEWAY_TOKEN = await ask('Gateway Token', '');
  }

  // ── Optional: Personalization ──────────────────────────────────────
  head('Personalization (optional)');

  if (await yesNo('Customize assistant identity?', false)) {
    cfg.ASSISTANT_NAME = await ask('Assistant name', 'Amber');
    cfg.OPERATOR_NAME  = await ask('Operator name (person being assisted)', '');
    cfg.OPERATOR_PHONE = await ask('Operator phone (E.164)', '');
    if (cfg.OPERATOR_PHONE && !isE164(cfg.OPERATOR_PHONE)) warn('Not a valid E.164 number');
    cfg.OPERATOR_EMAIL = await ask('Operator email', '');
    cfg.ORG_NAME       = await ask('Organization name', '');
    cfg.DEFAULT_CALENDAR = await ask('Default calendar name', '');
  }

  // ── Optional: Call Screening ───────────────────────────────────────
  head('Call Screening (optional)');

  if (await yesNo('Configure GenZ-style call screening numbers?', false)) {
    cfg.GENZ_CALLER_NUMBERS = await ask('Comma-separated E.164 numbers', '');
  }

  // ── Generate .env ──────────────────────────────────────────────────
  head('Generating .env');

  if (existsSync(envPath)) {
    const ts = new Date().toISOString().replace(/[:.]/g, '-');
    const backup = `${envPath}.backup.${ts}`;
    copyFileSync(envPath, backup);
    ok(`Backed up existing .env → ${backup}`);
  }

  const lines = [
    '# Amber Voice Assistant - Generated by setup wizard',
    `# ${new Date().toISOString()}`,
    '',
    '# === Telephony Provider ===',
    'VOICE_PROVIDER=twilio',
    '',
    '# === Twilio ===',
    `TWILIO_ACCOUNT_SID=${cfg.TWILIO_ACCOUNT_SID}`,
    `TWILIO_AUTH_TOKEN=${cfg.TWILIO_AUTH_TOKEN}`,
    `TWILIO_CALLER_ID=${cfg.TWILIO_CALLER_ID}`,
    '',
    '# === OpenAI ===',
    `OPENAI_API_KEY=${cfg.OPENAI_API_KEY}`,
    `OPENAI_PROJECT_ID=${cfg.OPENAI_PROJECT_ID || ''}`,
    `OPENAI_WEBHOOK_SECRET=${cfg.OPENAI_WEBHOOK_SECRET || ''}`,
    `OPENAI_VOICE=${cfg.OPENAI_VOICE}`,
    '',
    '# === Server ===',
    `PORT=${cfg.PORT}`,
    `PUBLIC_BASE_URL=${cfg.PUBLIC_BASE_URL}`,
  ];

  if (cfg.OPENCLAW_GATEWAY_URL) {
    lines.push('', '# === OpenClaw Gateway ===',
      `OPENCLAW_GATEWAY_URL=${cfg.OPENCLAW_GATEWAY_URL}`,
      `OPENCLAW_GATEWAY_TOKEN=${cfg.OPENCLAW_GATEWAY_TOKEN || ''}`);
  }

  if (cfg.ASSISTANT_NAME || cfg.OPERATOR_NAME) {
    lines.push('', '# === Personalization ===');
    for (const k of ['ASSISTANT_NAME','OPERATOR_NAME','OPERATOR_PHONE','OPERATOR_EMAIL','ORG_NAME','DEFAULT_CALENDAR']) {
      if (cfg[k]) lines.push(`${k}=${cfg[k]}`);
    }
  }

  if (cfg.GENZ_CALLER_NUMBERS) {
    lines.push('', '# === Call Screening ===', `GENZ_CALLER_NUMBERS=${cfg.GENZ_CALLER_NUMBERS}`);
  }

  lines.push('');
  writeFileSync(envPath, lines.join('\n'));
  ok(`.env written to ${envPath}`);

  // ── Post-setup ─────────────────────────────────────────────────────
  head('Post-Setup');

  if (await yesNo('Run npm install?')) {
    // Check for native build tools — better-sqlite3 (CRM skill) requires compilation.
    // On macOS this means Xcode CLI tools + accepted license. Warn early so the user
    // knows what to do if npm install fails with a gyp/make error.
    const platform = process.platform;
    if (platform === 'darwin') {
      try {
        execSync('xcode-select -p', { stdio: 'pipe' });
        // Xcode tools present — check license accepted
        try {
          execSync('xcodebuild -license check', { stdio: 'pipe' });
        } catch (_) {
          warn('Xcode license not accepted. The CRM skill (better-sqlite3) requires native compilation.');
          warn('If npm install fails, run: sudo xcodebuild -license accept');
        }
      } catch (_) {
        warn('Xcode Command Line Tools not found. The CRM skill (better-sqlite3) requires native compilation.');
        warn('Install them first: xcode-select --install');
      }
    } else if (platform === 'linux') {
      try {
        execSync('which make && which python3', { stdio: 'pipe' });
      } catch (_) {
        warn('build-essential or python3 may be missing. The CRM skill requires native compilation.');
        warn('On Debian/Ubuntu: sudo apt install build-essential python3');
      }
    }

    const s = spinner('Installing dependencies…');
    try {
      // Security: hardcoded npm command, cwd scoped to this script's own directory
      execSync('npm install', { cwd: __dirname, stdio: 'pipe' });
      s.stop(); ok('Dependencies installed');
    } catch (e) {
      s.stop(); fail(`npm install failed: ${e.message}`);
      if (platform === 'darwin') {
        info('If the error mentions gyp or make, run: sudo xcodebuild -license accept  then retry npm install.');
      }
    }
  }

  if (await yesNo('Run npm run build?')) {
    const s = spinner('Building…');
    try {
      // Security: hardcoded npm command, cwd scoped to this script's own directory
      execSync('npm run build', { cwd: __dirname, stdio: 'pipe' });
      s.stop(); ok('Build succeeded');
    } catch (e) {
      s.stop(); fail(`Build failed: ${e.message}`);
    }
  }

  // ── Native Tools (macOS only) ────────────────────────────────────
  if (process.platform === 'darwin') {
    head('Native Tools (macOS)');
    info('Amber uses native macOS tools for Calendar and Contacts access.');
    info('These need to be compiled from Swift source (one-time).');

    // Check for Swift compiler
    let hasSwift = false;
    try {
      execSync('which swiftc', { stdio: 'pipe' });
      hasSwift = true;
      ok('Swift compiler found');
    } catch (_) {
      warn('Swift compiler not found. Install Xcode Command Line Tools:');
      info('  xcode-select --install');
      info('You can re-run setup after installing to compile native tools.');
    }

    if (hasSwift) {
      const srcDir = resolve(__dirname, 'src');
      const toolsDir = resolve(__dirname, '..', 'tools');

      // Ensure tools directory exists
      const { mkdirSync } = await import('node:fs');
      try { mkdirSync(toolsDir, { recursive: true }); } catch (_) {}

      // ── ical-query ──
      const icalSrc = resolve(srcDir, 'ical-query.swift');
      const icalBin = resolve(toolsDir, 'ical-query');
      if (existsSync(icalSrc)) {
        if (existsSync(icalBin)) {
          ok('ical-query already compiled');
        } else if (await yesNo('Compile ical-query (Calendar access)?')) {
          const s = spinner('Compiling ical-query…');
          try {
            execSync(`swiftc "${icalSrc}" -o "${icalBin}" -framework EventKit -O`, { stdio: 'pipe', timeout: 60000 });
            s.stop(); ok('ical-query compiled');
          } catch (e) {
            s.stop(); fail(`ical-query compilation failed: ${e.message}`);
          }
        }
      } else {
        info('ical-query source not found — skipping (Calendar features may be limited)');
      }

      // ── Grant permissions ──
      const compiledTools = [];
      if (existsSync(icalBin)) compiledTools.push({ name: 'ical-query', bin: icalBin, what: 'Calendar' });

      if (compiledTools.length > 0) {
        head('macOS Permissions');
        info('macOS requires you to grant Calendar and Contacts access.');
        info('A system dialog will appear for each — click "Allow".\n');

        for (const tool of compiledTools) {
          if (await yesNo(`Grant ${tool.what} access now?`)) {
            try {
              // Run a harmless query to trigger the macOS permission prompt
              const testCmd = tool.name === 'ical-query' ? 'today' : 'search test';
              execSync(`"${tool.bin}" ${testCmd}`, { stdio: 'pipe', timeout: 30000 });
              ok(`${tool.what} access granted`);
            } catch (e) {
              const errMsg = e.stderr?.toString() || e.message || '';
              if (errMsg.includes('denied') || errMsg.includes('Denied')) {
                warn(`${tool.what} access was denied. Grant it manually:`);
                info(`  System Settings → Privacy & Security → ${tool.what} → enable ${tool.name}`);
              } else {
                // Non-permission error — the command may have run fine but returned non-zero
                // (e.g., no calendar events today). Check if it was actually a permission issue.
                ok(`${tool.what} permission prompt triggered — check if you saw a dialog`);
              }
            }
          }
        }
      }
    }
  }

  // ── Claude Desktop / Cowork Setup ───────────────────────────────
  head('Claude Desktop / Cowork Plugin (optional)');
  info('Amber can also run as an MCP plugin for Claude Desktop.');
  const isCowork = await yesNo('Are you setting up for Claude Desktop / Cowork?', false);

  // ── Contacts Sync (macOS + Cowork only) ─────────────────────────
  if (process.platform === 'darwin' && isCowork) {
    head('Apple Contacts Sync');
    info('Amber can look up contacts from your Apple address book.');
    info('This exports your contacts to a local JSON cache file.');
    info('(The cache stays on your machine — nothing is uploaded.)\n');

    if (await yesNo('Sync Apple Contacts now?')) {
      const s = spinner('Exporting contacts…');
      try {
        const syncScript = resolve(__dirname, 'scripts', 'sync-contacts.js');
        execSync(`node "${syncScript}"`, { cwd: __dirname, stdio: 'pipe', timeout: 30000 });
        s.stop();
        const cachePath = resolve(__dirname, 'contacts-cache.json');
        if (existsSync(cachePath)) {
          const cache = JSON.parse(readFileSync(cachePath, 'utf8'));
          ok(`Exported ${cache.count} contacts to contacts-cache.json`);
        } else {
          ok('Contacts sync completed');
        }
        info('To refresh later: npm run sync-contacts');
      } catch (e) {
        s.stop();
        const errMsg = e.stderr?.toString() || e.message || '';
        if (errMsg.includes('denied') || errMsg.includes('EPERM')) {
          fail('Contacts access denied.');
          info('Grant Full Disk Access to Terminal:');
          info('  System Settings → Privacy & Security → Full Disk Access → enable Terminal');
          info('Then re-run: npm run sync-contacts');
        } else {
          fail(`Contacts sync failed: ${e.message}`);
        }
      }
    } else {
      info('Skipped. Run later: npm run sync-contacts');
    }
  }

  // ── Summary ────────────────────────────────────────────────────────
  head('All Done! 🎉');

  const webhookUrl = `${cfg.PUBLIC_BASE_URL}/twilio/inbound`;
  const hasNativeTools = process.platform === 'darwin' &&
    existsSync(resolve(__dirname, '..', 'tools', 'ical-query'));
  const hasContactsCache = isCowork && existsSync(resolve(__dirname, 'contacts-cache.json'));

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
${hasNativeTools ? `
  4. ${c.cyan}Calendar access:${c.reset}
     ical-query compiled and configured.
     If permission was denied, grant it in:
     ${c.bold}System Settings → Privacy & Security → Calendar${c.reset}
` : ''}${hasContactsCache ? `
  ${hasNativeTools ? '5' : '4'}. ${c.cyan}Contacts:${c.reset}
     Apple Contacts synced to local cache.
     To refresh: ${c.bold}npm run sync-contacts${c.reset}
` : ''}
${c.dim}Config saved to: ${envPath}${c.reset}
`);

  rl.close();
}

main().catch((err) => {
  if (err.code === 'ERR_USE_AFTER_CLOSE' || err.message?.includes('readline was closed')) {
    // user hit Ctrl+C
    console.log(`\n${c.yellow}Setup cancelled.${c.reset}`);
  } else {
    console.error(`\n${c.red}Setup error: ${err.message}${c.reset}`);
  }
  process.exit(1);
});
