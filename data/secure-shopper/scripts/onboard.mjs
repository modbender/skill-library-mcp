#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';

const SKILL_DIR = path.resolve(new URL('.', import.meta.url).pathname, '..');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');

function usage(msg) {
  if (msg) console.error(msg);
  console.error(`\nUsage:
  node scripts/onboard.mjs \
    --sites 'Amazon=https://www.amazon.com|Walmart=https://www.walmart.com' \
    --zip 46202 \
    --address "optional" \
    --priority relevancy|cheaper|faster|reviews \
    --notes "optional"\n`);
  process.exit(2);
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) continue;
    const k = a.slice(2);
    const v = argv[i + 1];
    if (v == null || v.startsWith('--')) usage(`Missing value for --${k}`);
    out[k] = v;
    i++;
  }
  return out;
}

function parseSites(sitesStr) {
  if (!sitesStr) return [];
  // Format: Name=url|Name=url
  return sitesStr.split('|').map(pair => {
    const [name, baseUrl] = pair.split('=');
    if (!name || !baseUrl) throw new Error(`Bad --sites entry: ${pair}`);
    return {
      name: name.trim(),
      baseUrl: baseUrl.trim(),
      loginUrl: '',
      enabled: true,
      notes: ''
    };
  });
}

const args = parseArgs(process.argv.slice(2));

try {
  const existing = JSON.parse(await fs.readFile(CONFIG_PATH, 'utf8'));

  const goToSites = args.sites ? parseSites(args.sites) : existing.goToSites;
  const zip = args.zip ?? existing.location?.zip ?? '';
  const address = args.address ?? existing.location?.address ?? '';
  const priority = args.priority ?? existing.preferences?.priority ?? 'relevancy';
  const notes = args.notes ?? existing.preferences?.notes ?? '';

  const next = {
    goToSites,
    location: { zip, address },
    preferences: {
      priority,
      maxCandidatesPerSite: existing.preferences?.maxCandidatesPerSite ?? 5,
      notes
    }
  };

  await fs.writeFile(CONFIG_PATH, JSON.stringify(next, null, 2) + '\n', 'utf8');
  console.log(`Wrote ${CONFIG_PATH}`);
} catch (err) {
  console.error(err?.stack || String(err));
  process.exit(1);
}
