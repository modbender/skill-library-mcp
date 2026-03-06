#!/usr/bin/env node
/**
 * 小红书创作平台发布脚本 (Playwright via CDP)
 * Usage: node publish-xiaohongshu.js <image-path> <title> <description> [tags-comma-separated]
 *
 * description: 正文内容（不含话题标签）
 * tags: 可选，逗号分隔的话题关键词，如 "抽象艺术,数字艺术,当代艺术"
 *       脚本通过话题按钮触发推荐列表，再点击匹配项关联真实话题。
 *       话题按钮会插入 # 字符，点击推荐项会替换该 # 为完整话题元素。
 *       若推荐列表无匹配，则跳过。
 *
 * 需要已登录小红书创作平台。
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const { humanDelay, humanClick, humanType, humanFillContentEditable, humanBrowse, humanThink } = require('./utils/human-like');

function getCdpUrl() {
  try {
    const ps = execSync("ps aux | grep 'openclaw.*remote-debugging-port' | grep -v grep", { encoding: 'utf8' });
    const match = ps.match(/remote-debugging-port=(\d+)/);
    return `http://127.0.0.1:${match ? match[1] : '18800'}`;
  } catch { return 'http://127.0.0.1:18800'; }
}

function log(msg) { console.log(`[XHS] ${msg}`); }
function err(msg) { console.error(`[XHS ERROR] ${msg}`); }

async function addTopicTag(page, wantedTag) {
  // Step 1: Click topic button — inserts "#" into editor and shows recommendations
  const topicBtn = await page.$('button.contentBtn.topic-btn, button:has-text("话题")');
  if (!topicBtn) return 'no-button';
  await humanClick(page, topicBtn);
  await humanDelay(600, 1200);

  // Step 2: Try to find and click matching tag in recommendation list
  // The topic button inserted a "#" which the recommendation click will REPLACE.
  // Check initial visible tags first
  let matched = await page.evaluate((tag) => {
    const wrapper = document.querySelector('.recommend-topic-wrapper');
    if (!wrapper) return false;
    const spans = wrapper.querySelectorAll('span.tag');
    for (const span of spans) {
      const text = span.textContent.trim();
      if (text === '#' + tag || text === tag) {
        span.click();
        return true;
      }
    }
    return false;
  }, wantedTag);

  if (matched) return 'matched';

  // Step 3: Expand "更多" and retry
  const expanded = await page.evaluate(() => {
    const wrapper = document.querySelector('.recommend-topic-wrapper');
    if (!wrapper) return false;
    const moreBtn = [...wrapper.querySelectorAll('span, div')]
      .find(el => el.textContent.trim() === '更多' && el.offsetHeight > 0);
    if (moreBtn) { moreBtn.click(); return true; }
    return false;
  });

  if (expanded) {
    await humanDelay(400, 800);
    matched = await page.evaluate((tag) => {
      const wrapper = document.querySelector('.recommend-topic-wrapper');
      if (!wrapper) return false;
      const spans = wrapper.querySelectorAll('span.tag');
      for (const span of spans) {
        const text = span.textContent.trim();
        if (text === '#' + tag || text === tag) {
          span.click();
          return true;
        }
      }
      return false;
    }, wantedTag);

    if (matched) return 'matched-expanded';
  }

  // Step 4: Not found — remove the "#" that the topic button inserted
  await page.evaluate(() => {
    const editor = document.querySelector('[contenteditable="true"]');
    if (!editor) return;
    // Remove trailing standalone "#" not inside a tiptap-topic
    const walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT);
    const toClean = [];
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement.closest('.tiptap-topic')) continue;
      if (node.textContent.includes('#')) {
        toClean.push(node);
      }
    }
    toClean.forEach(node => {
      node.textContent = node.textContent.replace(/#/g, '');
      if (!node.textContent.trim()) node.remove();
    });
    // Also remove any suggestion spans
    editor.querySelectorAll('.suggestion').forEach(s => s.remove());
    editor.dispatchEvent(new Event('input', { bubbles: true }));
  });

  return 'not-found';
}

async function main() {
  const [,, imagePath, title, description, tagsStr] = process.argv;
  if (!imagePath || !title) {
    err('Usage: node publish-xiaohongshu.js <image> <title> [description] [tags]');
    process.exit(1);
  }

  const absPath = path.resolve(imagePath);
  if (!fs.existsSync(absPath)) {
    err(`File not found: ${absPath}`);
    process.exit(1);
  }
  const desc = description || '';
  const wantedTags = tagsStr ? tagsStr.split(',').map(t => t.trim()).filter(Boolean) : [];

  log(`Publishing: "${title}"`);
  log(`Image: ${absPath}`);
  if (wantedTags.length) log(`Wanted tags: ${wantedTags.join(', ')}`);

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
    // ===== 1. Navigate to publish page =====
    await page.goto('https://creator.xiaohongshu.com/publish/publish?from=homepage&target=image', {
      waitUntil: 'networkidle',
      timeout: 30000,
    });
    await humanDelay(2000, 4000);
    log('Publish page loaded');

    // 模拟人类浏览页面
    await humanBrowse(page, { duration: 2000 });

    // ===== 2. Upload image =====
    const fileInput = await page.$('input[type="file"]');
    if (!fileInput) { err('File input not found'); process.exit(1); }
    await fileInput.setInputFiles(absPath);
    log('Image uploaded');
    await humanDelay(4000, 7000);

    // ===== 3. Fill title =====
    const titleInput = await page.$('input[placeholder*="标题"]');
    if (titleInput) {
      await humanThink(800, 2000);
      await humanType(page, 'input[placeholder*="标题"]', title, { minDelay: 60, maxDelay: 200 });
      log(`Title: ${title}`);
    }

    // ===== 4. Fill description =====
    if (desc) {
      await humanThink(1000, 2500);
      await humanFillContentEditable(page, '[contenteditable="true"]', desc, { minDelay: 40, maxDelay: 150 });
      log('Description filled');
    }

    // ===== 5. Add topic tags =====
    if (wantedTags.length > 0) {
      let added = 0;
      for (const tag of wantedTags) {
        const result = await addTopicTag(page, tag);
        if (result.startsWith('matched')) {
          added++;
          log(`Tag: #${tag} ✅ (${result})`);
        } else {
          log(`Tag: #${tag} ⏭ (${result})`);
        }
        await humanDelay(200, 600);
      }
      log(`Tags: ${added}/${wantedTags.length} added`);

      // Final cleanup: remove any leftover bare # or suggestion spans
      await page.evaluate(() => {
        const editor = document.querySelector('[contenteditable="true"]');
        if (!editor) return;
        editor.querySelectorAll('.suggestion').forEach(s => s.remove());
        const walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          const node = walker.currentNode;
          if (node.parentElement.closest('.tiptap-topic')) continue;
          if (node.parentElement.closest('.content-hide')) continue;
          // Remove standalone # not part of topics
          node.textContent = node.textContent.replace(/(?<!\S)#(?!\S)/g, '').replace(/\s{2,}/g, ' ');
        }
        editor.dispatchEvent(new Event('input', { bubbles: true }));
      });
    }

    // ===== 6. Original declaration =====
    try {
      const origCheckbox = await page.$('input[type="checkbox"]:near(:text("原创声明"))');
      if (origCheckbox) {
        const checked = await origCheckbox.isChecked();
        if (!checked) {
          await origCheckbox.click();
          await page.waitForTimeout(1000);
          const agreeEl = await page.$('text=我已阅读并同意');
          if (agreeEl) { await agreeEl.click(); await page.waitForTimeout(500); }
          const declareBtn = await page.$('button:has-text("声明原创"):not([disabled])');
          if (declareBtn) { await declareBtn.click(); log('Original declaration ✅'); await page.waitForTimeout(1000); }
        }
      }
    } catch (e) { log('Original declaration skipped'); }

    // ===== 7. Publish =====
    await page.screenshot({ path: '/tmp/xhs-before-publish.png' });
    await humanThink(1000, 3000); // 发布前停顿，模拟检查
    const publishBtn = await page.$('button:has-text("发布")');
    if (!publishBtn) { err('Publish button not found'); process.exit(1); }
    await humanClick(page, publishBtn);
    log('Publish clicked');
    await humanDelay(4000, 7000);

    const currentUrl = page.url();
    if (!currentUrl.includes('/publish/publish')) {
      log('SUCCESS ✅');
    } else {
      const errText = await page.evaluate(() =>
        [...document.querySelectorAll('[class*="error"],[class*="toast"]')].map(e => e.textContent).join('; ')
      );
      if (errText) err(errText);
      else log('WARNING - Still on publish page');
    }
    await page.screenshot({ path: '/tmp/xhs-after-publish.png' });

  } catch (error) {
    err(error.message);
    await page.screenshot({ path: '/tmp/xhs-publish-error.png' }).catch(() => {});
    process.exit(1);
  } finally {
    await page.close();
  }
}

main().then(() => process.exit(0)).catch(e => { console.error('❌', e.message); process.exit(1); });
