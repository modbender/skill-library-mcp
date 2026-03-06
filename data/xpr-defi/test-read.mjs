/**
 * DeFi Skill — Read-only integration tests
 * Tests all 14 read-only tools against mainnet data.
 *
 * Usage: node openclaw/starter/agent/skills/defi/test-read.mjs
 */

// ── Test runner ──
let passed = 0, failed = 0, total = 0;
function assert(cond, msg) {
  total++;
  if (cond) { passed++; }
  else { failed++; console.error(`  FAIL: ${msg}`); }
}

// ── Collect tools ──
const tools = [];
const mockApi = {
  registerTool(t) { tools.push(t); },
  getConfig() {
    return {
      network: 'mainnet',
      rpcEndpoint: 'https://proton.eosusa.io',
    };
  },
};

// Load skill
const { default: defiSkill } = await import('./src/index.ts');
defiSkill(mockApi);

function findTool(name) {
  return tools.find(t => t.name === name);
}

console.log(`Loaded ${tools.length} tools`);
assert(tools.length === 30, `Expected 30 tools, got ${tools.length}`);

// ── 1. defi_get_token_price ──
console.log('\n--- defi_get_token_price ---');
const price = await findTool('defi_get_token_price').handler({ symbol: 'XPR_XMD' });
assert(!price.error, `No error: ${price.error}`);
assert(price.symbol === 'XPR_XMD', `Symbol is XPR_XMD: ${price.symbol}`);
assert(typeof price.close === 'number', `Close is number: ${price.close}`);
assert(typeof price.volume_bid === 'number', `volume_bid: ${price.volume_bid}`);
assert(typeof price.change_24h_pct === 'number', `change_24h_pct: ${price.change_24h_pct}`);
console.log(`  XPR/XMD: $${price.close}, 24h: ${price.change_24h_pct}%`);

// Bad symbol
const badPrice = await findTool('defi_get_token_price').handler({ symbol: 'FAKE_TOKEN' });
assert(badPrice.error, 'Returns error for unknown symbol');

// ── 2. defi_list_markets ──
console.log('\n--- defi_list_markets ---');
const markets = await findTool('defi_list_markets').handler({});
assert(!markets.error, `No error: ${markets.error}`);
assert(markets.total >= 15, `At least 15 markets: ${markets.total}`);
const xprMarket = markets.markets.find(m => m.symbol === 'XPR_XMD');
assert(xprMarket, 'XPR_XMD market exists');
assert(xprMarket.bid_token, 'Has bid_token info');
assert(xprMarket.ask_token, 'Has ask_token info');
console.log(`  ${markets.total} markets`);

// ── 3. defi_get_swap_rate ──
console.log('\n--- defi_get_swap_rate ---');
const swap = await findTool('defi_get_swap_rate').handler({
  from_token: '4,XPR,eosio.token',
  to_token: '6,XUSDC,xtokens',
  amount: 10000,
});
assert(!swap.error, `No error: ${swap.error}`);
assert(swap.output, `Has output: ${swap.output}`);
assert(parseFloat(swap.rate) > 0, `Rate > 0: ${swap.rate}`);
assert(swap.fee_pct, `Has fee: ${swap.fee_pct}`);
console.log(`  10000 XPR → ${swap.output}, rate=${swap.rate}, impact=${swap.price_impact_pct}%`);

// Bad pool
const badSwap = await findTool('defi_get_swap_rate').handler({
  from_token: '4,XPR,eosio.token',
  to_token: '6,FAKE,fake.token',
  amount: 100,
});
assert(badSwap.error, 'Returns error for unknown pool');

// ── 4. defi_list_pools ──
console.log('\n--- defi_list_pools ---');
const pools = await findTool('defi_list_pools').handler({});
assert(!pools.error, `No error: ${pools.error}`);
assert(pools.total >= 5, `At least 5 pools: ${pools.total}`);
const firstPool = pools.pools[0];
assert(firstPool.lt_symbol, `Pool has lt_symbol: ${firstPool.lt_symbol}`);
assert(firstPool.token1, 'Pool has token1');
assert(firstPool.fee_pct, `Pool has fee: ${firstPool.fee_pct}`);
assert(firstPool.pool_type, `Pool type: ${firstPool.pool_type}`);
console.log(`  ${pools.total} pools, first: ${firstPool.lt_symbol}`);

// ── 5. defi_get_ohlcv ──
console.log('\n--- defi_get_ohlcv ---');
const ohlcv = await findTool('defi_get_ohlcv').handler({
  symbol: 'XPR_XMD',
  interval: '1D',
  limit: 5,
});
assert(!ohlcv.error, `No error: ${ohlcv.error}`);
assert(ohlcv.candles.length > 0, `Has candles: ${ohlcv.candles.length}`);
const candle = ohlcv.candles[0];
assert(candle.time, `Candle has time: ${candle.time}`);
assert(typeof candle.open === 'number', `Candle has open: ${candle.open}`);
assert(typeof candle.close === 'number', `Candle has close: ${candle.close}`);
console.log(`  ${ohlcv.candles.length} candles, latest close: ${candle.close}`);

// ── 6. defi_get_orderbook ──
console.log('\n--- defi_get_orderbook ---');
const book = await findTool('defi_get_orderbook').handler({ symbol: 'XPR_XMD', step: 10000, limit: 5 });
assert(!book.error, `No error: ${book.error}`);
assert(Array.isArray(book.bids), 'Has bids array');
assert(Array.isArray(book.asks), 'Has asks array');
const totalDepth = (book.bids?.length || 0) + (book.asks?.length || 0);
assert(totalDepth > 0, `Has depth levels: ${totalDepth}`);
console.log(`  ${book.bids?.length || 0} bids, ${book.asks?.length || 0} asks`);

// ── 7. defi_get_recent_trades ──
console.log('\n--- defi_get_recent_trades ---');
const recent = await findTool('defi_get_recent_trades').handler({ symbol: 'XPR_XMD', limit: 5 });
assert(!recent.error, `No error: ${recent.error}`);
assert(recent.trades.length > 0, `Has trades: ${recent.trades.length}`);
const trade = recent.trades[0];
assert(trade.price, `Trade has price: ${trade.price}`);
assert(trade.side, `Trade has side: ${trade.side}`);
assert(trade.trx_id, `Trade has trx_id`);
console.log(`  ${recent.trades.length} trades, latest: ${trade.price} (${trade.side})`);

// ── 8. defi_get_open_orders ──
console.log('\n--- defi_get_open_orders ---');
// Use a known active market maker account
const openOrders = await findTool('defi_get_open_orders').handler({ account: 'communitymm3', limit: 5 });
assert(!openOrders.error, `No error: ${openOrders.error}`);
assert(Array.isArray(openOrders.orders), 'Has orders array');
if (openOrders.orders.length > 0) {
  const order = openOrders.orders[0];
  assert(order.order_id, 'Order has order_id');
  assert(order.side, 'Order has side');
  assert(order.price !== undefined, 'Order has price');
  console.log(`  ${openOrders.orders.length} open orders`);
} else {
  console.log('  No open orders for communitymm3 (may be normal)');
}

// ── 9. defi_get_order_history ──
console.log('\n--- defi_get_order_history ---');
const orderHist = await findTool('defi_get_order_history').handler({ account: 'communitymm3', limit: 3 });
assert(!orderHist.error, `No error: ${orderHist.error}`);
assert(Array.isArray(orderHist.orders), 'Has orders array');
console.log(`  ${orderHist.orders.length} historical orders`);

// ── 10. defi_get_trade_history ──
console.log('\n--- defi_get_trade_history ---');
const tradeHist = await findTool('defi_get_trade_history').handler({ account: 'communitymm3', limit: 3 });
assert(!tradeHist.error, `No error: ${tradeHist.error}`);
assert(Array.isArray(tradeHist.trades), 'Has trades array');
console.log(`  ${tradeHist.trades.length} historical trades`);

// ── 11. defi_get_dex_balances ──
console.log('\n--- defi_get_dex_balances ---');
const balances = await findTool('defi_get_dex_balances').handler({ account: 'communitymm3' });
assert(!balances.error, `No error: ${balances.error}`);
assert(Array.isArray(balances.balances), 'Has balances array');
console.log(`  ${balances.total} balance entries`);

// ── 12. defi_list_otc_offers ──
console.log('\n--- defi_list_otc_offers ---');
const otc = await findTool('defi_list_otc_offers').handler({ limit: 5 });
assert(!otc.error, `No error: ${otc.error}`);
assert(Array.isArray(otc.offers), 'Has offers array');
if (otc.offers.length > 0) {
  const offer = otc.offers[0];
  assert(offer.id !== undefined, 'Offer has id');
  assert(offer.from, 'Offer has from');
  console.log(`  ${otc.offers.length} OTC offers, first: #${offer.id} from ${offer.from}`);
} else {
  console.log('  No OTC offers (table may be empty)');
}

// ── 13. defi_list_farms ──
console.log('\n--- defi_list_farms ---');
const farms = await findTool('defi_list_farms').handler({});
assert(!farms.error, `No error: ${farms.error}`);
assert(farms.total >= 3, `At least 3 active farms: ${farms.total}`);
const firstFarm = farms.farms[0];
assert(firstFarm.stake_symbol, `Farm has stake_symbol: ${firstFarm.stake_symbol}`);
assert(firstFarm.stake_contract, `Farm has stake_contract: ${firstFarm.stake_contract}`);
assert(firstFarm.rewards?.length > 0, `Farm has rewards: ${firstFarm.rewards?.length}`);
assert(firstFarm.rewards[0].per_day > 0, `Farm has positive daily reward: ${firstFarm.rewards[0].per_day}`);
console.log(`  ${farms.total} active farms, first: ${firstFarm.stake_symbol} (${firstFarm.rewards[0].per_day} ${firstFarm.rewards[0].token}/day)`);

// All farms (including inactive)
const allFarms = await findTool('defi_list_farms').handler({ active_only: false });
assert(!allFarms.error, `No error listing all farms: ${allFarms.error}`);
assert(allFarms.total >= farms.total, `All farms >= active farms: ${allFarms.total} >= ${farms.total}`);
console.log(`  ${allFarms.total} total farms (including inactive)`);

// ── 14. defi_get_farm_stakes ──
console.log('\n--- defi_get_farm_stakes ---');
// Use "paul" account which has known farm positions
const farmStakes = await findTool('defi_get_farm_stakes').handler({ account: 'paul' });
assert(!farmStakes.error, `No error: ${farmStakes.error}`);
assert(Array.isArray(farmStakes.stakes), 'Has stakes array');
assert(farmStakes.total > 0, `Paul has farm stakes: ${farmStakes.total}`);
if (farmStakes.stakes.length > 0) {
  const stake = farmStakes.stakes[0];
  assert(stake.symbol, `Stake has symbol: ${stake.symbol}`);
  assert(stake.contract, `Stake has contract: ${stake.contract}`);
  assert(stake.balance > 0 || stake.accrued_rewards_raw.length > 0, 'Stake has balance or rewards');
  console.log(`  ${farmStakes.total} positions, first: ${stake.balance} ${stake.symbol}`);
}

// Unknown account
const noStakes = await findTool('defi_get_farm_stakes').handler({ account: 'zzzzzzzzzzzz' });
assert(!noStakes.error, 'No error for unknown account');
assert(noStakes.total === 0, 'Zero stakes for unknown account');

// ── Verify write tools exist and have confirmed parameter ──
console.log('\n--- Write tool validation ---');
const writeTools = [
  'defi_place_order', 'defi_cancel_order', 'defi_withdraw_dex',
  'defi_swap', 'defi_add_liquidity', 'defi_remove_liquidity',
  'defi_create_otc', 'defi_fill_otc', 'defi_cancel_otc',
  'defi_farm_stake', 'defi_farm_unstake', 'defi_farm_claim',
  'msig_propose', 'msig_approve',
];
for (const name of writeTools) {
  const tool = findTool(name);
  assert(tool, `${name} exists`);
  if (tool) {
    const hasConfirmed = tool.parameters.properties?.confirmed || tool.parameters.required?.includes('confirmed');
    assert(hasConfirmed, `${name} has confirmed parameter`);
  }
}
console.log(`  ${writeTools.length} write tools validated`);

// ── Verify confirmation gate on write tools ──
console.log('\n--- Confirmation gate tests ---');
const placeResult = await findTool('defi_place_order').handler({
  symbol: 'XPR_XMD', side: 'buy', amount: 100, price: 0.003,
});
assert(placeResult.error && placeResult.error.includes('Confirmation'), 'defi_place_order blocked without confirmed');

const swapResult = await findTool('defi_swap').handler({
  from_token: '4,XPR,eosio.token', to_token: '6,XUSDC,xtokens',
  amount: 100, min_output: 0.1,
});
assert(swapResult.error && swapResult.error.includes('Confirmation'), 'defi_swap blocked without confirmed');

const otcResult = await findTool('defi_create_otc').handler({
  from_tokens: [{ quantity: '100.0000 XPR', contract: 'eosio.token' }],
  to_tokens: [{ quantity: '1.000000 XUSDC', contract: 'xtokens' }],
});
assert(otcResult.error && otcResult.error.includes('Confirmation'), 'defi_create_otc blocked without confirmed');

const stakeResult = await findTool('defi_farm_stake').handler({
  lp_amount: '1.00000000 METAXMD', lp_contract: 'proton.swaps',
});
assert(stakeResult.error && stakeResult.error.includes('Confirmation'), 'defi_farm_stake blocked without confirmed');

const unstakeResult = await findTool('defi_farm_unstake').handler({
  lp_amount: '1.00000000 METAXMD', lp_contract: 'proton.swaps',
});
assert(unstakeResult.error && unstakeResult.error.includes('Confirmation'), 'defi_farm_unstake blocked without confirmed');

const claimResult = await findTool('defi_farm_claim').handler({
  stakes: ['METAXMD'],
});
assert(claimResult.error && claimResult.error.includes('Confirmation'), 'defi_farm_claim blocked without confirmed');

console.log('  All confirmation gates working');

// ── Summary ──
console.log(`\n${'='.repeat(50)}`);
console.log(`Results: ${passed}/${total} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
else console.log('All tests passed!');
