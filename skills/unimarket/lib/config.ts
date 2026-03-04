import { homedir } from 'node:os';
import { join } from 'node:path';

export const config = {
  serverUrl: process.env.VECTOR_SPHERE_SERVER ?? 'https://market-api.unicity.network',
  walletDataDir: process.env.VECTOR_WALLET_DIR ?? join(homedir(), '.openclaw', 'unicity'),
  walletTokensDir: process.env.VECTOR_TOKENS_DIR ?? join(homedir(), '.openclaw', 'unicity', 'tokens'),
  network: (process.env.VECTOR_NETWORK ?? 'testnet') as 'testnet' | 'mainnet' | 'dev',
};
