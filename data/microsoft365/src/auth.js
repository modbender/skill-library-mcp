// custom-ms/src/auth.js
const { loadConfig, saveTokens, loadTokens, normalizeAccount } = require('./config');

const fetchFn = globalThis.fetch;

const SCOPES = 'User.Read Mail.Read Mail.Send Calendars.ReadWrite Contacts.ReadWrite Files.ReadWrite.All offline_access';
const PERSONAL_TENANT_ID = '9188040d-6c67-4c5b-b112-36a304b66dad';

function toAccountLabel(value, fallback = 'personal') {
  const normalized = normalizeAccount(String(value || '').toLowerCase());
  return normalized || normalizeAccount(fallback);
}

function looksPersonalTenant(jwtPayload = {}) {
  const tid = String(jwtPayload.tid || '').toLowerCase();
  return tid === PERSONAL_TENANT_ID;
}

function decodeJwtPayload(token) {
  try {
    const parts = String(token || '').split('.');
    if (parts.length < 2) return null;
    const payloadB64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const padded = payloadB64 + '='.repeat((4 - (payloadB64.length % 4)) % 4);
    const decoded = Buffer.from(padded, 'base64').toString('utf8');
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

async function discoverAccountLabel(accessToken, fallbackAccountName) {
  const fallback = toAccountLabel(fallbackAccountName, 'personal');

  const jwtPayload = decodeJwtPayload(accessToken) || {};
  if (looksPersonalTenant(jwtPayload)) {
    return 'personal';
  }

  try {
    const orgRes = await fetchFn('https://graph.microsoft.com/v1.0/organization?$select=displayName', {
      headers: { Authorization: `Bearer ${accessToken}` }
    });

    if (orgRes.ok) {
      const orgData = await orgRes.json();
      const orgName = orgData?.value?.[0]?.displayName;
      if (orgName) return toAccountLabel(orgName, fallback);
    }
  } catch (err) {
    console.warn(`[auth][discoverAccountLabel] organisatie lookup mislukt: ${err.message}`);
  }

  try {
    const meRes = await fetchFn('https://graph.microsoft.com/v1.0/me?$select=userPrincipalName,mail', {
      headers: { Authorization: `Bearer ${accessToken}` }
    });

    if (meRes.ok) {
      const meData = await meRes.json();
      const identity = String(meData?.userPrincipalName || meData?.mail || '').toLowerCase();

      // Niet-perfecte fallback, maar voor MSA is dit vrijwel altijd personal.
      if (identity.endsWith('@outlook.com') || identity.endsWith('@hotmail.com') || identity.endsWith('@live.com') || identity.endsWith('@msn.com')) {
        return 'personal';
      }
    }
  } catch (err) {
    console.warn(`[auth][discoverAccountLabel] user lookup mislukt: ${err.message}`);
  }

  return fallback;
}

if (!fetchFn) {
  throw new Error('global fetch is niet beschikbaar. Gebruik Node.js 18+ of voeg een fetch polyfill toe.');
}

async function startDeviceFlow(account = 'default') {
  const accountName = normalizeAccount(account);
  const config = loadConfig(accountName);

  if (!config.clientId) {
    throw new Error(`Geen Client ID gevonden voor account '${accountName}'. Controleer je .env of config.${accountName}.json.`);
  }

  const tokenEndpoint = `https://login.microsoftonline.com/${config.tenantId}/oauth2/v2.0/devicecode`;
  console.log(`[DEBUG] Auth Endpoint: ${tokenEndpoint}`); // Toegevoegd voor diagnose
  const body = new URLSearchParams({
    client_id: config.clientId,
    scope: SCOPES
  });

  const res = await fetchFn(tokenEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body
  });

  if (!res.ok) {
    throw new Error(`Auth request faalde: ${res.status} ${res.statusText} - ${await res.text()}`);
  }

  const data = await res.json();
  console.log('\n========================================');
  console.log(`[Account: ${accountName}]`);
  console.log('Log in via je browser op:');
  console.log(`>>> ${data.verification_uri} <<<`);
  console.log(`Code: >>> ${data.user_code} <<<`);
  console.log('========================================\n');

  return pollForToken(data.device_code, data.interval, config, accountName);
}

async function pollForToken(deviceCode, interval, config, accountName) {
  const tokenEndpoint = `https://login.microsoftonline.com/${config.tenantId}/oauth2/v2.0/token`;
  let pollInterval = Number(interval || 5);
  let attempt = 0;

  while (true) {
    attempt += 1;
    await new Promise(resolve => setTimeout(resolve, pollInterval * 1000));

    const params = {
      grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
      client_id: config.clientId,
      device_code: deviceCode
    };

    if (config.clientSecret) params.client_secret = config.clientSecret;

    const body = new URLSearchParams(params);
    const res = await fetchFn(tokenEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body
    });

    const responseText = await res.text();

    let data;
    try {
      data = JSON.parse(responseText);
    } catch {
      console.error(`\n[auth][pollForToken] Ongeldige JSON in token response (attempt ${attempt})`);
      console.error(`[auth][pollForToken] HTTP ${res.status} ${res.statusText}`);
      console.error(`[auth][pollForToken] Body: ${responseText}`);
      throw new Error(`Token endpoint gaf geen JSON terug (${res.status} ${res.statusText}).`);
    }

    if (data.error) {
      if (data.error === 'authorization_pending') {
        process.stdout.write('.');
        continue;
      }
      if (data.error === 'slow_down') {
        pollInterval += 5;
        console.warn(`\n[auth][pollForToken] Microsoft vroeg om vertraging. Nieuw interval: ${pollInterval}s (attempt ${attempt})`);
        continue;
      }
      if (data.error === 'expired_token') {
        console.error('\nCode verlopen. Start opnieuw.');
        return null;
      }

      console.error('\n[auth][pollForToken] Token aanvraag mislukt na login. Details:');
      console.error({
        attempt,
        status: res.status,
        error: data.error,
        description: data.error_description,
        trace_id: data.trace_id,
        correlation_id: data.correlation_id,
      });

      throw new Error(`Token fout: ${data.error_description || data.error}`);
    }

    const discoveredAccountName = await discoverAccountLabel(data.access_token, accountName);

    console.log(`\nSucces! Authenticatie klaar.`);
    if (discoveredAccountName !== accountName) {
      console.log(`[auth] Account auto-discovered: '${accountName}' -> '${discoveredAccountName}'`);
    } else {
      console.log(`[auth] Account label: '${discoveredAccountName}'`);
    }

    // Tokens pas opslaan nadat het accountlabel bekend is.
    saveTokens(data, discoveredAccountName);
    console.log(`Tokens opgeslagen voor account '${discoveredAccountName}'.`);
    return data.access_token;
  }
}

function tokenIsExpiring(tokens) {
  const bufferMs = 300000; // 5 min buffer

  if (!tokens || typeof tokens !== 'object') return true;

  if (Number.isFinite(tokens.expires_at)) {
    return Date.now() > (tokens.expires_at - bufferMs);
  }

  // Als expires_at er niet is, bereken het op basis van expires_in (als aanwezig)
  if (tokens.expires_in) {
      // Als we geen created_at hebben, kunnen we het niet berekenen, dus dwing refresh af voor de zekerheid
      // Tenzij we net ingelogd zijn, maar dan zou saveTokens expires_at gezet moeten hebben.
      return true; 
  }

  return true;
}

async function getAccessToken(account = 'default') {
  const accountName = normalizeAccount(account);
  const tokens = loadTokens(accountName);
  const config = loadConfig(accountName);

  if (!config.clientId) {
    throw new Error(`Geen Client ID gevonden voor account '${accountName}'.`);
  }

  if (!tokens) {
    console.log(`Geen tokens voor account '${accountName}'. Start login...`);
    return startDeviceFlow(accountName);
  }

  if (tokenIsExpiring(tokens)) {
    console.log(`Token verlopen voor account '${accountName}'. Vernieuwen...`);
    return refreshAccessToken(tokens, config, accountName);
  }

  return tokens.access_token;
}

async function refreshAccessToken(existingTokens, config, accountName) {
  const tokenEndpoint = `https://login.microsoftonline.com/${config.tenantId}/oauth2/v2.0/token`;

  const params = {
    grant_type: 'refresh_token',
    client_id: config.clientId,
    refresh_token: existingTokens.refresh_token,
    scope: SCOPES
  };

  if (config.clientSecret) params.client_secret = config.clientSecret;

  const body = new URLSearchParams(params);

  try {
    const res = await fetchFn(tokenEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body
    });

    if (!res.ok) {
      const errText = await res.text();
      console.error('Refresh mislukt:', errText);
      console.log('Forceer nieuwe login...');
      return startDeviceFlow(accountName);
    }

    const data = await res.json();

    const mergedTokens = {
      ...existingTokens,
      ...data,
      refresh_token: data.refresh_token || existingTokens.refresh_token
    };

    saveTokens(mergedTokens, accountName);
    return mergedTokens.access_token;
  } catch (error) {
    console.error('Fout bij token refresh:', error.message);
    return null;
  }
}

module.exports = { startDeviceFlow, getAccessToken };
