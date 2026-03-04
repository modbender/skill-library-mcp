// Scrape public 2bulu track search/list page → JSON/CSV + screenshot
// Usage: node scrape_2bulu_tracks.js "https://www.2bulu.com/track/track_search.htm" 30
// Requires: npm i -D playwright

import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const START_URL = process.argv[2] || "https://www.2bulu.com/track/track_search.htm";
const LIMIT = Number(process.argv[3] || 30);
const OUT_DIR = path.join(process.cwd(), "out");
fs.mkdirSync(OUT_DIR, { recursive: true });

function toCSV(rows) {
  const cols = ["title", "url", "track_id_enc", "scraped_at"]; 
  const esc = (s) => `"${String(s ?? "").replaceAll('"', '""')}"`;
  return [
    cols.join(","),
    ...rows.map((r) => cols.map((c) => esc(r[c])).join(",")),
  ].join("\n");
}

const browser = await chromium.launch({ headless: true, channel: "chrome" });
const page = await browser.newPage();

await page.goto(START_URL, { waitUntil: "domcontentloaded" });
await page.waitForSelector('a[href*="/track/t-"]', { timeout: 30000 });
await page.waitForTimeout(800);

await page.screenshot({ path: path.join(OUT_DIR, "2bulu_track_search.png"), fullPage: true });

const items = await page.evaluate(() => {
  const as = Array.from(document.querySelectorAll('a[href*="/track/t-"]'));
  return as
    .map((a) => ({
      title: (a.innerText || "").trim(),
      url: a.href,
    }))
    .filter((x) => x.url && x.url.includes('/track/t-'));
});

const now = new Date().toISOString();
const uniq = new Map();
for (const x of items) {
  const url = String(x.url || "");
  const urlNorm = url.split("?")[0].split("#")[0];
  const m = urlNorm.match(/\/track\/t-([^.]*)\.htm/i);
  const track_id_enc = m ? m[1] : "";
  if (!track_id_enc) continue;
  const row = { title: String(x.title || "").trim(), url: urlNorm, track_id_enc, scraped_at: now };
  const prev = uniq.get(track_id_enc);
  if (!prev || (!prev.title && row.title)) uniq.set(track_id_enc, row);
}

const rows = Array.from(uniq.values()).slice(0, LIMIT);
fs.writeFileSync(path.join(OUT_DIR, "2bulu_tracks.json"), JSON.stringify(rows, null, 2), "utf-8");
fs.writeFileSync(path.join(OUT_DIR, "2bulu_tracks.csv"), toCSV(rows), "utf-8");

await browser.close();
console.log(`OK: scraped ${rows.length} tracks -> out/`);
