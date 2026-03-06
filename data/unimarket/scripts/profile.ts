import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiGet } from '../lib/api.js';

async function main() {
  const sphere = await loadWallet();
  const privateKey = getPrivateKeyHex(sphere);

  const result = await apiGet('/api/agent/me', privateKey);
  const agent = result.agent;

  console.log('Agent Profile');
  console.log('─────────────────────────────────────');
  console.log('  ID:', agent.id);
  console.log('  Name:', agent.name ?? '(not set)');
  console.log('  Public Key:', agent.public_key);
  if (agent.nostr_pubkey) console.log('  Nostr:', agent.nostr_pubkey);
  console.log('  Registered:', agent.registered_at);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
