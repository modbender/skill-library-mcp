#!/usr/bin/env node
/**
 * TelTel bulk SMS sender
 *
 * Usage:
 *   node send_sms_bulk.js --to "+3712..., +3712..." --message "Hi" --from "37163030348" [--callback "https://..."] [--apikey "..."] [--dry-run]
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

function splitToList(s) {
  return String(s || '')
    .split(/[\n,;]+/)
    .map(x => x.trim())
    .filter(Boolean);
}

async function main() {
  const args = parseArgs(process.argv);
  const apiKey = args.apikey || process.env.TELTEL_API_KEY;
  if (!apiKey && !args.dryRun) {
    console.error('Missing TELTEL_API_KEY (env) or --apikey');
    process.exit(2);
  }

  const from = (args.from || process.env.TELTEL_SMS_FROM || '').replace(/^\+/, '');
  const toList = splitToList(args.to);
  const message = args.message;
  const callback = args.callback;

  if (!from) {
    console.error('Missing --from (or TELTEL_SMS_FROM env).');
    process.exit(2);
  }
  if (!toList.length) {
    console.error('Missing --to (comma/newline separated list).');
    process.exit(2);
  }
  if (!message) {
    console.error('Missing --message');
    process.exit(2);
  }

  const payload = {
    data: {
      from,
      to: toList,
      message,
      ...(callback ? { callback } : {})
    }
  };

  const url = `${BASE_URL}/sms/bulk/text`;

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
