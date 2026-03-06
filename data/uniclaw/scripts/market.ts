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
        let chanceLine = '';
        if (pub) {
          const bid = pub.best_bid;
          const ask = pub.best_ask;
          const mid = bid != null && ask != null ? (bid + ask) / 2
            : bid != null ? bid
            : ask != null ? ask
            : pub.last_price;
          const pct = mid != null ? `${Math.round(mid * 100)}% chance` : 'No orders';
          chanceLine = `  ${pct}  |  Vol: ${pub.volume} UCT  |  Closes: ${m.closes_at}`;
        } else {
          chanceLine = `  Closes: ${m.closes_at}`;
        }
        console.log(`[${m.id}] ${m.question}`);
        console.log(chanceLine);
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

      // Compute mid price
      const bids = order_book.filter((o: any) => o.side === 'yes');
      const asks = order_book.filter((o: any) => o.side === 'no');
      const bestBid = bids.length > 0 ? Math.max(...bids.map((o: any) => parseFloat(o.price))) : null;
      const bestAsk = asks.length > 0 ? Math.min(...asks.map((o: any) => parseFloat(o.price))) : null;
      const mid = bestBid != null && bestAsk != null ? (bestBid + bestAsk) / 2
        : bestBid != null ? bestBid
        : bestAsk != null ? bestAsk
        : null;
      const pct = mid != null ? `${Math.round(mid * 100)}%` : '—';

      console.log(`${market.question}`);
      console.log(`${pct} chance  |  Vol: ${stats.volume} UCT (${stats.trade_count} trades)  |  Closes: ${market.closes_at}`);
      console.log();

      // Order book — all prices on the same probability axis
      const allOrders = order_book
        .map((o: any) => ({ price: parseFloat(o.price), depth: parseInt(o.depth, 10), side: o.side }))
        .sort((a: any, b: any) => b.price - a.price);

      if (allOrders.length > 0) {
        console.log('Order Book:');
        for (const o of allOrders) {
          const label = o.side === 'yes' ? 'bid' : 'ask';
          console.log(`  ${Math.round(o.price * 100)}%  ${o.depth} shares  (${label})`);
        }
      } else {
        console.log('Order Book: empty');
      }

      // Recent trades
      if (recent_trades.length > 0) {
        console.log();
        console.log('Recent Trades:');
        for (const t of recent_trades.slice(0, 5)) {
          console.log(`  ${t.quantity} shares @ ${Math.round(parseFloat(t.price) * 100)}%  —  ${new Date(t.created_at).toLocaleString()}`);
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
