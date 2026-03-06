#!/usr/bin/env node
'use strict';

/**
 * skill-rooms.js — 非交互房型查询，输出 JSON
 * 须先有 selection.json（由 skill 在用户选择酒店后写入）
 * 输出每个房型的多个房价方案（含灵活退改标记、按钮全局序号）
 * 用法: node skill-rooms.js
 */

const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });
const { chromium } = require('playwright');
const fs = require('fs');

const selFile = path.join(__dirname, 'selection.json');
if (!fs.existsSync(selFile)) {
  process.stderr.write('❌ 未找到 selection.json\n');
  process.exit(1);
}
const sel = JSON.parse(fs.readFileSync(selFile));
const BASE = 'https://www.marriott.com.cn';

async function removeOverlay(page) {
  const btn = page.locator('#onetrust-accept-btn-handler,button:has-text("全部接受")').first();
  if (await btn.isVisible({ timeout: 800 }).catch(() => false)) {
    await btn.click();
    await page.waitForTimeout(400);
  }
  await page.evaluate(() =>
    document.querySelectorAll('#onetrust-consent-sdk,.onetrust-pc-dark-filter').forEach(e => e.remove())
  ).catch(() => {});
}

async function connectBrowser() {
  try {
    const b = await chromium.connectOverCDP('http://localhost:9222', { timeout: 3000 });
    const ctx = b.contexts()[0];
    const pages = ctx.pages();
    const page = pages.find(p => p.url().includes('marriott')) || await ctx.newPage();
    return { browser: b, page };
  } catch (_) {}

  const cookiesFile = path.join(__dirname, 'cookies.json');
  if (!fs.existsSync(cookiesFile)) {
    process.stderr.write('❌ 没有 cookies.json 且无法连接 Chrome\n');
    process.exit(1);
  }
  const isLinux = process.platform === 'linux';
  const launchOpts = {
    headless: isLinux,
    args: ['--disable-blink-features=AutomationControlled', '--no-sandbox'],
  };
  if (process.platform === 'darwin') { launchOpts.channel = 'chrome'; launchOpts.headless = false; }

  const b = await chromium.launch(launchOpts);
  const ctx = await b.newContext({
    viewport: { width: 1366, height: 768 },
    locale: 'zh-CN',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7632.117 Safari/537.36',
  });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.chrome = { runtime: {} };
  });
  await ctx.addCookies(JSON.parse(fs.readFileSync(cookiesFile)));
  const page = await ctx.newPage();
  return { browser: b, page };
}

async function main() {
  const { browser, page } = await connectBrowser();
  try {
    await removeOverlay(page);

    if (!sel.propertyCode && !sel.url) {
      process.stderr.write('❌ 缺少 propertyCode 或 url\n');
      await browser.close(); process.exit(1);
    }

    const p = new URLSearchParams({
      propertyCode:     sel.propertyCode,
      fromDate:         sel.checkIn,
      toDate:           sel.checkOut,
      numAdultsPerRoom: sel.adults,
      roomCount:        sel.rooms || 1,
      childrenCount:    0,
      clusterCode:      'none',
      isTransient:      'true',
    });
    const availUrl = `${BASE}/reservation/availabilitySearch.mi?${p}`;

    await page.goto(availUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(4000);
    await removeOverlay(page);

    const bodySnip = await page.evaluate(() => document.body.innerText.substring(0, 200));
    if (bodySnip.includes('Access Denied') || bodySnip.includes('401')) {
      process.stderr.write('❌ 房型页被拦截，请在 Chrome 中手动刷新后重试\n');
      await page.screenshot({ path: path.join(__dirname, 'debug-avail-blocked.png') });
      await browser.close(); process.exit(1);
    }

    // 等待房型卡片加载
    await page.waitForSelector('.rate-card-container', { timeout: 20000 }).catch(() => {
      process.stderr.write('⚠️  未等到 .rate-card-container，尝试继续\n');
    });
    await page.waitForTimeout(1000);

    // 提取所有房型和房价方案
    const rooms = await page.evaluate(() => {
      // 全局"选择"按钮序号（用于 skill-book.js 直接点击）
      const allSelectBtns = [...document.querySelectorAll('button')].filter(b => b.textContent.trim() === '选择');

      const results = [];
      const cards = [...document.querySelectorAll('.rate-card-container')];

      for (const card of cards) {
        const compName = card.getAttribute('data-component-name') || '';
        // 跳过空卡片
        const cardText = card.innerText.trim();
        if (!cardText) continue;

        // 房型名称（第一行文字）
        const name = cardText.split('\n').find(l => l.trim()) || compName;

        // 床型判断
        const isBigBed = /大床|特大床|king/i.test(name + compName);
        const isDoubleBed = /双床|双人床|twin|double|dbdb/i.test(name + compName);
        const bedType = isBigBed ? '大床' : isDoubleBed ? '双床' : '其他';

        // 每个 .rate-details 是一个房价方案
        const rateBlocks = [...card.querySelectorAll('.rate-details')];
        const rates = rateBlocks.map(block => {
          const rateNameEl = block.querySelector('.rate-name');
          const rateName = rateNameEl ? rateNameEl.textContent.trim() : '';
          const isFlexible = /灵活|flexible|free cancel/i.test(rateName);

          // 价格：取 .room-rate（非 d-none 的那个）
          const priceEls = [...block.querySelectorAll('.room-rate')];
          const visiblePrice = priceEls.find(el => !el.classList.contains('d-none'));
          const priceText = visiblePrice ? visiblePrice.textContent.trim() : '';
          const price = parseInt(priceText.replace(/,/g, '')) || 0;

          // 总价
          const totalText = block.innerText.match(/(\d[\d,]+)\s*每间客房总费用/)?.[1] || '';
          const total = parseInt(totalText.replace(/,/g, '')) || 0;

          // 该方案"选择"按钮的全局序号
          const btn = [...block.querySelectorAll('button')].find(b => b.textContent.trim() === '选择');
          const btnGlobalIdx = btn ? allSelectBtns.indexOf(btn) : -1;

          return { rateName, isFlexible, price, total, btnGlobalIdx };
        }).filter(r => r.rateName);

        if (rates.length > 0) {
          results.push({ compName, name: name.substring(0, 60), bedType, rates });
        }
      }
      return results;
    });

    await browser.close();

    const result = {
      rooms,
      hotel:   sel.name,
      checkIn: sel.checkIn,
      checkOut:sel.checkOut,
      nights:  sel.nights,
    };
    fs.writeFileSync(path.join(__dirname, 'rooms-results.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } catch (err) {
    process.stderr.write('错误: ' + err.message + '\n');
    await page.screenshot({ path: path.join(__dirname, 'debug-error.png') }).catch(() => {});
    await browser.close();
    process.exit(1);
  }
}

main().catch(e => { process.stderr.write('错误: ' + e.message + '\n'); process.exit(1); });
