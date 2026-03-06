import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { bytesToHex, hexToBytes } from '@noble/hashes/utils.js';
import { secp256k1 } from '@noble/curves/secp256k1.js';
import { config } from '../lib/config.js';

function parseArgs(): Record<string, string> {
  const args: Record<string, string> = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--') && argv[i + 1]) {
      args[argv[i].slice(2)] = argv[i + 1];
      i++;
    }
  }
  return args;
}

async function main() {
  const args = parseArgs();
  if (!args.name) {
    console.log('Usage: npx tsx scripts/register.ts --name <display-name> [--nostr <nostr-pubkey>]');
    process.exit(1);
  }

  const sphere = await loadWallet();
  const privateKeyHex = getPrivateKeyHex(sphere);
  const publicKey = bytesToHex(secp256k1.getPublicKey(hexToBytes(privateKeyHex), true));
  const nametag = sphere.identity?.nametag ?? undefined;

  const body: Record<string, unknown> = {
    name: args.name,
    public_key: publicKey,
  };
  if (nametag) body.nametag = nametag;
  if (args.nostr) body.nostr_pubkey = args.nostr;

  const res = await fetch(`${config.serverUrl}/api/agent/register`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  if (!res.ok) {
    console.error('Registration failed:', data.error);
    process.exit(1);
  }

  console.log('Registered successfully!');
  console.log('Agent ID:', data.agentId);
  if (data.nametag) console.log('Nametag:', data.nametag);
  console.log('Display name:', data.displayName ?? args.name);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
