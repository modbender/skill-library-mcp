#!/usr/bin/env node
// Douban full export via CDP browser — outputs CSV
// Connects to an existing browser session (e.g. opened with --remote-debugging-port)

import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const BROWSER_URL = process.env.BROWSER_URL || 'http://127.0.0.1:18800';
const USER = process.env.DOUBAN_USER;
if (!USER) { console.error('Error: DOUBAN_USER env var is required'); process.exit(1); }
if (!/^[A-Za-z0-9._-]+$/.test(USER)) { console.error('Error: DOUBAN_USER contains invalid characters'); process.exit(1); }
const BASE_DIR = process.env.DOUBAN_OUTPUT_DIR || path.join(os.homedir(), 'douban-sync');
const OUTPUT_DIR = path.join(BASE_DIR, USER);

const CSV_HEADER = 'title,url,date,rating,status,comment\n';

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function csvEscape(str) {
  if (!str) return '';
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return '"' + str.replace(/"/g, '""') + '"';
  }
  return str;
}

function ratingStars(rating) {
  if (!rating || rating === 0) return '';
  return '★'.repeat(rating);
}

const parseScript = `
() => {
  const items = document.querySelectorAll('.list-view .item');
  const results = [];
  for (const item of items) {
    const t = item.querySelector('.title a');
    const title = t ? t.textContent.trim() : '';
    const link = t ? t.getAttribute('href') : '';
    const d = item.querySelector('.date');
    let date = '', rating = 0;
    if (d) {
      const r = d.querySelector('span[class*="rating"]');
      if (r) { const m = r.className.match(/rating(\\d+)-t/); if (m) rating = parseInt(m[1]); }
      const dm = d.textContent.match(/(\\d{4}-\\d{2}-\\d{2})/);
      if (dm) date = dm[1];
    }
    const c = item.querySelector('.comment');
    results.push({ title, link, date, rating, comment: c ? c.textContent.trim() : '' });
  }
  return results;
}
`;

const parseGameScript = `
() => {
  const items = document.querySelectorAll('.common-item');
  const results = [];
  for (const item of items) {
    const t = item.querySelector('.title a');
    const title = t ? t.textContent.trim() : '';
    const link = t ? t.getAttribute('href') : '';
    let date = '', rating = 0;
    const r = item.querySelector('.rating-star');
    if (r) { const m = r.className.match(/allstar(\\d+)/); if (m) rating = parseInt(m[1]) / 10; }
    const d = item.querySelector('.date');
    if (d) { const dm = d.textContent.match(/(\\d{4}-\\d{2}-\\d{2})/); if (dm) date = dm[1]; }
    results.push({ title, link, date, rating, comment: '' });
  }
  return results;
}
`;

const categories = [
  { base: 'https://book.douban.com', path: 'collect', status: '读过', file: '书.csv', type: 'book' },
  { base: 'https://book.douban.com', path: 'do', status: '在读', file: '书.csv', type: 'book' },
  { base: 'https://book.douban.com', path: 'wish', status: '想读', file: '书.csv', type: 'book' },
  { base: 'https://movie.douban.com', path: 'collect', status: '看过', file: '影视.csv', type: 'movie' },
  { base: 'https://movie.douban.com', path: 'do', status: '在看', file: '影视.csv', type: 'movie' },
  { base: 'https://movie.douban.com', path: 'wish', status: '想看', file: '影视.csv', type: 'movie' },
  { base: 'https://music.douban.com', path: 'collect', status: '听过', file: '音乐.csv', type: 'music' },
  { base: 'https://music.douban.com', path: 'do', status: '在听', file: '音乐.csv', type: 'music' },
  { base: 'https://music.douban.com', path: 'wish', status: '想听', file: '音乐.csv', type: 'music' },
  { base: 'https://www.douban.com', path: 'games?action=collect', status: '玩过', file: '游戏.csv', type: 'game' },
  { base: 'https://www.douban.com', path: 'games?action=do', status: '在玩', file: '游戏.csv', type: 'game' },
  { base: 'https://www.douban.com', path: 'games?action=wish', status: '想玩', file: '游戏.csv', type: 'game' },
];

async function scrapeCategory(browser, cat) {
  console.log(`\n=== ${cat.status} (${cat.type}) ===`);
  const page = await browser.newPage();
  const allItems = [];

  try {
    let start = 0;
    while (true) {
      const sep = cat.path.includes('?') ? '&' : '?';
      const url = `${cat.base}/people/${USER}/${cat.path}${sep}start=${start}&sort=time&rating=all&filter=all&mode=list`;
      console.log(`  Fetching start=${start}...`);

      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await sleep(1000);

      const script = cat.type === 'game' ? parseGameScript : parseScript;
      const items = await page.evaluate(new Function('return (' + script + ')()'));
      if (!items || items.length === 0) { console.log('  No items, stopping.'); break; }

      const pageSize = cat.type === 'game' ? 15 : 30;
      console.log(`  Got ${items.length} items`);
      allItems.push(...items);

      const hasNext = await page.evaluate(() => {
        const next = document.querySelector('.paginator .next a');
        return !!next;
      });
      if (!hasNext) break;
      start += pageSize;
      await sleep(2000);
    }
  } catch (err) {
    console.error(`  Error: ${err.message}`);
  } finally {
    await page.close();
  }

  console.log(`  Total: ${allItems.length} items`);
  return allItems;
}

function itemToCsvLine(item, status) {
  return [
    csvEscape(item.title),
    csvEscape(item.link),
    csvEscape(item.date),
    csvEscape(ratingStars(item.rating)),
    csvEscape(status),
    csvEscape(item.comment),
  ].join(',');
}

async function main() {
  console.log('Connecting to browser...');
  const browser = await puppeteer.connect({ browserURL: BROWSER_URL });
  console.log('Connected!');

  try {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });

    const fileData = {};

    for (const cat of categories) {
      const items = await scrapeCategory(browser, cat);
      if (!fileData[cat.file]) fileData[cat.file] = [];
      for (const item of items) {
        fileData[cat.file].push(itemToCsvLine(item, cat.status));
      }
      await sleep(3000);
    }

    for (const [file, lines] of Object.entries(fileData)) {
      const filePath = path.join(OUTPUT_DIR, file);
      fs.writeFileSync(filePath, CSV_HEADER + lines.join('\n') + '\n', 'utf8');
      console.log(`Written ${lines.length} rows to ${filePath}`);
    }

    console.log('\n✅ All done!');
  } finally {
    browser.disconnect();
  }
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
