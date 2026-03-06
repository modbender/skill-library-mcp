// End-to-end smoke test for UniClaw
// Run: npx tsx scripts/smoke-test.ts
// Requires: Unicity plugin wallet at ~/.openclaw/unicity/

import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiPost, apiGet, apiDelete } from '../lib/api.js';
import { config } from '../lib/config.js';

async function main() {
  console.log('=== UniClaw Smoke Test ===\n');
  console.log(`Server: ${config.serverUrl}\n`);

  // 1. Load wallet (must exist via Unicity plugin)
  console.log('1. Loading wallet...');
  const sphere = await loadWallet();
  const privateKey = getPrivateKeyHex(sphere);
  const address = sphere.identity?.l1Address;
  console.log(`   Address: ${address?.slice(0, 20)}...`);

  // 2. Register with server
  console.log('\n2. Registering with server...');
  try {
    const agentName = `smoke-test-${Date.now()}`;
    const regResult = await apiPost('/register', { name: agentName }, privateKey);
    console.log(`   Registered as: ${regResult.agent?.name ?? regResult.name} (id: ${regResult.agent?.id ?? regResult.id})`);
  } catch (err: any) {
    if (err.message.includes('already') || err.message.includes('exists')) {
      console.log('   Already registered');
    } else {
      console.log(`   Registration failed: ${err.message}`);
    }
  }

  // 3. Check server balance
  console.log('\n3. Checking server balance...');
  try {
    const balResult = await apiGet('/balance', privateKey);
    console.log(`   Available: ${balResult.available ?? balResult.balance ?? 0} UCT`);
    console.log(`   Locked: ${balResult.locked ?? 0} UCT`);
  } catch (err: any) {
    console.log(`   Balance check failed: ${err.message}`);
  }

  // 4. List markets
  console.log('\n4. Listing markets...');
  let markets: any[] = [];
  try {
    const marketsResult = await apiGet('/markets', privateKey);
    markets = marketsResult.markets ?? marketsResult ?? [];
    console.log(`   Found ${markets.length} active market(s)`);
    for (const m of markets.slice(0, 3)) {
      const question = m.question ?? m.title ?? m.name ?? 'Unknown';
      console.log(`   - ${m.id}: ${question.slice(0, 50)}${question.length > 50 ? '...' : ''}`);
    }
    if (markets.length > 3) {
      console.log(`   ... and ${markets.length - 3} more`);
    }
  } catch (err: any) {
    console.log(`   Failed to list markets: ${err.message}`);
  }

  // 5. Test trading (if we have markets)
  if (markets.length > 0) {
    const testMarket = markets[0];
    console.log(`\n5. Testing order flow on market: ${testMarket.id}`);

    // Try placing an order
    console.log('   Placing test order (YES @ 0.10, qty 1)...');
    let placedOrderId: string | null = null;
    try {
      const orderResult = await apiPost(`/markets/${testMarket.id}/orders`, {
        side: 'yes',
        price: 0.10,
        quantity: 1,
      }, privateKey);
      placedOrderId = orderResult.order?.id ?? orderResult.id ?? null;
      console.log(`   Order placed: ${placedOrderId ?? JSON.stringify(orderResult)}`);
    } catch (err: any) {
      if (err.message.includes('Insufficient') || err.message.includes('balance')) {
        console.log('   No server balance - deposit UCT to test trading');
      } else {
        console.log(`   Order failed: ${err.message}`);
      }
    }

    // Check open orders
    console.log('   Checking open orders...');
    try {
      const ordersResult = await apiGet('/orders', privateKey);
      const orders = ordersResult.orders ?? ordersResult ?? [];
      console.log(`   Open orders: ${orders.length}`);

      // Cancel if we placed an order
      if (placedOrderId || orders.length > 0) {
        const orderToCancel = placedOrderId ?? orders[0]?.id;
        const marketId = orders[0]?.market_id ?? testMarket.id;
        if (orderToCancel) {
          console.log(`   Cancelling order ${orderToCancel}...`);
          try {
            await apiDelete(`/markets/${marketId}/orders/${orderToCancel}`, privateKey);
            console.log('   Order cancelled');
          } catch (err: any) {
            console.log(`   Cancel failed: ${err.message}`);
          }
        }
      }
    } catch (err: any) {
      console.log(`   Orders check failed: ${err.message}`);
    }
  } else {
    console.log('\n5. No markets available - skipping order tests');
  }

  // 6. Final balance
  console.log('\n6. Final balance check...');
  try {
    const finalBal = await apiGet('/balance', privateKey);
    console.log(`   Available: ${finalBal.available ?? finalBal.balance ?? 0} UCT`);
    console.log(`   Locked: ${finalBal.locked ?? 0} UCT`);
  } catch (err: any) {
    console.log(`   Balance check failed: ${err.message}`);
  }

  // 7. Check positions
  console.log('\n7. Checking positions...');
  try {
    const posResult = await apiGet('/positions', privateKey);
    const positions = posResult.positions ?? posResult ?? [];
    console.log(`   Positions: ${positions.length}`);
    for (const p of positions) {
      console.log(`   - ${p.market_id}: ${p.side} x${p.quantity} @ ${p.avg_cost}`);
    }
  } catch (err: any) {
    console.log(`   Positions check failed: ${err.message}`);
  }

  console.log('\n=== Smoke Test Complete ===');
}

main().catch((err) => {
  console.error('\nSmoke test failed:', err);
  process.exit(1);
});
