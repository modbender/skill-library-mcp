#!/usr/bin/env node

/**
 * ClawFlight - Find flights with Starlink WiFi
 * V1: OpenClaw skill — Amadeus API backend
 * 
 * Usage:
 *   node clawflight.js search --from BKK --to LHR --date 2026-03-14 --priority wifi
 *   node clawflight.js airlines
 *   node clawflight.js save --flight UA123 --arrival 2026-03-15T14:30:00Z
 *   node clawflight.js rate --airline UA --speed 5 --reliability 4 --ease 5
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import axios from 'axios';
import { Command } from 'commander';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Paths
const PROJECT_ROOT = join(__dirname, '..');
const AIRLINES_FILE = join(PROJECT_ROOT, 'data', 'airlines.json');
const SAVED_FLIGHTS_FILE = join(PROJECT_ROOT, 'data', 'saved-flights.json');
const RATINGS_FILE = join(PROJECT_ROOT, 'data', 'ratings.json');
const TOKEN_CACHE_FILE = join(PROJECT_ROOT, 'data', '.amadeus-token.json');

// Config
const AMADEUS_CLIENT_ID = process.env.AMADEUS_CLIENT_ID;
const AMADEUS_CLIENT_SECRET = process.env.AMADEUS_CLIENT_SECRET;
const AMADEUS_BASE_URL = process.env.AMADEUS_ENV === 'production'
  ? 'https://api.amadeus.com'
  : 'https://test.api.amadeus.com';

if (!AMADEUS_CLIENT_ID || !AMADEUS_CLIENT_SECRET) {
  console.error('❌ Missing Amadeus credentials. Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET.');
  console.error('   Get a free key at: https://developers.amadeus.com/self-service');
  process.exit(1);
}

const AFFILIATE_ID = 'clawflight';

// ─── Amadeus Auth ────────────────────────────────────────────────────────────

async function getAmadeusToken() {
  // Check cache first
  if (existsSync(TOKEN_CACHE_FILE)) {
    try {
      const cached = JSON.parse(readFileSync(TOKEN_CACHE_FILE, 'utf-8'));
      if (cached.expires_at > Date.now() + 60000) {
        return cached.access_token;
      }
    } catch (e) { /* ignore */ }
  }

  // Fetch new token
  const response = await axios.post(
    `${AMADEUS_BASE_URL}/v1/security/oauth2/token`,
    new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: AMADEUS_CLIENT_ID,
      client_secret: AMADEUS_CLIENT_SECRET,
    }),
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );

  const token = {
    access_token: response.data.access_token,
    expires_at: Date.now() + (response.data.expires_in * 1000),
  };

  writeFileSync(TOKEN_CACHE_FILE, JSON.stringify(token));
  return token.access_token;
}

// ─── Data ─────────────────────────────────────────────────────────────────────

function loadAirlines() {
  const data = readFileSync(AIRLINES_FILE, 'utf-8');
  return JSON.parse(data);
}

function getStarlinkAirlinesMap() {
  const airlines = loadAirlines();
  const map = new Map();
  for (const a of airlines) map.set(a.id.toUpperCase(), a);
  return map;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatDuration(iso) {
  // PT7H30M → "7h 30m"
  const match = iso.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
  if (!match) return iso;
  const h = match[1] ? `${match[1]}h` : '';
  const m = match[2] ? ` ${match[2]}m` : '';
  return (h + m).trim();
}

function generateAffiliateLink(from, to, date, carrier) {
  // Skyscanner deep link (works without account, replace with affiliate tag once approved)
  const d = date?.replace(/-/g, '') || '';
  return `https://www.skyscanner.com/transport/flights/${from}/${to}/${d}/?adults=1&ref=clawflight`;
}

// ─── Search ───────────────────────────────────────────────────────────────────

async function searchFlights({ from, to, date, adults = 1, limit = 30 }) {
  const token = await getAmadeusToken();

  const response = await axios.get(
    `${AMADEUS_BASE_URL}/v2/shopping/flight-offers`,
    {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        originLocationCode: from.toUpperCase(),
        destinationLocationCode: to.toUpperCase(),
        departureDate: date,
        adults,
        max: limit,
        currencyCode: 'USD',
      },
    }
  );

  return response.data.data || [];
}

function filterStarlinkFlights(offers, starlinkMap) {
  return offers
    .filter(offer => {
      const carriers = new Set();
      offer.itineraries?.forEach(it =>
        it.segments?.forEach(seg => {
          carriers.add(seg.carrierCode?.toUpperCase());
          if (seg.operatingCarrierCode) carriers.add(seg.operatingCarrierCode.toUpperCase());
        })
      );
      // Flight qualifies if ANY carrier on it is Starlink
      return [...carriers].some(c => starlinkMap.has(c));
    })
    .map(offer => {
      const carriers = new Set();
      offer.itineraries?.forEach(it =>
        it.segments?.forEach(seg => {
          carriers.add(seg.carrierCode?.toUpperCase());
        })
      );

      const mainCarrier = [...carriers][0];
      const airlineData = starlinkMap.get(mainCarrier) || {};
      const score = airlineData.community_score || { speed: 0, reliability: 0, ease: 0 };
      const wifiScore = score.count > 0
        ? ((score.speed + score.reliability + score.ease) / 3).toFixed(1)
        : airlineData.wifi_score_seed || '4.0';

      const it = offer.itineraries[0];
      const firstSeg = it.segments[0];
      const lastSeg = it.segments[it.segments.length - 1];

      return {
        _offer: offer,
        _airlineData: airlineData,
        _carrierCode: mainCarrier,
        _wifiScore: wifiScore,
        price: parseFloat(offer.price?.total || 0),
        currency: offer.price?.currency || 'USD',
        duration: it.duration,
        departure: firstSeg.departure?.at,
        arrival: lastSeg.arrival?.at,
        stops: it.segments.length - 1,
        from: firstSeg.departure?.iataCode,
        fromCity: firstSeg.departure?.iataCode,
        to: lastSeg.arrival?.iataCode,
        toCity: lastSeg.arrival?.iataCode,
      };
    });
}

function rankFlights(flights, priority = 'wifi') {
  const ranked = [...flights];
  switch (priority) {
    case 'cheap':  ranked.sort((a, b) => a.price - b.price); break;
    case 'fast':   ranked.sort((a, b) => a.duration.localeCompare(b.duration)); break;
    case 'wifi':   ranked.sort((a, b) => parseFloat(b._wifiScore) - parseFloat(a._wifiScore)); break;
    case 'jetlag': {
      // Prefer flights that arrive at destination during daytime (10am-6pm local)
      ranked.sort((a, b) => {
        const aHour = new Date(a.arrival).getUTCHours();
        const bHour = new Date(b.arrival).getUTCHours();
        const aScore = 24 - Math.abs(14 - aHour);
        const bScore = 24 - Math.abs(14 - bHour);
        return bScore - aScore;
      });
      break;
    }
    default: ranked.sort((a, b) => a.price - b.price);
  }
  return ranked;
}

// ─── Display ──────────────────────────────────────────────────────────────────

function displayResults(flights, options = {}) {
  const { json = false } = options;

  if (flights.length === 0) {
    const msg = {
      found: 0,
      message: 'No Starlink-equipped flights found on this route.',
      tip: 'Best routes for Starlink: US domestic (UA, AS, WN), transatlantic (UA, AF), Middle East hub (QR).',
    };
    console.log(json
      ? JSON.stringify(msg, null, 2)
      : `\n❌ ${msg.message}\n💡 ${msg.tip}\n`);
    return;
  }

  if (json) {
    console.log(JSON.stringify(flights.slice(0, 5).map((f, i) => ({
      rank: i + 1,
      airline: f._airlineData.name || f._carrierCode,
      airline_code: f._carrierCode,
      wifi_type: 'Starlink',
      wifi_score: f._wifiScore,
      price: f.price,
      currency: f.currency,
      duration: formatDuration(f.duration),
      stops: f.stops,
      departure: f.departure,
      arrival: f.arrival,
      route: `${f.from} → ${f.to}`,
      booking_link: generateAffiliateLink(f.from, f.to, f.departure?.split('T')[0], f._carrierCode),
    })), null, 2));
    return;
  }

  console.log('\n🛫 ClawFlight — Starlink Flights\n' + '═'.repeat(55));

  for (let i = 0; i < Math.min(flights.length, 5); i++) {
    const f = flights[i];
    const dep = new Date(f.departure);
    const dateStr = dep.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const timeStr = dep.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const stopsStr = f.stops === 0 ? 'direct' : `${f.stops} stop${f.stops > 1 ? 's' : ''}`;
    const airlineName = f._airlineData.name || f._carrierCode;
    const fleetCoverage = f._airlineData.fleet_coverage_pct;
    const guarantee = fleetCoverage >= 80 ? '✅' : fleetCoverage >= 50 ? '⚠️' : '❓';

    console.log(`\n✈️  #${i + 1} — ${airlineName} ${guarantee} (Starlink ⭐ ${f._wifiScore})`);
    console.log(`    ${dateStr} ${timeStr} | ${formatDuration(f.duration)} | ${stopsStr}`);
    console.log(`    ${f.from} → ${f.to} | ${f.currency} ${f.price.toFixed(0)}`);
    if (fleetCoverage < 80) {
      console.log(`    ⚠️  Fleet coverage: ${fleetCoverage}% — not guaranteed on your aircraft`);
    }
    console.log(`    🔗 ${generateAffiliateLink(f.from, f.to, f.departure?.split('T')[0], f._carrierCode)}`);
  }

  console.log('\n' + '═'.repeat(55));
  console.log(`Found ${flights.length} Starlink-equipped flights. Showing top 5.\n`);
}

function listAirlines(options = {}) {
  const airlines = loadAirlines();
  const { json = false } = options;

  if (json) { console.log(JSON.stringify(airlines, null, 2)); return; }

  console.log('\n🛜 Starlink-Equipped Airlines (' + airlines.length + ')\n');
  console.log('═'.repeat(65));

  for (const a of airlines) {
    const s = a.community_score || {};
    const avg = (s.speed && s.reliability && s.ease)
      ? ((s.speed + s.reliability + s.ease) / 3).toFixed(1)
      : '—';
    const bar = '█'.repeat(Math.round(a.fleet_coverage_pct / 10)) + '░'.repeat(10 - Math.round(a.fleet_coverage_pct / 10));
    console.log(`\n${a.id.padEnd(6)} ${a.name}`);
    console.log(`   WiFi: ${a.wifi_type.toUpperCase()} | Fleet: ${bar} ${a.fleet_coverage_pct}% | Score: ⭐ ${avg}`);
    console.log(`   Regions: ${a.regions.join(', ')}`);
  }
  console.log('\n');
}

function saveFlight({ flightNumber, arrivalTime }) {
  let saved = [];
  if (existsSync(SAVED_FLIGHTS_FILE)) {
    try { saved = JSON.parse(readFileSync(SAVED_FLIGHTS_FILE, 'utf-8')); } catch (e) {}
  }
  const entry = {
    id: Date.now(),
    flight_number: flightNumber,
    arrival: arrivalTime,
    nudge_at: new Date(new Date(arrivalTime).getTime() + 6 * 60 * 60 * 1000).toISOString(),
    cron_scheduled: false,
    created_at: new Date().toISOString(),
  };
  saved.push(entry);
  writeFileSync(SAVED_FLIGHTS_FILE, JSON.stringify(saved, null, 2));
  console.log(`\n✅ Flight ${flightNumber} saved.`);
  console.log(`   Arrives: ${arrivalTime}`);
  console.log(`   Rating nudge at: ${entry.nudge_at}\n`);
}

function submitRating({ airline, speed, reliability, ease }) {
  let ratings = [];
  if (existsSync(RATINGS_FILE)) {
    try { ratings = JSON.parse(readFileSync(RATINGS_FILE, 'utf-8')); } catch (e) {}
  }
  ratings.push({
    id: Date.now(),
    airline_id: airline.toUpperCase(),
    speed: parseInt(speed),
    reliability: parseInt(reliability),
    ease: parseInt(ease),
    submitted_at: new Date().toISOString(),
  });
  writeFileSync(RATINGS_FILE, JSON.stringify(ratings, null, 2));
  console.log(`\n✅ Rating submitted for ${airline.toUpperCase()}`);
  console.log(`   Speed: ${speed}/5 | Reliability: ${reliability}/5 | Ease: ${ease}/5\n`);
}

// ─── CLI ──────────────────────────────────────────────────────────────────────

const program = new Command();

program
  .name('clawflight')
  .description('✈️  Find flights with Starlink WiFi — ClawFlight V1')
  .version('1.0.0');

program
  .command('search')
  .description('Search for Starlink-equipped flights')
  .requiredOption('-f, --from <code>', 'Origin IATA code (e.g., BKK, JFK)')
  .requiredOption('-t, --to <code>', 'Destination IATA code (e.g., LHR, LAX)')
  .requiredOption('-d, --date <date>', 'Departure date YYYY-MM-DD')
  .option('-p, --priority <type>', 'Priority: wifi|cheap|fast|jetlag', 'wifi')
  .option('-a, --adults <n>', 'Passengers', '1')
  .option('--json', 'Machine-readable JSON output')
  .action(async (opts) => {
    try {
      console.log(`\n🔍 Searching ${opts.from.toUpperCase()} → ${opts.to.toUpperCase()} on ${opts.date}...`);
      const offers = await searchFlights({
        from: opts.from, to: opts.to, date: opts.date, adults: parseInt(opts.adults),
      });
      const starlinkMap = getStarlinkAirlinesMap();
      const filtered = filterStarlinkFlights(offers, starlinkMap);
      const ranked = rankFlights(filtered, opts.priority);
      displayResults(ranked, { json: opts.json });
    } catch (err) {
      if (err.response) {
        console.error(`\n❌ API Error ${err.response.status}:`, JSON.stringify(err.response.data, null, 2));
      } else {
        console.error('\n❌ Error:', err.message);
      }
      process.exit(1);
    }
  });

program
  .command('airlines')
  .description('List all Starlink-equipped airlines in the database')
  .option('--json', 'JSON output')
  .action((opts) => listAirlines({ json: opts.json }));

program
  .command('save')
  .description('Save a flight to get a WiFi rating nudge 6h after landing')
  .requiredOption('-f, --flight <number>', 'Flight number e.g. UA123')
  .requiredOption('-a, --arrival <datetime>', 'Arrival ISO datetime e.g. 2026-03-15T14:30:00Z')
  .action((opts) => saveFlight({ flightNumber: opts.flight, arrivalTime: opts.arrival }));

program
  .command('rate')
  .description('Submit WiFi rating for a flight')
  .requiredOption('-a, --airline <code>', 'Airline IATA code e.g. UA')
  .requiredOption('-s, --speed <1-5>', 'Speed rating')
  .requiredOption('-r, --reliability <1-5>', 'Reliability rating')
  .requiredOption('-e, --ease <1-5>', 'Ease of connection rating')
  .action((opts) => submitRating(opts));

program.parse();
