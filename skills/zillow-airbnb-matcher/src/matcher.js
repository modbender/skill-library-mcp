/**
 * Address matching engine
 * Handles the messy reality that "123 South Main St" and "123 S Main Street" are the same property
 */

const Fuse = require('fuse.js');

// Abbreviation maps for address normalization
const DIRECTION_MAP = {
  'north': 'n', 'south': 's', 'east': 'e', 'west': 'w',
  'northeast': 'ne', 'northwest': 'nw', 'southeast': 'se', 'southwest': 'sw'
};

const STREET_TYPE_MAP = {
  'avenue': 'ave', 'boulevard': 'blvd', 'circle': 'cir', 'court': 'ct',
  'drive': 'dr', 'highway': 'hwy', 'lane': 'ln', 'place': 'pl',
  'road': 'rd', 'square': 'sq', 'street': 'st', 'terrace': 'ter',
  'trail': 'trl', 'way': 'wy', 'expressway': 'expy', 'freeway': 'fwy',
  'parkway': 'pkwy', 'pike': 'pk'
};

// Unit/apt prefix normalization
const UNIT_PREFIXES = ['apt', 'apartment', 'unit', 'suite', 'ste', '#', 'no', 'num', 'number'];

/**
 * Normalize an address to a canonical form for comparison
 * e.g., "1847 South Congress Avenue, Unit 3" => "1847 s congress ave 3"
 */
function normalizeAddress(address) {
  if (!address) return '';

  let addr = address.toLowerCase().trim();

  // Remove commas, periods
  addr = addr.replace(/[.,]/g, ' ');

  // Normalize unit/apt designators
  UNIT_PREFIXES.forEach(prefix => {
    const regex = new RegExp(`\\b${prefix}\\s*`, 'g');
    addr = addr.replace(regex, '# ');
  });
  // Collapse multiple # markers
  addr = addr.replace(/#+\s*/g, '# ');

  // Expand or contract directional prefixes/suffixes
  const words = addr.split(/\s+/);
  const normalized = words.map(word => {
    const w = word.replace(/[^a-z0-9#]/g, '');
    return DIRECTION_MAP[w] || STREET_TYPE_MAP[w] || w;
  });

  addr = normalized.join(' ').trim();

  // Remove double spaces
  addr = addr.replace(/\s+/g, ' ');

  return addr;
}

/**
 * Extract the house number from an address
 */
function extractHouseNumber(address) {
  const match = address.match(/^(\d+)/);
  return match ? match[1] : null;
}

/**
 * Calculate address similarity score (0-1)
 * Weights house number match heavily (must match),
 * then fuzzy matches the rest
 */
function addressSimilarity(addr1, addr2) {
  const n1 = normalizeAddress(addr1);
  const n2 = normalizeAddress(addr2);

  if (n1 === n2) return 1.0;

  const num1 = extractHouseNumber(n1);
  const num2 = extractHouseNumber(n2);

  // House numbers MUST match for a valid address match
  if (num1 && num2 && num1 !== num2) return 0;
  if (!num1 || !num2) return 0;

  // Get the non-numeric parts for fuzzy matching
  const street1 = n1.replace(/^\d+\s*/, '').replace(/^#\s*\S+\s*/, '');
  const street2 = n2.replace(/^\d+\s*/, '').replace(/^#\s*\S+\s*/, '');

  // Levenshtein-based similarity
  const longer = street1.length > street2.length ? street1 : street2;
  const shorter = street1.length > street2.length ? street2 : street1;

  if (longer.length === 0) return 1.0;

  const editDist = levenshtein(longer, shorter);
  const similarity = (longer.length - editDist) / longer.length;

  return similarity;
}

/**
 * Haversine distance between two lat/lng points in meters
 */
function haversineDistance(lat1, lng1, lat2, lng2) {
  const R = 6371000; // Earth radius in meters
  const toRad = d => d * Math.PI / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a = Math.sin(dLat/2)**2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}

function levenshtein(s, t) {
  const m = s.length, n = t.length;
  const dp = Array.from({ length: m + 1 }, (_, i) =>
    Array.from({ length: n + 1 }, (_, j) => (i === 0 ? j : j === 0 ? i : 0))
  );
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = s[i - 1] === t[j - 1]
        ? dp[i - 1][j - 1]
        : 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
    }
  }
  return dp[m][n];
}

/**
 * Main matching function
 * Cross-references Zillow listings against Airbnb listings
 * Returns matched pairs with scores and investment metrics
 */
function matchListings(zillowListings, airbnbListings, options = {}) {
  const { minScore = 0.75, verbose = false } = options;

  const matches = [];
  const unmatchedZillow = [];
  const unmatchedAirbnb = [...airbnbListings]; // start with all, remove as matched

  // Build all candidate pairs with scores first
  const candidates = [];
  for (const zillow of zillowListings) {
    for (const airbnb of airbnbListings) {
      let score = addressSimilarity(zillow.address, airbnb.address);

      if (score < minScore && zillow.lat && zillow.lng && airbnb.lat && airbnb.lng) {
        const distMeters = haversineDistance(zillow.lat, zillow.lng, airbnb.lat, airbnb.lng);
        if (distMeters < 100) score = Math.max(score, 0.92);
        else if (distMeters < 200) score = Math.max(score, 0.82);
        else if (distMeters < 500) score = Math.max(score, 0.65);
      }

      if (verbose) {
        console.log(`  Comparing: "${zillow.address}" vs "${airbnb.address}" => ${(score * 100).toFixed(0)}%`);
      }

      if (score >= minScore) {
        candidates.push({ zillow, airbnb, score });
      }
    }
  }

  // Sort by score descending — best matches first
  candidates.sort((a, b) => b.score - a.score);

  // Greedy 1:1 matching — each Airbnb and each Zillow used only ONCE
  const usedZillow = new Set();
  const usedAirbnb = new Set();

  for (const { zillow, airbnb, score } of candidates) {
    const zKey = zillow.address || zillow.listingUrl;
    const aKey = airbnb.airbnbUrl || airbnb.address || airbnb.id;

    if (usedZillow.has(zKey) || usedAirbnb.has(aKey)) continue;

    usedZillow.add(zKey);
    usedAirbnb.add(aKey);

    const metrics = calculateInvestmentMetrics(zillow, airbnb);
    matches.push({ zillow, airbnb, matchScore: score, metrics });

    const idx = unmatchedAirbnb.findIndex(a => (a.airbnbUrl || a.address || a.id) === aKey);
    if (idx > -1) unmatchedAirbnb.splice(idx, 1);
  }

  // Collect unmatched Zillow listings
  for (const zillow of zillowListings) {
    const zKey = zillow.address || zillow.listingUrl;
    if (!usedZillow.has(zKey)) {
      unmatchedZillow.push(zillow);
    }
  }

  return {
    matches,
    unmatchedZillow,
    unmatchedAirbnb,
    summary: {
      total_zillow: zillowListings.length,
      total_airbnb: airbnbListings.length,
      matched: matches.length,
      match_rate: `${((matches.length / zillowListings.length) * 100).toFixed(0)}%`
    }
  };
}

/**
 * Calculate investment metrics for a matched property pair
 */
function calculateInvestmentMetrics(zillow, airbnb) {
  // Parse price if it's a string like "$824,000"
  let purchasePrice = zillow.price;
  if (typeof purchasePrice === 'string') {
    purchasePrice = parseInt(purchasePrice.replace(/[^0-9]/g, ''), 10) || 0;
  }
  const annualRevenue = airbnb.annual_revenue_est || 0;

  // If we don't have enough data, return partial metrics
  if (!purchasePrice || purchasePrice === 0) {
    return { _incomplete: true, reason: 'Missing purchase price' };
  }

  // Standard assumptions (can be configured)
  const ASSUMPTIONS = {
    downPaymentPct: 0.20,        // 20% down
    mortgageRate: 0.0725,        // 7.25% (2025 rate)
    mortgageTerm: 30,
    propertyTaxPct: 0.0185,      // 1.85% (TX average)
    insurancePct: 0.006,         // 0.6%
    maintenancePct: 0.01,        // 1% of value
    mgmtFeePct: 0.20,            // 20% property mgmt
    airbnbFeePct: 0.03,          // 3% Airbnb host fee
    vacancyReserve: 0.05,        // 5% vacancy buffer
  };

  const downPayment = purchasePrice * ASSUMPTIONS.downPaymentPct;
  const loanAmount = purchasePrice - downPayment;

  // Monthly mortgage (P&I)
  const monthlyRate = ASSUMPTIONS.mortgageRate / 12;
  const numPayments = ASSUMPTIONS.mortgageTerm * 12;
  const monthlyMortgage = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
    (Math.pow(1 + monthlyRate, numPayments) - 1);

  // Annual expenses
  const annualMortgage = monthlyMortgage * 12;
  const annualTax = purchasePrice * ASSUMPTIONS.propertyTaxPct;
  const annualInsurance = purchasePrice * ASSUMPTIONS.insurancePct;
  const annualMaintenance = purchasePrice * ASSUMPTIONS.maintenancePct;
  const annualMgmtFee = annualRevenue * ASSUMPTIONS.mgmtFeePct;
  const airbnbFees = annualRevenue * ASSUMPTIONS.airbnbFeePct;
  const vacancyReserve = annualRevenue * ASSUMPTIONS.vacancyReserve;

  const totalAnnualExpenses = annualMortgage + annualTax + annualInsurance +
    annualMaintenance + annualMgmtFee + airbnbFees + vacancyReserve;

  const annualNOI = annualRevenue - (annualTax + annualInsurance + annualMaintenance + annualMgmtFee + airbnbFees + vacancyReserve);
  const annualCashFlow = annualRevenue - totalAnnualExpenses;
  const monthlyCashFlow = annualCashFlow / 12;

  // GRM (Gross Rent Multiplier) - lower = better
  const grm = purchasePrice / annualRevenue;

  // Cap Rate (NOI / Purchase Price)
  const capRate = (annualNOI / purchasePrice) * 100;

  // Cash-on-Cash Return
  const cashOnCash = (annualCashFlow / downPayment) * 100;

  // Gross Yield
  const grossYield = (annualRevenue / purchasePrice) * 100;

  // Break-even occupancy needed to cover all expenses
  const breakEvenOccupancy = totalAnnualExpenses / (airbnb.nightly_rate * 365);

  return {
    purchasePrice,
    downPayment,
    monthlyMortgage: Math.round(monthlyMortgage),
    annualRevenue,
    monthlyRevenue: Math.round(annualRevenue / 12),
    totalAnnualExpenses: Math.round(totalAnnualExpenses),
    annualCashFlow: Math.round(annualCashFlow),
    monthlyCashFlow: Math.round(monthlyCashFlow),
    capRate: capRate.toFixed(2),
    cashOnCash: cashOnCash.toFixed(2),
    grossYield: grossYield.toFixed(2),
    grm: grm.toFixed(1),
    breakEvenOccupancy: `${(breakEvenOccupancy * 100).toFixed(0)}%`,
    currentOccupancy: `${(airbnb.occupancy_rate * 100).toFixed(0)}%`,
    isPositiveCashFlow: annualCashFlow > 0,
    investmentGrade: gradeInvestment(capRate, cashOnCash, airbnb.occupancy_rate, airbnb.avg_rating)
  };
}

function gradeInvestment(capRate, cashOnCash, occupancy, rating) {
  let score = 0;

  // Cap rate scoring (higher = better for investor)
  if (capRate >= 8) score += 3;
  else if (capRate >= 6) score += 2;
  else if (capRate >= 4) score += 1;

  // Cash-on-cash (higher = better)
  if (cashOnCash >= 10) score += 3;
  else if (cashOnCash >= 6) score += 2;
  else if (cashOnCash >= 3) score += 1;

  // Occupancy (higher = more reliable income)
  if (occupancy >= 0.85) score += 2;
  else if (occupancy >= 0.70) score += 1;

  // Track record
  if (rating >= 4.9) score += 1;
  else if (rating >= 4.7) score += 0.5;

  if (score >= 7) return { grade: 'A', label: '🟢 EXCELLENT', emoji: '🟢' };
  if (score >= 5) return { grade: 'B', label: '🟡 GOOD', emoji: '🟡' };
  if (score >= 3) return { grade: 'C', label: '🟠 FAIR', emoji: '🟠' };
  return { grade: 'D', label: '🔴 WEAK', emoji: '🔴' };
}

module.exports = { matchListings, normalizeAddress, addressSimilarity, calculateInvestmentMetrics };
