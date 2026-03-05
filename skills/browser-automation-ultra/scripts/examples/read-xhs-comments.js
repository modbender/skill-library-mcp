#!/usr/bin/env node
/**
 * 小红书评论读取脚本
 * Usage: node read-xhs-comments.js [--limit N]
 * 
 * 输出 JSON 数组到 stdout:
 * [{ index, user, relation, comment, time, hasReplyBtn }]
 * 
 * 需要已登录小红书。
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');

function getCdpUrl() {
  try {
    const ps = execSync("ps aux | grep 'openclaw.*remote-debugging-port' | grep -v grep", { encoding: 'utf8' });
    const match = ps.match(/remote-debugging-port=(\d+)/);
    return `http://127.0.0.1:${match ? match[1] : '18800'}`;
  } catch { return 'http://127.0.0.1:18800'; }
}

function log(msg) { console.error(`[XHS-READ] ${msg}`); }

async function main() {
  const args = process.argv.slice(2);
  const limitIdx = args.indexOf('--limit');
  const limit = limitIdx >= 0 ? parseInt(args[limitIdx + 1]) || 20 : 20;

  let browser;
  try {
    browser = await chromium.connectOverCDP(getCdpUrl());
  } catch (e) {
    log('Cannot connect to CDP. Is OpenClaw browser running?');
    process.exit(1);
  }

  const context = browser.contexts()[0];
  const page = await context.newPage();

  try {
    await page.goto('https://www.xiaohongshu.com/notification', {
      waitUntil: 'networkidle',
      timeout: 30000,
    });
    await page.waitForTimeout(3000);
    log('Notification page loaded');

    const comments = await page.evaluate((maxItems) => {
      const results = [];
      const mains = document.querySelectorAll('.main');

      mains.forEach((main, i) => {
        if (results.length >= maxItems) return;

        const userEl = main.querySelector('.user-info a');
        const relationEl = main.querySelector('.user-tag');
        const timeEl = main.querySelector('.interaction-time');
        const contentEl = main.querySelector('.interaction-content');
        const hintEl = main.querySelector('.interaction-hint span:first-child');
        const replyBtn = main.querySelector('.action-reply');
        const noteImg = main.parentElement?.querySelector('img[class*="cover"], img[class*="note"]');

        // Skip non-comment notifications (e.g. nav items without interaction-content)
        if (!contentEl && !hintEl) return;

        const type = hintEl?.textContent?.trim() || '';
        // Only include comment/reply notifications
        if (!type.includes('评论') && !type.includes('回复')) return;

        results.push({
          index: results.length,
          user: userEl?.textContent?.trim() || '',
          relation: relationEl?.textContent?.trim() || '',
          type: type,
          comment: contentEl?.textContent?.trim() || '',
          time: timeEl?.textContent?.trim() || '',
          hasReplyBtn: !!replyBtn,
          // replyBtnIndex: index among all .action-reply buttons (for reply script)
          _mainIndex: i,
        });
      });

      // Calculate reply button indices for each item that has one
      const allReplyBtns = document.querySelectorAll('.action-reply');
      const btnToMainIndex = [];
      allReplyBtns.forEach((btn) => {
        const main = btn.closest('.main');
        if (main) {
          const mains = document.querySelectorAll('.main');
          for (let j = 0; j < mains.length; j++) {
            if (mains[j] === main) { btnToMainIndex.push(j); break; }
          }
        }
      });

      results.forEach(item => {
        const btnIdx = btnToMainIndex.indexOf(item._mainIndex);
        item.replyBtnIndex = btnIdx >= 0 ? btnIdx : -1;
        delete item._mainIndex;
      });

      return results;
    }, limit);

    log(`Found ${comments.length} comment(s)`);
    console.log(JSON.stringify(comments, null, 2));

  } catch (error) {
    log(`Error: ${error.message}`);
    process.exit(1);
  } finally {
    await page.close();
  }
}

main().then(() => process.exit(0)).catch(e => { console.error('❌', e.message); process.exit(1); });
