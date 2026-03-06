import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiGet } from '../lib/api.js';

const command = process.argv[2];

async function main() {
  const sphere = await loadWallet();
  const privateKey = getPrivateKeyHex(sphere);

  switch (command) {
    case 'balance': {
      const data = await apiGet('/api/agent/balance', privateKey);
      console.log('Available:', data.available, 'UCT');
      console.log('Locked:', data.locked, 'UCT');
      break;
    }

    case 'positions': {
      const { positions } = await apiGet('/api/agent/positions', privateKey);
      if (positions.length === 0) {
        console.log('No open positions.');
        return;
      }
      for (const p of positions) {
        console.log(`[${p.market_id}] ${p.side} x${p.quantity} (avg cost: ${p.avg_cost})`);
      }
      break;
    }

    default:
      console.log('Usage: npx tsx scripts/portfolio.ts <balance|positions>');
      process.exit(1);
  }
}

main().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});
