#!/usr/bin/env node
/**
 * Chicago Metra Commuter Rail — OpenClaw Skill
 * Real-time train arrivals (GTFS-RT protobuf), vehicle positions, service alerts,
 * schedule info, and fare calculation for all 11 Metra lines.
 *
 * SECURITY MANIFEST
 *   Environment variables: METRA_API_KEY (required for all GTFS-RT feeds)
 *   External endpoints:    gtfspublic.metrarr.com (GTFS-RT, Bearer token auth)
 *                          schedules.metrarail.com (GTFS static, no auth)
 *   Local files written:   ~/.metra/gtfs/ (GTFS static data cache)
 *   Local files read:      ~/.metra/gtfs/*.txt (GTFS CSV files)
 *   User input handling:   Used for local filtering only, never interpolated into
 *                          shell commands
 */

import { parseArgs } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';

// ---------------------------------------------------------------------------
// Load .env file (if present) — no external dependencies
// ---------------------------------------------------------------------------
function loadEnv() {
  const envPath = path.join(path.dirname(new URL(import.meta.url).pathname), '..', '.env');
  if (!fs.existsSync(envPath)) return;
  const content = fs.readFileSync(envPath, 'utf-8');
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    const val = trimmed.slice(eq + 1).trim();
    if (!process.env[key]) process.env[key] = val;
  }
}
loadEnv();

// ---------------------------------------------------------------------------
// API Configuration
// ---------------------------------------------------------------------------
const METRA_API_KEY = process.env.METRA_API_KEY || '';

const FEED_BASE = 'https://gtfspublic.metrarr.com/gtfs/public';
const FEEDS = {
  trip_updates: `${FEED_BASE}/tripupdates`,
  vehicle_positions: `${FEED_BASE}/positions`,
  alerts: `${FEED_BASE}/alerts`,
};

const GTFS_STATIC_URL = 'https://schedules.metrarail.com/gtfs/schedule.zip';
const GTFS_PUBLISHED_URL = 'https://schedules.metrarail.com/gtfs/published.txt';
const GTFS_DIR = path.join(os.homedir(), '.metra', 'gtfs');

// ---------------------------------------------------------------------------
// Metra Lines Metadata
// ---------------------------------------------------------------------------
const METRA_LINES = {
  'BNSF':  { name: 'BNSF Railway',              color: 'Orange',      terminal: 'Union Station (CUS)',                    outer: 'Aurora' },
  'ME':    { name: 'Metra Electric',             color: 'Teal',        terminal: 'Millennium Station',                     outer: 'University Park / South Chicago / Blue Island' },
  'HC':    { name: 'Heritage Corridor',          color: 'Purple',      terminal: 'Union Station (CUS)',                    outer: 'Joliet' },
  'MD-N':  { name: 'Milwaukee District North',   color: 'Light Green', terminal: 'Union Station (CUS)',                    outer: 'Fox Lake' },
  'MD-W':  { name: 'Milwaukee District West',    color: 'Light Green', terminal: 'Union Station (CUS)',                    outer: 'Elburn / Big Timber' },
  'NCS':   { name: 'North Central Service',      color: 'Gold',        terminal: 'Union Station (CUS)',                    outer: 'Antioch' },
  'RI':    { name: 'Rock Island',                color: 'Red',         terminal: 'LaSalle Street Station',                 outer: 'Joliet' },
  'SWS':   { name: 'SouthWest Service',          color: 'Dark Purple', terminal: 'Union Station (CUS)',                    outer: 'Manhattan' },
  'UP-N':  { name: 'Union Pacific North',        color: 'Dark Green',  terminal: 'Ogilvie Transportation Center (OTC)',    outer: 'Kenosha' },
  'UP-NW': { name: 'Union Pacific Northwest',    color: 'Blue',        terminal: 'Ogilvie Transportation Center (OTC)',    outer: 'Harvard / McHenry' },
  'UP-W':  { name: 'Union Pacific West',         color: 'Blue',        terminal: 'Ogilvie Transportation Center (OTC)',    outer: 'Elburn' },
};

// Route code aliases for user-friendly matching
const ROUTE_ALIASES = {
  'bnsf': 'BNSF', 'burlington': 'BNSF', 'burlington northern': 'BNSF',
  'me': 'ME', 'metra electric': 'ME', 'electric': 'ME',
  'hc': 'HC', 'heritage': 'HC', 'heritage corridor': 'HC',
  'md-n': 'MD-N', 'mdn': 'MD-N', 'milwaukee north': 'MD-N', 'mil north': 'MD-N', 'milwaukee district north': 'MD-N',
  'md-w': 'MD-W', 'mdw': 'MD-W', 'milwaukee west': 'MD-W', 'mil west': 'MD-W', 'milwaukee district west': 'MD-W',
  'ncs': 'NCS', 'north central': 'NCS', 'north central service': 'NCS',
  'ri': 'RI', 'rock island': 'RI', 'rock': 'RI',
  'sws': 'SWS', 'southwest': 'SWS', 'south west': 'SWS', 'southwest service': 'SWS',
  'up-n': 'UP-N', 'upn': 'UP-N', 'union pacific north': 'UP-N',
  'up-nw': 'UP-NW', 'upnw': 'UP-NW', 'union pacific northwest': 'UP-NW',
  'up-w': 'UP-W', 'upw': 'UP-W', 'union pacific west': 'UP-W',
};

function resolveLineCode(input) {
  if (!input) return null;
  const upper = input.toUpperCase();
  if (METRA_LINES[upper]) return upper;
  return ROUTE_ALIASES[input.toLowerCase()] || upper;
}

// ---------------------------------------------------------------------------
// Major Stations with Aliases (for fuzzy matching without GTFS)
// ---------------------------------------------------------------------------
const STATIONS = [
  // Downtown terminals
  { name: 'Chicago Union Station', lines: ['BNSF', 'HC', 'MD-N', 'MD-W', 'NCS', 'SWS'], aliases: ['union station', 'cus', 'chicago union station', 'union', 'chicago union'] },
  { name: 'Ogilvie Transportation Center', lines: ['UP-N', 'UP-NW', 'UP-W'], aliases: ['ogilvie', 'otc', 'ogilvie transportation center', 'northwestern station', 'ogilvie transportation'] },
  { name: 'LaSalle Street Station', lines: ['RI'], aliases: ['lasalle', 'lasalle street', 'lasalle street station', 'la salle', 'lasalle station'] },
  { name: 'Millennium Station', lines: ['ME'], aliases: ['millennium', 'millennium station', 'randolph street'] },
  // BNSF line
  { name: 'Naperville', lines: ['BNSF'], aliases: ['naperville'] },
  { name: 'Aurora', lines: ['BNSF'], aliases: ['aurora'] },
  { name: 'Route 59', lines: ['BNSF'], aliases: ['route 59'] },
  { name: 'Lisle', lines: ['BNSF'], aliases: ['lisle'] },
  { name: 'Downers Grove Main Street', lines: ['BNSF'], aliases: ['downers grove', 'downers grove main'] },
  { name: 'Westmont', lines: ['BNSF'], aliases: ['westmont'] },
  { name: 'Clarendon Hills', lines: ['BNSF'], aliases: ['clarendon hills'] },
  { name: 'Hinsdale', lines: ['BNSF'], aliases: ['hinsdale'] },
  { name: 'Western Springs', lines: ['BNSF'], aliases: ['western springs'] },
  { name: 'LaGrange Road', lines: ['BNSF'], aliases: ['lagrange', 'la grange', 'lagrange road'] },
  { name: 'Brookfield', lines: ['BNSF'], aliases: ['brookfield bnsf'] },
  { name: 'Berwyn', lines: ['BNSF'], aliases: ['berwyn'] },
  { name: 'Cicero', lines: ['BNSF'], aliases: ['cicero bnsf'] },
  { name: 'Halsted Street', lines: ['BNSF'], aliases: ['halsted bnsf'] },
  // UP-N line
  { name: 'Clybourn', lines: ['UP-N'], aliases: ['clybourn'] },
  { name: 'Ravenswood', lines: ['UP-N'], aliases: ['ravenswood'] },
  { name: 'Rogers Park', lines: ['UP-N'], aliases: ['rogers park'] },
  { name: 'Evanston Davis Street', lines: ['UP-N'], aliases: ['evanston', 'davis street', 'davis st', 'evanston davis'] },
  { name: 'Wilmette', lines: ['UP-N'], aliases: ['wilmette'] },
  { name: 'Kenilworth', lines: ['UP-N'], aliases: ['kenilworth'] },
  { name: 'Winnetka', lines: ['UP-N'], aliases: ['winnetka'] },
  { name: 'Glencoe', lines: ['UP-N'], aliases: ['glencoe'] },
  { name: 'Highland Park', lines: ['UP-N'], aliases: ['highland park'] },
  { name: 'Lake Forest', lines: ['UP-N'], aliases: ['lake forest'] },
  { name: 'Waukegan', lines: ['UP-N'], aliases: ['waukegan'] },
  { name: 'Kenosha', lines: ['UP-N'], aliases: ['kenosha'] },
  // UP-NW line
  { name: 'Arlington Heights', lines: ['UP-NW'], aliases: ['arlington heights'] },
  { name: 'Palatine', lines: ['UP-NW'], aliases: ['palatine'] },
  { name: 'Barrington', lines: ['UP-NW'], aliases: ['barrington'] },
  { name: 'Crystal Lake', lines: ['UP-NW'], aliases: ['crystal lake'] },
  { name: 'Harvard', lines: ['UP-NW'], aliases: ['harvard'] },
  { name: 'McHenry', lines: ['UP-NW'], aliases: ['mchenry'] },
  { name: 'Cary', lines: ['UP-NW'], aliases: ['cary'] },
  { name: 'Des Plaines', lines: ['UP-NW'], aliases: ['des plaines up-nw'] },
  { name: 'Mount Prospect', lines: ['UP-NW'], aliases: ['mount prospect', 'mt prospect'] },
  // UP-W line
  { name: 'Elmhurst', lines: ['UP-W'], aliases: ['elmhurst'] },
  { name: 'Glen Ellyn', lines: ['UP-W'], aliases: ['glen ellyn'] },
  { name: 'Wheaton', lines: ['UP-W'], aliases: ['wheaton'] },
  { name: 'Geneva', lines: ['UP-W'], aliases: ['geneva'] },
  { name: 'Elburn', lines: ['UP-W'], aliases: ['elburn'] },
  { name: 'West Chicago', lines: ['UP-W'], aliases: ['west chicago'] },
  { name: 'Villa Park', lines: ['UP-W'], aliases: ['villa park'] },
  { name: 'Lombard', lines: ['UP-W'], aliases: ['lombard'] },
  // MD-N line
  { name: 'Libertyville', lines: ['MD-N'], aliases: ['libertyville'] },
  { name: 'Vernon Hills', lines: ['MD-N'], aliases: ['vernon hills'] },
  { name: 'Lake Cook Road', lines: ['MD-N', 'NCS'], aliases: ['lake cook', 'lake cook road'] },
  { name: 'Fox Lake', lines: ['MD-N'], aliases: ['fox lake'] },
  { name: 'Deerfield', lines: ['MD-N'], aliases: ['deerfield'] },
  { name: 'Morton Grove', lines: ['MD-N'], aliases: ['morton grove'] },
  // MD-W line
  { name: 'Elgin', lines: ['MD-W'], aliases: ['elgin'] },
  { name: 'Bensenville', lines: ['MD-W'], aliases: ['bensenville'] },
  { name: 'Roselle', lines: ['MD-W'], aliases: ['roselle'] },
  { name: 'Itasca', lines: ['MD-W'], aliases: ['itasca'] },
  { name: 'Hanover Park', lines: ['MD-W'], aliases: ['hanover park'] },
  { name: 'Schaumburg', lines: ['MD-W'], aliases: ['schaumburg'] },
  { name: 'Franklin Park', lines: ['MD-W'], aliases: ['franklin park'] },
  // ME line
  { name: 'University Park', lines: ['ME'], aliases: ['university park'] },
  { name: '93rd Street (South Chicago)', lines: ['ME'], aliases: ['south chicago', '93rd st', '93rd street'] },
  { name: 'Blue Island', lines: ['ME'], aliases: ['blue island'] },
  { name: 'McCormick Place', lines: ['ME'], aliases: ['mccormick', 'mccormick place'] },
  { name: 'Museum Campus/11th Street', lines: ['ME'], aliases: ['museum campus', '11th st', '11th street'] },
  { name: 'Hyde Park (53rd Street)', lines: ['ME'], aliases: ['hyde park', '53rd st', '53rd street'] },
  { name: 'Homewood', lines: ['ME'], aliases: ['homewood'] },
  // RI line
  { name: 'Joliet', lines: ['RI', 'HC'], aliases: ['joliet'] },
  { name: 'New Lenox', lines: ['RI'], aliases: ['new lenox'] },
  { name: '35th Street/"Lou Jones"', lines: ['RI'], aliases: ['35th st', '35th street', 'bronzeville'] },
  { name: 'Oak Forest', lines: ['RI'], aliases: ['oak forest'] },
  { name: 'Tinley Park', lines: ['RI'], aliases: ['tinley park'] },
  // NCS line
  { name: 'Antioch', lines: ['NCS'], aliases: ['antioch'] },
  { name: 'Prairie Crossing', lines: ['NCS'], aliases: ['prairie crossing'] },
  // SWS line
  { name: 'Manhattan', lines: ['SWS'], aliases: ['manhattan sws'] },
  { name: 'Orland Park', lines: ['SWS'], aliases: ['orland park'] },
  { name: 'Palos Heights', lines: ['SWS'], aliases: ['palos heights'] },
  { name: 'Chicago Ridge', lines: ['SWS'], aliases: ['chicago ridge'] },
  // HC line
  { name: 'Lockport', lines: ['HC'], aliases: ['lockport'] },
  { name: 'Lemont', lines: ['HC'], aliases: ['lemont'] },
  { name: 'Summit', lines: ['HC'], aliases: ['summit'] },
];

// ---------------------------------------------------------------------------
// Fare Data (4-Zone System, effective Feb 2024)
// ---------------------------------------------------------------------------

// Map GTFS zone_id letters to fare zone numbers
const ZONE_LETTER_MAP = {
  'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 3, 'G': 3, 'H': 4, 'I': 4, 'J': 4,
};

function zoneIdToFareZone(zoneId) {
  if (!zoneId) return null;
  const upper = zoneId.toUpperCase().trim();
  // Try letter mapping first
  if (ZONE_LETTER_MAP[upper]) return ZONE_LETTER_MAP[upper];
  // Try numeric
  const num = parseInt(upper);
  if (num >= 1 && num <= 4) return num;
  return null;
}

const FARE_TABLE = {
  '1-2':  { oneWay: 3.75,  dayPass: 7.50,  dayPass5: 35.75,  monthly: 75.00 },
  '1-3':  { oneWay: 5.50,  dayPass: 11.00, dayPass5: 52.25,  monthly: 110.00 },
  '1-4':  { oneWay: 6.75,  dayPass: 13.50, dayPass5: 64.25,  monthly: 135.00 },
  '2-4':  { oneWay: 3.75,  dayPass: 7.50,  dayPass5: 35.75,  monthly: 75.00 },
};

function getFareKey(zone1, zone2) {
  const lo = Math.min(zone1, zone2);
  const hi = Math.max(zone1, zone2);
  if (lo === hi) return `${lo}-${lo + 1}`; // Same zone -> minimum fare
  if (lo === 1) return `1-${hi}`;
  return '2-4'; // Neither end is zone 1
}

// ---------------------------------------------------------------------------
// Time helpers — CST/CDT (US Central Time)
// ---------------------------------------------------------------------------
function localTzOffsetHours() {
  const now = new Date();
  const year = now.getUTCFullYear();
  const mar1 = new Date(Date.UTC(year, 2, 1));
  const firstSunMar = (7 - mar1.getUTCDay()) % 7 + 1;
  const dstStart = Date.UTC(year, 2, firstSunMar + 7, 8); // 2:00 AM CST = 08:00 UTC
  const nov1 = new Date(Date.UTC(year, 10, 1));
  const firstSunNov = (7 - nov1.getUTCDay()) % 7 + 1;
  const dstEnd = Date.UTC(year, 10, firstSunNov, 7); // 2:00 AM CDT = 07:00 UTC
  const ts = now.getTime();
  return (ts >= dstStart && ts < dstEnd) ? -5 : -6;
}

function toLocalDate(ts) {
  const d = typeof ts === 'number' ? new Date(ts * 1000) : ts;
  const offset = localTzOffsetHours();
  return new Date(d.getTime() + offset * 3600000);
}

function localNow() {
  return toLocalDate(new Date());
}

function fmtTime(d) {
  let h = d.getUTCHours(), m = d.getUTCMinutes(), s = d.getUTCSeconds();
  const ampm = h >= 12 ? 'PM' : 'AM';
  if (h > 12) h -= 12; else if (h === 0) h = 12;
  return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')} ${ampm}`;
}

function fmtTimeHM(d) {
  let h = d.getUTCHours(), m = d.getUTCMinutes();
  const ampm = h >= 12 ? 'PM' : 'AM';
  if (h > 12) h -= 12; else if (h === 0) h = 12;
  return `${h}:${String(m).padStart(2, '0')} ${ampm}`;
}

function fmtDateTimeShort(d) {
  const mo = d.getUTCMonth() + 1, day = d.getUTCDate();
  let h = d.getUTCHours(), m = d.getUTCMinutes();
  const ampm = h >= 12 ? 'PM' : 'AM';
  if (h > 12) h -= 12; else if (h === 0) h = 12;
  return `${String(mo).padStart(2, '0')}/${String(day).padStart(2, '0')} ${h}:${String(m).padStart(2, '0')} ${ampm}`;
}

function fmtGtfsTime(timeStr) {
  if (!timeStr) return '??';
  const [h, m] = timeStr.split(':');
  let hr = parseInt(h);
  if (isNaN(hr)) return timeStr;
  // GTFS allows hours >= 24 for next-day trips
  if (hr >= 24) hr -= 24;
  const ampm = hr >= 12 ? 'PM' : 'AM';
  if (hr > 12) hr -= 12; else if (hr === 0) hr = 12;
  return `${hr}:${m} ${ampm}`;
}

// ---------------------------------------------------------------------------
// GTFS-RT Protobuf helpers
// ---------------------------------------------------------------------------

let _protobufRoot = null;

function requireApiKey() {
  if (!METRA_API_KEY) {
    console.log('Metra API key required.');
    console.log('Get a free key at: https://metra.com/developers');
    console.log('Then set METRA_API_KEY in your environment.');
    return false;
  }
  return true;
}

async function getProtobufRoot() {
  if (_protobufRoot) return _protobufRoot;
  let protobuf;
  try {
    protobuf = (await import('protobufjs')).default;
  } catch {
    console.error('ERROR: protobufjs not installed.');
    console.error('Run: npm install (in the skill directory)');
    process.exit(1);
  }
  const protoPath = path.join(path.dirname(new URL(import.meta.url).pathname), 'gtfs-realtime.proto');
  _protobufRoot = await protobuf.load(protoPath);
  return _protobufRoot;
}

async function parsePb(url) {
  const root = await getProtobufRoot();
  const FeedMessage = root.lookupType('transit_realtime.FeedMessage');
  const resp = await fetch(url, {
    signal: AbortSignal.timeout(30000),
    headers: { 'Authorization': `Bearer ${METRA_API_KEY}` },
  });
  if (resp.status === 401 || resp.status === 403) {
    throw new Error('Authentication failed. Check your METRA_API_KEY.');
  }
  if (!resp.ok) throw new Error(`HTTP ${resp.status} fetching ${url}`);
  const buf = Buffer.from(await resp.arrayBuffer());
  // Check if we got HTML instead of protobuf
  if (buf.length > 0 && buf[0] === 0x3c) {
    throw new Error('Feed returned HTML instead of protobuf — endpoint may be temporarily unavailable');
  }
  return FeedMessage.decode(buf);
}

// ---------------------------------------------------------------------------
// GTFS Static data helpers
// ---------------------------------------------------------------------------

function ensureGtfs() {
  if (!fs.existsSync(path.join(GTFS_DIR, 'stops.txt'))) {
    console.log(`GTFS static data not found at ${GTFS_DIR}`);
    console.log('Run: node scripts/metra.mjs refresh-gtfs');
    return false;
  }
  return true;
}

function parseCsvLine(line) {
  const fields = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"') {
        if (i + 1 < line.length && line[i + 1] === '"') { current += '"'; i++; }
        else inQuotes = false;
      } else {
        current += ch;
      }
    } else {
      if (ch === '"') inQuotes = true;
      else if (ch === ',') { fields.push(current); current = ''; }
      else current += ch;
    }
  }
  fields.push(current);
  return fields;
}

function loadCsv(filename) {
  const filePath = path.join(GTFS_DIR, filename);
  if (!fs.existsSync(filePath)) return [];
  let content = fs.readFileSync(filePath, 'utf-8');
  if (content.charCodeAt(0) === 0xFEFF) content = content.slice(1);
  const lines = content.split(/\r?\n/).filter(l => l.trim());
  if (lines.length === 0) return [];
  // Metra GTFS CSVs have spaces after commas — trim all headers and values
  const headers = parseCsvLine(lines[0]).map(h => h.trim());
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const vals = parseCsvLine(lines[i]);
    const obj = {};
    for (let j = 0; j < headers.length; j++) {
      obj[headers[j]] = (vals[j] || '').trim();
    }
    rows.push(obj);
  }
  return rows;
}

let _stopsCache = null;
function loadStops() {
  if (_stopsCache) return _stopsCache;
  const rows = loadCsv('stops.txt');
  const m = {};
  for (const r of rows) m[r.stop_id] = r;
  _stopsCache = m;
  return m;
}

let _routesCache = null;
function loadRoutes() {
  if (_routesCache) return _routesCache;
  const rows = loadCsv('routes.txt');
  const m = {};
  for (const r of rows) m[r.route_id] = r;
  _routesCache = m;
  return m;
}

let _tripsCache = null;
function loadTrips() {
  if (_tripsCache) return _tripsCache;
  const rows = loadCsv('trips.txt');
  const m = {};
  for (const r of rows) m[r.trip_id] = r;
  _tripsCache = m;
  return m;
}

function getActiveServiceIds(dateStr) {
  const active = new Set();
  const calRows = loadCsv('calendar.txt');
  const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  const y = parseInt(dateStr.slice(0, 4)), m = parseInt(dateStr.slice(4, 6)) - 1, d = parseInt(dateStr.slice(6, 8));
  const dayOfWeek = new Date(Date.UTC(y, m, d)).getUTCDay();
  const dayCol = dayNames[dayOfWeek];
  for (const r of calRows) {
    if (r[dayCol] === '1' && dateStr >= r.start_date && dateStr <= r.end_date) {
      active.add(r.service_id);
    }
  }
  const exceptRows = loadCsv('calendar_dates.txt');
  for (const r of exceptRows) {
    if (r.date !== dateStr) continue;
    if (r.exception_type === '1') active.add(r.service_id);
    else if (r.exception_type === '2') active.delete(r.service_id);
  }
  return active;
}

function loadStopTimesForStop(stopId) {
  const rows = loadCsv('stop_times.txt');
  return rows.filter(r => r.stop_id === stopId);
}

function loadStopTimesForTrip(tripId) {
  const rows = loadCsv('stop_times.txt');
  return rows.filter(r => r.trip_id === tripId)
    .sort((a, b) => parseInt(a.stop_sequence || '0') - parseInt(b.stop_sequence || '0'));
}

// ---------------------------------------------------------------------------
// Haversine distance (miles)
// ---------------------------------------------------------------------------
function haversine(lat1, lon1, lat2, lon2) {
  const R = 3959;
  const dlat = (lat2 - lat1) * Math.PI / 180;
  const dlon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dlat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dlon / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

// ---------------------------------------------------------------------------
// Station Search — fuzzy matching on embedded data + GTFS stops
// ---------------------------------------------------------------------------

function searchStation(query, lineFilter) {
  const q = query.toLowerCase().trim();
  const results = [];
  const seen = new Set();

  // 1. Search embedded major stations
  for (const s of STATIONS) {
    if (lineFilter && !s.lines.includes(lineFilter)) continue;
    const nameNorm = s.name.toLowerCase();
    let score = 999;
    if (nameNorm === q) score = 0;
    else if (s.aliases.some(a => a === q)) score = 1;
    else if (nameNorm.includes(q)) score = 2;
    else if (s.aliases.some(a => a.includes(q))) score = 3;
    else if (q.split(/\s+/).every(w => nameNorm.includes(w) || s.aliases.some(a => a.includes(w)))) score = 4;
    else continue;
    const key = s.name;
    if (seen.has(key)) continue;
    seen.add(key);
    results.push({ ...s, score, source: 'embedded' });
  }

  // 2. Search GTFS stops
  if (fs.existsSync(path.join(GTFS_DIR, 'stops.txt'))) {
    const stops = loadStops();
    for (const [sid, s] of Object.entries(stops)) {
      const nameNorm = (s.stop_name || '').toLowerCase();
      let score = 999;
      if (nameNorm === q) score = 5;
      else if (nameNorm.includes(q)) score = 6;
      else continue;
      const key = `gtfs_${sid}`;
      if (seen.has(key)) continue;
      // Also skip if the same name was already matched from embedded data
      if (seen.has(s.stop_name)) continue;
      seen.add(key);
      results.push({
        name: s.stop_name,
        stop_id: sid,
        lines: [],
        aliases: [],
        score,
        source: 'gtfs',
        zone_id: s.zone_id || '',
      });
    }
  }

  results.sort((a, b) => a.score - b.score || a.name.localeCompare(b.name));
  return results;
}

// Find GTFS stop_id(s) for a station (by name matching)
function resolveStopIds(stationName, lineFilter) {
  if (!ensureGtfs()) return [];
  const stops = loadStops();
  const routes = loadRoutes();
  const trips = loadTrips();
  const q = stationName.toLowerCase().trim();

  // Direct stop_id match
  if (stops[q] || stops[q.toUpperCase()]) {
    return [q.toUpperCase()];
  }

  // Also check well-known stop_id mappings for embedded stations
  const embeddedMatch = STATIONS.find(s => s.name.toLowerCase() === q || s.aliases.some(a => a === q));

  // Name match — try multiple strategies
  const matched = [];
  for (const [sid, s] of Object.entries(stops)) {
    const nameNorm = (s.stop_name || '').toLowerCase();
    // Exact or contains match (either direction)
    if (nameNorm === q || nameNorm.includes(q) || q.includes(nameNorm)) {
      matched.push(sid);
      continue;
    }
    // Try matching individual words from the query
    const queryWords = q.split(/[\s/(),.]+/).filter(w => w.length > 2);
    if (queryWords.length > 0 && queryWords.every(w => nameNorm.includes(w))) {
      matched.push(sid);
      continue;
    }
    // Try aliases from embedded station data
    if (embeddedMatch) {
      for (const alias of embeddedMatch.aliases) {
        if (nameNorm.includes(alias) || alias.includes(nameNorm)) {
          matched.push(sid);
          break;
        }
      }
    }
  }

  // If line filter, verify stops are actually on that line
  if (lineFilter && matched.length > 0) {
    const stopTimesAll = loadCsv('stop_times.txt');
    const lineTrips = new Set();
    for (const [tid, t] of Object.entries(trips)) {
      const routeId = t.route_id || '';
      const rShort = routes[routeId]?.route_short_name || routeId;
      if (rShort.toUpperCase() === lineFilter || routeId.toUpperCase() === lineFilter) {
        lineTrips.add(tid);
      }
    }
    const stopsOnLine = new Set();
    for (const st of stopTimesAll) {
      if (lineTrips.has(st.trip_id)) stopsOnLine.add(st.stop_id);
    }
    const filtered = matched.filter(sid => stopsOnLine.has(sid));
    if (filtered.length > 0) return filtered;
  }

  return matched;
}

// Extract line code from a trip_id like "BNSF_BN1252_V1_B"
function lineFromTripId(tripId) {
  if (!tripId) return '';
  const prefix = tripId.split('_')[0];
  if (METRA_LINES[prefix]) return prefix;
  // Try matching known prefixes
  for (const code of Object.keys(METRA_LINES)) {
    if (tripId.toUpperCase().startsWith(code + '_') || tripId.toUpperCase().startsWith(code.replace('-', '') + '_')) {
      return code;
    }
  }
  return prefix;
}

// Extract human-readable train number from trip_id
function trainNumberFromTripId(tripId) {
  if (!tripId) return '';
  const parts = tripId.split('_');
  return parts.length >= 2 ? parts[1] : tripId;
}

// Determine direction (inbound/outbound) from direction_id
// Metra convention: 0 = outbound (away from downtown), 1 = inbound (toward downtown)
function directionLabel(directionId) {
  if (directionId === 0 || directionId === '0') return 'Outbound';
  if (directionId === 1 || directionId === '1') return 'Inbound';
  return '';
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

async function cmdRefreshGtfs() {
  console.log(`Downloading GTFS static data to ${GTFS_DIR} ...`);
  fs.mkdirSync(GTFS_DIR, { recursive: true });

  // Check published timestamp
  try {
    const pubResp = await fetch(GTFS_PUBLISHED_URL, { signal: AbortSignal.timeout(10000) });
    if (pubResp.ok) {
      const pubText = (await pubResp.text()).trim();
      console.log(`Schedule last published: ${pubText}`);
    }
  } catch { /* ignore */ }

  const resp = await fetch(GTFS_STATIC_URL, { signal: AbortSignal.timeout(120000) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const buf = Buffer.from(await resp.arrayBuffer());

  const tmpZip = path.join(GTFS_DIR, '_gtfs_tmp.zip');
  fs.writeFileSync(tmpZip, buf);

  try {
    execFileSync('unzip', ['-o', tmpZip, '-d', GTFS_DIR], { stdio: 'pipe' });
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.error('Error: "unzip" command not found. Install it first:');
      console.error('  Ubuntu/Debian: sudo apt install unzip');
      console.error('  macOS: brew install unzip');
      console.error('  Arch: sudo pacman -S unzip');
    } else {
      console.error(`Error extracting GTFS zip: ${err.message}`);
    }
    fs.unlinkSync(tmpZip);
    return;
  }
  fs.unlinkSync(tmpZip);

  // Clear caches
  _stopsCache = null;
  _routesCache = null;
  _tripsCache = null;

  const files = fs.readdirSync(GTFS_DIR).filter(f => f.endsWith('.txt')).sort();
  console.log(`Extracted ${files.length} files:`);
  for (const f of files) console.log(`  ${f}`);
  console.log('GTFS data refreshed successfully.');
}

// ---- Arrivals ----

async function cmdArrivals(opts) {
  if (!requireApiKey()) return;

  const stationName = opts.station;
  const lineFilter = opts.line ? resolveLineCode(opts.line) : null;

  if (!stationName) {
    console.log('Provide --station with a station name.');
    console.log("Use 'stops --search <name>' to find stations.");
    return;
  }

  // Resolve station
  const matches = searchStation(stationName, lineFilter);
  if (!matches.length) {
    console.log(`No stations found matching '${stationName}'.`);
    console.log("Try 'stops --search <name>' to search all stops.");
    return;
  }

  if (matches.length > 1 && matches[0].score > 0) {
    console.log(`Found ${matches.length} stations matching '${stationName}':`);
    for (const s of matches.slice(0, 8)) {
      const lineStr = s.lines?.length ? ` (${s.lines.join(', ')})` : '';
      console.log(`  ${s.name}${lineStr}`);
    }
    console.log(`\nUsing best match: ${matches[0].name}\n`);
  }

  const station = matches[0];
  const stopIds = resolveStopIds(station.name, lineFilter);

  if (!stopIds.length) {
    console.log(`Could not resolve stop IDs for '${station.name}'.`);
    console.log('Try running refresh-gtfs to update station data.');
    return;
  }

  const targetSet = new Set(stopIds);
  const stationLabel = station.name;
  const lineInfo = lineFilter && METRA_LINES[lineFilter] ? METRA_LINES[lineFilter] : null;

  console.log(`\n=== Arrivals at: ${stationLabel} ===`);
  if (lineInfo) console.log(`    Line: ${lineInfo.name}`);
  console.log();

  // Fetch trip updates
  const feed = await parsePb(FEEDS.trip_updates);
  const routes = ensureGtfs() ? loadRoutes() : {};
  const trips = ensureGtfs() ? loadTrips() : {};
  const now = localNow();
  const arrivals = [];

  for (const entity of feed.entity || []) {
    const tu = entity.tripUpdate;
    if (!tu) continue;

    const tripId = tu.trip?.tripId || '';
    const routeId = tu.trip?.routeId || '';
    const dirId = tu.trip?.directionId;
    const rShort = routes[routeId]?.route_short_name || routeId;
    const tripLine = rShort || lineFromTripId(tripId);

    if (lineFilter && tripLine.toUpperCase() !== lineFilter) continue;

    const tripInfo = trips[tripId] || {};
    const trainNum = tripInfo.trip_short_name || trainNumberFromTripId(tripId);
    const headsign = tripInfo.trip_headsign || '';
    const dir = directionLabel(dirId !== undefined ? dirId : tripInfo.direction_id);

    for (const stu of tu.stopTimeUpdate || []) {
      const stopId = stu.stopId || '';
      if (!targetSet.has(stopId)) continue;

      let arrivalTime = null, delay = 0;
      if (stu.arrival?.time) {
        arrivalTime = toLocalDate(Number(stu.arrival.time));
        delay = stu.arrival.delay || 0;
      } else if (stu.departure?.time) {
        arrivalTime = toLocalDate(Number(stu.departure.time));
        delay = stu.departure.delay || 0;
      }
      if (!arrivalTime) continue;

      const minsAway = (arrivalTime.getTime() - now.getTime()) / 60000;
      if (minsAway < -2) continue;

      const lineMeta = METRA_LINES[tripLine] || METRA_LINES[tripLine.toUpperCase()];

      arrivals.push({
        line: tripLine,
        lineName: lineMeta?.name || tripLine,
        trainNum,
        headsign,
        direction: dir,
        arrival: fmtTimeHM(arrivalTime),
        minsAway: Math.round(minsAway),
        delayMins: delay ? Math.round(delay / 60) : 0,
        terminal: lineMeta?.terminal || '',
      });
    }
  }

  if (!arrivals.length) {
    console.log('No real-time arrivals found.');
    console.log('Falling back to scheduled times...\n');
    showScheduledArrivals(stopIds, lineFilter);
    return;
  }

  arrivals.sort((a, b) => a.minsAway - b.minsAway);

  for (const a of arrivals.slice(0, 20)) {
    const eta = a.minsAway <= 0 ? 'Due' : a.minsAway === 1 ? '1 min' : `${a.minsAway} min`;
    const delayStr = a.delayMins > 0 ? ` (+${a.delayMins}m late)` : '';
    const dirStr = a.direction ? ` ${a.direction}` : '';
    const hsStr = a.headsign ? ` -> ${a.headsign}` : '';

    console.log(`  🚂 ${a.lineName} Train ${a.trainNum}${dirStr}${hsStr}`);
    console.log(`     ${a.arrival} (${eta})${delayStr}`);
    console.log();
  }
}

function showScheduledArrivals(stopIds, lineFilter) {
  if (!ensureGtfs()) return;

  const routes = loadRoutes();
  const trips = loadTrips();
  const now = localNow();
  const yyyy = String(now.getUTCFullYear());
  const mo = String(now.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(now.getUTCDate()).padStart(2, '0');
  const todayStr = `${yyyy}${mo}${dd}`;
  const activeServices = getActiveServiceIds(todayStr);

  const hh = String(now.getUTCHours()).padStart(2, '0');
  const mm = String(now.getUTCMinutes()).padStart(2, '0');
  const ss = String(now.getUTCSeconds()).padStart(2, '0');
  const currentTime = `${hh}:${mm}:${ss}`;

  const upcoming = [];
  const seen = new Set();

  for (const stopId of stopIds) {
    const stopTimes = loadStopTimesForStop(stopId);
    for (const st of stopTimes) {
      const tripInfo = trips[st.trip_id] || {};
      const routeId = tripInfo.route_id || '';
      const serviceId = tripInfo.service_id || '';
      if (!activeServices.has(serviceId)) continue;

      const rShort = routes[routeId]?.route_short_name || routeId;
      if (lineFilter && rShort.toUpperCase() !== lineFilter) continue;

      const depTime = st.departure_time || st.arrival_time || '';
      if (depTime <= currentTime) continue;

      const trainNum = tripInfo.trip_short_name || trainNumberFromTripId(st.trip_id);
      const headsign = tripInfo.trip_headsign || '';
      const dir = directionLabel(tripInfo.direction_id);
      const dedup = `${rShort}|${depTime}|${trainNum}`;
      if (seen.has(dedup)) continue;
      seen.add(dedup);

      const lineMeta = METRA_LINES[rShort] || METRA_LINES[rShort.toUpperCase()];

      upcoming.push({
        line: rShort,
        lineName: lineMeta?.name || rShort,
        trainNum,
        headsign,
        direction: dir,
        time: depTime,
      });
    }
  }

  upcoming.sort((a, b) => a.time.localeCompare(b.time));

  if (!upcoming.length) {
    console.log('No upcoming scheduled departures found for today.');
    return;
  }

  console.log('Scheduled departures (no real-time data available):');
  for (const u of upcoming.slice(0, 15)) {
    const dirStr = u.direction ? ` ${u.direction}` : '';
    const hsStr = u.headsign ? ` -> ${u.headsign}` : '';
    console.log(`  🚂 ${u.lineName} Train ${u.trainNum}${dirStr}${hsStr}`);
    console.log(`     ${fmtGtfsTime(u.time)} (scheduled)`);
    console.log();
  }
}

// ---- Vehicles ----

async function cmdVehicles(opts) {
  if (!requireApiKey()) return;

  const lineFilter = opts.line ? resolveLineCode(opts.line) : null;
  if (!lineFilter) {
    console.log('Provide --line with a Metra line code.');
    console.log('Valid lines: ' + Object.keys(METRA_LINES).join(', '));
    return;
  }

  const lineMeta = METRA_LINES[lineFilter];
  if (!lineMeta) {
    console.log(`Unknown Metra line: ${opts.line}`);
    console.log('Valid lines: ' + Object.keys(METRA_LINES).join(', '));
    return;
  }

  console.log(`\nFetching ${lineMeta.name} vehicle positions...`);

  const feed = await parsePb(FEEDS.vehicle_positions);
  const stops = ensureGtfs() ? loadStops() : {};
  const routes = ensureGtfs() ? loadRoutes() : {};
  const trips = ensureGtfs() ? loadTrips() : {};
  const vehicles = [];

  for (const entity of feed.entity || []) {
    const v = entity.vehicle;
    if (!v) continue;

    const tripId = v.trip?.tripId || '';
    const routeId = v.trip?.routeId || '';
    const rShort = routes[routeId]?.route_short_name || routeId;
    const tripLine = rShort || lineFromTripId(tripId);

    if (tripLine.toUpperCase() !== lineFilter) continue;

    const pos = v.position || {};
    const stopId = v.stopId || '';
    const status = v.currentStatus || 0;
    const ts = v.timestamp;
    const dirId = v.trip?.directionId;

    const tripInfo = trips[tripId] || {};
    const trainNum = tripInfo.trip_short_name || trainNumberFromTripId(tripId);
    const headsign = tripInfo.trip_headsign || '';
    const dir = directionLabel(dirId !== undefined ? dirId : tripInfo.direction_id);
    const stopName = stops[stopId]?.stop_name || stopId;
    const statusLabels = { 0: 'Approaching', 1: 'Stopped at', 2: 'In transit to' };
    const statusStr = statusLabels[status] || 'En route to';

    let timeStr = '';
    if (ts) {
      try { timeStr = fmtTime(toLocalDate(Number(ts))); } catch { timeStr = String(ts); }
    }

    vehicles.push({
      trainNum,
      headsign,
      direction: dir,
      stopName,
      status: statusStr,
      lat: pos.latitude,
      lon: pos.longitude,
      bearing: pos.bearing,
      speed: pos.speed,
      time: timeStr,
    });
  }

  if (!vehicles.length) {
    console.log(`No active trains found on ${lineMeta.name}.`);
    console.log('Trains may be underground or at terminals (GPS loss), or service may not be running.');
    return;
  }

  console.log(`\n=== ${lineMeta.name} Positions (${vehicles.length} active) ===\n`);

  for (const v of vehicles) {
    const dirStr = v.direction ? ` — ${v.direction}` : '';
    const hsStr = v.headsign ? ` -> ${v.headsign}` : '';

    console.log(`  🚂 Train ${v.trainNum}${dirStr}${hsStr}`);
    console.log(`     ${v.status} ${v.stopName}`);
    if (v.lat && v.lon) {
      let posStr = `     Position: (${Number(v.lat).toFixed(5)}, ${Number(v.lon).toFixed(5)})`;
      if (v.bearing) posStr += ` bearing ${v.bearing}°`;
      if (v.speed) posStr += ` @ ${(v.speed * 2.237).toFixed(0)} mph`;
      console.log(posStr);
    }
    if (v.time) console.log(`     Last update: ${v.time}`);
    console.log();
  }
}

// ---- Alerts ----

async function cmdAlerts(opts) {
  if (!requireApiKey()) return;

  const lineFilter = opts.line ? resolveLineCode(opts.line) : null;

  const feed = await parsePb(FEEDS.alerts);
  const routes = ensureGtfs() ? loadRoutes() : {};

  if (!feed.entity || feed.entity.length === 0) {
    const filterMsg = lineFilter ? ` for ${METRA_LINES[lineFilter]?.name || lineFilter}` : '';
    console.log(`No active service alerts${filterMsg}.`);
    return;
  }

  let entities = feed.entity;
  if (lineFilter) {
    entities = entities.filter(e => {
      const alert = e.alert;
      if (!alert?.informedEntity) return false;
      return alert.informedEntity.some(ie => {
        const rid = ie.routeId || '';
        const rShort = routes[rid]?.route_short_name || rid;
        return rShort.toUpperCase() === lineFilter || rid.toUpperCase() === lineFilter;
      });
    });
  }

  if (!entities.length) {
    const filterMsg = lineFilter ? ` for ${METRA_LINES[lineFilter]?.name || lineFilter}` : '';
    console.log(`No active alerts${filterMsg}.`);
    return;
  }

  console.log(`\n=== Metra Service Alerts (${entities.length} active) ===\n`);

  for (const entity of entities) {
    const alert = entity.alert;
    if (!alert) continue;

    let header = '';
    if (alert.headerText?.translation?.length)
      header = alert.headerText.translation[0].text;
    let desc = '';
    if (alert.descriptionText?.translation?.length)
      desc = alert.descriptionText.translation[0].text;

    const affected = [];
    if (alert.informedEntity) {
      for (const ie of alert.informedEntity) {
        const rid = ie.routeId || '';
        if (rid) {
          const rShort = routes[rid]?.route_short_name || rid;
          if (!affected.includes(rShort)) affected.push(rShort);
        }
      }
    }

    const periods = [];
    if (alert.activePeriod) {
      for (const ap of alert.activePeriod) {
        const start = ap.start ? fmtDateTimeShort(toLocalDate(Number(ap.start))) : '?';
        const end = ap.end ? fmtDateTimeShort(toLocalDate(Number(ap.end))) : 'ongoing';
        periods.push(`${start} - ${end}`);
      }
    }

    const effect = alert.effect || 0;
    let icon = '';
    if (effect === 1) icon = '  '; // NO_SERVICE
    else if (effect === 2 || effect === 3) icon = '  '; // REDUCED/DELAYS
    else icon = '  ';

    console.log(`${icon} ${header || '(No headline)'}`);
    if (affected.length) console.log(`   Lines: ${affected.join(', ')}`);
    if (periods.length) console.log(`   Period: ${periods[0]}${periods.length > 1 ? ` (+${periods.length - 1} more)` : ''}`);
    if (desc) {
      if (desc.length > 400) desc = desc.slice(0, 400) + '...';
      console.log(`   ${desc}`);
    }
    console.log();
  }
}

// ---- Routes ----

function cmdRoutes() {
  console.log('\n=== Metra Commuter Rail Lines (11 lines) ===\n');
  for (const [code, line] of Object.entries(METRA_LINES)) {
    console.log(`  ${code.padEnd(6)} | ${line.name.padEnd(28)} | ${line.color}`);
    console.log(`  ${''.padEnd(6)} | ${line.terminal.padEnd(28)} | -> ${line.outer}`);
  }
}

// ---- Stops ----

function cmdStops(opts) {
  if (opts.search) {
    const query = opts.search;
    const results = searchStation(query, null);
    if (!results.length) {
      console.log(`No stations found matching '${query}'.`);
      return;
    }
    console.log(`\n=== Stations matching '${query}' (${results.length} found) ===\n`);
    for (const s of results.slice(0, 25)) {
      const lineStr = s.lines?.length ? ` (${s.lines.join(', ')})` : '';
      const zoneStr = s.zone_id ? ` [Zone ${s.zone_id}]` : '';
      console.log(`  📍 ${s.name}${lineStr}${zoneStr}`);
      if (s.stop_id) console.log(`     ID: ${s.stop_id}`);
      console.log();
    }
  } else if (opts.line) {
    const lineCode = resolveLineCode(opts.line);
    if (!METRA_LINES[lineCode]) {
      console.log(`Unknown line: ${opts.line}`);
      console.log('Valid lines: ' + Object.keys(METRA_LINES).join(', '));
      return;
    }
    if (!ensureGtfs()) return;

    const routes = loadRoutes();
    const trips = loadTrips();
    const stops = loadStops();
    const lineMeta = METRA_LINES[lineCode];

    console.log(`\n=== Stops on ${lineMeta.name} (${lineCode}) ===`);
    console.log(`    ${lineMeta.terminal} -> ${lineMeta.outer}\n`);

    // Find a trip for this route to get stop sequence
    const routeTrips = Object.values(trips).filter(t => {
      const rShort = routes[t.route_id]?.route_short_name || t.route_id || '';
      return rShort.toUpperCase() === lineCode || t.route_id.toUpperCase() === lineCode;
    });

    if (!routeTrips.length) {
      console.log('No trip data found. Try running refresh-gtfs.');
      return;
    }

    // Metra: direction_id 1 = inbound (toward downtown)
    const dir0 = routeTrips.filter(t => t.direction_id === '1');
    // Pick the trip with the most stops for completeness
    let bestTrip = null;
    let bestCount = 0;
    for (const t of (dir0.length ? dir0 : routeTrips)) {
      const st = loadStopTimesForTrip(t.trip_id);
      if (st.length > bestCount) {
        bestTrip = t;
        bestCount = st.length;
      }
    }

    if (!bestTrip) {
      console.log('No stop sequence found.');
      return;
    }

    const stopTimes = loadStopTimesForTrip(bestTrip.trip_id);
    for (const st of stopTimes) {
      const s = stops[st.stop_id];
      const sname = s?.stop_name || st.stop_id;
      const zone = s?.zone_id ? ` [Zone ${s.zone_id}]` : '';
      console.log(`  ${(st.stop_sequence || '').padStart(3)}. ${sname}${zone}`);
    }
  } else if (opts.near) {
    if (!ensureGtfs()) return;
    const parts = opts.near.split(',');
    if (parts.length !== 2) { console.log('Invalid format. Use: --near LAT,LON'); return; }
    const [lat, lon] = parts.map(Number);
    if (isNaN(lat) || isNaN(lon)) { console.log('Invalid format. Use: --near LAT,LON'); return; }
    const radius = opts.radius ? parseFloat(opts.radius) : 1.0;

    const stops = loadStops();
    const nearby = [];
    for (const s of Object.values(stops)) {
      const slat = parseFloat(s.stop_lat), slon = parseFloat(s.stop_lon);
      if (isNaN(slat) || isNaN(slon)) continue;
      const dist = haversine(lat, lon, slat, slon);
      if (dist <= radius) nearby.push([dist, s]);
    }
    nearby.sort((a, b) => a[0] - b[0]);

    if (!nearby.length) { console.log(`No Metra stations found within ${radius} miles of (${lat}, ${lon}).`); return; }
    console.log(`\n=== Nearby Metra Stations (${nearby.length} within ${radius} mi) ===\n`);
    for (const [dist, s] of nearby.slice(0, 20)) {
      const zone = s.zone_id ? ` [Zone ${s.zone_id}]` : '';
      console.log(`  📍 ${s.stop_name} — ${dist.toFixed(2)} mi${zone}`);
      console.log(`     ID: ${s.stop_id}`);
      console.log();
    }
  } else {
    console.log('Provide --search <name>, --line <code>, or --near LAT,LON');
  }
}

// ---- Route Info ----

function cmdRouteInfo(opts) {
  const lineCode = opts.line ? resolveLineCode(opts.line) : null;
  if (!lineCode) {
    console.log('Provide --line with a Metra line code.');
    console.log('Valid lines: ' + Object.keys(METRA_LINES).join(', '));
    return;
  }

  const lineMeta = METRA_LINES[lineCode];
  if (!lineMeta) {
    console.log(`Unknown line: ${opts.line}`);
    console.log('Valid lines: ' + Object.keys(METRA_LINES).join(', '));
    return;
  }

  console.log(`\n=== ${lineMeta.name} (${lineCode}) ===`);
  console.log(`    Color: ${lineMeta.color}`);
  console.log(`    Downtown Terminal: ${lineMeta.terminal}`);
  console.log(`    Outer Terminal: ${lineMeta.outer}`);
  console.log();

  if (!ensureGtfs()) return;

  const routes = loadRoutes();
  const trips = loadTrips();
  const stops = loadStops();

  // Find route in GTFS
  const routeId = Object.keys(routes).find(k => {
    const rShort = routes[k].route_short_name || '';
    return rShort.toUpperCase() === lineCode || k.toUpperCase() === lineCode;
  });

  if (!routeId) {
    console.log('No GTFS route data found. Try running refresh-gtfs.');
    return;
  }

  const r = routes[routeId];
  if (r.route_long_name) console.log(`    Full Name: ${r.route_long_name}`);

  // Show stops for both directions
  const routeTrips = Object.values(trips).filter(t => t.route_id === routeId);
  if (!routeTrips.length) {
    console.log('\nNo trip data found.');
    return;
  }

  // Metra: direction_id 1 = inbound, 0 = outbound
  for (const dirId of ['1', '0']) {
    const dirTrips = routeTrips.filter(t => t.direction_id === dirId);
    if (!dirTrips.length) continue;

    // Pick trip with most stops
    let bestTrip = null;
    let bestCount = 0;
    for (const t of dirTrips) {
      const st = loadStopTimesForTrip(t.trip_id);
      if (st.length > bestCount) {
        bestTrip = t;
        bestCount = st.length;
      }
    }

    if (!bestTrip || bestCount === 0) continue;

    const dirLabel = dirId === '1' ? 'Inbound' : 'Outbound';
    const headsign = bestTrip.trip_headsign || dirLabel;
    console.log(`\n${dirLabel} Stops (${headsign}) — ${bestCount} stops:`);

    const stopTimes = loadStopTimesForTrip(bestTrip.trip_id);
    for (const st of stopTimes) {
      const s = stops[st.stop_id];
      const sname = s?.stop_name || st.stop_id;
      const zone = s?.zone_id ? ` [Zone ${s.zone_id}]` : '';
      console.log(`  ${(st.stop_sequence || '').padStart(3)}. ${sname}${zone}`);
    }
  }
}

// ---- Fares ----

function cmdFares(opts) {
  const fromStation = opts.from;
  const toStation = opts.to;

  if (fromStation && toStation) {
    // Calculate fare between two stations
    if (!ensureGtfs()) return;
    const stops = loadStops();

    // Find from station
    const fromMatches = searchStation(fromStation, null);
    if (!fromMatches.length) {
      console.log(`No station found matching '${fromStation}'.`);
      return;
    }
    const toMatches = searchStation(toStation, null);
    if (!toMatches.length) {
      console.log(`No station found matching '${toStation}'.`);
      return;
    }

    const fromName = fromMatches[0].name;
    const toName = toMatches[0].name;

    // Get zone IDs
    const fromStopIds = resolveStopIds(fromName, null);
    const toStopIds = resolveStopIds(toName, null);

    let fromZoneId = null, toZoneId = null;
    for (const sid of fromStopIds) {
      if (stops[sid]?.zone_id) { fromZoneId = stops[sid].zone_id; break; }
    }
    for (const sid of toStopIds) {
      if (stops[sid]?.zone_id) { toZoneId = stops[sid].zone_id; break; }
    }

    if (!fromZoneId || !toZoneId) {
      console.log('Could not determine fare zones for these stations.');
      console.log('Zone data may not be available in GTFS. Showing general fare table instead.\n');
      showFareTable();
      return;
    }

    const fromFareZone = zoneIdToFareZone(fromZoneId);
    const toFareZone = zoneIdToFareZone(toZoneId);

    if (!fromFareZone || !toFareZone) {
      console.log(`Unknown zone IDs: ${fromZoneId}, ${toZoneId}`);
      console.log('Showing general fare table instead.\n');
      showFareTable();
      return;
    }

    const fareKey = getFareKey(fromFareZone, toFareZone);
    const fares = FARE_TABLE[fareKey];

    if (!fares) {
      console.log('Could not determine fare for this zone pair.');
      showFareTable();
      return;
    }

    console.log(`\n=== Fare: ${fromName} -> ${toName} ===`);
    console.log(`    Zone ${fromFareZone} (${fromZoneId}) -> Zone ${toFareZone} (${toZoneId})`);
    console.log(`    Fare Category: Zones ${fareKey}\n`);
    console.log(`    One-Way:        $${fares.oneWay.toFixed(2)}`);
    console.log(`    Day Pass:       $${fares.dayPass.toFixed(2)}`);
    console.log(`    Day Pass 5-Pk:  $${fares.dayPass5.toFixed(2)}`);
    console.log(`    Monthly Pass:   $${fares.monthly.toFixed(2)}`);
    console.log();
    console.log('    Onboard Surcharge (cash): $5.00 additional');
    console.log('    Weekend Day Pass: $7.00 (systemwide)');
  } else {
    showFareTable();
  }
}

function showFareTable() {
  console.log(`\n=== Metra Fares (4-Zone System, effective Feb 2024) ===\n`);
  console.log('  Ticket Type        | Zones 1-2 | Zones 1-3 | Zones 1-4 | Zones 2-4');
  console.log('  -------------------|-----------|-----------|-----------|----------');
  console.log('  One-Way            |   $3.75   |   $5.50   |   $6.75   |   $3.75');
  console.log('  Day Pass           |   $7.50   |  $11.00   |  $13.50   |   $7.50');
  console.log('  Day Pass 5-Pack    |  $35.75   |  $52.25   |  $64.25   |  $35.75');
  console.log('  Monthly Pass       |  $75.00   | $110.00   | $135.00   |  $75.00');
  console.log();
  console.log('  Special Passes:');
  console.log('    Sat/Sun/Holiday Day Pass:  $7.00 (systemwide)');
  console.log('    Weekend Pass (Ventra app): $10.00 (systemwide)');
  console.log('    Regional Connect (w/ Mo.): $30.00 (adds CTA + Pace)');
  console.log('    Onboard Surcharge (cash):  $5.00');
  console.log();
  console.log('  Monthly Passes: unlimited weekday rides between zones, systemwide on weekends.');
  console.log('  Reduced fares (seniors, students, military): approximately half price.');
}

// ---- Schedule ----

function cmdSchedule(opts) {
  const stationName = opts.station;
  const lineFilter = opts.line ? resolveLineCode(opts.line) : null;

  if (!stationName) {
    console.log('Provide --station with a station name.');
    return;
  }

  if (!ensureGtfs()) return;

  const matches = searchStation(stationName, lineFilter);
  if (!matches.length) {
    console.log(`No stations found matching '${stationName}'.`);
    return;
  }

  if (matches.length > 1 && matches[0].score > 0) {
    console.log(`Found ${matches.length} stations matching '${stationName}':`);
    for (const s of matches.slice(0, 8)) {
      const lineStr = s.lines?.length ? ` (${s.lines.join(', ')})` : '';
      console.log(`  ${s.name}${lineStr}`);
    }
    console.log(`\nUsing best match: ${matches[0].name}\n`);
  }

  const station = matches[0];
  const stopIds = resolveStopIds(station.name, lineFilter);

  if (!stopIds.length) {
    console.log(`Could not resolve stop IDs for '${station.name}'.`);
    return;
  }

  const routes = loadRoutes();
  const trips = loadTrips();
  const now = localNow();
  const yyyy = String(now.getUTCFullYear());
  const mo = String(now.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(now.getUTCDate()).padStart(2, '0');
  const todayStr = `${yyyy}${mo}${dd}`;
  const activeServices = getActiveServiceIds(todayStr);

  const hh = String(now.getUTCHours()).padStart(2, '0');
  const mm = String(now.getUTCMinutes()).padStart(2, '0');
  const currentTime = `${hh}:${mm}:00`;

  // Gather departures
  const inbound = [];
  const outbound = [];
  const seen = new Set();

  for (const stopId of stopIds) {
    const stopTimes = loadStopTimesForStop(stopId);
    for (const st of stopTimes) {
      const tripInfo = trips[st.trip_id] || {};
      const routeId = tripInfo.route_id || '';
      const serviceId = tripInfo.service_id || '';
      if (!activeServices.has(serviceId)) continue;

      const rShort = routes[routeId]?.route_short_name || routeId;
      if (lineFilter && rShort.toUpperCase() !== lineFilter) continue;

      const depTime = st.departure_time || st.arrival_time || '';
      if (depTime <= currentTime) continue;

      const trainNum = tripInfo.trip_short_name || trainNumberFromTripId(st.trip_id);
      const headsign = tripInfo.trip_headsign || '';
      const dir = tripInfo.direction_id;
      const dedup = `${rShort}|${trainNum}|${depTime}`;
      if (seen.has(dedup)) continue;
      seen.add(dedup);

      const lineMeta = METRA_LINES[rShort] || METRA_LINES[rShort.toUpperCase()];

      const entry = {
        line: rShort,
        lineName: lineMeta?.name || rShort,
        trainNum,
        headsign,
        time: depTime,
      };

      // Metra: direction_id 1 = inbound, 0 = outbound
      if (dir === '1') inbound.push(entry);
      else outbound.push(entry);
    }
  }

  inbound.sort((a, b) => a.time.localeCompare(b.time));
  outbound.sort((a, b) => a.time.localeCompare(b.time));

  const lineName = lineFilter && METRA_LINES[lineFilter] ? METRA_LINES[lineFilter].name : null;
  const dayLabel = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][now.getUTCDay()];

  console.log(`\n=== Schedule for: ${station.name} ===`);
  console.log(`    ${dayLabel}, ${mo}/${dd}/${yyyy}`);
  if (lineName) console.log(`    Line: ${lineName}`);
  console.log();

  if (inbound.length) {
    console.log(`Inbound (toward downtown Chicago) — ${inbound.length} remaining today:`);
    for (const e of inbound.slice(0, 20)) {
      const hsStr = e.headsign ? ` -> ${e.headsign}` : '';
      console.log(`  🚂 ${fmtGtfsTime(e.time)}  ${e.lineName} Train ${e.trainNum}${hsStr}`);
    }
    console.log();
  }

  if (outbound.length) {
    console.log(`Outbound (away from downtown) — ${outbound.length} remaining today:`);
    for (const e of outbound.slice(0, 20)) {
      const hsStr = e.headsign ? ` -> ${e.headsign}` : '';
      console.log(`  🚂 ${fmtGtfsTime(e.time)}  ${e.lineName} Train ${e.trainNum}${hsStr}`);
    }
    console.log();
  }

  if (!inbound.length && !outbound.length) {
    console.log('No remaining departures found for today.');
    console.log('This station may not have service on the current schedule.');
  }
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === '-h') {
    console.log(`Chicago Metra Commuter Rail — OpenClaw Skill

Commands:
  arrivals      Train arrivals (--station NAME) [--line CODE]
  vehicles      Live train positions (--line CODE)
  alerts        Service alerts [--line CODE]
  routes        List all 11 Metra lines
  stops         Search stops (--search NAME | --line CODE | --near LAT,LON [--radius MI])
  route-info    Line details and stops (--line CODE)
  fares         Fare table, or calculate (--from STATION --to STATION)
  schedule      Today's schedule (--station NAME) [--line CODE]
  refresh-gtfs  Download/refresh GTFS static data

Metra Lines: BNSF, ME, HC, MD-N, MD-W, NCS, RI, SWS, UP-N, UP-NW, UP-W

Environment: METRA_API_KEY (free, required for all real-time data)
Get a key at: https://metra.com/developers`);
    return;
  }

  const rest = args.slice(1);

  const optDefs = {
    station: { type: 'string' },
    line: { type: 'string' },
    search: { type: 'string' },
    near: { type: 'string' },
    radius: { type: 'string' },
    from: { type: 'string' },
    to: { type: 'string' },
  };

  let opts = {};
  try {
    const parsed = parseArgs({ args: rest, options: optDefs, allowPositionals: true, strict: false });
    opts = parsed.values;
  } catch (err) {
    console.error(`Error parsing arguments: ${err.message}`);
    process.exit(1);
  }

  const handlers = {
    'refresh-gtfs': () => cmdRefreshGtfs(),
    arrivals: () => cmdArrivals(opts),
    vehicles: () => cmdVehicles(opts),
    alerts: () => cmdAlerts(opts),
    routes: () => cmdRoutes(),
    stops: () => cmdStops(opts),
    'route-info': () => cmdRouteInfo(opts),
    fares: () => cmdFares(opts),
    schedule: () => cmdSchedule(opts),
  };

  if (handlers[command]) {
    Promise.resolve(handlers[command]()).catch(err => {
      if (err.name === 'TimeoutError' || err.message?.includes('timeout')) {
        console.error('Request timed out. Metra feed may be slow or unreachable. Try again in a moment.');
      } else if (err.code === 'ENOTFOUND' || err.code === 'ECONNREFUSED') {
        console.error('Network error: Could not reach Metra API. Check your internet connection.');
      } else if (err.message?.includes('Authentication failed')) {
        console.error(err.message);
        console.error('Get a free key at: https://metra.com/developers');
      } else {
        console.error(`Error: ${err.message}`);
      }
      process.exit(1);
    });
  } else {
    console.error(`Unknown command: ${command}`);
    console.error("Run 'node scripts/metra.mjs --help' for available commands.");
    process.exit(1);
  }
}

main();
