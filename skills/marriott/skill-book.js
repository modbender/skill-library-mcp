#!/usr/bin/env node
'use strict';

/**
 * skill-book.js — 非交互预订，由 Claude skill 在用户确认后调用
 * 须先有 selection.json + rooms-results.json（由 skill-select.js / skill-rooms.js 生成）
 * 用法: node skill-book.js --btn <btnGlobalIdx>
 */

const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });
const { chromium } = require('playwright');
const minimist = require('minimist');
const fs = require('fs');

const args      = minimist(process.argv.slice(2));
const btnIdx    = parseInt(args.btn);
if (isNaN(btnIdx) || btnIdx < 0) {
  process.stderr.write('用法: node skill-book.js --btn <btnGlobalIdx>\n');
  process.exit(1);
}

const selFile   = path.join(__dirname, 'selection.json');
const roomsFile = path.join(__dirname, 'rooms-results.json');
if (!fs.existsSync(selFile))   { process.stderr.write('❌ 未找到 selection.json\n');   process.exit(1); }
if (!fs.existsSync(roomsFile)) { process.stderr.write('❌ 未找到 rooms-results.json\n'); process.exit(1); }

const sel       = JSON.parse(fs.readFileSync(selFile));
const roomsData = JSON.parse(fs.readFileSync(roomsFile));

// 根据 btnGlobalIdx 找到对应的房型和房价方案
let selectedRoom = null, selectedRate = null;
for (const room of roomsData.rooms) {
  for (const rate of room.rates) {
    if (rate.btnGlobalIdx === btnIdx) { selectedRoom = room; selectedRate = rate; break; }
  }
  if (selectedRoom) break;
}
if (!selectedRoom) {
  process.stderr.write(`❌ btnGlobalIdx ${btnIdx} 未在 rooms-results.json 中找到\n`);
  process.exit(1);
}

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

async function safeClick(loc) {
  try { await loc.click({ timeout: 5000 }); }
  catch (_) { await loc.dispatchEvent('click'); }
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

    // ── 1. 打开酒店可用性页面 ────────────────────────────────────────────────
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
    const availUrl = sel.propertyCode
      ? `${BASE}/reservation/availabilitySearch.mi?${p}`
      : sel.url;

    await page.goto(availUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(3000);
    await removeOverlay(page);

    const bodySnip = await page.evaluate(() => document.body.innerText.substring(0, 300));
    if (bodySnip.includes('Access Denied')) {
      process.stderr.write('❌ 房型页被拦截\n');
      await page.screenshot({ path: path.join(__dirname, 'debug-avail-blocked.png') });
      await browser.close(); process.exit(1);
    }

    // ── 2. 等待房型加载，点击指定"选择"按钮（按全局序号） ────────────────────
    await page.waitForSelector('.rate-card-container', { timeout: 20000 }).catch(() => {});
    await page.waitForTimeout(1000);

    const clicked = await page.evaluate((idx) => {
      const btns = [...document.querySelectorAll('button')].filter(b => b.textContent.trim() === '选择');
      const btn = btns[idx];
      if (btn) { btn.click(); return true; }
      return false;
    }, btnIdx);

    if (!clicked) {
      process.stderr.write(`❌ 未找到第 ${btnIdx} 个"选择"按钮\n`);
      await page.screenshot({ path: path.join(__dirname, 'debug-no-btn.png') });
      await browser.close(); process.exit(1);
    }

    // ── 3. 等待跳转到结账/宾客信息页 ────────────────────────────────────────
    try { await page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }); } catch (_) {}
    await page.waitForTimeout(3000);
    await removeOverlay(page);
    await page.screenshot({ path: path.join(__dirname, 'debug-checkout.png') });

    // ── 4. 处理支付确认（如有"需要更正"提示，先选默认支付方式） ──────────────
    const reviewText = await page.evaluate(() => document.body.innerText);
    if (reviewText.includes('需要更正') || reviewText.includes('完成您的预订')) {
      process.stderr.write('ℹ️  检测到支付确认页面，尝试选择默认支付方式...\n');
      await page.screenshot({ path: path.join(__dirname, 'debug-payment-page.png') });

      const paymentClicked = await page.evaluate(() => {
        const radios = [...document.querySelectorAll('input[type="radio"]')]
          .filter(r => {
            const label = r.closest('label') || document.querySelector(`label[for="${r.id}"]`);
            const text = (label ? label.innerText : '') + r.name + r.id;
            return /card|credit|信用|payment|pay/i.test(text);
          });
        if (radios.length > 0) { radios[0].click(); return 'radio:' + (radios[0].id || radios[0].name); }

        const btns = [...document.querySelectorAll('button, a')];
        const useBtn = btns.find(b => /使用此卡|使用|Use this card/i.test(b.textContent));
        if (useBtn) { useBtn.click(); return 'use-btn:' + useBtn.textContent.trim(); }

        const anyRadio = document.querySelector('input[type="radio"]');
        if (anyRadio) { anyRadio.click(); return 'any-radio'; }

        return null;
      });
      if (paymentClicked) {
        process.stderr.write(`ℹ️  已选择支付方式: ${paymentClicked}\n`);
      } else {
        process.stderr.write('⚠️  未找到支付选项，直接尝试点击"立即预订"\n');
      }
      await page.waitForTimeout(1500);
    }

    // ── 5. 点击最终"立即预订"按钮 ─────────────────────────────────────────────
    const confirmBtn = page.locator(
      'button.m-button-l:has-text("立即预订"),button:has-text("立即预订"),' +
      'button:has-text("确认预订"),button:has-text("提交"),button:has-text("完成预订"),' +
      'button:has-text("Reserve Now"),button[class*="book-now"],button[class*="confirm"]'
    ).first();
    if (await confirmBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await safeClick(confirmBtn);
    } else {
      process.stderr.write('⚠️  未找到确认按钮，请查看 debug-checkout.png\n');
    }

    // ── 6. 等待确认页，提取确认号 ────────────────────────────────────────────
    try { await page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 30000 }); } catch (_) {}
    await page.waitForTimeout(4000);
    await removeOverlay(page);
    await page.screenshot({ path: path.join(__dirname, 'debug-confirmation.png') });

    const confirmData = await page.evaluate(() => {
      const text = document.body.innerText;
      const confM = text.match(/确认[号码]\s*[#＃]?\s*(\d{6,12})/i) ||
                    text.match(/确认[号码][:：\s#＃]*([A-Z0-9]{6,12})/i) ||
                    text.match(/Confirmation\s*[#No.:：]*\s*([A-Z0-9]{6,12})/i) ||
                    text.match(/订单[号码][:：\s]*([A-Z0-9]{6,12})/i) ||
                    text.match(/\b([A-Z]{2,4}\d{6,10})\b/);
      const priceM = text.match(/总[计价][费]?[:：\s]*[¥￥]?\s*(\d[\d,]+)/i) ||
                     text.match(/[¥￥]\s*(\d[\d,]+)\s*(CNY|元)/i);
      return {
        confirmNumber: confM  ? confM[1]  : '',
        totalPrice:    priceM ? priceM[1] : '',
        pageUrl:       window.location.href,
        snippet:       text.split('\n').filter(l => l.trim()).slice(0, 20).join('\n').substring(0, 600),
      };
    });

    await browser.close();

    const result = {
      success:       !!confirmData.confirmNumber,
      confirmNumber: confirmData.confirmNumber,
      totalPrice:    confirmData.totalPrice || String(selectedRate.total),
      hotel:         sel.name,
      room:          selectedRoom.name,
      rateName:      selectedRate.rateName,
      pricePerNight: selectedRate.price,
      checkIn:       sel.checkIn,
      checkOut:      sel.checkOut,
      nights:        sel.nights,
      pageUrl:       confirmData.pageUrl,
      snippet:       confirmData.snippet,
      bookedAt:      new Date().toISOString(),
    };

    fs.writeFileSync(path.join(__dirname, 'confirmation.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } catch (err) {
    process.stderr.write('错误: ' + err.message + '\n');
    await page.screenshot({ path: path.join(__dirname, 'debug-error.png') }).catch(() => {});
    await browser.close();
    process.exit(1);
  }
}

main().catch(e => { process.stderr.write('错误: ' + e.message + '\n'); process.exit(1); });
