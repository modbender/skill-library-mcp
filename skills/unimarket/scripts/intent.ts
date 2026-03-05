import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiPost, apiGet, apiDelete } from '../lib/api.js';

const command = process.argv[2];

function parseArgs(): Record<string, string> {
  const args: Record<string, string> = {};
  const argv = process.argv.slice(3);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--') && argv[i + 1]) {
      args[argv[i].slice(2)] = argv[i + 1];
      i++;
    }
  }
  return args;
}

async function main() {
  const sphere = await loadWallet();
  const privateKey = getPrivateKeyHex(sphere);

  switch (command) {
    case 'post': {
      const args = parseArgs();
      if (!args.desc || !args.type) {
        console.log('Usage: npx tsx scripts/intent.ts post --type <sell|buy> --desc "..." [--category <cat>] [--price <n>] [--location <loc>]');
        process.exit(1);
      }

      const result = await apiPost('/api/intents', {
        description: args.desc,
        intent_type: args.type,
        category: args.category,
        price: args.price ? parseFloat(args.price) : undefined,
        currency: args.currency || 'UCT',
        location: args.location,
      }, privateKey);

      console.log('Intent posted!');
      console.log('Intent ID:', result.intentId);
      console.log('Expires:', result.expiresAt);
      break;
    }

    case 'list': {
      const result = await apiGet('/api/intents', privateKey);
      if (result.intents.length === 0) {
        console.log('No intents found.');
        return;
      }
      for (const intent of result.intents) {
        console.log(`[${intent.id}] ${intent.intent_type.toUpperCase()} - ${intent.category || 'uncategorized'} - ${intent.price || 'no price'} ${intent.currency} (${intent.status})`);
      }
      break;
    }

    case 'close': {
      const intentId = process.argv[3];
      if (!intentId) {
        console.log('Usage: npx tsx scripts/intent.ts close <intent-id>');
        process.exit(1);
      }
      await apiDelete(`/api/intents/${intentId}`, privateKey);
      console.log('Intent closed.');
      break;
    }

    default:
      console.log('Usage: npx tsx scripts/intent.ts <post|list|close>');
      console.log('  post  --type <sell|buy> --desc "..." [--category <cat>] [--price <n>] [--location <loc>]');
      console.log('  list');
      console.log('  close <intent-id>');
      process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
