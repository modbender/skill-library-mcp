import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiPost } from '../lib/api.js';

const name = process.argv[2];

async function main() {
  if (!name) {
    console.log('Usage: npx tsx scripts/register.ts <agent-name>');
    process.exit(1);
  }

  const sphere = await loadWallet();
  const privateKey = getPrivateKeyHex(sphere);

  const result = await apiPost('/api/agent/register', { name }, privateKey);
  console.log('Registered successfully!');
  console.log('Agent ID:', result.agent.id);
  console.log('Public Key:', result.agent.public_key);
  console.log('Name:', result.agent.name);
}

main().catch((err) => {
  console.error('Registration failed:', err.message);
  process.exit(1);
});
