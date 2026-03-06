#!/usr/bin/env node
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');

function sanitizeName(input) {
  return input.replace(/[^a-zA-Z0-9._-]/g, '_').slice(0, 120);
}

function nowStamp() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return (
    d.getUTCFullYear() +
    pad(d.getUTCMonth() + 1) +
    pad(d.getUTCDate()) +
    'T' +
    pad(d.getUTCHours()) +
    pad(d.getUTCMinutes()) +
    pad(d.getUTCSeconds()) +
    'Z'
  );
}

async function main() {
  const urls = process.argv.slice(2);
  if (urls.length === 0) {
    console.error('Usage: node mission-control-visual-qa.js <url1> [url2 ...]');
    process.exit(2);
  }

  const outputDir = process.env.OUTPUT_DIR || path.join(os.homedir(), '.openclaw/workspace/output/visual-qa');
  fs.mkdirSync(outputDir, { recursive: true });

  let puppeteer;
  try {
    puppeteer = require('puppeteer');
  } catch (err) {
    console.error('Missing dependency: puppeteer. Install on SAPCONET host.');
    console.error(err.message);
    process.exit(3);
  }

  const browser = await puppeteer.launch({
    headless: true,
    executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const results = [];

  try {
    for (const url of urls) {
      const page = await browser.newPage();
      await page.setViewport({ width: 1440, height: 900 });

      const item = {
        url,
        ok: false,
        checks: {},
      };

      try {
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 45000 });
        const meta = await page.evaluate(() => {
          const text = document.body ? document.body.innerText || '' : '';
          return {
            title: document.title || '',
            hasMain: Boolean(document.querySelector('main')),
            hasH1: Boolean(document.querySelector('h1')),
            bodyTextLength: text.trim().length,
          };
        });

        item.checks = {
          titleNonEmpty: meta.title.length > 0,
          hasMain: meta.hasMain,
          hasH1: meta.hasH1,
          bodyTextLengthGt100: meta.bodyTextLength > 100,
          title: meta.title,
          bodyTextLength: meta.bodyTextLength,
        };

        item.ok =
          item.checks.titleNonEmpty &&
          item.checks.hasMain &&
          item.checks.hasH1 &&
          item.checks.bodyTextLengthGt100;

        const fileName = `${nowStamp()}_${sanitizeName(new URL(url).hostname + new URL(url).pathname)}.png`;
        const screenshotPath = path.join(outputDir, fileName);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        item.screenshotPath = screenshotPath;
      } catch (err) {
        item.error = err.message;
      } finally {
        await page.close();
      }

      results.push(item);
    }
  } finally {
    await browser.close();
  }

  const summary = {
    ranAt: new Date().toISOString(),
    outputDir,
    total: results.length,
    passed: results.filter((r) => r.ok).length,
    failed: results.filter((r) => !r.ok).length,
    results,
  };

  console.log(JSON.stringify(summary, null, 2));
  process.exit(summary.failed > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
