#!/usr/bin/env node
/**
 * Behance Publish Script (Playwright via CDP)
 * Usage: ./scripts/browser-lock.sh run scripts/browser/publish-behance.js <image-path> <title> <description> <tags-csv> <categories-csv>
 * 
 * Categories: comma-separated Chinese names matching Behance's category list
 * Default categories: 数码艺术,插图,美术
 * 
 * Connects to standalone Chrome launched by browser-lock.sh.
 * Requires: Behance (Adobe) session already logged in.
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const path = require('path');
const { humanDelay, humanClick, humanType, humanThink, humanBrowse } = require('./utils/human-like');

function discoverCdpUrl() {
  try {
    const ps = execSync("ps aux | grep 'remote-debugging-port=' | grep -v grep", { encoding: 'utf8', timeout: 3000 });
    const match = ps.match(/remote-debugging-port=(\d+)/);
    if (match) return `http://127.0.0.1:${match[1]}`;
  } catch {}
  if (process.env.CDP_PORT) return `http://127.0.0.1:${process.env.CDP_PORT}`;
  for (const port of [18800, 9222]) {
    try {
      execSync(`curl -s --max-time 1 http://127.0.0.1:${port}/json/version`, { encoding: 'utf8', timeout: 2000 });
      return `http://127.0.0.1:${port}`;
    } catch {}
  }
  throw new Error('CDP port not found');
}

function log(msg) { console.log(`[BE] ${msg}`); }

async function main() {
  const [,, imagePath, title, description, tagsStr, categoriesStr] = process.argv;
  if (!imagePath || !title) {
    console.error('Usage: node publish-behance.js <image> <title> [description] [tags] [categories]');
    process.exit(1);
  }

  const absPath = path.resolve(imagePath);
  const tags = (tagsStr || 'digital art,abstract art,generative art').split(',').map(t => t.trim());
  const categories = (categoriesStr || '数码艺术,插图,美术').split(',').map(c => c.trim());
  const desc = description || title;

  log(`Publishing: "${title}"`);
  log(`Tags: ${tags.join(', ')}`);
  log(`Categories: ${categories.join(', ')}`);

  let browser;
  try {
    browser = await chromium.connectOverCDP(discoverCdpUrl());
  } catch (e) {
    console.error('❌ Cannot connect to CDP:', e.message);
    process.exit(1);
  }

  const context = browser.contexts()[0];
  const page = await context.newPage();

  try {
    // ===== 1. Open editor =====
    await page.goto('https://www.behance.net/portfolio/editor', { waitUntil: 'networkidle', timeout: 30000 });
    await humanDelay(2000, 4000);

    // Dismiss popups
    for (let i = 0; i < 3; i++) {
      const closed = await page.evaluate(() => {
        const btns = [...document.querySelectorAll('button, a')];
        const dismiss = btns.find(b => /Continue to editor|继续转到编辑器|Maybe later|稍后/.test(b.textContent));
        if (dismiss) { dismiss.click(); return true; }
        return false;
      });
      if (closed) await humanDelay(800, 1500);
      else break;
    }
    log('Editor opened');
    await humanBrowse(page, { duration: 2000 });

    // ===== 2. Upload image via file input (qqfile) =====
    const addImgBtn = await page.$('button:has-text("Add an Image"), button:has-text("Add Photo")');
    if (addImgBtn) await humanClick(page, addImgBtn);
    await humanDelay(800, 1500);

    // Use the hidden file input
    const fileInput = await page.$('input[name="qqfile"]');
    if (fileInput) {
      await fileInput.setInputFiles(absPath);
      log('Image uploaded via file input');
    } else {
      // Fallback: use filechooser event
      const [fileChooser] = await Promise.all([
        page.waitForEvent('filechooser', { timeout: 10000 }),
        page.click('button:has-text("图像"), button:has-text("Image"), button:has-text("添加图像")')
      ]);
      await fileChooser.setFiles(absPath);
      log('Image uploaded via filechooser');
    }

    await humanDelay(6000, 10000);
    log('Upload processing complete');

    // ===== 3. Click "继续" (Continue) =====
    await humanThink(1000, 2000);
    const continueBtn = await page.$('button:has-text("继续"), button:has-text("Continue")');
    if (continueBtn) {
      await humanClick(page, continueBtn);
      log('Clicked Continue');
    } else {
      throw new Error('Continue button not found');
    }
    await humanDelay(2000, 4000);

    // ===== 4. Fill publish dialog fields =====
    // Wait for the dialog
    await page.waitForSelector('dialog, [role="dialog"]', { timeout: 10000 });
    log('Publish dialog opened');

    // 4a. Title
    await humanThink(500, 1500);
    const titleInput = await page.$('input[placeholder*="标题"], input[placeholder*="title"], input[placeholder*="Title"], input[placeholder*="项目"]');
    if (titleInput) {
      await humanClick(page, titleInput);
      await page.keyboard.down('Meta');
      await page.keyboard.press('a');
      await page.keyboard.up('Meta');
      await humanDelay(100, 300);
      await humanType(page, null, title, { minDelay: 50, maxDelay: 160 });
      log(`Title set: ${title}`);
    } else {
      log('WARNING: Title input not found');
    }

    // 4b. Tags
    await humanThink(300, 800);
    const tagInputs = await page.$$('input[placeholder*="关键字"], input[placeholder*="tag"], input[placeholder*="Tag"]');
    let tagInput = tagInputs[0];
    if (!tagInput) tagInput = await page.$('input[placeholder=""]');

    if (tagInput) {
      for (const tag of tags) {
        await humanClick(page, tagInput);
        await humanType(page, null, tag, { minDelay: 40, maxDelay: 120 });
        await page.keyboard.press('Enter');
        await humanDelay(300, 700);
      }
      log(`Tags added: ${tags.join(', ')}`);
    } else {
      log('WARNING: Tag input not found');
    }

    // 4c. Categories — click "查看全部" to open category modal
    const viewAllBtn = await page.$('button:has-text("查看全部"), button:has-text("View All")');
    if (viewAllBtn) {
      await viewAllBtn.click();
      await page.waitForTimeout(1500);
      log('Category modal opened');

      // Select categories by checkbox label
      for (const cat of categories) {
        const checkbox = await page.$(`text="${cat}" >> xpath=.. >> input[type="checkbox"], label:has-text("${cat}") input[type="checkbox"]`);
        if (checkbox) {
          await checkbox.check();
          log(`Category selected: ${cat}`);
        } else {
          // Fallback: find checkbox by nearby text
          const checked = await page.evaluate((catName) => {
            const labels = [...document.querySelectorAll('label, span, div')];
            for (const el of labels) {
              if (el.textContent.trim() === catName) {
                const cb = el.closest('label, div')?.querySelector('input[type="checkbox"]') 
                  || el.previousElementSibling;
                if (cb && cb.type === 'checkbox' && !cb.checked) {
                  cb.click();
                  return true;
                }
              }
            }
            return false;
          }, cat);
          log(checked ? `Category selected (fallback): ${cat}` : `WARNING: Category not found: ${cat}`);
        }
        await humanDelay(300, 700);
      }

      const doneBtn = await page.$('button:has-text("完成"), button:has-text("Done")');
      if (doneBtn) {
        await humanClick(page, doneBtn);
        await humanDelay(800, 1500);
        log('Category selection done');
      }
    } else {
      log('WARNING: Category button not found');
    }

    // 4d. Description
    await humanThink(500, 1200);
    const descInput = await page.$('textarea[placeholder*="描述"], textarea[placeholder*="description"], textarea[placeholder*="Description"]');
    if (descInput) {
      await humanClick(page, descInput);
      await humanDelay(200, 500);
      await humanType(page, null, desc, { minDelay: 30, maxDelay: 100 });
      log('Description set');
    } else {
      log('WARNING: Description textarea not found');
    }

    // ===== 5. Click "发布" (Publish) =====
    await humanThink(1500, 3000);
    
    const publishBtn = await page.$('button:has-text("发布"):not(:has-text("安排"))');
    if (publishBtn) {
      // Wait for it to be enabled
      await page.waitForFunction(() => {
        const btns = [...document.querySelectorAll('button')];
        const pub = btns.find(b => b.textContent.trim() === '发布' || b.textContent.trim() === 'Publish');
        return pub && !pub.disabled;
      }, {}, { timeout: 15000 });
      
      await humanClick(page, publishBtn);
      log('Clicked Publish');
    } else {
      throw new Error('Publish button not found');
    }

    await humanDelay(6000, 10000);

    // ===== 6. Verify =====
    const finalUrl = page.url();
    log(`Final URL: ${finalUrl}`);

    if (finalUrl.includes('gallery') || finalUrl.includes('freeonart') || !finalUrl.includes('editor')) {
      log('✅ SUCCESS — Project published!');
    } else {
      await page.screenshot({ path: '/tmp/be-publish-result.png' });
      log('⚠️ Check /tmp/be-publish-result.png for status');
    }

  } catch (error) {
    console.error('❌ Error:', error.message);
    await page.screenshot({ path: '/tmp/be-publish-error.png' }).catch(() => {});
    throw error;
  } finally {
    await page.close();
  }
}

main().then(() => process.exit(0)).catch(e => {
  console.error('❌', e.message);
  process.exit(1);
});
