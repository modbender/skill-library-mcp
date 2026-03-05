#!/usr/bin/env node
/**
 * Zillow × Airbnb Matcher — Chat Output Script
 * Designed for Alfred (OpenClaw) → Telegram/chat output
 *
 * Usage:
 *   node scripts/search.js --demo
 *   node scripts/search.js --zip 78704
 *   node scripts/search.js --city "Nashville, TN"
 *   node scripts/search.js --demo --commercial
 *   node scripts/search.js --zip 78704 --max-price 800000
 *
 * OUTPUT: Plain text, emoji-friendly, NO box-drawing chars, safe for Telegram
 */

// Load dependencies (run 'npm install' or 'bash scripts/install.sh' first)
const path = require('path');
const fs = require('fs');
const skillDir = path.join(__dirname, '..');

if (!fs.existsSync(path.join(skillDir, 'node_modules', 'dotenv'))) {
  console.error('❌ Dependencies not installed. Run: bash scripts/install.sh');
  process.exit(1);
}

// Load .env ONLY from skill directory
const envPath = path.join(__dirname, '../.env');
if (fs.existsSync(envPath)) {
  require('dotenv').config({ path: envPath });
}

const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');
const { matchListings } = require('../src/matcher');
const { DEMO_ZILLOW_LISTINGS, DEMO_AIRBNB_LISTINGS, DEMO_COMMERCIAL_ZILLOW } = require('../src/demo-data');

// ─── CLI --------------------------------------------------────────────────────

const argv = yargs(hideBin(process.argv))
  .option('demo', { type: 'boolean', default: false, description: 'Run with Austin TX sample data (no API needed)' })
  .option('zip', { type: 'string', description: 'ZIP code to search' })
  .option('city', { type: 'string', description: 'City to search (e.g. "Nashville, TN")' })
  .option('commercial', { type: 'boolean', default: false, description: 'Show commercial properties too' })
  .option('max-price', { type: 'number', description: 'Max purchase price filter' })
  .option('min-price', { type: 'number', description: 'Min purchase price filter' })
  .option('min-beds', { type: 'number', description: 'Minimum bedrooms' })
  .option('min-score', { type: 'number', default: 0.75, description: 'Match confidence (0-1)' })
  .argv;

// ─── Main --------------------------------------------------───────────────────

async function main() {
  const isDemo = argv.demo;
  const location = argv.zip || argv.city;

  // No args — check if setup is needed, then show help
  if (!isDemo && !location) {
    if (!process.env.RAPIDAPI_KEY) {
      printSetupGuide();
      process.exit(0);
    }
    printHelp();
    process.exit(0);
  }

  // Live search without API key — show setup guide
  if (!isDemo && !process.env.RAPIDAPI_KEY) {
    printSetupGuide();
    process.exit(1);
  }

  let zillowListings, airbnbListings;

  if (isDemo) {
    zillowListings = applyFilters(DEMO_ZILLOW_LISTINGS, argv);
    airbnbListings = DEMO_AIRBNB_LISTINGS;

  } else {
    // Live mode — requires API keys
    const { fetchZillowListings } = require('../src/zillow');
    const { fetchAirbnbListings } = require('../src/airbnb');

    try {
      process.stderr.write('Fetching Zillow listings...\n');
      zillowListings = await fetchZillowListings(location, {
        minPrice: argv['min-price'],
        maxPrice: argv['max-price'],
        beds: argv['min-beds']
      });
      zillowListings = applyFilters(zillowListings, argv);
      process.stderr.write(`Found ${zillowListings.length} Zillow listings\n`);
    } catch (err) {
      console.log(`❌ Could not fetch Zillow data: ${err.message}`);
      console.log('');
      console.log('💡 Try running with --demo to test the tool first:');
      console.log('   node scripts/search.js --demo');
      process.exit(1);
    }

    try {
      process.stderr.write('Fetching Airbnb listings...\n');
      airbnbListings = await fetchAirbnbListings(location);
      process.stderr.write(`Found ${airbnbListings.length} Airbnb listings\n`);
    } catch (err) {
      console.log(`❌ Could not fetch Airbnb data: ${err.message}`);
      console.log('');
      console.log('💡 Try running with --demo to test the tool first:');
      console.log('   node scripts/search.js --demo');
      process.exit(1);
    }
  }

  // Run matching
  const results = matchListings(zillowListings, airbnbListings, {
    minScore: argv['min-score']
  });

  // Print chat-friendly report
  const locationLabel = isDemo
    ? 'Austin TX 78704 (demo)'
    : (argv.zip ? `ZIP ${argv.zip}` : argv.city);

  printChatReport(results, locationLabel, isDemo);

  // Commercial add-on
  if (argv.commercial && isDemo) {
    printCommercialReport();
  }
}

// ─── Chat Report (Telegram-friendly) -------------------------────────────────

function printChatReport(results, location, isDemo) {
  const { matches, unmatchedZillow, summary } = results;
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  // Header
  console.log(`🏠 Property Match Report — ${location}`);
  if (isDemo) {
    console.log(`⚠️ DEMO MODE — showing Austin TX sample data`);
  }
  console.log(`📅 ${dateStr}`);
  console.log('');

  // Summary line
  const positiveCount = matches.filter(m => m.metrics.isPositiveCashFlow).length;
  const gradeACount = matches.filter(m => m.metrics.investmentGrade.grade === 'A').length;

  if (matches.length === 0) {
    console.log(`❌ No matches found out of ${summary.total_zillow} listings`);
    console.log('');
    console.log('Try a different ZIP or city with more STR activity.');
    console.log('Popular STR markets: 78704 (Austin), 33139 (Miami Beach), 37203 (Nashville)');
    return;
  }

  console.log(`✅ Found ${matches.length} match${matches.length !== 1 ? 'es' : ''} out of ${summary.total_zillow} listings`);
  console.log(`💰 ${positiveCount} positive cash flow | ⭐ ${gradeACount} Grade A`);
  console.log('');
  console.log('-------------------------');
  console.log('');

  // Sort by grade then CoC
  const sorted = [...matches].sort((a, b) => {
    const gradeOrder = { A: 0, B: 1, C: 2, D: 3 };
    const ga = gradeOrder[a.metrics.investmentGrade.grade] || 3;
    const gb = gradeOrder[b.metrics.investmentGrade.grade] || 3;
    if (ga !== gb) return ga - gb;
    return parseFloat(b.metrics.cashOnCash) - parseFloat(a.metrics.cashOnCash);
  });

  // Property cards
  sorted.forEach((match, idx) => {
    printPropertyCard(match, idx + 1);
  });

  // Summary footer
  printSummaryFooter(sorted, summary, unmatchedZillow.length);
}

function printPropertyCard(match, num) {
  const { zillow, airbnb, matchScore, metrics } = match;
  const grade = metrics.investmentGrade;

  // Grade label
  const gradeEmoji = grade.grade === 'A' ? '🟢' :
                     grade.grade === 'B' ? '🟡' :
                     grade.grade === 'C' ? '🟠' : '🔴';

  const gradeLabel = grade.grade === 'A' ? 'EXCELLENT' :
                     grade.grade === 'B' ? 'GOOD' :
                     grade.grade === 'C' ? 'FAIR' : 'WEAK';

  // Address cleanup
  const address = zillow.address;
  const cityState = `${zillow.city} ${zillow.state}`;

  // Handle incomplete metrics
  const hasMetrics = metrics && !metrics._incomplete && !isNaN(metrics.monthlyCashFlow);
  
  // Cash flow display
  const cfSign = hasMetrics && metrics.monthlyCashFlow >= 0 ? '+' : '-';
  const annualSign = hasMetrics && metrics.annualCashFlow >= 0 ? '+' : '-';
  const cfLabel = hasMetrics ? `${cfSign}$${Math.abs(metrics.monthlyCashFlow).toLocaleString()}/mo` : 'N/A';

  // Occupancy
  const occupancy = airbnb.occupancy_rate ? (airbnb.occupancy_rate * 100).toFixed(0) : '~70 (est)';

  console.log(`${gradeEmoji} #${num} ${gradeLabel} — ${address}`);
  console.log(`📍 ${cityState} ${zillow.zip} | ${zillow.propertyType}`);
  const priceDisplay = typeof zillow.price === 'number' ? `$${zillow.price.toLocaleString()}` : (zillow.price || 'N/A');
  console.log(`💰 ${priceDisplay} | ${zillow.beds || '?'}bd/${zillow.baths || '?'}ba | ${zillow.sqft?.toLocaleString() || '?'} sqft`);
  console.log(`📅 ${zillow.daysOnMarket} days on market | Built ${zillow.yearBuilt || 'N/A'}`);
  console.log('');
  const ratingDisplay = airbnb.avg_rating ? `⭐ ${airbnb.avg_rating}` : '⭐ N/A';
  console.log(`🌙 Airbnb: $${(airbnb.monthly_revenue_avg || 0).toLocaleString()}/mo avg | ${ratingDisplay} (${airbnb.total_reviews || 0} reviews)`);
  console.log(`📊 Occupancy: ${occupancy}% | ${airbnb.host_status || 'Regular'} | ${airbnb.active_months || '?'} months of history`);
  console.log(`📆 Peak season: ${airbnb.peak_season || 'Year-round'}`);
  console.log('');
  if (hasMetrics) {
    console.log(`📈 Cap Rate: ${metrics.capRate}% | CoC: ${metrics.cashOnCash}% | GRM: ${metrics.grm}x`);
    console.log(`💵 Cash Flow: ${cfLabel} | Annual: ${annualSign}$${Math.abs(metrics.annualCashFlow).toLocaleString()}/yr`);
    console.log(`🏦 Mortgage: $${metrics.monthlyMortgage.toLocaleString()}/mo | Down: $${metrics.downPayment.toLocaleString()}`);
    console.log(`🎯 Break-even occupancy: ${metrics.breakEvenOccupancy} (currently at ${occupancy}%)`);
  } else if (airbnb.nightly_rate) {
    console.log(`💵 Est. nightly rate: $${airbnb.nightly_rate}/night | ~$${airbnb.monthly_revenue_avg?.toLocaleString() || '?'}/mo (at 70% occ)`);
  } else {
    console.log(`💵 Revenue data unavailable — check Airbnb listing for pricing`);
  }

  // Low/high monthly range if available
  if (airbnb.lowest_month_revenue && airbnb.highest_month_revenue) {
    console.log(`📉 Revenue range: $${airbnb.lowest_month_revenue.toLocaleString()} (slow) → $${airbnb.highest_month_revenue.toLocaleString()} (peak)`);
  }

  // Links
  if (zillow.listingUrl && !zillow.listingUrl.includes('undefined')) {
    console.log(`🔗 Zillow: ${zillow.listingUrl}`);
  }
  if (airbnb.airbnbUrl && !airbnb.airbnbUrl.includes('undefined')) {
    console.log(`🔗 Airbnb: ${airbnb.airbnbUrl}`);
  }

  console.log('');
  console.log('-------------------------');
  console.log('');
}

function printSummaryFooter(sorted, summary, unmatchedCount) {
  const positiveCount = sorted.filter(m => m.metrics.isPositiveCashFlow).length;
  const gradeACount = sorted.filter(m => m.metrics.investmentGrade.grade === 'A').length;

  console.log(`📋 Summary: ${positiveCount} positive cash flow, ${gradeACount} Grade A`);

  if (unmatchedCount > 0) {
    console.log(`ℹ️ ${unmatchedCount} listing${unmatchedCount !== 1 ? 's' : ''} on Zillow with no active Airbnb match`);
  }

  // Pick best bet by: highest CoC among positive cash flow, or highest CoC overall
  const positiveCF = sorted.filter(m => m.metrics.isPositiveCashFlow);
  const best = (positiveCF.length > 0 ? positiveCF : sorted)
    .sort((a, b) => parseFloat(b.metrics.cashOnCash) - parseFloat(a.metrics.cashOnCash))[0];

  if (best) {
    const shortAddr = best.zillow.address.replace(/,.*/, ''); // trim after comma
    const annualRev = best.metrics?.annualRevenue || best.airbnb.annual_revenue_est || 0;
    const annualRevK = (annualRev / 1000).toFixed(0);
    const occ = best.airbnb.occupancy_rate ? `${(best.airbnb.occupancy_rate * 100).toFixed(0)}%` : '~70% (est)';
    const coc = best.metrics?.cashOnCash && !isNaN(best.metrics.cashOnCash) ? `${best.metrics.cashOnCash}%` : 'N/A';
    console.log('');
    console.log(`🏆 Best bet: ${shortAddr} — $${annualRevK}K/yr revenue`);
    console.log(`   ${best.airbnb.total_reviews || '?'} reviews | ${occ} occupancy | ${coc} CoC`);
  }

  console.log('');
  console.log('📌 Next steps:');
  console.log('   1. Check STR permits in this ZIP (google "short term rental rules [city]")');
  console.log('   2. Verify Airbnb revenue with host directly (message through listing)');
  console.log('   3. Run sensitivity: what if occupancy drops to 65%?');
  console.log('   4. Check HOA rules — many condos ban short-term rentals');
}

// ─── Commercial Report --------------------------------------------------──────

function printCommercialReport() {
  console.log('');
  console.log('🏢 Commercial Properties (Crexi / LoopNet)');
  console.log('⚠️ DEMO MODE — Sample commercial listings');
  console.log('');
  console.log('-------------------------');
  console.log('');

  DEMO_COMMERCIAL_ZILLOW.forEach((prop, idx) => {
    console.log(`🏢 #${idx + 1} — ${prop.address}`);
    console.log(`📍 ${prop.city}, ${prop.state} ${prop.zip}`);
    console.log(`🏗️ ${prop.propertyType} | ${prop.sqft?.toLocaleString()} sqft | Built ${prop.yearBuilt}`);
    console.log(`💰 $${prop.price.toLocaleString()}`);
    if (prop.capRate) console.log(`📈 Cap Rate: ${prop.capRate}% (seller-stated)`);
    if (prop.units) console.log(`🏠 ${prop.units} potential STR units`);
    console.log(`🗂️ Zoning: ${prop.zoning} | Source: ${prop.source}`);
    console.log(`📅 ${prop.daysOnMarket} days on market`);
    console.log(`🔗 ${prop.listingUrl}`);
    console.log('');
    console.log('-------------------------');
    console.log('');
  });

  console.log('💡 Commercial STR Tips:');
  console.log('   Multi-family (5+ units): Check unit-level Airbnb activity');
  console.log('   Mixed-use: Great for STR arbitrage (rent unit, sublet as Airbnb)');
  console.log('   Best data source: AirDNA market reports for your target city');
  console.log('   Commercial data: CoStar, Crexi, LoopNet for commercial property intel');
}

// ─── Help --------------------------------------------------───────────────────

function printSetupGuide() {
  console.log('🏠 Zillow × Airbnb Matcher — Setup Required');
  console.log('');
  console.log('You need a free RapidAPI key to search live data.');
  console.log('Takes 2 minutes, no credit card needed:');
  console.log('');
  console.log('1️⃣ Go to https://rapidapi.com and sign up (free)');
  console.log('2️⃣ Subscribe to these 2 free APIs:');
  console.log('   • Airbnb: https://rapidapi.com/3b-data-3b-data-default/api/airbnb13');
  console.log('   • Zillow: https://rapidapi.com/apimaker/api/zillow-com1');
  console.log('3️⃣ Copy your API key (find it on any API page, top right)');
  console.log('4️⃣ Add it to your .env file:');
  console.log(`   echo "RAPIDAPI_KEY=your_key_here" >> ${path.join(__dirname, '../.env')}`);
  console.log('');
  console.log('💡 While you set that up, try the demo:');
  console.log('   "airbnb demo"');
  console.log('');
  console.log('💰 Pricing:');
  console.log('   FREE: 100 Airbnb + 600 Zillow searches/month (~3 searches/day)');
  console.log('   Basic ($10/mo each): 1,000 Airbnb + 5,000 Zillow searches');
  console.log('   Each search uses 1 Airbnb + 1 Zillow request = 2 total');
}

function printHelp() {
  console.log('🏠 Zillow x Airbnb Property Matcher');
  console.log('');
  console.log('Usage:');
  console.log('  node scripts/search.js --demo                    Demo with Austin TX data');
  console.log('  node scripts/search.js --zip 78704               Live search by ZIP');
  console.log('  node scripts/search.js --city "Nashville, TN"    Live search by city');
  console.log('  node scripts/search.js --demo --commercial       Include commercial');
  console.log('');
  console.log('Filters:');
  console.log('  --max-price 800000   Max purchase price');
  console.log('  --min-price 300000   Min purchase price');
  console.log('  --min-beds 2         Minimum bedrooms');
  console.log('');
  console.log('Live mode requires RAPIDAPI_KEY in .env');
  console.log('Get a free key at: https://rapidapi.com');
  console.log('');
  console.log('See GUIDE.md for full setup instructions.');
}

// ─── Helpers --------------------------------------------------────────────────

function applyFilters(listings, argv) {
  return listings.filter(l => {
    if (argv['min-price'] && l.price < argv['min-price']) return false;
    if (argv['max-price'] && l.price > argv['max-price']) return false;
    if (argv['min-beds'] && l.beds < argv['min-beds']) return false;
    return true;
  });
}

// ─── Run --------------------------------------------------────────────────────

main().catch(err => {
  console.log(`❌ Error: ${err.message}`);
  process.exit(1);
});
