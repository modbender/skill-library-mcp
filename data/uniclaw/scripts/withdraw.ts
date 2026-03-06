import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiPost } from '../lib/api.js';

function parseArgs(): { amount: string; to: string } {
  const args = process.argv.slice(2);
  let amount = '', to = '';
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--amount' && args[i + 1]) amount = args[i + 1];
    if (args[i] === '--to' && args[i + 1]) to = args[i + 1];
  }
  if (!amount || !to) {
    console.log('Usage: npx tsx scripts/withdraw.ts --amount <amount> --to <address>');
    process.exit(1);
  }
  return { amount, to };
}

async function main() {
  const { amount, to } = parseArgs();
  const sphere = await loadWallet();
  const privateKey = getPrivateKeyHex(sphere);

  const result = await apiPost('/api/agent/withdraw', {
    amount: parseFloat(amount),
    recipientAddress: to,
  }, privateKey);

  console.log('Withdrawal submitted!');
  console.log('ID:', result.withdrawal.id);
  console.log('Amount:', result.withdrawal.amount);
  console.log('To:', result.withdrawal.recipientAddress);
  console.log('Status:', result.withdrawal.status);
}

main().catch((err) => {
  console.error('Withdrawal failed:', err.message);
  process.exit(1);
});
