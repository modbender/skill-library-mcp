#!/usr/bin/env node

/**
 * SXSW 2026 Schedule CLI
 *
 * Security manifest:
 *   Env vars read: none
 *   External endpoints: none (local data only)
 *   Local files read: data/sxsw-2026-schedule.json, data/sxsw-2026-index.json
 *   Local files written: none
 *   User input: CLI arguments only (sanitized via parseArgs)
 */

import { parseArgs } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');
const SCHEDULE_FILE = path.join(DATA_DIR, 'sxsw-2026-schedule.json');
const INDEX_FILE = path.join(DATA_DIR, 'sxsw-2026-index.json');

// ── Interfaces ─────────────────────────────────────────────────────

interface Speaker {
  name: string;
  title: string;
  company: string;
}

interface SXSWEvent {
  id: string;
  title: string;
  description: string;
  date: string;
  start_time: string;
  end_time: string;
  venue: string;
  venue_address: string;
  venue_id: string;
  track: string;
  tags: string[];
  format: string;
  event_type: string;
  speakers: Speaker[];
  credential_types: string[];
  experience_level: string;
  url: string;
  thumbnail_url: string;
}

interface Schedule {
  scraped_at: string;
  event_count: number;
  date_range: { start: string; end: string };
  events: SXSWEvent[];
}

interface SearchIndex {
  byDate: Record<string, string[]>;
  byTrack: Record<string, string[]>;
  byVenue: Record<string, string[]>;
  byFormat: Record<string, string[]>;
  byType: Record<string, string[]>;
  bySpeaker: Record<string, string[]>;
  keywords: Record<string, string[]>;
  scraped_at?: string;
  event_count?: number;
  aggregations?: Record<string, { key: string; count: number }[]>;
}

interface EventFilterOptions {
  date?: string;
  track?: string;
  venue?: string;
  format?: string;
  search?: string;
  verbose?: boolean;
  limit?: string;
  help?: boolean;
}

interface PrintOptions {
  title?: string;
  verbose?: boolean;
  limit?: number;
}

// ── Data loading ────────────────────────────────────────────────────

let _schedule: Schedule | null = null;
let _index: SearchIndex | null = null;

function loadSchedule(): Schedule {
  if (!_schedule) {
    _schedule = JSON.parse(fs.readFileSync(SCHEDULE_FILE, 'utf8'));
  }
  return _schedule!;
}

function loadIndex(): SearchIndex {
  if (!_index) {
    _index = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));
  }
  return _index!;
}

function getEventsMap(): Map<string, SXSWEvent> {
  const schedule = loadSchedule();
  const map = new Map<string, SXSWEvent>();
  for (const evt of schedule.events) {
    map.set(evt.id, evt);
  }
  return map;
}

// ── Time utilities ──────────────────────────────────────────────────

function fmtTime(isoStr: string): string {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  return d.toLocaleTimeString('en-US', {
    timeZone: 'America/Chicago',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

function fmtDate(dateStr: string): string {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T12:00:00');
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
}

function fmtDateLong(dateStr: string): string {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T12:00:00');
  return d.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
}

function getTodayCST(): string {
  return new Date().toLocaleDateString('en-CA', { timeZone: 'America/Chicago' });
}

function getTomorrowCST(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toLocaleDateString('en-CA', { timeZone: 'America/Chicago' });
}

// ── Formatters ──────────────────────────────────────────────────────

function fmtEvent(evt: SXSWEvent, verbose: boolean = false): string {
  const time = evt.start_time ? fmtTime(evt.start_time) : 'TBD';
  const end = evt.end_time ? ` - ${fmtTime(evt.end_time)}` : '';
  const venue = evt.venue ? ` @ ${evt.venue}` : '';
  const track = evt.track ? ` [${evt.track}]` : '';
  const format = evt.format ? ` (${evt.format})` : '';

  let line = `  ${time}${end}${venue}${format}${track}`;
  line += `\n    ${evt.title}`;

  if (verbose && evt.speakers.length > 0) {
    const names = evt.speakers.map(s => {
      let n = s.name;
      if (s.title && s.company) n += ` (${s.title}, ${s.company})`;
      else if (s.company) n += ` (${s.company})`;
      else if (s.title) n += ` (${s.title})`;
      return n;
    });
    line += `\n    Speakers: ${names.join(', ')}`;
  }

  if (verbose && evt.description) {
    const desc = evt.description.replace(/\r?\n/g, ' ').trim();
    const truncated = desc.length > 200 ? desc.slice(0, 200) + '...' : desc;
    line += `\n    ${truncated}`;
  }

  line += `\n    ${evt.url}`;
  return line;
}

function printEvents(events: SXSWEvent[], { title, verbose = false, limit = 0 }: PrintOptions = {}): void {
  if (title) console.log(`\n${title}`);

  const schedule = loadSchedule();
  console.log(`Data freshness: scraped ${schedule.scraped_at}`);

  if (events.length === 0) {
    console.log('\n  No events found.');
    return;
  }

  const display = limit > 0 ? events.slice(0, limit) : events;
  console.log(`\nShowing ${display.length} of ${events.length} events:\n`);

  // Group by date
  const byDate = new Map<string, SXSWEvent[]>();
  for (const evt of display) {
    const date = evt.date || 'Date TBD';
    if (!byDate.has(date)) byDate.set(date, []);
    byDate.get(date)!.push(evt);
  }

  for (const [date, evts] of byDate) {
    const label = date === 'Date TBD' ? date : `${fmtDate(date)} (${date})`;
    console.log(`--- ${label} ---`);
    for (const evt of evts) {
      console.log(fmtEvent(evt, verbose));
    }
    console.log();
  }
}

// ── Resolvers ───────────────────────────────────────────────────────

function resolveIds(ids: string[]): SXSWEvent[] {
  const eventsMap = getEventsMap();
  return ids.map(id => eventsMap.get(id)).filter(Boolean) as SXSWEvent[];
}

// ── Commands ────────────────────────────────────────────────────────

function cmdEvents(opts: EventFilterOptions): void {
  const schedule = loadSchedule();
  const index = loadIndex();
  let events = schedule.events;

  // Filter by date
  if (opts.date) {
    const dateIds = index.byDate[opts.date] || [];
    if (dateIds.length > 0) {
      const idSet = new Set(dateIds);
      events = events.filter(e => idSet.has(e.id));
    } else {
      events = events.filter(e => e.date === opts.date);
    }
  }

  // Filter by track/category
  if (opts.track) {
    const q = opts.track.toLowerCase();
    const matchedIds = new Set<string>();
    for (const [track, ids] of Object.entries(index.byTrack)) {
      if (track.toLowerCase().includes(q)) {
        for (const id of ids) matchedIds.add(id);
      }
    }
    if (matchedIds.size > 0) {
      events = events.filter(e => matchedIds.has(e.id));
    } else {
      events = events.filter(e =>
        (e.track && e.track.toLowerCase().includes(q)) ||
        e.tags.some(t => t.toLowerCase().includes(q))
      );
    }
  }

  // Filter by venue
  if (opts.venue) {
    const q = opts.venue.toLowerCase();
    const matchedIds = new Set<string>();
    for (const [venue, ids] of Object.entries(index.byVenue)) {
      if (venue.toLowerCase().includes(q)) {
        for (const id of ids) matchedIds.add(id);
      }
    }
    if (matchedIds.size > 0) {
      events = events.filter(e => matchedIds.has(e.id));
    } else {
      events = events.filter(e => e.venue.toLowerCase().includes(q));
    }
  }

  // Filter by format
  if (opts.format) {
    const q = opts.format.toLowerCase();
    const matchedIds = new Set<string>();
    for (const [fmt, ids] of Object.entries(index.byFormat)) {
      if (fmt.toLowerCase().includes(q)) {
        for (const id of ids) matchedIds.add(id);
      }
    }
    if (matchedIds.size > 0) {
      events = events.filter(e => matchedIds.has(e.id));
    } else {
      events = events.filter(e => e.format.toLowerCase().includes(q));
    }
  }

  // Full-text search
  if (opts.search) {
    const words = opts.search.toLowerCase().match(/\b\w{3,}\b/g) || [];
    if (words.length > 0) {
      const keywords = index.keywords;
      // Intersect results for all search words
      let matchedIds: Set<string> | null = null;
      for (const w of words) {
        const ids = new Set(keywords[w] || []);
        if (matchedIds === null) {
          matchedIds = ids;
        } else {
          const prev: Set<string> = matchedIds;
          matchedIds = new Set([...prev].filter(id => ids.has(id)));
        }
      }
      if (matchedIds && matchedIds.size > 0) {
        events = events.filter(e => matchedIds!.has(e.id));
      } else {
        // Fallback: brute-force search
        const q = opts.search.toLowerCase();
        events = events.filter(e =>
          e.title.toLowerCase().includes(q) ||
          e.description.toLowerCase().includes(q) ||
          e.track.toLowerCase().includes(q) ||
          e.tags.some(t => t.toLowerCase().includes(q))
        );
      }
    }
  }

  const filters: string[] = [];
  if (opts.date) filters.push(`date=${opts.date}`);
  if (opts.track) filters.push(`track="${opts.track}"`);
  if (opts.venue) filters.push(`venue="${opts.venue}"`);
  if (opts.format) filters.push(`format="${opts.format}"`);
  if (opts.search) filters.push(`search="${opts.search}"`);

  const title = filters.length > 0
    ? `SXSW 2026 Events (${filters.join(', ')})`
    : 'SXSW 2026 Events';

  printEvents(events, { title, verbose: opts.verbose, limit: opts.limit ? parseInt(opts.limit) : 0 });
}

function cmdSpeakers(opts: EventFilterOptions): void {
  const index = loadIndex();

  if (opts.search) {
    const q = opts.search.toLowerCase();
    const matchedIds = new Set<string>();
    const matchedSpeakers: string[] = [];

    for (const [name, ids] of Object.entries(index.bySpeaker)) {
      if (name.toLowerCase().includes(q)) {
        matchedSpeakers.push(name);
        for (const id of ids) matchedIds.add(id);
      }
    }

    if (matchedSpeakers.length === 0) {
      console.log(`\nNo speakers found matching "${opts.search}"`);
      return;
    }

    console.log(`\nSpeakers matching "${opts.search}":`);
    for (const name of matchedSpeakers) {
      console.log(`  - ${name} (${index.bySpeaker[name].length} session(s))`);
    }

    const events = resolveIds([...matchedIds]);
    printEvents(events, { title: `Sessions for matching speakers`, verbose: true });
  } else {
    // List all speakers
    const speakers = Object.entries(index.bySpeaker)
      .sort((a, b) => b[1].length - a[1].length);

    console.log(`\nSXSW 2026 Speakers (${speakers.length} total)\n`);
    console.log('Top speakers by session count:');
    for (const [name, ids] of speakers.slice(0, 50)) {
      console.log(`  ${name} — ${ids.length} session(s)`);
    }
    if (speakers.length > 50) {
      console.log(`\n  ... and ${speakers.length - 50} more. Use --search to find specific speakers.`);
    }
  }
}

function cmdVenues(): void {
  const index = loadIndex();
  const venues = Object.entries(index.byVenue)
    .sort((a, b) => b[1].length - a[1].length);

  console.log(`\nSXSW 2026 Venues (${venues.length} total)\n`);
  for (const [venue, ids] of venues) {
    console.log(`  ${venue} — ${ids.length} event(s)`);
  }
}

function cmdTracks(): void {
  const index = loadIndex();
  // Use aggregation data if available, otherwise fall back to index
  if (index.aggregations?.theme) {
    console.log(`\nSXSW 2026 Tracks\n`);
    for (const t of index.aggregations.theme) {
      console.log(`  ${t.key} — ${t.count} event(s)`);
    }
  } else {
    const tracks = Object.entries(index.byTrack)
      .filter(([_, ids]) => ids.length >= 5) // skip tags with very few events
      .sort((a, b) => b[1].length - a[1].length);

    console.log(`\nSXSW 2026 Tracks & Tags (${tracks.length} shown)\n`);
    for (const [track, ids] of tracks) {
      console.log(`  ${track} — ${ids.length} event(s)`);
    }
  }
}

function cmdToday(): void {
  const today = getTodayCST();
  console.log(`\nToday is ${fmtDateLong(today)} (Austin time)`);
  cmdEvents({ date: today, verbose: false });
}

function cmdTomorrow(): void {
  const tomorrow = getTomorrowCST();
  console.log(`\nTomorrow is ${fmtDateLong(tomorrow)} (Austin time)`);
  cmdEvents({ date: tomorrow, verbose: false });
}

function cmdRecommend(): void {
  const schedule = loadSchedule();
  const index = loadIndex();

  // Highlight keynotes, featured sessions, and popular formats
  const featured = schedule.events.filter(e =>
    e.format.toLowerCase().includes('keynote') ||
    e.format.toLowerCase().includes('featured session') ||
    e.format.toLowerCase().includes('fireside chat')
  );

  // Sort by date
  featured.sort((a, b) => {
    const dc = a.date.localeCompare(b.date);
    if (dc !== 0) return dc;
    return a.start_time.localeCompare(b.start_time);
  });

  printEvents(featured, {
    title: 'SXSW 2026 Must-See Events (Keynotes, Featured Sessions, Fireside Chats)',
    verbose: true,
  });

  // Also show format breakdown
  if (index.aggregations?.format) {
    console.log('\nAll event formats:');
    for (const f of index.aggregations.format) {
      console.log(`  ${f.key} — ${f.count}`);
    }
  }
}

function cmdInfo(): void {
  const schedule = loadSchedule();
  const index = loadIndex();

  console.log('\nSXSW 2026 Dataset Info');
  console.log(`  Scraped at: ${schedule.scraped_at}`);
  console.log(`  Total events: ${schedule.event_count}`);
  console.log(`  Date range: ${schedule.date_range.start} to ${schedule.date_range.end}`);
  console.log(`  Dates: ${Object.keys(index.byDate).length}`);
  console.log(`  Tracks: ${Object.keys(index.byTrack).length}`);
  console.log(`  Venues: ${Object.keys(index.byVenue).length}`);
  console.log(`  Formats: ${Object.keys(index.byFormat).length}`);
  console.log(`  Speakers: ${Object.keys(index.bySpeaker).length}`);
  console.log(`  Keywords indexed: ${Object.keys(index.keywords).length}`);

  console.log('\nEvents by date:');
  for (const [date, ids] of Object.entries(index.byDate).sort()) {
    console.log(`  ${fmtDate(date)} (${date}): ${ids.length} events`);
  }

  console.log('\nSXSW 2026 runs March 12-18 in Austin, TX');
  console.log('  Registrant pickup: Austin Convention Center');
  console.log('  Main venue areas: Austin Convention Center, JW Marriott, Hilton, Fairmont');
  console.log('  Music showcases: downtown bars and venues along 6th St, Red River, Rainey St');
}

// ── CLI entry point ─────────────────────────────────────────────────

const USAGE = `
SXSW 2026 Schedule CLI

Usage:
  sxsw.ts <command> [options]

Commands:
  events      List/search events
  speakers    List/search speakers
  venues      List all venues
  tracks      List all tracks/categories
  today       Show today's events
  tomorrow    Show tomorrow's events
  recommend   Highlight keynotes and featured sessions
  info        Show dataset info and key dates

Events options:
  --date <YYYY-MM-DD>   Filter by date
  --track <name>        Filter by track/category
  --venue <name>        Filter by venue
  --format <type>       Filter by format (keynote, panel, etc.)
  --search <query>      Full-text search
  --verbose             Show descriptions and speakers
  --limit <n>           Limit number of results

Speakers options:
  --search <name>       Search for a speaker by name

Examples:
  sxsw.ts events --date 2026-03-14
  sxsw.ts events --track "AI" --verbose
  sxsw.ts events --search "machine learning"
  sxsw.ts speakers --search "Amy Webb"
  sxsw.ts today
  sxsw.ts recommend
`.trim();

function main(): void {
  const { values, positionals } = parseArgs({
    allowPositionals: true,
    options: {
      date: { type: 'string' },
      track: { type: 'string' },
      venue: { type: 'string' },
      format: { type: 'string' },
      search: { type: 'string' },
      verbose: { type: 'boolean', default: false },
      limit: { type: 'string' },
      help: { type: 'boolean', short: 'h', default: false },
    },
  });

  const command = positionals[0];

  if (!command || values.help) {
    console.log(USAGE);
    process.exit(0);
  }

  const handlers: Record<string, () => void> = {
    events: () => cmdEvents(values),
    speakers: () => cmdSpeakers(values),
    venues: () => cmdVenues(),
    tracks: () => cmdTracks(),
    today: () => cmdToday(),
    tomorrow: () => cmdTomorrow(),
    recommend: () => cmdRecommend(),
    info: () => cmdInfo(),
  };

  const handler = handlers[command];
  if (!handler) {
    console.error(`Unknown command: ${command}`);
    console.error('Run with --help for usage info');
    process.exit(1);
  }

  handler();
}

Promise.resolve().then(main).catch(err => {
  console.error(`Error: ${(err as Error).message}`);
  process.exit(1);
});
