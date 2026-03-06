#!/usr/bin/env node
/**
 * Red Alert Real-Time Listener — Socket.IO connection to redalert.orielhaim.com
 *
 * Usage:
 *   node realtime.mjs                          # Listen for all alerts
 *   node realtime.mjs --city "כפר סבא"         # Filter for specific city
 *   node realtime.mjs --test                    # Connect to /test namespace
 *   node realtime.mjs --json                    # Output JSON lines
 *   node realtime.mjs --duration 60             # Listen for N seconds then exit
 *
 * Env: RED_ALERT_API_KEY (optional, for authenticated access)
 */

import { io } from "socket.io-client";

const BASE_URL = "https://redalert.orielhaim.com";

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { json: false, test: false, duration: 0 };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--city" && args[i+1]) opts.city = args[++i];
    if (args[i] === "--test") opts.test = true;
    if (args[i] === "--json") opts.json = true;
    if (args[i] === "--duration" && args[i+1]) opts.duration = parseInt(args[++i]);
  }
  return opts;
}

function main() {
  const opts = parseArgs();
  const ns = opts.test ? "/test" : "/";

  const socket = io(`${BASE_URL}${ns}`, {
    auth: process.env.RED_ALERT_API_KEY ? { apiKey: process.env.RED_ALERT_API_KEY } : undefined,
    transports: ["websocket"]
  });

  socket.on("connect", () => {
    if (!opts.json) console.error(`Connected to ${BASE_URL}${ns} (id: ${socket.id})`);
  });

  socket.on("connect_error", (err) => {
    console.error(`Connection error: ${err.message}`);
    process.exit(1);
  });

  // Listen for all alert events
  const ALERT_EVENTS = ["alert", "rockets", "hostileAircraftIntrusion", "tsunami", "earthquake", "terroristInfiltration"];

  socket.onAny((event, ...args) => {
    if (!ALERT_EVENTS.includes(event) && event !== "alert") return;

    for (const alert of args) {
      // Filter by city if specified
      if (opts.city && alert.cities && !alert.cities.some(c => c.includes(opts.city))) continue;

      if (opts.json) {
        console.log(JSON.stringify({ event, ...alert, receivedAt: new Date().toISOString() }));
      } else {
        const cities = alert.cities?.join(", ") || "unknown";
        const type = alert.type || event;
        const time = alert.timestamp || new Date().toISOString();
        console.log(`\n🚨 [${time}] ${type.toUpperCase()}`);
        console.log(`   Cities: ${cities}`);
        if (alert.title) console.log(`   Title: ${alert.title}`);
        if (alert.instructions) console.log(`   Instructions: ${alert.instructions}`);
        if (alert.isTest) console.log(`   ⚠️  TEST ALERT`);
      }
    }
  });

  if (opts.duration > 0) {
    setTimeout(() => {
      if (!opts.json) console.error(`\nDuration ${opts.duration}s reached, disconnecting.`);
      socket.disconnect();
      process.exit(0);
    }, opts.duration * 1000);
  }

  // Graceful shutdown
  process.on("SIGINT", () => {
    socket.disconnect();
    process.exit(0);
  });
}

main();
