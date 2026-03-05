// Shared NS API helpers
// Security: enforce allowlisted host + HTTPS and never log subscription keys.

const NS_API_HOST_ALLOWLIST = new Set([
  'gateway.apiportal.ns.nl',
]);

export function requireNsSubscriptionKey() {
  // Prefer the newer env var name, but support legacy NS_API_KEY for backward compatibility.
  const key = process.env.NS_SUBSCRIPTION_KEY || process.env.NS_API_KEY;
  if (!key) {
    throw new Error('NS_SUBSCRIPTION_KEY not set (or legacy NS_API_KEY missing)');
  }
  return key;
}

function assertAllowlistedUrl(url) {
  const u = typeof url === 'string' ? new URL(url) : url;
  if (u.protocol !== 'https:') {
    throw new Error(`Refusing non-HTTPS request: ${u.protocol}`);
  }
  if (!NS_API_HOST_ALLOWLIST.has(u.hostname)) {
    throw new Error(`Refusing request to non-allowlisted host: ${u.hostname}`);
  }
  return u;
}

export async function nsFetch(url, { subscriptionKey, headers = {}, ...opts } = {}) {
  const u = assertAllowlistedUrl(url);

  const res = await fetch(u, {
    ...opts,
    headers: {
      'Ocp-Apim-Subscription-Key': subscriptionKey,
      'Accept': 'application/json',
      ...headers,
    },
  });

  return res;
}
