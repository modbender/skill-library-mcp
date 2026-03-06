#!/usr/bin/env node
// Lookup airport IATA codes via Amadeus API
const API_KEY = process.env.AMADEUS_API_KEY || 'nK2MnRGXXe9hL9leXxitRTcunkuTGxvK';
const API_SECRET = process.env.AMADEUS_API_SECRET || '8YBuqJY1txzZN4l0';
const BASE = process.env.AMADEUS_BASE_URL || 'https://test.api.amadeus.com';

const keyword = process.argv[2];
if (!keyword) {
  console.error('Usage: airports.mjs <city or airport name>');
  console.error('Example: airports.mjs 揭阳');
  process.exit(1);
}

// Common Chinese city → IATA mappings (Amadeus may not support Chinese search well)
const CN_AIRPORTS = {
  '北京': ['PEK', 'PKX'], '上海': ['PVG', 'SHA'], '广州': ['CAN'], '深圳': ['SZX'],
  '成都': ['CTU', 'TFU'], '重庆': ['CKG'], '杭州': ['HGH'], '南京': ['NKG'],
  '武汉': ['WUH'], '西安': ['XIY'], '长沙': ['CSX'], '昆明': ['KMG'],
  '厦门': ['XMN'], '青岛': ['TAO'], '大连': ['DLC'], '天津': ['TSN'],
  '郑州': ['CGO'], '沈阳': ['SHE'], '哈尔滨': ['HRB'], '海口': ['HAK'],
  '三亚': ['SYX'], '贵阳': ['KWE'], '南宁': ['NNG'], '福州': ['FOC'],
  '济南': ['TNA'], '合肥': ['HFE'], '太原': ['TYN'], '乌鲁木齐': ['URC'],
  '兰州': ['LHW'], '银川': ['INC'], '西宁': ['XNN'], '呼和浩特': ['HET'],
  '拉萨': ['LXA'], '珠海': ['ZUH'], '温州': ['WNZ'], '宁波': ['NGB'],
  '无锡': ['WUX'], '揭阳': ['SWA'], '潮汕': ['SWA'], '汕头': ['SWA'],
  '香港': ['HKG'], '澳门': ['MFM'], '台北': ['TPE', 'TSA'],
  // International
  '东京': ['NRT', 'HND'], '首尔': ['ICN', 'GMP'], '新加坡': ['SIN'],
  '曼谷': ['BKK', 'DMK'], '吉隆坡': ['KUL'], '伦敦': ['LHR', 'LGW'],
  '纽约': ['JFK', 'EWR'], '洛杉矶': ['LAX'], '巴黎': ['CDG', 'ORY'],
};

// Check local mapping first
const local = CN_AIRPORTS[keyword];
if (local) {
  console.log(`${keyword} → ${local.join(', ')}`);
  process.exit(0);
}

// If it's already an IATA code
if (/^[A-Z]{3}$/i.test(keyword)) {
  console.log(keyword.toUpperCase());
  process.exit(0);
}

// Fallback: Amadeus API
async function getToken() {
  const res = await fetch(`${BASE}/v1/security/oauth2/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=client_credentials&client_id=${API_KEY}&client_secret=${API_SECRET}`,
  });
  return (await res.json()).access_token;
}

const token = await getToken();
const res = await fetch(`${BASE}/v1/reference-data/locations?subType=AIRPORT,CITY&keyword=${encodeURIComponent(keyword)}&page[limit]=5`, {
  headers: { 'Authorization': `Bearer ${token}` },
});
const data = await res.json();

if (data.data?.length) {
  for (const loc of data.data) {
    console.log(`${loc.name} (${loc.iataCode}) - ${loc.address?.cityName || ''}, ${loc.address?.countryName || ''}`);
  }
} else {
  console.error(`No airports found for: ${keyword}`);
  process.exit(1);
}
