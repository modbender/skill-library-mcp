import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  parseCTATimestamp, parseCsvLine, haversine, localTzOffsetHours,
  fmtTime, fmtTimeHM, resolveTrainRoute, searchStation, STATIONS,
} from '../scripts/cta.mjs';

// ---------------------------------------------------------------------------
// parseCTATimestamp
// ---------------------------------------------------------------------------
describe('parseCTATimestamp', () => {
  it('parses Bus Tracker format (YYYYMMDD HH:MM)', () => {
    const d = parseCTATimestamp('20260221 14:30');
    assert.equal(d.getUTCHours(), 14);
    assert.equal(d.getUTCMinutes(), 30);
    assert.equal(d.getUTCFullYear(), 2026);
    assert.equal(d.getUTCMonth(), 1); // Feb = 1
    assert.equal(d.getUTCDate(), 21);
  });

  it('parses Bus Tracker format with seconds', () => {
    const d = parseCTATimestamp('20260221 14:30:45');
    assert.equal(d.getUTCSeconds(), 45);
  });

  it('parses Train Tracker ISO format (YYYY-MM-DDTHH:MM:SS)', () => {
    const d = parseCTATimestamp('2026-02-21T08:15:00');
    assert.equal(d.getUTCHours(), 8);
    assert.equal(d.getUTCMinutes(), 15);
    assert.equal(d.getUTCSeconds(), 0);
  });

  it('returns null for empty/null input', () => {
    assert.equal(parseCTATimestamp(null), null);
    assert.equal(parseCTATimestamp(''), null);
    assert.equal(parseCTATimestamp(undefined), null);
  });
});

// ---------------------------------------------------------------------------
// parseCsvLine
// ---------------------------------------------------------------------------
describe('parseCsvLine', () => {
  it('parses simple comma-separated values', () => {
    assert.deepEqual(parseCsvLine('a,b,c'), ['a', 'b', 'c']);
  });

  it('handles quoted fields with commas', () => {
    assert.deepEqual(parseCsvLine('"hello, world",b,c'), ['hello, world', 'b', 'c']);
  });

  it('handles escaped quotes (doubled)', () => {
    assert.deepEqual(parseCsvLine('"say ""hi""",b'), ['say "hi"', 'b']);
  });

  it('handles empty fields', () => {
    assert.deepEqual(parseCsvLine('a,,c'), ['a', '', 'c']);
  });

  it('handles single field', () => {
    assert.deepEqual(parseCsvLine('hello'), ['hello']);
  });
});

// ---------------------------------------------------------------------------
// haversine
// ---------------------------------------------------------------------------
describe('haversine', () => {
  it('returns 0 for same point', () => {
    assert.equal(haversine(41.8781, -87.6298, 41.8781, -87.6298), 0);
  });

  it('calculates distance between Chicago Loop and O\'Hare (~14-15 mi)', () => {
    const dist = haversine(41.8781, -87.6298, 41.9742, -87.9073);
    assert.ok(dist > 13 && dist < 16, `Expected ~14mi, got ${dist}`);
  });

  it('returns distance in miles', () => {
    // NYC to LA ~2450mi
    const dist = haversine(40.7128, -74.0060, 34.0522, -118.2437);
    assert.ok(dist > 2400 && dist < 2500, `Expected ~2450mi, got ${dist}`);
  });
});

// ---------------------------------------------------------------------------
// localTzOffsetHours
// ---------------------------------------------------------------------------
describe('localTzOffsetHours', () => {
  it('returns -5 or -6 (CDT or CST)', () => {
    const offset = localTzOffsetHours();
    assert.ok(offset === -5 || offset === -6, `Expected -5 or -6, got ${offset}`);
  });
});

// ---------------------------------------------------------------------------
// fmtTime / fmtTimeHM
// ---------------------------------------------------------------------------
describe('fmtTime', () => {
  it('formats morning time in 12-hour with seconds', () => {
    const d = new Date(Date.UTC(2026, 0, 1, 9, 5, 30));
    assert.equal(fmtTime(d), '9:05:30 AM');
  });

  it('formats afternoon time', () => {
    const d = new Date(Date.UTC(2026, 0, 1, 14, 30, 0));
    assert.equal(fmtTime(d), '2:30:00 PM');
  });

  it('formats midnight as 12 AM', () => {
    const d = new Date(Date.UTC(2026, 0, 1, 0, 0, 0));
    assert.equal(fmtTime(d), '12:00:00 AM');
  });

  it('formats noon as 12 PM', () => {
    const d = new Date(Date.UTC(2026, 0, 1, 12, 0, 0));
    assert.equal(fmtTime(d), '12:00:00 PM');
  });
});

describe('fmtTimeHM', () => {
  it('formats without seconds', () => {
    const d = new Date(Date.UTC(2026, 0, 1, 14, 30, 0));
    assert.equal(fmtTimeHM(d), '2:30 PM');
  });

  it('pads minutes to 2 digits', () => {
    const d = new Date(Date.UTC(2026, 0, 1, 9, 5, 0));
    assert.equal(fmtTimeHM(d), '9:05 AM');
  });
});

// ---------------------------------------------------------------------------
// resolveTrainRoute
// ---------------------------------------------------------------------------
describe('resolveTrainRoute', () => {
  it('returns canonical code for exact match', () => {
    assert.equal(resolveTrainRoute('Red'), 'Red');
    assert.equal(resolveTrainRoute('Brn'), 'Brn');
  });

  it('resolves aliases (case-insensitive)', () => {
    assert.equal(resolveTrainRoute('red'), 'Red');
    assert.equal(resolveTrainRoute('blue'), 'Blue');
    assert.equal(resolveTrainRoute('brown'), 'Brn');
    assert.equal(resolveTrainRoute('green'), 'G');
    assert.equal(resolveTrainRoute('orange'), 'Org');
    assert.equal(resolveTrainRoute('purple'), 'P');
  });

  it('returns null for empty input', () => {
    assert.equal(resolveTrainRoute(null), null);
    assert.equal(resolveTrainRoute(''), null);
  });

  it('passes through unknown input', () => {
    assert.equal(resolveTrainRoute('unknown'), 'unknown');
  });
});

// ---------------------------------------------------------------------------
// searchStation
// ---------------------------------------------------------------------------
describe('searchStation', () => {
  it('finds exact match by name', () => {
    const results = searchStation("Clark/Lake");
    assert.ok(results.length > 0);
    assert.equal(results[0].name, 'Clark/Lake');
  });

  it('finds by alias', () => {
    const results = searchStation('wrigley');
    assert.ok(results.length > 0);
    assert.equal(results[0].name, 'Addison (Red)');
  });

  it('finds by partial match', () => {
    const results = searchStation('ohare');
    assert.ok(results.length > 0);
    assert.equal(results[0].name, "O'Hare");
  });

  it('returns empty for gibberish', () => {
    const results = searchStation('zzzzxyzzy');
    assert.equal(results.length, 0);
  });

  it('filters by route', () => {
    const results = searchStation('belmont', 'Red');
    assert.ok(results.length > 0);
    assert.ok(results[0].lines.includes('Red'));
  });
});

// ---------------------------------------------------------------------------
// STATIONS data integrity
// ---------------------------------------------------------------------------
describe('STATIONS', () => {
  it('has no duplicate mapids', () => {
    const seen = new Map();
    for (const s of STATIONS) {
      if (seen.has(s.mapid)) {
        assert.fail(`Duplicate mapid ${s.mapid}: "${seen.get(s.mapid)}" and "${s.name}"`);
      }
      seen.set(s.mapid, s.name);
    }
  });

  it('all mapids are 5-digit strings starting with 4', () => {
    for (const s of STATIONS) {
      assert.match(s.mapid, /^4\d{4}$/, `Invalid mapid "${s.mapid}" for ${s.name}`);
    }
  });
});
