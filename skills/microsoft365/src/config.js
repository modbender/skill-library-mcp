// custom-ms/src/config.js
const fs = require('fs');
const path = require('path');

const os = require('os');

let dotEnvLoaded = false;

function getOpenClawPath() {
  return process.env.OPENCLAW_HOME || path.join(os.homedir(), '.openclaw');
}

function parseDotEnv(content) {
  const env = {};
  const lines = String(content || '').split(/\r?\n/);

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;

    const eq = trimmed.indexOf('=');
    if (eq === -1) continue;

    const key = trimmed.slice(0, eq).trim();
    if (!key) continue;

    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }

    env[key] = value;
  }

  return env;
}

function loadDotEnvOnce() {
  if (dotEnvLoaded) return;
  dotEnvLoaded = true;

  const envPath = path.join(getOpenClawPath(), 'credentials/ms365.env');
  if (!fs.existsSync(envPath)) return;

  try {
    const raw = fs.readFileSync(envPath, 'utf8');
    const parsed = parseDotEnv(raw);

    for (const [key, value] of Object.entries(parsed)) {
      if (process.env[key] !== value) {
        process.env[key] = value;
      }
    }
  } catch (err) {
    console.error(`[config] Kon .env niet laden (${envPath}):`, err.message);
  }
}

function normalizeAccount(account = 'default') {
  const raw = String(account || '').trim().toLowerCase();
  const safe = raw.replace(/[^a-z0-9._-]/g, '');
  return safe || 'default';
}

function getPaths(account = 'default') {
  const accountName = normalizeAccount(account);
  const credentialsDir = path.join(getOpenClawPath(), 'credentials');
  
  return {
    config: path.join(__dirname, `../config.${accountName}.json`), // Config blijft in skill map (niet gevoelig)
    tokens: path.join(credentialsDir, `ms365.tokens.${accountName}.json`)
  };
}

function safeReadJson(filePath, fallback = null) {
  try {
    if (!fs.existsSync(filePath)) return fallback;
    const raw = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    console.error(`Kon JSON niet lezen/parsen (${filePath}):`, err.message);
    return fallback;
  }
}

function loadConfig(account = 'default') {
  loadDotEnvOnce();

  const accountName = normalizeAccount(account);
  const { config: configPath } = getPaths(accountName);

  // 1) Account-specifiek configbestand (optioneel)
  const fileConfig = safeReadJson(configPath, null);
  if (fileConfig && typeof fileConfig === 'object') {
    return fileConfig;
  }

  // 2) Fallback naar env (account-specifiek => globaal)
  // Ondersteunt dynamische namen zoals saxion/personal.
  const envPrefix = `MICROSOFT_${accountName.toUpperCase()}_`;

  const clientId = process.env[`${envPrefix}CLIENT_ID`] || process.env.MICROSOFT_CLIENT_ID || null;
  const tenantId = process.env[`${envPrefix}TENANT_ID`] || process.env.MICROSOFT_TENANT_ID || 'common';
  const clientSecret = process.env[`${envPrefix}CLIENT_SECRET`] || process.env.MICROSOFT_CLIENT_SECRET;

  if (clientId) {
    return {
      clientId,
      tenantId,
      clientSecret,
      scopes: 'User.Read Mail.Read Calendars.Read Contacts.Read Files.Read.All offline_access'
    };
  }

  // 3) Geen credentials gevonden
  // Tenant blijft accountspecifiek (bijv. personal=consumers) voor consistente diagnostiek.
  return { clientId: null, tenantId, scopes: '' };
}

function loadTokens(account = 'default') {
  const { tokens: tokenPath } = getPaths(account);
  return safeReadJson(tokenPath, null);
}

function saveTokens(tokens, account = 'default') {
  if (!tokens || typeof tokens !== 'object') {
    throw new Error('saveTokens verwacht een tokens-object.');
  }

  const { tokens: tokenPath } = getPaths(account);
  const toSave = { ...tokens };

  // Houd refresh_token vast als provider hem niet altijd terugstuurt,
  // deze merge gebeurt in auth.js bij refresh.
  if (!toSave.expires_at) {
    const expiresIn = Number(toSave.expires_in || 0);
    if (Number.isFinite(expiresIn) && expiresIn > 0) {
      toSave.expires_at = Date.now() + (expiresIn * 1000);
    }
  }

  fs.writeFileSync(tokenPath, JSON.stringify(toSave, null, 2));
}

module.exports = { loadConfig, loadTokens, saveTokens, normalizeAccount };
