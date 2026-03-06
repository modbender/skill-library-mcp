#!/usr/bin/env node
/**
 * TelTel SMS sender
 *
 * Usage:
 *   node send_sms.js --to "+3712xxxxxxx" --message "Hi" --from "37163030348" [--callback "https://..."] [--apikey "..."] [--dry-run]
 *
 * Env:
 *   TELTEL_API_KEY (preferred)
 *   TELTEL_SMS_FROM (optional default)
 */

const BASE_URL = process.env.TELTEL_BASE_URL || 'https://api.teltel.io/v2';

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) continue;
    const key = a.slice(2);
    if (key === 'dry-run') { out.dryRun = true; continue; }
    const val = argv[i + 1];
    i++;
    out[key] = val;
  }
  return out;
}

function requireField(obj, name) {
  if (!obj[name] || String(obj[name]).trim() === '') {
    console.error(`Missing required --${name}`);
    process.exit(2);
  }
}

async function main() {
  const args = parseArgs(process.argv);

  const apiKey = args.apikey || process.env.TELTEL_API_KEY;
  if (!apiKey && !args.dryRun) {
    console.error('Missing TELTEL_API_KEY (env) or --apikey');
    process.exit(2);
  }

  const from = (args.from || process.env.TELTEL_SMS_FROM || '').replace(/^\+/, '');
  const to = (args.to || '').trim();
  const message = args.message;
  const callback = args.callback;

  requireField({ to }, 'to');
  requireField({ message }, 'message');
  if (!from) {
    console.error('Missing --from (or TELTEL_SMS_FROM env).');
    process.exit(2);
  }

  const payload = {
    data: {
      from,
      to,
      message,
      ...(callback ? { callback } : {})
    }
  };

  const url = `${BASE_URL}/sms/text`;

  if (args.dryRun) {
    console.log(JSON.stringify({ url, payload }, null, 2));
    return;
  }

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': apiKey,
    },
    body: JSON.stringify(payload),
  });

  const text = await res.text();
  let json;
  try { json = JSON.parse(text); } catch { json = null; }

  if (!res.ok) {
    console.error(`TelTel API error: HTTP ${res.status}`);
    console.error(text);
    process.exit(1);
  }

  console.log(JSON.stringify(json ?? { raw: text }, null, 2));
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
