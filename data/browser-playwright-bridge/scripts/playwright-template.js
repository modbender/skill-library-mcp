/**
 * Playwright script template for OpenClaw browser bridge.
 *
 * Usage:
 *   ./scripts/browser-lock.sh run scripts/my-script.js [args...]
 *
 * Shares cookies/login with OpenClaw browser via same Chrome user-data-dir.
 * No `npx playwright install` needed — connects to existing Chrome via CDP.
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');

/**
 * Discover the CDP URL by inspecting Chrome process args.
 * Falls back to CDP_PORT env var, then probes common ports.
 */
function discoverCdpUrl() {
  // Method 1: extract from running Chrome process
  try {
    const ps = execSync(
      "ps aux | grep 'remote-debugging-port=' | grep -v grep",
      { encoding: 'utf8', timeout: 3000 }
    );
    const match = ps.match(/remote-debugging-port=(\d+)/);
    if (match) return `http://127.0.0.1:${match[1]}`;
  } catch {}

  // Method 2: CDP_PORT env var
  if (process.env.CDP_PORT) {
    return `http://127.0.0.1:${process.env.CDP_PORT}`;
  }

  // Method 3: probe common ports (18800 is typical OpenClaw default)
  for (const port of [18800, 9222, 9229]) {
    try {
      execSync(`curl -s --max-time 1 http://127.0.0.1:${port}/json/version`, {
        encoding: 'utf8', timeout: 2000
      });
      return `http://127.0.0.1:${port}`;
    } catch {}
  }

  throw new Error('CDP port not found. Is Chrome running with --remote-debugging-port?');
}

async function main() {
  let browser;
  try {
    browser = await chromium.connectOverCDP(discoverCdpUrl());
  } catch (e) {
    console.error('❌ Cannot connect to Chrome CDP:', e.message);
    console.error('   Ensure browser-lock.sh acquire was called, or Chrome is running with --remote-debugging-port');
    process.exit(1);
  }

  const context = browser.contexts()[0]; // reuse existing context (cookies!)
  const page = await context.newPage();

  try {
    // ====== Your automation here ======

    await page.goto('https://example.com');
    console.log('Title:', await page.title());

    // ==================================
  } catch (e) {
    console.error('❌ Script error:', e.message);
    throw e;
  } finally {
    await page.close();     // close only your tab
    // NEVER call browser.close() — it kills the entire Chrome
  }
}

main().then(() => process.exit(0)).catch(e => {
  console.error('❌', e.message);
  process.exit(1);
});
