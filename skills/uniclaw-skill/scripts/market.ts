import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiGet, apiPublicGet } from '../lib/api.js';

const command = process.argv[2];
const arg = process.argv[3];

async function main() {
  switch (command) {
    case 'list': {
      const sphere = await loadWallet();
      const privateKey = getPrivateKeyHex(sphere);
      const { markets } = await apiGet('/api/agent/markets', privateKey);
      if (markets.length === 0) {
        console.log('No active markets.');
        return;
      }
      // Fetch public data for prices
      const pubData = await apiPublicGet('/api/public/markets');
      const pubMap = new Map(pubData.markets.map((m: any) => [m.id, m]));

      for (const m of markets) {
        const pub = pubMap.get(m.id) as any;
        const priceInfo = pub
          ? ` | YES bid: ${pub.yes_bid ?? '—'}  NO ask: ${pub.no_ask ?? '—'}  Last: ${pub.last_price ?? '—'}  Vol: ${pub.volume}`
          : '';
        console.log(`[${m.id}] ${m.question}`);
        console.log(`  Closes: ${m.closes_at}${priceInfo}`);
        console.log();
      }
      break;
    }

    case 'detail': {
      if (!arg) {
        console.log('Usage: npx tsx scripts/market.ts detail <market-id>');
        process.exit(1);
      }
      const data = await apiPublicGet(`/api/public/markets/${arg}`);
      const { market, order_book, recent_trades, stats } = data;

      console.log('Market:', market.id);
      console.log('Question:', market.question);
      console.log('Closes:', market.closes_at);
      console.log('Status:', market.status);
      console.log(`Volume: ${stats.volume} UCT (${stats.trade_count} trades)`);
      console.log();

      // Order book
      const yesBids = order_book.filter((o: any) => o.side === 'yes').reverse();
      const noOffers = order_book.filter((o: any) => o.side === 'no');

      if (yesBids.length > 0 || noOffers.length > 0) {
        console.log('Order Book:');
        if (yesBids.length > 0) {
          console.log('  YES bids:');
          for (const o of yesBids) {
            console.log(`    ${o.price} x${o.depth}`);
          }
        }
        if (noOffers.length > 0) {
          console.log('  NO bids:');
          for (const o of noOffers) {
            console.log(`    ${o.price} x${o.depth}`);
          }
        }
      } else {
        console.log('Order Book: empty');
      }

      // Recent trades
      if (recent_trades.length > 0) {
        console.log();
        console.log('Recent Trades:');
        for (const t of recent_trades.slice(0, 5)) {
          console.log(`  ${t.quantity}@${t.price} — ${new Date(t.created_at).toLocaleString()}`);
        }
      }
      break;
    }

    default:
      console.log('Usage: npx tsx scripts/market.ts <list|detail> [market-id]');
      process.exit(1);
  }
}

main().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});
