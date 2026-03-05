/**
 * Quick integration test for XMD skill read-only tools.
 * Calls mainnet xmd.token / xmd.treasury directly — no signing needed.
 *
 * Usage: node test-read.mjs
 */

const RPC = 'https://proton.eosusa.io';
const XMD_TOKEN = 'xmd.token';
const XMD_TREASURY = 'xmd.treasury';
const ORACLE = 'oracles';

async function getTableRows(opts) {
  const resp = await fetch(`${RPC}/v1/chain/get_table_rows`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      json: true,
      code: opts.code,
      scope: opts.scope,
      table: opts.table,
      lower_bound: opts.lower_bound,
      upper_bound: opts.upper_bound,
      limit: opts.limit || 100,
    }),
  });
  const data = await resp.json();
  return data.rows || [];
}

function parseExtSym(sym) {
  if (!sym) return null;
  const parts = (sym.sym || '').split(',');
  if (parts.length !== 2) return null;
  return { precision: parseInt(parts[0]), symbol: parts[1].trim(), contract: sym.contract || '' };
}

function parseQuantity(qty) {
  const parts = qty.trim().split(' ');
  if (parts.length !== 2) return null;
  return { amount: parseFloat(parts[0]), symbol: parts[1] };
}

let passed = 0;
let failed = 0;

function assert(condition, msg) {
  if (condition) { passed++; console.log(`  PASS: ${msg}`); }
  else { failed++; console.log(`  FAIL: ${msg}`); }
}

// ── Test 1: xmd_get_config ──
console.log('\n--- xmd_get_config ---');
const globals = await getTableRows({ code: XMD_TREASURY, scope: XMD_TREASURY, table: 'xmdglobals', limit: 1 });
assert(globals.length === 1, 'xmdglobals singleton exists');
assert(globals[0].isPaused === 0, 'Treasury is not paused');
assert(globals[0].feeAccount === 'fee.metal', `Fee account = fee.metal (got ${globals[0].feeAccount})`);
assert(parseFloat(globals[0].minOraclePrice) >= 0.99, `Min oracle price >= 0.99 (got ${globals[0].minOraclePrice})`);

// ── Test 2: xmd_list_collateral ──
console.log('\n--- xmd_list_collateral ---');
const tokens = await getTableRows({ code: XMD_TREASURY, scope: XMD_TREASURY, table: 'tokens', limit: 50 });
assert(tokens.length >= 4, `Found ${tokens.length} collateral types (expected >= 4)`);

const xusdc = tokens.find(t => parseExtSym(t.symbol)?.symbol === 'XUSDC');
assert(!!xusdc, 'XUSDC collateral exists');
assert(parseExtSym(xusdc.symbol)?.contract === 'xtokens', 'XUSDC contract = xtokens');
assert(!!xusdc.isMintEnabled, 'XUSDC mint enabled');
assert(!!xusdc.isRedeemEnabled, 'XUSDC redeem enabled');
assert(parseFloat(xusdc.maxTreasuryPercent) === 60, `XUSDC max treasury = 60% (got ${xusdc.maxTreasuryPercent})`);
assert(parseFloat(xusdc.mintFee) === 0, `XUSDC mint fee = 0 (got ${xusdc.mintFee})`);
assert(parseFloat(xusdc.redemptionFee) === 0, `XUSDC redemption fee = 0 (got ${xusdc.redemptionFee})`);
assert(xusdc.oracleIndex === 5, `XUSDC oracle index = 5 (got ${xusdc.oracleIndex})`);
assert(parseFloat(xusdc.amountMinted) > 100000000, `XUSDC total minted > $100M (got ${parseFloat(xusdc.amountMinted).toFixed(0)})`);

const xpax = tokens.find(t => parseExtSym(t.symbol)?.symbol === 'XPAX');
assert(!!xpax, 'XPAX collateral exists');
assert(parseExtSym(xpax.symbol)?.contract === 'xtokens', 'XPAX contract = xtokens');

const xpyusd = tokens.find(t => parseExtSym(t.symbol)?.symbol === 'XPYUSD');
assert(!!xpyusd, 'XPYUSD collateral exists');

const mpd = tokens.find(t => parseExtSym(t.symbol)?.symbol === 'MPD');
assert(!!mpd, 'MPD collateral exists');
assert(parseExtSym(mpd.symbol)?.contract === 'mpd.token', 'MPD contract = mpd.token');

// ── Test 3: xmd_get_supply ──
console.log('\n--- xmd_get_supply ---');
const stats = await getTableRows({ code: XMD_TOKEN, scope: 'XMD', table: 'stat', limit: 1 });
assert(stats.length === 1, 'XMD stat row exists');
const supply = parseQuantity(stats[0].supply);
assert(supply.symbol === 'XMD', `Symbol = XMD`);
assert(supply.amount > 1000000, `Supply > 1M XMD (got ${supply.amount.toLocaleString()})`);
assert(stats[0].issuer === 'xmd.treasury', `Issuer = xmd.treasury (got ${stats[0].issuer})`);
const maxSupply = parseQuantity(stats[0].max_supply);
assert(maxSupply.amount === 0, `Max supply = 0 (unlimited)`);

// ── Test 4: xmd_get_balance ──
console.log('\n--- xmd_get_balance ---');
const balRows = await getTableRows({ code: XMD_TOKEN, scope: 'jamestaggart', table: 'accounts', limit: 5 });
const xmdBal = balRows.find(r => parseQuantity(r.balance)?.symbol === 'XMD');
assert(!!xmdBal, `jamestaggart has XMD balance`);
assert(parseQuantity(xmdBal.balance).amount > 0, `Balance > 0 (got ${xmdBal.balance})`);

// Non-existent user
const noBal = await getTableRows({ code: XMD_TOKEN, scope: 'zzzzzzzzzzz1', table: 'accounts', limit: 5 });
assert(noBal.length === 0, 'Non-existent user returns empty');

// ── Test 5: xmd_get_treasury_reserves ──
console.log('\n--- xmd_get_treasury_reserves ---');
const xusdcBal = await getTableRows({ code: 'xtokens', scope: XMD_TREASURY, table: 'accounts', limit: 20 });
const xusdcReserve = xusdcBal.find(r => parseQuantity(r.balance)?.symbol === 'XUSDC');
assert(!!xusdcReserve, 'Treasury holds XUSDC');
const xusdcAmount = parseQuantity(xusdcReserve.balance).amount;
assert(xusdcAmount > 100000, `XUSDC reserve > $100k (got ${xusdcAmount.toLocaleString()})`);

// Check total reserves roughly match XMD supply
let totalReserves = 0;
for (const row of xusdcBal) {
  const parsed = parseQuantity(row.balance);
  if (parsed) totalReserves += parsed.amount;
}
const mpdBal = await getTableRows({ code: 'mpd.token', scope: XMD_TREASURY, table: 'accounts', limit: 5 });
for (const row of mpdBal) {
  const parsed = parseQuantity(row.balance);
  if (parsed) totalReserves += parsed.amount;
}
const ratio = (totalReserves / supply.amount) * 100;
assert(ratio > 90 && ratio < 110, `Collateralization ratio ${ratio.toFixed(1)}% (expected ~100%)`);

// ── Test 6: xmd_get_oracle_price ──
console.log('\n--- xmd_get_oracle_price (XUSDC = feed 5) ---');
const oracleData = await getTableRows({ code: ORACLE, scope: ORACLE, table: 'data', lower_bound: 5, upper_bound: 5, limit: 1 });
assert(oracleData.length === 1, 'USDC/USD oracle data exists');
const usdcPrice = parseFloat(oracleData[0].aggregate?.d_double || 0);
assert(usdcPrice >= 0.99 && usdcPrice <= 1.01, `USDC/USD price = ${usdcPrice} (expected ~1.0)`);
assert(Array.isArray(oracleData[0].points), 'Has provider data points');

// PAX oracle
console.log('\n--- xmd_get_oracle_price (XPAX = feed 14) ---');
const paxOracle = await getTableRows({ code: ORACLE, scope: ORACLE, table: 'data', lower_bound: 14, upper_bound: 14, limit: 1 });
assert(paxOracle.length === 1, 'PAX/USD oracle data exists');
const paxPrice = parseFloat(paxOracle[0].aggregate?.d_double || 0);
assert(paxPrice >= 0.99 && paxPrice <= 1.01, `PAX/USD price = ${paxPrice.toFixed(6)}`);
assert(paxOracle[0].points.length >= 2, `PAX has ${paxOracle[0].points.length} oracle providers`);

// PYUSD oracle
console.log('\n--- xmd_get_oracle_price (XPYUSD = feed 17) ---');
const pyusdOracle = await getTableRows({ code: ORACLE, scope: ORACLE, table: 'data', lower_bound: 17, upper_bound: 17, limit: 1 });
assert(pyusdOracle.length === 1, 'PYUSD/USD oracle data exists');
const pyusdPrice = parseFloat(pyusdOracle[0].aggregate?.d_double || 0);
assert(pyusdPrice >= 0.99 && pyusdPrice <= 1.01, `PYUSD/USD price = ${pyusdPrice.toFixed(6)}`);

// Oracle feed names
console.log('\n--- oracle feed names ---');
const feedNames = await Promise.all([5, 14, 17, 20].map(async idx => {
  const rows = await getTableRows({ code: ORACLE, scope: ORACLE, table: 'feeds', lower_bound: idx, upper_bound: idx, limit: 1 });
  return { index: idx, name: rows[0]?.name || 'unknown' };
}));
for (const f of feedNames) {
  assert(f.name !== 'unknown', `Feed ${f.index} = ${f.name}`);
}

// ── Test 7: net outstanding per collateral ──
console.log('\n--- net outstanding per collateral ---');
for (const t of tokens) {
  const sym = parseExtSym(t.symbol);
  if (!sym) continue;
  const minted = parseFloat(t.amountMinted) || 0;
  const redeemed = parseFloat(t.amountRedeemed) || 0;
  const net = minted - redeemed;
  assert(net >= 0, `${sym.symbol}: net outstanding = ${net.toFixed(2)} (minted ${minted.toFixed(0)} - redeemed ${redeemed.toFixed(0)})`);
}

// ── Summary ──
console.log(`\n${'='.repeat(40)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
