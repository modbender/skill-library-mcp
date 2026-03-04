import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiPost } from '../lib/api.js';

function parseArgs(): { amount: string } {
  const args = process.argv.slice(2);
  let amount = '';
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--amount' && args[i + 1]) {
      amount = args[i + 1];
    }
  }
  if (!amount) {
    console.log('Usage: npx tsx scripts/deposit.ts --amount <amount>');
    process.exit(1);
  }
  return { amount };
}

async function main() {
  const { amount } = parseArgs();
  const sphere = await loadWallet();
  const privateKey = getPrivateKeyHex(sphere);

  const { address } = await apiPost('/api/agent/deposit-address', {}, privateKey);

  console.log('');
  console.log(`To deposit ${amount} UCT, send tokens to the server using the Unicity plugin:`);
  console.log('');
  console.log(`  Use the uniclaw_send_tokens tool with:`);
  console.log(`    recipient: ${address}`);
  console.log(`    amount: ${amount}`);
  console.log(`    coin: UCT`);
  console.log('');
  console.log('The server will detect the transfer and credit your trading balance automatically.');
}

main().catch((err) => {
  console.error('Deposit failed:', err.message);
  process.exit(1);
});
