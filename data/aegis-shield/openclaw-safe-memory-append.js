#!/usr/bin/env node
/**
 * openclaw-safe-memory-append
 *
 * Level 1 memory guardrail: scan + lint + sanitize before writing to memory.
 *
 * Local-only v0.1: uses local aegis-shield library (no network).
 */

const fs = require('fs');
const path = require('path');

function die(msg, code = 2) {
  process.stderr.write(msg + '\n');
  process.exit(code);
}

function nowUtcISO() {
  return new Date().toISOString();
}

function todayUTC() {
  const d = new Date();
  const yyyy = d.getUTCFullYear();
  const mm = String(d.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(d.getUTCDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (c) => (data += c));
    process.stdin.on('end', () => resolve(data));
  });
}

function lint(text) {
  const findings = [];

  const imperative = /(\balways\b|\bnever\b|\bmust\b|\bignore\b|\bdo not\b|\boverride\b|\bbypass\b|\bfrom now on\b)/i;
  if (imperative.test(text)) findings.push('imperative-language');

  const toolish = /(\b(curl|wget|rm -rf|chmod|chown|sudo|systemctl|bash -c|sh -c)\b)/i;
  if (toolish.test(text)) findings.push('tool-directive');

  const secretish = /(\btoken\b|\bapi[_ -]?key\b|\bsecret\b|\bnsec\b|\bprivate key\b|\baccess_token\b)/i;
  if (secretish.test(text)) findings.push('secret-risk');

  const authority = /(DJ said|official policy|as per system|system instruction|developer message)/i;
  if (authority.test(text)) findings.push('authority-laundering');

  return findings;
}

function sanitizeToDeclarative(text) {
  // v0.1: conservative. Strip excess whitespace; do not attempt heavy rewriting.
  // Keep as a single paragraph summary marker.
  const t = text.replace(/\r\n/g, '\n').trim();
  // Collapse very long blocks a bit.
  return t.length > 800 ? (t.slice(0, 800) + '…') : t;
}

async function main() {
  const args = process.argv.slice(2);

  const getArg = (name) => {
    const idx = args.indexOf(`--${name}`);
    if (idx === -1) return null;
    return args[idx + 1] ?? '';
  };

  const textArg = getArg('text');
  const source = getArg('source');
  const target = getArg('target') || 'daily'; // daily|longterm
  const tags = (getArg('tags') || '').split(',').map(s => s.trim()).filter(Boolean);
  const allowIf = (getArg('allowIf') || 'medium').toLowerCase();

  if (!source) die('Missing --source (required).');

  const text = (textArg != null && textArg !== '') ? textArg : (await readStdin());
  if (!text || !text.trim()) die('No text provided. Use --text or pipe stdin.');

  // Load scanner (local)
  let scan;
  try {
    ({ scan } = require('/home/openclaw/.openclaw/workspace/aegis-shield/dist/index.js'));
  } catch (e) {
    die('Failed to load aegis-shield local library. Is /home/openclaw/.openclaw/workspace/aegis-shield built?', 3);
  }

  const scanRes = scan(text);
  const severity = (scanRes && scanRes.severity) || 'unknown';
  const score = (scanRes && typeof scanRes.score === 'number') ? scanRes.score : null;
  const reasons = (scanRes && Array.isArray(scanRes.matches)) ? scanRes.matches : [];

  const lintFindings = lint(text);

  const sevRank = { none:0, info:0, low:1, medium:2, high:3, critical:4, unknown:99 };
  const thresholdRank = { low:1, medium:2, high:3, critical:4 };

  const shouldQuarantine = (sevRank[severity] ?? 99) >= (thresholdRank[allowIf] ?? 2) || lintFindings.length > 0;

  const wsRoot = '/home/openclaw/.openclaw/workspace';
  const memDir = path.join(wsRoot, 'memory');
  const quarantineDir = path.join(memDir, 'quarantine');

  if (!fs.existsSync(memDir)) fs.mkdirSync(memDir, { recursive: true });
  if (!fs.existsSync(quarantineDir)) fs.mkdirSync(quarantineDir, { recursive: true, mode: 0o700 });

  const day = todayUTC();

  const sanitized = sanitizeToDeclarative(text);
  const tagStr = tags.length ? ` [${tags.join(', ')}]` : '';

  const entry = `- [${nowUtcISO()}]${tagStr} ${sanitized}\n  Source: ${source}\n`;

  if (shouldQuarantine) {
    const qPath = path.join(quarantineDir, `${day}.md`);
    const block = [
      `\n## Quarantine — ${nowUtcISO()}\n`,
      `Source: ${source}\n`,
      `Scan: severity=${severity} score=${score}\n`,
      `Scan reasons: ${reasons.length ? reasons.join(', ') : '(none)'}\n`,
      `Lint findings: ${lintFindings.length ? lintFindings.join(', ') : '(none)'}\n`,
      `\nOriginal text:\n\n`,
      '```\n' + text.trim() + '\n```\n',
      `\nSuggested sanitized entry:\n\n`,
      entry,
      `\nPromotion checklist: confirm safe + declarative + sourced.\n`
    ].join('');

    fs.appendFileSync(qPath, block, 'utf8');
    process.stdout.write(JSON.stringify({
      status: 'quarantined', severity, score, reasons, lintFindings,
      quarantine_to: qPath,
      sanitized_entry: entry
    }, null, 2) + '\n');
    return;
  }

  let outPath;
  if (target === 'longterm') {
    outPath = path.join(wsRoot, 'MEMORY.md');
  } else {
    outPath = path.join(memDir, `${day}.md`);
  }

  fs.appendFileSync(outPath, entry, 'utf8');

  process.stdout.write(JSON.stringify({
    status: 'accepted', severity, score, reasons, lintFindings,
    written_to: outPath,
    sanitized_entry: entry
  }, null, 2) + '\n');
}

main().catch((e) => die(String(e && e.stack || e), 1));
