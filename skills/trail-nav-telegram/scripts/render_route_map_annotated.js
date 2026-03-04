// Render annotated route map (GeoJSON LineString + alerts JSON) to HTML + PNG
// Usage: node render_route_map_annotated.js <geojsonPath> <alertsJsonPath> [title]
// Output: ./out/route_map_annotated.html + ./out/route_map_annotated.png
// Requires: npm i -D playwright

import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const geoPath = process.argv[2];
const alertsPath = process.argv[3];
const title = process.argv[4] || "Route (annotated)";
if (!geoPath || !alertsPath) {
  console.error("Usage: node render_route_map_annotated.js <geojsonPath> <alertsJsonPath> [title]");
  process.exit(1);
}

const geo = JSON.parse(fs.readFileSync(geoPath, "utf8"));
const alerts = JSON.parse(fs.readFileSync(alertsPath, "utf8"));
const coords = geo.features?.[0]?.geometry?.coordinates;
if (!Array.isArray(coords) || coords.length < 2) throw new Error("No coordinates in geojson");
const latlng = coords.map(([lon, lat]) => [lat, lon]);

const nodes = (alerts.nodes || []).map((n) => {
  const kind = n.kind || "node";
  return {
    letter: n.letter || "?",
    name: n.name || n.id,
    lat: n.lat,
    lon: n.lon,
    kind,
    color: colorByKind(kind),
  };
});

const outDir = path.join(process.cwd(), "out");
fs.mkdirSync(outDir, { recursive: true });
const htmlPath = path.join(outDir, "route_map_annotated.html");
const pngPath = path.join(outDir, "route_map_annotated.png");

function colorByKind(kind) {
  if (kind === "trailhead") return "#16a34a";
  if (kind === "hazard") return "#f97316";
  if (kind === "summit_or_ridge") return "#7c3aed";
  if (kind === "descent") return "#0ea5e9";
  if (kind === "finish") return "#2563eb";
  return "#111827";
}

const legendLines = nodes
  .map((n) => `<div><span class=\"tag\">${n.letter}</span> ${n.name}</div>`)
  .join("\n");

const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
  html, body { margin:0; padding:0; }
  #wrap { width: 1400px; height: 900px; position: relative; }
  #map { width: 1400px; height: 900px; }
  .panel { position:absolute; left:14px; top:14px; right:14px; display:flex; gap:12px; flex-wrap:wrap; align-items:flex-start; pointer-events:none; }
  .title { background:rgba(255,255,255,0.92); padding:10px 12px; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial; box-shadow:0 2px 12px rgba(0,0,0,0.15); }
  .title b{ font-size:16px; }
  .legend { background:rgba(255,255,255,0.92); padding:10px 12px; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial; box-shadow:0 2px 12px rgba(0,0,0,0.15); }
  .legend div{ font-size:13px; line-height:1.3; }
  .tag { display:inline-block; min-width: 18px; text-align:center; font-weight:700; }
  .label {
    background: rgba(17,24,39,0.88);
    color: #fff;
    padding: 5px 8px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.20);
    font-family: -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",Segoe UI,Roboto,Arial;
    font-size: 13px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    white-space: nowrap;
  }
</style>
</head>
<body>
<div id="wrap">
  <div id="map"></div>
  <div class="panel">
    <div class="title"><b>${title}</b><div style="font-size:13px; color:#374151; margin-top:2px;">关键风险点标注版</div></div>
    <div class="legend">${legendLines}</div>
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  const map = L.map('map', { zoomControl: true }).setView([22.523, 114.532], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' }).addTo(map);

  const line = ${JSON.stringify(latlng)};
  const poly = L.polyline(line, {color:'#e11d48', weight:4, opacity:0.95}).addTo(map);
  map.fitBounds(poly.getBounds(), {padding:[40,40]});

  function badgeIcon(letter, color) {
    const html = '<div style="width:28px;height:28px;border-radius:14px;background:' + color + ';border:2px solid rgba(255,255,255,0.95);display:flex;align-items:center;justify-content:center;box-shadow:0 2px 10px rgba(0,0,0,0.25);font-weight:800;color:#fff;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial;">' + letter + '</div>';
    return L.divIcon({ html: html, className:'', iconSize:[28,28], iconAnchor:[14,14] });
  }

  function addNode(letter, lat, lon, title, color) {
    const m = L.marker([lat, lon], { icon: badgeIcon(letter, color) }).addTo(map);
    const tip = '<span class="label"><b>' + letter + '</b> ' + title + '</span>';
    m.bindTooltip(tip, {permanent:true, direction:'right', offset:[12,0], opacity:1});
    return m;
  }

  const nodes = ${JSON.stringify(nodes)};
  for (const n of nodes) {
    addNode(n.letter, n.lat, n.lon, n.name, n.color || '#111827');
  }
</script>
</body>
</html>`;

fs.writeFileSync(htmlPath, html, "utf8");

const browser = await chromium.launch({ headless: true, channel: "chrome" });
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
await page.goto("file://" + htmlPath, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2500);
await page.screenshot({ path: pngPath, fullPage: false });
await browser.close();

console.log(pngPath);
