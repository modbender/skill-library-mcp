#!/usr/bin/env node
/**
 * 抓取 World Monitor 数据并生成摘要
 * 输出到 ~/.openclaw/intel-data/
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dataDir = process.env.INTEL_DATA_DIR || path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw', 'intel-data');
const CAPTURE_URL = 'https://worldmonitor.app';
const WAIT_MS = 12000;

function shouldCapture(url) {
  return (
    url.includes('/api/') ||
    url.includes('worldmonitor') ||
    url.includes('polymarket') ||
    url.includes('/news/') ||
    url.includes('/intelligence/') ||
    url.includes('/market/') ||
    url.includes('/conflict/') ||
    url.includes('list-feed-digest') ||
    url.includes('listFeedDigest') ||
    url.includes('list-earthquakes') ||
    url.includes('get-macro-signals')
  );
}

async function main() {
  fs.mkdirSync(dataDir, { recursive: true });
  console.log('🚀 Launching browser, loading World Monitor...');
  const browser = await chromium.launch({ headless: true });
  const captured = new Map();

  try {
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      viewport: { width: 1280, height: 720 },
    });
    const page = await context.newPage();

    page.on('response', async (response) => {
      const url = response.url();
      if (!shouldCapture(url)) return;
      try {
        const contentType = response.headers()['content-type'] || '';
        if (!contentType.includes('json') && !contentType.includes('application/json')) return;
        const body = await response.text();
        let data = body;
        try {
          data = JSON.parse(body);
        } catch {}
        captured.set(url, { status: response.status(), data });
      } catch (e) {}
    });

    await page.goto(CAPTURE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.log('📄 Page loaded, waiting for API data...');
    await page.waitForTimeout(WAIT_MS);
    await browser.close();
  } catch (err) {
    console.error('Error:', err.message);
    await browser.close();
    process.exit(1);
  }

  const results = { _capturedAt: Date.now() };
  for (const [url, { status, data }] of captured) {
    results[url.replace(/^https?:\/\/[^/]+/, '')] = { status, data };
  }

  const dataPath = path.join(dataDir, 'captured-data.json');
  fs.writeFileSync(dataPath, JSON.stringify(results, null, 2), 'utf-8');
  console.log(`\n💾 Data saved: ${dataPath}`);

  // 生成摘要
  const lines = [
    '# 情报摘要 (Intel Brief)\n',
    `生成时间: ${new Date().toISOString()}\n`,
    '## 快速索引（按主题跳转）\n',
    '| 主题 | 章节 | 说明 |',
    '|------|------|------|',
    '| 伊朗/中东 | ## 伊朗相关事件 | 现场事件、空袭、冲突 |',
    '| 新闻头条 | ## 新闻头条 | 按地区分类，含链接 |',
    '| 地震 | ## 近期地震 | M4.5+，含 USGS 链接 |',
    '| Telegram | ## Telegram OSINT | 频道情报，含原文链接 |',
    '| 预测市场 | ## Polymarket | 地缘/政治预测，含市场链接 |',
    '| 战略风险 | ## 战略风险 | 全球风险评分 |',
    '',
  ];

  const d = results;
  const digest = d['/api/news/v1/list-feed-digest?variant=full&lang=en'];
  if (digest?.data?.categories) {
    lines.push('## 新闻头条\n');
    for (const [cat, bucket] of Object.entries(digest.data.categories)) {
      if (bucket?.items?.length) {
        lines.push(`### ${cat}\n`);
        bucket.items.slice(0, 5).forEach((item) => {
          const link = item.link ? ` [原文](${item.link})` : '';
          lines.push(`- **${item.title}** (${item.source})${link}`);
        });
        lines.push('');
      }
    }
  }

  const bootstrap = d['/api/bootstrap'];
  if (bootstrap?.data?.data?.earthquakes?.earthquakes?.length) {
    lines.push('## 近期地震 (M4.5+)\n');
    bootstrap.data.data.earthquakes.earthquakes.slice(0, 10).forEach((e) => {
      const url = e.sourceUrl ? ` [详情](${e.sourceUrl})` : '';
      lines.push(`- M${e.magnitude} ${e.place}${url}`);
    });
    lines.push('');
  }

  const iranEvents = d['/api/conflict/v1/list-iran-events?_v=7'];
  if (iranEvents?.data?.events?.length) {
    lines.push('## 伊朗相关事件\n');
    iranEvents.data.events.slice(0, 15).forEach((e) => {
      const title = e.title || e.description || e.summary || JSON.stringify(e).slice(0, 80);
      const loc = e.locationName ? ` (${e.locationName})` : '';
      const url = e.sourceUrl ? ` [来源](${e.sourceUrl})` : '';
      lines.push(`- ${title}${loc}${url}`);
    });
    lines.push('');
  }

  const telegram = d['/api/telegram-feed?limit=50'];
  if (telegram?.data?.items?.length) {
    lines.push('## Telegram OSINT\n');
    telegram.data.items.slice(0, 10).forEach((item) => {
      const raw = (item.text || item.content || '').replace(/\s+/g, ' ').trim();
      const text = raw.slice(0, 120);
      const channel = item.channel ? `[@${item.channel}] ` : '';
      const url = item.url ? ` [原文](${item.url})` : '';
      if (text) lines.push(`- ${channel}${text}${url}`);
    });
    lines.push('');
  }

  const polyKeys = Object.keys(d).filter((k) => k.includes('polymarket'));
  if (polyKeys.length) {
    const first = d[polyKeys[0]]?.data;
    if (Array.isArray(first) && first[0]) {
      lines.push('## Polymarket 预测市场\n');
      first.slice(0, 5).forEach((e) => {
        const q = e.question || e.title || e.markets?.[0]?.question;
        const slug = e.slug || e.markets?.[0]?.slug;
        const url = slug ? ` [市场](https://polymarket.com/event/${slug})` : '';
        const desc = (e.description || e.markets?.[0]?.description || '').slice(0, 80);
        const hint = desc ? ` — ${desc.replace(/\n/g, ' ')}...` : '';
        if (q) lines.push(`- ${q}${url}${hint}`);
      });
      lines.push('');
    }
  }

  const risk = d['/api/intelligence/v1/get-risk-scores'];
  if (risk?.data?.strategicRisks) {
    lines.push('## 战略风险\n');
    lines.push(JSON.stringify(risk.data.strategicRisks, null, 2).slice(0, 500));
  }

  const briefPath = path.join(dataDir, 'intel-brief.md');
  fs.writeFileSync(briefPath, lines.join('\n'), 'utf-8');
  console.log(`✅ Brief saved: ${briefPath}`);
  console.log(`   ${lines.filter((l) => l.startsWith('-')).length} items`);
  console.log(`\nDone. Run query to search.`);
}

main();
