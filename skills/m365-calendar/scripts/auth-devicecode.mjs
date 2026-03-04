#!/usr/bin/env node
import fs from 'node:fs';
import { PublicClientApplication } from '@azure/msal-node';
import { ensureSecretsDir, profilePaths, writeJson, getArg, mustGetArg } from './_lib.mjs';

/**
 * Device code auth for delegated Graph calendar scopes.
 *
 * Examples:
 *  node skills/m365-calendar/scripts/auth-devicecode.mjs --profile business --tenant organizations --email you@company.com
 *  node skills/m365-calendar/scripts/auth-devicecode.mjs --profile home --tenant consumers --email you@outlook.com
 *
 * Optional:
 *  --clientId <appId>  (use an app registration that allows personal Microsoft accounts for consumers)
 */

const profile = mustGetArg('profile');
const tenant = getArg('tenant', 'organizations'); // organizations|consumers|common|<tenantId>
const email = getArg('email', undefined);
const clientId = mustGetArg('clientId');

// Minimum scopes for our use-cases
const wantOffline = process.argv.includes('--offline');

const scopes = [
  'Calendars.Read',
  'Calendars.ReadWrite',
  // offline_access is optional; without it we avoid long-lived refresh tokens on disk.
  ...(wantOffline ? ['offline_access'] : []),
  'openid',
  'profile',
  'email',
];

ensureSecretsDir();
const { cfgPath, cachePath } = profilePaths(profile);

let cache = fs.existsSync(cachePath) ? fs.readFileSync(cachePath, 'utf8') : '';

const pca = new PublicClientApplication({
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenant}`,
  },
  cache: {
    cachePlugin: {
      beforeCacheAccess: async (ctx) => {
        if (cache) ctx.tokenCache.deserialize(cache);
      },
      afterCacheAccess: async (ctx) => {
        if (ctx.cacheHasChanged) {
          cache = ctx.tokenCache.serialize();
          fs.writeFileSync(cachePath, cache, 'utf8');
        }
      },
    },
  },
});

const result = await pca.acquireTokenByDeviceCode({
  scopes,
  deviceCodeCallback: (resp) => {
    // For consumers, we saw MSAL returning undefined fields; build our own message.
    const uri = resp.verificationUri || resp.verification_uri || 'https://microsoft.com/devicelogin';
    const code = resp.userCode || resp.user_code;
    console.log(`Open ${uri} and enter code: ${code}`);
  },
});

writeJson(cfgPath, {
  clientId,
  tenant,
  email,
  scopes: wantOffline
    ? ['Calendars.Read', 'Calendars.ReadWrite', 'offline_access']
    : ['Calendars.Read', 'Calendars.ReadWrite'],
  authFlow: wantOffline ? 'device_code_delegated_offline' : 'device_code_delegated',
  createdAt: new Date().toISOString(),
  notes: wantOffline
    ? 'offline_access enabled (refresh tokens may be stored in local token cache). Do not commit secrets.'
    : 'offline_access disabled (no refresh token expected). Do not commit secrets.',
});

console.log(`OK: authenticated profile=${profile} tenant=${tenant} user=${result?.account?.username || 'unknown'}`);
