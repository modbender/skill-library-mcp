#!/usr/bin/env node
'use strict';

/**
 * skill-search.js — 非交互搜索，输出 JSON
 * 通过 Nominatim 地理编码 + 直接 URL 跳转，完全无表单操作，规避 Akamai 检测
 * 用法: node skill-search.js --dest "上海金桥" --in 2026-03-06 --out 2026-03-10
 */

const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });
const { chromium } = require('playwright');
const minimist = require('minimist');
const fs = require('fs');

const args = minimist(process.argv.slice(2));
if (!args.dest || !args.in || !args.out) {
  process.stderr.write('用法: node skill-search.js --dest "目的地" --in YYYY-MM-DD --out YYYY-MM-DD\n');
  process.exit(1);
}

const dest    = String(args.dest);
const checkIn = String(args.in);
const checkOut= String(args.out);
const adults  = parseInt(args.adults) || 1;
const rooms   = parseInt(args.rooms)  || 1;
const BASE    = 'https://www.marriott.com.cn';

function calcNights(d1, d2) {
  return Math.round((new Date(d2) - new Date(d1)) / 86400000);
}

// ─── 地理编码（OpenStreetMap Nominatim，免费无需 API key） ───────────────────

async function geocode(query) {
  const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1&accept-language=zh-CN`;
  const resp = await fetch(url, { headers: { 'User-Agent': 'MarriottSkill/1.0' } });
  const data = await resp.json();
  if (!data.length) throw new Error(`找不到目的地坐标: ${query}`);
  return { lat: data[0].lat, lon: data[0].lon, displayName: data[0].display_name };
}

// ─── Browser helpers ──────────────────────────────────────────────────────────

async function removeOverlay(page) {
  const btn = page.locator('#onetrust-accept-btn-handler, button:has-text("全部接受")').first();
  if (await btn.isVisible({ timeout: 800 }).catch(() => false)) {
    await btn.click();
    await page.waitForTimeout(400);
  }
  await page.evaluate(() =>
    document.querySelectorAll('#onetrust-consent-sdk,.onetrust-pc-dark-filter').forEach(e => e.remove())
  ).catch(() => {});
}

async function fetchAddress(page, hotelUrl) {
  if (!hotelUrl) return '';
  try {
    return await page.evaluate(async (url) => {
      const resp = await fetch(url, { credentials: 'include' });
      const html = await resp.text();
      const addrM = html.match(/<address[^>]*>([\s\S]{0,200}?)<\/address>/i);
      if (addrM) return addrM[1].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().substring(0, 80);
      const ldM = html.match(/"streetAddress"\s*:\s*"([^"]{5,80})"/);
      if (ldM) return ldM[1];
      return '';
    }, hotelUrl);
  } catch (_) { return ''; }
}

// ─── main ─────────────────────────────────────────────────────────────────────

async function main() {
  const nights = calcNights(checkIn, checkOut);

  // 1. 地理编码
  process.stderr.write(`正在查询 "${dest}" 坐标...\n`);
  const geo = await geocode(dest);
  process.stderr.write(`坐标: ${geo.lat}, ${geo.lon} (${geo.displayName.substring(0, 50)})\n`);

  // 2. 连接 Chrome
  let browser;
  try {
    browser = await chromium.connectOverCDP('http://localhost:9222');
  } catch (_) {
    process.stderr.write('❌ 无法连接 Chrome，请先运行: bash launch-chrome.sh\n');
    process.exit(1);
  }

  const ctx   = browser.contexts()[0];
  const cookies = await ctx.cookies();
  const loginState = cookies.find(c => c.name === 's_loginState');
  const stateVal = loginState ? loginState.value : '';
  if (!stateVal || stateVal === 'unauthenticated') {
    process.stderr.write('❌ 未检测到登录状态，请先在 Chrome 中登录万豪\n');
    await browser.close(); process.exit(1);
  }
  if (stateVal === 'remembered') {
    process.stderr.write('登录状态为 remembered，将在跳转后自动完成认证\n');
  }

  const pages = ctx.pages();
  let page = pages.find(p => p.url().includes('marriott')) || pages[0];
  if (!page) page = await ctx.newPage();

  // 3. 直接跳转搜索 URL（无表单操作，不触发 Akamai）
  const params = new URLSearchParams({
    'destinationAddress.destination': dest,
    'destinationAddress.latitude':    geo.lat,
    'destinationAddress.longitude':   geo.lon,
    'destinationAddress.country':     'CN',
    fromDate:         checkIn,
    toDate:           checkOut,
    roomCount:        String(rooms),
    numAdultsPerRoom: String(adults),
    clusterCode:      'none',
    isTransient:      'true',
  });
  const searchUrl = `${BASE}/search/findHotels.mi?${params}`;

  process.stderr.write('跳转搜索页面...\n');
  await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(4000);
  await removeOverlay(page);

  // 页面加载后保存最新 cookies（remembered → authenticated 后更新）
  const freshCookies = await ctx.cookies();
  fs.writeFileSync(path.join(__dirname, 'cookies.json'), JSON.stringify(freshCookies, null, 2));

  const bodySnip = await page.evaluate(() => document.body.innerText.substring(0, 200));
  if (bodySnip.includes('Access Denied') || bodySnip.includes('401')) {
    process.stderr.write('❌ 被 Akamai 拦截，请在 Chrome 中手动刷新页面后重试\n');
    await page.screenshot({ path: path.join(__dirname, 'debug-search-blocked.png') });
    await browser.close(); process.exit(1);
  }

  // 4. 滚动加载酒店卡片
  for (let i = 0; i < 6; i++) {
    await page.evaluate(() => window.scrollBy(0, 600));
    await page.waitForTimeout(400);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(300);

  // 5. 提取酒店（按距离排序，取前4）
  const allHotels = await page.evaluate(() => {
    const seen = new Set();
    return [...document.querySelectorAll('[class*="property-card-container"]')].map(card => {
      const nameEl = card.querySelector('.t-subtitle-xl');
      const name   = nameEl ? nameEl.textContent.trim().split('\n')[0].trim() : '';
      if (!name || seen.has(name)) return null;
      seen.add(name);
      const cardText = card.innerText || '';
      const priceM   = cardText.match(/(\d[\d,]+)\s*CNY/);
      const price    = priceM ? `¥${priceM[1]}/晚` : 'N/A';
      const distEl   = card.querySelector('.reviews-distance-container,[class*="distance"]');
      const distRaw  = distEl ? distEl.textContent.replace(/\s+/g,' ').trim() : '';
      const distance = distRaw.replace(/^[\d.]+\s*\|\s*/, '').trim();
      const linkEl   = card.querySelector('a[href*="propertyCode"],a[href*="/hotels/"]');
      const url      = linkEl ? linkEl.href : '';
      const pidM     = url.match(/propertyCode=([A-Z0-9]+)/i);
      const propertyCode = pidM ? pidM[1] : '';
      const descEl   = card.querySelector('[class*="description"],[class*="desc"],[class*="excerpt"]');
      const desc     = descEl ? descEl.textContent.trim().substring(0, 60) : '';
      return { name, price, distance, url, propertyCode, desc };
    }).filter(Boolean);
  });

  const top4 = allHotels.slice(0, 4);

  // 6. 获取地址
  process.stderr.write('获取酒店地址...\n');
  for (const h of top4) {
    h.address = h.url ? await fetchAddress(page, h.url) : '';
  }

  await browser.close();

  const result = { hotels: top4, checkIn, checkOut, adults, rooms, nights, dest };
  fs.writeFileSync(path.join(__dirname, 'search-results.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result));
}

main().catch(e => { process.stderr.write('错误: ' + e.message + '\n'); process.exit(1); });
