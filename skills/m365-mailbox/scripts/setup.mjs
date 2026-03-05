#!/usr/bin/env node
import fs from 'node:fs';
import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { PublicClientApplication } from '@azure/msal-node';
import { ensureSecretsDir, profilePaths, writeJson, getArg, mustGetArg, csv } from './_lib.mjs';

// Permission bundles
const bundles = {
  read: { allow: ['read'], scopes: ['Mail.Read'] },
  draft: { allow: ['read', 'draft'], scopes: ['Mail.ReadWrite'] },
  send: { allow: ['read', 'draft', 'send'], scopes: ['Mail.ReadWrite', 'Mail.Send'] },
  full: { allow: ['read', 'draft', 'send'], scopes: ['Mail.ReadWrite', 'Mail.Send'] },
};

function uniq(arr) {
  return [...new Set(arr)];
}

async function promptIfMissing(value, question) {
  if (value) return value;
  const rl = readline.createInterface({ input, output });
  const ans = (await rl.question(question)).trim();
  rl.close();
  return ans;
}

const profile = mustGetArg('profile');
let tenant = getArg('tenant', 'organizations'); // organizations|consumers|common|<tenantId>
let email = getArg('email', undefined);
let clientId = getArg('clientId', undefined);
const tz = getArg('tz', 'Europe/Vienna');

// User choice: minimal vs broad
// --consent minimal|broad
let consent = getArg('consent', undefined);
// User choice: allowed capabilities (read,draft,send)
let allowCsv = getArg('allow', undefined); // e.g. read,draft,send
let bundle = getArg('bundle', undefined); // read|draft|send|full
const offline = process.argv.includes('--offline');

clientId = await promptIfMissing(clientId, 'App (client) ID: ');
tenant = await promptIfMissing(tenant, 'Tenant (organizations|consumers|common or tenantId): ');

if (!consent) {
  consent = (await promptIfMissing(undefined, 'Consent mode (minimal|broad) [minimal]: ')) || 'minimal';
}

let allow;
let baseScopes;

if (bundle) {
  const b = bundles[bundle];
  if (!b) throw new Error(`Unknown --bundle ${bundle}`);
  allow = b.allow;
  baseScopes = b.scopes;
} else {
  if (!allowCsv) {
    allowCsv = (await promptIfMissing(undefined, 'Allow OpenClaw to do (comma list: read,draft,send) [read]: ')) || 'read';
  }
  allow = csv(allowCsv);
  if (allow.includes('send') || allow.includes('draft')) {
    baseScopes = allow.includes('send') ? ['Mail.ReadWrite', 'Mail.Send'] : ['Mail.ReadWrite'];
  } else {
    baseScopes = ['Mail.Read'];
  }
}

// Consent scopes decision
const requestedScopes = consent === 'broad'
  ? ['Mail.Read', 'Mail.ReadWrite', 'Mail.Send']  // broad = all permissions to avoid scope mismatches
  : baseScopes;

const scopes = uniq([
  ...requestedScopes,
  ...(offline ? ['offline_access'] : []),
  'openid',
  'profile',
  'email',
]);

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

await pca.acquireTokenByDeviceCode({
  scopes,
  deviceCodeCallback: (resp) => {
    const uri = resp.verificationUri || resp.verification_uri || 'https://microsoft.com/devicelogin';
    const code = resp.userCode || resp.user_code;
    console.log(`Open ${uri} and enter code: ${code}`);
  },
});

writeJson(cfgPath, {
  clientId,
  tenant,
  email,
  tz,
  consentMode: consent,
  requestedScopes,
  offlineAccess: offline,
  policy: {
    allow: uniq(allow),
    // Default safety: ask for confirmation for any write-like action.
    // (read is autonomous; draft/send require explicit confirmation by default)
    requireConfirm: uniq([
      ...(uniq(allow).includes('draft') ? ['draft'] : []),
      ...(uniq(allow).includes('send') ? ['send'] : []),
    ]),
  },
  createdAt: new Date().toISOString(),
});

console.log(`OK: profile=${profile} consent=${consent} allow=${uniq(allow).join(',')}`);
