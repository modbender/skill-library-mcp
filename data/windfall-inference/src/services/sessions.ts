// Shared session store — used by both index.ts and inference route
// Avoids circular imports

export interface WalletSession {
  walletAddress: string;
  expiresAt: number;
  isAgent?: boolean;
  identityTier?: string;
}

export const walletSessions = new Map<string, WalletSession>();

/** Look up a wallet session by Bearer token. Returns session if valid, null if expired/missing. */
export function getWalletSession(bearerToken: string): WalletSession | null {
  const session = walletSessions.get(bearerToken);
  if (!session) return null;
  if (Date.now() > session.expiresAt) {
    walletSessions.delete(bearerToken);
    return null;
  }
  return session;
}
