import { homedir } from 'node:os';
import { join } from 'node:path';

export const config = {
  serverUrl: process.env.UNICLAW_SERVER ?? 'https://api.uniclaw.app',
  walletDataDir: process.env.UNICLAW_WALLET_DIR ?? join(homedir(), '.openclaw', 'unicity'),
  walletTokensDir: process.env.UNICLAW_TOKENS_DIR ?? join(homedir(), '.openclaw', 'unicity', 'tokens'),
  network: (process.env.UNICLAW_NETWORK ?? 'testnet') as 'testnet' | 'mainnet' | 'dev',
};
