#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';

const url = process.argv[2];
if (!url) {
  console.error('ERROR=MISSING_URL');
  process.exit(2);
}
if (!/^https?:\/\/(www\.)?instagram\.com\/(reel|reels)\//i.test(url)) {
  console.error('ERROR=INVALID_URL');
  process.exit(3);
}

const WORKSPACE_ROOT = process.env.OPENCLAW_WORKSPACE || process.cwd();
const OUT_DIR = process.env.REEL_DOWNLOAD_DIR
  ? path.resolve(process.env.REEL_DOWNLOAD_DIR)
  : path.resolve(WORKSPACE_ROOT, 'downloads');
fs.mkdirSync(OUT_DIR, { recursive: true });

const executablePath = process.env.BROWSER_EXECUTABLE_PATH || '/usr/bin/brave-browser';
if (!fs.existsSync(executablePath)) {
  console.error(`ERROR=BROWSER_NOT_FOUND:${executablePath}`);
  process.exit(4);
}

const browser = await chromium.launch({
  executablePath,
  headless: true,
  args: ['--no-sandbox', '--disable-dev-shm-usage']
});

const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  acceptDownloads: true,
});

const page = await context.newPage();

try {
  await page.goto('https://sssinstagram.com/reels-downloader', { waitUntil: 'domcontentloaded', timeout: 60000 });

  const inputSelectors = [
    '#input',
    'input.form__input',
    'input[type="text"]',
    'input[type="url"]',
    'input[placeholder*="Paste" i]',
    'input[placeholder*="Instagram" i]',
    'input[name*="url" i]',
    'input[id*="url" i]',
  ];

  let inputFound = false;
  for (const sel of inputSelectors) {
    const el = page.locator(sel).first();
    if (await el.count()) {
      await el.fill(url);
      inputFound = true;
      break;
    }
  }
  if (!inputFound) {
    throw new Error('INPUT_NOT_FOUND');
  }

  const submitSelectors = [
    'button:has-text("Download")',
    'button:has-text("Get")',
    'input[type="submit"]',
    'button[type="submit"]',
  ];

  let clicked = false;
  for (const sel of submitSelectors) {
    const btn = page.locator(sel).first();
    if (await btn.count()) {
      await btn.click({ timeout: 10000 });
      clicked = true;
      break;
    }
  }
  if (!clicked) throw new Error('SUBMIT_NOT_FOUND');

  await page.waitForTimeout(3000);

  const directLinkCandidates = page.locator('a[href*="cdn"], a[href*=".mp4"], a:has-text("Download")');
  const candidateCount = await directLinkCandidates.count();

  let mediaPath = '';
  if (candidateCount > 0) {
    for (let i = 0; i < candidateCount; i++) {
      const a = directLinkCandidates.nth(i);
      const href = await a.getAttribute('href');
      if (!href) continue;
      if (!href.startsWith('http')) continue;

      const filename = `reel-${Date.now()}-${i}.mp4`;
      const outFile = path.join(OUT_DIR, filename);

      const resp = await fetch(href, {
        headers: {
          'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
          'referer': 'https://www.instagram.com/'
        }
      });
      if (!resp.ok) continue;
      const ctype = (resp.headers.get('content-type') || '').toLowerCase();
      const ab = await resp.arrayBuffer();
      const body = Buffer.from(ab);
      if (!body || body.length < 20_000) continue;
      if (!(ctype.includes('video') || href.includes('.mp4'))) continue;

      fs.writeFileSync(outFile, body);
      mediaPath = outFile;
      break;
    }
  }

  if (!mediaPath) {
    const dl = page.locator('a:has-text("Download")').first();
    if (await dl.count()) {
      const [download] = await Promise.all([
        page.waitForEvent('download', { timeout: 30000 }).catch(() => null),
        dl.click().catch(() => null),
      ]);
      if (download) {
        const suggested = download.suggestedFilename() || `reel-${Date.now()}.mp4`;
        const outFile = path.join(OUT_DIR, suggested.replace(/[^a-zA-Z0-9._-]/g, '_'));
        await download.saveAs(outFile);
        mediaPath = outFile;
      }
    }
  }

  if (!mediaPath || !fs.existsSync(mediaPath)) {
    throw new Error('DOWNLOAD_FAILED');
  }

  const ext = path.extname(mediaPath).toLowerCase();
  const stat = fs.statSync(mediaPath);
  if (!['.mp4', '.mov', '.mkv', '.webm'].includes(ext) || stat.size < 20_000) {
    throw new Error('NOT_A_VALID_VIDEO');
  }

  console.log(`MEDIA_PATH=${mediaPath}`);
} catch (err) {
  console.error(`ERROR=${err.message || 'UNKNOWN'}`);
  process.exit(5);
} finally {
  await context.close();
  await browser.close();
}
