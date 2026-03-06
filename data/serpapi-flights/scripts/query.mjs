#!/usr/bin/env node
// Query Google Flights via SerpApi
import { parseArgs } from 'node:util';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Load API key from env or config
const API_KEY = process.env.SERPAPI_KEY || process.env.SERPAPI_API_KEY || '';
if (!API_KEY) {
  console.error('Error: SERPAPI_KEY not set');
  process.exit(1);
}

const { values, positionals } = parseArgs({
  options: {
    date: { type: 'string', short: 'd' },
    return: { type: 'string', short: 'r' },
    class: { type: 'string', short: 'c', default: '1' }, // 1=economy, 2=premium, 3=business, 4=first
    adults: { type: 'string', short: 'a', default: '1' },
    currency: { type: 'string', default: 'CNY' },
    lang: { type: 'string', default: 'zh-CN' },
    direct: { type: 'boolean', default: false },
    json: { type: 'boolean', default: false },
    all: { type: 'boolean', default: false }, // query all cabin classes
  },
  allowPositionals: true,
  strict: false,
});

const [fromCode, toCode] = positionals;
if (!fromCode || !toCode) {
  console.error('Usage: query.mjs <FROM_IATA> <TO_IATA> [-d YYYY-MM-DD] [options]');
  console.error('');
  console.error('Examples:');
  console.error('  query.mjs HKG PVG -d 2026-02-25');
  console.error('  query.mjs HKG PVG -d 2026-02-25 -c 3          # business class');
  console.error('  query.mjs HKG PVG -d 2026-02-25 --all          # all cabin classes');
  console.error('  query.mjs HKG PVG -d 2026-02-25 --direct        # non-stop only');
  console.error('  query.mjs HKG PVG -d 2026-02-25 -r 2026-03-01   # round trip');
  console.error('');
  console.error('Cabin classes: 1=economy, 2=premium economy, 3=business, 4=first');
  process.exit(1);
}

const date = values.date || new Date().toLocaleDateString('sv-SE', { timeZone: 'Asia/Shanghai' });
const from = fromCode.toUpperCase();
const to = toCode.toUpperCase();

// Chinese city name → IATA helper
const CN_MAP = {
  '北京': 'PEK', '上海': 'PVG', '广州': 'CAN', '深圳': 'SZX', '成都': 'CTU',
  '重庆': 'CKG', '杭州': 'HGH', '南京': 'NKG', '武汉': 'WUH', '西安': 'XIY',
  '长沙': 'CSX', '昆明': 'KMG', '厦门': 'XMN', '青岛': 'TAO', '大连': 'DLC',
  '天津': 'TSN', '郑州': 'CGO', '沈阳': 'SHE', '哈尔滨': 'HRB', '海口': 'HAK',
  '三亚': 'SYX', '贵阳': 'KWE', '南宁': 'NNG', '福州': 'FOC', '济南': 'TNA',
  '合肥': 'HFE', '太原': 'TYN', '乌鲁木齐': 'URC', '兰州': 'LHW', '珠海': 'ZUH',
  '温州': 'WNZ', '宁波': 'NGB', '无锡': 'WUX', '揭阳': 'SWA', '潮汕': 'SWA',
  '汕头': 'SWA', '香港': 'HKG', '澳门': 'MFM', '台北': 'TPE',
};

function resolveIATA(code) {
  return CN_MAP[code] || code.toUpperCase();
}

const CLASS_NAMES = { '1': '经济舱', '2': '超级经济舱', '3': '商务舱', '4': '头等舱' };

async function queryFlights(travelClass) {
  const params = new URLSearchParams({
    engine: 'google_flights',
    departure_id: resolveIATA(from),
    arrival_id: resolveIATA(to),
    outbound_date: date,
    currency: values.currency,
    hl: values.lang,
    type: '2', // one-way
    travel_class: travelClass,
    adults: values.adults,
    api_key: API_KEY,
  });

  if (values.return) {
    params.set('type', '1'); // round-trip
    params.set('return_date', values.return);
  }
  if (values.direct) params.set('stops', '0');

  const url = `https://serpapi.com/search.json?${params}`;
  console.error(`Querying ${CLASS_NAMES[travelClass] || 'economy'}: ${from} → ${to} on ${date}...`);

  const res = await fetch(url);
  const data = await res.json();

  if (data.error) {
    console.error('API Error:', data.error);
    return [];
  }

  const best = data.best_flights || [];
  const other = data.other_flights || [];
  return [...best.map(f => ({ ...f, _best: true })), ...other.map(f => ({ ...f, _best: false }))];
}

function fmtDuration(min) {
  const h = Math.floor(min / 60);
  const m = min % 60;
  return `${h}h${m.toString().padStart(2, '0')}m`;
}

function fmtTime(dt) {
  return dt?.split(' ')[1]?.slice(0, 5) || '--';
}

function fmtDate(dt) {
  return dt?.split(' ')[0] || '';
}

// Query one or all cabin classes
const classesToQuery = values.all ? ['1', '3'] : [values.class];
const allResults = [];

for (const cls of classesToQuery) {
  const flights = await queryFlights(cls);
  for (const f of flights) {
    f._class = cls;
    f._className = CLASS_NAMES[cls] || cls;
  }
  allResults.push(...flights);
}

if (values.json) {
  console.log(JSON.stringify(allResults, null, 2));
  process.exit(0);
}

if (allResults.length === 0) {
  console.log(`No flights found: ${from} → ${to} on ${date}`);
  process.exit(0);
}

// Group by class
const byClass = {};
for (const f of allResults) {
  const key = f._className;
  if (!byClass[key]) byClass[key] = [];
  byClass[key].push(f);
}

for (const [className, flights] of Object.entries(byClass)) {
  console.log(`\n## ${className} | ${from} → ${to} | ${date} | ${flights.length}个航班\n`);
  console.log('| 航空公司 | 航班号 | 出发→到达 | 飞行时间 | 经停 | 价格 | 机型 | 延误 |');
  console.log('|----------|--------|-----------|----------|------|------|------|------|');

  // Sort by price
  flights.sort((a, b) => (a.price || 99999) - (b.price || 99999));

  for (const f of flights) {
    const segs = f.flights || [];
    const first = segs[0];
    const last = segs[segs.length - 1];
    if (!first) continue;

    const airline = first.airline || '?';
    const fno = first.flight_number || '?';
    const dep = fmtTime(first.departure_airport?.time);
    const arr = fmtTime(last.arrival_airport?.time);
    const depDate = fmtDate(first.departure_airport?.time);
    const arrDate = fmtDate(last.arrival_airport?.time);
    const crossDay = arrDate > depDate ? '+1' : '';
    const duration = fmtDuration(f.total_duration || 0);
    const stops = segs.length - 1;
    const stopsText = stops === 0 ? '直飞' : `经停${stops}次`;
    const price = f.price ? `¥${f.price}` : '待查';
    const plane = first.airplane || '';
    const delayed = first.often_delayed_by_over_30_min ? '⚠️' : '';

    console.log(`| ${airline} | ${fno} | ${dep}→${arr}${crossDay} | ${duration} | ${stopsText} | ${price} | ${plane} | ${delayed} |`);
  }
}

console.log(`\n> 数据来源: Google Flights (SerpApi) | 货币: ${values.currency}`);
