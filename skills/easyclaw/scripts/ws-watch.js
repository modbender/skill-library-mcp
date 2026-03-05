#!/usr/bin/env node
require("dotenv").config();

const WebSocket = require("ws");
const { parseArgs } = require("./common");
const { wsUrl } = require("./backend-common");

function usage() {
  console.log(`Usage:
  node scripts/ws-watch.js --channel system.status
  node scripts/ws-watch.js --channels "agent.signals,portfolio.updates"
  node scripts/ws-watch.js --channel "chart.ticks.1" --json

Options:
  --channel <name>       Single channel
  --channels <csv>       Comma separated channels (alternative)
  --duration-sec <n>     Auto exit after n seconds
  --once                 Exit on first event
  --json                 Print raw event JSON
`);
}

function parseChannels(args) {
  const raw =
    (typeof args.channels === "string" && args.channels) ||
    (typeof args.channel === "string" && args.channel) ||
    "system.status";

  return raw
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function toBool(value) {
  if (value === true) return true;
  if (typeof value !== "string") return false;
  const normalized = value.trim().toLowerCase();
  return normalized === "1" || normalized === "true" || normalized === "yes";
}

function toInt(value, fallback) {
  if (value === undefined || value === null || String(value).trim() === "") {
    return fallback;
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(`Invalid number: ${value}`);
  }
  return Math.floor(parsed);
}

function prettyPrint(message) {
  const channel = message.channel || "(unknown)";
  const ts = message.ts ? new Date(message.ts * 1000).toISOString() : new Date().toISOString();
  const eventType = message.type || "event";
  if (message.error) {
    console.log(`[${ts}] ${eventType} ${channel} error=${message.error}`);
    return;
  }
  const data =
    message.data === undefined || message.data === null
      ? "null"
      : JSON.stringify(message.data);
  console.log(`[${ts}] ${eventType} ${channel} data=${data}`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || args.h) {
    usage();
    return;
  }

  const channels = parseChannels(args);
  const outputJSON = toBool(args.json);
  const once = toBool(args.once);
  const durationSec = toInt(args["duration-sec"], 0);
  const endpoint = wsUrl();

  console.log(`[info] ws=${endpoint}`);
  console.log(`[info] channels=${channels.join(",")}`);

  const socket = new WebSocket(endpoint);
  let received = 0;

  let timer = null;
  if (durationSec > 0) {
    timer = setTimeout(() => {
      console.log(`[info] duration reached (${durationSec}s), closing`);
      socket.close(1000, "duration reached");
    }, durationSec * 1000);
  }

  socket.on("open", () => {
    for (const channel of channels) {
      socket.send(
        JSON.stringify({
          type: "subscribe",
          channel
        })
      );
    }
  });

  socket.on("message", (raw) => {
    let message;
    try {
      message = JSON.parse(String(raw));
    } catch (_err) {
      message = { type: "raw", data: String(raw), ts: Math.floor(Date.now() / 1000) };
    }

    received += 1;
    if (outputJSON) {
      console.log(JSON.stringify(message, null, 2));
    } else {
      prettyPrint(message);
    }

    if (once) {
      socket.close(1000, "once completed");
    }
  });

  socket.on("error", (error) => {
    console.error(`[error] websocket: ${error.message}`);
    process.exitCode = 1;
  });

  socket.on("close", (code, reason) => {
    if (timer) {
      clearTimeout(timer);
    }
    const message = reason ? reason.toString() : "";
    console.log(`[info] closed code=${code} reason=${message} events=${received}`);
  });

  const shutdown = () => {
    socket.close(1000, "signal");
  };
  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

main();
