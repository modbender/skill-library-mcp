import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { Sphere } from '@unicitylabs/sphere-sdk';
import { createNodeProviders } from '@unicitylabs/sphere-sdk/impl/nodejs';
import { config } from './config.js';

let sphereInstance: Sphere | null = null;

export async function loadWallet(): Promise<Sphere> {
  if (sphereInstance) return sphereInstance;

  const mnemonicPath = join(config.walletDataDir, 'mnemonic.txt');
  const mnemonic = existsSync(mnemonicPath)
    ? readFileSync(mnemonicPath, 'utf-8').trim()
    : undefined;

  if (!mnemonic) {
    throw new Error('No wallet found. Set up your wallet using the Unicity plugin first (openclaw uniclaw setup)');
  }

  const trustBasePath = join(config.walletDataDir, 'trustbase.json');

  const providers = createNodeProviders({
    network: config.network,
    dataDir: config.walletDataDir,
    tokensDir: config.walletTokensDir,
    oracle: {
      trustBasePath,
      apiKey: process.env.UNICITY_API_KEY ?? 'sk_06365a9c44654841a366068bcfc68986',
    },
    transport: {
      debug: true,
    },
  });

  const { sphere } = await Sphere.init({
    ...providers,
    mnemonic,
  });

  if (!sphere.identity) {
    throw new Error('Wallet mnemonic found but identity could not be restored');
  }

  sphereInstance = sphere;
  return sphere;
}

// Access the private key from Sphere's internal _identity field.
// The public `sphere.identity` getter strips privateKey, but the
// underlying TypeScript-private `_identity` stores a FullIdentity
// which includes `privateKey: string`.
export function getPrivateKeyHex(sphere: Sphere): string {
  const fullIdentity = (sphere as any)._identity;
  if (!fullIdentity?.privateKey) {
    throw new Error('No wallet identity or private key not accessible');
  }
  return fullIdentity.privateKey;
}
