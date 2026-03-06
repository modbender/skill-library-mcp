#!/usr/bin/env node
/**
 * Read latest email from Proton Mail inbox (Playwright via CDP)
 * Usage: node read-proton-latest.js [--index N] [--json]
 *   --index N   Read the Nth email (0-based, default 0 = latest)
 *   --json      Output as JSON instead of plain text
 *
 * Requires: Proton Mail already logged in in the OpenClaw browser.
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

function log(msg) { console.log(`[PROTON] ${msg}`); }
function err(msg) { console.error(`[PROTON ERROR] ${msg}`); }

async function main() {
  // Parse args
  const args = process.argv.slice(2);
  let index = 0;
  let jsonOutput = false;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--index' && args[i + 1]) { index = parseInt(args[i + 1]); i++; }
    if (args[i] === '--json') jsonOutput = true;
  }

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
    // 1. Navigate to inbox
    log('Opening inbox...');
    await page.goto('https://mail.proton.me/u/0/inbox', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);

    // 2. Get email list metadata
    const emailList = await page.evaluate(() => {
      var items = document.querySelectorAll('[data-shortcut-target="item-container"]');
      return Array.from(items).map(function(item) {
        var sender = item.querySelector('[data-testid="message-column:sender-address"]');
        var subject = item.querySelector('[data-testid="message-column:subject"]');
        var time = item.querySelector('time');
        return {
          sender: sender ? sender.textContent.trim() : '',
          subject: subject ? subject.textContent.trim() : '',
          time: time ? time.getAttribute('datetime') || time.textContent.trim() : ''
        };
      });
    });

    if (emailList.length === 0) {
      err('No emails found in inbox');
      process.exit(1);
    }

    if (index >= emailList.length) {
      err('Index ' + index + ' out of range (inbox has ' + emailList.length + ' emails)');
      process.exit(1);
    }

    const meta = emailList[index];
    log('Opening email [' + index + ']: "' + (meta.subject || 'no subject') + '" from ' + (meta.sender || 'unknown'));

    // 3. Click the email
    await page.evaluate(function(idx) {
      document.querySelectorAll('[data-shortcut-target="item-container"]')[idx].click();
    }, index);
    await page.waitForTimeout(3000);

    // 4. Read email body from iframe
    const body = await page.evaluate(function() {
      var iframe = document.querySelector('iframe[sandbox]');
      if (!iframe) return '';
      var doc = iframe.contentDocument;
      if (!doc) return '';
      return doc.body.innerText.substring(0, 5000);
    });

    // 5. Get full metadata from opened email
    const detail = await page.evaluate(function() {
      var fromEl = document.querySelector('[data-testid="message:from"]') ||
                   document.querySelector('button[class*="from"]');
      var toEl = document.querySelector('[data-testid="message:to"]');
      var subjectEl = document.querySelector('h1');
      return {
        from: fromEl ? fromEl.textContent.trim() : '',
        to: toEl ? toEl.textContent.trim() : '',
        subject: subjectEl ? subjectEl.textContent.trim() : ''
      };
    });

    // 6. Output
    if (jsonOutput) {
      console.log(JSON.stringify({
        index: index,
        sender: meta.sender || detail.from,
        subject: meta.subject || detail.subject,
        time: meta.time,
        body: body
      }, null, 2));
    } else {
      console.log('\n--- Email ---');
      console.log('From: ' + (meta.sender || detail.from));
      console.log('Subject: ' + (meta.subject || detail.subject));
      console.log('Time: ' + meta.time);
      console.log('---');
      console.log(body);
      console.log('--- End ---');
    }

  } catch (error) {
    err(error.message);
    await page.screenshot({ path: '/tmp/proton-read-error.png' }).catch(function() {});
    process.exit(1);
  } finally {
    await page.close();
  }
}

main().then(function() { process.exit(0); }).catch(function(e) { err(e.message); process.exit(1); });
