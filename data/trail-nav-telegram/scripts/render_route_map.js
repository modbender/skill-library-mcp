// Render a GeoJSON LineString into an HTML map + PNG screenshot (Leaflet + Playwright)
// Usage: node render_route_map.js <geojsonPath> [title]
// Requires: npm i -D playwright

import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const geoPath = process.argv[2];
if (!geoPath) {
  console.error("Usage: node render_route_map.js <geojsonPath> [title]");
  process.exit(1);
}
const title = process.argv[3] || "Route";

const geo = JSON.parse(fs.readFileSync(geoPath, "utf8"));
const coords = geo.features?.[0]?.geometry?.coordinates;
if (!Array.isArray(coords) || !coords.length) throw new Error("No coordinates");

let minLon = Infinity,
  minLat = Infinity,
  maxLon = -Infinity,
  maxLat = -Infinity;
for (const [lon, lat] of coords) {
  if (lon < minLon) minLon = lon;
  if (lon > maxLon) maxLon = lon;
  if (lat < minLat) minLat = lat;
  if (lat > maxLat) maxLat = lat;
}
const centerLon = (minLon + maxLon) / 2;
const centerLat = (minLat + maxLat) / 2;

const outDir = path.join(process.cwd(), "out");
fs.mkdirSync(outDir, { recursive: true });
const htmlPath = path.join(outDir, "route_map.html");
const pngPath = path.join(outDir, "route_map.png");

const latlng = coords.map(([lon, lat]) => [lat, lon]);

const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
  html, body { margin:0; padding:0; }
  #map { width: 1200px; height: 800px; }
  .panel { position:absolute; left:12px; top:12px; background:rgba(255,255,255,0.92); padding:10px 12px; border-radius:10px; font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial; font-size:14px; line-height:1.3; box-shadow:0 2px 12px rgba(0,0,0,0.15); }
  .panel b { font-size:15px; }
</style>
</head>
<body>
<div id="map"></div>
<div class="panel"><b>${title}</b></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  const map = L.map('map').setView([${centerLat}, ${centerLon}], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' }).addTo(map);
  const line = ${JSON.stringify(latlng)};
  const poly = L.polyline(line, {color:'#e11d48', weight:4}).addTo(map);
  map.fitBounds(poly.getBounds(), {padding:[30,30]});
  L.circleMarker(line[0], {radius:6, color:'#16a34a', fillColor:'#16a34a', fillOpacity:1}).addTo(map).bindPopup('Start');
  L.circleMarker(line[line.length-1], {radius:6, color:'#2563eb', fillColor:'#2563eb', fillOpacity:1}).addTo(map).bindPopup('End');
</script>
</body>
</html>`;

fs.writeFileSync(htmlPath, html, "utf8");

const browser = await chromium.launch({ headless: true, channel: "chrome" });
const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
await page.goto("file://" + htmlPath, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2500);
await page.screenshot({ path: pngPath, fullPage: false });
await browser.close();

console.log(pngPath);
