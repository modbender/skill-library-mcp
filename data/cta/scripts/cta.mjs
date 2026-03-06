#!/usr/bin/env node
/**
 * CTA Chicago Transit — OpenClaw Skill
 * Real-time L train arrivals, bus predictions, service alerts, and route info.
 * Uses CTA's Train Tracker, Bus Tracker, and Customer Alerts APIs.
 *
 * SECURITY MANIFEST
 *   Environment variables: CTA_TRAIN_API_KEY, CTA_BUS_API_KEY
 *   External endpoints:    https://lapi.transitchicago.com (Train Tracker, key required)
 *                          https://www.ctabustracker.com (Bus Tracker, key required)
 *                          https://www.transitchicago.com (Alerts, no key; GTFS static, no key)
 *   Local files written:   ~/.cta/gtfs/ (GTFS static data cache)
 *   Local files read:      ~/.cta/gtfs/*.txt (GTFS CSV files)
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
const CTA_TRAIN_API_KEY = process.env.CTA_TRAIN_API_KEY || '';
const CTA_BUS_API_KEY = process.env.CTA_BUS_API_KEY || '';

const TRAIN_BASE = 'https://lapi.transitchicago.com/api/1.0';
const BUS_BASE = 'https://www.ctabustracker.com/bustime/api/v2';
const ALERTS_BASE = 'https://www.transitchicago.com/api/1.0';
const GTFS_STATIC_URL = 'https://www.transitchicago.com/downloads/sch_data/google_transit.zip';

const GTFS_DIR = path.join(os.homedir(), '.cta', 'gtfs');

// ---------------------------------------------------------------------------
// L Train Lines
// ---------------------------------------------------------------------------
const L_LINES = {
  Red:  { name: 'Red Line',    color: 'Red',    terminals: ['Howard', '95th/Dan Ryan'] },
  Blue: { name: 'Blue Line',   color: 'Blue',   terminals: ['O\'Hare', 'Forest Park'] },
  Brn:  { name: 'Brown Line',  color: 'Brown',  terminals: ['Kimball', 'Loop'] },
  G:    { name: 'Green Line',  color: 'Green',  terminals: ['Harlem/Lake', 'Ashland/63rd', 'Cottage Grove'] },
  Org:  { name: 'Orange Line', color: 'Orange', terminals: ['Midway', 'Loop'] },
  P:    { name: 'Purple Line', color: 'Purple', terminals: ['Linden', 'Howard'] },
  Pink: { name: 'Pink Line',   color: 'Pink',   terminals: ['54th/Cermak', 'Loop'] },
  Y:    { name: 'Yellow Line', color: 'Yellow', terminals: ['Dempster-Skokie', 'Howard'] },
};

// Route code aliases for user-friendly matching
const ROUTE_ALIASES = {
  red: 'Red', blue: 'Blue', brown: 'Brn', brn: 'Brn',
  green: 'G', g: 'G', orange: 'Org', org: 'Org',
  purple: 'P', p: 'P', pink: 'Pink', yellow: 'Y', y: 'Y',
};

function resolveTrainRoute(input) {
  if (!input) return null;
  if (L_LINES[input]) return input;
  return ROUTE_ALIASES[input.toLowerCase()] || input;
}

// ---------------------------------------------------------------------------
// Key Station Data (for fuzzy matching without GTFS)
// mapid = parent station ID (4xxxx)
// ---------------------------------------------------------------------------
const STATIONS = [
  { mapid: '40890', name: "O'Hare", lines: ['Blue'], aliases: ['ohare', 'airport', "o'hare", 'ohare airport'] },
  { mapid: '40390', name: 'Forest Park', lines: ['Blue'], aliases: ['forest park'] },
  { mapid: '40930', name: 'Midway', lines: ['Org'], aliases: ['midway', 'midway airport'] },
  { mapid: '40900', name: 'Howard', lines: ['Red', 'P', 'Y'], aliases: ['howard'] },
  { mapid: '40450', name: '95th/Dan Ryan', lines: ['Red'], aliases: ['95th', 'dan ryan', '95th dan ryan'] },
  { mapid: '40380', name: 'Clark/Lake', lines: ['Blue', 'Brn', 'G', 'Org', 'P', 'Pink'], aliases: ['clark lake', 'clark and lake'] },
  { mapid: '40260', name: 'State/Lake', lines: ['Brn', 'G', 'Org', 'P', 'Pink'], aliases: ['state lake', 'state and lake'] },
  { mapid: '41700', name: 'Washington/Wabash', lines: ['Brn', 'G', 'Org', 'P', 'Pink'], aliases: ['washington wabash', 'washington and wabash'] },
  { mapid: '40680', name: 'Adams/Wabash', lines: ['Brn', 'G', 'Org', 'P', 'Pink'], aliases: ['adams wabash', 'adams and wabash'] },
  { mapid: '40850', name: 'Harold Washington Library', lines: ['Brn', 'Org', 'Pink', 'P'], aliases: ['library', 'harold washington', 'harold washington library'] },
  { mapid: '40160', name: 'LaSalle/Van Buren', lines: ['Brn', 'Org', 'Pink', 'P'], aliases: ['lasalle', 'van buren', 'lasalle van buren'] },
  { mapid: '40040', name: 'Quincy', lines: ['Brn', 'Org', 'Pink', 'P'], aliases: ['quincy'] },
  { mapid: '41320', name: 'Belmont', lines: ['Red', 'Brn', 'P'], aliases: ['belmont red', 'belmont brown'] },
  { mapid: '41220', name: 'Fullerton', lines: ['Red', 'Brn', 'P'], aliases: ['fullerton'] },
  { mapid: '41400', name: 'Roosevelt', lines: ['Red', 'Org', 'G'], aliases: ['roosevelt'] },
  { mapid: '40560', name: 'Jackson (Red)', lines: ['Red'], aliases: ['jackson red'] },
  { mapid: '40070', name: 'Jackson (Blue)', lines: ['Blue'], aliases: ['jackson blue'] },
  { mapid: '41450', name: 'Chicago (Red)', lines: ['Red'], aliases: ['chicago red', 'chicago ave red'] },
  { mapid: '41410', name: 'Chicago (Blue)', lines: ['Blue'], aliases: ['chicago blue', 'chicago ave blue'] },
  { mapid: '40330', name: 'Grand (Red)', lines: ['Red'], aliases: ['grand red'] },
  { mapid: '40490', name: 'Grand (Blue)', lines: ['Blue'], aliases: ['grand blue'] },
  { mapid: '41090', name: 'Monroe (Red)', lines: ['Red'], aliases: ['monroe red'] },
  { mapid: '41160', name: 'Monroe (Blue)', lines: ['Blue'], aliases: ['monroe blue'] },
  { mapid: '41440', name: 'Addison (Red)', lines: ['Red'], aliases: ['wrigley', 'addison red', 'cubs', 'wrigley field'] },
  { mapid: '41240', name: 'Addison (Brown)', lines: ['Brn'], aliases: ['addison brown'] },
  { mapid: '40190', name: 'Sox-35th', lines: ['Red'], aliases: ['sox', 'white sox', '35th', 'guaranteed rate', 'sox 35th'] },
  { mapid: '40350', name: 'UIC-Halsted', lines: ['Blue'], aliases: ['uic', 'united center', 'bulls', 'blackhawks', 'uic halsted'] },
  { mapid: '40530', name: 'Washington (Blue)', lines: ['Blue'], aliases: ['washington blue'] },
  { mapid: '41020', name: 'Logan Square', lines: ['Blue'], aliases: ['logan', 'logan square'] },
  { mapid: '40590', name: 'Damen (Blue)', lines: ['Blue'], aliases: ['wicker park', 'damen blue'] },
  { mapid: '41010', name: 'Kimball', lines: ['Brn'], aliases: ['kimball'] },
  { mapid: '40460', name: 'Linden', lines: ['P'], aliases: ['linden', 'wilmette'] },
  { mapid: '40140', name: 'Dempster-Skokie', lines: ['Y'], aliases: ['dempster', 'skokie'] },
  { mapid: '40830', name: 'Harlem/Lake (Green)', lines: ['G'], aliases: ['harlem green', 'harlem lake'] },
  { mapid: '40510', name: '54th/Cermak', lines: ['Pink'], aliases: ['54th cermak', '54th'] },
  { mapid: '41120', name: 'Cermak-Chinatown', lines: ['Red'], aliases: ['chinatown', 'cermak chinatown'] },
  { mapid: '40720', name: 'Cottage Grove', lines: ['G'], aliases: ['cottage grove'] },
  { mapid: '40290', name: 'Ashland/63rd', lines: ['G'], aliases: ['ashland 63rd'] },
  { mapid: '41000', name: 'Randolph/Wabash', lines: ['Brn', 'G', 'Org', 'P', 'Pink'], aliases: ['millennium', 'randolph', 'randolph wabash'] },
  { mapid: '40730', name: 'Western (Brown)', lines: ['Brn'], aliases: ['western brown'] },
  { mapid: '40220', name: 'Western (Blue - O\'Hare)', lines: ['Blue'], aliases: ['western blue ohare'] },
  { mapid: '40810', name: 'Western (Blue - Forest Park)', lines: ['Blue'], aliases: ['western blue forest park'] },
  { mapid: '41480', name: 'Western (Orange)', lines: ['Org'], aliases: ['western orange'] },
  { mapid: '40750', name: 'Merchandise Mart', lines: ['Brn', 'P'], aliases: ['merchandise mart', 'merch mart'] },
  { mapid: '40800', name: 'Sedgwick', lines: ['Brn', 'P'], aliases: ['sedgwick'] },
  { mapid: '40660', name: 'Armitage', lines: ['Brn', 'P'], aliases: ['armitage'] },
  { mapid: '40570', name: 'Diversey', lines: ['Brn', 'P'], aliases: ['diversey'] },
  { mapid: '41290', name: 'Lake (Red)', lines: ['Red'], aliases: ['lake red'] },
  { mapid: '40920', name: 'Pulaski (Blue)', lines: ['Blue'], aliases: ['pulaski blue'] },
  { mapid: '40180', name: 'Halsted (Orange)', lines: ['Org'], aliases: ['halsted orange'] },
  { mapid: '40980', name: 'Ashland (Orange)', lines: ['Org'], aliases: ['ashland orange'] },
  { mapid: '41060', name: '35th/Archer', lines: ['Org'], aliases: ['35th archer'] },
];

function searchStation(query, routeFilter) {
  const q = query.toLowerCase().replace(/['']/g, '').trim();

  // First try embedded stations
  const scored = [];
  for (const s of STATIONS) {
    if (routeFilter && !s.lines.includes(routeFilter)) continue;
    const nameNorm = s.name.toLowerCase().replace(/['']/g, '');
    let score = 999;
    if (nameNorm === q) score = 0;
    else if (s.aliases.some(a => a === q)) score = 1;
    else if (nameNorm.includes(q)) score = 2;
    else if (s.aliases.some(a => a.includes(q))) score = 3;
    else if (q.split(/\s+/).every(w => nameNorm.includes(w) || s.aliases.some(a => a.includes(w)))) score = 4;
    else continue;
    scored.push({ ...s, score });
  }
  scored.sort((a, b) => a.score - b.score || a.name.localeCompare(b.name));

  // Also search GTFS stops if available
  if (fs.existsSync(path.join(GTFS_DIR, 'stops.txt'))) {
    const stops = loadStops();
    for (const [sid, s] of Object.entries(stops)) {
      // Only consider parent stations (4xxxx) for train searches
      if (!sid.startsWith('4')) continue;
      if (scored.some(st => st.mapid === sid)) continue;
      const nameNorm = (s.stop_name || '').toLowerCase().replace(/['']/g, '');
      let score = 999;
      if (nameNorm === q) score = 5;
      else if (nameNorm.includes(q)) score = 6;
      else continue;
      scored.push({ mapid: sid, name: s.stop_name, lines: [], score });
    }
    scored.sort((a, b) => a.score - b.score || a.name.localeCompare(b.name));
  }

  return scored;
}

// ---------------------------------------------------------------------------
// Time helpers — CST/CDT (US Central Time)
// ---------------------------------------------------------------------------
function localTzOffsetHours() {
  const now = new Date();
  const year = now.getUTCFullYear();
  const mar1 = new Date(Date.UTC(year, 2, 1));
  const firstSunMar = (7 - mar1.getUTCDay()) % 7 + 1;
  const dstStart = Date.UTC(year, 2, firstSunMar + 7, 8);
  const nov1 = new Date(Date.UTC(year, 10, 1));
  const firstSunNov = (7 - nov1.getUTCDay()) % 7 + 1;
  const dstEnd = Date.UTC(year, 10, firstSunNov, 7);
  const ts = now.getTime();
  return (ts >= dstStart && ts < dstEnd) ? -5 : -6;
}

function toLocalDate(d) {
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
  return `${String(mo).padStart(2, '0')}/${String(day).padStart(2, '0')} ${h}:${String(m).padStart(2, '0')}${ampm}`;
}

// Parse CTA timestamp — all CTA APIs return Central Time.
// Train Tracker uses ISO: "2026-02-16T20:37:05"
// Bus Tracker uses:       "20260216 20:34"
// We store Central Time values in a Date's UTC slots so fmtTimeHM reads them directly.
function parseCTATimestamp(ts) {
  if (!ts) return null;

  // Bus Tracker format: YYYYMMDD HH:MM or YYYYMMDD HH:MM:SS
  const busMatch = ts.match(/^(\d{4})(\d{2})(\d{2})\s+(\d{2}):(\d{2})(?::(\d{2}))?$/);
  if (busMatch) {
    const [, y, mo, d, h, mi, s] = busMatch;
    return new Date(Date.UTC(
      parseInt(y), parseInt(mo) - 1, parseInt(d),
      parseInt(h), parseInt(mi), parseInt(s || '0')
    ));
  }

  // Train Tracker ISO format: YYYY-MM-DDTHH:MM:SS (Central Time, no timezone suffix)
  const isoMatch = ts.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$/);
  if (isoMatch) {
    const [, y, mo, d, h, mi, s] = isoMatch;
    return new Date(Date.UTC(
      parseInt(y), parseInt(mo) - 1, parseInt(d),
      parseInt(h), parseInt(mi), parseInt(s)
    ));
  }

  // Fallback: parse manually to avoid timezone interpretation
  const parsed = new Date(ts);
  if (!isNaN(parsed.getTime())) return parsed;
  return null;
}

// ---------------------------------------------------------------------------
// GTFS Static data helpers
// ---------------------------------------------------------------------------

function ensureGtfs() {
  if (!fs.existsSync(path.join(GTFS_DIR, 'stops.txt'))) {
    console.log(`GTFS static data not found at ${GTFS_DIR}`);
    console.log('Run: node scripts/cta.mjs refresh-gtfs');
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
  const headers = parseCsvLine(lines[0]);
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const vals = parseCsvLine(lines[i]);
    const obj = {};
    for (let j = 0; j < headers.length; j++) {
      obj[headers[j]] = vals[j] || '';
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

function loadRoutes() {
  const rows = loadCsv('routes.txt');
  const m = {};
  for (const r of rows) m[r.route_id] = r;
  return m;
}

function loadTrips() {
  const rows = loadCsv('trips.txt');
  const m = {};
  for (const r of rows) m[r.trip_id] = r;
  return m;
}

function loadStopTimesForTrip(tripId) {
  const rows = loadCsv('stop_times.txt');
  return rows.filter(r => r.trip_id === tripId)
    .sort((a, b) => parseInt(a.stop_sequence || '0') - parseInt(b.stop_sequence || '0'));
}

// ---------------------------------------------------------------------------
// Haversine
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
// API helpers
// ---------------------------------------------------------------------------

function requireTrainKey() {
  if (!CTA_TRAIN_API_KEY) {
    console.log('CTA Train Tracker API key required.');
    console.log('Get a free key at: https://www.transitchicago.com/developers/traintrackerapply/');
    console.log('Then set CTA_TRAIN_API_KEY in your environment.');
    return false;
  }
  return true;
}

function requireBusKey() {
  if (!CTA_BUS_API_KEY) {
    console.log('CTA Bus Tracker API key required.');
    console.log('Get a free key at: https://www.transitchicago.com/developers/bustracker/');
    console.log('Then set CTA_BUS_API_KEY in your environment.');
    return false;
  }
  return true;
}

async function fetchJSON(url) {
  const resp = await fetch(url, { signal: AbortSignal.timeout(30000) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status} from ${new URL(url).hostname}`);
  return resp.json();
}

function handleCTAError(data, apiName) {
  // Train Tracker errors
  if (data?.ctatt?.errCd && data.ctatt.errCd !== '0') {
    const code = data.ctatt.errCd;
    const msg = data.ctatt.errNm || 'Unknown error';
    if (code === '101') {
      console.log(`${apiName}: Invalid API key. Check your CTA_TRAIN_API_KEY.`);
    } else if (code === '501') {
      console.log(`${apiName}: No arrival data found. The station may not have active service right now.`);
    } else {
      console.log(`${apiName} error (${code}): ${msg}`);
    }
    return true;
  }
  // Bus Tracker errors
  if (data?.['bustime-response']?.error) {
    const errors = data['bustime-response'].error;
    const errArr = Array.isArray(errors) ? errors : [errors];
    for (const e of errArr) {
      const msg = e.msg || e.stpnm || 'Unknown error';
      if (msg.includes('Invalid API access key')) {
        console.log(`${apiName}: Invalid API key. Check your CTA_BUS_API_KEY.`);
      } else if (msg.includes('No data found') || msg.includes('No arrival times')) {
        console.log(`${apiName}: No data found. The stop/route may not have active service right now.`);
      } else {
        console.log(`${apiName} error: ${msg}`);
      }
    }
    return true;
  }
  return false;
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

async function cmdRefreshGtfs() {
  console.log(`Downloading GTFS static data to ${GTFS_DIR} ...`);
  fs.mkdirSync(GTFS_DIR, { recursive: true });

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
      console.error('  macOS: brew install unzip (or use built-in)');
      console.error('  Arch: sudo pacman -S unzip');
    } else {
      console.error(`Error extracting GTFS zip: ${err.message}`);
    }
    fs.unlinkSync(tmpZip);
    return;
  }
  fs.unlinkSync(tmpZip);

  const files = fs.readdirSync(GTFS_DIR).filter(f => f.endsWith('.txt')).sort();
  console.log(`Extracted ${files.length} files:`);
  for (const f of files) console.log(`  ${f}`);
  console.log('GTFS data refreshed successfully.');
}

// ---- Train Arrivals ----

async function cmdArrivals(opts) {
  if (!requireTrainKey()) return;

  let mapid = opts.mapid;
  let stopId = opts.stop;
  const stationName = opts.station;
  const stopSearch = opts['stop-search'];
  const routeFilter = opts.route ? resolveTrainRoute(opts.route) : null;

  // Resolve station by name search
  if (stationName || stopSearch) {
    const query = stationName || stopSearch;
    const matches = searchStation(query, routeFilter);
    if (!matches.length) {
      console.log(`No stations found matching '${query}'.`);
      console.log("Try 'stops --search <name>' to search all stops.");
      return;
    }
    if (matches.length > 1) {
      console.log(`Found ${matches.length} stations matching '${query}':`);
      for (const s of matches.slice(0, 8)) {
        const lineStr = s.lines?.length ? ` (${s.lines.join(', ')})` : '';
        console.log(`  ${s.mapid} — ${s.name}${lineStr}`);
      }
      console.log(`\nUsing best match: ${matches[0].name}\n`);
    }
    mapid = matches[0].mapid;
  }

  if (!mapid && !stopId) {
    console.log('Provide --station, --stop-search, --mapid, or --stop');
    return;
  }

  // Build URL
  let url;
  if (stopId) {
    url = `${TRAIN_BASE}/ttarrivals.aspx?key=${encodeURIComponent(CTA_TRAIN_API_KEY)}&stpid=${encodeURIComponent(stopId)}&max=15&outputType=JSON`;
  } else {
    url = `${TRAIN_BASE}/ttarrivals.aspx?key=${encodeURIComponent(CTA_TRAIN_API_KEY)}&mapid=${encodeURIComponent(mapid)}&max=15&outputType=JSON`;
  }

  const data = await fetchJSON(url);
  if (handleCTAError(data, 'Train Tracker')) return;

  const arrivals = data?.ctatt?.eta;
  if (!arrivals || arrivals.length === 0) {
    console.log('No upcoming train arrivals at this station.');
    return;
  }

  const arrList = Array.isArray(arrivals) ? arrivals : [arrivals];
  const stationLabel = arrList[0]?.staNm || mapid || stopId;
  console.log(`\n=== Train Arrivals at: ${stationLabel} ===\n`);

  // Filter by route if specified
  const filtered = routeFilter
    ? arrList.filter(a => a.rt === routeFilter)
    : arrList;

  if (!filtered.length) {
    console.log(`No arrivals found for ${L_LINES[routeFilter]?.name || routeFilter} at this station.`);
    return;
  }

  for (const a of filtered) {
    const line = L_LINES[a.rt];
    const lineName = line ? line.name : a.rt;
    const dest = a.destNm || 'Unknown';
    const isApproaching = a.isApp === '1';
    const isDelayed = a.isDly === '1';

    const arrTime = parseCTATimestamp(a.arrT);

    let etaStr = '';
    if (isApproaching) {
      etaStr = 'Due';
    } else if (arrTime) {
      // arrT is in Central Time — compare to Central now
      // Since parseCTATimestamp returns a Date in UTC with CT values,
      // compare against localNow which is also shifted to CT
      const now = localNow();
      const minsAway = Math.round((arrTime.getTime() - now.getTime()) / 60000);
      if (minsAway <= 1) etaStr = 'Due';
      else etaStr = `${minsAway} min`;
    }

    const timeStr = arrTime ? fmtTimeHM(arrTime) : '??';
    const delayStr = isDelayed ? ' (delayed)' : '';

    console.log(`  🚇 ${lineName} toward ${dest}`);
    console.log(`     ${timeStr} (${etaStr})${delayStr}`);
    if (a.rn) console.log(`     Run #${a.rn}`);
    console.log();
  }
}

// ---- Bus Arrivals ----

async function cmdBusArrivals(opts) {
  if (!requireBusKey()) return;

  let stopId = opts.stop;
  const stopSearch = opts['stop-search'];
  const routeFilter = opts.route;

  if (stopSearch) {
    if (!ensureGtfs()) return;
    const stops = loadStops();
    const query = stopSearch.toLowerCase();
    const matches = Object.values(stops).filter(s =>
      (s.stop_name || '').toLowerCase().includes(query)
    );
    if (!matches.length) {
      console.log(`No stops found matching '${stopSearch}'.`);
      return;
    }
    // Rank: prefer exact, then shorter names
    matches.sort((a, b) => {
      const an = (a.stop_name || '').toLowerCase();
      const bn = (b.stop_name || '').toLowerCase();
      if (an === query && bn !== query) return -1;
      if (bn === query && an !== query) return 1;
      return an.length - bn.length || an.localeCompare(bn);
    });
    if (matches.length > 1) {
      console.log(`Found ${matches.length} stops matching '${stopSearch}':`);
      for (const s of matches.slice(0, 10)) {
        console.log(`  ${s.stop_id.padStart(6)} — ${s.stop_name}`);
      }
      console.log(`\nUsing best match: ${matches[0].stop_name}\n`);
    }
    stopId = matches[0].stop_id;
  }

  if (!stopId) {
    console.log('Provide --stop or --stop-search');
    return;
  }

  let url = `${BUS_BASE}/getpredictions?key=${encodeURIComponent(CTA_BUS_API_KEY)}&stpid=${encodeURIComponent(stopId)}&format=json`;
  if (routeFilter) {
    url += `&rt=${encodeURIComponent(routeFilter)}`;
  }

  const data = await fetchJSON(url);
  if (handleCTAError(data, 'Bus Tracker')) return;

  const preds = data?.['bustime-response']?.prd;
  if (!preds || preds.length === 0) {
    console.log('No upcoming bus predictions at this stop.');
    return;
  }

  const predList = Array.isArray(preds) ? preds : [preds];
  const stopLabel = predList[0]?.stpnm || stopId;
  console.log(`\n=== Bus Predictions at: ${stopLabel} (Stop ${stopId}) ===\n`);

  for (const p of predList) {
    const route = p.rt || '?';
    const dir = p.rtdir || '';
    const dest = p.des || '';
    const predType = p.typ === 'A' ? 'Arriving' : 'Departing';

    const predTime = parseCTATimestamp(p.prdtm);
    const genTime = parseCTATimestamp(p.tmstmp);
    let minsAway = parseInt(p.prdctdn);
    if (isNaN(minsAway) && predTime && genTime) {
      minsAway = Math.round((predTime.getTime() - genTime.getTime()) / 60000);
    }

    const etaStr = (p.prdctdn === 'DUE' || minsAway <= 0) ? 'Due' :
      minsAway === 1 ? '1 min' : `${minsAway} min`;
    const timeStr = predTime ? fmtTimeHM(predTime) : '??';
    const delayed = p.dly === 'true' ? ' (delayed)' : '';

    console.log(`  🚌 Route ${route} ${dir} → ${dest}`);
    console.log(`     ${timeStr} (${etaStr})${delayed}`);
    if (p.vid) console.log(`     Vehicle #${p.vid}`);
    console.log();
  }
}

// ---- Train Vehicles (Positions) ----

async function cmdVehicles(opts) {
  if (!requireTrainKey()) return;

  const routeCode = opts.route ? resolveTrainRoute(opts.route) : null;
  if (!routeCode) {
    console.log('Provide --route with an L line code (e.g., Red, Blue, Brn, G, Org, P, Pink, Y)');
    return;
  }

  const line = L_LINES[routeCode];
  if (!line) {
    console.log(`Unknown L line: ${opts.route}`);
    console.log('Valid lines: Red, Blue, Brn (Brown), G (Green), Org (Orange), P (Purple), Pink, Y (Yellow)');
    return;
  }

  const url = `${TRAIN_BASE}/ttpositions.aspx?key=${encodeURIComponent(CTA_TRAIN_API_KEY)}&rt=${encodeURIComponent(routeCode)}&outputType=JSON`;
  const data = await fetchJSON(url);
  if (handleCTAError(data, 'Train Tracker')) return;

  const routes = data?.ctatt?.route;
  if (!routes) {
    console.log(`No position data available for ${line.name}.`);
    return;
  }

  const routeArr = Array.isArray(routes) ? routes : [routes];
  let allTrains = [];
  for (const r of routeArr) {
    const trains = r.train;
    if (!trains) continue;
    const trainArr = Array.isArray(trains) ? trains : [trains];
    allTrains = allTrains.concat(trainArr);
  }

  if (!allTrains.length) {
    console.log(`No active trains on ${line.name}.`);
    return;
  }

  console.log(`\n=== ${line.name} Train Positions (${allTrains.length} active) ===\n`);

  for (const t of allTrains) {
    const dest = t.destNm || 'Unknown';
    const nextSta = t.nextStaNm || 'Unknown';
    const isApp = t.isApp === '1';
    const isDly = t.isDly === '1';
    const lat = t.lat;
    const lon = t.lon;
    const heading = t.heading;

    let statusStr = '';
    if (isApp) statusStr = `Approaching ${nextSta}`;
    else statusStr = `En route to ${nextSta}`;
    if (isDly) statusStr += ' (delayed)';

    console.log(`  🚇 Run #${t.rn} → ${dest}`);
    console.log(`     ${statusStr}`);
    if (lat && lon) console.log(`     Position: (${lat}, ${lon}) heading ${heading || '?'}°`);
    console.log();
  }
}

// ---- Bus Vehicles ----

async function cmdBusVehicles(opts) {
  if (!requireBusKey()) return;

  const route = opts.route;
  if (!route) {
    console.log('Provide --route with a bus route number (e.g., 22, 36, 77)');
    return;
  }

  const url = `${BUS_BASE}/getvehicles?key=${encodeURIComponent(CTA_BUS_API_KEY)}&rt=${encodeURIComponent(route)}&format=json`;
  const data = await fetchJSON(url);
  if (handleCTAError(data, 'Bus Tracker')) return;

  const vehicles = data?.['bustime-response']?.vehicle;
  if (!vehicles || vehicles.length === 0) {
    console.log(`No active buses on route ${route}.`);
    return;
  }

  const vList = Array.isArray(vehicles) ? vehicles : [vehicles];
  console.log(`\n=== Route ${route} Bus Positions (${vList.length} active) ===\n`);

  for (const v of vList) {
    const vid = v.vid || '?';
    const dir = v.rtdir || '';
    const dest = v.des || '';
    const lat = v.lat;
    const lon = v.lon;
    const heading = v.hdg;
    const speed = v.spd;
    const delayed = v.dly === 'true' ? ' (delayed)' : '';

    const tsStr = v.tmstmp ? (() => {
      const t = parseCTATimestamp(v.tmstmp);
      return t ? fmtTimeHM(t) : v.tmstmp;
    })() : '';

    console.log(`  🚌 Vehicle #${vid} — ${dir}${delayed}`);
    if (dest) console.log(`     Destination: ${dest}`);
    if (lat && lon) console.log(`     Position: (${lat}, ${lon}) heading ${heading || '?'}° @ ${speed || '?'} mph`);
    if (tsStr) console.log(`     Last update: ${tsStr}`);
    console.log();
  }
}

// ---- Alerts ----

async function cmdAlerts(opts) {
  const routeFilter = opts.route;

  let url = `${ALERTS_BASE}/alerts.aspx?outputType=JSON`;
  if (routeFilter) {
    // Resolve L line codes to route IDs used by alerts API
    const resolved = resolveTrainRoute(routeFilter);
    url += `&routeid=${encodeURIComponent(resolved || routeFilter)}`;
  }

  const data = await fetchJSON(url);

  const alerts = data?.CTAAlerts?.Alert;
  if (!alerts || alerts.length === 0) {
    const filterMsg = routeFilter ? ` for ${routeFilter}` : '';
    console.log(`No active service alerts${filterMsg}.`);
    return;
  }

  const alertList = Array.isArray(alerts) ? alerts : [alerts];
  console.log(`\n=== CTA Service Alerts (${alertList.length} active) ===\n`);

  for (const a of alertList) {
    const headline = a.Headline || 'No headline';
    const shortDesc = a.ShortDescription || '';
    const impact = a.Impact || '';
    const severity = a.SeverityScore || '';

    // Affected services
    const services = a.ImpactedService?.Service;
    const serviceList = services ? (Array.isArray(services) ? services : [services]) : [];
    const affected = serviceList.map(s => s.ServiceName || s.ServiceId || '').filter(Boolean);

    // Event start/end
    const eventStart = a.EventStart || '';
    const eventEnd = a.EventEnd || '';

    let severityIcon = '';
    const severityNum = parseInt(severity) || 0;
    if (severityNum >= 70) severityIcon = '🔴';
    else if (severityNum >= 40) severityIcon = '🟡';
    else severityIcon = '🟢';

    console.log(`${severityIcon} ${headline}`);
    if (affected.length) console.log(`   Routes: ${affected.join(', ')}`);
    if (impact) console.log(`   Impact: ${impact}`);
    if (eventStart || eventEnd) console.log(`   Period: ${eventStart} — ${eventEnd || 'ongoing'}`);
    if (shortDesc) {
      let desc = shortDesc;
      if (desc.length > 300) desc = desc.slice(0, 300) + '...';
      console.log(`   ${desc}`);
    }
    console.log();
  }
}

// ---- Routes ----

async function cmdRoutes() {
  // Show L lines (always available)
  console.log('\n=== CTA L Train Lines ===\n');
  for (const [code, line] of Object.entries(L_LINES)) {
    console.log(`  ${code.padEnd(5)} | ${line.name.padEnd(13)} | ${line.terminals.join(' ↔ ')}`);
  }

  // Show bus routes from GTFS if available
  if (ensureGtfs()) {
    const routes = loadRoutes();
    const typeNames = { '0': 'Tram', '1': 'Rail', '2': 'Rail', '3': 'Bus', '4': 'Ferry' };
    const busRoutes = Object.values(routes).filter(r => r.route_type === '3');

    console.log(`\n=== CTA Bus Routes (${busRoutes.length}) ===\n`);
    busRoutes.sort((a, b) => {
      const an = parseInt(a.route_short_name) || 9999;
      const bn = parseInt(b.route_short_name) || 9999;
      return an - bn || a.route_short_name.localeCompare(b.route_short_name);
    });
    for (const r of busRoutes) {
      const short = (r.route_short_name || r.route_id).padStart(5);
      const longName = r.route_long_name || '';
      console.log(`  ${short} | ${longName}`);
    }
  }
}

async function cmdBusRoutes() {
  if (!requireBusKey()) return;

  const url = `${BUS_BASE}/getroutes?key=${encodeURIComponent(CTA_BUS_API_KEY)}&format=json`;
  const data = await fetchJSON(url);
  if (handleCTAError(data, 'Bus Tracker')) return;

  const routes = data?.['bustime-response']?.routes;
  if (!routes || routes.length === 0) {
    console.log('No bus routes found.');
    return;
  }

  const routeList = Array.isArray(routes) ? routes : [routes];
  console.log(`\n=== CTA Bus Routes (${routeList.length}) ===\n`);

  for (const r of routeList) {
    const num = (r.rt || '?').padStart(5);
    const name = r.rtnm || '';
    const color = r.rtclr ? ` [${r.rtclr}]` : '';
    console.log(`  ${num} | ${name}${color}`);
  }
}

// ---- Stops ----

function cmdStops(opts) {
  if (!ensureGtfs()) return;
  const stops = loadStops();

  if (opts.search) {
    const query = opts.search.toLowerCase();
    const matches = Object.values(stops).filter(s =>
      (s.stop_name || '').toLowerCase().includes(query) ||
      (s.stop_desc || '').toLowerCase().includes(query)
    );
    if (!matches.length) { console.log(`No stops found matching '${opts.search}'.`); return; }
    console.log(`\n=== Stops matching '${opts.search}' (${matches.length} found) ===\n`);
    for (const s of matches.sort((a, b) => a.stop_name.localeCompare(b.stop_name)).slice(0, 25)) {
      console.log(`  📍 ${s.stop_name}`);
      console.log(`     ID: ${s.stop_id}  |  (${s.stop_lat}, ${s.stop_lon})`);
      if (s.stop_desc) console.log(`     ${s.stop_desc}`);
      console.log();
    }
  } else if (opts.near) {
    const parts = opts.near.split(',');
    if (parts.length !== 2) { console.log('Invalid format. Use: --near LAT,LON'); return; }
    const [lat, lon] = parts.map(Number);
    if (isNaN(lat) || isNaN(lon)) { console.log('Invalid format. Use: --near LAT,LON'); return; }
    const radius = opts.radius ? parseFloat(opts.radius) : 0.5;
    if (isNaN(radius) || radius <= 0) { console.log('Invalid --radius value. Must be a positive number (miles).'); return; }

    const nearby = [];
    for (const s of Object.values(stops)) {
      const slat = parseFloat(s.stop_lat), slon = parseFloat(s.stop_lon);
      if (isNaN(slat) || isNaN(slon)) continue;
      const dist = haversine(lat, lon, slat, slon);
      if (dist <= radius) nearby.push([dist, s]);
    }
    nearby.sort((a, b) => a[0] - b[0]);

    if (!nearby.length) { console.log(`No stops found within ${radius} miles of (${lat}, ${lon}).`); return; }
    console.log(`\n=== Nearby Stops (${nearby.length} within ${radius} mi) ===\n`);
    for (const [dist, s] of nearby.slice(0, 20)) {
      console.log(`  📍 ${s.stop_name} — ${dist.toFixed(2)} mi`);
      console.log(`     ID: ${s.stop_id}`);
      console.log();
    }
  } else {
    console.log('Provide --search <name> or --near LAT,LON');
  }
}

// ---- Route Info ----

async function cmdRouteInfo(opts) {
  const routeInput = opts.route;
  if (!routeInput) {
    console.log('Provide --route with a line code (Red, Blue, etc.) or bus route number.');
    return;
  }

  // Check if it's an L line
  const resolved = resolveTrainRoute(routeInput);
  if (L_LINES[resolved]) {
    // Use GTFS for stop list
    if (!ensureGtfs()) return;
    const routes = loadRoutes();
    const trips = loadTrips();
    const stops = loadStops();
    const line = L_LINES[resolved];

    console.log(`\n=== ${line.name} ===`);
    console.log(`    Code: ${resolved}  |  Terminals: ${line.terminals.join(' ↔ ')}`);
    console.log();

    // Find a trip for this route to get stop sequence
    const routeTrips = Object.values(trips).filter(t => {
      const rShort = routes[t.route_id]?.route_short_name || '';
      return rShort === resolved || t.route_id === resolved || rShort === line.name;
    });

    if (routeTrips.length) {
      const dir0 = routeTrips.filter(t => t.direction_id === '0');
      const sampleTrip = (dir0.length ? dir0 : routeTrips)[0];
      const stopTimes = loadStopTimesForTrip(sampleTrip.trip_id);

      if (stopTimes.length) {
        console.log(`Stops (${sampleTrip.trip_headsign || 'direction 0'}):`);
        for (const st of stopTimes) {
          const sname = stops[st.stop_id]?.stop_name || st.stop_id;
          console.log(`  ${(st.stop_sequence || '').padStart(3)}. ${sname} (ID: ${st.stop_id})`);
        }
      }
    } else {
      console.log('No trip data found in GTFS. Try running refresh-gtfs.');
    }
    return;
  }

  // Must be a bus route — try Bus Tracker API for directions and stops
  if (!requireBusKey()) {
    // Fall back to GTFS
    if (!ensureGtfs()) return;
    const routes = loadRoutes();
    const trips = loadTrips();
    const stops = loadStops();

    const routeId = Object.keys(routes).find(k =>
      routes[k].route_short_name === routeInput || k === routeInput
    );
    if (!routeId) { console.log(`Route '${routeInput}' not found.`); return; }
    const r = routes[routeId];
    console.log(`\n=== Route ${r.route_short_name || routeId} — ${r.route_long_name || ''} ===\n`);

    const routeTrips = Object.values(trips).filter(t => t.route_id === routeId);
    if (routeTrips.length) {
      const dir0 = routeTrips.filter(t => t.direction_id === '0');
      const sampleTrip = (dir0.length ? dir0 : routeTrips)[0];
      const stopTimes = loadStopTimesForTrip(sampleTrip.trip_id);
      if (stopTimes.length) {
        console.log(`Stops (${sampleTrip.trip_headsign || ''}):`);
        for (const st of stopTimes) {
          const sname = stops[st.stop_id]?.stop_name || st.stop_id;
          console.log(`  ${(st.stop_sequence || '').padStart(3)}. ${sname} (ID: ${st.stop_id})`);
        }
      }
    }
    return;
  }

  // Use Bus Tracker API
  const dirUrl = `${BUS_BASE}/getdirections?key=${encodeURIComponent(CTA_BUS_API_KEY)}&rt=${encodeURIComponent(routeInput)}&format=json`;
  const dirData = await fetchJSON(dirUrl);
  if (handleCTAError(dirData, 'Bus Tracker')) return;

  const directions = dirData?.['bustime-response']?.directions;
  if (!directions) {
    console.log(`Route '${routeInput}' not found or no direction data available.`);
    return;
  }

  const dirList = Array.isArray(directions) ? directions : [directions];
  console.log(`\n=== Route ${routeInput} ===\n`);

  for (const dir of dirList) {
    const dirName = dir.dir || dir;
    console.log(`Direction: ${dirName}`);

    const stopsUrl = `${BUS_BASE}/getstops?key=${encodeURIComponent(CTA_BUS_API_KEY)}&rt=${encodeURIComponent(routeInput)}&dir=${encodeURIComponent(dirName)}&format=json`;
    const stopsData = await fetchJSON(stopsUrl);
    if (handleCTAError(stopsData, 'Bus Tracker')) continue;

    const stopsList = stopsData?.['bustime-response']?.stops;
    if (!stopsList) continue;

    const stopsArr = Array.isArray(stopsList) ? stopsList : [stopsList];
    for (const s of stopsArr) {
      const sid = s.stpid || '?';
      const sname = s.stpnm || '?';
      console.log(`  ${sid.padStart(6)} — ${sname}`);
    }
    console.log();
  }
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === '-h') {
    console.log(`CTA Chicago Transit — OpenClaw Skill

Commands:
  arrivals        Train arrivals (--station NAME | --stop-search NAME | --mapid ID | --stop ID) [--route LINE]
  bus-arrivals    Bus predictions (--stop ID | --stop-search NAME) [--route NUM]
  vehicles        Live train positions (--route LINE)
  bus-vehicles    Live bus positions (--route NUM)
  alerts          Service alerts [--route ID]
  routes          List all CTA routes (L lines + bus)
  bus-routes      List all bus routes (from Bus Tracker API)
  stops           Search stops (--search NAME | --near LAT,LON [--radius MI])
  route-info      Route details and stops (--route LINE_OR_NUM)
  refresh-gtfs    Download/refresh GTFS static data

L Lines: Red, Blue, Brn (Brown), G (Green), Org (Orange), P (Purple), Pink, Y (Yellow)

Environment: CTA_TRAIN_API_KEY, CTA_BUS_API_KEY (free, from transitchicago.com)`);
    return;
  }

  const rest = args.slice(1);

  const optDefs = {
    route: { type: 'string' },
    stop: { type: 'string' },
    'stop-search': { type: 'string' },
    station: { type: 'string' },
    mapid: { type: 'string' },
    search: { type: 'string' },
    near: { type: 'string' },
    radius: { type: 'string' },
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
    'bus-arrivals': () => cmdBusArrivals(opts),
    vehicles: () => cmdVehicles(opts),
    'bus-vehicles': () => cmdBusVehicles(opts),
    alerts: () => cmdAlerts(opts),
    routes: () => cmdRoutes(),
    'bus-routes': () => cmdBusRoutes(),
    stops: () => cmdStops(opts),
    'route-info': () => cmdRouteInfo(opts),
  };

  if (handlers[command]) {
    Promise.resolve(handlers[command]()).catch(err => {
      if (err.name === 'TimeoutError' || err.message?.includes('timeout')) {
        console.error('Request timed out. CTA API may be slow or unreachable. Try again in a moment.');
      } else if (err.code === 'ENOTFOUND' || err.code === 'ECONNREFUSED') {
        console.error('Network error: Could not reach CTA API. Check your internet connection.');
      } else {
        console.error(`Error: ${err.message}`);
      }
      process.exit(1);
    });
  } else {
    console.error(`Unknown command: ${command}`);
    console.error("Run 'node scripts/cta.mjs --help' for available commands.");
    process.exit(1);
  }
}

// Run CLI when executed directly
const isMain = process.argv[1] && import.meta.url === `file://${process.argv[1]}`;
if (isMain) main();

// Exports for testing
export {
  parseCTATimestamp, parseCsvLine, haversine, localTzOffsetHours,
  fmtTime, fmtTimeHM, resolveTrainRoute, searchStation, STATIONS,
};
