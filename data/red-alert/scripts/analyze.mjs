#!/usr/bin/env node
/**
 * Red Alert Analyzer — Fetch alert history and compute shelter stats for a city.
 *
 * Usage:
 *   node analyze.mjs --city "כפר סבא" --since "2026-02-28T08:00"
 *   node analyze.mjs --city "כפר סבא" --since "2026-02-28T08:00" --format chart-json
 *   node analyze.mjs --city "כפר סבא" --since "2026-02-28T08:00" --format table-json
 *   node analyze.mjs --city "כפר סבא" --since "2026-02-28T08:00" --format summary-json
 *   node analyze.mjs --nationwide --since "2026-02-28T08:00" --format chart-json
 */

import https from "https";

const TZEVAADOM_URL = "https://api.tzevaadom.co.il/alerts-history";
const ISRAEL_OFFSET_MS = 2 * 60 * 60 * 1000; // UTC+2 (winter)

// Shelter times by city pattern (seconds)
const SHELTER_TIMES = {
  "שדרות": 15, "אשכלון": 30, "אשדוד": 45, "באר שבע": 45,
  "תל אביב": 90, "כפר סבא": 90, "נתניה": 90, "רמת גן": 90,
  "פתח תקווה": 90, "ראשון לציון": 90, "חולון": 90,
  "חיפה": 60, "חדרה": 60,
  "default": 90
};

const THREAT_MAP = {
  0: "Rockets & Missiles", 1: "Hostile Aircraft", 2: "Earthquake",
  3: "Tsunami", 5: "Terrorist Infiltration"
};

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { format: "text", shelterTime: null };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--city" && args[i+1]) opts.city = args[++i];
    if (args[i] === "--since" && args[i+1]) opts.since = args[++i];
    if (args[i] === "--format" && args[i+1]) opts.format = args[++i];
    if (args[i] === "--nationwide") opts.nationwide = true;
    if (args[i] === "--shelter-time" && args[i+1]) opts.shelterTime = parseInt(args[++i]);
    if (args[i] === "--json") opts.format = "summary-json";
  }
  return opts;
}

function fetchJSON(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = "";
      res.on("data", (chunk) => data += chunk);
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error(`Failed to parse: ${data.slice(0, 200)}`)); }
      });
    }).on("error", reject);
  });
}

function toIsraelStr(ts) {
  return new Date(ts * 1000 + ISRAEL_OFFSET_MS).toISOString().replace("T", " ").slice(0, 16);
}

function toIsraelDate(ts) {
  const d = new Date(ts * 1000 + ISRAEL_OFFSET_MS);
  const dd = String(d.getUTCDate()).padStart(2, "0");
  const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
  return `${dd}/${mm} ${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")}`;
}

function toHour(ts) {
  const d = new Date(ts * 1000 + ISRAEL_OFFSET_MS);
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return `${months[d.getUTCMonth()]} ${d.getUTCDate()} ${String(d.getUTCHours()).padStart(2,"0")}:00`;
}

function getShelterTime(city) {
  for (const [pattern, time] of Object.entries(SHELTER_TIMES)) {
    if (pattern !== "default" && city.includes(pattern)) return time;
  }
  return SHELTER_TIMES.default;
}

async function main() {
  const opts = parseArgs();
  if (!opts.city && !opts.nationwide) {
    console.error("Usage: node analyze.mjs --city \"כפר סבא\" [--since ISO] [--format text|chart-json|table-json|summary-json]");
    process.exit(1);
  }

  const data = await fetchJSON(TZEVAADOM_URL);
  const sinceTs = opts.since ? new Date(opts.since).getTime() / 1000 : 0;
  const shelterSec = opts.shelterTime || (opts.city ? getShelterTime(opts.city) : 90);

  // Filter alerts
  let cityAlerts = [];
  let allAlerts = [];

  for (const record of data) {
    for (const alert of (record.alerts || [])) {
      if (alert.time < sinceTs) continue;
      allAlerts.push(alert);
      if (opts.city) {
        const match = alert.cities?.some(c => c.includes(opts.city));
        if (match) cityAlerts.push(alert);
      }
    }
  }

  const alerts = opts.nationwide ? allAlerts : cityAlerts;
  alerts.sort((a, b) => a.time - b.time);

  // Compute shelter sessions (alerts within 10 min = same session)
  const sessions = [];
  if (alerts.length > 0) {
    let cs = alerts[0].time, ce = cs + shelterSec, count = 1;
    for (let i = 1; i < alerts.length; i++) {
      if (alerts[i].time - ce < 600) {
        ce = alerts[i].time + shelterSec;
        count++;
      } else {
        sessions.push({ start: cs, end: ce, alerts: count });
        cs = alerts[i].time; ce = cs + shelterSec; count = 1;
      }
    }
    sessions.push({ start: cs, end: ce, alerts: count });
  }

  const totalShelter = sessions.reduce((s, x) => s + (x.end - x.start), 0);

  // Hourly counts
  const hourly = {};
  for (const a of alerts) {
    const h = toHour(a.time);
    hourly[h] = (hourly[h] || 0) + 1;
  }

  // Threat breakdown
  const threats = {};
  for (const a of alerts) {
    const t = THREAT_MAP[a.threat] || `Unknown(${a.threat})`;
    threats[t] = (threats[t] || 0) + 1;
  }

  // Output based on format
  const label = opts.nationwide ? "Nationwide" : opts.city;

  if (opts.format === "chart-json") {
    const chartData = Object.entries(hourly).sort().map(([x, y]) => ({ x, y }));
    process.stdout.write(JSON.stringify(chartData));
  } else if (opts.format === "table-json") {
    const tableData = sessions.map((s, i) => {
      const dur = Math.round(s.end - s.start);
      return {
        "#": i + 1,
        Date: toIsraelDate(s.start).split(" ")[0],
        Time: `${toIsraelDate(s.start).split(" ")[1]}-${toIsraelDate(s.end).split(" ")[1]}`,
        Duration: `${Math.floor(dur/60)}m ${dur%60}s`,
        Alerts: s.alerts
      };
    });
    process.stdout.write(JSON.stringify(tableData));
  } else if (opts.format === "summary-json") {
    process.stdout.write(JSON.stringify({
      city: label,
      totalAlerts: alerts.length,
      shelterSessions: sessions.length,
      totalShelterSeconds: totalShelter,
      totalShelterMinutes: Math.round(totalShelter / 60 * 10) / 10,
      threats,
      hourly,
      sessions: sessions.map(s => ({
        start: toIsraelStr(s.start),
        end: toIsraelStr(s.end),
        durationSec: Math.round(s.end - s.start),
        alerts: s.alerts
      }))
    }, null, 2));
  } else {
    // Text output
    console.log(`\n🚨 ${label} — Alert Analysis`);
    console.log(`   Since: ${opts.since || "all available"}`);
    console.log(`   Alerts: ${alerts.length}`);
    console.log(`   Shelter sessions: ${sessions.length}`);
    console.log(`   Total shelter time: ${Math.floor(totalShelter/60)}m ${Math.round(totalShelter%60)}s`);
    console.log(`   Shelter time per alert: ${shelterSec}s`);
    console.log(`\n   Threat breakdown:`);
    for (const [t, c] of Object.entries(threats)) console.log(`     ${t}: ${c}`);
    console.log(`\n   Shelter sessions:`);
    for (const [i, s] of sessions.entries()) {
      const dur = Math.round(s.end - s.start);
      console.log(`     #${i+1}: ${toIsraelDate(s.start)} - ${toIsraelDate(s.end).split(" ")[1]} (${Math.floor(dur/60)}m${dur%60}s, ${s.alerts} alerts)`);
    }
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
