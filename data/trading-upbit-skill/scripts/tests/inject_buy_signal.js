\
/**
 * Inject a synthetic BUY_SIGNAL event to resources/events.json.
 *
 * Usage:
 *   node scripts/tests/inject_buy_signal.js --market KRW-XRP --budget 10000 --price 2300 --target 2310 --ratio 0.995 --breakout false --near true --momentum true
 *
 * Notes:
 * - This does NOT place a real order by itself. It just writes a pending event.
 * - Run: node skill.js worker_once  (or run_worker_once.js) to process it.
 */
const path = require("path");
const { ensureResources, readJson, writeJson, nowISO, makeId } = require("./common");

function arg(name, def) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx === -1) return def;
  const v = process.argv[idx + 1];
  if (v === undefined) return def;
  return v;
}
function boolArg(name, def) {
  const v = arg(name, undefined);
  if (v === undefined) return def;
  return v === "true" || v === "1" || v === "yes";
}
function numArg(name, def) {
  const v = arg(name, undefined);
  if (v === undefined) return def;
  const n = Number(v);
  return Number.isFinite(n) ? n : def;
}

const market = arg("market", "KRW-XRP");
const budgetKRW = numArg("budget", 10000);
const price = numArg("price", NaN);
const targetPrice = numArg("target", NaN);
const ratio = numArg("ratio", NaN);
const breakout = boolArg("breakout", false);
const near = boolArg("near", true);
const momentumOk = boolArg("momentum", true);

const dir = ensureResources();
const eventsPath = path.join(dir, "events.json");
const events = readJson(eventsPath, []);

const evt = {
  id: makeId("evt"),
  type: "BUY_SIGNAL",
  market,
  budgetKRW,
  payload: {
    price: Number.isFinite(price) ? price : undefined,
    targetPrice: Number.isFinite(targetPrice) ? targetPrice : undefined,
    ratio: Number.isFinite(ratio) ? ratio : undefined,
    breakout,
    near,
    momentumOk,
    injected: true
  },
  meta: { strategy: "InjectedTest" },
  dedupeKey: `BUY_SIGNAL:${market}:INJECTED`,
  processed: false,
  createdAt: nowISO()
};

events.push(evt);
writeJson(eventsPath, events);

console.log(`[TEST] Injected BUY_SIGNAL -> ${eventsPath}`);
console.log(JSON.stringify(evt, null, 2));
