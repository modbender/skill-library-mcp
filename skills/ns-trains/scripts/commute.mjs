#!/usr/bin/env node
/**
 * NS Commute Shortcut
 * Usage: node commute.mjs [--to-work | --to-home]
 * 
 * Configure via environment variables:
 *   NS_HOME_STATION - Your home station (e.g., "Almere Centrum")
 *   NS_WORK_STATION - Your work station (e.g., "Amsterdam Zuid")
 */

import { nsFetch, requireNsSubscriptionKey } from './ns-api.mjs';

const NS_SUBSCRIPTION_KEY = (() => {
  try { return requireNsSubscriptionKey(); }
  catch (e) { console.error(`❌ ${e.message}`); process.exit(1); }
})();

const BASE_URL = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/trips';

// Commute settings from environment
const COMMUTE = {
  home: process.env.NS_HOME_STATION || '',
  work: process.env.NS_WORK_STATION || ''
};

// NS_SUBSCRIPTION_KEY is validated at startup via requireNsSubscriptionKey()

const args = process.argv.slice(2);
const toWork = args.includes('--to-work') || args.includes('-w') || args.includes('work');
const toHome = args.includes('--to-home') || args.includes('-h') || args.includes('home');

if (!toWork && !toHome) {
  console.log(`
🚆 NS Commute Shortcut

Usage: node commute.mjs [direction]

Directions:
  --to-work, -w, work    Home → Work
  --to-home, -h, home    Work → Home

Configuration (environment variables):
  NS_SUBSCRIPTION_KEY        Your NS API subscription key (required)
  NS_HOME_STATION   Your home station (e.g., "Almere Centrum")
  NS_WORK_STATION   Your work station (e.g., "Amsterdam Zuid")

Examples:
  node commute.mjs --to-work
  node commute.mjs home
`);
  process.exit(1);
}

if (!COMMUTE.home || !COMMUTE.work) {
  console.error(`❌ Commute stations not configured

Set these environment variables:
  export NS_HOME_STATION="Your Home Station"
  export NS_WORK_STATION="Your Work Station"

Example:
  export NS_HOME_STATION="Utrecht Centraal"
  export NS_WORK_STATION="Amsterdam Zuid"
`);
  process.exit(1);
}

const from = toWork ? COMMUTE.home : COMMUTE.work;
const to = toWork ? COMMUTE.work : COMMUTE.home;
const direction = toWork ? '🏢 To Work' : '🏠 To Home';

async function planCommute() {
  const params = new URLSearchParams({
    fromStation: from,
    toStation: to,
    searchForArrival: 'false'
  });

  try {
    const res = await nsFetch(`${BASE_URL}?${params}`, {
      subscriptionKey: NS_SUBSCRIPTION_KEY,
    });

    if (!res.ok) {
      console.error(`❌ API Error: ${res.status}`);
      process.exit(1);
    }

    const data = await res.json();
    const trips = data.trips || [];

    if (trips.length === 0) {
      console.log('❌ No trips found');
      process.exit(0);
    }

    console.log(`\n${direction}: ${from} → ${to}`);
    console.log('═'.repeat(50));

    trips.slice(0, 5).forEach((trip, i) => {
      const legs = trip.legs || [];
      const firstLeg = legs[0];
      const lastLeg = legs[legs.length - 1];
      if (!firstLeg || !lastLeg) return;

      const dep = new Date(firstLeg.origin?.plannedDateTime);
      const arr = new Date(lastLeg.destination?.plannedDateTime);
      const duration = trip.plannedDurationInMinutes || Math.round((arr - dep) / 60000);

      const depTime = dep.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
      const arrTime = arr.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });

      const depDelay = firstLeg.origin?.actualDateTime ?
        Math.round((new Date(firstLeg.origin.actualDateTime) - dep) / 60000) : 0;
      const delayStr = depDelay > 0 ? ` (+${depDelay})` : '';

      const transfers = trip.transfers || 0;
      const platform = firstLeg.origin?.plannedTrack || '?';
      const status = trip.status === 'NORMAL' ? '✅' : '⚠️';

      const crowd = firstLeg.crowdForecast || 'UNKNOWN';
      const crowdEmoji = { 'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴' }[crowd] || '⚪';

      console.log(`\n${status} ${depTime}${delayStr} → ${arrTime} (${duration} min)`);
      console.log(`   🔄 ${transfers} transfers | 🚏 Spoor ${platform} | ${crowdEmoji} ${crowd.toLowerCase()}`);

      if (trip.messages?.length > 0) {
        trip.messages.forEach(m => m.text && console.log(`   ⚠️  ${m.text}`));
      }
    });

    console.log('\n' + '─'.repeat(50));
    console.log(`⏱️  ${new Date().toLocaleTimeString('nl-NL')}`);

  } catch (err) {
    console.error(`❌ Error: ${err.message}`);
    process.exit(1);
  }
}

planCommute();
