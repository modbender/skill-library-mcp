import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const DATA_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../data");
const LIVE_BUY = path.join(DATA_DIR, "live_zillow_buy.json");
const LIVE_RENT = path.join(DATA_DIR, "live_zillow_rent.json");

function parseNum(v) {
  if (v == null) return null;
  const n = Number(String(v).replace(/[^0-9.-]/g, ""));
  return Number.isFinite(n) ? n : null;
}

function normalizeHomeType(v = "") {
  const s = String(v).toLowerCase();
  if (s.includes("single")) return "single_family";
  if (s.includes("town")) return "townhouse";
  if (s.includes("condo")) return "condo";
  if (s.includes("apt") || s.includes("apartment")) return "apartment";
  return s || "unknown";
}

function parseAddressLine(line = "") {
  const m = String(line).match(/^(.*?),\s*([^,]+),\s*([A-Z]{2})\s*(\d{5})?/i);
  if (!m) return { street: line || "", city: "", state: "", zip: "" };
  return { street: m[1].trim(), city: m[2].trim(), state: m[3].toUpperCase(), zip: m[4] || "" };
}

function normalizeListing(raw, intent) {
  const addr = raw.address ? parseAddressLine(raw.address) : {
    street: raw.street || "",
    city: raw.city || "",
    state: raw.state || "",
    zip: raw.zip || "",
  };
  return {
    provider: "zillow",
    providerId: String(raw.zpid || raw.url || `${addr.street}|${addr.city}|${raw.price || raw.rent || ""}`),
    status: intent === "rent" ? "for_rent" : (String(raw.status || "").toLowerCase().includes("sold") ? "sold" : "for_sale"),
    address: addr,
    url: raw.url || "",
    price: intent === "buy" ? parseNum(raw.price) : null,
    rent: intent === "rent" ? parseNum(raw.rent || raw.price) : null,
    beds: parseNum(raw.beds),
    baths: parseNum(raw.baths),
    sqft: parseNum(raw.sqft),
    lotSqft: parseNum(raw.lotSqft),
    yearBuilt: parseNum(raw.yearBuilt),
    daysOnRedfin: parseNum(raw.daysOnMarket),
    homeType: normalizeHomeType(raw.homeType),
    schoolScore: parseNum(raw.schoolScore),
    driveMinutesToGoogleplex: parseNum(raw.driveMinutesToGoogleplex),
    driveMinutesToOpenAIMTV: parseNum(raw.driveMinutesToOpenAIMTV),
    hasBackyard: raw.hasBackyard != null ? !!raw.hasBackyard : null,
    schoolDistrict: raw.schoolDistrict || addr.city || null,
    schools: raw.schools || {},
    lat: parseNum(raw.lat),
    lng: parseNum(raw.lng),
    soldDate: raw.soldDate || null,
    listedDate: raw.listedDate || null,
    sourceAsOf: new Date().toISOString(),
  };
}

function loadCache(path, intent, query, ttlHours = 24) {
  try {
    const obj = JSON.parse(fs.readFileSync(path, "utf8"));
    const ts = Date.parse(obj.fetchedAt || "");
    if (!Number.isFinite(ts)) return [];
    if (Date.now() - ts > ttlHours * 3600 * 1000) return [];

    const citySet = new Set((query?.area?.cities || []).map((x) => String(x).toLowerCase()));
    const zipSet = new Set((query?.constraints?.hard?.zipCodes || []).map((x) => String(x)));

    return (obj.listings || [])
      .map((x) => normalizeListing(x, intent))
      .filter((x) => {
        const cityOk = !citySet.size || citySet.has(String(x.address?.city || "").toLowerCase());
        const zipOk = !zipSet.size || zipSet.has(String(x.address?.zip || ""));
        return cityOk || zipOk;
      });
  } catch {
    return [];
  }
}

export async function searchListings(query) {
  const intent = query?.intent === "rent" ? "rent" : "buy";
  return intent === "rent"
    ? loadCache(LIVE_RENT, "rent", query, 12)
    : loadCache(LIVE_BUY, "buy", query, 24);
}
