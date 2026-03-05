#!/usr/bin/env node
/**
 * Import a raw OAuth token JSON (from device code / token endpoint) into a skill profile.
 *
 * This is a fallback when MSAL device-code flow is blocked/broken by tenant policy.
 *
 * Usage:
 *  node skills/m365-calendar/scripts/import-raw-token.mjs --profile tom-home --file ~/.openclaw/secrets/m365-calendar/tom-home-raw-token.json
 */

import fs from 'node:fs';
import { mustGetArg, profilePaths, ensureSecretsDir, writeJson } from './_lib.mjs';

const profile = mustGetArg('profile');
const file = mustGetArg('file');

ensureSecretsDir();
const { cfgPath, cachePath } = profilePaths(profile);

const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
if (!raw.access_token) throw new Error('Raw token file missing access_token');

// Store as a simple JSON cache format that _graph.mjs can consume when present.
fs.writeFileSync(cachePath, JSON.stringify(raw, null, 2) + '\n', 'utf8');

writeJson(cfgPath, {
  clientId: raw.client_id || null,
  tenant: raw.tenant || 'consumers',
  email: raw.email || null,
  scopes: raw.scope ? String(raw.scope).split(' ') : [],
  authFlow: 'device_code_raw_import',
  createdAt: new Date().toISOString(),
  notes: 'Imported raw token JSON. Prefer MSAL cache when possible.',
});

console.log(`OK: imported raw token into profile=${profile}`);
