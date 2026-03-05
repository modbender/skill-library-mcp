#!/usr/bin/env node
// Query flights via Amadeus API
import { parseArgs } from 'node:util';

const API_KEY = process.env.AMADEUS_API_KEY || 'nK2MnRGXXe9hL9leXxitRTcunkuTGxvK';
const API_SECRET = process.env.AMADEUS_API_SECRET || '8YBuqJY1txzZN4l0';
const BASE = process.env.AMADEUS_BASE_URL || 'https://test.api.amadeus.com'; // Change to https://api.amadeus.com for production

const { values, positionals } = parseArgs({
  options: {
    date: { type: 'string', short: 'd' },
    adults: { type: 'string', short: 'a', default: '1' },
    class: { type: 'string', short: 'c', default: '' }, // ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
    direct: { type: 'boolean', default: false },
    max: { type: 'string', short: 'n', default: '20' },
    json: { type: 'boolean', default: false },
    currency: { type: 'string', default: 'CNY' },
  },
  allowPositionals: true,
  strict: false,
});

const [from, to] = positionals;
if (!from || !to) {
  console.error('Usage: query.mjs <FROM_IATA> <TO_IATA> [-d YYYY-MM-DD] [--direct] [-c ECONOMY|BUSINESS]');
  console.error('Example: query.mjs HKG PVG -d 2026-02-25');
  console.error('         query.mjs SWA HGH -d 2026-02-24 --direct');
  process.exit(1);
}

const date = values.date || new Date().toLocaleDateString('sv-SE', { timeZone: 'Asia/Shanghai' });

// Get OAuth token
async function getToken() {
  const res = await fetch(`${BASE}/v1/security/oauth2/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=client_credentials&client_id=${API_KEY}&client_secret=${API_SECRET}`,
  });
  const data = await res.json();
  if (!data.access_token) {
    console.error('Auth failed:', JSON.stringify(data));
    process.exit(1);
  }
  return data.access_token;
}

// Search flights
async function searchFlights(token) {
  const params = new URLSearchParams({
    originLocationCode: from.toUpperCase(),
    destinationLocationCode: to.toUpperCase(),
    departureDate: date,
    adults: values.adults,
    max: values.max,
    currencyCode: values.currency,
  });
  if (values.direct) params.set('nonStop', 'true');
  if (values.class) params.set('travelClass', values.class.toUpperCase());

  const url = `${BASE}/v2/shopping/flight-offers?${params}`;
  console.error(`Searching: ${from.toUpperCase()} → ${to.toUpperCase()} on ${date}...`);

  const res = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  const data = await res.json();

  if (data.errors) {
    console.error('API Error:', JSON.stringify(data.errors, null, 2));
    process.exit(1);
  }
  return data;
}

// Format duration: PT2H30M → 2h30m
function fmtDuration(iso) {
  if (!iso) return '--';
  return iso.replace('PT', '').replace('H', 'h').replace('M', 'm').toLowerCase();
}

// Format time: 2026-02-25T13:15:00 → 13:15
function fmtTime(dt) {
  if (!dt) return '--';
  return dt.split('T')[1]?.slice(0, 5) || dt;
}

function fmtDate(dt) {
  if (!dt) return '';
  return dt.split('T')[0];
}

const token = await getToken();
const result = await searchFlights(token);

if (values.json) {
  console.log(JSON.stringify(result, null, 2));
  process.exit(0);
}

const offers = result.data || [];
const dictionaries = result.dictionaries || {};
const carriers = dictionaries.carriers || {};

if (offers.length === 0) {
  console.log(`No flights found: ${from.toUpperCase()} → ${to.toUpperCase()} on ${date}`);
  process.exit(0);
}

console.log(`\n${from.toUpperCase()} → ${to.toUpperCase()} | ${date} | ${offers.length} offers\n`);
console.log(`| 航空公司 | 航班号 | 出发→到达 | 飞行时间 | 经停 | 价格(${values.currency}) | 舱位 | 余座 |`);
console.log('|----------|--------|-----------|----------|------|--------|------|------|');

for (const offer of offers) {
  const itin = offer.itineraries?.[0];
  if (!itin) continue;

  const segments = itin.segments || [];
  const first = segments[0];
  const last = segments[segments.length - 1];

  const airline = carriers[first?.carrierCode] || first?.carrierCode || '?';
  const flightNo = `${first?.carrierCode}${first?.number}`;
  const depart = fmtTime(first?.departure?.at);
  const arrive = fmtTime(last?.arrival?.at);
  const duration = fmtDuration(itin.duration);
  const stops = segments.length - 1;
  const stopsText = stops === 0 ? '直飞' : `经停${stops}次`;
  const price = `${offer.price?.total || '?'}`;
  const cabin = first?.travelerPricings?.[0]?.fareDetailsBySegment?.[0]?.cabin ||
    offer.travelerPricings?.[0]?.fareDetailsBySegment?.[0]?.cabin || '';
  const seats = offer.numberOfBookableSeats || '?';

  // Cross-day indicator
  const departDate = fmtDate(first?.departure?.at);
  const arriveDate = fmtDate(last?.arrival?.at);
  const crossDay = arriveDate > departDate ? '+1' : '';

  console.log(`| ${airline} | ${flightNo} | ${depart}→${arrive}${crossDay} | ${duration} | ${stopsText} | ¥${price} | ${cabin} | ${seats} |`);
}

console.log(`\n> 数据来源: Amadeus ${BASE.includes('test') ? '(测试环境-模拟数据)' : '(生产环境-实时数据)'}`);
