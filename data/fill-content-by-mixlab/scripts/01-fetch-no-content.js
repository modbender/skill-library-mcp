#!/usr/bin/env node

/**
 * Fill Content: 获取无正文条目
 * - 拉取 https://www.mixdao.world/api/latest（需环境变量 MIXDAO_API_KEY，Bearer token）
 * - 过滤出 hasContent === false 的条目，写入 temp/fill-content-{date}.json
 * - 输出 [FILE PATH] <path> 供后续步骤使用
 *
 * 用法: node scripts/01-fetch-no-content.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import https from 'https';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const API_URL = 'https://www.mixdao.world/api/latest';
const SKIP_KEYS = new Set(['sources', 'sourceLabels', 'hasMore', 'date']);

const DATE_TZ = 'Asia/Shanghai';

function getTodayDateStrInTz(tz) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: tz,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());
}

function fetchLatest() {
  return new Promise((resolve, reject) => {
    const apiKey = process.env.MIXDAO_API_KEY;
    if (!apiKey) {
      reject(new Error('MIXDAO_API_KEY is not set.'));
      return;
    }
    const url = new URL(API_URL);
    const opts = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method: 'GET',
      headers: { Authorization: `Bearer ${apiKey}` },
    };
    const req = https.request(opts, (res) => {
      res.setTimeout(15000, () => {
        req.destroy();
        reject(new Error('API 请求超时'));
      });
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        const body = Buffer.concat(chunks).toString('utf8');
        if (res.statusCode !== 200) {
          reject(new Error(`API returned ${res.statusCode}: ${body.slice(0, 200)}`));
          return;
        }
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(new Error('Invalid JSON from API: ' + e.message));
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

/**
 * 从 API 响应中收集所有 story，再过滤出 hasContent === false 的条目。
 * 响应可能是 { stories } 或 { hn: [], arxiv: [], ... }。
 */
function collectNoContentItems(raw) {
  let list = [];
  if (Array.isArray(raw.stories) && raw.stories.length > 0) {
    list = raw.stories;
  } else {
    for (const key of Object.keys(raw)) {
      if (SKIP_KEYS.has(key)) continue;
      const arr = Array.isArray(raw[key]) ? raw[key] : [];
      list = list.concat(arr);
    }
  }
  const noContent = list.filter((item) => item && item.hasContent === false);
  return noContent.map((item) => ({
    cachedStoryId: item.cachedStoryId || item.id,
    url: item.url || item.link || '',
    title: (item.title || item.translatedTitle || '').replace(/&#8217;/g, "'"),
    translatedTitle: (item.translatedTitle || item.title || '').replace(/&#8217;/g, "'"),
    text: (item.text || '').trim(),
  }));
}

function main() {
  fetchLatest()
    .then((raw) => {
      const date = raw.date || getTodayDateStrInTz(DATE_TZ);
      const items = collectNoContentItems(raw);
      const tempFileName = `fill-content-${date}.json`;
      const tempDir = path.join(__dirname, '..', 'temp');
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
      }
      const tempFilePath = path.join(tempDir, tempFileName);
      const outputData = { date, items };
      fs.writeFileSync(tempFilePath, JSON.stringify(outputData, null, 2), 'utf8');
      console.log(`[FILE PATH] ${tempFilePath}`);
      if (items.length === 0) {
        console.error('01-fetch-no-content.js: 当前无 hasContent 为 false 的条目');
      }
    })
    .catch((err) => {
      console.error('Error:', err.message);
      process.exit(1);
    });
}

main();
