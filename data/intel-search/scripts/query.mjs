#!/usr/bin/env node
/**
 * 简化版搜索 - 查什么都可以，时间任意
 * 用法: node query.mjs [查询] [时间]
 * 示例: node query.mjs 伊朗 3h
 *       node query.mjs 地震
 *       node query.mjs 科技 1h
 *       node query.mjs 裁员
 *       node query.mjs           # 全部概览
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dataDir = process.env.INTEL_DATA_DIR || path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw', 'intel-data');
const briefPath = path.join(dataDir, 'intel-brief.md');
const dataPath = path.join(dataDir, 'captured-data.json');

const args = process.argv.slice(2);
let queryRaw = args[0] || '';
let timeRaw = args[1] || '';

// 若第一个参数像时间（3h、30min），则交换
if (/^\d+[hmd]|^\d+[小时分钟天]|min|h|d$/i.test(queryRaw) && !timeRaw) {
  timeRaw = queryRaw;
  queryRaw = '';
}

/** 任意时间解析，空=不限制 */
function parseTime(s) {
  if (!s) return null;
  const m = s.match(/^(\d*\.?\d+)\s*(分钟|min|小时|h|天|d|周|w)?$/i);
  if (!m) return null;
  const n = parseFloat(m[1]) || 3;
  const u = (m[2] || 'h').toLowerCase();
  if (u === '分钟' || u === 'min') return n * 60 * 1000;
  if (u === '小时' || u === 'h') return n * 3600000;
  if (u === '天' || u === 'd') return n * 86400000;
  if (u === '周' || u === 'w') return n * 7 * 86400000;
  return n * 3600000;
}

const WINDOW_MS = parseTime(timeRaw);
const now = Date.now();
const since = WINDOW_MS ? now - WINDOW_MS : 0;

function toMs(v) {
  if (!v) return 0;
  if (typeof v === 'number') return v < 1e12 ? v * 1000 : v;
  if (typeof v === 'string') return new Date(v).getTime();
  return 0;
}

function ago(ts) {
  const d = now - ts;
  if (d < 60000) return `${Math.round(d / 1000)}s ago`;
  if (d < 3600000) return `${Math.round(d / 60000)}min ago`;
  if (d < 86400000) return `${Math.round(d / 3600000)}h ago`;
  return `${Math.round(d / 86400000)}d ago`;
}

// 主题 → 章节映射（中英文）
const TOPIC_MAP = {
  // 中文
  中东: ['middleeast', '伊朗相关事件', 'Telegram OSINT', 'politics', 'us', 'gov', 'asia', 'energy'],
  伊朗: ['middleeast', '伊朗相关事件', 'Telegram OSINT', 'politics', 'us', 'gov'],
  以色列: ['middleeast', '伊朗相关事件', 'Telegram OSINT', 'intel'],
  黎巴嫩: ['middleeast', '伊朗相关事件', 'Telegram OSINT'],
  地震: ['近期地震'],
  科技: ['tech'],
  人工智能: ['ai'],
  财经: ['finance', 'energy'],
  金融: ['finance'],
  油价: ['energy', 'finance'],
  裁员: ['layoffs'],
  政治: ['politics', 'gov'],
  美国: ['us', 'politics'],
  欧洲: ['europe'],
  亚洲: ['asia'],
  非洲: ['africa'],
  拉美: ['latam'],
  能源: ['energy'],
  智库: ['thinktanks'],
  危机: ['crisis'],
  预测: ['Polymarket'],
  风险: ['战略风险'],
  全部: null,
  概览: null,
  有什么: null,
  // 英文
  iran: ['middleeast', '伊朗相关事件', 'Telegram OSINT', 'politics', 'us', 'gov'],
  'middle east': ['middleeast', '伊朗相关事件', 'Telegram OSINT', 'politics', 'us', 'gov', 'asia', 'energy'],
  israel: ['middleeast', '伊朗相关事件', 'Telegram OSINT', 'intel'],
  lebanon: ['middleeast', '伊朗相关事件', 'Telegram OSINT'],
  earthquake: ['近期地震'],
  tech: ['tech'],
  ai: ['ai'],
  finance: ['finance', 'energy'],
  oil: ['energy', 'finance'],
  layoffs: ['layoffs'],
  politics: ['politics', 'gov'],
  us: ['us', 'politics'],
  europe: ['europe'],
  asia: ['asia'],
  africa: ['africa'],
  latam: ['latam'],
  energy: ['energy'],
  thinktank: ['thinktanks'],
  crisis: ['crisis'],
  polymarket: ['Polymarket'],
  telegram: ['Telegram OSINT'],
  risk: ['战略风险'],
  all: null,
  overview: null,
};

function getSectionsToShow(q) {
  if (!q) return null;
  const qLower = q.toLowerCase();
  const keys = Object.keys(TOPIC_MAP).filter((k) => q.includes(k) || qLower.includes(k.toLowerCase()));
  const key = keys.sort((a, b) => b.length - a.length)[0]; // 最长匹配优先
  if (key && TOPIC_MAP[key] === null) return null; // 全部
  if (key) return TOPIC_MAP[key];
  return null; // 关键词搜索
}

/** 检测用户语言：含中文→zh，否则→en */
function detectLang(q) {
  return /[\u4e00-\u9fff]/.test(q) ? 'zh' : 'en';
}

if (!fs.existsSync(briefPath) || !fs.existsSync(dataPath)) {
  console.log('❌ No data found. Run first: node scripts/fetch.mjs');
  process.exit(1);
}

const brief = fs.readFileSync(briefPath, 'utf-8');
const lines = brief.split('\n');
const query = queryRaw.trim().toLowerCase();

// 解析 brief 为区块
const sections = [];
let current = null;
for (const line of lines) {
  if (line.startsWith('### ') || line.startsWith('## ')) {
    const head = line.match(/^#{2,3}\s+(.+)$/)?.[1] || '';
    current = { head: line, id: head, items: [] };
    sections.push(current);
  } else if (current && line.startsWith('- ')) {
    current.items.push(line);
  }
}

// 确定要显示的区块
let toShow = getSectionsToShow(query);
let keyword = null;
if (!toShow && query) {
  keyword = query; // 关键词搜索
}

function matchesKeyword(line, kw) {
  if (!kw) return true;
  return line.toLowerCase().includes(kw);
}

// 输出
const timeLabel = timeRaw ? timeRaw : 'all';
const queryLabel = query || 'overview';
const userLang = detectLang(queryRaw);
console.log(`🔍 ${queryLabel} · ${timeLabel}`);
console.log(`LANG: ${userLang}\n`); // 提示 Agent：用户用中文问→翻译成中文呈现；用英文问→保持英文

// 若有时间过滤，从 captured-data 取带时间戳的内容
let timeFiltered = [];
try {
  const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
  const capturedAt = data._capturedAt || 0;

  const allItems = [];
  const iran = data['/api/conflict/v1/list-iran-events?_v=7']?.data?.events || [];
  const telegram = data['/api/telegram-feed?limit=50']?.data?.items || [];
  const digest = data['/api/news/v1/list-feed-digest?variant=full&lang=en']?.data?.categories || [];

  iran.forEach((e) => {
    allItems.push({ type: '伊朗', text: e.title, loc: e.locationName, ts: e.timestamp, source: e.sourceUrl });
  });
  telegram.forEach((e) => {
    allItems.push({ type: 'TG', text: (e.text || '').slice(0, 100), ts: e.ts ? toMs(e.ts) : 0, source: e.url });
  });
  for (const [cat, bucket] of Object.entries(digest)) {
    (bucket?.items || []).forEach((e) => {
      allItems.push({ type: cat, text: e.title, ts: e.publishedAt, source: e.link });
    });
  }

  timeFiltered = allItems
    .filter((e) => !since || (e.ts && e.ts >= since))
    .filter((e) => {
      if (!query) return true;
      if (keyword) return (e.text || '').toLowerCase().includes(keyword);
      const cats = toShow || [];
      return cats.some((c) => e.type.toLowerCase().includes(c.toLowerCase()));
    })
    .sort((a, b) => (b.ts || 0) - (a.ts || 0))
    .slice(0, 25)
    .map((e) => ({ ...e, ago: e.ts ? ago(e.ts) : '' }));

  if (timeFiltered.length > 0 && timeRaw) {
    console.log(`--- Time-filtered (${timeFiltered.length} items) ---\n`);
    timeFiltered.forEach((e) => {
      const link = e.source ? `\n  → ${e.source}` : '';
      console.log(`[${e.type}] ${e.text}${e.ago ? ` (${e.ago})` : ''}${link}\n`);
    });
  }
} catch (err) {}

// Output from brief (sections + keyword match)
console.log('--- Summary ---\n');
for (const s of sections) {
  const show = !toShow || toShow.some((t) => s.id.includes(t));
  if (!show) continue;
  const items = keyword ? s.items.filter((i) => matchesKeyword(i, keyword)) : s.items;
  if (items.length === 0 && keyword) continue;
  console.log(s.head);
  items.slice(0, 8).forEach((i) => console.log(i));
  console.log('');
}
