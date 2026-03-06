\
/**
 * Add or update a synthetic position in resources/positions.json (for SELL tests).
 *
 * Usage:
 *   node scripts/tests/set_position.js --market KRW-XRP --amount 5 --avgBuy 2300 --peak 2350
 */
const path = require("path");
const { ensureResources, readJson, writeJson, nowISO } = require("./common");

function arg(name, def) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx === -1) return def;
  const v = process.argv[idx + 1];
  return v === undefined ? def : v;
}
function numArg(name, def) {
  const v = arg(name, undefined);
  if (v === undefined) return def;
  const n = Number(v);
  return Number.isFinite(n) ? n : def;
}

const market = arg("market", "KRW-XRP");
const amount = numArg("amount", 1);
const avgBuy = numArg("avgBuy", 2300);
const peak = numArg("peak", avgBuy);

const dir = ensureResources();
const posPath = path.join(dir, "positions.json");
const doc = readJson(posPath, { positions: [] });

let p = doc.positions.find(x => x.market === market);
if (!p) {
  p = { market };
  doc.positions.push(p);
}
p.amount = amount;
p.avgBuyPrice = avgBuy;
p.peakPrice = peak;
p.updatedAt = nowISO();
p.injected = true;

writeJson(posPath, doc);

console.log(`[TEST] Set position for ${market} -> ${posPath}`);
console.log(JSON.stringify(p, null, 2));
