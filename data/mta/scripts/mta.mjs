#!/usr/bin/env node
/**
 * NYC MTA Transit — OpenClaw Skill
 * Real-time subway arrivals (GTFS-RT protobuf), bus predictions (SIRI JSON),
 * service alerts, and route info for New York City.
 *
 * SECURITY MANIFEST
 *   Environment variables: MTA_BUS_API_KEY (optional — only for bus commands)
 *   External endpoints:    api-endpoint.mta.info (subway GTFS-RT, open access, no auth)
 *                          bustime.mta.info (SIRI bus API, key required)
 *                          web.mta.info (GTFS static, no auth)
 *   Local files written:   ~/.mta/gtfs/ (GTFS static data cache)
 *   Local files read:      ~/.mta/gtfs/*.txt (GTFS CSV files)
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
const MTA_BUS_API_KEY = process.env.MTA_BUS_API_KEY || '';

const FEED_BASE = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds';
// MTA requires %2F encoding for the path separator after mtagtfsfeeds
const subwayFeedUrl = (feed) => `${FEED_BASE}/nyct%2F${feed}`;
const alertsFeedUrl = (feed) => `${FEED_BASE}/camsys%2F${feed}`;
const BUS_SIRI_BASE = 'https://bustime.mta.info/api/siri';
const BUS_OBA_BASE = 'https://bustime.mta.info/api/where';
// HTTP intentional — MTA does not serve this endpoint over HTTPS (redirects back to HTTP)
const GTFS_STATIC_URL = 'http://web.mta.info/developers/data/nyct/subway/google_transit.zip';

const GTFS_DIR = path.join(os.homedir(), '.mta', 'gtfs');

// ---------------------------------------------------------------------------
// Subway Feed Map — which feed to fetch for each line
// ---------------------------------------------------------------------------
const FEED_MAP = {
  '1': 'gtfs', '2': 'gtfs', '3': 'gtfs', '4': 'gtfs', '5': 'gtfs', '6': 'gtfs', '7': 'gtfs', 'GS': 'gtfs',
  'A': 'gtfs-ace', 'C': 'gtfs-ace', 'E': 'gtfs-ace', 'H': 'gtfs-ace', 'FS': 'gtfs-ace',
  'B': 'gtfs-bdfm', 'D': 'gtfs-bdfm', 'F': 'gtfs-bdfm', 'M': 'gtfs-bdfm',
  'G': 'gtfs-g',
  'J': 'gtfs-jz', 'Z': 'gtfs-jz',
  'L': 'gtfs-l',
  'N': 'gtfs-nqrw', 'Q': 'gtfs-nqrw', 'R': 'gtfs-nqrw', 'W': 'gtfs-nqrw',
  'SI': 'gtfs-si',
};

const ALL_FEEDS = ['gtfs', 'gtfs-ace', 'gtfs-bdfm', 'gtfs-g', 'gtfs-jz', 'gtfs-l', 'gtfs-nqrw', 'gtfs-si'];

// ---------------------------------------------------------------------------
// Subway Line Metadata
// ---------------------------------------------------------------------------
const SUBWAY_LINES = {
  '1': { name: '1 train', color: 'Red', route: '7th Ave Local', terminals: ['Van Cortlandt Park-242 St', 'South Ferry'] },
  '2': { name: '2 train', color: 'Red', route: '7th Ave Express', terminals: ['Wakefield-241 St', 'Flatbush Ave-Brooklyn College'] },
  '3': { name: '3 train', color: 'Red', route: '7th Ave Express', terminals: ['Harlem-148 St', 'New Lots Ave'] },
  '4': { name: '4 train', color: 'Green', route: 'Lexington Ave Express', terminals: ['Woodlawn', 'Crown Heights-Utica Ave'] },
  '5': { name: '5 train', color: 'Green', route: 'Lexington Ave Express', terminals: ['Eastchester-Dyre Ave', 'Flatbush Ave-Brooklyn College'] },
  '6': { name: '6 train', color: 'Green', route: 'Lexington Ave Local', terminals: ['Pelham Bay Park', 'Brooklyn Bridge-City Hall'] },
  '7': { name: '7 train', color: 'Purple', route: 'Flushing', terminals: ['Flushing-Main St', '34 St-Hudson Yards'] },
  'A': { name: 'A train', color: 'Blue', route: '8th Ave Express', terminals: ['Inwood-207 St', 'Far Rockaway / Lefferts Blvd'] },
  'C': { name: 'C train', color: 'Blue', route: '8th Ave Local', terminals: ['168 St', 'Euclid Ave'] },
  'E': { name: 'E train', color: 'Blue', route: '8th Ave Local', terminals: ['Jamaica Center', 'World Trade Center'] },
  'B': { name: 'B train', color: 'Orange', route: '6th Ave Express', terminals: ['Bedford Park Blvd', 'Brighton Beach'] },
  'D': { name: 'D train', color: 'Orange', route: '6th Ave Express', terminals: ['Norwood-205 St', 'Coney Island-Stillwell Ave'] },
  'F': { name: 'F train', color: 'Orange', route: '6th Ave Local', terminals: ['Jamaica-179 St', 'Coney Island-Stillwell Ave'] },
  'M': { name: 'M train', color: 'Orange', route: '6th Ave Local', terminals: ['Middle Village-Metropolitan Ave', 'Forest Hills-71 Ave'] },
  'G': { name: 'G train', color: 'Light Green', route: 'Brooklyn-Queens Crosstown', terminals: ['Court Sq', 'Church Ave'] },
  'J': { name: 'J train', color: 'Brown', route: 'Nassau St', terminals: ['Jamaica Center', 'Broad St'] },
  'Z': { name: 'Z train', color: 'Brown', route: 'Nassau St Express', terminals: ['Jamaica Center', 'Broad St'] },
  'L': { name: 'L train', color: 'Gray', route: '14th St-Canarsie', terminals: ['8 Ave', 'Canarsie-Rockaway Pkwy'] },
  'N': { name: 'N train', color: 'Yellow', route: 'Broadway Express', terminals: ['Astoria-Ditmars Blvd', 'Coney Island-Stillwell Ave'] },
  'Q': { name: 'Q train', color: 'Yellow', route: 'Broadway Express', terminals: ['96 St', 'Coney Island-Stillwell Ave'] },
  'R': { name: 'R train', color: 'Yellow', route: 'Broadway Local', terminals: ['Forest Hills-71 Ave', 'Bay Ridge-95 St'] },
  'W': { name: 'W train', color: 'Yellow', route: 'Broadway Local', terminals: ['Astoria-Ditmars Blvd', 'Whitehall St-South Ferry'] },
  'GS': { name: '42 St Shuttle', color: 'Gray', route: '42nd St Shuttle', terminals: ['Times Sq-42 St', 'Grand Central-42 St'] },
  'FS': { name: 'Franklin Ave Shuttle', color: 'Gray', route: 'Franklin Ave Shuttle', terminals: ['Franklin Ave', 'Prospect Park'] },
  'H': { name: 'Rockaway Park Shuttle', color: 'Gray', route: 'Rockaway Park Shuttle', terminals: ['Broad Channel', 'Rockaway Park-Beach 116 St'] },
  'SI': { name: 'Staten Island Railway', color: 'Blue', route: 'Staten Island Railway', terminals: ['St George', 'Tottenville'] },
};

// ---------------------------------------------------------------------------
// Major Stations with Aliases (for fuzzy matching without GTFS)
// parent_stop_id is the numeric prefix used in GTFS stop IDs
// ---------------------------------------------------------------------------
const STATIONS = [
  { id: '127', name: 'Times Sq-42 St', lines: ['1','2','3','7','N','Q','R','W','GS'], aliases: ['times square', '42nd street', '42nd', 'tsq', 'times sq'] },
  { id: '631', name: 'Grand Central-42 St', lines: ['4','5','6','7','GS'], aliases: ['grand central', 'gct', 'grand central terminal'] },
  { id: 'A28', name: '34 St-Penn Station', lines: ['A','C','E'], aliases: ['penn station', 'penn', 'msg', 'madison square garden'] },
  { id: '128', name: '34 St-Penn Station', lines: ['1','2','3'], aliases: ['penn station 123', '34th penn 123'] },
  { id: 'D17', name: '34 St-Herald Sq', lines: ['B','D','F','M','N','Q','R','W'], aliases: ['herald square', 'macys', '34th herald', 'herald sq'] },
  { id: '635', name: '14 St-Union Sq', lines: ['4','5','6','L','N','Q','R','W'], aliases: ['union square', '14th street', 'union sq'] },
  { id: 'R20', name: 'Fulton St', lines: ['2','3','4','5','A','C','J','Z'], aliases: ['fulton', 'fulton street'] },
  { id: 'R31', name: 'Atlantic Ave-Barclays Ctr', lines: ['2','3','4','5','B','D','N','Q','R'], aliases: ['barclays', 'atlantic', 'barclays center', 'atlantic ave'] },
  { id: 'A41', name: 'Jay St-MetroTech', lines: ['A','C','F','R'], aliases: ['jay street', 'metrotech', 'downtown brooklyn'] },
  { id: 'A34', name: 'Chambers St', lines: ['A','C'], aliases: ['chambers'] },
  { id: 'E01', name: 'World Trade Center', lines: ['E'], aliases: ['wtc', 'world trade', 'world trade center'] },
  { id: '137', name: 'Chambers St', lines: ['1','2','3'], aliases: ['chambers 123'] },
  { id: 'A24', name: '59 St-Columbus Circle', lines: ['1','A','B','C','D'], aliases: ['columbus circle', '59th', '59 st'] },
  { id: '726', name: '34 St-Hudson Yards', lines: ['7'], aliases: ['hudson yards'] },
  { id: '418', name: 'Brooklyn Bridge-City Hall', lines: ['4','5','6','J','Z'], aliases: ['brooklyn bridge', 'city hall'] },
  { id: 'R23', name: 'Wall St', lines: ['2','3'], aliases: ['wall street'] },
  { id: '629', name: 'Lexington Ave/59 St', lines: ['N','R','W','4','5','6'], aliases: ['lex', 'lexington', 'bloomingdales', 'lex 59'] },
  { id: 'A12', name: '125 St', lines: ['A','B','C','D'], aliases: ['125th', 'harlem'] },
  { id: '225', name: '125 St', lines: ['1'], aliases: ['125th 1'] },
  { id: '621', name: '125 St', lines: ['4','5','6'], aliases: ['125th 456'] },
  { id: 'A32', name: 'Canal St', lines: ['A','C','E'], aliases: ['canal', 'chinatown'] },
  { id: '640', name: 'Canal St', lines: ['6','J','Z','N','Q','R','W'], aliases: ['canal st 6', 'canal nqrw'] },
  { id: 'A31', name: '14 St/8 Ave', lines: ['A','C','E','L'], aliases: ['8th ave 14th', 'chelsea', '14 st 8 ave'] },
  { id: 'A36', name: 'West 4 St-Washington Sq', lines: ['A','B','C','D','E','F','M'], aliases: ['west 4th', 'washington square', 'nyu', 'west 4 st'] },
  { id: 'D13', name: '161 St-Yankee Stadium', lines: ['4','B','D'], aliases: ['yankee stadium', 'yankees', '161st'] },
  { id: '702', name: 'Mets-Willets Point', lines: ['7'], aliases: ['citi field', 'mets', 'willets point'] },
  { id: 'H11', name: 'Howard Beach-JFK Airport', lines: ['A'], aliases: ['jfk', 'airport', 'howard beach'] },
  { id: 'D43', name: 'Coney Island-Stillwell Ave', lines: ['D','F','N','Q'], aliases: ['coney island', 'stillwell'] },
  { id: '401', name: 'Borough Hall', lines: ['4','5'], aliases: ['borough hall'] },
  { id: 'R28', name: 'Court St', lines: ['R'], aliases: ['court st', 'court street'] },
  { id: 'G14', name: 'Court Sq', lines: ['G','7','E','M'], aliases: ['court sq', 'court square', 'long island city'] },
  { id: 'L01', name: '8 Ave', lines: ['L'], aliases: ['8 ave l', '8th ave l'] },
  { id: 'L29', name: 'Canarsie-Rockaway Pkwy', lines: ['L'], aliases: ['canarsie', 'rockaway pkwy'] },
  { id: 'R01', name: 'Astoria-Ditmars Blvd', lines: ['N','W'], aliases: ['astoria', 'ditmars'] },
  { id: 'Q01', name: '96 St', lines: ['Q'], aliases: ['96th q', '96 st 2nd ave'] },
  { id: '101', name: 'Van Cortlandt Park-242 St', lines: ['1'], aliases: ['van cortlandt', '242 st'] },
  { id: '201', name: 'Wakefield-241 St', lines: ['2'], aliases: ['wakefield', '241 st'] },
  { id: '142', name: 'South Ferry', lines: ['1'], aliases: ['south ferry', 'whitehall', 'staten island ferry'] },
  { id: 'A02', name: 'Inwood-207 St', lines: ['A'], aliases: ['inwood', '207 st'] },
  { id: 'R17', name: '49 St', lines: ['N','R','W'], aliases: ['49th', 'rockefeller center area'] },
  { id: 'D15', name: '47-50 Sts-Rockefeller Ctr', lines: ['B','D','F','M'], aliases: ['rockefeller', 'rockefeller center', 'rock center', '47-50'] },
  { id: '227', name: '96 St', lines: ['1','2','3'], aliases: ['96th 123'] },
  { id: '626', name: '86 St', lines: ['4','5','6'], aliases: ['86th lex', '86 st lex'] },
  { id: '132', name: '72 St', lines: ['1','2','3'], aliases: ['72nd 123', '72 st 1'] },
  { id: 'R14', name: '57 St-7 Av', lines: ['N','Q','R','W'], aliases: ['57th 7th', '57 st 7 ave'] },
  { id: 'A25', name: '50 St', lines: ['A','C','E'], aliases: ['50th ace'] },
  { id: '125', name: '50 St', lines: ['1'], aliases: ['50th 1'] },
];

// ---------------------------------------------------------------------------
// Time helpers — Eastern Time (EST/EDT)
// ---------------------------------------------------------------------------
function localTzOffsetHours() {
  const now = new Date();
  const year = now.getUTCFullYear();
  // 2nd Sunday of March
  const mar1 = new Date(Date.UTC(year, 2, 1));
  const firstSunMar = (7 - mar1.getUTCDay()) % 7 + 1;
  const dstStart = Date.UTC(year, 2, firstSunMar + 7, 7); // 2:00 AM EST = 07:00 UTC
  // 1st Sunday of November
  const nov1 = new Date(Date.UTC(year, 10, 1));
  const firstSunNov = (7 - nov1.getUTCDay()) % 7 + 1;
  const dstEnd = Date.UTC(year, 10, firstSunNov, 6); // 2:00 AM EDT = 06:00 UTC
  const ts = now.getTime();
  return (ts >= dstStart && ts < dstEnd) ? -4 : -5;
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
  return `${String(mo).padStart(2, '0')}/${String(day).padStart(2, '0')} ${h}:${String(m).padStart(2, '0')}${ampm}`;
}

// ---------------------------------------------------------------------------
// GTFS-RT Protobuf helpers (subway feeds + alerts)
// ---------------------------------------------------------------------------

let _protobufRoot = null;

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

  // Load proto files from disk (proto/ directory)
  const protoDir = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'proto');
  const gtfsProto = path.join(protoDir, 'gtfs-realtime.proto');
  const nyctProto = path.join(protoDir, 'nyct-subway.proto');

  const root = new protobuf.Root();
  root.resolvePath = (origin, target) => {
    return path.join(protoDir, path.basename(target));
  };
  await root.load([gtfsProto, nyctProto]);
  _protobufRoot = root;
  return root;
}

async function parseSubwayFeed(feedName) {
  const root = await getProtobufRoot();
  const FeedMessage = root.lookupType('transit_realtime.FeedMessage');
  const url = subwayFeedUrl(feedName);
  const resp = await fetch(url, { signal: AbortSignal.timeout(30000) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status} fetching ${url}`);
  const buf = Buffer.from(await resp.arrayBuffer());
  if (buf.length > 0 && buf[0] === 0x3c) {
    throw new Error('Feed returned HTML instead of protobuf — endpoint may be temporarily unavailable');
  }
  return FeedMessage.decode(buf);
}

async function parseAlertsFeed(feedUrl) {
  const root = await getProtobufRoot();
  const FeedMessage = root.lookupType('transit_realtime.FeedMessage');
  const resp = await fetch(feedUrl, { signal: AbortSignal.timeout(30000) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status} fetching ${feedUrl}`);
  const buf = Buffer.from(await resp.arrayBuffer());
  if (buf.length > 0 && buf[0] === 0x3c) {
    throw new Error('Feed returned HTML instead of protobuf — endpoint may be temporarily unavailable');
  }
  return FeedMessage.decode(buf);
}

// ---------------------------------------------------------------------------
// Bus API helpers (SIRI JSON + OneBusAway)
// ---------------------------------------------------------------------------

function requireBusKey() {
  if (!MTA_BUS_API_KEY) {
    console.log('MTA BusTime API key required.');
    console.log('Get a free key at: https://register.developer.obanyc.com/');
    console.log('Then set MTA_BUS_API_KEY in your environment.');
    return false;
  }
  return true;
}

async function fetchJSON(url) {
  const resp = await fetch(url, { signal: AbortSignal.timeout(30000) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status} fetching ${url}`);
  return resp.json();
}

// ---------------------------------------------------------------------------
// GTFS Static Data helpers
// ---------------------------------------------------------------------------

function ensureGtfs() {
  if (!fs.existsSync(path.join(GTFS_DIR, 'stops.txt'))) {
    console.log(`GTFS static data not found at ${GTFS_DIR}`);
    console.log('Run: node scripts/mta.mjs refresh-gtfs');
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
      if (ch === '"') { if (line[i + 1] === '"') { current += '"'; i++; } else inQuotes = false; }
      else current += ch;
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
    const nameMatch = s.name.toLowerCase().includes(q);
    const aliasMatch = s.aliases.some(a => a.includes(q) || q.includes(a));
    if (nameMatch || aliasMatch) {
      if (lineFilter && !s.lines.includes(lineFilter)) continue;
      const key = `${s.id}_${s.name}`;
      if (seen.has(key)) continue;
      seen.add(key);
      // Rank: exact alias > alias contains > name contains
      let rank = 3;
      if (s.aliases.some(a => a === q)) rank = 0;
      else if (s.name.toLowerCase() === q) rank = 0;
      else if (aliasMatch) rank = 1;
      else rank = 2;
      results.push({ ...s, rank });
    }
  }

  // 2. Search GTFS stops (parent stations only — location_type 1 or no suffix)
  if (ensureGtfs()) {
    const stops = loadStops();
    for (const s of Object.values(stops)) {
      // Only parent stations (location_type === '1') or stops without N/S suffix
      if (s.location_type !== '1' && s.location_type !== '') continue;
      const nameMatch = (s.stop_name || '').toLowerCase().includes(q);
      if (!nameMatch) continue;

      // Extract parent ID
      const pid = s.stop_id;
      const key = `gtfs_${pid}`;
      if (seen.has(key)) continue;
      seen.add(key);
      results.push({
        id: pid,
        name: s.stop_name,
        lines: [],
        aliases: [],
        rank: 4,
        gtfs: true,
      });
    }
  }

  results.sort((a, b) => a.rank - b.rank || a.name.localeCompare(b.name));
  return results;
}

// Find all GTFS stop IDs that belong to a parent station
function getStopIdsForStation(stationId) {
  if (!ensureGtfs()) return [stationId + 'N', stationId + 'S'];
  const stops = loadStops();
  const ids = [];
  for (const [sid, s] of Object.entries(stops)) {
    if (sid === stationId || s.parent_station === stationId || sid.startsWith(stationId)) {
      ids.push(sid);
    }
  }
  return ids.length ? ids : [stationId + 'N', stationId + 'S'];
}

// Determine which feeds to fetch for a station's lines
function getFeedsForStation(station) {
  const feeds = new Set();
  if (station.lines && station.lines.length > 0) {
    for (const line of station.lines) {
      const feed = FEED_MAP[line];
      if (feed) feeds.add(feed);
    }
  }
  if (feeds.size === 0) {
    // Unknown lines — fetch all feeds
    return ALL_FEEDS;
  }
  return [...feeds];
}

// Get direction label from stop ID suffix or NYCT extension
function getDirectionLabel(stopId, nyctDirection) {
  if (nyctDirection === 1) return 'Uptown & The Bronx';
  if (nyctDirection === 3) return 'Downtown & Brooklyn';
  if (typeof stopId === 'string') {
    if (stopId.endsWith('N')) return 'Uptown & The Bronx';
    if (stopId.endsWith('S')) return 'Downtown & Brooklyn';
  }
  return '';
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

  execFileSync('unzip', ['-o', tmpZip, '-d', GTFS_DIR], { stdio: 'pipe' });
  fs.unlinkSync(tmpZip);

  const files = fs.readdirSync(GTFS_DIR).filter(f => f.endsWith('.txt')).sort();
  console.log(`Extracted ${files.length} files:`);
  for (const f of files) console.log(`  ${f}`);
  console.log('GTFS data refreshed successfully.');
}

// ---- Subway Arrivals ----

async function cmdArrivals(opts) {
  let stationId = opts.stop;
  const stationName = opts.station;
  const stopSearch = opts['stop-search'];
  const lineFilter = opts.line;

  // Resolve station by name search
  if (stationName || stopSearch) {
    const query = stationName || stopSearch;
    const matches = searchStation(query, lineFilter);
    if (!matches.length) {
      console.log(`No stations found matching '${query}'.`);
      console.log("Try 'stops --search <name>' to find stations.");
      return;
    }
    if (matches.length > 1) {
      console.log(`Found ${matches.length} stations matching '${query}':`);
      for (const s of matches.slice(0, 8)) {
        const lineStr = s.lines?.length ? ` (${s.lines.join(', ')})` : '';
        console.log(`  ${s.id} — ${s.name}${lineStr}`);
      }
      console.log(`\nUsing best match: ${matches[0].name}\n`);
    }
    stationId = matches[0].id;
  }

  if (!stationId) {
    console.log('Provide --station, --stop-search, or --stop');
    return;
  }

  // Determine if this is a directional stop ID (ends with N or S)
  const isDirectional = /^[A-Z0-9]+[NS]$/.test(stationId);
  const parentId = isDirectional ? stationId.slice(0, -1) : stationId;

  // Get stop IDs to match against
  const targetStopIds = isDirectional ? [stationId] : getStopIdsForStation(parentId);
  const targetSet = new Set(targetStopIds);

  // Determine station info for display
  let stationLabel = stationId;
  const matchedStation = STATIONS.find(s => s.id === parentId);
  if (matchedStation) {
    stationLabel = matchedStation.name;
  } else if (ensureGtfs()) {
    const stops = loadStops();
    const stopInfo = stops[parentId] || stops[stationId];
    if (stopInfo) stationLabel = stopInfo.stop_name;
  }

  // Determine which feeds to fetch
  let feedsToFetch;
  if (lineFilter && FEED_MAP[lineFilter]) {
    feedsToFetch = [FEED_MAP[lineFilter]];
  } else if (matchedStation) {
    feedsToFetch = getFeedsForStation(matchedStation);
  } else {
    feedsToFetch = ALL_FEEDS;
  }

  console.log(`\n=== Subway Arrivals at: ${stationLabel} (${stationId}) ===\n`);

  // Fetch all relevant feeds in parallel
  const feedResults = await Promise.allSettled(
    feedsToFetch.map(f => parseSubwayFeed(f))
  );

  const now = localNow();
  const arrivals = [];

  for (const result of feedResults) {
    if (result.status !== 'fulfilled') continue;
    const feed = result.value;

    for (const entity of feed.entity || []) {
      const tu = entity.tripUpdate;
      if (!tu) continue;

      const routeId = tu.trip?.routeId || '';
      if (lineFilter && routeId !== lineFilter) continue;

      // Get NYCT extension data
      const nyctTrip = tu.trip?.['.transit_realtime.nyctTripDescriptor'] || tu.trip?.['.nyctTripDescriptor'] || {};
      const trainId = nyctTrip.trainId || '';
      const direction = nyctTrip.direction || null;

      for (const stu of tu.stopTimeUpdate || []) {
        const stopId = stu.stopId || '';
        if (!targetSet.has(stopId)) continue;

        let arrivalTime = null;
        if (stu.arrival?.time) {
          arrivalTime = toLocalDate(Number(stu.arrival.time));
        } else if (stu.departure?.time) {
          arrivalTime = toLocalDate(Number(stu.departure.time));
        }

        if (!arrivalTime) continue;

        const minsAway = (arrivalTime.getTime() - now.getTime()) / 60000;
        if (minsAway < -2) continue;

        // Track info from NYCT extension
        const nyctStop = stu['.transit_realtime.nyctStopTimeUpdate'] || stu['.nyctStopTimeUpdate'] || {};
        const scheduledTrack = nyctStop.scheduledTrack || '';
        const actualTrack = nyctStop.actualTrack || '';

        const dirLabel = getDirectionLabel(stopId, direction);
        const line = SUBWAY_LINES[routeId];
        const lineName = line ? line.name : routeId;

        arrivals.push({
          route: routeId,
          lineName,
          color: line?.color || '',
          direction: dirLabel,
          arrival: fmtTimeHM(arrivalTime),
          minsAway: Math.round(minsAway),
          trainId,
          scheduledTrack,
          actualTrack,
          stopId,
        });
      }
    }
  }

  if (!arrivals.length) {
    console.log('No upcoming subway arrivals found.');
    console.log('This may be due to reduced service (late night/weekend) or a temporary feed issue.');
    return;
  }

  arrivals.sort((a, b) => a.minsAway - b.minsAway);

  for (const a of arrivals.slice(0, 20)) {
    const eta = a.minsAway <= 0 ? 'Approaching' : a.minsAway === 1 ? '1 min' : `${a.minsAway} min`;
    let trackStr = '';
    if (a.actualTrack && a.actualTrack !== a.scheduledTrack) {
      trackStr = ` [Track ${a.actualTrack}, scheduled ${a.scheduledTrack}]`;
    } else if (a.actualTrack) {
      trackStr = ` [Track ${a.actualTrack}]`;
    }
    const dirStr = a.direction ? ` — ${a.direction}` : '';

    console.log(`  ${a.lineName}${dirStr}`);
    console.log(`     ${a.arrival} (${eta})${trackStr}`);
    if (a.trainId) console.log(`     Train ${a.trainId}`);
    console.log();
  }
}

// ---- Subway Vehicles ----

async function cmdVehicles(opts) {
  const lineFilter = opts.line;
  if (!lineFilter) {
    console.log('Provide --line with a subway line (e.g., 1, A, L)');
    return;
  }

  const feedName = FEED_MAP[lineFilter];
  if (!feedName) {
    console.log(`Unknown subway line: ${lineFilter}`);
    console.log('Valid lines: 1-7, A, C, E, B, D, F, M, G, J, Z, L, N, Q, R, W, GS, FS, H, SI');
    return;
  }

  const line = SUBWAY_LINES[lineFilter];
  console.log(`\nFetching ${line?.name || lineFilter} positions...`);

  const feed = await parseSubwayFeed(feedName);
  const vehicles = [];
  const stops = ensureGtfs() ? loadStops() : {};

  for (const entity of feed.entity || []) {
    const v = entity.vehicle;
    if (!v) continue;

    const routeId = v.trip?.routeId || '';
    if (routeId !== lineFilter) continue;

    const nyctTrip = v.trip?.['.transit_realtime.nyctTripDescriptor'] || v.trip?.['.nyctTripDescriptor'] || {};
    const trainId = nyctTrip.trainId || '';
    const direction = nyctTrip.direction || null;
    const stopId = v.stopId || '';
    const status = v.currentStatus || 0; // 0=INCOMING_AT, 1=STOPPED_AT, 2=IN_TRANSIT_TO
    const ts = v.timestamp;

    const dirLabel = getDirectionLabel(stopId, direction);
    const stopName = stops[stopId]?.stop_name || stopId;
    const statusLabels = { 0: 'Approaching', 1: 'Stopped at', 2: 'In transit to' };
    const statusStr = statusLabels[status] || 'En route to';

    let timeStr = '';
    if (ts) {
      try { timeStr = fmtTime(toLocalDate(Number(ts))); } catch { timeStr = String(ts); }
    }

    vehicles.push({ trainId, direction: dirLabel, stopName, status: statusStr, time: timeStr });
  }

  if (!vehicles.length) {
    console.log(`No active trains found on ${line?.name || lineFilter}.`);
    return;
  }

  console.log(`\n=== ${line?.name || lineFilter} Positions (${vehicles.length} active) ===\n`);

  for (const v of vehicles) {
    const dirStr = v.direction ? ` — ${v.direction}` : '';
    console.log(`  Train ${v.trainId || '?'}${dirStr}`);
    console.log(`     ${v.status} ${v.stopName}`);
    if (v.time) console.log(`     Last update: ${v.time}`);
    console.log();
  }
}

// ---- Bus Arrivals (SIRI StopMonitoring) ----

async function cmdBusArrivals(opts) {
  if (!requireBusKey()) return;

  let stopId = opts.stop;
  const stopSearch = opts['stop-search'];
  const routeFilter = opts.route;

  if (stopSearch) {
    // Use OneBusAway search — search nearby or by name
    // For now, try the stop search endpoint
    console.log(`Searching bus stops for '${stopSearch}'...`);
    // OBA doesn't have a text search endpoint, so we'll search GTFS or provide guidance
    console.log('Bus stop search requires a stop ID (e.g., MTA_308209).');
    console.log('Find stop IDs using: bus-stops --near LAT,LON');
    console.log('Or check the MTA BusTime website: https://bustime.mta.info/');
    return;
  }

  if (!stopId) {
    console.log('Provide --stop with a bus stop ID (e.g., MTA_308209)');
    console.log('Find stop IDs using: bus-stops --near LAT,LON');
    return;
  }

  let url = `${BUS_SIRI_BASE}/stop-monitoring.json?key=${encodeURIComponent(MTA_BUS_API_KEY)}&MonitoringRef=${encodeURIComponent(stopId)}`;
  if (routeFilter) {
    url += `&LineRef=MTA%20NYCT_${encodeURIComponent(routeFilter)}`;
  }

  const data = await fetchJSON(url);
  const delivery = data?.Siri?.ServiceDelivery?.StopMonitoringDelivery;
  if (!delivery || !delivery.length) {
    console.log('No bus monitoring data available for this stop.');
    return;
  }

  const visits = delivery[0]?.MonitoredStopVisit;
  if (!visits || !visits.length) {
    const filterMsg = routeFilter ? ` for route ${routeFilter}` : '';
    console.log(`No upcoming bus arrivals${filterMsg} at stop ${stopId}.`);
    return;
  }

  // Get stop name from first result
  const firstVj = visits[0]?.MonitoredVehicleJourney;
  const stopLabel = firstVj?.MonitoredCall?.StopPointName?.[0]?.value || stopId;
  console.log(`\n=== Bus Arrivals at: ${stopLabel} (${stopId}) ===\n`);

  for (const visit of visits.slice(0, 15)) {
    const vj = visit?.MonitoredVehicleJourney;
    if (!vj) continue;

    const routeRef = vj.LineRef || '';
    const route = routeRef.replace(/^MTA NYCT_|^MTABC_/, '');
    const dest = vj.DestinationName?.[0]?.value || '';
    const direction = vj.DirectionRef === '0' ? '' : '';

    const mc = vj.MonitoredCall || {};
    const distances = mc.Extensions?.Distances || {};
    const stopsAway = distances.StopsFromCall ?? '';
    const distMiles = distances.DistanceFromCall ? (distances.DistanceFromCall / 1609.34).toFixed(1) : '';

    // Expected arrival time
    let etaStr = '';
    const expectedArrival = mc.ExpectedArrivalTime || mc.ExpectedDepartureTime;
    if (expectedArrival) {
      const arrTime = new Date(expectedArrival);
      const minsAway = Math.round((arrTime.getTime() - Date.now()) / 60000);
      if (minsAway <= 0) etaStr = 'Approaching';
      else if (minsAway === 1) etaStr = '1 min';
      else etaStr = `${minsAway} min`;
    }

    const presentable = mc.ArrivalProximityText || '';
    if (!etaStr && presentable) etaStr = presentable;

    const vehicleRef = vj.VehicleRef || '';

    console.log(`  Route ${route} -> ${dest}`);
    let detailLine = `     `;
    if (etaStr) detailLine += `${etaStr}`;
    if (stopsAway !== '') detailLine += ` (${stopsAway} stops away)`;
    if (distMiles) detailLine += ` — ${distMiles} mi`;
    console.log(detailLine);
    if (vehicleRef) console.log(`     Vehicle ${vehicleRef}`);
    console.log();
  }
}

// ---- Bus Vehicles (SIRI VehicleMonitoring) ----

async function cmdBusVehicles(opts) {
  if (!requireBusKey()) return;

  const route = opts.route;
  if (!route) {
    console.log('Provide --route with a bus route (e.g., M1, B52, Bx12)');
    return;
  }

  const url = `${BUS_SIRI_BASE}/vehicle-monitoring.json?key=${encodeURIComponent(MTA_BUS_API_KEY)}&LineRef=MTA%20NYCT_${encodeURIComponent(route)}&VehicleMonitoringDetailLevel=calls`;
  const data = await fetchJSON(url);

  const delivery = data?.Siri?.ServiceDelivery?.VehicleMonitoringDelivery;
  if (!delivery || !delivery.length) {
    console.log(`No vehicle data available for route ${route}.`);
    return;
  }

  const activities = delivery[0]?.VehicleActivity;
  if (!activities || !activities.length) {
    console.log(`No active buses on route ${route}.`);
    return;
  }

  console.log(`\n=== Route ${route} Bus Positions (${activities.length} active) ===\n`);

  for (const activity of activities) {
    const vj = activity?.MonitoredVehicleJourney;
    if (!vj) continue;

    const dest = vj.DestinationName?.[0]?.value || '';
    const vehicleRef = vj.VehicleRef || '';
    const lat = vj.VehicleLocation?.Latitude;
    const lon = vj.VehicleLocation?.Longitude;
    const bearing = vj.Bearing;
    const progressStatus = vj.ProgressStatus?.[0] || '';

    const mc = vj.MonitoredCall || {};
    const nextStop = mc.StopPointName?.[0]?.value || '';

    let statusStr = '';
    if (progressStatus === 'layover') statusStr = '(layover)';
    else if (progressStatus === 'prevTrip') statusStr = '(prev trip)';

    console.log(`  Vehicle ${vehicleRef} -> ${dest} ${statusStr}`);
    if (nextStop) console.log(`     Next stop: ${nextStop}`);
    if (lat && lon) console.log(`     Position: (${lat}, ${lon}) bearing ${bearing || '?'}`);
    console.log();
  }
}

// ---- Alerts ----

async function cmdAlerts(opts) {
  const lineFilter = opts.line;
  const subwayOnly = opts.subway;
  const busOnly = opts.bus;

  let feedUrl;
  if (subwayOnly) {
    feedUrl = alertsFeedUrl('subway-alerts');
  } else if (busOnly) {
    feedUrl = alertsFeedUrl('bus-alerts');
  } else {
    feedUrl = alertsFeedUrl('all-alerts');
  }

  const feed = await parseAlertsFeed(feedUrl);

  if (!feed.entity || feed.entity.length === 0) {
    const scope = subwayOnly ? 'subway' : busOnly ? 'bus' : '';
    console.log(`No active ${scope} service alerts.`);
    return;
  }

  // Filter by line if specified
  let entities = feed.entity;
  if (lineFilter) {
    entities = entities.filter(e => {
      const alert = e.alert;
      if (!alert?.informedEntity) return false;
      return alert.informedEntity.some(ie =>
        ie.routeId === lineFilter ||
        ie.routeId === `MTASBWY_${lineFilter}`
      );
    });
  }

  if (!entities.length) {
    console.log(`No active alerts for ${lineFilter || 'this filter'}.`);
    return;
  }

  const scope = subwayOnly ? 'Subway' : busOnly ? 'Bus' : 'MTA';
  console.log(`\n=== ${scope} Service Alerts (${entities.length} active) ===\n`);

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
        const rid = ie.routeId;
        if (rid) {
          const clean = rid.replace(/^MTASBWY_|^MTA NYCT_|^MTABC_/, '');
          if (!affected.includes(clean)) affected.push(clean);
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

    // Determine severity icon from effect
    const effect = alert.effect || 0;
    let icon = '';
    if (effect === 1) icon = '  '; // NO_SERVICE
    else if (effect === 2 || effect === 3) icon = '  '; // REDUCED_SERVICE / SIGNIFICANT_DELAYS
    else icon = '  ';

    console.log(`${icon} ${header}`);
    if (affected.length) console.log(`   Routes: ${affected.join(', ')}`);
    if (periods.length) console.log(`   Period: ${periods[0]}${periods.length > 1 ? ` (+${periods.length - 1} more)` : ''}`);
    if (desc) {
      if (desc.length > 300) desc = desc.slice(0, 300) + '...';
      console.log(`   ${desc}`);
    }
    console.log();
  }
}

// ---- Routes ----

function cmdRoutes() {
  console.log('\n=== NYC Subway Lines ===\n');
  const order = ['1','2','3','4','5','6','7','A','C','E','B','D','F','M','G','J','Z','L','N','Q','R','W','GS','FS','H','SI'];
  for (const code of order) {
    const line = SUBWAY_LINES[code];
    if (!line) continue;
    console.log(`  ${code.padEnd(4)} | ${line.color.padEnd(12)} | ${line.route}`);
    console.log(`  ${''.padEnd(4)} | ${''.padEnd(12)} | ${line.terminals.join(' <-> ')}`);
  }
}

// ---- Bus Routes ----

async function cmdBusRoutes() {
  if (!requireBusKey()) return;

  const url = `${BUS_OBA_BASE}/routes-for-agency/MTA%20NYCT.json?key=${encodeURIComponent(MTA_BUS_API_KEY)}`;
  const data = await fetchJSON(url);

  const routes = data?.data?.list;
  if (!routes || !routes.length) {
    console.log('No bus routes found.');
    return;
  }

  console.log(`\n=== MTA Bus Routes (${routes.length}) ===\n`);

  // Sort by route short name
  routes.sort((a, b) => {
    const an = a.shortName || a.id || '';
    const bn = b.shortName || b.id || '';
    return an.localeCompare(bn, undefined, { numeric: true });
  });

  for (const r of routes) {
    const short = (r.shortName || r.id || '?').padEnd(8);
    const longName = r.longName || '';
    console.log(`  ${short} | ${longName}`);
  }
}

// ---- Stops ----

function cmdStops(opts) {
  if (opts.search) {
    const query = opts.search.toLowerCase();

    // Search embedded stations
    const results = searchStation(query, null);
    if (!results.length) {
      console.log(`No subway stations found matching '${opts.search}'.`);
      return;
    }

    console.log(`\n=== Subway Stations matching '${opts.search}' (${results.length} found) ===\n`);
    for (const s of results.slice(0, 25)) {
      const lineStr = s.lines?.length ? ` (${s.lines.join(', ')})` : '';
      console.log(`  ${s.name}${lineStr}`);
      console.log(`     ID: ${s.id}`);
      console.log();
    }
  } else if (opts.near) {
    if (!ensureGtfs()) return;
    const parts = opts.near.split(',');
    if (parts.length !== 2) { console.log('Invalid format. Use: --near LAT,LON'); return; }
    const [lat, lon] = parts.map(Number);
    if (isNaN(lat) || isNaN(lon)) { console.log('Invalid format. Use: --near LAT,LON'); return; }
    const radius = opts.radius ? parseFloat(opts.radius) : 0.5;

    const stops = loadStops();
    const nearby = [];
    for (const s of Object.values(stops)) {
      // Only parent stations
      if (s.location_type !== '1') continue;
      const slat = parseFloat(s.stop_lat), slon = parseFloat(s.stop_lon);
      if (isNaN(slat) || isNaN(slon)) continue;
      const dist = haversine(lat, lon, slat, slon);
      if (dist <= radius) nearby.push([dist, s]);
    }
    nearby.sort((a, b) => a[0] - b[0]);

    if (!nearby.length) { console.log(`No subway stations within ${radius} miles of (${lat}, ${lon}).`); return; }
    console.log(`\n=== Nearby Subway Stations (${nearby.length} within ${radius} mi) ===\n`);
    for (const [dist, s] of nearby.slice(0, 20)) {
      console.log(`  ${s.stop_name} — ${dist.toFixed(2)} mi`);
      console.log(`     ID: ${s.stop_id}`);
      console.log();
    }
  } else {
    console.log('Provide --search <name> or --near LAT,LON');
  }
}

// ---- Bus Stops ----

async function cmdBusStops(opts) {
  if (!requireBusKey()) return;

  if (opts.near) {
    const parts = opts.near.split(',');
    if (parts.length !== 2) { console.log('Invalid format. Use: --near LAT,LON'); return; }
    const [lat, lon] = parts.map(Number);
    if (isNaN(lat) || isNaN(lon)) { console.log('Invalid format. Use: --near LAT,LON'); return; }

    const url = `${BUS_OBA_BASE}/stops-for-location.json?lat=${lat}&lon=${lon}&latSpan=0.005&lonSpan=0.005&key=${encodeURIComponent(MTA_BUS_API_KEY)}`;
    const data = await fetchJSON(url);

    const stopsList = data?.data?.list;
    if (!stopsList || !stopsList.length) {
      console.log(`No bus stops found near (${lat}, ${lon}).`);
      return;
    }

    console.log(`\n=== Nearby Bus Stops (${stopsList.length} found) ===\n`);
    for (const s of stopsList.slice(0, 20)) {
      const dist = haversine(lat, lon, s.lat, s.lon);
      const routes = s.routeIds?.map(r => r.replace(/^MTA NYCT_|^MTABC_/, '')).join(', ') || '';
      console.log(`  ${s.name} — ${dist.toFixed(2)} mi`);
      console.log(`     ID: ${s.id}  |  Code: ${s.code || '?'}`);
      if (routes) console.log(`     Routes: ${routes}`);
      console.log();
    }
  } else if (opts.route) {
    const route = opts.route;
    const url = `${BUS_OBA_BASE}/stops-for-route/MTA%20NYCT_${encodeURIComponent(route)}.json?key=${encodeURIComponent(MTA_BUS_API_KEY)}&includePolylines=false&version=2`;

    let data;
    try {
      data = await fetchJSON(url);
    } catch {
      // Try MTABC agency prefix
      const url2 = `${BUS_OBA_BASE}/stops-for-route/MTABC_${encodeURIComponent(route)}.json?key=${encodeURIComponent(MTA_BUS_API_KEY)}&includePolylines=false&version=2`;
      data = await fetchJSON(url2);
    }

    const stops = data?.data?.references?.stops || data?.data?.list;
    if (!stops || !stops.length) {
      console.log(`No stops found for route ${route}.`);
      return;
    }

    console.log(`\n=== Stops on Route ${route} (${stops.length} stops) ===\n`);
    for (const s of stops) {
      console.log(`  ${s.name}`);
      console.log(`     ID: ${s.id}  |  Direction: ${s.direction || '?'}`);
    }
  } else {
    console.log('Provide --near LAT,LON or --route ROUTE_ID');
  }
}

// ---- Route Info (subway line stops) ----

async function cmdRouteInfo(opts) {
  const lineFilter = opts.line;
  if (!lineFilter) {
    console.log('Provide --line with a subway line (e.g., A, 1, L)');
    return;
  }

  const line = SUBWAY_LINES[lineFilter];
  if (!line) {
    console.log(`Unknown subway line: ${lineFilter}`);
    return;
  }

  console.log(`\n=== ${line.name} — ${line.route} ===`);
  console.log(`    Color: ${line.color}  |  Terminals: ${line.terminals.join(' <-> ')}`);
  console.log();

  if (!ensureGtfs()) return;

  const routes = loadRoutes();
  const trips = loadTrips();
  const stops = loadStops();

  // Find route ID in GTFS
  const routeId = Object.keys(routes).find(k =>
    routes[k].route_short_name === lineFilter || routes[k].route_id === lineFilter || k === lineFilter
  );

  if (!routeId) {
    // Fall back: list embedded station data for this line
    const lineStations = STATIONS.filter(s => s.lines.includes(lineFilter));
    if (lineStations.length) {
      console.log('Stations (from embedded data):');
      for (const s of lineStations) {
        console.log(`  ${s.name} (ID: ${s.id})`);
      }
    } else {
      console.log('No GTFS route data found. Try running refresh-gtfs.');
    }
    return;
  }

  const routeTrips = Object.values(trips).filter(t => t.route_id === routeId);
  if (!routeTrips.length) {
    console.log('No trips found for this line in GTFS data.');
    return;
  }

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
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === '-h') {
    console.log(`NYC MTA Transit — OpenClaw Skill

Commands:
  arrivals        Subway arrivals (--station NAME | --stop-search NAME | --stop ID) [--line LINE]
  bus-arrivals    Bus predictions (--stop ID) [--route ROUTE]
  vehicles        Subway train positions (--line LINE)
  bus-vehicles    Bus positions (--route ROUTE)
  alerts          Service alerts [--subway] [--bus] [--line LINE]
  routes          List all subway lines
  bus-routes      List bus routes (requires API key)
  stops           Search subway stops (--search NAME | --near LAT,LON)
  bus-stops       Search bus stops (--near LAT,LON | --route ROUTE)
  route-info      Subway line details (--line LINE)
  refresh-gtfs    Download/refresh GTFS static data

Subway Lines: 1-7, A, C, E, B, D, F, M, G, J, Z, L, N, Q, R, W, S (shuttles), SIR

Environment: MTA_BUS_API_KEY (free, for bus commands only — subway works without any key)`);
    return;
  }

  const rest = args.slice(1);

  const optDefs = {
    stop: { type: 'string' },
    'stop-search': { type: 'string' },
    station: { type: 'string' },
    line: { type: 'string' },
    route: { type: 'string' },
    search: { type: 'string' },
    near: { type: 'string' },
    radius: { type: 'string' },
    subway: { type: 'boolean' },
    bus: { type: 'boolean' },
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
    'bus-stops': () => cmdBusStops(opts),
    'route-info': () => cmdRouteInfo(opts),
  };

  if (handlers[command]) {
    Promise.resolve(handlers[command]()).catch(err => {
      if (err.name === 'TimeoutError' || err.message?.includes('timeout')) {
        console.error('Request timed out. MTA feed may be slow or unreachable. Try again in a moment.');
      } else if (err.code === 'ENOTFOUND' || err.code === 'ECONNREFUSED') {
        console.error('Network error: Could not reach MTA API. Check your internet connection.');
      } else {
        console.error(`Error: ${err.message}`);
      }
      process.exit(1);
    });
  } else {
    console.error(`Unknown command: ${command}`);
    console.error("Run 'node scripts/mta.mjs --help' for available commands.");
    process.exit(1);
  }
}

main();
