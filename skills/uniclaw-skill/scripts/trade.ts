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
      const result = await apiPost(`/api/agent/markets/${marketId}/orders`, {
        side,
        price: parseFloat(price),
        quantity: parseInt(quantity, 10),
      }, privateKey);

      console.log('Order placed! ID:', result.orderId);
      if (result.fills.length > 0) {
        console.log('Fills:');
        for (const fill of result.fills) {
          console.log(`  ${fill.quantity} @ ${fill.price}`);
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
        console.log(`[${o.id}] ${o.market_id} ${o.side} ${o.quantity}@${o.price} (filled: ${o.filled_quantity})`);
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
