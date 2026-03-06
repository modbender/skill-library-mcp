#!/usr/bin/env node
/**
 * 小红书评论回复脚本
 * Usage: node reply-xhs-comment.js <comment-index> <reply-text>
 * 
 * comment-index: 第几条评论 (0-based, 对应 read-xhs-comments.js 输出的 index)
 * reply-text: 回复内容
 * 
 * 需要已登录小红书。
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const { humanDelay, humanClick, humanType, humanThink, humanBrowse } = require('./utils/human-like');

function getCdpUrl() {
  try {
    const ps = execSync("ps aux | grep 'openclaw.*remote-debugging-port' | grep -v grep", { encoding: 'utf8' });
    const match = ps.match(/remote-debugging-port=(\d+)/);
    return `http://127.0.0.1:${match ? match[1] : '18800'}`;
  } catch { return 'http://127.0.0.1:18800'; }
}

function log(msg) { console.log(`[XHS-REPLY] ${msg}`); }
function err(msg) { console.error(`[XHS-REPLY ERROR] ${msg}`); }

async function main() {
  const [,, indexStr, replyText] = process.argv;
  if (indexStr === undefined || !replyText) {
    err('Usage: node reply-xhs-comment.js <comment-index> <reply-text>');
    process.exit(1);
  }
  const targetIndex = parseInt(indexStr);

  log(`Replying to comment #${targetIndex}: "${replyText}"`);

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
    await page.goto('https://www.xiaohongshu.com/notification', {
      waitUntil: 'networkidle',
      timeout: 30000,
    });
    await humanDelay(2000, 4000);
    log('Notification page loaded');

    // 模拟先浏览通知页
    await humanBrowse(page, { duration: 1500 });

    // Click the reply button for the target comment
    const replyBtns = await page.$$('.action-reply');
    if (targetIndex >= replyBtns.length) {
      err(`index ${targetIndex} out of range (${replyBtns.length} reply buttons)`);
      process.exit(1);
    }
    await humanClick(page, replyBtns[targetIndex]);
    log('Reply button clicked');
    await humanDelay(800, 1500);

    // Find and type into the textarea
    const ta = await page.$('textarea.comment-input');
    if (!ta) { err('textarea not found'); process.exit(1); }
    await humanClick(page, ta);
    await humanDelay(300, 700);
    await humanType(page, null, replyText, { minDelay: 60, maxDelay: 200 });
    log('Reply text typed');
    await humanThink(500, 1500);

    // Click send button
    const sendBtn = await page.$('div.submit, button.submit');
    if (!sendBtn) {
      // Fallback
      const sent = await page.evaluate(() => {
        const all = [...document.querySelectorAll('button, div, span')]
          .filter(el => el.textContent.trim() === '发送' && el.offsetHeight > 0 && el.children.length === 0);
        if (all.length > 0) { all[0].click(); return 'ok'; }
        return 'not found';
      });
      if (sent !== 'ok') { err('send button not found'); process.exit(1); }
    } else {
      await humanClick(page, sendBtn);
    }
    log('Send clicked');
    await humanDelay(1500, 3000);

    // Verify: textarea should disappear after successful send
    const verified = await page.evaluate(() => {
      const ta = document.querySelector('textarea.comment-input');
      return ta ? (ta.offsetHeight > 0 ? 'still visible' : 'hidden') : 'gone';
    });

    if (verified === 'gone' || verified === 'hidden') {
      log('SUCCESS - Reply sent');
    } else {
      log(`WARNING - textarea ${verified}, reply may not have sent`);
    }

  } catch (error) {
    err(error.message);
    process.exit(1);
  } finally {
    await page.close();
  }
}

main().then(() => process.exit(0)).catch(e => { console.error('❌', e.message); process.exit(1); });
