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

  // Get the server's deposit nametag
  const { address } = await apiPost('/api/agent/deposit-address', {}, privateKey);

  console.log(`Depositing ${amount} UCT to server (${address})...`);

  // Receive any pending tokens first so balance is up-to-date
  try {
    await sphere.payments.receive({ finalize: true, timeout: 15_000 });
  } catch {
    // May fail if no pending events — that's fine
  }

  // Resolve the UCT coin ID from the token registry
  const allTokens = sphere.payments.getTokens({ status: 'confirmed' });
  if (allTokens.length === 0) {
    console.error('No confirmed tokens in wallet. Top up first: openclaw unicity top-up');
    process.exit(1);
  }

  // Use the coinId from the first available token (all UCT on testnet)
  const coinId = allTokens[0].coinId;

  // Convert human-readable amount to smallest units
  const decimals = allTokens[0].decimals ?? 8;
  const parts = amount.split('.');
  const intPart = parts[0] ?? '0';
  const fracPart = (parts[1] ?? '').padEnd(decimals, '0').slice(0, decimals);
  const amountSmallest = intPart + fracPart;

  // Send tokens directly to the server
  const result = await sphere.payments.send({
    recipient: address,
    amount: amountSmallest,
    coinId,
  });

  if (result.error) {
    console.error(`Deposit failed: ${result.error}`);
    process.exit(1);
  }

  console.log(`Sent ${amount} UCT to ${address} (tx: ${result.id})`);
  console.log('The server will detect the transfer and credit your trading balance automatically.');
}

main().catch((err) => {
  console.error('Deposit failed:', err.message);
  process.exit(1);
});
