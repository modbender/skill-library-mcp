#!/usr/bin/env node

/**
 * Simulated Road Trip — GPS-grounded road trips for your Clawbot.
 *
 * Usage:
 *   node roadtrip.mjs --from "NYC" --to "LA" --theme foodie --stops 5
 *   node roadtrip.mjs --from "Salem, MA" --to "Sleepy Hollow, NY" --theme haunted --drip 1h
 *
 * Environment:
 *   TURAI_API_KEY  — Required. Your Turai API key.
 */

import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { parseArgs } from "node:util";
import { setTimeout as sleep } from "node:timers/promises";

// ---------------------------------------------------------------------------
// CLI args
// ---------------------------------------------------------------------------

const { values: args } = parseArgs({
  options: {
    from:    { type: "string", short: "f" },
    to:      { type: "string", short: "t" },
    theme:   { type: "string", default: "history" },
    stops:   { type: "string", short: "n", default: "5" },
    drip:    { type: "string", short: "d" },          // e.g. "1h", "30m", "1d"
    output:  { type: "string", short: "o" },           // save JSON
    format:  { type: "string", default: "chat" },      // chat | social | json
    help:    { type: "boolean", short: "h", default: false },
  },
  strict: true,
});

if (args.help) {
  console.log(`
Simulated Road Trip — GPS-grounded road trips for your Clawbot

Options:
  -f, --from <place>       Starting location (required)
  -t, --to <place>         Destination (required)
      --theme <theme>      Trip theme (default: history)
  -n, --stops <count>      Number of stops (default: 5)
  -d, --drip <interval>    Drip-feed interval: 30m, 1h, 2h, 4h, 1d
  -o, --output <path>      Save full trip JSON to file
      --format <fmt>       Output format: chat, social, json (default: chat)
  -h, --help               Show this help

Themes: history, foodie, haunted, weird, nature, art, architecture,
        music, literary, film, spiritual, adventure

Environment:
  TURAI_API_KEY            Your Turai API key (required)
`);
  process.exit(0);
}

const VALID_THEMES = [
  "history", "foodie", "haunted", "weird", "nature", "art",
  "architecture", "music", "literary", "film", "spiritual", "adventure",
];

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

const apiKey = process.env.TURAI_API_KEY;
if (!apiKey) {
  console.error("Error: TURAI_API_KEY environment variable is not set.");
  console.error("Get a key at https://turai.org and export TURAI_API_KEY=your-key");
  process.exit(1);
}

if (!args.from || !args.to) {
  console.error("Error: --from and --to are required.");
  console.error('Example: --from "New York City" --to "Los Angeles"');
  process.exit(1);
}

if (!VALID_THEMES.includes(args.theme)) {
  console.error(`Error: Invalid theme "${args.theme}". Valid: ${VALID_THEMES.join(", ")}`);
  process.exit(1);
}

const numStops = parseInt(args.stops, 10);
if (isNaN(numStops) || numStops < 1 || numStops > 20) {
  console.error("Error: --stops must be a number between 1 and 20.");
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Drip-feed parsing
// ---------------------------------------------------------------------------

function parseDripInterval(str) {
  if (!str) return null;
  const match = str.match(/^(\d+)(m|h|d)$/);
  if (!match) {
    console.error('Error: Invalid drip format. Use: 30m, 1h, 2h, 4h, 1d');
    process.exit(1);
  }
  const val = parseInt(match[1], 10);
  const unit = match[2];
  const multipliers = { m: 60_000, h: 3_600_000, d: 86_400_000 };
  return val * multipliers[unit];
}

const dripMs = parseDripInterval(args.drip);

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------

async function planRoadtrip({ from, to, theme, stops }) {
  const url = "https://turai.org/api/agent/roadtrip";

  const body = { from, to, theme, stops };

  console.log(`🚗 Planning road trip...`);
  console.log(`   From:   ${from}`);
  console.log(`   To:     ${to}`);
  console.log(`   Theme:  ${theme}`);
  console.log(`   Stops:  ${stops}`);
  console.log();

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => "(no body)");
    throw new Error(`API error ${res.status}: ${errText}`);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// Formatters
// ---------------------------------------------------------------------------

function formatChat(stop, index, total) {
  const parts = [];
  const num = `[${index + 1}/${total}]`;

  const name = stop.name || stop.location || `Stop ${index + 1}`;
  parts.push(`📍 ${num} ${name}`);

  if (stop.coordinates) {
    const { lat, lng } = stop.coordinates;
    parts.push(`   🌐 ${lat}, ${lng}`);
  }

  if (stop.distance) parts.push(`   🛣️  ${stop.distance}`);
  if (stop.duration) parts.push(`   ⏱️  ${stop.duration}`);

  parts.push("");

  const narration = stop.narration || stop.description || stop.text || "";
  if (narration) parts.push(narration);

  if (stop.tips) parts.push(`\n💡 ${stop.tips}`);

  return parts.join("\n");
}

function formatSocial(stop, index, total) {
  const name = stop.name || stop.location || `Stop ${index + 1}`;
  const narration = stop.narration || stop.description || stop.text || "";
  const hashtag = args.theme ? `#${args.theme}` : "";

  let post = `📍 ${name}\n\n${narration}`;
  if (stop.coordinates) {
    const { lat, lng } = stop.coordinates;
    post += `\n\n📌 ${lat}, ${lng}`;
  }
  post += `\n\n🚗 Stop ${index + 1} of ${total} ${hashtag} #roadtrip`;
  return post;
}

function formatStop(stop, index, total) {
  switch (args.format) {
    case "social": return formatSocial(stop, index, total);
    case "json":   return JSON.stringify(stop, null, 2);
    default:       return formatChat(stop, index, total);
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const tripData = await planRoadtrip({
    from: args.from,
    to: args.to,
    theme: args.theme,
    stops: numStops,
  });

  // Handle various response shapes
  const stops = tripData.stops || tripData.route || tripData.legs || tripData;
  const stopsArray = Array.isArray(stops) ? stops : [stops];

  if (stopsArray.length === 0) {
    console.log("⚠️  No stops returned. Full response:");
    console.log(JSON.stringify(tripData, null, 2));
    process.exit(1);
  }

  console.log(`🗺️  Road trip planned! ${stopsArray.length} stops.\n`);

  // Save full JSON if requested
  if (args.output) {
    const outPath = resolve(args.output);
    await writeFile(outPath, JSON.stringify(tripData, null, 2));
    console.log(`💾 Full trip data saved to: ${outPath}\n`);
  }

  // Output each stop
  for (let i = 0; i < stopsArray.length; i++) {
    const formatted = formatStop(stopsArray[i], i, stopsArray.length);
    console.log(formatted);
    console.log("\n" + "─".repeat(60) + "\n");

    // Drip-feed: wait between stops (skip after last)
    if (dripMs && i < stopsArray.length - 1) {
      const nextIn = args.drip;
      console.log(`⏳ Next stop in ${nextIn}... (drip-feed mode)`);
      await sleep(dripMs);
    }
  }

  console.log("🏁 Trip complete!");
}

main().catch((err) => {
  console.error("❌ Error:", err.message);
  process.exit(1);
});
