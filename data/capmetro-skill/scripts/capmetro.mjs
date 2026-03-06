#!/usr/bin/env node
/**
 * CapMetro Austin Transit - OpenClaw Skill (Node.js port)
 * Real-time vehicle positions, arrivals, alerts, and route info.
 * All data from Texas Open Data Portal (no API key required).
 *
 * SECURITY MANIFEST
 *   Environment variables: None
 *   External endpoints:    data.texas.gov (read-only GET, open access, no auth)
 *   Local files written:   ~/.capmetro/gtfs/ (GTFS static data cache)
 *   Local files read:      ~/.capmetro/gtfs/*.txt (GTFS CSV files)
 *   User input handling:   Used for local filtering only, never interpolated into
 *                          URLs or shell commands
 */

import { parseArgs } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';

// ---------------------------------------------------------------------------
// Feed URLs (Texas Open Data Portal — open access, no key)
// ---------------------------------------------------------------------------
const FEEDS = {
  vehicle_positions_json: 'https://data.texas.gov/download/cuc7-ywmd/text%2Fplain',
  vehicle_positions_pb: 'https://data.texas.gov/download/eiei-9rpf/application%2Foctet-stream',
  trip_updates_pb: 'https://data.texas.gov/download/rmk2-acnw/application%2Foctet-stream',
  service_alerts_pb: 'https://data.texas.gov/download/nusn-7fcn/application%2Foctet-stream',
  gtfs_static: 'https://data.texas.gov/download/r4v4-vz24/application%2Fx-zip-compressed',
};

const GTFS_DIR = path.join(os.homedir(), '.capmetro', 'gtfs');

// CST/CDT: US Central Time — DST starts 2nd Sunday of March, ends 1st Sunday of November
function localTzOffsetHours() {
  const now = new Date();
  const year = now.getUTCFullYear();
  // 2nd Sunday of March: find first Sunday in March, add 7 days
  const mar1 = new Date(Date.UTC(year, 2, 1));
  const firstSunMar = (7 - mar1.getUTCDay()) % 7 + 1;
  const dstStart = Date.UTC(year, 2, firstSunMar + 7, 8); // 2:00 AM CST = 08:00 UTC
  // 1st Sunday of November
  const nov1 = new Date(Date.UTC(year, 10, 1));
  const firstSunNov = (7 - nov1.getUTCDay()) % 7 + 1;
  const dstEnd = Date.UTC(year, 10, firstSunNov, 7); // 2:00 AM CDT = 07:00 UTC
  const ts = now.getTime();
  return (ts >= dstStart && ts < dstEnd) ? -5 : -6;
}

function toLocalDate(ts) {
  // ts can be a unix timestamp (seconds) or Date
  const d = typeof ts === 'number' ? new Date(ts * 1000) : ts;
  // Shift UTC time by offset to get "local" time we can format
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
  return `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')} ${ampm}`;
}

function fmtTimeHM(d) {
  let h = d.getUTCHours(), m = d.getUTCMinutes();
  const ampm = h >= 12 ? 'PM' : 'AM';
  if (h > 12) h -= 12; else if (h === 0) h = 12;
  return `${h}:${String(m).padStart(2,'0')} ${ampm}`;
}

function fmtDateTimeShort(d) {
  const mo = d.getUTCMonth() + 1, day = d.getUTCDate();
  let h = d.getUTCHours(), m = d.getUTCMinutes();
  const ampm = h >= 12 ? 'PM' : 'AM';
  if (h > 12) h -= 12; else if (h === 0) h = 12;
  return `${String(mo).padStart(2,'0')}/${String(day).padStart(2,'0')} ${h}:${String(m).padStart(2,'0')}${ampm}`;
}

// ---------------------------------------------------------------------------
// GTFS-RT Protobuf helpers
// ---------------------------------------------------------------------------

let _protobufRoot = null;

async function getProtobufRoot() {
  if (_protobufRoot) return _protobufRoot;
  let protobuf;
  try {
    protobuf = (await import('protobufjs')).default;
  } catch {
    console.error('ERROR: protobufjs not installed.');
    console.error('Run: npm install protobufjs (in the skill directory)');
    process.exit(1);
  }

  // Load proto file from disk (next to this script)
  const protoPath = path.join(path.dirname(new URL(import.meta.url).pathname), 'gtfs-realtime.proto');
  _protobufRoot = await protobuf.load(protoPath);
  return _protobufRoot;
}

async function parsePb(url) {
  const root = await getProtobufRoot();
  const FeedMessage = root.lookupType('transit_realtime.FeedMessage');
  const resp = await fetch(url, { signal: AbortSignal.timeout(30000) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status} fetching ${url}`);
  const buf = Buffer.from(await resp.arrayBuffer());
  // Check if we got HTML instead of protobuf (redirect to login page)
  if (buf.length > 0 && buf[0] === 0x3c) {
    throw new Error('Feed returned HTML instead of protobuf — endpoint may require authentication or be temporarily unavailable');
  }
  return FeedMessage.decode(buf);
}

// ---------------------------------------------------------------------------
// GTFS Static data helpers
// ---------------------------------------------------------------------------

function ensureGtfs() {
  if (!fs.existsSync(path.join(GTFS_DIR, 'stops.txt'))) {
    console.log(`GTFS static data not found at ${GTFS_DIR}`);
    console.log('Run: node scripts/capmetro.mjs refresh-gtfs');
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
  // Strip BOM
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

function loadStops() {
  const rows = loadCsv('stops.txt');
  const m = {};
  for (const r of rows) m[r.stop_id] = r;
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

function getActiveServiceIds(dateStr) {
  // dateStr format: YYYYMMDD — check both calendar.txt and calendar_dates.txt
  const active = new Set();

  // calendar.txt: recurring service by day-of-week
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

  // calendar_dates.txt: exceptions (type 1 = added, type 2 = removed)
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
// Commands
// ---------------------------------------------------------------------------

async function cmdRefreshGtfs() {
  console.log(`Downloading GTFS static data to ${GTFS_DIR} ...`);
  fs.mkdirSync(GTFS_DIR, { recursive: true });

  const resp = await fetch(FEEDS.gtfs_static, { signal: AbortSignal.timeout(120000) });
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

async function cmdAlerts() {
  const feed = await parsePb(FEEDS.service_alerts_pb);
  const routes = ensureGtfs() ? loadRoutes() : {};

  if (!feed.entity || feed.entity.length === 0) {
    console.log('No active service alerts.');
    return;
  }

  console.log(`=== CapMetro Service Alerts (${feed.entity.length} active) ===\n`);
  for (const entity of feed.entity) {
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
          const rname = routes[rid]?.route_short_name || rid;
          affected.push(rname);
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

    console.log(`📢 ${header}`);
    if (affected.length) console.log(`   Routes: ${affected.join(', ')}`);
    if (periods.length) console.log(`   Period: ${periods.join('; ')}`);
    if (desc) {
      if (desc.length > 300) desc = desc.slice(0, 300) + '...';
      console.log(`   ${desc}`);
    }
    console.log();
  }
}

async function cmdVehicles(opts) {
  const routeFilter = opts.route;
  console.log('Fetching vehicle positions...');
  const resp = await fetch(FEEDS.vehicle_positions_json, { signal: AbortSignal.timeout(30000) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const data = await resp.json();

  const routes = ensureGtfs() ? loadRoutes() : {};
  const entities = data.entity || data;

  const vehicles = [];
  for (const entity of entities) {
    const v = entity.vehicle || entity;
    const trip = v.trip || {};
    const pos = v.position || {};
    const vid = v.vehicle?.id || '?';
    const rid = trip.routeId || trip.route_id || '';
    const lat = pos.latitude;
    const lon = pos.longitude;
    const ts = v.timestamp;

    if (routeFilter && rid !== routeFilter) continue;
    if (!rid) continue;

    const rname = routes[rid]?.route_short_name || rid;
    const rlong = routes[rid]?.route_long_name || '';

    let timeStr = '';
    if (ts) {
      try { timeStr = fmtTime(toLocalDate(parseInt(ts))); } catch { timeStr = String(ts); }
    }

    vehicles.push({ vid, route: rname, route_name: rlong, lat, lon, time: timeStr });
  }

  if (!vehicles.length) {
    const filterMsg = routeFilter ? ` on route ${routeFilter}` : '';
    console.log(`No active vehicles found${filterMsg}.`);
    return;
  }

  console.log(`\n=== Active CapMetro Vehicles (${vehicles.length}) ===\n`);
  const byRoute = {};
  for (const v of vehicles) (byRoute[v.route] ||= []).push(v);

  for (const route of Object.keys(byRoute).sort((a, b) => a.padStart(5, '0').localeCompare(b.padStart(5, '0')))) {
    const vlist = byRoute[route];
    console.log(`Route ${route} — ${vlist[0].route_name} (${vlist.length} vehicles)`);
    for (const v of vlist) {
      console.log(`  🚍 Vehicle ${v.vid}: (${Number(v.lat).toFixed(5)}, ${Number(v.lon).toFixed(5)}) @ ${v.time}`);
    }
    console.log();
  }
}

async function cmdArrivals(opts) {
  let stopId = opts.stop;
  const stopSearch = opts['stop-search'];
  const routeFilter = opts.route;
  const headsignFilter = opts.headsign?.toLowerCase();

  if (!ensureGtfs()) return;
  const stops = loadStops();
  const routes = loadRoutes();
  const trips = loadTrips();

  if (stopSearch) {
    const query = stopSearch.toLowerCase();
    const matches = Object.values(stops).filter(s => (s.stop_name || '').toLowerCase().includes(query));
    if (!matches.length) { console.log(`No stops found matching '${stopSearch}'.`); return; }

    // Prefer exact name match, then "Station" matches (rail), then alphabetical
    const rankStop = (s) => {
      const name = (s.stop_name || '').toLowerCase();
      if (name === query) return 0;                          // exact match
      if (name === query + ' station') return 1;             // "lakeline station"
      if (name.includes('station') && name.includes(query)) return 2; // station containing query
      return 3;                                               // other partial matches
    };
    matches.sort((a, b) => {
      const ra = rankStop(a), rb = rankStop(b);
      if (ra !== rb) return ra - rb;
      return a.stop_name.localeCompare(b.stop_name);
    });

    if (matches.length > 1) {
      console.log(`Found ${matches.length} stops matching '${stopSearch}':`);
      for (const s of matches.slice(0, 10)) console.log(`  ${s.stop_id.padStart(6)} — ${s.stop_name}`);
      console.log(`\nUsing best match: ${matches[0].stop_name}\n`);
    }
    stopId = matches[0].stop_id;
  }

  if (!stopId || !stops[stopId]) {
    console.log(stopId ? `Stop ID '${stopId}' not found in GTFS data.` : 'Provide --stop or --stop-search');
    console.log("Use 'stops --search <name>' to find stop IDs.");
    return;
  }

  const stop = stops[stopId];
  console.log(`\n=== Arrivals at: ${stop.stop_name} (ID: ${stopId}) ===\n`);

  const feed = await parsePb(FEEDS.trip_updates_pb);
  const rtArrivals = [];

  for (const entity of feed.entity || []) {
    const tu = entity.tripUpdate;
    if (!tu) continue;
    const tripId = tu.trip?.tripId || '';
    const routeId = tu.trip?.routeId || '';
    if (routeFilter && routeId !== routeFilter) continue;

    for (const stu of tu.stopTimeUpdate || []) {
      if (stu.stopId !== stopId) continue;

      let arrivalTime = null, delay = 0;
      if (stu.arrival?.time) {
        arrivalTime = toLocalDate(Number(stu.arrival.time));
        delay = stu.arrival.delay || 0;
      } else if (stu.departure?.time) {
        arrivalTime = toLocalDate(Number(stu.departure.time));
        delay = stu.departure.delay || 0;
      }

      if (arrivalTime) {
        const rname = routes[routeId]?.route_short_name || routeId;
        const tripInfo = trips[tripId] || {};
        const headsign = tripInfo.trip_headsign || routes[routeId]?.route_long_name || '';
        if (headsignFilter && !headsign.toLowerCase().includes(headsignFilter)) continue;

        const now = localNow();
        const minsAway = (arrivalTime.getTime() - now.getTime()) / 60000;
        if (minsAway < -5) continue;

        rtArrivals.push({
          route: rname, headsign,
          arrival: fmtTimeHM(arrivalTime),
          minsAway: Math.round(minsAway),
          delayMins: delay ? Math.round(delay / 60) : 0,
        });
      }
    }
  }

  if (rtArrivals.length) {
    rtArrivals.sort((a, b) => a.minsAway - b.minsAway);
    console.log('Real-time arrivals:');
    for (const a of rtArrivals.slice(0, 15)) {
      const delayStr = a.delayMins > 0 ? ` (+${a.delayMins}m late)` : '';
      const eta = a.minsAway <= 0 ? 'NOW' : a.minsAway === 1 ? '1 min' : `${a.minsAway} min`;
      console.log(`  🚌 Route ${a.route} → ${a.headsign}`);
      console.log(`     ${a.arrival} (${eta})${delayStr}`);
      console.log();
    }
  } else {
    // Get active service IDs for today
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

    // Try today first, fall back to tomorrow if no results
    const stopTimes = loadStopTimesForStop(stopId);

    function findUpcoming(serviceIds, minTime) {
      const results = [];
      const seen = new Set();
      for (const st of stopTimes) {
        const tripInfo = trips[st.trip_id] || {};
        const routeId = tripInfo.route_id || '';
        const serviceId = tripInfo.service_id || '';
        if (!serviceIds.has(serviceId)) continue;
        if (routeFilter && routeId !== routeFilter) continue;
        const arrTime = st.arrival_time || st.departure_time || '';
        if (arrTime <= minTime) continue;
        const rname = routes[routeId]?.route_short_name || routeId;
        const headsign = tripInfo.trip_headsign || '';
        if (headsignFilter && !headsign.toLowerCase().includes(headsignFilter)) continue;
        const dedup = `${rname}|${arrTime}|${headsign}`;
        if (seen.has(dedup)) continue;
        seen.add(dedup);
        results.push({ route: rname, headsign, time: arrTime });
      }
      results.sort((a, b) => a.time.localeCompare(b.time));
      return results;
    }

    let upcoming = findUpcoming(activeServices, currentTime);
    let dateLabel = 'today';

    if (!upcoming.length) {
      // Try tomorrow
      const tomorrow = new Date(now.getTime() + 86400000);
      const ty = String(tomorrow.getUTCFullYear());
      const tm = String(tomorrow.getUTCMonth() + 1).padStart(2, '0');
      const td = String(tomorrow.getUTCDate()).padStart(2, '0');
      const tomorrowServices = getActiveServiceIds(`${ty}${tm}${td}`);
      upcoming = findUpcoming(tomorrowServices, '00:00:00');
      dateLabel = 'tomorrow';
    }

    console.log(`No real-time data available. Showing scheduled times for ${dateLabel}:`);

    if (!upcoming.length) {
      console.log(`  No upcoming departures found for ${dateLabel}.`);
      return;
    }
    for (const u of upcoming.slice(0, 15)) {
      let timeStr = u.time;
      try {
        const [h, m] = u.time.split(':');
        let hr = parseInt(h);
        const ampm = hr >= 12 ? 'PM' : 'AM';
        if (hr > 12) hr -= 12; else if (hr === 0) hr = 12;
        timeStr = `${hr}:${m} ${ampm}`;
      } catch {}
      console.log(`  🚌 Route ${u.route} → ${u.headsign} at ${timeStr}`);
    }
  }
}

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

function cmdRoutes() {
  if (!ensureGtfs()) return;
  const routes = loadRoutes();
  const typeNames = { '0': 'Tram', '1': 'Subway', '2': 'Rail', '3': 'Bus', '4': 'Ferry' };

  console.log(`\n=== CapMetro Routes (${Object.keys(routes).length}) ===\n`);
  for (const rid of Object.keys(routes).sort((a, b) => a.padStart(5, '0').localeCompare(b.padStart(5, '0')))) {
    const r = routes[rid];
    const rtype = typeNames[r.route_type || '3'] || 'Other';
    const short = r.route_short_name || rid;
    const longName = r.route_long_name || '';
    console.log(`  ${short.padStart(6)} | ${rtype.padEnd(5)} | ${longName}`);
  }
}

function cmdRouteInfo(opts) {
  if (!ensureGtfs()) return;
  let routeId = opts.route;
  const routes = loadRoutes();
  const trips = loadTrips();
  const stops = loadStops();

  if (!routes[routeId]) {
    // Try matching by short name
    const match = Object.entries(routes).find(([, r]) => r.route_short_name === routeId);
    if (match) routeId = match[0];
    else { console.log(`Route '${opts.route}' not found.`); return; }
  }

  const r = routes[routeId];
  console.log(`\n=== Route ${r.route_short_name || routeId} — ${r.route_long_name || ''} ===`);
  console.log(`    Type: ${r.route_type || '?'}  |  ID: ${routeId}`);
  if (r.route_url) console.log(`    URL: ${r.route_url}`);
  console.log();

  const routeTrips = Object.values(trips).filter(t => t.route_id === routeId);
  if (!routeTrips.length) { console.log('No trips found for this route.'); return; }

  const dir0 = routeTrips.filter(t => t.direction_id === '0');
  const sampleTrip = (dir0.length ? dir0 : routeTrips)[0];
  const stopTimes = loadStopTimesForTrip(sampleTrip.trip_id);

  if (stopTimes.length) {
    console.log(`Stops (direction: ${sampleTrip.trip_headsign || ''}):`);
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
    console.log(`CapMetro Austin Transit — OpenClaw Skill

Commands:
  alerts         Show current service alerts
  vehicles       Show real-time vehicle positions [--route ID]
  arrivals       Next arrivals at a stop (--stop ID | --stop-search NAME) [--route ID] [--headsign TEXT]
  stops          Search for stops (--search NAME | --near LAT,LON [--radius MI])
  routes         List all routes
  route-info     Get route details and stops (--route ID)
  refresh-gtfs   Download/refresh GTFS static data`);
    return;
  }

  const rest = args.slice(1);

  const optDefs = {
    route: { type: 'string' },
    stop: { type: 'string' },
    'stop-search': { type: 'string' },
    headsign: { type: 'string' },
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
    alerts: () => cmdAlerts(),
    vehicles: () => cmdVehicles(opts),
    arrivals: () => cmdArrivals(opts),
    stops: () => cmdStops(opts),
    routes: () => cmdRoutes(),
    'route-info': () => cmdRouteInfo(opts),
  };

  if (handlers[command]) {
    Promise.resolve(handlers[command]()).catch(err => {
      console.error(`Error: ${err.message}`);
      process.exit(1);
    });
  } else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

main();
