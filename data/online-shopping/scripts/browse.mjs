#!/usr/bin/env node

/**
 * Stealth browser launcher for online shopping.
 * 
 * Usage: xvfb-run --auto-servernum node browse.mjs <url> [--screenshot <path>] [--wait <ms>] [--text]
 * 
 * Opens a URL with Patchright stealth browser, optionally takes a screenshot
 * and/or dumps page text. Uses persistent context for session continuity.
 * 
 * Examples:
 *   xvfb-run --auto-servernum node browse.mjs "https://www.inet.se/hitta?q=NAS+8TB" --screenshot /tmp/results.png --text
 *   xvfb-run --auto-servernum node browse.mjs "https://www.inet.se/kassa" --screenshot /tmp/checkout.png --text --wait 5000
 */

import { createRequire } from 'module';
import { parseArgs } from 'node:util';
import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';

// Auto-detect patchright location
function findPatchright() {
  const candidates = [
    // Relative to OpenClaw install
    execSync('npm root -g 2>/dev/null').toString().trim() + '/openclaw/node_modules/patchright',
    // Common global paths
    process.env.HOME + '/.npm-global/lib/node_modules/openclaw/node_modules/patchright',
    '/usr/local/lib/node_modules/openclaw/node_modules/patchright',
    '/usr/lib/node_modules/openclaw/node_modules/patchright',
    // Direct global install
    execSync('npm root -g 2>/dev/null').toString().trim() + '/patchright',
  ];
  for (const p of candidates) {
    try { if (existsSync(p)) return p; } catch {}
  }
  throw new Error('Patchright not found. Run scripts/setup.sh first.');
}

const require = createRequire(import.meta.url);
const { chromium } = require(findPatchright());

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    screenshot: { type: 'string', short: 's' },
    wait: { type: 'string', short: 'w', default: '5000' },
    text: { type: 'boolean', short: 't', default: false },
    'full-page': { type: 'boolean', default: false },
    'max-chars': { type: 'string', default: '8000' },
  },
});

const url = positionals[0];
if (!url) {
  console.error('Usage: browse.mjs <url> [--screenshot <path>] [--wait <ms>] [--text]');
  process.exit(1);
}

const browser = await chromium.launchPersistentContext('/tmp/patchright-ctx', {
  headless: false,
  viewport: null,
  args: ['--no-sandbox', '--disable-gpu'],
});

const page = browser.pages()[0] || await browser.newPage();
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
await page.waitForTimeout(parseInt(values.wait));

// Close common cookie banners
for (const text of ['Jag förstår', 'Accept all', 'Accept cookies', 'Acceptera']) {
  try {
    const btn = page.locator(`button:has-text("${text}")`);
    if (await btn.isVisible({ timeout: 1000 })) {
      await btn.click();
      await page.waitForTimeout(500);
      break;
    }
  } catch(e) {}
}

console.log(`URL: ${page.url()}`);
console.log(`Title: ${await page.title()}`);

if (values.screenshot) {
  await page.screenshot({ path: values.screenshot, fullPage: values['full-page'] });
  console.log(`Screenshot: ${values.screenshot}`);
}

if (values.text) {
  const maxChars = parseInt(values['max-chars']);
  const content = await page.evaluate((max) => document.body.innerText.substring(0, max), maxChars);
  console.log(`\n--- PAGE TEXT ---\n${content}\n--- END ---`);
}

await browser.close();
