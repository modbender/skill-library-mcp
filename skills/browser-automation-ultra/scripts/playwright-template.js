#!/usr/bin/env node
/**
 * Playwright Script Template — Browser Automation Ultra
 *
 * Usage: ./scripts/browser-lock.sh run scripts/browser/<name>.js [args]
 *
 * Rules:
 * - NEVER browser.close() — kills entire Chrome
 * - ALWAYS page.close() in finally block
 * - ALWAYS process.exit(0) at end (Playwright keeps event loop)
 * - ALWAYS use human-like functions for all interactions
 * - NEVER use fixed delays, fill(), or element.click()
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const {
  humanDelay,
  humanThink,
  humanClick,
  humanType,
  humanFillContentEditable,
  humanBrowse,
  humanScroll,
  jitterWait,
} = require('./utils/human-like');

// ─── CDP Discovery ───
function discoverCdpUrl() {
  try {
    const ps = execSync("ps aux | grep 'remote-debugging-port' | grep -v grep", { encoding: 'utf8' });
    const match = ps.match(/remote-debugging-port=(\d+)/);
    return `http://127.0.0.1:${match ? match[1] : '18800'}`;
  } catch {
    return 'http://127.0.0.1:18800';
  }
}

// ─── Helpers ───
function log(msg) { console.log(`[TASK] ${msg}`); }
function err(msg) { console.error(`[ERROR] ${msg}`); }

// ─── Main ───
async function main() {
  // Parse CLI args as needed
  // const [arg1, arg2] = process.argv.slice(2);

  let browser;
  try {
    browser = await chromium.connectOverCDP(discoverCdpUrl());
  } catch (e) {
    err('Cannot connect to CDP. Is Chrome running?');
    process.exit(1);
  }

  const context = browser.contexts()[0];
  const page = await context.newPage();

  try {
    // ===== Your automation here =====

    // 1. Navigate
    await page.goto('https://example.com', { waitUntil: 'networkidle', timeout: 30000 });
    await humanDelay(2000, 4000);
    log('Page loaded');

    // 2. Browse (simulate human reading the page)
    await humanBrowse(page);

    // 3. Interact
    await humanThink(800, 2000);
    await humanType(page, 'input[name="title"]', 'My Title');
    await humanClick(page, 'button[type="submit"]');

    // 4. Wait for result
    await humanDelay(3000, 6000);
    log('Done');

  } catch (error) {
    err(error.message);
    await page.screenshot({ path: '/tmp/task-error.png' }).catch(() => {});
    process.exit(1);
  } finally {
    await page.close();
  }
}

main().then(() => process.exit(0)).catch(e => { err(e.message); process.exit(1); });
