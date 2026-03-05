// Parse 2bulu KML (XML) → basic stats + GeoJSON line + compact RoutePack JSON
// Usage: node parse_2bulu_kml.js <kmlPath>

import fs from "node:fs";
import path from "node:path";

const kmlPath = process.argv[2];
if (!kmlPath) {
  console.error("Usage: node parse_2bulu_kml.js <kmlPath>");
  process.exit(1);
}

const text = fs.readFileSync(kmlPath, "utf8");
const name = (text.match(/<name><!\[CDATA\[(.*?)\]\]><\/name>/) || [])[1] || "route";
const mileage_m = Number((text.match(/<Data name=\"Mileage\">\s*<value>([0-9.]+)<\/value>/) || [])[1] || "0") || null;

const mBegin = text.match(/<Data name=\"BeginTime\">\s*<value>(\d+)<\/value>/);
const mEnd = text.match(/<Data name=\"EndTime\">\s*<value>(\d+)<\/value>/);
const begin_ms = mBegin ? Number(mBegin[1]) : null;
const end_ms = mEnd ? Number(mEnd[1]) : null;
const duration_s = begin_ms && end_ms ? (end_ms - begin_ms) / 1000 : null;

function parseCoord(s) {
  const parts = s.trim().split(",");
  return { lon: +parts[0], lat: +parts[1], alt: parts[2] != null ? +parts[2] : null };
}

const startName = (text.match(/<Data name=\"PosStartName\">\s*<value><!\[CDATA\[(.*?)\]\]><\/value>/) || [])[1] || null;
const endName = (text.match(/<Data name=\"PosEndName\">\s*<value><!\[CDATA\[(.*?)\]\]><\/value>/) || [])[1] || null;

const mStart = text.match(/<Placemark id=\"startPoint\"[\s\S]*?<coordinates>([^<]+)<\/coordinates>/);
const mEndPt = text.match(/<Placemark id=\"endPoint\"[\s\S]*?<coordinates>([^<]+)<\/coordinates>/);
const start = mStart ? parseCoord(mStart[1]) : null;
const end = mEndPt ? parseCoord(mEndPt[1]) : null;

// gx:coord points
const re = /<gx:coord>\s*([0-9.+-]+)\s+([0-9.+-]+)\s+([0-9.+-]+)\s*<\/gx:coord>/g;
let m;
const line = [];
let minLon = Infinity,
  minLat = Infinity,
  maxLon = -Infinity,
  maxLat = -Infinity;
let maxAlt = -Infinity;
let elevGain = 0;
let prevAlt = null;

while ((m = re.exec(text))) {
  const lon = +m[1],
    lat = +m[2],
    alt = +m[3];
  line.push([lon, lat]);
  if (lon < minLon) minLon = lon;
  if (lon > maxLon) maxLon = lon;
  if (lat < minLat) minLat = lat;
  if (lat > maxLat) maxLat = lat;
  if (alt > maxAlt) maxAlt = alt;
  if (prevAlt != null && alt > prevAlt) elevGain += alt - prevAlt;
  prevAlt = alt;
}

const routepack = {
  name,
  startName,
  endName,
  mileage_km: mileage_m ? mileage_m / 1000 : null,
  duration_s,
  max_alt_m: Number.isFinite(maxAlt) ? Math.round(maxAlt) : null,
  elev_gain_m_est: Math.round(elevGain),
  start,
  end,
  points: line.length,
  bbox: line.length ? [minLon, minLat, maxLon, maxLat] : null,
};

const geojson = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { name, startName, endName },
      geometry: { type: "LineString", coordinates: line },
    },
  ],
};

const outDir = path.join(process.cwd(), "out");
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, "routepack.json"), JSON.stringify(routepack, null, 2), "utf8");
fs.writeFileSync(path.join(outDir, "route.geojson"), JSON.stringify(geojson), "utf8");
console.log(JSON.stringify(routepack, null, 2));
