#!/usr/bin/env node
/*
 * Configure Telegram bot menu button and /canvas command.
 * Usage: node scripts/setup-bot.js
 */

const fs = require('fs');
const path = require('path');

function parseDotEnv(envPath) {
  if (!fs.existsSync(envPath)) return {};
  const out = {};
  const lines = fs.readFileSync(envPath, 'utf8').split(/\r?\n/);
  for (const line of lines) {
    if (!line || line.trim().startsWith('#')) continue;
    const idx = line.indexOf('=');
    if (idx === -1) continue;
    const key = line.slice(0, idx).trim();
    let val = line.slice(idx + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    out[key] = val;
  }
  return out;
}

async function callTelegram(token, method, payload) {
  const url = `https://api.telegram.org/bot${token}/${method}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok || !json.ok) {
    const errMsg = json?.description || res.statusText || 'Unknown error';
    throw new Error(`${method} failed: ${errMsg}`);
  }
  return json;
}

async function main() {
  const envFromFile = parseDotEnv(path.resolve(process.cwd(), '.env'));
  const BOT_TOKEN = process.env.BOT_TOKEN || envFromFile.BOT_TOKEN;
  const MINIAPP_URL = process.env.MINIAPP_URL || envFromFile.MINIAPP_URL;

  if (!BOT_TOKEN || !MINIAPP_URL) {
    console.error('Missing BOT_TOKEN or MINIAPP_URL');
    process.exit(1);
  }

  try {
    await callTelegram(BOT_TOKEN, 'setChatMenuButton', {
      menu_button: {
        type: 'web_app',
        text: 'Canvas',
        web_app: { url: MINIAPP_URL },
      },
    });
    console.log('Menu button configured.');

    await callTelegram(BOT_TOKEN, 'setMyCommands', {
      commands: [
        { command: 'canvas', description: 'Open Canvas' },
      ],
    });
    console.log('/canvas command registered.');
  } catch (err) {
    console.error(err.message || String(err));
    process.exit(1);
  }
}

main();
