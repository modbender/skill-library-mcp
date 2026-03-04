import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const DATA_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../data");
const SAMPLE_BUY = path.join(DATA_DIR, "sample_redfin_buy.json");
const SAMPLE_RENT = path.join(DATA_DIR, "sample_redfin_rent.json");
const LIVE_RENT = path.join(DATA_DIR, "live_redfin_rent.json");
const LIVE_SOLD = path.join(DATA_DIR, "live_redfin_sold.json");

const CITY_REGION = {
  "mountain view": 12739,
  "cupertino": 4239,
  "los altos": 10854,
  "sunnyvale": 19457,
  "palo alto": 14325,
};

const CITY_DRIVE_MIN = {
  "mountain view": 12,
  "cupertino": 20,
  "los altos": 16,
  "sunnyvale": 18,
  "palo alto": 20,
};

const CITY_DRIVE_MIN_OPENAI_MTV = {
  "mountain view": 8,
  "cupertino": 22,
  "los altos": 16,
  "sunnyvale": 16,
  "palo alto": 18,
};

const CITY_SCHOOL_SCORE_EST = {
  "mountain view": 8.5,
  "cupertino": 9.2,
  "los altos": 9.1,
  "sunnyvale": 8.7,
  "palo alto": 9.4,
};

function normalizeHomeType(v, address = "", url = "") {
  const s = (v || "").toString().toLowerCase();
  const addr = String(address || "").toLowerCase();
  const u = String(url || "").toLowerCase();

  if (s.includes("town")) return "townhouse";
  if (s.includes("condo")) return "condo";

  // Guard against mislabeled sold/cache rows where unit-style homes are tagged
  // as "Single Family Residential".
  const hasUnitSignal = /\b(unit|#|apt|suite|ste|townhome|townhouse|condo)\b/i.test(addr) || /\/condo\/|\/townhouse\//i.test(u);
  if (s.includes("single")) return hasUnitSignal ? "townhouse" : "single_family";

  if (!s && hasUnitSignal) return "townhouse";
  return s || "unknown";
}

function parseNum(v) {
  if (v == null) return null;
  const n = Number(String(v).replace(/[^0-9.-]/g, ""));
  return Number.isFinite(n) ? n : null;
}

function parseAddressLine(line = "") {
  // e.g. "331 Carolina Ln, Palo Alto, CA 94306"
  const m = String(line).match(/^(.*?),\s*([^,]+),\s*CA\s*(\d{5})/i);
  if (!m) return { street: line || "", city: "", state: "CA", zip: "" };
  return { street: m[1].trim(), city: m[2].trim(), state: "CA", zip: m[3] };
}

function parseBeds(v) {
  const s = String(v || "");
  const m = s.match(/(\d+(?:\.\d+)?)/);
  return m ? Number(m[1]) : null;
}

function parseCsvLine(line) {
  const out = [];
  let cur = "";
  let q = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (q && line[i + 1] === '"') { cur += '"'; i++; continue; }
      q = !q;
      continue;
    }
    if (ch === "," && !q) {
      out.push(cur);
      cur = "";
      continue;
    }
    cur += ch;
  }
  out.push(cur);
  return out;
}

function fromCsvRows(text) {
  const lines = String(text || "").split(/\r?\n/).filter(Boolean);
  const csvStart = lines.findIndex((x) => x.startsWith("SALE TYPE,"));
  if (csvStart < 0) return [];
  const rows = [];
  for (let i = csvStart + 1; i < lines.length; i++) {
    const ln = lines[i];
    if (!ln.startsWith("MLS Listing")) continue;
    const c = parseCsvLine(ln);
    rows.push({
      saleType: c[0],
      propertyType: c[2],
      address: c[3],
      city: c[4],
      state: c[5],
      zip: c[6],
      price: parseNum(c[7]),
      beds: parseNum(c[8]),
      baths: parseNum(c[9]),
      sqft: parseNum(c[11]),
      lotSize: parseNum(c[12]),
      yearBuilt: parseNum(c[13]),
      daysOnRedfin: parseNum(c[14]),
      status: c[17],
      url: c[20],
      source: c[21],
      mls: c[22],
      lat: parseNum(c[25]),
      lng: parseNum(c[26]),
    });
  }
  return rows;
}

async function fetchViaJina(url) {
  const mirror = `https://r.jina.ai/http://${url.replace(/^https?:\/\//, "")}`;
  const res = await fetch(mirror, { headers: { "user-agent": "Mozilla/5.0" } });
  if (!res.ok) throw new Error(`Jina fetch failed ${res.status}`);
  return res.text();
}

async function fetchCityForSale(city) {
  const key = city.toLowerCase();
  const regionId = CITY_REGION[key];
  if (!regionId) return [];

  const url = `https://www.redfin.com/stingray/api/gis-csv?al=1&market=sfbay&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id=${regionId}&region_type=6&status=1&uipt=1&v=8`;
  const raw = await fetchViaJina(url);
  return fromCsvRows(raw);
}

export function normalizeListing(raw, intent) {
  const cityKey = (raw.city || "").toLowerCase();
  const lotSize = raw.lotSize ?? null;

  return {
    provider: "redfin",
    providerId: String(raw.mls || raw.url || raw.address || Math.random()),
    status: intent === "rent" ? "for_rent" : (String(raw.status || "").toLowerCase().includes("sold") ? "sold" : "for_sale"),
    address: {
      street: raw.street || raw.address || "",
      city: raw.city || "",
      state: raw.state || "CA",
      zip: raw.zip || "",
    },
    url: raw.url || "",
    price: raw.price ?? null,
    rent: raw.rent ?? null,
    beds: raw.beds ?? null,
    baths: raw.baths ?? null,
    sqft: raw.sqft ?? null,
    lotSqft: lotSize,
    yearBuilt: raw.yearBuilt ?? null,
    daysOnRedfin: raw.daysOnRedfin ?? null,
    homeType: normalizeHomeType(raw.homeType || raw.propertyType, raw.street || raw.address, raw.url),
    schoolScore: raw.schoolScore ?? CITY_SCHOOL_SCORE_EST[cityKey] ?? null,
    driveMinutesToGoogleplex: raw.driveMinutesToGoogleplex ?? CITY_DRIVE_MIN[cityKey] ?? null,
    driveMinutesToOpenAIMTV: raw.driveMinutesToOpenAIMTV ?? CITY_DRIVE_MIN_OPENAI_MTV[cityKey] ?? null,
    hasBackyard: raw.hasBackyard != null ? !!raw.hasBackyard : (lotSize != null ? lotSize >= 3500 : false),
    schoolDistrict: raw.schoolDistrict || raw.city || null,
    schools: raw.schools || {
      elementary: raw.elementarySchool || null,
      middle: raw.middleSchool || null,
      high: raw.highSchool || null,
    },
    lat: raw.lat ?? null,
    lng: raw.lng ?? null,
    soldDate: raw.soldDate || null,
    listedDate: raw.listedDate || null,
    sourceAsOf: new Date().toISOString(),
  };
}

function likelyPlaceholderUrl(url = "") {
  const m = String(url).match(/\/home\/(\d+)\/?$/i);
  if (!m) return false;
  return Number(m[1]) < 1000;
}

function loadSample(intent) {
  const fp = intent === "rent" ? SAMPLE_RENT : SAMPLE_BUY;
  const obj = JSON.parse(fs.readFileSync(fp, "utf8"));
  return (obj.listings || [])
    .filter((x) => !likelyPlaceholderUrl(x.url))
    .map((x) => normalizeListing(x, intent));
}

export function loadLiveSold(query) {
  try {
    const obj = JSON.parse(fs.readFileSync(LIVE_SOLD, "utf8"));
    const fetchedAt = Date.parse(obj.fetchedAt || "");
    if (!Number.isFinite(fetchedAt)) return { available: false, listings: [] };

    // Freshness window: 24h
    if (Date.now() - fetchedAt > 24 * 3600 * 1000) return { available: false, listings: [] };

    const citySet = new Set((query?.area?.cities || []).map((x) => x.toLowerCase()));
    const listings = (obj.listings || [])
      .map((x) => {
        const addr = parseAddressLine(x.address || `${x.street || ""}, ${x.city || ""}, CA ${x.zip || ""}`);
        return normalizeListing({
          address: addr.street,
          city: x.city || addr.city,
          state: x.state || addr.state,
          zip: x.zip || addr.zip,
          url: x.url,
          price: parseNum(x.price || x.soldPrice),
          beds: parseBeds(x.beds),
          baths: parseNum(x.baths),
          sqft: parseNum(x.sqft),
          lotSize: parseNum(x.lotSize),
          yearBuilt: parseNum(x.yearBuilt),
          homeType: x.homeType || x.propertyType || "Single Family Residential",
          status: "Sold",
          soldDate: x.soldDate || x.dateSold || null,
          lat: parseNum(x.lat),
          lng: parseNum(x.lng),
          schoolScore: parseNum(x.schoolScore),
          driveMinutesToGoogleplex: parseNum(x.driveMinutesToGoogleplex),
          driveMinutesToOpenAIMTV: parseNum(x.driveMinutesToOpenAIMTV),
          schoolDistrict: x.schoolDistrict,
          schools: x.schools,
        }, "buy");
      })
      .filter((x) => citySet.has((x.address?.city || "").toLowerCase()));

    return { available: true, listings };
  } catch {
    return { available: false, listings: [] };
  }
}

function loadLiveRent(query) {
  try {
    const obj = JSON.parse(fs.readFileSync(LIVE_RENT, "utf8"));
    const fetchedAt = Date.parse(obj.fetchedAt || "");
    if (!Number.isFinite(fetchedAt)) return { available: false, listings: [] };

    // Freshness window: 12h
    if (Date.now() - fetchedAt > 12 * 3600 * 1000) return { available: false, listings: [] };

    const citySet = new Set((query?.area?.cities || []).map((x) => x.toLowerCase()));
    const listings = (obj.listings || [])
      .map((x) => {
        const addr = parseAddressLine(x.address);
        return normalizeListing({
          address: addr.street,
          city: addr.city,
          state: addr.state,
          zip: addr.zip,
          url: x.url,
          rent: parseNum(x.price),
          beds: parseBeds(x.beds),
          baths: parseNum(x.baths),
          sqft: parseNum(x.sqft),
          homeType: x.url?.includes('/home/') ? 'Single Family Residential' : 'Apartment',
          schoolDistrict: addr.city,
        }, "rent");
      })
      .filter((x) => citySet.has((x.address?.city || "").toLowerCase()));

    return { available: true, listings };
  } catch {
    return { available: false, listings: [] };
  }
}

async function searchLiveBuy(query) {
  const cities = query?.area?.cities || [];
  const rows = [];
  for (const city of cities) {
    try {
      const r = await fetchCityForSale(city);
      rows.push(...r);
    } catch {
      // ignore city-level fetch failures in aggregation
    }
  }

  const citySet = new Set(cities.map((x) => x.toLowerCase()));
  const active = rows
    .map((x) => normalizeListing(x, "buy"))
    .filter((x) => citySet.has((x.address?.city || "").toLowerCase()));

  const sold = loadLiveSold(query);
  return active.concat(sold.listings || []);
}

const SCHOOL_CACHE = path.join(DATA_DIR, "redfin_school_cache.json");
const LIVE_SCHOOL_SIDECAR = path.join(DATA_DIR, "live_redfin_school.json");
const NOISE_CACHE = path.join(DATA_DIR, "noise_cache.json");

function loadSchoolCache() {
  try { return JSON.parse(fs.readFileSync(SCHOOL_CACHE, "utf8")); } catch { return { byUrl: {} }; }
}

function saveSchoolCache(obj) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(SCHOOL_CACHE, JSON.stringify(obj, null, 2));
}

function loadSidecarSchoolCache() {
  try {
    const obj = JSON.parse(fs.readFileSync(LIVE_SCHOOL_SIDECAR, "utf8"));
    return obj && typeof obj === "object" ? obj : { byUrl: {} };
  } catch {
    return { byUrl: {} };
  }
}

function readFreshSidecarSchools(url, sidecar, maxAgeMs = 48 * 3600 * 1000) {
  if (!url || !sidecar?.byUrl) return null;
  const row = sidecar.byUrl[url];
  if (!row || !row.schools) return null;
  const ts = Date.parse(row.fetchedAt || sidecar.fetchedAt || "");
  if (!Number.isFinite(ts)) return null;
  if (Date.now() - ts > maxAgeMs) return null;
  return row.schools;
}

function hasUsableSchoolData(schools) {
  if (!schools || typeof schools !== "object") return false;
  for (const k of ["elementary", "middle", "high"]) {
    const s = schools[k];
    if (!s) continue;
    if (typeof s === "string" && s.trim()) return true;
    if (s.name || s.rating != null || s.distanceMi != null) return true;
  }
  return false;
}

function loadNoiseCache() {
  try { return JSON.parse(fs.readFileSync(NOISE_CACHE, "utf8")); } catch { return { byKey: {} }; }
}

function saveNoiseCache(obj) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(NOISE_CACHE, JSON.stringify(obj, null, 2));
}

function citySchoolFallback(city = "") {
  const c = String(city).toLowerCase();
  const districtDefaults = {
    "mountain view": {
      elementary: { name: "Neighborhood elementary (district assigned)", rating: 8, distanceMi: null },
      middle: { name: "Neighborhood middle (district assigned)", rating: 8, distanceMi: null },
      high: { name: "Neighborhood high school (district assigned)", rating: 8, distanceMi: null },
    },
    "sunnyvale": {
      elementary: { name: "Neighborhood elementary (district assigned)", rating: 8, distanceMi: null },
      middle: { name: "Neighborhood middle (district assigned)", rating: 8, distanceMi: null },
      high: { name: "Neighborhood high school (district assigned)", rating: 8, distanceMi: null },
    },
    "cupertino": {
      elementary: { name: "Neighborhood elementary (district assigned)", rating: 9, distanceMi: null },
      middle: { name: "Neighborhood middle (district assigned)", rating: 9, distanceMi: null },
      high: { name: "Neighborhood high school (district assigned)", rating: 9, distanceMi: null },
    },
    "los altos": {
      elementary: { name: "Neighborhood elementary (district assigned)", rating: 9, distanceMi: null },
      middle: { name: "Neighborhood middle (district assigned)", rating: 9, distanceMi: null },
      high: { name: "Neighborhood high school (district assigned)", rating: 9, distanceMi: null },
    },
    "palo alto": {
      elementary: { name: "Neighborhood elementary (district assigned)", rating: 9, distanceMi: null },
      middle: { name: "Neighborhood middle (district assigned)", rating: 9, distanceMi: null },
      high: { name: "Neighborhood high school (district assigned)", rating: 9, distanceMi: null },
    },
  };
  return districtDefaults[c] || null;
}

function parseSchoolBlock(text, label) {
  const lines = String(text || "").split(/\r?\n/).slice(0, 1200);
  const candidates = lines.filter((ln) => new RegExp(`\\b${label}\\b`, "i").test(ln) && /school/i.test(ln));
  if (!candidates.length) return null;

  const line = candidates[0];
  const rating = parseNum((line.match(/(\d+(?:\.\d+)?)\s*\/\s*10/) || [])[1]);
  const distanceMi = parseNum((line.match(/(\d+(?:\.\d+)?)\s*mi/i) || [])[1]);
  const nameGuess = (line.match(/:\s*([^,|]+school[^,|]*)/i) || [])[1] || null;

  if (rating == null && distanceMi == null && !nameGuess) return null;
  return { name: nameGuess, rating, distanceMi };
}

function parseSchoolsFromDetail(text) {
  if (!text || /confirm you are human|security check/i.test(text)) return null;

  const elementary = parseSchoolBlock(text, "Elementary");
  const middle = parseSchoolBlock(text, "Middle");
  const high = parseSchoolBlock(text, "High");

  if (!elementary && !middle && !high) return null;
  return {
    elementary: elementary || null,
    middle: middle || null,
    high: high || null,
  };
}

async function fetchSchoolsForUrl(url) {
  try {
    const text = await fetchViaJina(url);
    return parseSchoolsFromDetail(text);
  } catch {
    return null;
  }
}

export async function enrichListingsWithSchoolDetails(listings = [], options = {}) {
  const maxListings = Number(options.maxListings || 8);
  const ttlMs = Number(options.ttlMs || 7 * 24 * 3600 * 1000);
  const sidecarMaxAgeMs = Number(options.sidecarMaxAgeMs || 48 * 3600 * 1000);
  const out = [...listings];
  const cache = loadSchoolCache();
  const sidecar = loadSidecarSchoolCache();
  const now = Date.now();

  for (let i = 0; i < Math.min(out.length, maxListings); i++) {
    const l = out[i];
    const key = l.url;
    if (!key) continue;

    // Priority 1: sidecar browser-harvested school details
    const sidecarSchools = readFreshSidecarSchools(key, sidecar, sidecarMaxAgeMs);
    if (sidecarSchools && hasUsableSchoolData(sidecarSchools)) {
      out[i] = { ...l, schools: sidecarSchools, schoolSource: "redfin-sidecar" };
      cache.byUrl[key] = { schools: sidecarSchools, fetchedAt: new Date().toISOString(), source: "redfin-sidecar" };
      continue;
    }

    // Priority 2: local parsed cache
    const cached = cache.byUrl?.[key];
    if (cached && now - Date.parse(cached.fetchedAt || 0) < ttlMs && hasUsableSchoolData(cached.schools)) {
      out[i] = { ...l, schools: cached.schools || l.schools, schoolSource: cached.source || "cache" };
      continue;
    }

    // Priority 3: Redfin detail fetch via mirror
    const schools = await fetchSchoolsForUrl(key);
    if (schools && hasUsableSchoolData(schools)) {
      out[i] = { ...l, schools, schoolSource: "redfin-detail" };
      cache.byUrl[key] = { schools, fetchedAt: new Date().toISOString(), source: "redfin-detail" };
      continue;
    }

    // Priority 4: fallback city-level proxy (clearly marked estimate)
    const fallback = citySchoolFallback(l.address?.city);
    if (fallback) {
      out[i] = { ...l, schools: fallback, schoolSource: "city-fallback-estimate" };
      cache.byUrl[key] = { schools: fallback, fetchedAt: new Date().toISOString(), source: "city-fallback-estimate" };
    }
  }

  saveSchoolCache(cache);
  return out;
}

function approxMetersBetween(lat1, lng1, lat2, lng2) {
  const x = (lng2 - lng1) * Math.cos(((lat1 + lat2) / 2) * Math.PI / 180);
  const y = (lat2 - lat1);
  return Math.sqrt(x * x + y * y) * 111320;
}

function pointToSegmentMeters(p, a, b) {
  const ax = a.lng, ay = a.lat, bx = b.lng, by = b.lat, px = p.lng, py = p.lat;
  const abx = bx - ax, aby = by - ay;
  const ab2 = abx * abx + aby * aby;
  if (!ab2) return approxMetersBetween(py, px, ay, ax);
  const apx = px - ax, apy = py - ay;
  const t = Math.max(0, Math.min(1, (apx * abx + apy * aby) / ab2));
  const proj = { lng: ax + t * abx, lat: ay + t * aby };
  return approxMetersBetween(py, px, proj.lat, proj.lng);
}

function minDistanceToWayMeters(p, coords = []) {
  if (coords.length < 2) return null;
  let best = null;
  for (let i = 0; i < coords.length - 1; i++) {
    const d = pointToSegmentMeters(p, coords[i], coords[i + 1]);
    if (best == null || d < best) best = d;
  }
  return best;
}

async function fetchNoiseContext(lat, lng, radiusM = 1800) {
  const query = `[out:json][timeout:20];(way(around:${radiusM},${lat},${lng})[railway];way(around:${radiusM},${lat},${lng})[highway~"motorway|trunk|primary|secondary"];);out body;>;out skel qt;`;
  const res = await fetch("https://overpass-api.de/api/interpreter", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: `data=${encodeURIComponent(query)}`,
  });
  if (!res.ok) throw new Error(`overpass ${res.status}`);
  return res.json();
}

function parseNoiseDistances(osm, lat, lng) {
  const nodes = new Map();
  for (const e of (osm?.elements || [])) {
    if (e.type === "node") nodes.set(e.id, { lat: e.lat, lng: e.lon });
  }

  let rail = null, freeway = null, arterial = null;
  const p = { lat, lng };

  for (const e of (osm?.elements || [])) {
    if (e.type !== "way") continue;
    const coords = (e.nodes || []).map((id) => nodes.get(id)).filter(Boolean);
    if (coords.length < 2) continue;
    const d = minDistanceToWayMeters(p, coords);
    if (d == null) continue;

    const rw = String(e.tags?.railway || "").toLowerCase();
    const hw = String(e.tags?.highway || "").toLowerCase();

    if (rw && ["rail", "light_rail", "subway", "tram"].includes(rw)) {
      rail = rail == null ? d : Math.min(rail, d);
    }

    if (["motorway", "trunk"].includes(hw)) {
      freeway = freeway == null ? d : Math.min(freeway, d);
    }

    if (["primary", "secondary"].includes(hw)) {
      arterial = arterial == null ? d : Math.min(arterial, d);
    }
  }

  return { rail, freeway, arterial };
}

function noiseRisk(dist = {}) {
  const rail = dist.rail ?? 99999;
  const fwy = dist.freeway ?? 99999;
  const art = dist.arterial ?? 99999;

  let score = 0;
  if (rail < 250) score += 45; else if (rail < 600) score += 20;
  if (fwy < 300) score += 40; else if (fwy < 800) score += 18;
  if (art < 100) score += 20; else if (art < 250) score += 10;

  const label = score >= 55 ? "high" : score >= 25 ? "medium" : "low";
  return { score, label };
}

function noiseKey(l) {
  const lat = Number(l?.lat);
  const lng = Number(l?.lng);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  return `${lat.toFixed(4)},${lng.toFixed(4)}`;
}

export async function enrichListingsWithNoise(listings = [], options = {}) {
  const maxListings = Number(options.maxListings || 10);
  const ttlMs = Number(options.ttlMs || 10 * 24 * 3600 * 1000);
  const radiusM = Number(options.radiusM || 1800);
  const out = [...listings];
  const cache = loadNoiseCache();

  for (let i = 0; i < Math.min(out.length, maxListings); i++) {
    const l = out[i];
    const key = noiseKey(l);
    if (!key) continue;

    const cached = cache.byKey?.[key];
    const ts = Date.parse(cached?.fetchedAt || "");
    if (cached && Number.isFinite(ts) && (Date.now() - ts) < ttlMs) {
      out[i] = { ...l, noise: cached.noise };
      continue;
    }

    try {
      const osm = await fetchNoiseContext(l.lat, l.lng, radiusM);
      const d = parseNoiseDistances(osm, l.lat, l.lng);
      const r = noiseRisk(d);
      const noise = {
        label: r.label,
        score: r.score,
        railMeters: d.rail != null ? Math.round(d.rail) : null,
        freewayMeters: d.freeway != null ? Math.round(d.freeway) : null,
        arterialMeters: d.arterial != null ? Math.round(d.arterial) : null,
      };
      out[i] = { ...l, noise };
      cache.byKey[key] = { noise, fetchedAt: new Date().toISOString() };
    } catch {
      // keep listing without noise context on fetch failure
    }
  }

  saveNoiseCache(cache);
  return out;
}

export async function searchListings(query) {
  const intent = query.intent || "buy";

  if (intent === "buy") {
    const live = await searchLiveBuy(query);
    if (live.length) return live;
    return loadSample("buy");
  }

  // Rent: use sidecar-collected live cache when available/fresh; fallback to fixture only when live cache is unavailable.
  const rentLive = loadLiveRent(query);
  if (rentLive.available) return rentLive.listings;
  return loadSample("rent");
}
