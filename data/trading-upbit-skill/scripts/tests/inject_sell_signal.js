\
/**
 * Inject a synthetic SELL_SIGNAL event to resources/events.json.
 *
 * Usage:
 *   node scripts/tests/inject_sell_signal.js --market KRW-ETH --reason MANUAL_TEST
 *
 * Run worker to process:
 *   node skill.js worker_once
 */
const path = require("path");
const { ensureResources, readJson, writeJson, nowISO, makeId } = require("./common");

function arg(name, def) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx === -1) return def;
  const v = process.argv[idx + 1];
  return v === undefined ? def : v;
}

const market = arg("market", "KRW-ETH");
const reason = arg("reason", "MANUAL_TEST");

const dir = ensureResources();
const eventsPath = path.join(dir, "events.json");
const events = readJson(eventsPath, []);

const evt = {
  id: makeId("evt"),
  type: "SELL_SIGNAL",
  market,
  payload: { reason, injected: true },
  meta: { strategy: "InjectedTest" },
  dedupeKey: `SELL_SIGNAL:${market}:INJECTED`,
  processed: false,
  createdAt: nowISO()
};

events.push(evt);
writeJson(eventsPath, events);

console.log(`[TEST] Injected SELL_SIGNAL -> ${eventsPath}`);
console.log(JSON.stringify(evt, null, 2));
