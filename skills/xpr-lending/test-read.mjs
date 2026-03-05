/**
 * Quick integration test for lending skill read-only tools.
 * Calls mainnet lending.loan directly — no signing needed.
 *
 * Usage: node test-read.mjs
 */

const RPC = 'https://proton.eosusa.io';

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
      key_type: opts.key_type,
      index_position: opts.index_position,
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

const LENDING = 'lending.loan';
let passed = 0;
let failed = 0;

function assert(condition, msg) {
  if (condition) { passed++; console.log(`  PASS: ${msg}`); }
  else { failed++; console.log(`  FAIL: ${msg}`); }
}

// ── Test 1: loan_list_markets ──
console.log('\n--- loan_list_markets ---');
const markets = await getTableRows({ code: LENDING, scope: LENDING, table: 'markets', limit: 50 });
assert(markets.length >= 10, `Found ${markets.length} markets (expected >= 10)`);

const lbtc = markets.find(m => parseExtSym(m.share_symbol)?.symbol === 'LBTC');
assert(!!lbtc, 'LBTC market exists');
assert(parseExtSym(lbtc.share_symbol)?.contract === 'shares.loan', `Share contract = shares.loan`);
assert(parseExtSym(lbtc.underlying_symbol)?.symbol === 'XBTC', `Underlying = XBTC`);
assert(parseExtSym(lbtc.underlying_symbol)?.contract === 'xtokens', `Underlying contract = xtokens`);
assert(lbtc.collateral_factor > 0.5, `Collateral factor > 50% (${lbtc.collateral_factor})`);
assert(lbtc.variable_interest_model?.kink > 0, `Has kink interest model`);

// ── Test 2: loan_get_config ──
console.log('\n--- loan_get_config ---');
const globals = await getTableRows({ code: LENDING, scope: LENDING, table: 'globals.cfg', limit: 1 });
assert(globals.length === 1, 'globals.cfg singleton exists');
assert(globals[0].oracle_contract === 'oracles', `Oracle = oracles`);
assert(globals[0].close_factor > 0, `Close factor > 0 (${globals[0].close_factor})`);
assert(globals[0].liquidation_incentive > 0, `Liquidation incentive > 0`);
assert(globals[0].reward_symbol?.contract === 'loan.token', `LOAN contract = loan.token`);
assert(parseExtSym(globals[0].reward_symbol)?.symbol === 'LOAN', `Reward symbol = LOAN`);

// ── Test 3: rewards.cfg ──
console.log('\n--- rewards.cfg ---');
const rewardsCfg = await getTableRows({ code: LENDING, scope: LENDING, table: 'rewards.cfg', limit: 50 });
assert(rewardsCfg.length >= 10, `Found ${rewardsCfg.length} reward configs`);
const lbtcReward = rewardsCfg.find(r => r.market_symbol === 'LBTC');
assert(!!lbtcReward, 'LBTC rewards config exists');
assert(lbtcReward.supplier_rewards_per_half_second > 0, 'Has supplier rewards');

// ── Test 4: loan_get_user_positions (shares) ──
console.log('\n--- loan_get_user_positions (shares for 111333) ---');
const shares = await getTableRows({
  code: LENDING, scope: LENDING, table: 'shares',
  lower_bound: '111333', upper_bound: '111333', limit: 1, key_type: 'name',
});
assert(shares.length === 1, `Found 1 share row for 111333`);
assert(shares[0].account === '111333', `Account = 111333`);
assert(Array.isArray(shares[0].tokens), 'Has tokens array');
const lxprShare = shares[0].tokens.find(t => parseExtSym(t.key)?.symbol === 'LXPR');
assert(!!lxprShare, 'Has LXPR share position');
assert(lxprShare.value > 0, `LXPR balance > 0 (${lxprShare.value})`);

// ── Test 5: loan_get_user_positions (borrows) ──
console.log('\n--- loan_get_user_positions (borrows for 11nestor22) ---');
const borrows = await getTableRows({
  code: LENDING, scope: LENDING, table: 'borrows',
  lower_bound: '11nestor22', upper_bound: '11nestor22', limit: 1, key_type: 'name',
});
assert(borrows.length === 1, `Found 1 borrow row for 11nestor22`);
const usdcBorrow = borrows[0].tokens.find(t => parseExtSym(t.key)?.symbol === 'XUSDC');
assert(!!usdcBorrow, 'Has XUSDC borrow');
assert(usdcBorrow.value.variable_principal > 0, `XUSDC variable_principal > 0 (${usdcBorrow.value.variable_principal})`);

// ── Test 6: loan_get_user_rewards ──
console.log('\n--- loan_get_user_rewards (11nestor22) ---');
const rewards = await getTableRows({
  code: LENDING, scope: LENDING, table: 'rewards',
  lower_bound: '11nestor22', upper_bound: '11nestor22', limit: 1, key_type: 'name',
});
assert(rewards.length === 1, `Found 1 reward row for 11nestor22`);
assert(Array.isArray(rewards[0].markets), 'Has markets array');
assert(rewards[0].markets.length > 0, `Has ${rewards[0].markets.length} market rewards`);

// ── Test 7: non-existent user returns empty ──
console.log('\n--- non-existent user ---');
const noUser = await getTableRows({
  code: LENDING, scope: LENDING, table: 'shares',
  lower_bound: 'zzzzzzzzzzz1', upper_bound: 'zzzzzzzzzzz1', limit: 1, key_type: 'name',
});
assert(noUser.length === 0, 'Non-existent user returns empty array');

// ── Test 8: loan_get_market_apy ──
console.log('\n--- loan_get_market_apy (XBTC, 7d) ---');
const apyResp = await fetch(`https://identity.api.prod.metalx.com/v1/loan/stats/apy?token_symbol=XBTC&days=7`, {
  headers: { 'Accept': 'application/json' },
});
const apyData = await apyResp.json();
assert(apyData.tokenSymbol === 'XBTC', `Token = XBTC`);
assert(apyData.days === 7, `Days = 7`);
assert(apyData.avgDepositApy > 0, `Deposit APY > 0 (${(apyData.avgDepositApy * 100).toFixed(2)}%)`);
assert(apyData.avgBorrowApy > 0, `Borrow APY > 0 (${(apyData.avgBorrowApy * 100).toFixed(2)}%)`);
assert(Array.isArray(apyData.chartData), 'Has chart data');
assert(apyData.chartData.length >= 5, `Chart has ${apyData.chartData.length} points`);

// ── Test 9: loan_get_market_tvl ──
console.log('\n--- loan_get_market_tvl (XBTC, 7d) ---');
const tvlResp = await fetch(`https://identity.api.prod.metalx.com/v1/loan/stats/tvl?token_symbol=XBTC&days=7`, {
  headers: { 'Accept': 'application/json' },
});
const tvlData = await tvlResp.json();
assert(tvlData.tokenSymbol === 'XBTC', `Token = XBTC`);
assert(tvlData.avgDepositTvl > 0, `Deposit TVL > 0 ($${Math.round(tvlData.avgDepositTvl).toLocaleString()})`);
assert(tvlData.avgBorrowTvl > 0, `Borrow TVL > 0 ($${Math.round(tvlData.avgBorrowTvl).toLocaleString()})`);
const utilPct = (tvlData.avgBorrowTvl / tvlData.avgDepositTvl * 100).toFixed(1);
assert(parseFloat(utilPct) > 0 && parseFloat(utilPct) < 100, `Utilization = ${utilPct}%`);

// ── Test 10: APY for XUSDC (different market) ──
console.log('\n--- loan_get_market_apy (XUSDC, 30d) ---');
const usdcApy = await fetch(`https://identity.api.prod.metalx.com/v1/loan/stats/apy?token_symbol=XUSDC&days=30`, {
  headers: { 'Accept': 'application/json' },
}).then(r => r.json());
assert(usdcApy.tokenSymbol === 'XUSDC', `Token = XUSDC`);
assert(usdcApy.days === 30, `Days = 30`);
assert(usdcApy.avgDepositApy > 0, `XUSDC deposit APY > 0 (${(usdcApy.avgDepositApy * 100).toFixed(2)}%)`);

// ── Summary ──
console.log(`\n${'='.repeat(40)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
