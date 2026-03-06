#!/usr/bin/env node
/**
 * NS Station Arrivals
 * Usage: node arrivals.mjs --station "Station Name"
 */

import { nsFetch, requireNsSubscriptionKey } from './ns-api.mjs';

const NS_SUBSCRIPTION_KEY = (() => {
  try { return requireNsSubscriptionKey(); }
  catch (e) { console.error(`❌ ${e.message}`); process.exit(1); }
})();

const STATIONS_URL = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/stations';
const ARRIVALS_URL = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/arrivals';

const args = process.argv.slice(2);
const getArg = (flag) => {
  const idx = args.indexOf(flag);
  return idx !== -1 ? args[idx + 1] : null;
};

const station = getArg('--station') || getArg('-s');
const limit = parseInt(getArg('--limit') || '10');

if (!station) {
  console.log(`
🚉 NS Station Arrivals

Usage: node arrivals.mjs --station "Station Name" [--limit 10]

Examples:
  node arrivals.mjs --station "Amsterdam Zuid"
  node arrivals.mjs -s "Almere Centrum" --limit 5
`);
  process.exit(1);
}

async function getStationCode(name) {
  const res = await nsFetch(`${STATIONS_URL}?q=${encodeURIComponent(name)}`, {
    subscriptionKey: NS_SUBSCRIPTION_KEY,
  });
  const data = await res.json();
  return data.payload?.[0]?.code || null;
}

async function getArrivals() {
  try {
    // Resolve station name to code
    const code = await getStationCode(station);
    if (!code) {
      console.error(`❌ Station not found: ${station}`);
      process.exit(1);
    }

    const res = await nsFetch(`${ARRIVALS_URL}?station=${code}&maxJourneys=${limit}`, {
      subscriptionKey: NS_SUBSCRIPTION_KEY,
    });

    if (!res.ok) {
      console.error(`❌ API Error: ${res.status}`);
      process.exit(1);
    }

    const data = await res.json();
    const arrivals = data.payload?.arrivals || [];

    if (arrivals.length === 0) {
      console.log(`❌ No arrivals found for "${station}"`);
      process.exit(0);
    }

    console.log(`\n🚉 Arrivals at ${station}`);
    console.log('═'.repeat(50));

    arrivals.forEach(arr => {
      const planned = new Date(arr.plannedDateTime);
      const actual = arr.actualDateTime ? new Date(arr.actualDateTime) : planned;
      const delay = Math.round((actual - planned) / 60000);

      const time = planned.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
      const delayStr = delay > 0 ? ` (+${delay})` : '';
      const status = arr.cancelled ? '❌' : (delay > 0 ? '⚠️' : '✅');

      const origin = arr.origin || 'Unknown';
      const platform = arr.actualTrack || arr.plannedTrack || '?';
      const trainType = arr.product?.shortCategoryName || '?';

      console.log(`\n${status} ${time}${delayStr} ← ${origin}`);
      console.log(`   🚆 ${trainType} | 🚏 Platform ${platform}`);

      if (arr.cancelled) console.log(`   ❌ CANCELLED`);
    });

    console.log('\n' + '─'.repeat(50));
    console.log(`⏱️  Updated: ${new Date().toLocaleTimeString('nl-NL')}`);

  } catch (err) {
    console.error(`❌ Error: ${err.message}`);
    process.exit(1);
  }
}

getArrivals();
