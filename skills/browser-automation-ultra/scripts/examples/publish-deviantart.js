#!/usr/bin/env node
/**
 * DeviantArt Publish Script (Playwright via CDP)
 * Usage: node publish-deviantart.js <image-path> <title> <description> <tags-comma-separated>
 * 
 * Connects to OpenClaw's managed browser.
 * Requires: DA session already logged in.
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const path = require('path');
const { humanDelay, humanClick, humanType, humanThink, humanBrowse, humanScroll } = require('./utils/human-like');

function getCdpUrl() {
  try {
    const ps = execSync("ps aux | grep 'openclaw.*remote-debugging-port' | grep -v grep", { encoding: 'utf8' });
    const match = ps.match(/remote-debugging-port=(\d+)/);
    return `http://127.0.0.1:${match ? match[1] : '18800'}`;
  } catch { return 'http://127.0.0.1:18800'; }
}

function log(msg) { console.log(`[DA] ${msg}`); }
function err(msg) { console.error(`[DA ERROR] ${msg}`); }

async function main() {
  const [,, imagePath, title, description, tagsStr] = process.argv;
  if (!imagePath || !title) {
    err('Usage: node publish-deviantart.js <image> <title> [description] [tags]');
    process.exit(1);
  }

  const absPath = path.resolve(imagePath);
  const tags = (tagsStr || 'digitalart,abstractart').split(',').map(t => t.trim());
  const desc = description || title;

  log(`Publishing: "${title}"`);
  log(`Image: ${absPath}`);
  log(`Tags: ${tags.join(', ')}`);

  let browser;
  try {
    browser = await chromium.connectOverCDP(getCdpUrl());
  } catch (e) {
    err('Cannot connect to CDP. Is OpenClaw browser running?');
    process.exit(1);
  }

  const context = browser.contexts()[0];
  const page = await context.newPage();

  try {
    // ===== 1. Navigate to submit page =====
    await page.goto('https://www.deviantart.com/studio?new=1', { waitUntil: 'networkidle', timeout: 30000 });
    await humanDelay(2000, 4000);
    log('Submit dialog loaded');

    // ===== 2. Upload image =====
    // DA requires clicking "Upload Your Art" first, then file input becomes active
    // Use Promise.all to handle file chooser event
    const [fileChooser] = await Promise.all([
      page.waitForEvent('filechooser', { timeout: 10000 }),
      page.evaluate(() => {
        // Click "Upload Your Art" button
        const btns = [...document.querySelectorAll('button')];
        const uploadBtn = btns.find(b => b.textContent.includes('Upload Your Art'));
        if (uploadBtn) uploadBtn.click();
      })
    ]);
    await fileChooser.setFiles(absPath);
    log('Image uploaded via file chooser');

    // Wait for image processing
    await humanDelay(5000, 8000);

    // ===== 3. Verify upload succeeded =====
    // After upload, form fields should appear. Take screenshot to verify.
    await page.screenshot({ path: '/tmp/da-after-upload.png' });

    // ===== 4. Fill title =====
    await humanThink(800, 2000);
    // Find the title input (has auto-filled filename)
    const titleInputSelector = await page.evaluate(() => {
      const allInputs = document.querySelectorAll('input[type="text"]');
      for (const input of allInputs) {
        if (input.placeholder === 'Search') continue;
        if (input.closest('[role="menu"]')) continue;
        const parent = input.closest('div');
        const hasLabel = parent?.textContent?.includes('Title');
        if (input.value !== '' || hasLabel) {
          // Add a temporary id for targeting
          input.setAttribute('data-da-title', 'true');
          return 'found';
        }
      }
      return 'not_found';
    });

    if (titleInputSelector === 'found') {
      const titleEl = await page.$('input[data-da-title="true"]');
      if (titleEl) {
        await humanClick(page, titleEl);
        await page.keyboard.down('Meta');
        await page.keyboard.press('a');
        await page.keyboard.up('Meta');
        await humanDelay(100, 300);
        await humanType(page, null, title, { minDelay: 40, maxDelay: 150 });
        log(`Title: ${title}`);
      }
    } else {
      log('Title: not_found');
    }

    // ===== 5. Add tags =====
    // Tag input is inside a combobox. Search entire page.
    const tagInputInfo = await page.evaluate(() => {
      const combobox = document.querySelector('[role="combobox"]');
      if (combobox) {
        const input = combobox.querySelector('input');
        if (input) { input.focus(); return `combobox: ${input.className.substring(0, 30)}`; }
      }
      // Fallback: find input near "tag" text
      const allInputs = document.querySelectorAll('input[type="text"]');
      for (const inp of allInputs) {
        if (inp.placeholder === 'Search') continue;
        const parent = inp.closest('div');
        if (parent?.textContent?.includes('tag') || parent?.textContent?.includes('Tag')) {
          inp.focus();
          return `near-tag: ${inp.className.substring(0, 30)}`;
        }
      }
      return 'not_found';
    });
    log(`Tag input: ${tagInputInfo}`);

    if (!tagInputInfo.includes('not_found')) {
      const existingTags = await page.evaluate(() => {
        const chips = document.querySelectorAll('[class*="tag"] [class*="chip"], [class*="tag"] button');
        return [...chips].map(c => c.textContent.replace('✕', '').trim().toLowerCase()).filter(t => t);
      });
      log(`Existing tags: ${existingTags.join(', ') || 'none'}`);

      for (const tag of tags) {
        if (existingTags.includes(tag.toLowerCase())) {
          log(`  Skipping duplicate tag: ${tag}`);
          continue;
        }
        await page.evaluate(() => {
          const combobox = document.querySelector('[role="combobox"]');
          if (combobox) { const input = combobox.querySelector('input'); if (input) input.focus(); }
        });
        await humanDelay(200, 500);
        await humanType(page, null, tag, { minDelay: 40, maxDelay: 120, typoRate: 0.02 });
        await page.keyboard.press('Enter');
        await humanDelay(300, 800);
      }
      log(`Tags typed: ${tags.join(', ')}`);
    }

    // ===== 6. Fill description =====
    await humanThink(500, 1500);
    // Find the contenteditable for description and mark it
    const descFound = await page.evaluate(() => {
      const editables = document.querySelectorAll('[contenteditable="true"]');
      for (const ed of editables) {
        if (ed.offsetHeight < 50) continue;
        ed.setAttribute('data-da-desc', 'true');
        return true;
      }
      return false;
    });
    if (descFound) {
      await humanFillContentEditable(page, '[data-da-desc="true"]', desc, { minDelay: 30, maxDelay: 120 });
      log('Description filled');
    } else {
      log('Description: not_found');
    }

    // ===== 7. Screenshot before submit =====
    await humanThink(1000, 2500); // 发布前检查停顿
    await page.screenshot({ path: '/tmp/da-before-submit.png' });

    // ===== 8. Click Submit (NOT "Save to Studio") =====
    // The dialog has two buttons at the bottom. "Submit" is the primary action.
    // Strategy: find all buttons with text "Submit", exclude nav/menu ones
    const submitResult = await page.evaluate(() => {
      const btns = [...document.querySelectorAll('button')];
      
      // Collect all Submit buttons with context info
      const submitBtns = btns.filter(b => {
        const text = b.textContent.trim();
        if (text !== 'Submit') return false;
        // Exclude header nav submit button
        if (b.closest('nav') || b.closest('header') || b.closest('[role="menu"]')) return false;
        // Exclude the site header submit dropdown trigger
        if (b.closest('[class*="site-header"]')) return false;
        return true;
      });

      if (submitBtns.length === 0) return 'no_submit_found';

      // If multiple, pick the one inside the dialog or modal
      let target = submitBtns.find(b => b.closest('[role="dialog"]') || b.closest('[class*="modal"]'));
      if (!target) target = submitBtns[submitBtns.length - 1]; // fallback: last one

      target.click();
      return `clicked (class: ${target.className.substring(0, 30)})`;
    });
    log(`Submit: ${submitResult}`);

    await humanDelay(4000, 7000);

    // ===== 9. Verify =====
    await page.screenshot({ path: '/tmp/da-after-submit.png' });
    
    // Check if it went to published or if dialog closed
    const finalState = await page.evaluate(() => {
      const dialog = document.querySelector('[role="dialog"]');
      const errorMsg = document.querySelector('[class*="error" i]');
      return {
        dialogOpen: !!dialog,
        hasError: !!errorMsg,
        errorText: errorMsg?.textContent?.substring(0, 100) || '',
        url: window.location.href
      };
    });
    
    log(`Final state: dialog=${finalState.dialogOpen}, error=${finalState.hasError}`);
    if (finalState.hasError) log(`Error: ${finalState.errorText}`);
    
    // Navigate to published to verify
    await page.goto('https://www.deviantart.com/studio/published', { waitUntil: 'networkidle', timeout: 15000 });
    const topItem = await page.evaluate(() => {
      const firstBtn = document.querySelector('li button[class*="IIhy6Y"]');
      return firstBtn ? firstBtn.textContent.trim() : 'unknown';
    });
    log(`Top published item: "${topItem}"`);
    
    if (topItem.toLowerCase().includes(process.argv[3]?.toLowerCase()?.substring(0, 10) || '???')) {
      log('SUCCESS - Verified in published list');
    } else {
      log('WARNING - Could not verify in published list. Check /tmp/da-after-submit.png');
    }

  } catch (error) {
    err(error.message);
    await page.screenshot({ path: '/tmp/da-publish-error.png' }).catch(() => {});
    process.exit(1);
  } finally {
    await page.close();
  }
}

main();
