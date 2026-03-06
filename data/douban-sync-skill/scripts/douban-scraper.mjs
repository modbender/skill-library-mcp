#!/usr/bin/env node
// Douban full export scraper — outputs CSV
// Fetches all collection pages via HTTP (no browser needed, but may get rate-limited)

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const BASE_BOOK = 'https://book.douban.com';
const BASE_MOVIE = 'https://movie.douban.com';
const BASE_MUSIC = 'https://music.douban.com';
const BASE_GAME = 'https://www.douban.com';
const USER = process.env.DOUBAN_USER;
if (!USER) { console.error('Error: DOUBAN_USER env var is required'); process.exit(1); }
if (!/^[A-Za-z0-9._-]+$/.test(USER)) { console.error('Error: DOUBAN_USER contains invalid characters'); process.exit(1); }
const BASE_DIR = process.env.DOUBAN_OUTPUT_DIR || path.join(os.homedir(), 'douban-sync');
const OUTPUT_DIR = path.join(BASE_DIR, USER);

const CSV_HEADER = 'title,url,date,rating,status,comment\n';

const categories = [
  { base: BASE_BOOK, type: 'book', path: 'collect', status: '读过', file: '书.csv' },
  { base: BASE_BOOK, type: 'book', path: 'do', status: '在读', file: '书.csv' },
  { base: BASE_BOOK, type: 'book', path: 'wish', status: '想读', file: '书.csv' },
  { base: BASE_MOVIE, type: 'movie', path: 'collect', status: '看过', file: '影视.csv' },
  { base: BASE_MOVIE, type: 'movie', path: 'do', status: '在看', file: '影视.csv' },
  { base: BASE_MOVIE, type: 'movie', path: 'wish', status: '想看', file: '影视.csv' },
  { base: BASE_MUSIC, type: 'music', path: 'collect', status: '听过', file: '音乐.csv' },
  { base: BASE_MUSIC, type: 'music', path: 'do', status: '在听', file: '音乐.csv' },
  { base: BASE_MUSIC, type: 'music', path: 'wish', status: '想听', file: '音乐.csv' },
  { base: BASE_GAME, type: 'game', path: 'games?action=collect', status: '玩过', file: '游戏.csv' },
  { base: BASE_GAME, type: 'game', path: 'games?action=do', status: '在玩', file: '游戏.csv' },
  { base: BASE_GAME, type: 'game', path: 'games?action=wish', status: '想玩', file: '游戏.csv' },
];

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

function parseListPage(html) {
  const items = [];
  const itemBlocks = html.split(/<div class="item">/);

  for (let i = 1; i < itemBlocks.length; i++) {
    const block = itemBlocks[i];

    // Title and link
    const titleMatch = block.match(/<a[^>]*href="(https:\/\/(?:book|movie|music)\.douban\.com\/subject\/\d+\/)"[^>]*>([\s\S]*?)<\/a>/);
    if (!titleMatch) continue;
    const link = titleMatch[1];
    const title = titleMatch[2].replace(/<[^>]+>/g, '').trim();

    // Date and rating
    const dateMatch = block.match(/<span class="date">([\s\S]*?)<\/span>/);
    let date = '', rating = 0;
    if (dateMatch) {
      const dm = dateMatch[1].match(/(\d{4}-\d{2}-\d{2})/);
      if (dm) date = dm[1];
      const rm = dateMatch[1].match(/rating(\d+)-t/);
      if (rm) rating = parseInt(rm[1]);
    }

    // Comment
    const commentMatch = block.match(/<span class="comment">([\s\S]*?)<\/span>/);
    const comment = commentMatch ? commentMatch[1].replace(/<[^>]+>/g, '').trim() : '';

    items.push({ title, link, date, rating, comment });
  }
  return items;
}

function parseGamePage(html) {
  const items = [];
  const itemBlocks = html.split(/<div class="common-item">/);

  for (let i = 1; i < itemBlocks.length; i++) {
    const block = itemBlocks[i];

    // Title and link
    const titleMatch = block.match(/<div class="title">\s*<a href="(https:\/\/www\.douban\.com\/game\/\d+\/)">([\s\S]*?)<\/a>/);
    if (!titleMatch) continue;
    const link = titleMatch[1];
    const title = titleMatch[2].replace(/<[^>]+>/g, '').trim();

    // Rating: allstarNN where NN/10 = stars
    let rating = 0;
    const ratingMatch = block.match(/allstar(\d+)/);
    if (ratingMatch) rating = parseInt(ratingMatch[1]) / 10;

    // Date
    let date = '';
    const dateMatch = block.match(/<span class="date">([\s\S]*?)<\/span>/);
    if (dateMatch) {
      const dm = dateMatch[1].match(/(\d{4}-\d{2}-\d{2})/);
      if (dm) date = dm[1];
    }

    items.push({ title, link, date, rating, comment: '' });
  }
  return items;
}

async function fetchPage(url) {
  const resp = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      'Accept': 'text/html',
    }
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status} for ${url}`);
  return await resp.text();
}

async function fetchAllItems(base, userPath, type) {
  const allItems = [];
  let start = 0;
  let retries = 0;
  const MAX_RETRIES = 5;
  const hasQuery = userPath.includes('?');
  const isGame = type === 'game';
  const pageSize = isGame ? 15 : 30;

  while (true) {
    const sep = hasQuery ? '&' : '?';
    const url = `${base}/people/${USER}/${userPath}${sep}start=${start}&sort=time&rating=all&filter=all&mode=list`;
    console.log(`Fetching: ${url}`);

    try {
      const html = await fetchPage(url);
      const items = isGame ? parseGamePage(html) : parseListPage(html);

      if (items.length === 0) { console.log('  No items, stopping.'); break; }
      console.log(`  Found ${items.length} items`);
      allItems.push(...items);
      retries = 0;

      if (items.length < pageSize) { console.log(`  Last page.`); break; }
      start += pageSize;
      await sleep(2000);
    } catch (err) {
      console.error(`  Error: ${err.message}`);
      if ((err.message.includes('403') || err.message.includes('418')) && retries < MAX_RETRIES) {
        retries++;
        const delay = 10000 * Math.pow(2, retries - 1);
        console.log(`  Rate limited, retry ${retries}/${MAX_RETRIES}, waiting ${delay/1000}s...`);
        await sleep(delay);
        continue;
      }
      console.error(`  Giving up after ${retries} retries.`);
      break;
    }
  }
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
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  // Group by output file to avoid overwriting
  const fileData = {};

  for (const cat of categories) {
    console.log(`\n=== ${cat.status} (${cat.type}) ===`);
    const items = await fetchAllItems(cat.base, cat.path, cat.type);
    console.log(`Total: ${items.length} items`);

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

  console.log('\nDone!');
}

main().catch(console.error);
