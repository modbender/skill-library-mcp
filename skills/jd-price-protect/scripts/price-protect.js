#!/usr/bin/env node
// JD Price Protection - Click all "申请价保" buttons via CDP
const { createHmac } = require('crypto');
const { readFileSync } = require('fs');
const { join } = require('path');

const RELAY_CONTEXT = 'openclaw-extension-relay-v1';
const HOME = process.env.HOME || process.env.USERPROFILE;

function getGatewayToken() {
  const cfg = JSON.parse(readFileSync(join(HOME, '.openclaw/openclaw.json'), 'utf8'));
  return cfg.gateway?.auth?.token;
}

function deriveRelayToken(gatewayToken, port) {
  return createHmac('sha256', gatewayToken).update(`${RELAY_CONTEXT}:${port}`).digest('hex');
}

function findPlaywright() {
  const paths = [
    'playwright-core',
    join(HOME, '.nvm/versions/node', process.version, 'lib/node_modules/openclaw/node_modules/playwright-core'),
  ];
  for (const p of paths) { try { return require(p); } catch {} }
  throw new Error('playwright-core not found');
}

async function run() {
  const port = parseInt(process.env.RELAY_PORT || '18792');
  const gwToken = process.env.GATEWAY_TOKEN || getGatewayToken();
  if (!gwToken) throw new Error('No gateway token found');

  const relayToken = deriveRelayToken(gwToken, port);
  const { chromium } = findPlaywright();

  const browser = await chromium.connectOverCDP(`ws://127.0.0.1:${port}/cdp`, {
    headers: { 'x-openclaw-relay-token': relayToken }, timeout: 5000
  });

  const page = browser.contexts().flatMap(c => c.pages())
    .find(p => p.url().includes('pcsitepp-fm.jd.com'));

  if (!page) {
    // Try navigating any available page
    const anyPage = browser.contexts().flatMap(c => c.pages())[0];
    if (anyPage) {
      await anyPage.goto('https://pcsitepp-fm.jd.com/', { waitUntil: 'networkidle', timeout: 15000 });
      return run_on_page(anyPage, browser);
    }
    throw new Error('No browser page available. Ensure Chrome relay is connected.');
  }

  return run_on_page(page, browser);
}

async function clickAllButtons(page) {
  const btns = page.getByText('申请价保', { exact: true });
  const count = await btns.count();
  let clicked = 0;
  for (let i = 0; i < count; i++) {
    try {
      await btns.nth(i).scrollIntoViewIfNeeded({ timeout: 2000 });
      await page.waitForTimeout(300);
      await btns.nth(i).click({ timeout: 3000, force: true });
      clicked++;
      await page.waitForTimeout(2500);
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    } catch { /* skip non-clickable */ }
  }
  return { count, clicked };
}

async function collectResults(page) {
  const items = [];
  const rows = await page.locator('#dataList tr').all();
  for (const row of rows) {
    const text = await row.innerText().catch(() => '');
    if (!text.includes('￥')) continue;
    const name = text.split('\n')[0].substring(0, 40);
    if (text.includes('价保成功')) {
      const m = text.match(/金额：([\d.]+)/);
      items.push({ name, type: 'success', amount: m ? m[1] : '?' });
    } else if (text.includes('价保失败') || text.includes('无差价')) {
      items.push({ name, type: 'failed', reason: text.includes('无差价') ? '无差价' : '失败' });
    }
  }
  return items;
}

async function hasNextPage(page) {
  const next = page.locator('.page-next:not(.disabled), a:has-text("下一页"):not(.disabled)');
  return (await next.count()) > 0 ? next.first() : null;
}

async function run_on_page(page, browser) {
  if (!page.url().includes('pcsitepp-fm.jd.com')) {
    await page.goto('https://pcsitepp-fm.jd.com/', { waitUntil: 'networkidle', timeout: 15000 });
  }
  await page.waitForTimeout(2000);

  const results = { total: 0, clicked: 0, pages: 0, success: [], failed: [] };
  const MAX_PAGES = 20; // safety limit

  for (let pg = 0; pg < MAX_PAGES; pg++) {
    results.pages++;
    const { count, clicked } = await clickAllButtons(page);
    results.total += count;
    results.clicked += clicked;

    // Check for next page before reload
    const nextBtn = await hasNextPage(page);
    
    // Reload current page to get results
    await page.reload({ waitUntil: 'networkidle', timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);

    const items = await collectResults(page);
    for (const item of items) {
      if (item.type === 'success') results.success.push({ name: item.name, amount: item.amount });
      else results.failed.push({ name: item.name, reason: item.reason });
    }

    // Navigate to next page
    if (!nextBtn) break;
    const nextAfterReload = await hasNextPage(page);
    if (!nextAfterReload) break;
    try {
      await nextAfterReload.click({ timeout: 3000 });
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(2000);
    } catch { break; }
  }

  await browser.close();
  return results;
}

run().then(r => {
  console.log(JSON.stringify(r, null, 2));
}).catch(e => {
  console.error('ERROR:', e.message);
  process.exit(1);
});
