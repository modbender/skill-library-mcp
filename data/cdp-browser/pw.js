const playwright = require('playwright');
const fs = require('fs');
const path = require('path');

function validateHttpUrl(input) {
  if (!input || typeof input !== 'string') throw new Error('Missing url');
  const trimmed = input.trim();
  if (!trimmed) throw new Error('Missing url');

  let parsed;
  try {
    parsed = new URL(trimmed);
  } catch {
    throw new Error(`Invalid URL: ${input}`);
  }

  if (!['http:', 'https:'].includes(parsed.protocol)) {
    throw new Error(`Blocked URL scheme: ${parsed.protocol} (only http/https allowed)`);
  }

  return parsed.toString();
}

(async () => {
  let args = process.argv.slice(2);
  const action = args[0];
  if (!action) {
    console.log('Usage: node pw.js <action> <tabId> [args...]');
    process.exit(1);
  }
  const tabId = args[1];
  if (!tabId) {
    console.error('Missing tabId');
    process.exit(1);
  }

  // Filter --confirm for tweet-post, --save-pending for tweet-draft
  const hasConfirm = args.includes('--confirm');
  const savePending = args.includes('--save-pending');
  args = args.filter(a => a !== '--confirm' && a !== '--save-pending');

  // Fetch tabs to get wsEndpoint
  const tabsResp = await fetch('http://localhost:9222/json/list');
  if (!tabsResp.ok) throw new Error('Browser not available at localhost:9222');
  const tabs = await tabsResp.json();
  const tab = tabs.find(t => t.id === tabId);
  if (!tab) {
    console.error(`Tab ${tabId} not found. Available: ${tabs.map(t=>t.id).join(', ')}`);
    process.exit(1);
  }
  const browser = await playwright.chromium.connectOverCDP('http://localhost:9222');
  const allPages = browser.contexts().flatMap(c => c.pages());
  const tabIndex = tabs.filter(t => t.type === 'page').findIndex(t => t.id === tabId);
  const page = tabIndex >= 0 ? allPages[tabIndex] : allPages.find(p => p.url() === tab.url) || allPages[0];
  if (!page) throw new Error(`Could not find page for tab ${tabId}`);

  try {
    switch (action) {
      case 'snapshot':
        const safeId = String(tabId).replace(/[^A-Za-z0-9_-]/g, '');
        const pngPath = path.join(__dirname, `snapshot-${safeId}.png`);
        await page.screenshot({ path: pngPath, fullPage: true });
        console.log(`Snapshot saved: ${pngPath}`);
        break;
      case 'goto': {
        const safeUrl = validateHttpUrl(args[2]);
        await page.goto(safeUrl, { waitUntil: 'networkidle' });
        console.log(`Navigated to ${safeUrl}`);
        break;
      }
      case 'close-popup':
        await page.evaluate(() => {
          Array.from(document.querySelectorAll('[role="dialog"], .modal, .popup, [role="dialogue"]')).forEach(el => {
            el.remove?.() || (el.style.display = 'none');
            el.style.visibility = 'hidden';
          });
        });
        console.log('Popups closed');
        break;
      case 'scroll':
        const target = args[2];
        const dir = args[3] || 'down';
        const amount = parseInt(target, 10);
        if (!isNaN(amount) && amount >= 0 && amount <= 1e7) {
          const delta = dir === 'up' ? -amount : amount;
          await page.evaluate((d) => window.scrollBy(0, d), delta);
        } else {
          await page.evaluate((sel) => document.querySelector(sel)?.scrollIntoView({ block: 'center' }), target);
        }
        console.log(`Scrolled ${target} ${dir}`);
        break;
      case 'query': {
        const op = args[2];
        const selector = args[3] || null;
        if (!op) throw new Error('Usage: query <tabId> getText|getHtml|getUrl [selector]');
        const result = await page.evaluate(([o, sel]) => {
          if (o === 'getUrl') return location.href;
          const el = sel ? document.querySelector(sel) : document.body;
          if (!el) return null;
          if (o === 'getText') return el.innerText ?? null;
          if (o === 'getHtml') return el.innerHTML ?? null;
          return null;
        }, [op, selector]);
        console.log(result ?? '');
        break;
      }
      case 'tweet-draft': {
        let draftText = args.slice(2).join(' ');
        if (!draftText) throw new Error('Missing text');
        try {
          await page.click('[data-testid="SideNav_NewTweet_Button"], a[href="/compose/post"], [aria-label*="Post"]', { timeout: 3000 });
        } catch (e) {
          console.log('Compose launcher not found, trying goto');
          await page.goto('https://x.com/compose/post');
        }
        await page.waitForSelector('div[role="textbox"][contenteditable="true"], div[data-testid="tweetTextarea_0"]', { timeout: 10000 });
        await page.fill('div[role="textbox"][contenteditable="true"]', draftText);
        if (savePending) {
          const workspace = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME || process.env.USERPROFILE || '.', '.openclaw', 'workspace');
          const pendingDir = path.join(workspace, '.cdp-browser');
          const pendingPath = path.join(pendingDir, 'pending-tweet.json');
          try {
            if (!fs.existsSync(pendingDir)) fs.mkdirSync(pendingDir, { recursive: true });
            fs.writeFileSync(pendingPath, JSON.stringify({ text: draftText, tabId, timestamp: Date.now() }, null, 2));
            console.log(`Pending state saved: ${pendingPath}`);
          } catch (e) {
            console.error('Could not save pending state:', e.message);
          }
        }
        console.log(`Draft filled (not posted): ${draftText}`);
        break;
      }
      case 'tweet-post': {
        if (!hasConfirm) throw new Error('tweet-post requires --confirm flag');
        let postText = args.slice(2).join(' ');
        if (!postText) throw new Error('Missing text');
        try {
          await page.click('[data-testid="SideNav_NewTweet_Button"], a[href="/compose/post"], [aria-label*="Post"]', { timeout: 3000 });
        } catch (e) {
          console.log('Compose launcher not found, trying goto');
          await page.goto('https://x.com/compose/post');
        }
        await page.waitForSelector('div[role="textbox"][contenteditable="true"], div[data-testid="tweetTextarea_0"]', { timeout: 10000 });
        await page.fill('div[role="textbox"][contenteditable="true"]', postText);
        await page.click('[data-testid="tweetButton"], [data-testid="tweetButtonInline"]');
        console.log(`Tweet posted: ${postText}`);
        break;
      }
      case 'tweet':
        // Legacy: treat as tweet-draft (safe default)
        let text = args.slice(2).join(' ');
        if (!text) throw new Error('Missing text');
        try {
          await page.click('[data-testid="tweetButtonInline"], [aria-label*="Tweet"], [data-testid="SideNav_NewTweet_Button"]', { timeout: 3000 });
        } catch (e) {
          console.log('Compose button not found, trying goto');
          await page.goto('https://x.com/compose/post');
        }
        await page.waitForSelector('div[role="textbox"][contenteditable="true"], div[data-testid="tweetTextarea_0"]', { timeout: 10000 });
        await page.fill('div[role="textbox"][contenteditable="true"]', text);
        console.log(`Draft filled (not posted). Use tweet-post --confirm to post.`);
        break;
      default:
        throw new Error(`Unknown action: ${action}`);
    }
  } finally {
    await browser.close();
  }
})().catch(err => {
  console.error(err.message || err);
  process.exit(1);
});
