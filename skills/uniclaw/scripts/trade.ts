import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiPost, apiGet, apiDelete } from '../lib/api.js';

const command = process.argv[2];

function parseTradeArgs(): { marketId: string; side: string; price: string; quantity: string } {
  const args = process.argv.slice(3);
  let marketId = '', side = '', price = '', quantity = '';
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--market' && args[i + 1]) marketId = args[i + 1];
    if (args[i] === '--side' && args[i + 1]) side = args[i + 1];
    if (args[i] === '--price' && args[i + 1]) price = args[i + 1];
    if (args[i] === '--qty' && args[i + 1]) quantity = args[i + 1];
  }
  if (!marketId || !side || !price || !quantity) {
    console.log('Usage: npx tsx scripts/trade.ts buy --market <id> --side <yes|no> --price <0.01-0.99> --qty <n>');
    process.exit(1);
  }
  return { marketId, side, price, quantity };
}

async function main() {
  const sphere = await loadWallet();
  const privateKey = getPrivateKeyHex(sphere);

  switch (command) {
    case 'buy': {
      const { marketId, side, price, quantity } = parseTradeArgs();
      const priceNum = parseFloat(price);
      const qtyNum = parseInt(quantity, 10);
      const collateral = side === 'yes' ? priceNum : 1 - priceNum;
      const totalCost = collateral * qtyNum;
      const payout = qtyNum;

      console.log(`Betting ${side.toUpperCase()} at ${Math.round(priceNum * 100)}%`);
      console.log(`Cost: ${totalCost.toFixed(2)} UCT (${qtyNum} shares x ${collateral.toFixed(2)} each)`);
      console.log(`Payout if correct: ${payout.toFixed(2)} UCT (profit: ${(payout - totalCost).toFixed(2)} UCT)`);
      console.log();

      const result = await apiPost(`/api/agent/markets/${marketId}/orders`, {
        side,
        price: priceNum,
        quantity: qtyNum,
      }, privateKey);

      console.log('Order placed! ID:', result.orderId);
      if (result.fills.length > 0) {
        console.log('Fills:');
        for (const fill of result.fills) {
          console.log(`  ${fill.quantity} shares @ ${Math.round(fill.price * 100)}%`);
        }
      } else {
        console.log('Resting on book (no immediate fills).');
      }
      break;
    }

    case 'cancel': {
      const marketId = process.argv[3];
      const orderId = process.argv[4];
      if (!marketId || !orderId) {
        console.log('Usage: npx tsx scripts/trade.ts cancel <market-id> <order-id>');
        process.exit(1);
      }
      await apiDelete(`/api/agent/markets/${marketId}/orders/${orderId}`, privateKey);
      console.log('Order cancelled.');
      break;
    }

    case 'orders': {
      const { orders } = await apiGet('/api/agent/orders', privateKey);
      if (orders.length === 0) {
        console.log('No open orders.');
        return;
      }
      for (const o of orders) {
        const pct = Math.round(parseFloat(o.price) * 100);
        console.log(`[${o.id}] ${o.market_id} ${o.side.toUpperCase()} ${o.quantity} shares @ ${pct}% (filled: ${o.filled_quantity})`);
      }
      break;
    }

    default:
      console.log('Usage: npx tsx scripts/trade.ts <buy|cancel|orders>');
      process.exit(1);
  }
}

main().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});
