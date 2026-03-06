#!/usr/bin/env npx tsx

// StrikeRadar CLI - US-Iran strike probability monitor
// Wraps https://api.usstrikeradar.com (by Yonatan Back)

const BASE_URL = "https://api.usstrikeradar.com";
const TIMEOUT = 10_000;
const SIGNAL_NAMES = ["news", "connectivity", "energy", "flight", "tanker", "weather", "polymarket", "pentagon"] as const;

const isAgent = !process.stdout.isTTY;
const BOLD = "\x1b[1m";
const DIM = "\x1b[2m";
const RESET = "\x1b[0m";

// --- Types ---

interface Signal {
  risk: number;
  detail: string;
  history: number[];
  raw_data: Record<string, any>;
}

interface StrikeData {
  news: Signal;
  connectivity: Signal;
  energy: Signal;
  flight: Signal;
  tanker: Signal;
  weather: Signal;
  polymarket: Signal;
  pentagon: Signal;
  total_risk: { risk: number; detail: string };
  last_updated: string;
}

interface PulseData {
  watching_now: number;
  activity_multiplier: number;
  activity_level: string;
  israel: { count: number; surge: number };
  countries: Array<{ cc: string; flag: string; count: number; surge: number }>;
  total_countries: number;
}

// --- API ---

async function getData(): Promise<StrikeData> {
  const res = await fetch(`${BASE_URL}/api/data`, { signal: AbortSignal.timeout(TIMEOUT) });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function getPulse(): Promise<PulseData> {
  const res = await fetch(`${BASE_URL}/api/pulse`, { method: "POST", signal: AbortSignal.timeout(TIMEOUT) });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// --- Output helpers ---

function emitJson(command: string, result: any, nextActions: Array<{ command: string; description: string }> = []) {
  console.log(JSON.stringify({ ok: true, command, result, next_actions: nextActions }));
}

function emitError(command: string, message: string, fix: string) {
  if (isAgent) {
    console.log(JSON.stringify({ ok: false, command, error: { message }, fix }));
  } else {
    console.error(`Error: ${message}\nFix: ${fix}`);
  }
  process.exit(1);
}

function riskColor(risk: number): string {
  if (risk >= 70) return "\x1b[31m";
  if (risk >= 40) return "\x1b[33m";
  return "\x1b[32m";
}

// --- Commands ---

async function statusCommand() {
  try {
    const data = await getData();
    const result = {
      total_risk: data.total_risk.risk,
      last_updated: data.last_updated,
      signals: Object.fromEntries(
        SIGNAL_NAMES.map((name) => [name, { risk: data[name].risk, detail: data[name].detail }])
      ),
    };

    if (isAgent) {
      emitJson("strikeradar status", result, [
        { command: "strikeradar signal news", description: "View news signal details" },
        { command: "strikeradar signal flight", description: "View flight tracking details" },
        { command: "strikeradar pulse", description: "See live viewer count" },
      ]);
      return;
    }

    const total = data.total_risk.risk;
    const filled = Math.round(total / 5);
    console.log();
    console.log(`${BOLD}  US Strike Radar${RESET}  ${DIM}${data.last_updated}${RESET}`);
    console.log();
    console.log(`  ${BOLD}Total Risk: ${riskColor(total)}${total}%${RESET}`);
    console.log(`  ${DIM}${"█".repeat(filled)}${"░".repeat(20 - filled)}${RESET}`);
    console.log();
    for (const name of SIGNAL_NAMES) {
      const sig = data[name];
      console.log(`  ${name.padEnd(14)} ${riskColor(sig.risk)}${String(sig.risk).padStart(3)}%${RESET}  ${DIM}${sig.detail}${RESET}`);
    }
    console.log();
  } catch (err: any) {
    emitError("strikeradar status", err.message, "Check your internet connection or try again later");
  }
}

async function signalCommand(name: string) {
  if (!SIGNAL_NAMES.includes(name as any)) {
    emitError(`strikeradar signal ${name}`, `Unknown signal: ${name}`, `Valid signals: ${SIGNAL_NAMES.join(", ")}`);
    return;
  }

  try {
    const data = await getData();
    const signal = data[name as keyof StrikeData] as Signal;

    if (isAgent) {
      emitJson(`strikeradar signal ${name}`, { name, ...signal }, [
        { command: "strikeradar status", description: "View all signals overview" },
        { command: "strikeradar pulse", description: "See live viewer count" },
      ]);
      return;
    }

    console.log();
    console.log(`${BOLD}  ${name.toUpperCase()}${RESET}  Risk: ${signal.risk}%`);
    console.log(`  ${DIM}${signal.detail}${RESET}`);
    console.log();

    const raw = signal.raw_data;
    if (!raw) return;

    if (name === "news" && raw.articles) {
      console.log(`  ${BOLD}Articles${RESET} (${raw.total_count} total, ${raw.alert_count} critical)`);
      for (const art of raw.articles.slice(0, 10)) {
        const marker = art.is_alert ? "\x1b[31m!\x1b[0m" : " ";
        console.log(`  ${marker} ${art.title}`);
      }
    } else if (name === "flight") {
      console.log(`  ${BOLD}Aircraft${RESET}: ${raw.aircraft_count} in region`);
      console.log(`  ${BOLD}Airlines${RESET}: ${raw.key_airlines_present}/${raw.key_airlines_expected} key airlines present`);
      if (raw.airlines?.length) console.log(`  ${DIM}Active: ${raw.airlines.join(", ")}${RESET}`);
    } else if (name === "energy") {
      console.log(`  ${BOLD}Oil Price${RESET}: $${raw.price} (${raw.change_pct > 0 ? "+" : ""}${raw.change_pct}%)`);
      console.log(`  ${BOLD}Status${RESET}: ${raw.status}  ${BOLD}Volatility${RESET}: ${raw.volatility_index}`);
      if (raw.market_closed) console.log(`  ${DIM}Market closed${RESET}`);
    } else if (name === "pentagon") {
      console.log(`  ${BOLD}Status${RESET}: ${raw.status}  ${BOLD}Score${RESET}: ${raw.score}`);
      if (raw.places?.length) for (const p of raw.places) if (p.score > 0) console.log(`    ${p.name}: ${p.status} (${p.score})`);
    } else if (name === "connectivity") {
      console.log(`  ${BOLD}Status${RESET}: ${raw.status}  ${BOLD}Trend${RESET}: ${raw.trend}`);
    } else if (name === "polymarket") {
      console.log(`  ${BOLD}Market${RESET}: ${raw.market}  ${BOLD}Odds${RESET}: ${raw.odds}%`);
    } else if (name === "tanker") {
      console.log(`  ${BOLD}Tankers${RESET}: ${raw.tanker_count} detected`);
      if (raw.callsigns?.length) console.log(`  ${BOLD}Callsigns${RESET}: ${raw.callsigns.join(", ")}`);
    } else if (name === "weather") {
      console.log(`  ${BOLD}Condition${RESET}: ${raw.description}  ${BOLD}Temp${RESET}: ${raw.temp}  ${BOLD}Visibility${RESET}: ${raw.visibility}`);
    } else {
      console.log(JSON.stringify(raw, null, 2));
    }
    console.log();
  } catch (err: any) {
    emitError(`strikeradar signal ${name}`, err.message, "Check your internet connection or try again later");
  }
}

async function pulseCommand() {
  try {
    const pulse = await getPulse();

    if (isAgent) {
      emitJson("strikeradar pulse", pulse, [
        { command: "strikeradar status", description: "View risk status" },
        { command: "strikeradar signal news", description: "View news details" },
      ]);
      return;
    }

    console.log();
    console.log(`${BOLD}  Live Pulse${RESET}`);
    console.log();
    console.log(`  ${BOLD}Watching now${RESET}: ${pulse.watching_now.toLocaleString()}`);
    console.log(`  ${BOLD}Activity${RESET}: ${pulse.activity_level} (${pulse.activity_multiplier}x)`);
    console.log(`  ${BOLD}Countries${RESET}: ${pulse.total_countries}`);
    if (pulse.israel) console.log(`  ${BOLD}Israel${RESET}: ${pulse.israel.count.toLocaleString()} viewers (surge: ${pulse.israel.surge}x)`);
    if (pulse.countries?.length) {
      console.log();
      for (const c of pulse.countries.slice(0, 10)) {
        console.log(`  ${c.flag} ${c.cc.padEnd(4)} ${String(c.count).padStart(6)} viewers  ${DIM}surge: ${c.surge}x${RESET}`);
      }
    }
    console.log();
  } catch (err: any) {
    emitError("strikeradar pulse", err.message, "Check your internet connection or try again later");
  }
}

// --- Main ---

const [cmd, ...args] = process.argv.slice(2);

switch (cmd) {
  case "signal":
    if (!args[0]) emitError("strikeradar signal", "Missing signal name", `Usage: strikeradar signal <${SIGNAL_NAMES.join("|")}>`);
    else signalCommand(args[0]);
    break;
  case "pulse":
    pulseCommand();
    break;
  case "status":
  default:
    if (!cmd && isAgent) {
      emitJson("strikeradar", {
        description: "US-Iran strike probability monitor",
        commands: [
          { command: "strikeradar status", description: "All signals with risk scores" },
          { command: "strikeradar signal <name>", description: "Deep dive into one signal" },
          { command: "strikeradar pulse", description: "Live viewer count by country" },
        ],
      }, [
        { command: "strikeradar status", description: "All signals with risk scores" },
        { command: "strikeradar signal <name>", description: "Deep dive into one signal" },
        { command: "strikeradar pulse", description: "Live viewer count by country" },
      ]);
    } else {
      statusCommand();
    }
    break;
}
