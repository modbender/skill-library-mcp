function toNum(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function toTs(v) {
  const t = Date.parse(v || "");
  return Number.isFinite(t) ? t : null;
}

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function priceOf(listing) {
  if (!listing) return null;
  if (listing.status === "for_rent") return toNum(listing.rent);
  return toNum(listing.price);
}

function normType(v) {
  return String(v || "").trim().toLowerCase();
}

function strIncludes(hay, needle) {
  return String(hay || "").toLowerCase().includes(String(needle || "").toLowerCase());
}

function haversineMiles(aLat, aLng, bLat, bLng) {
  const lat1 = toNum(aLat), lon1 = toNum(aLng), lat2 = toNum(bLat), lon2 = toNum(bLng);
  if ([lat1, lon1, lat2, lon2].some((x) => x == null)) return null;
  const R = 3958.8;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const s1 = Math.sin(dLat / 2);
  const s2 = Math.sin(dLon / 2);
  const a = s1 * s1 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * s2 * s2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function recencyDays(listing, nowMs = Date.now()) {
  const ts = toTs(listing?.soldDate || listing?.listedDate || listing?.sourceAsOf);
  if (!ts) return null;
  return Math.max(0, (nowMs - ts) / (24 * 3600 * 1000));
}

function recencyScore(listing, options = {}) {
  const days = recencyDays(listing, options.nowMs || Date.now());
  if (days == null) return 0;
  const recentWindow = toNum(options.recencyWindowDays) ?? 180;
  const score = 15 * (1 - clamp(days / recentWindow, 0, 1));
  return score;
}

function distanceScore(subject, listing, options = {}) {
  const miles = haversineMiles(subject?.lat, subject?.lng, listing?.lat, listing?.lng);
  if (miles == null) return 0;
  const maxMiles = toNum(options.maxDistanceMiles) ?? 5;
  return 15 * (1 - clamp(miles / maxMiles, 0, 1));
}

function statusTier(listing, intent) {
  const s = String(listing?.status || "").toLowerCase();
  if (intent === "rent") return s === "for_rent" ? 3 : 0;
  if (s === "sold") return 3;
  if (s === "pending" || s === "contingent") return 2;
  if (s === "for_sale") return 1;
  return 0;
}

export function buildSubjectFromListing(listing, overrides = {}) {
  return {
    address: overrides.address || listing?.address?.street || null,
    city: overrides.city || listing?.address?.city || null,
    zip: overrides.zip || listing?.address?.zip || null,
    beds: overrides.beds ?? listing?.beds ?? null,
    baths: overrides.baths ?? listing?.baths ?? null,
    sqft: overrides.sqft ?? listing?.sqft ?? null,
    homeType: overrides.homeType || listing?.homeType || null,
    schoolScore: overrides.schoolScore ?? listing?.schoolScore ?? null,
    status: overrides.status || listing?.status || null,
    lat: overrides.lat ?? listing?.lat ?? null,
    lng: overrides.lng ?? listing?.lng ?? null,
  };
}

export function similarityScore(subject, listing, options = {}) {
  let score = 0;

  if (!subject || !listing) return score;

  if (subject.city && listing.address?.city && normType(subject.city) === normType(listing.address.city)) {
    score += 30;
  }

  if (subject.homeType && listing.homeType && normType(subject.homeType) === normType(listing.homeType)) {
    score += 20;
  }

  if (subject.beds != null && listing.beds != null) {
    const d = Math.abs(Number(subject.beds) - Number(listing.beds));
    score += Math.max(0, 20 - d * 8);
  }

  if (subject.baths != null && listing.baths != null) {
    const d = Math.abs(Number(subject.baths) - Number(listing.baths));
    score += Math.max(0, 15 - d * 6);
  }

  if (subject.sqft != null && listing.sqft != null && Number(subject.sqft) > 0) {
    const ratio = Math.abs(Number(subject.sqft) - Number(listing.sqft)) / Number(subject.sqft);
    score += Math.max(0, 25 - ratio * 80);
  }

  score += recencyScore(listing, options);
  score += distanceScore(subject, listing, options);

  return score;
}

export function computeCompStats(comps = []) {
  const prices = comps.map((x) => toNum(x.compPrice)).filter((x) => x != null).sort((a, b) => a - b);
  if (!prices.length) {
    return {
      count: 0,
      min: null,
      max: null,
      median: null,
      p25: null,
      p75: null,
      avg: null,
    };
  }

  const pickQ = (q) => {
    const idx = Math.max(0, Math.min(prices.length - 1, Math.round((prices.length - 1) * q)));
    return prices[idx];
  };

  const avg = prices.reduce((a, b) => a + b, 0) / prices.length;
  return {
    count: prices.length,
    min: prices[0],
    max: prices[prices.length - 1],
    median: pickQ(0.5),
    p25: pickQ(0.25),
    p75: pickQ(0.75),
    avg: Math.round(avg),
  };
}

function confidenceGrade(subject, comps, stats) {
  const n = stats?.count || 0;
  if (!n) return "C";

  const sqft = toNum(subject?.sqft);
  const within15 = comps.filter((x) => {
    if (!sqft || !x?.listing?.sqft) return false;
    return Math.abs(x.listing.sqft - sqft) / sqft <= 0.15;
  }).length;

  if (n >= 6 && within15 >= Math.ceil(n * 0.6)) return "A";
  if (n >= 3) return "B";
  return "C";
}

export function findComparableListings(subject, listings = [], options = {}) {
  const limit = Number(options.limit || 10);
  const minScore = Number(options.minScore || 25);
  const intent = options.intent || (subject?.status === "for_rent" ? "rent" : "buy");
  const strict = options.strict || {};

  const filtered = (listings || [])
    .filter((l) => {
      if (!l) return false;
      if (!priceOf(l)) return false;
      if (subject?.city && l.address?.city && normType(subject.city) !== normType(l.address.city)) return false;
      if (subject?.address && l.address?.street && strIncludes(l.address.street, subject.address)) return false;

      if (strict.sameCityOrZip) {
        const cityMatch = subject?.city && l.address?.city && normType(subject.city) === normType(l.address.city);
        const zipMatch = subject?.zip && l.address?.zip && String(subject.zip) === String(l.address.zip);
        if (!cityMatch && !zipMatch) return false;
      }

      if (strict.homeTypeMatch && subject?.homeType && l.homeType && normType(subject.homeType) !== normType(l.homeType)) return false;
      if (strict.bedsExact && subject?.beds != null && l.beds != null && Number(subject.beds) !== Number(l.beds)) return false;

      if (strict.sqftPct != null && subject?.sqft != null && l.sqft != null && Number(subject.sqft) > 0) {
        const pct = Math.abs(Number(subject.sqft) - Number(l.sqft)) / Number(subject.sqft);
        if (pct > Number(strict.sqftPct)) return false;
      }

      if (strict.schoolScoreDelta != null && subject?.schoolScore != null && l.schoolScore != null) {
        if (Math.abs(Number(subject.schoolScore) - Number(l.schoolScore)) > Number(strict.schoolScoreDelta)) return false;
      }

      return statusTier(l, intent) > 0;
    })
    .map((l) => {
      const score = similarityScore(subject, l, options);
      const compPrice = priceOf(l);
      const ppsf = l.sqft && compPrice ? Math.round(compPrice / l.sqft) : null;
      const statusPriority = statusTier(l, intent);
      return { listing: l, similarityScore: score, compPrice, ppsf, statusPriority };
    })
    .filter((x) => x.similarityScore >= minScore)
    .sort((a, b) => (b.statusPriority - a.statusPriority) || (b.similarityScore - a.similarityScore))
    .slice(0, limit);

  const stats = computeCompStats(filtered);
  const confidence = confidenceGrade(subject, filtered, stats);
  return { subject, comps: filtered, stats, confidence };
}

export function findRecentSimilarPrices(subject, listings = [], options = {}) {
  return findComparableListings(subject, listings, {
    minScore: options.minScore ?? 30,
    limit: options.limit ?? 8,
    recencyWindowDays: options.recencyWindowDays ?? 180,
    maxDistanceMiles: options.maxDistanceMiles ?? 5,
    intent: options.intent,
    nowMs: options.nowMs,
    strict: options.strict,
  });
}
