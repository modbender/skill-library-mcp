import fs from "fs";
import path from "path";
import crypto from "crypto";
import { fileURLToPath } from "url";
import { normalizeQuery, defaultBuyQuery, defaultRentQuery } from "./core/query_normalizer.mjs";
import { dedupeListings, listingKey } from "./core/dedupe.mjs";
import { filterAndRank } from "./core/scoring.mjs";
import { findRecentSimilarPrices, buildSubjectFromListing } from "./core/comps.mjs";
import { loadLatestSnapshot, writeSnapshot, snapshotDiff } from "./core/notifier.mjs";
import { enrichListingsWithSchoolDetails, enrichListingsWithNoise, loadLiveSold } from "./providers/redfin.mjs";
import { searchListings, parseProvidersFlag } from "./providers/index.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "data");
const SUBS_PATH = path.join(ROOT, "subscriptions.json");
const QUERIES_PATH = path.join(ROOT, "queries.json");
const PROFILES_PATH = path.join(ROOT, "profiles.json");
const SNAP_ROOT = path.join(ROOT, "snapshots");

const PROVIDER_CACHE_FILES = {
  zillow: {
    buy: path.join(ROOT, "live_zillow_buy.json"),
    rent: path.join(ROOT, "live_zillow_rent.json"),
  },
  realtor: {
    buy: path.join(ROOT, "live_realtor_buy.json"),
    rent: path.join(ROOT, "live_realtor_rent.json"),
  },
};

function readJson(fp, fallback = null) { try { return JSON.parse(fs.readFileSync(fp, "utf8")); } catch { return fallback; } }
function writeJson(fp, data) { fs.mkdirSync(path.dirname(fp), { recursive: true }); fs.writeFileSync(fp, JSON.stringify(data, null, 2)); }
function arg(name, fallback = null) { const i = process.argv.indexOf(name); return i >= 0 && i + 1 < process.argv.length ? process.argv[i + 1] : fallback; }

function parseNaturalLanguageRequest(text = "") {
  const t = String(text || "").toLowerCase();

  const isSouthBay = /south\s*bay/.test(t);
  const isDefault = /default\s*profile|default/.test(t);

  if (/for\s+sale|buy|homes?\s+for\s+sale/.test(t)) {
    return {
      intent: "buy",
      queryId: (isSouthBay || isDefault) ? "south-bay-buy-default" : "south-bay-buy-default",
    };
  }

  if (/for\s+rent|lease|rental/.test(t)) {
    return {
      intent: "rent",
      queryId: (isSouthBay || isDefault) ? "south-bay-rent-default" : "south-bay-rent-default",
    };
  }

  if (/similar|comp|comparable/.test(t)) {
    return {
      intent: "comps",
      queryId: "south-bay-buy-default",
    };
  }

  return null;
}

function saveQuery(q) {
  const all = readJson(QUERIES_PATH, { queries: [] });
  const queries = (all.queries || []).filter((x) => x.queryId !== q.queryId);
  queries.push({ ...q, updatedAt: new Date().toISOString() });
  writeJson(QUERIES_PATH, { queries });
}

function getQuery(queryId) {
  const all = readJson(QUERIES_PATH, { queries: [] });
  return (all.queries || []).find((x) => x.queryId === queryId) || null;
}

function ensureDefaults() {
  const buy = normalizeQuery(defaultBuyQuery());
  const rent = normalizeQuery(defaultRentQuery());
  saveQuery(buy);
  saveQuery(rent);
}

function slug(s = "") {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50) || "profile";
}

function parseCsvArg(name) {
  const v = arg(name, "");
  return String(v).split(",").map((x) => x.trim()).filter(Boolean);
}

function readProfiles() {
  const obj = readJson(PROFILES_PATH, { profiles: [] });
  return Array.isArray(obj?.profiles) ? obj : { profiles: [] };
}

function writeProfiles(obj) {
  writeJson(PROFILES_PATH, obj);
}

function upsertProfile(profile) {
  const all = readProfiles();
  const rest = all.profiles.filter((x) => String(x.name).toLowerCase() !== String(profile.name).toLowerCase());
  rest.push({ ...profile, updatedAt: new Date().toISOString() });
  writeProfiles({ profiles: rest });
}

function getProfile(name) {
  if (!name) return null;
  const all = readProfiles();
  return all.profiles.find((x) => String(x.name).toLowerCase() === String(name).toLowerCase()) || null;
}

function queryFromProfile(profile, intent) {
  const hard = {};
  if (profile.constraints?.budgetMax != null) {
    if (intent === "rent") hard.rentMax = Number(profile.constraints.budgetMax);
    else hard.priceMax = Number(profile.constraints.budgetMax);
  }
  if (profile.constraints?.bedsMin != null) hard.bedsMin = Number(profile.constraints.bedsMin);
  if (profile.constraints?.bathsMin != null) hard.bathsMin = Number(profile.constraints.bathsMin);
  if (profile.constraints?.schoolScoreMin != null) hard.schoolScoreMin = Number(profile.constraints.schoolScoreMin);
  if (profile.constraints?.maxDriveMinutesToGoogleplex != null) hard.maxDriveMinutesToGoogleplex = Number(profile.constraints.maxDriveMinutesToGoogleplex);
  if (Array.isArray(profile.constraints?.homeTypes) && profile.constraints.homeTypes.length) hard.homeTypes = profile.constraints.homeTypes;
  if (Array.isArray(profile.area?.zipCodes) && profile.area.zipCodes.length) hard.zipCodes = profile.area.zipCodes;

  const city = profile.area?.city ? [profile.area.city] : [];
  const cities = Array.isArray(profile.area?.cities) && profile.area.cities.length ? profile.area.cities : city;

  return normalizeQuery({
    queryId: `profile-${slug(profile.name)}-${intent}`,
    intent,
    area: {
      mode: "city_set",
      cities,
      state: profile.area?.state || "CA",
      country: profile.area?.country || "US",
      zipCodes: profile.area?.zipCodes || [],
    },
    constraints: {
      hard,
      soft: {
        preferBackyardForKids: profile.constraints?.preferBackyardForKids !== false,
      },
    },
    notify: profile.notify || {},
  });
}

function applySearchFlagsToQuery(query, intent) {
  const q = JSON.parse(JSON.stringify(query || {}));
  q.area = q.area || { cities: [] };
  q.constraints = q.constraints || { hard: {}, soft: {} };
  q.constraints.hard = q.constraints.hard || {};

  const city = arg("--city", null);
  const cities = parseCsvArg("--cities");
  const state = arg("--state", null);
  const country = arg("--country", null);
  const zip = arg("--zip", null);
  const zips = parseCsvArg("--zip-codes");

  const mergedCities = [...new Set([...(cities || []), ...(city ? [city] : [])])];
  const mergedZips = [...new Set([...(zips || []), ...(zip ? [zip] : [])])];

  if (mergedCities.length) q.area.cities = mergedCities;
  if (state) q.area.state = state;
  if (country) q.area.country = country;
  if (mergedZips.length) q.constraints.hard.zipCodes = mergedZips;

  const bedsMin = arg("--beds-min", null);
  const bathsMin = arg("--baths-min", null);
  const schoolMin = arg("--school-min", null);
  const homeType = arg("--home-type", null);
  const homeTypes = parseCsvArg("--home-types");
  const budgetMax = arg("--budget-max", null);

  if (bedsMin != null) q.constraints.hard.bedsMin = Number(bedsMin);
  if (bathsMin != null) q.constraints.hard.bathsMin = Number(bathsMin);
  if (schoolMin != null) q.constraints.hard.schoolScoreMin = Number(schoolMin);

  const mergedHomeTypes = [...new Set([...(homeTypes || []), ...(homeType ? [homeType] : [])])].map((x) => String(x).toLowerCase());
  if (mergedHomeTypes.length) q.constraints.hard.homeTypes = mergedHomeTypes;

  if (budgetMax != null) {
    if (intent === "rent") q.constraints.hard.rentMax = Number(budgetMax);
    else q.constraints.hard.priceMax = Number(budgetMax);
  }

  return q;
}

async function runSearch(query, options = {}) {
  const providers = options.providers || ["redfin"];
  const raw = await searchListings(query, providers);
  const deduped = dedupeListings(raw).map((x) => ({ ...x, listingKey: listingKey(x) }));
  let ranked = filterAndRank(deduped, query);
  if (options.enrichSchools) {
    ranked = await enrichListingsWithSchoolDetails(ranked, { maxListings: options.schoolDetailLimit || 8 });
  }
  if (options.enrichNoise) {
    ranked = await enrichListingsWithNoise(ranked, { maxListings: options.noiseDetailLimit || 10 });
  }
  return ranked;
}

function fmtMoney(n) {
  const v = Number(n);
  if (!Number.isFinite(v)) return "n/a";
  return `$${v.toLocaleString("en-US")}`;
}

function parseRedfinTitleSubject(text, url) {
  const title = (String(text || "").match(/Title:\s*(.+)/) || [])[1] || "";
  const beds = Number((title.match(/(\d+(?:\.\d+)?)\s*beds?/i) || [])[1]);
  const baths = Number((title.match(/(\d+(?:\.\d+)?)\s*baths?/i) || [])[1]);
  const addr = (title.match(/^(.+?),\s*([^,]+),\s*CA\s*(\d{5})/i) || []);
  const street = addr[1] || null;
  const city = addr[2] || null;
  const zip = addr[3] || null;

  return {
    address: street,
    city,
    zip,
    beds: Number.isFinite(beds) ? beds : null,
    baths: Number.isFinite(baths) ? baths : null,
    homeType: /\/condo\//i.test(url) ? "condo" : /\/townhouse\//i.test(url) ? "townhouse" : "single_family",
  };
}

async function buildSubjectFromRedfinUrl(redfinUrl, results = []) {
  const hit = results.find((x) => String(x.url || "").replace(/\/$/, "") === String(redfinUrl || "").replace(/\/$/, ""));
  if (hit) return buildSubjectFromListing(hit, { status: "for_sale" });

  const mirror = `https://r.jina.ai/http://${String(redfinUrl).replace(/^https?:\/\//, "")}`;
  const res = await fetch(mirror, { headers: { "user-agent": "Mozilla/5.0" } });
  if (!res.ok) throw new Error(`Failed to fetch redfin-url subject (${res.status})`);
  const text = await res.text();
  return parseRedfinTitleSubject(text, redfinUrl);
}

function withSchoolFallback(schools = {}, schoolScore = null, source = null) {
  const hasAny = ["elementary", "middle", "high"].some((k) => {
    const v = schools?.[k];
    if (!v) return false;
    if (typeof v === "string") return v.trim().length > 0;
    return Object.values(v).some((x) => x != null && String(x).trim?.() !== "");
  });

  if (hasAny) return { schools, source };
  if (schoolScore == null) return { schools, source };

  const fallback = {
    elementary: { rating: schoolScore },
    middle: { rating: schoolScore },
    high: { rating: schoolScore },
  };
  return { schools: fallback, source: source || "city-fallback-estimate" };
}

function schoolLine(schools = {}, source = null) {
  const compactFallback = source === "city-fallback-estimate";

  const cleanName = (name = "") => String(name)
    .replace(/\s*\(district assigned\)\s*/ig, "")
    .replace(/^Neighborhood\s+/i, "")
    .trim();

  const mk = (k, label) => {
    const raw = schools?.[k] || {};
    const s = typeof raw === "string" ? { name: raw } : raw;
    const rating = s.rating != null ? `${s.rating}/10` : "n/a";
    const dist = s.distanceMi != null ? `${s.distanceMi} mi` : null;
    const name = cleanName(s.name || "");

    if (compactFallback) {
      return `${label}: ${rating}`;
    }

    if (name && dist) return `${label}: ${name} (${rating}, ${dist})`;
    if (name) return `${label}: ${name} (${rating})`;
    return `${label}: ${rating}`;
  };

  const line = `${mk("elementary", "E")} | ${mk("middle", "M")} | ${mk("high", "H")}`;
  return source ? `${line} | source: ${source}` : line;
}

function propertySummary(x) {
  const pros = [];
  const cons = [];

  if (x.hasBackyard) pros.push("has a backyard that is useful for kids/outdoor time");
  if (x.schoolScore != null && x.schoolScore >= 8.5) pros.push(`strong estimated school profile (score ${x.schoolScore})`);
  if (x.driveMinutesToGoogleplex != null && x.driveMinutesToGoogleplex <= 20) pros.push(`reasonable commute estimate (~${x.driveMinutesToGoogleplex} min to Googleplex)`);
  if (x.sqft != null && x.sqft >= 2200) pros.push(`larger interior footprint (${x.sqft} sqft)`);

  if (x.noise?.label === "low") pros.push("set back from major transport noise corridors");
  if (x.noise?.label === "high") cons.push("closer to rail/highway/main-road corridors, potential noise risk");
  if (x.noise?.label === "medium") cons.push("some exposure to nearby transport corridors; verify on-site at peak hours");

  if (x.baths != null && x.baths < 2.5) cons.push("bathroom count may feel tight for a larger household");
  if (x.sqft != null && x.sqft < 1800) cons.push("interior size is on the smaller side for 4+ bed homes");
  cons.push("interior finish/renovation condition is unknown from this feed");

  const proTxt = (pros[0] || "solid baseline match for default South Bay constraints");
  const conTxt = (cons[0] || "needs on-site review for tradeoffs");
  return `Pros: ${proTxt}. Also ${pros[1] || "location and school details should be verified in person"}. Cons: ${conTxt}.`;
}

function similarSoldLine(subject, listings = []) {
  const subjectRef = buildSubjectFromListing(subject, { status: "for_sale" });
  const comp = findRecentSimilarPrices(subjectRef, listings, {
    intent: "buy",
    recencyWindowDays: 365,
    limit: 20,
    minScore: 20,
    strict: {
      homeTypeMatch: true,
      bedsExact: true,
      sameCityOrZip: true,
      schoolScoreDelta: 0.5,
      sqftPct: 0.2,
    },
  });

  const sold = comp.comps
    .filter((c) => String(c.listing?.status || "").toLowerCase() === "sold")
    .slice(0, 3)
    .map((c) => {
      const l = c.listing;
      const soldDate = l.soldDate ? new Date(l.soldDate).toISOString().slice(0, 10) : "n/a";
      return `${fmtMoney(l.price)} on ${soldDate} (${l.url})`;
    });

  if (sold.length) return sold.join("; ");

  const activeFallback = comp.comps
    .filter((c) => String(c.listing?.status || "").toLowerCase() !== "sold")
    .slice(0, 3)
    .map((c) => {
      const l = c.listing;
      const amount = fmtMoney(l.price);
      return `${amount} (${l.status || "for_sale"}) (${l.url})`;
    });

  if (activeFallback.length) return `[active fallback] ${activeFallback.join("; ")}`;
  return "none found within 1 year";
}

function shortLine(x, allListings = []) {
  const amount = x.status === "for_rent" ? `${fmtMoney(x.rent)}/mo` : fmtMoney(x.price);
  const type = (x.homeType || "unknown").replaceAll("_", " ");
  const dGoogle = x.driveMinutesToGoogleplex != null ? `Gpx ~${x.driveMinutesToGoogleplex}m` : "Gpx n/a";
  const dOpenAI = x.driveMinutesToOpenAIMTV != null ? `OpenAI-MTV ~${x.driveMinutesToOpenAIMTV}m` : "OpenAI-MTV n/a";
  const dom = x.daysOnRedfin != null ? `DOM ${x.daysOnRedfin}d` : "DOM n/a";
  const n = x.noise || {};
  const dRail = n.railMeters != null ? `rail ${n.railMeters}m` : "rail n/a";
  const dFwy = n.freewayMeters != null ? `hwy ${n.freewayMeters}m` : "hwy n/a";
  const dRoad = n.arterialMeters != null ? `main ${n.arterialMeters}m` : "main n/a";
  const noise = n.label ? `noise ${n.label}` : "noise n/a";
  const similarHouses = x.status === "for_sale" ? similarSoldLine(x, allListings) : "n/a";
  const school = withSchoolFallback(x.schools, x.schoolScore, x.schoolSource);
  return `- [${x.status}] ${x.address.street}, ${x.address.city}\n  Price: ${amount} | Type: ${type} | ${x.beds}bd/${x.baths}ba | ${x.sqft ?? "?"} sqft | ${dom} | ${dGoogle} | ${dOpenAI} | ${noise} (${dRail}, ${dFwy}, ${dRoad}) | score ${x.rankScore?.toFixed(1) ?? "0.0"}\n  Schools: ${schoolLine(school.schools, school.source)}\n  Similar houses: ${similarHouses}\n  Summary: ${propertySummary(x)}\n  Link: ${x.url}`;
}

function sortByDomAsc(listings = []) {
  return [...listings].sort((a, b) => {
    const aDomRaw = a?.daysOnRedfin ?? a?.domDaysOnRedfin;
    const bDomRaw = b?.daysOnRedfin ?? b?.domDaysOnRedfin;
    const da = Number.isFinite(Number(aDomRaw)) ? Number(aDomRaw) : Number.POSITIVE_INFINITY;
    const db = Number.isFinite(Number(bDomRaw)) ? Number(bDomRaw) : Number.POSITIVE_INFINITY;
    if (da !== db) return da - db;
    const sa = Number.isFinite(Number(a?.rankScore)) ? Number(a.rankScore) : -Infinity;
    const sb = Number.isFinite(Number(b?.rankScore)) ? Number(b.rankScore) : -Infinity;
    return sb - sa;
  });
}

function ensureSubs() {
  const obj = readJson(SUBS_PATH, null);
  if (obj && Array.isArray(obj.subscriptions)) return obj;
  const init = { subscriptions: [] };
  writeJson(SUBS_PATH, init);
  return init;
}

function upsertSubscription(sub) {
  const store = ensureSubs();
  const rest = store.subscriptions.filter((x) => x.subscriptionId !== sub.subscriptionId);
  rest.push(sub);
  writeJson(SUBS_PATH, { subscriptions: rest });
}

function listSubscriptions() {
  const store = ensureSubs();
  return store.subscriptions;
}

function makeSubId(queryId) {
  const d = crypto.createHash("sha1").update(queryId).digest("hex").slice(0, 8);
  return `sub-${queryId}-${d}`;
}

async function cmdSearch() {
  ensureDefaults();
  const profileName = arg("--profile", null);
  const intent = arg("--intent", "buy").toLowerCase();

  let queryId = arg("--query", intent === "rent" ? "south-bay-rent-default" : "south-bay-buy-default");
  let q = getQuery(queryId);

  if (profileName) {
    const p = getProfile(profileName);
    if (!p) throw new Error(`Unknown profile: ${profileName}`);
    q = queryFromProfile(p, intent === "rent" ? "rent" : "buy");
    queryId = q.queryId;
  }

  if (!q) throw new Error(`Unknown query: ${queryId}`);
  q = applySearchFlagsToQuery(q, intent);
  const hasCities = Array.isArray(q?.area?.cities) && q.area.cities.length;
  const hasZips = Array.isArray(q?.constraints?.hard?.zipCodes) && q.constraints.hard.zipCodes.length;
  if (!hasCities && !hasZips) {
    throw new Error("No area configured in query/profile. Pass --city/--cities or --zip/--zip-codes when creating profile.");
  }

  const providers = parseProvidersFlag(arg("--providers", "redfin,zillow,realtor"));
  const results = await runSearch(q, { providers, enrichSchools: true, schoolDetailLimit: 10, enrichNoise: true, noiseDetailLimit: 10 });
  const desiredStatus = intent === "rent" ? "for_rent" : "for_sale";
  const display = sortByDomAsc(results.filter((x) => x.status === desiredStatus));
  console.log(`Housing Scout search (${queryId})`);
  if (!display.length) return console.log("(no matches)");
  display.slice(0, 20).forEach((x) => console.log(shortLine(x, results)));
}

async function cmdLease() {
  ensureDefaults();
  const profileName = arg("--profile", null);
  const queryId = arg("--query", "south-bay-rent-default");
  const baseQuery = getQuery(queryId);
  let q = baseQuery;
  if (profileName) {
    const p = getProfile(profileName);
    if (!p) throw new Error(`Unknown profile: ${profileName}`);
    q = queryFromProfile(p, "rent");
  }
  if (!q) throw new Error(`Unknown query: ${queryId}`);

  const redfinUrl = arg("--redfin-url", null);
  const city = arg("--city", null);
  const zip = arg("--zip", null);
  const schoolDistrict = arg("--school-district", null);
  const bedsMin = arg("--beds-min", null);
  const bathsMin = arg("--baths-min", null);
  const schoolMin = arg("--school-min", null);
  const homeType = arg("--home-type", null);
  const limit = Number(arg("--limit", "20"));

  const query = JSON.parse(JSON.stringify(q));
  query.constraints = query.constraints || { hard: {}, soft: {} };
  query.constraints.hard = query.constraints.hard || {};

  if (bedsMin != null) query.constraints.hard.bedsMin = Number(bedsMin);
  if (bathsMin != null) query.constraints.hard.bathsMin = Number(bathsMin);
  if (schoolMin != null) query.constraints.hard.schoolScoreMin = Number(schoolMin);
  if (homeType) query.constraints.hard.homeTypes = [homeType];
  if (city) query.area.cities = [city];

  const providers = parseProvidersFlag(arg("--providers", "redfin,zillow,realtor"));
  let results = await runSearch(query, { providers, enrichSchools: true, schoolDetailLimit: 10, enrichNoise: true, noiseDetailLimit: 10 });

  if (redfinUrl) {
    const subject = await buildSubjectFromRedfinUrl(redfinUrl, results);
    results = results.filter((x) => {
      const cityMatch = subject?.city && x.address?.city && String(subject.city).toLowerCase() === String(x.address.city).toLowerCase();
      const zipMatch = subject?.zip && x.address?.zip && String(subject.zip) === String(x.address.zip);
      const bedsOk = subject?.beds != null && x.beds != null ? Number(x.beds) >= Number(subject.beds) : true;
      const bathsOk = subject?.baths != null && x.baths != null ? Number(x.baths) >= Number(subject.baths) : true;
      const typeOk = subject?.homeType && x.homeType ? String(subject.homeType).toLowerCase() === String(x.homeType).toLowerCase() : true;
      return (cityMatch || zipMatch) && bedsOk && bathsOk && typeOk;
    });
  }

  if (city) results = results.filter((x) => String(x.address?.city || "").toLowerCase() === String(city).toLowerCase());
  if (zip) results = results.filter((x) => String(x.address?.zip || "") === String(zip));
  if (schoolDistrict) {
    const key = String(schoolDistrict).toLowerCase();
    results = results.filter((x) => String(x.schoolDistrict || "").toLowerCase().includes(key));
  }

  results = sortByDomAsc(results);

  console.log(`Housing Scout lease (${queryId})`);
  if (!results.length) return console.log("(no matches)");
  results.slice(0, limit).forEach((x) => console.log(shortLine(x, results)));
}

function cmdProviderCacheStatus() {
  const provider = String(arg("--provider", "")).toLowerCase();
  const intent = String(arg("--intent", "buy")).toLowerCase();

  if (!PROVIDER_CACHE_FILES[provider]) throw new Error("Unsupported --provider. Use zillow|realtor");
  if (!["buy", "rent"].includes(intent)) throw new Error("Unsupported --intent. Use buy|rent");

  const target = PROVIDER_CACHE_FILES[provider][intent];
  const obj = readJson(target, null);
  if (!obj) return console.log(`Cache missing: ${target}`);

  const ts = Date.parse(obj.fetchedAt || "");
  const ageHours = Number.isFinite(ts) ? ((Date.now() - ts) / 3600000) : null;
  const ttlHours = intent === "rent" ? 12 : 24;
  const fresh = ageHours != null ? ageHours <= ttlHours : false;
  const rows = Array.isArray(obj.listings) ? obj.listings.length : 0;

  console.log(`Provider cache status: ${provider}/${intent}`);
  console.log(`Path: ${target}`);
  console.log(`Rows: ${rows}`);
  console.log(`FetchedAt: ${obj.fetchedAt || "n/a"}`);
  console.log(`AgeHours: ${ageHours != null ? ageHours.toFixed(1) : "n/a"}`);
  console.log(`TTLHours: ${ttlHours}`);
  console.log(`Fresh: ${fresh ? "yes" : "no"}`);
}

async function cmdQuickstart() {
  const name = arg("--name", "my-home-profile");
  const city = arg("--city", null);
  const state = arg("--state", "CA");
  const country = arg("--country", "US");
  const zip = arg("--zip", null);
  const intent = String(arg("--intent", "buy")).toLowerCase();
  const runNow = String(arg("--run", "false")).toLowerCase() === "true";

  if (!city && !zip) {
    console.log("Quickstart needs --city or --zip.");
    console.log("Example:");
    console.log('  node housing_scout.mjs quickstart --name "great nyc area" --city "New York" --state "NY" --country "US" --beds-min 3 --budget-max 2000000');
    return;
  }

  const args = ["create_profile", "--name", name, "--state", state, "--country", country];
  if (city) args.push("--city", city);
  if (zip) args.push("--zip", zip);

  const pass = ["--beds-min", "--baths-min", "--budget-max", "--school-min", "--home-type", "--home-types"];
  for (const key of pass) {
    const v = arg(key, null);
    if (v != null) args.push(key, v);
  }

  const saved = process.argv;
  process.argv = [saved[0], saved[1], ...args];
  try {
    cmdCreateProfile();
  } finally {
    process.argv = saved;
  }

  const nextCmd = `node housing_scout.mjs search --profile "${name}" --intent ${intent}`;
  console.log("Next:");
  console.log(`  ${nextCmd}`);

  if (runNow) {
    console.log("\nRunning first search now...");
    const searchArgs = [saved[0], saved[1], "search", "--profile", name, "--intent", intent];
    const providers = arg("--providers", null);
    if (providers) searchArgs.push("--providers", providers);
    process.argv = searchArgs;
    try {
      await cmdSearch();
    } finally {
      process.argv = saved;
    }
  }
}

function cmdRefreshProviderCache() {
  const provider = String(arg("--provider", "")).toLowerCase();
  const intent = String(arg("--intent", "buy")).toLowerCase();
  const from = arg("--from", null);

  if (!PROVIDER_CACHE_FILES[provider]) throw new Error("Unsupported --provider. Use zillow|realtor");
  if (!["buy", "rent"].includes(intent)) throw new Error("Unsupported --intent. Use buy|rent");
  if (!from) throw new Error("Missing --from <path-to-json>");

  const target = PROVIDER_CACHE_FILES[provider][intent];
  const incoming = readJson(from, null);
  if (!incoming || !Array.isArray(incoming.listings)) {
    throw new Error("Input JSON must contain { listings: [...] }");
  }

  const current = readJson(target, { fetchedAt: null, source: `${provider}-sidecar-cache`, listings: [] });
  const merged = [...(current.listings || []), ...incoming.listings];

  const byKey = new Map();
  for (const row of merged) {
    const k = String(row.url || `${row.address || row.street || ""}|${row.city || ""}|${row.zip || ""}|${row.price || row.rent || ""}`);
    if (!k) continue;
    byKey.set(k, row);
  }

  const out = {
    fetchedAt: new Date().toISOString(),
    source: incoming.source || current.source || `${provider}-sidecar-cache`,
    notes: incoming.notes || current.notes || "refreshed via refresh_provider_cache",
    listings: [...byKey.values()],
  };

  writeJson(target, out);
  console.log(`Cache refreshed: ${provider}/${intent}`);
  console.log(`Target: ${target}`);
  console.log(`Rows: ${out.listings.length}`);
}

function cmdCreateProfile() {
  const name = arg("--name", null);
  if (!name) throw new Error("Missing --name for profile");

  const cities = parseCsvArg("--cities");
  const city = arg("--city", null);
  const zipCodes = parseCsvArg("--zip-codes");
  const zipSingle = arg("--zip", null);
  if (zipSingle) zipCodes.push(zipSingle);

  const area = {
    city: city || null,
    cities: cities.length ? cities : (city ? [city] : []),
    state: arg("--state", "CA"),
    country: arg("--country", "US"),
    zipCodes: [...new Set(zipCodes)],
  };

  if (!area.cities.length && !area.zipCodes.length) {
    throw new Error("Profile needs at least one city or zip code.");
  }

  const homeTypes = parseCsvArg("--home-types");
  const homeTypeSingle = arg("--home-type", null);
  if (homeTypeSingle) homeTypes.push(homeTypeSingle);

  const profile = {
    name,
    area,
    constraints: {
      budgetMax: arg("--budget-max", null) != null ? Number(arg("--budget-max")) : null,
      bedsMin: arg("--beds-min", null) != null ? Number(arg("--beds-min")) : null,
      bathsMin: arg("--baths-min", null) != null ? Number(arg("--baths-min")) : null,
      schoolScoreMin: arg("--school-min", null) != null ? Number(arg("--school-min")) : null,
      maxDriveMinutesToGoogleplex: arg("--max-drive-min", null) != null ? Number(arg("--max-drive-min")) : null,
      homeTypes: [...new Set(homeTypes.map((x) => String(x).toLowerCase()))],
      preferBackyardForKids: arg("--prefer-backyard", "true") !== "false",
    },
    notify: {
      channel: arg("--channel", "telegram"),
      to: arg("--to", "YOUR_CHAT_ID"),
    },
    createdAt: new Date().toISOString(),
  };

  upsertProfile(profile);
  console.log(`Profile saved: ${name}`);
  console.log(`Use it with:`);
  console.log(`  node housing_scout.mjs search --profile "${name}" --intent buy`);
  console.log(`  node housing_scout.mjs lease --profile "${name}"`);
}

function cmdListProfiles() {
  const all = readProfiles().profiles;
  if (!all.length) return console.log("No profiles.");
  for (const p of all) {
    const cities = (p.area?.cities || []).join(", ") || "(none)";
    const zips = (p.area?.zipCodes || []).join(", ") || "(none)";
    const budget = p.constraints?.budgetMax != null ? fmtMoney(p.constraints.budgetMax) : "n/a";
    console.log(`- ${p.name} | cities: ${cities} | zips: ${zips} | budgetMax: ${budget} | bedsMin: ${p.constraints?.bedsMin ?? "n/a"}`);
  }
}

function cmdShowProfile() {
  const name = arg("--name", null);
  if (!name) throw new Error("Missing --name");
  const p = getProfile(name);
  if (!p) throw new Error(`Unknown profile: ${name}`);
  console.log(JSON.stringify(p, null, 2));
}

function cmdDeleteProfile() {
  const name = arg("--name", null);
  if (!name) throw new Error("Missing --name");
  const all = readProfiles();
  const before = all.profiles.length;
  all.profiles = all.profiles.filter((x) => String(x.name).toLowerCase() !== String(name).toLowerCase());
  writeProfiles(all);
  const removed = before !== all.profiles.length;
  console.log(removed ? `Profile deleted: ${name}` : `Profile not found: ${name}`);
}

function cmdSoldFeedStatus() {
  ensureDefaults();
  const queryId = arg("--query", "south-bay-buy-default");
  const q = getQuery(queryId);
  if (!q) throw new Error(`Unknown query: ${queryId}`);

  const sold = loadLiveSold(q);
  console.log(`Housing Scout sold feed (${queryId})`);
  console.log(`available: ${sold.available ? "yes" : "no"}`);
  console.log(`rows: ${(sold.listings || []).length}`);

  if (!sold.available || !(sold.listings || []).length) {
    console.log("Tip: populate /app/workspace/tools/housing_scout/data/live_redfin_sold.json with recent sold records.");
    return;
  }

  const byCity = new Map();
  for (const l of sold.listings) {
    const c = l.address?.city || "(unknown)";
    byCity.set(c, (byCity.get(c) || 0) + 1);
  }

  console.log("city_counts:");
  [...byCity.entries()].sort((a, b) => b[1] - a[1]).forEach(([city, n]) => {
    console.log(`- ${city}: ${n}`);
  });

  const bad = sold.listings.filter((l) => !(l.soldDate && (l.price || l.soldPrice) && l.url));
  if (bad.length) {
    console.log(`warnings: ${bad.length} rows missing soldDate/price/url`);
  }
}

async function cmdNl() {
  ensureDefaults();
  const text = arg("--text", "");
  if (!text) throw new Error("Missing --text for nl command");

  const parsed = parseNaturalLanguageRequest(text);
  if (!parsed) {
    console.log("Could not confidently parse request. Try examples:");
    console.log('- "help me find homes for sale in south bay with default profile"');
    console.log('- "find rentals in south bay with default profile"');
    return;
  }

  if (parsed.intent === "buy") {
    const q = getQuery(parsed.queryId);
    const providers = parseProvidersFlag(arg("--providers", "redfin,zillow,realtor"));
    const results = await runSearch(q, { providers, enrichSchools: true, schoolDetailLimit: 10, enrichNoise: true, noiseDetailLimit: 10 });
    const display = sortByDomAsc(results.filter((x) => x.status === "for_sale"));
    console.log(`Housing Scout NL -> search (${parsed.queryId})`);
    if (!display.length) return console.log("(no matches)");
    return display.slice(0, 20).forEach((x) => console.log(shortLine(x, results)));
  }

  if (parsed.intent === "rent") {
    const q = getQuery(parsed.queryId);
    const providers = parseProvidersFlag(arg("--providers", "redfin,zillow,realtor"));
    const results = await runSearch(q, { providers, enrichSchools: true, schoolDetailLimit: 10, enrichNoise: true, noiseDetailLimit: 10 });
    const display = sortByDomAsc(results.filter((x) => x.status === "for_rent"));
    console.log(`Housing Scout NL -> lease (${parsed.queryId})`);
    if (!display.length) return console.log("(no matches)");
    return display.slice(0, 20).forEach((x) => console.log(shortLine(x, results)));
  }

  if (parsed.intent === "comps") {
    console.log("NL comps recognized. Please provide --redfin-url or explicit subject fields with comps command.");
    return;
  }
}

async function cmdComps() {
  ensureDefaults();
  const queryId = arg("--query", "south-bay-buy-default");
  const q = getQuery(queryId);
  if (!q) throw new Error(`Unknown query: ${queryId}`);

  const providers = parseProvidersFlag(arg("--providers", "redfin,zillow,realtor"));
  const results = await runSearch(q, { providers, enrichSchools: true, schoolDetailLimit: 10, enrichNoise: true, noiseDetailLimit: 10 });
  if (!results.length) return console.log("No listings available for comps.");

  const redfinUrl = arg("--redfin-url", null);
  const address = arg("--address", null);
  const city = arg("--city", null);
  const beds = arg("--beds", null);
  const baths = arg("--baths", null);
  const sqft = arg("--sqft", null);
  const homeType = arg("--home-type", null);

  const isRedfinMode = !!redfinUrl;
  const minScore = Number(arg("--min-score", isRedfinMode ? "20" : "25"));
  const limit = Number(arg("--limit", isRedfinMode ? "5" : "8"));

  const subjectListing = address
    ? results.find((x) => String(x.address?.street || "").toLowerCase().includes(String(address).toLowerCase()))
    : null;

  let subject;
  if (isRedfinMode) {
    subject = await buildSubjectFromRedfinUrl(redfinUrl, results);
  } else {
    if (!subjectListing && !city) {
      throw new Error("Provide --redfin-url, or --address, or manual subject fields like --city/--beds/--sqft.");
    }
    subject = buildSubjectFromListing(subjectListing, {
      address,
      city,
      beds: beds != null ? Number(beds) : undefined,
      baths: baths != null ? Number(baths) : undefined,
      sqft: sqft != null ? Number(sqft) : undefined,
      homeType,
      status: q.intent === "rent" ? "for_rent" : "for_sale",
    });
  }

  const strict = isRedfinMode ? {
    homeTypeMatch: true,
    bedsExact: true,
    sameCityOrZip: true,
    schoolScoreDelta: 0.5,
    sqftPct: 0.2,
  } : undefined;

  const comp = findRecentSimilarPrices(subject, results, {
    intent: q.intent,
    limit,
    minScore,
    recencyWindowDays: Number(arg("--recency-days", isRedfinMode ? "365" : "180")),
    maxDistanceMiles: Number(arg("--max-distance-mi", "5")),
    strict,
  });

  console.log(`House Comps (${queryId})`);
  console.log(`Subject: ${subject.address || "(manual)"}, ${subject.city || ""} ${subject.zip || ""} | ${subject.beds ?? "?"}bd/${subject.baths ?? "?"}ba | ${subject.sqft ?? "?"} sqft | ${subject.homeType || "?"}`);
  console.log(`Stats: n=${comp.stats.count} | min=${fmtMoney(comp.stats.min)} | p25=${fmtMoney(comp.stats.p25)} | median=${fmtMoney(comp.stats.median)} | p75=${fmtMoney(comp.stats.p75)} | max=${fmtMoney(comp.stats.max)} | avg=${fmtMoney(comp.stats.avg)} | confidence=${comp.confidence}`);

  if (!comp.comps.length) return console.log("No comparables matched threshold.");
  for (const c of comp.comps) {
    const l = c.listing;
    const soldDate = l.soldDate ? new Date(l.soldDate).toISOString().slice(0, 10) : null;
    const soldPrice = l.status === "sold" ? l.price : null;
    const soldLine = soldPrice ? ` | sold ${fmtMoney(soldPrice)} on ${soldDate || "n/a"}` : "";
    const amount = l.status === "for_rent" ? `${fmtMoney(l.rent)}/mo` : fmtMoney(l.price);
    const type = (l.homeType || "unknown").replaceAll("_", " ");
    const dGoogle = l.driveMinutesToGoogleplex != null ? `Gpx ~${l.driveMinutesToGoogleplex}m` : "Gpx n/a";
    const dOpenAI = l.driveMinutesToOpenAIMTV != null ? `OpenAI-MTV ~${l.driveMinutesToOpenAIMTV}m` : "OpenAI-MTV n/a";
    const dom = l.daysOnRedfin != null ? `DOM ${l.daysOnRedfin}d` : "DOM n/a";
    const n = l.noise || {};
    const dRail = n.railMeters != null ? `rail ${n.railMeters}m` : "rail n/a";
    const dFwy = n.freewayMeters != null ? `hwy ${n.freewayMeters}m` : "hwy n/a";
    const dRoad = n.arterialMeters != null ? `main ${n.arterialMeters}m` : "main n/a";
    const noise = n.label ? `noise ${n.label}` : "noise n/a";

    console.log(`- [${l.status}] ${l.address.street}, ${l.address.city}`);
    console.log(`  Price: ${amount}${soldLine} | Type: ${type} | ${l.beds}bd/${l.baths}ba | ${l.sqft ?? "?"} sqft | ${dom} | ${dGoogle} | ${dOpenAI} | ${noise} (${dRail}, ${dFwy}, ${dRoad}) | sim ${c.similarityScore.toFixed(1)} | $/sqft ${c.ppsf ?? "n/a"}`);
    const school = withSchoolFallback(l.schools, l.schoolScore, l.schoolSource);
    console.log(`  Schools: ${schoolLine(school.schools, school.source)}`);
    console.log(`  Summary: ${propertySummary(l)}`);
    console.log(`  Link: ${l.url}`);
  }
}

function cmdSubscribe() {
  ensureDefaults();
  const queryId = arg("--query");
  if (!queryId) throw new Error("Missing --query");
  const q = getQuery(queryId);
  if (!q) throw new Error(`Unknown query: ${queryId}`);

  const sub = {
    subscriptionId: makeSubId(queryId),
    queryId,
    channel: arg("--channel", q.notify?.channel || "telegram"),
    to: arg("--to", q.notify?.to || "YOUR_CHAT_ID"),
    enabled: true,
    createdAt: new Date().toISOString(),
  };
  upsertSubscription(sub);
  console.log(`Subscribed: ${sub.subscriptionId} -> ${queryId} (${sub.channel}:${sub.to})`);
}

function cmdListSubscriptions() {
  const subs = listSubscriptions();
  if (!subs.length) return console.log("No subscriptions.");
  for (const s of subs) {
    console.log(`- ${s.subscriptionId} | ${s.queryId} | ${s.enabled ? "enabled" : "disabled"} | ${s.channel}:${s.to}`);
  }
}

function cmdUnsubscribe() {
  const subId = arg("--subscription-id", null);
  const queryId = arg("--query", null);
  if (!subId && !queryId) throw new Error("Missing --subscription-id or --query");

  const store = ensureSubs();
  const before = store.subscriptions.length;
  store.subscriptions = store.subscriptions.filter((s) => {
    if (subId && s.subscriptionId === subId) return false;
    if (queryId && s.queryId === queryId) return false;
    return true;
  });
  writeJson(SUBS_PATH, store);
  const removed = before - store.subscriptions.length;
  console.log(removed > 0 ? `Unsubscribed: removed ${removed}` : "No matching subscription found.");
}

async function cmdRunSubscriptions() {
  ensureDefaults();
  const subs = listSubscriptions().filter((x) => x.enabled);
  if (!subs.length) return console.log("No enabled subscriptions.");

  for (const s of subs) {
    const q = getQuery(s.queryId);
    if (!q) continue;
    const current = await runSearch(q);
    const snapDir = path.join(SNAP_ROOT, s.subscriptionId);
    const prev = loadLatestSnapshot(snapDir);
    writeSnapshot(snapDir, current);

    const events = snapshotDiff(prev, current);
    const lines = events.map((e) => {
      const l = e.listing;
      const amount = l.status === "for_rent" ? `$${l.rent}/mo` : `$${l.price}`;
      return `  - ${e.type}: ${l.address.street}, ${l.address.city} (${amount})`;
    });

    console.log(`${s.subscriptionId}: ${events.length} changes`);
    lines.forEach((x) => console.log(x));
    if (events.length) {
      const body = [
        `Housing Scout update (${s.queryId})`,
        ...events.slice(0, 10).map((e) => {
          const l = e.listing;
          const amount = l.status === "for_rent" ? `$${l.rent}/mo` : `$${l.price}`;
          return `- ${e.type}: ${l.address.street}, ${l.address.city} (${amount})`;
        }),
      ].join("\n");

      console.log(`  notify -> ${s.channel}:${s.to}`);
      console.log(`  NOTIFY_PAYLOAD ${JSON.stringify({ channel: s.channel, to: s.to, message: body })}`);
    }
  }
}

async function main() {
  const cmd = (process.argv[2] || "help").toLowerCase();

  if (cmd === "init") return ensureDefaults();
  if (cmd === "search") return cmdSearch();
  if (cmd === "lease") return cmdLease();
  if (cmd === "provider_cache_status") return cmdProviderCacheStatus();
  if (cmd === "refresh_provider_cache") return cmdRefreshProviderCache();
  if (cmd === "quickstart") return cmdQuickstart();
  if (cmd === "create_profile") return cmdCreateProfile();
  if (cmd === "list_profiles") return cmdListProfiles();
  if (cmd === "show_profile") return cmdShowProfile();
  if (cmd === "delete_profile") return cmdDeleteProfile();
  if (cmd === "sold_feed_status") return cmdSoldFeedStatus();
  if (cmd === "nl") return cmdNl();
  if (cmd === "comps") return cmdComps();
  if (cmd === "subscribe") return cmdSubscribe();
  if (cmd === "unsubscribe") return cmdUnsubscribe();
  if (cmd === "list_subscriptions") return cmdListSubscriptions();
  if (cmd === "run_subscriptions") return cmdRunSubscriptions();

  console.log(`Usage:
  node housing_scout.mjs init
  node housing_scout.mjs search --query south-bay-buy-default [--providers redfin,zillow,realtor]
  node housing_scout.mjs search --query south-bay-rent-default [--providers redfin,zillow,realtor]
  node housing_scout.mjs search --profile "my-profile" --intent buy
  node housing_scout.mjs search --profile "my-profile" --intent rent
  node housing_scout.mjs search --intent buy --city "Seattle" --state "WA" --beds-min 3 --budget-max 1200000
  node housing_scout.mjs lease --query south-bay-rent-default --city Sunnyvale --beds-min 4 --baths-min 3
  node housing_scout.mjs lease --profile "my-profile"
  node housing_scout.mjs provider_cache_status --provider zillow --intent buy
  node housing_scout.mjs refresh_provider_cache --provider zillow --intent buy --from /app/workspace/tmp/zillow_buy.json
  node housing_scout.mjs quickstart --name "great nyc area" --city "New York" --state "NY" --beds-min 3 --budget-max 2000000 [--run true]
  node housing_scout.mjs create_profile --name "great new york city area" --city "New York" --state "NY" --country "US" --beds-min 3 --budget-max 2000000
  node housing_scout.mjs list_profiles
  node housing_scout.mjs show_profile --name "great new york city area"
  node housing_scout.mjs delete_profile --name "great new york city area"
  node housing_scout.mjs sold_feed_status --query south-bay-buy-default
  node housing_scout.mjs nl --text "help me find homes for sale in south bay with default profile"
  node housing_scout.mjs comps --query south-bay-buy-default --address "123 Main St"
  node housing_scout.mjs comps --query south-bay-buy-default --redfin-url "https://www.redfin.com/..."
  node housing_scout.mjs comps --query south-bay-buy-default --city Sunnyvale --beds 4 --baths 3 --sqft 2200 --home-type single_family [--recency-days 180] [--max-distance-mi 5]
  node housing_scout.mjs subscribe --query <queryId> [--channel telegram] [--to YOUR_CHAT_ID]
  node housing_scout.mjs unsubscribe --query <queryId>
  node housing_scout.mjs unsubscribe --subscription-id <subId>
  node housing_scout.mjs list_subscriptions
  node housing_scout.mjs run_subscriptions
`);
}

main().catch((e) => {
  console.error("housing_scout error:", e?.message || e);
  process.exit(1);
});
