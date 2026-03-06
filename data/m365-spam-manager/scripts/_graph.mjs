import fs from 'node:fs';
import { PublicClientApplication } from '@azure/msal-node';
import { profilePaths, readJson } from './_lib.mjs';

export async function getAccessToken(profile, scopes) {
  const { cfgPath, cachePath } = profilePaths(profile);
  if (!fs.existsSync(cfgPath)) throw new Error(`Missing profile config: ${cfgPath} (run m365-mailbox setup first)`);
  if (!fs.existsSync(cachePath)) throw new Error(`Missing token cache: ${cachePath} (run m365-mailbox setup first)`);

  const cfg = readJson(cfgPath);
  const cacheText = fs.readFileSync(cachePath, 'utf8');

  // Try raw token first
  try {
    const raw = JSON.parse(cacheText);
    if (raw && typeof raw === 'object' && raw.access_token) return raw.access_token;
  } catch {}

  // MSAL cache
  let cache = cacheText;
  const pca = new PublicClientApplication({
    auth: {
      clientId: cfg.clientId,
      authority: `https://login.microsoftonline.com/${cfg.tenant}`,
    },
    cache: {
      cachePlugin: {
        beforeCacheAccess: async (ctx) => ctx.tokenCache.deserialize(cache),
        afterCacheAccess: async (ctx) => {
          if (ctx.cacheHasChanged) {
            cache = ctx.tokenCache.serialize();
            fs.writeFileSync(cachePath, cache, 'utf8');
          }
        },
      },
    },
  });

  const accounts = await pca.getTokenCache().getAllAccounts();
  if (!accounts.length) throw new Error(`No accounts in token cache for profile ${profile}`);

  const res = await pca.acquireTokenSilent({ account: accounts[0], scopes });
  return res.accessToken;
}

export async function graphFetch(url, { method = 'GET', headers = {}, body, token } = {}) {
  const res = await fetch(url, {
    method,
    headers: {
      ...headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body,
  });

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const msg = typeof data === 'object' ? JSON.stringify(data) : String(data);
    throw new Error(`Graph error ${res.status}: ${msg.slice(0, 800)}`);
  }

  return data;
}
