#!/usr/bin/env node
/**
 * Pinterest Publish Script (Playwright)
 * Usage: node publish-pinterest.js <image-path> <title> <description> [board-name]
 * 
 * Connects to OpenClaw's managed browser via CDP.
 * Requires: Pinterest session already logged in.
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const { humanDelay, humanClick, humanType, humanThink, humanBrowse, humanScroll } = require('./utils/human-like');

function discoverCdpUrl() {
  try {
    const ps = execSync("ps aux | grep 'remote-debugging-port=' | grep -v grep", { encoding: 'utf8', timeout: 3000 });
    const match = ps.match(/remote-debugging-port=(\d+)/);
    if (match) return `http://127.0.0.1:${match[1]}`;
  } catch {}
  if (process.env.CDP_PORT) return `http://127.0.0.1:${process.env.CDP_PORT}`;
  for (const port of [18800, 9222, 9229]) {
    try {
      execSync(`curl -s --max-time 1 http://127.0.0.1:${port}/json/version`, { encoding: 'utf8', timeout: 2000 });
      return `http://127.0.0.1:${port}`;
    } catch {}
  }
  throw new Error('CDP port not found');
}

async function main() {
  const [,, imagePath, title, description, boardName] = process.argv;
  if (!imagePath || !title) {
    console.error('Usage: node publish-pinterest.js <image> <title> [description] [board]');
    process.exit(1);
  }

  const desc = description || title;
  const board = boardName || 'Abstract Digital Art';

  console.log(`[PIN] Publishing: "${title}"`);
  console.log(`[PIN] Image: ${imagePath}`);

  let browser;
  try {
    browser = await chromium.connectOverCDP(discoverCdpUrl());
  } catch (e) {
    console.error('[PIN] Cannot connect to CDP. Is OpenClaw browser running?');
    process.exit(1);
  }

  const context = browser.contexts()[0];
  const page = await context.newPage();

  try {
    await page.goto('https://www.pinterest.com/pin-creation-tool/', { waitUntil: 'networkidle', timeout: 30000 });
    await humanDelay(2000, 4000);

    // 1. Upload image via file input
    const fileInput = await page.waitForSelector('#storyboard-upload-input, input[type="file"]', { timeout: 10000 });
    await fileInput.setInputFiles(imagePath);
    console.log('[PIN] Image uploaded');
    await humanDelay(3000, 6000);

    // 2. Fill title
    await humanThink(800, 2000);
    const titleInput = await page.waitForSelector('input[placeholder*="标题" i]:not([disabled]), input[placeholder*="title" i]:not([disabled])', { timeout: 10000 }).catch(() => null);
    if (titleInput) {
      await humanClick(page, titleInput);
      await page.keyboard.down('Meta');
      await page.keyboard.press('a');
      await page.keyboard.up('Meta');
      await humanDelay(100, 300);
      await humanType(page, null, title, { minDelay: 50, maxDelay: 160 });
      console.log(`[PIN] Title: ${title}`);
    } else {
      console.log('[PIN] WARN: title input not found');
    }

    // 3. Fill description (Draft.js editor)
    await humanThink(500, 1500);
    const descEditor = await page.waitForSelector('.public-DraftEditor-content', { timeout: 5000 }).catch(() => null);
    if (descEditor) {
      await humanClick(page, descEditor);
      await humanDelay(200, 500);
      await humanType(page, null, desc, { minDelay: 40, maxDelay: 130 });
      console.log('[PIN] Description set');
    } else {
      console.log('[PIN] WARN: description editor not found');
    }

    // 4. Select board - click the board dropdown
    const boardBtn = await page.evaluate(() => {
      // Find button containing "选择一块图板" or "Select board" or the board dropdown
      const btns = [...document.querySelectorAll('button')];
      const b = btns.find(b => b.textContent.includes('选择一块图板') || b.textContent.includes('Select board') || b.textContent.includes('Abstract Digital Art'));
      if (b) { b.click(); return b.textContent.trim().substring(0, 50); }
      return null;
    });
    if (boardBtn) {
      console.log(`[PIN] Board dropdown clicked: "${boardBtn}"`);
      await humanDelay(1000, 2500);

      const searchInput = await page.waitForSelector('input[placeholder*="搜索" i], input[placeholder*="search" i]', { timeout: 3000 }).catch(() => null);
      if (searchInput) {
        await humanType(page, searchInput, board, { minDelay: 50, maxDelay: 140 });
        await humanDelay(1000, 2000);
      }

      // Click matching board item
      const clicked = await page.evaluate((boardName) => {
        const items = document.querySelectorAll('[role="option"], [role="listbox"] [role="button"], [data-test-id*="board"]');
        for (const item of items) {
          if (item.textContent.includes(boardName)) {
            item.click();
            return item.textContent.trim().substring(0, 50);
          }
        }
        // Fallback: any clickable element with board name
        const all = [...document.querySelectorAll('div, span, button')];
        const match = all.find(el => el.textContent.trim() === boardName && el.offsetParent !== null);
        if (match) { match.click(); return match.textContent.trim(); }
        return null;
      }, board);

      if (clicked) {
        console.log(`[PIN] Board selected: ${clicked}`);
      } else {
        console.log('[PIN] WARN: board not found in dropdown');
      }
      await humanDelay(800, 1500);
    } else {
      console.log('[PIN] WARN: board dropdown not found');
    }

    // 5. Click publish button
    await humanThink(800, 2000);
    const published = await page.evaluate(() => {
      const btns = [...document.querySelectorAll('button')];
      const pub = btns.find(b => {
        const text = b.textContent.trim();
        return (text === '发布' || text === 'Publish') && !b.disabled && b.offsetParent !== null;
      });
      if (pub) {
        pub.click();
        return true;
      }
      return false;
    });

    if (published) {
      console.log('[PIN] Publish button clicked');
    } else {
      console.error('[PIN] ERROR: Publish button not found or disabled');
      await page.screenshot({ path: '/tmp/pinterest-no-publish-btn.png' }).catch(() => {});
      process.exit(1);
    }

    // 6. Wait and verify
    await humanDelay(4000, 7000);

    // Check if we got redirected or if there's a success state
    const url = page.url();
    console.log(`[PIN] Final URL: ${url}`);

    // Check if pin was created by looking at the page
    const result = await page.evaluate(() => {
      // Check for error messages
      const err = document.querySelector('[data-test-id*="error"], [class*="error"]');
      if (err && err.textContent.trim()) return { error: err.textContent.trim().substring(0, 100) };
      return { ok: true };
    });

    if (result.error) {
      console.error(`[PIN] ERROR: ${result.error}`);
      process.exit(1);
    }

    console.log('[PIN] SUCCESS');

  } catch (err) {
    console.error(`[PIN] Error: ${err.message}`);
    await page.screenshot({ path: '/tmp/pinterest-publish-error.png' }).catch(() => {});
    process.exit(1);
  } finally {
    await page.close();
  }
}

main();
