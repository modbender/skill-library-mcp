#!/usr/bin/env node
/**
 * TfL London Transit — OpenClaw Skill
 * Real-time Tube arrivals, bus predictions, line status, disruptions,
 * journey planning, and route info for the London Underground, DLR,
 * Overground, Elizabeth line, buses, and trams.
 * Uses TfL's Unified API (single REST JSON API for all modes).
 *
 * SECURITY MANIFEST
 *   Environment variables: TFL_API_KEY (optional — API works without it, rate-limited)
 *   External endpoints:    api.tfl.gov.uk (TfL Unified API, read-only GET, JSON)
 *   Local files written:   None
 *   Local files read:      .env (if present, for API key)
 *   User input handling:   Used for local filtering and URL query parameters only,
 *                          never interpolated into shell commands
 */

import { parseArgs } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';

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
const TFL_API_KEY = process.env.TFL_API_KEY || '';
const TFL_BASE = 'https://api.tfl.gov.uk';

let _keyWarningShown = false;
function noteApiKey() {
  if (!TFL_API_KEY && !_keyWarningShown) {
    _keyWarningShown = true;
    console.log('Note: TFL_API_KEY not set. Requests are rate-limited.');
    console.log('Get a free key at: https://api-portal.tfl.gov.uk/');
    console.log('With a key you get 500 requests/minute.\n');
  }
}

function apiUrl(endpoint) {
  const sep = endpoint.includes('?') ? '&' : '?';
  return TFL_API_KEY
    ? `${TFL_BASE}${endpoint}${sep}app_key=${encodeURIComponent(TFL_API_KEY)}`
    : `${TFL_BASE}${endpoint}`;
}

async function fetchJSON(url) {
  const resp = await fetch(url, { signal: AbortSignal.timeout(30000) });
  if (resp.status === 429) {
    throw new Error('Rate limited by TfL API. Set TFL_API_KEY for 500 requests/minute. Get a free key at: https://api-portal.tfl.gov.uk/');
  }
  if (!resp.ok) {
    let msg = `HTTP ${resp.status}`;
    try {
      const body = await resp.json();
      if (body.message) msg += `: ${body.message}`;
    } catch {}
    throw new Error(msg);
  }
  return resp.json();
}

// ---------------------------------------------------------------------------
// Tube Lines
// ---------------------------------------------------------------------------
const TUBE_LINES = {
  bakerloo:          { name: 'Bakerloo',          emoji: '\u{1F7E4}', terminals: ['Harrow & Wealdstone', 'Elephant & Castle'] },
  central:           { name: 'Central',            emoji: '\u{1F534}', terminals: ['Epping / Ealing Broadway', 'West Ruislip'] },
  circle:            { name: 'Circle',             emoji: '\u{1F7E1}', terminals: ['Hammersmith (loop via Liverpool Street)'] },
  district:          { name: 'District',           emoji: '\u{1F7E2}', terminals: ['Richmond / Ealing Broadway', 'Upminster'] },
  'hammersmith-city': { name: 'Hammersmith & City', emoji: '\u{1FA77}', terminals: ['Hammersmith', 'Barking'] },
  jubilee:           { name: 'Jubilee',            emoji: '\u26AA',    terminals: ['Stanmore', 'Stratford'] },
  metropolitan:      { name: 'Metropolitan',       emoji: '\u{1F7E3}', terminals: ['Chesham / Amersham / Uxbridge', 'Aldgate'] },
  northern:          { name: 'Northern',           emoji: '\u26AB',    terminals: ['Edgware / High Barnet', 'Morden / Battersea'] },
  piccadilly:        { name: 'Piccadilly',         emoji: '\u{1F535}', terminals: ['Heathrow T5 / Uxbridge', 'Cockfosters'] },
  victoria:          { name: 'Victoria',           emoji: '\u{1FA75}', terminals: ['Walthamstow Central', 'Brixton'] },
  'waterloo-city':   { name: 'Waterloo & City',    emoji: '\u{1F986}', terminals: ['Waterloo', 'Bank'] },
};

const OTHER_LINES = {
  dlr:               { name: 'DLR',                emoji: '\u{1F688}', type: 'Docklands Light Railway' },
  liberty:           { name: 'Liberty',             emoji: '\u{1F69D}', type: 'Overground (Romford — Upminster)' },
  lioness:           { name: 'Lioness',             emoji: '\u{1F69D}', type: 'Overground (Watford — Euston)' },
  mildmay:           { name: 'Mildmay',             emoji: '\u{1F69D}', type: 'Overground (Stratford — Richmond/Clapham)' },
  suffragette:       { name: 'Suffragette',         emoji: '\u{1F69D}', type: 'Overground (Gospel Oak — Barking)' },
  weaver:            { name: 'Weaver',              emoji: '\u{1F69D}', type: 'Overground (Liverpool St — Enfield/Cheshunt/Chingford)' },
  windrush:          { name: 'Windrush',            emoji: '\u{1F69D}', type: 'Overground (Highbury — Crystal Palace/Clapham/W Croydon)' },
  elizabeth:         { name: 'Elizabeth line',      emoji: '\u{1F49C}', type: 'Crossrail' },
  tram:              { name: 'London Trams',        emoji: '\u{1F68B}', type: 'Croydon Tramlink' },
};

function lineEmoji(lineId) {
  return TUBE_LINES[lineId]?.emoji || OTHER_LINES[lineId]?.emoji || '\u{1F687}';
}

function lineName(lineId) {
  return TUBE_LINES[lineId]?.name || OTHER_LINES[lineId]?.name || lineId;
}

// Line ID aliases for user-friendly matching
const LINE_ALIASES = {
  baker: 'bakerloo', bak: 'bakerloo',
  cen: 'central',
  cir: 'circle',
  dis: 'district', dst: 'district',
  'hammersmith': 'hammersmith-city', ham: 'hammersmith-city', 'h&c': 'hammersmith-city',
  jub: 'jubilee',
  met: 'metropolitan', metro: 'metropolitan',
  nor: 'northern', nth: 'northern',
  pic: 'piccadilly', picc: 'piccadilly',
  vic: 'victoria',
  'waterloo': 'waterloo-city', wat: 'waterloo-city', 'w&c': 'waterloo-city',
  overground: 'lioness', over: 'lioness',
  liz: 'elizabeth', crossrail: 'elizabeth', xr: 'elizabeth',
};

function resolveLine(input) {
  if (!input) return null;
  const lower = input.toLowerCase().trim();
  if (TUBE_LINES[lower] || OTHER_LINES[lower]) return lower;
  return LINE_ALIASES[lower] || lower;
}

// ---------------------------------------------------------------------------
// Station Data (for fuzzy matching — top stations)
// ---------------------------------------------------------------------------
const STATIONS = [
  { naptanId: '940GZZLUKSX', name: "King's Cross St. Pancras", aliases: ['kings cross', "king's cross", 'kgx', 'st pancras'] },
  { naptanId: '940GZZLUOXC', name: 'Oxford Circus', aliases: ['oxford circus', 'oxford st'] },
  { naptanId: '940GZZLUWLO', name: 'Waterloo', aliases: ['waterloo'] },
  { naptanId: '940GZZLUVIC', name: 'Victoria', aliases: ['victoria station', 'victoria'] },
  { naptanId: '940GZZLULVT', name: 'Liverpool Street', aliases: ['liverpool street', 'liverpool st'] },
  { naptanId: '940GZZLUPAC', name: 'Paddington', aliases: ['paddington'] },
  { naptanId: '940GZZLUEUS', name: 'Euston', aliases: ['euston'] },
  { naptanId: '940GZZLULNB', name: 'London Bridge', aliases: ['london bridge'] },
  { naptanId: '940GZZLUBNK', name: 'Bank', aliases: ['bank', 'monument'] },
  { naptanId: '940GZZLUCYF', name: 'Canary Wharf', aliases: ['canary wharf'] },
  { naptanId: '940GZZLULSQ', name: 'Leicester Square', aliases: ['leicester square', 'leicester sq'] },
  { naptanId: '940GZZLUPCC', name: 'Piccadilly Circus', aliases: ['piccadilly circus'] },
  { naptanId: '940GZZLUWSM', name: 'Westminster', aliases: ['westminster', 'big ben', 'parliament'] },
  { naptanId: '940GZZLUGPK', name: 'Green Park', aliases: ['green park'] },
  { naptanId: '940GZZLUBND', name: 'Bond Street', aliases: ['bond street'] },
  { naptanId: '940GZZLUTCR', name: 'Tottenham Court Road', aliases: ['tottenham court road', 'tcr'] },
  { naptanId: '940GZZLUCTN', name: 'Camden Town', aliases: ['camden', 'camden town'] },
  { naptanId: '940GZZLUBXN', name: 'Brixton', aliases: ['brixton'] },
  { naptanId: '940GZZLUSTD', name: 'Stratford', aliases: ['stratford', 'olympic park'] },
  { naptanId: '940GZZLUHR5', name: 'Heathrow Terminal 5', aliases: ['heathrow', 'lhr', 'airport', 'heathrow t5'] },
  { naptanId: '940GZZLUHR4', name: 'Heathrow Terminals 2 & 3', aliases: ['heathrow t2', 'heathrow t3', 'heathrow 123'] },
  { naptanId: '940GZZLUBST', name: 'Baker Street', aliases: ['baker street', 'sherlock'] },
  { naptanId: '940GZZLUNHG', name: 'Notting Hill Gate', aliases: ['notting hill'] },
  { naptanId: '940GZZLUAGL', name: 'Angel', aliases: ['angel', 'islington'] },
  { naptanId: '940GZZLUCPC', name: 'Clapham Common', aliases: ['clapham common'] },
  { naptanId: '910GCLPHMJC', name: 'Clapham Junction', aliases: ['clapham junction'] },
  { naptanId: '940GZZLUCPS', name: 'Clapham South', aliases: ['clapham south', 'clapham'] },
  { naptanId: '940GZZLUWYP', name: 'Wembley Park', aliases: ['wembley', 'wembley stadium'] },
  { naptanId: '940GZZLUTFP', name: 'Tufnell Park', aliases: ['tufnell park'] },
  { naptanId: '940GZZLUHBT', name: 'High Barnet', aliases: ['high barnet', 'barnet'] },
  { naptanId: '940GZZLUEAC', name: 'East Acton', aliases: ['east acton'] },
  { naptanId: '940GZZLUKNG', name: 'Kennington', aliases: ['kennington'] },
  { naptanId: '940GZZLUSKW', name: 'South Kensington', aliases: ['south ken', 'south kensington'] },
  { naptanId: '940GZZLUSKS', name: 'Sloane Square', aliases: ['sloane square'] },
  { naptanId: '940GZZLUERB', name: 'Edgware Road (Bakerloo)', aliases: ['edgware road'] },
  { naptanId: '940GZZLUMDN', name: 'Morden', aliases: ['morden'] },
  { naptanId: '940GZZLUSWN', name: 'Stockwell', aliases: ['stockwell'] },
  { naptanId: '940GZZLUBLG', name: 'Bethnal Green', aliases: ['bethnal green'] },
  { naptanId: '940GZZLUMSH', name: 'Moorgate', aliases: ['moorgate'] },
  { naptanId: '940GZZLUFCN', name: 'Farringdon', aliases: ['farringdon'] },
];

function searchStation(query) {
  const q = query.toLowerCase().replace(/['']/g, '').trim();

  const scored = [];
  for (const s of STATIONS) {
    const nameNorm = s.name.toLowerCase().replace(/['']/g, '');
    let score = 999;
    if (nameNorm === q) score = 0;
    else if (s.aliases.some(a => a === q)) score = 1;
    else if (nameNorm.startsWith(q)) score = 2;
    else if (s.aliases.some(a => a.startsWith(q))) score = 3;
    else if (nameNorm.includes(q)) score = 4;
    else if (s.aliases.some(a => a.includes(q))) score = 5;
    else if (q.split(/\s+/).every(w => nameNorm.includes(w) || s.aliases.some(a => a.includes(w)))) score = 6;
    else continue;
    scored.push({ ...s, score });
  }
  scored.sort((a, b) => a.score - b.score || a.name.localeCompare(b.name));
  return scored;
}

// ---------------------------------------------------------------------------
// Time helpers — GMT/BST (London Time)
// ---------------------------------------------------------------------------
function londonTzOffsetHours() {
  const now = new Date();
  const year = now.getUTCFullYear();
  // BST starts last Sunday of March at 01:00 UTC
  const mar31 = new Date(Date.UTC(year, 2, 31));
  const lastSunMar = 31 - mar31.getUTCDay();
  const bstStart = Date.UTC(year, 2, lastSunMar, 1);
  // BST ends last Sunday of October at 01:00 UTC
  const oct31 = new Date(Date.UTC(year, 9, 31));
  const lastSunOct = 31 - oct31.getUTCDay();
  const bstEnd = Date.UTC(year, 9, lastSunOct, 1);
  const ts = now.getTime();
  return (ts >= bstStart && ts < bstEnd) ? 1 : 0;
}

function toLondonDate(d) {
  const offset = londonTzOffsetHours();
  return new Date(d.getTime() + offset * 3600000);
}

function londonNow() {
  return toLondonDate(new Date());
}

function fmtTime24(d) {
  const h = d.getUTCHours(), m = d.getUTCMinutes();
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

// ---------------------------------------------------------------------------
// Haversine (miles)
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

// ---- Line Status ----

async function cmdStatus(opts) {
  noteApiKey();
  const lineId = opts.line ? resolveLine(opts.line) : null;
  const showAll = opts.all;

  let url;
  if (lineId) {
    url = apiUrl(`/Line/${encodeURIComponent(lineId)}/Status`);
  } else if (showAll) {
    url = apiUrl('/Line/Mode/tube,dlr,overground,elizabeth-line,tram/Status');
  } else {
    url = apiUrl('/Line/Mode/tube/Status');
  }

  const data = await fetchJSON(url);
  if (!data || data.length === 0) {
    console.log('No line status data available.');
    return;
  }

  const lines = Array.isArray(data) ? data : [data];
  const label = lineId ? `${lineName(lineId)} Status` : showAll ? 'All TfL Lines Status' : 'Tube Status';
  console.log(`\n=== ${label} ===\n`);

  for (const line of lines) {
    const id = line.id || '';
    const name = line.name || id;
    const emoji = lineEmoji(id);
    const statuses = line.lineStatuses || [];

    for (const status of statuses) {
      const severity = status.statusSeverityDescription || 'Unknown';
      const reason = status.reason || '';

      let icon = '';
      if (severity === 'Good Service') icon = '\u2705';
      else if (severity === 'Minor Delays') icon = '\u{1F7E1}';
      else if (severity.includes('Severe') || severity.includes('Suspended')) icon = '\u{1F534}';
      else if (severity.includes('Part')) icon = '\u{1F7E0}';
      else if (severity === 'Service Closed') icon = '\u26AB';
      else icon = '\u{1F7E1}';

      console.log(`${emoji} ${name}: ${icon} ${severity}`);
      if (reason) {
        const shortReason = reason.length > 300 ? reason.slice(0, 300) + '...' : reason;
        console.log(`   ${shortReason}`);
      }
    }
  }
}

// ---- Arrivals ----

async function cmdArrivals(opts) {
  noteApiKey();
  let naptanId = opts.stop;
  const stopSearch = opts['stop-search'];
  const stationName = opts.station;
  const lineFilter = opts.line ? resolveLine(opts.line) : null;

  // Resolve station by name search
  if (stationName || stopSearch) {
    const query = stationName || stopSearch;
    const localMatches = searchStation(query);

    if (localMatches.length) {
      if (localMatches.length > 1) {
        console.log(`Found ${localMatches.length} stations matching '${query}':`);
        for (const s of localMatches.slice(0, 8)) {
          console.log(`  ${s.naptanId} \u2014 ${s.name}`);
        }
        console.log(`\nUsing best match: ${localMatches[0].name}\n`);
      }
      naptanId = localMatches[0].naptanId;
    } else {
      // Fall back to TfL search API
      console.log(`Searching TfL for '${query}'...`);
      const searchUrl = apiUrl(`/StopPoint/Search/${encodeURIComponent(query)}?modes=tube,dlr,overground,elizabeth-line,tram`);
      const searchData = await fetchJSON(searchUrl);
      const matches = searchData?.matches || [];
      if (!matches.length) {
        console.log(`No stations found matching '${query}'.`);
        console.log("Try 'stops --search <name>' to search all stops.");
        return;
      }
      if (matches.length > 1) {
        console.log(`Found ${matches.length} stations matching '${query}':`);
        for (const s of matches.slice(0, 8)) {
          console.log(`  ${s.id} \u2014 ${s.name}`);
        }
        console.log(`\nUsing best match: ${matches[0].name}\n`);
      }
      naptanId = matches[0].id;
    }
  }

  if (!naptanId) {
    console.log('Provide --station, --stop-search, or --stop');
    return;
  }

  const url = apiUrl(`/StopPoint/${encodeURIComponent(naptanId)}/Arrivals`);
  const data = await fetchJSON(url);

  if (!data || data.length === 0) {
    console.log(`No arrivals at ${naptanId}. Station may be closed or have no active service.`);
    return;
  }

  let arrivals = Array.isArray(data) ? data : [data];

  // Filter by line if specified
  if (lineFilter) {
    arrivals = arrivals.filter(a => a.lineId === lineFilter);
    if (!arrivals.length) {
      console.log(`No arrivals for ${lineName(lineFilter)} at this station.`);
      return;
    }
  }

  // Sort by timeToStation
  arrivals.sort((a, b) => (a.timeToStation || 0) - (b.timeToStation || 0));

  const stationLabel = arrivals[0]?.stationName || naptanId;
  console.log(`\n=== Arrivals at: ${stationLabel} ===\n`);

  for (const a of arrivals.slice(0, 20)) {
    const emoji = lineEmoji(a.lineId);
    const name = a.lineName || a.lineId || '?';
    const dest = a.destinationName || a.towards || 'Unknown';
    const secs = a.timeToStation || 0;
    const mins = Math.round(secs / 60);
    const platform = a.platformName || '';

    let etaStr;
    if (mins <= 0) etaStr = 'Due';
    else if (mins === 1) etaStr = '1 min';
    else etaStr = `${mins} min`;

    const expectedTime = a.expectedArrival ? fmtTime24(toLondonDate(new Date(a.expectedArrival))) : '';

    console.log(`  ${emoji} ${name} \u2192 ${dest}`);
    console.log(`     ${expectedTime ? expectedTime + ' ' : ''}(${etaStr})${platform ? ' \u2014 ' + platform : ''}`);
    if (a.currentLocation) console.log(`     ${a.currentLocation}`);
    console.log();
  }
}

// ---- Bus Arrivals ----

async function cmdBusArrivals(opts) {
  noteApiKey();
  let stopId = opts.stop;
  const stopSearch = opts['stop-search'];
  const routeFilter = opts.route;

  if (stopSearch) {
    console.log(`Searching TfL for bus stops matching '${stopSearch}'...`);
    const searchUrl = apiUrl(`/StopPoint/Search/${encodeURIComponent(stopSearch)}?modes=bus`);
    const searchData = await fetchJSON(searchUrl);
    const matches = searchData?.matches || [];
    if (!matches.length) {
      console.log(`No bus stops found matching '${stopSearch}'.`);
      return;
    }
    if (matches.length > 1) {
      console.log(`Found ${matches.length} stops matching '${stopSearch}':`);
      for (const s of matches.slice(0, 10)) {
        console.log(`  ${s.id} \u2014 ${s.name}`);
      }
      console.log(`\nUsing best match: ${matches[0].name}\n`);
    }
    stopId = matches[0].id;
  }

  if (!stopId) {
    console.log('Provide --stop or --stop-search');
    return;
  }

  const url = apiUrl(`/StopPoint/${encodeURIComponent(stopId)}/Arrivals`);
  const data = await fetchJSON(url);

  if (!data || data.length === 0) {
    console.log(`No bus arrivals at stop ${stopId}.`);
    return;
  }

  let arrivals = Array.isArray(data) ? data : [data];

  // Filter to bus mode
  arrivals = arrivals.filter(a => a.modeName === 'bus');

  // Filter by route if specified
  if (routeFilter) {
    arrivals = arrivals.filter(a => a.lineName === routeFilter || a.lineId === routeFilter);
    if (!arrivals.length) {
      console.log(`No arrivals for route ${routeFilter} at this stop.`);
      return;
    }
  }

  arrivals.sort((a, b) => (a.timeToStation || 0) - (b.timeToStation || 0));

  const stopLabel = arrivals[0]?.stationName || stopId;
  console.log(`\n=== Bus Arrivals at: ${stopLabel} (${stopId}) ===\n`);

  for (const a of arrivals.slice(0, 20)) {
    const route = a.lineName || a.lineId || '?';
    const dest = a.destinationName || a.towards || 'Unknown';
    const secs = a.timeToStation || 0;
    const mins = Math.round(secs / 60);

    let etaStr;
    if (mins <= 0) etaStr = 'Due';
    else if (mins === 1) etaStr = '1 min';
    else etaStr = `${mins} min`;

    const expectedTime = a.expectedArrival ? fmtTime24(toLondonDate(new Date(a.expectedArrival))) : '';

    console.log(`  \u{1F68C} Route ${route} \u2192 ${dest}`);
    console.log(`     ${expectedTime ? expectedTime + ' ' : ''}(${etaStr})`);
    console.log();
  }
}

// ---- Disruptions ----

async function cmdDisruptions(opts) {
  noteApiKey();
  const lineId = opts.line ? resolveLine(opts.line) : null;

  let url;
  if (lineId) {
    url = apiUrl(`/Line/${encodeURIComponent(lineId)}/Disruption`);
  } else {
    // Get disruptions for all Tube + rail lines
    // TfL expects comma-separated line IDs unencoded in the path
    const allLineIds = [
      ...Object.keys(TUBE_LINES),
      ...Object.keys(OTHER_LINES),
    ].join(',');
    url = apiUrl(`/Line/${allLineIds}/Disruption`);
  }

  const data = await fetchJSON(url);

  if (!data || data.length === 0) {
    const filterMsg = lineId ? ` on ${lineName(lineId)}` : '';
    console.log(`No active disruptions${filterMsg}.`);
    return;
  }

  const disruptions = Array.isArray(data) ? data : [data];
  const label = lineId ? `${lineName(lineId)} Disruptions` : 'TfL Disruptions';
  console.log(`\n=== ${label} (${disruptions.length} active) ===\n`);

  for (const d of disruptions) {
    const category = d.category || '';
    const desc = d.description || '';
    const affectedLines = (d.affectedRoutes || []).map(r => r.name).filter(Boolean);
    const closureText = d.closureText || '';

    const categoryDesc = d.categoryDescription || category || 'Disruption';

    let icon = '\u{1F7E1}';
    if (category === 'RealTime' || categoryDesc.includes('Severe')) icon = '\u{1F534}';
    else if (category === 'PlannedWork') icon = '\u{1F7E0}';
    else if (category === 'Information') icon = '\u{1F535}';

    console.log(`${icon} ${categoryDesc}`);
    if (affectedLines.length) console.log(`   Lines: ${affectedLines.join(', ')}`);
    if (closureText && closureText !== categoryDesc) console.log(`   ${closureText}`);
    if (desc) {
      const shortDesc = desc.length > 400 ? desc.slice(0, 400) + '...' : desc;
      console.log(`   ${shortDesc}`);
    }
    console.log();
  }
}

// ---- Routes ----

async function cmdRoutes(opts) {
  const showAll = opts.all;

  console.log('\n=== Tube Lines ===\n');
  for (const [id, line] of Object.entries(TUBE_LINES)) {
    console.log(`  ${line.emoji} ${line.name.padEnd(20)} ${line.terminals.join(' \u2194 ')}`);
  }

  if (showAll) {
    console.log('\n=== Other TfL Rail ===\n');
    for (const [id, line] of Object.entries(OTHER_LINES)) {
      console.log(`  ${line.emoji} ${line.name.padEnd(20)} ${line.type}`);
    }
  }
}

// ---- Bus Routes ----

async function cmdBusRoutes(opts) {
  noteApiKey();
  console.log('Fetching bus routes from TfL...');
  const url = apiUrl('/Line/Mode/bus');
  const data = await fetchJSON(url);

  if (!data || data.length === 0) {
    console.log('No bus routes found.');
    return;
  }

  const routes = Array.isArray(data) ? data : [data];
  routes.sort((a, b) => {
    const an = parseInt(a.name) || 9999;
    const bn = parseInt(b.name) || 9999;
    return an - bn || (a.name || '').localeCompare(b.name || '');
  });

  console.log(`\n=== TfL Bus Routes (${routes.length}) ===\n`);

  for (const r of routes) {
    console.log(`  ${(r.name || r.id || '?').padStart(5)} | ${r.id}`);
  }
}

// ---- Stops ----

async function cmdStops(opts) {
  noteApiKey();
  const searchQuery = opts.search;
  const near = opts.near;
  const lineId = opts.line ? resolveLine(opts.line) : null;
  const radius = opts.radius ? parseInt(opts.radius) : 500;

  if (lineId) {
    // List stops on a line
    const url = apiUrl(`/Line/${encodeURIComponent(lineId)}/StopPoints`);
    const data = await fetchJSON(url);

    if (!data || data.length === 0) {
      console.log(`No stops found for ${lineName(lineId)}.`);
      return;
    }

    const stops = Array.isArray(data) ? data : [data];
    console.log(`\n=== Stops on ${lineName(lineId)} (${stops.length}) ===\n`);
    for (const s of stops) {
      console.log(`  \u{1F4CD} ${s.commonName || s.id}`);
      console.log(`     ID: ${s.naptanId || s.id}  |  (${s.lat}, ${s.lon})`);
      console.log();
    }
    return;
  }

  if (searchQuery) {
    // First try embedded stations
    const localMatches = searchStation(searchQuery);
    if (localMatches.length) {
      console.log(`\n=== Stations matching '${searchQuery}' (${localMatches.length} local matches) ===\n`);
      for (const s of localMatches.slice(0, 20)) {
        console.log(`  \u{1F4CD} ${s.name}`);
        console.log(`     ID: ${s.naptanId}`);
        console.log();
      }
    }

    // Also search TfL API for more results
    const searchUrl = apiUrl(`/StopPoint/Search/${encodeURIComponent(searchQuery)}?modes=tube,bus,dlr,overground,elizabeth-line,tram`);
    const searchData = await fetchJSON(searchUrl);
    const matches = searchData?.matches || [];

    if (matches.length) {
      // Filter out any we already showed from local data
      const localIds = new Set(localMatches.map(s => s.naptanId));
      const apiOnly = matches.filter(m => !localIds.has(m.id));
      if (apiOnly.length) {
        console.log(`=== Additional TfL results (${apiOnly.length}) ===\n`);
        for (const s of apiOnly.slice(0, 15)) {
          console.log(`  \u{1F4CD} ${s.name}`);
          console.log(`     ID: ${s.id}`);
          if (s.modes?.length) console.log(`     Modes: ${s.modes.join(', ')}`);
          console.log();
        }
      }
    }

    if (!localMatches.length && !matches.length) {
      console.log(`No stops found matching '${searchQuery}'.`);
    }
    return;
  }

  if (near) {
    const parts = near.split(',');
    if (parts.length !== 2) { console.log('Invalid format. Use: --near LAT,LON'); return; }
    const [lat, lon] = parts.map(Number);
    if (isNaN(lat) || isNaN(lon)) { console.log('Invalid format. Use: --near LAT,LON'); return; }

    const url = apiUrl(`/StopPoint?lat=${lat}&lon=${lon}&stopTypes=NaptanMetroStation,NaptanRailStation,NaptanBusCoachStation,NaptanPublicBusCoachTram&radius=${radius}`);
    const data = await fetchJSON(url);

    const stops = data?.stopPoints || [];
    if (!stops.length) {
      console.log(`No stops found within ${radius}m of (${lat}, ${lon}).`);
      return;
    }

    // Sort by distance
    stops.sort((a, b) => (a.distance || 0) - (b.distance || 0));

    console.log(`\n=== Nearby Stops (${stops.length} within ${radius}m) ===\n`);
    for (const s of stops.slice(0, 20)) {
      const dist = s.distance != null ? ` \u2014 ${Math.round(s.distance)}m` : '';
      const modes = s.modes?.length ? ` [${s.modes.join(', ')}]` : '';
      console.log(`  \u{1F4CD} ${s.commonName || s.id}${dist}${modes}`);
      console.log(`     ID: ${s.naptanId || s.id}`);
      console.log();
    }
    return;
  }

  console.log('Provide --search <name>, --near LAT,LON, or --line <lineId>');
}

// ---- Route Info ----

async function cmdRouteInfo(opts) {
  noteApiKey();
  const lineId = opts.line ? resolveLine(opts.line) : null;
  const routeId = opts.route;
  const targetLine = lineId || routeId;

  if (!targetLine) {
    console.log('Provide --line <lineId> or --route <routeNumber>');
    return;
  }

  // Get route sequence
  const url = apiUrl(`/Line/${encodeURIComponent(targetLine)}/Route/Sequence/outbound`);
  let data;
  try {
    data = await fetchJSON(url);
  } catch (err) {
    // Try as inbound if outbound fails
    try {
      data = await fetchJSON(apiUrl(`/Line/${encodeURIComponent(targetLine)}/Route/Sequence/inbound`));
    } catch {
      console.log(`Route '${targetLine}' not found or no route data available.`);
      return;
    }
  }

  const name = data?.lineName || targetLine;
  console.log(`\n=== ${name} Route ===\n`);

  // stopPointSequences has the actual stop data; orderedLineRoutes has branch names
  const sequences = data?.stopPointSequences || [];
  if (!sequences.length) {
    // Fall back to orderedLineRoutes for branch names only
    const branches = data?.orderedLineRoutes || [];
    if (branches.length) {
      for (const b of branches) {
        console.log(`  ${b.name || 'Route'}`);
      }
    } else {
      console.log('No route sequence data available.');
    }
    return;
  }

  for (const seq of sequences) {
    const branch = seq.name || seq.direction || '';
    if (branch) console.log(`Branch: ${branch}\n`);

    const stopPoints = seq.stopPoint || [];
    for (let i = 0; i < stopPoints.length; i++) {
      const s = stopPoints[i];
      const sname = s.name || s.commonName || s.id;
      console.log(`  ${String(i + 1).padStart(3)}. ${sname}`);
    }
    console.log();
  }
}

// ---- Journey Planning ----

async function cmdJourney(opts) {
  noteApiKey();
  let from = opts.from;
  let to = opts.to;

  if (!from || !to) {
    console.log('Provide --from and --to (station name or LAT,LON)');
    return;
  }

  // Resolve station names to NaPTAN IDs or coordinates
  from = await resolveJourneyPoint(from);
  to = await resolveJourneyPoint(to);

  if (!from || !to) return;

  const url = apiUrl(`/Journey/JourneyResults/${encodeURIComponent(from)}/to/${encodeURIComponent(to)}`);
  const data = await fetchJSON(url);

  const journeys = data?.journeys || [];
  if (!journeys.length) {
    console.log('No journey results found.');
    return;
  }

  console.log(`\n=== Journey: ${opts.from} \u2192 ${opts.to} ===\n`);

  for (let j = 0; j < Math.min(journeys.length, 3); j++) {
    const journey = journeys[j];
    const duration = journey.duration || '?';
    const startTime = journey.startDateTime ? fmtTime24(toLondonDate(new Date(journey.startDateTime))) : '';
    const arrTime = journey.arrivalDateTime ? fmtTime24(toLondonDate(new Date(journey.arrivalDateTime))) : '';

    console.log(`--- Option ${j + 1}: ${duration} min (${startTime} \u2192 ${arrTime}) ---\n`);

    const legs = journey.legs || [];
    for (let i = 0; i < legs.length; i++) {
      const leg = legs[i];
      const mode = leg.mode?.name || leg.mode?.id || '?';
      const lineName = leg.routeOptions?.[0]?.name || '';
      const lineDir = leg.routeOptions?.[0]?.directions?.[0] || '';
      const from = leg.departurePoint?.commonName || '';
      const to = leg.arrivalPoint?.commonName || '';
      const legDuration = leg.duration || '';

      let modeEmoji = '\u{1F6B6}';
      if (mode === 'tube') modeEmoji = '\u{1F687}';
      else if (mode === 'bus') modeEmoji = '\u{1F68C}';
      else if (mode === 'dlr') modeEmoji = '\u{1F688}';
      else if (mode === 'overground') modeEmoji = '\u{1F69D}';
      else if (mode === 'elizabeth-line') modeEmoji = '\u{1F49C}';
      else if (mode === 'walking') modeEmoji = '\u{1F6B6}';
      else if (mode === 'tram') modeEmoji = '\u{1F68B}';

      console.log(`  ${modeEmoji} ${mode}${lineName ? ' (' + lineName + ')' : ''}`);
      console.log(`     ${from} \u2192 ${to} (${legDuration} min)`);
      if (lineDir) console.log(`     Direction: ${lineDir}`);

      // Show intermediate stops count
      const path = leg.path?.stopPoints || [];
      if (path.length > 0) {
        console.log(`     ${path.length} stop${path.length === 1 ? '' : 's'}`);
      }
      console.log();
    }

    // Fare info
    const fare = journey.fare;
    if (fare?.totalCost) {
      const cost = (fare.totalCost / 100).toFixed(2);
      console.log(`  \u{1F4B7} Fare: \u00A3${cost}`);
      console.log();
    }
  }
}

async function resolveJourneyPoint(input) {
  // Check if it looks like coordinates
  if (/^-?\d+\.?\d*,-?\d+\.?\d*$/.test(input.trim())) {
    return input.trim();
  }

  // Try embedded stations first
  const localMatches = searchStation(input);
  if (localMatches.length) {
    return localMatches[0].naptanId;
  }

  // Fall back to TfL search
  const searchUrl = apiUrl(`/StopPoint/Search/${encodeURIComponent(input)}?modes=tube,bus,dlr,overground,elizabeth-line,tram`);
  const searchData = await fetchJSON(searchUrl);
  const matches = searchData?.matches || [];
  if (matches.length) {
    return matches[0].id;
  }

  console.log(`Could not resolve '${input}' to a station or location.`);
  return null;
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === '-h') {
    console.log(`TfL London Transit \u2014 OpenClaw Skill

Commands:
  status          Tube line status [--line LINE] [--all]
  arrivals        Arrivals at station (--station NAME | --stop-search NAME | --stop ID) [--line LINE]
  bus-arrivals    Bus arrivals (--stop ID | --stop-search NAME) [--route NUM]
  disruptions     Current disruptions [--line LINE]
  routes          List Tube lines [--all for all modes]
  bus-routes      List all bus routes
  stops           Search stops (--search NAME | --near LAT,LON [--radius M] | --line LINE)
  route-info      Route stops (--line LINE | --route NUM)
  journey         Plan a journey (--from PLACE --to PLACE)

Tube Lines: bakerloo, central, circle, district, hammersmith-city, jubilee,
            metropolitan, northern, piccadilly, victoria, waterloo-city
Other: dlr, london-overground, elizabeth, tram

Environment: TFL_API_KEY (optional, free, from api-portal.tfl.gov.uk)`);
    return;
  }

  const rest = args.slice(1);

  const optDefs = {
    line: { type: 'string' },
    route: { type: 'string' },
    stop: { type: 'string' },
    'stop-search': { type: 'string' },
    station: { type: 'string' },
    search: { type: 'string' },
    near: { type: 'string' },
    radius: { type: 'string' },
    from: { type: 'string' },
    to: { type: 'string' },
    all: { type: 'boolean' },
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
    status: () => cmdStatus(opts),
    arrivals: () => cmdArrivals(opts),
    'bus-arrivals': () => cmdBusArrivals(opts),
    disruptions: () => cmdDisruptions(opts),
    routes: () => cmdRoutes(opts),
    'bus-routes': () => cmdBusRoutes(opts),
    stops: () => cmdStops(opts),
    'route-info': () => cmdRouteInfo(opts),
    journey: () => cmdJourney(opts),
  };

  if (handlers[command]) {
    Promise.resolve(handlers[command]()).catch(err => {
      if (err.name === 'TimeoutError' || err.message?.includes('timeout')) {
        console.error('Request timed out. TfL API may be slow or unreachable. Try again in a moment.');
      } else if (err.code === 'ENOTFOUND' || err.code === 'ECONNREFUSED') {
        console.error('Network error: Could not reach TfL API. Check your internet connection.');
      } else if (err.message?.includes('Rate limited')) {
        console.error(err.message);
      } else {
        console.error(`Error: ${err.message}`);
      }
      process.exit(1);
    });
  } else {
    console.error(`Unknown command: ${command}`);
    console.error("Run 'node scripts/tfl.mjs --help' for available commands.");
    process.exit(1);
  }
}

main();
