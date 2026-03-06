/**
 * Metadata sync — fetch RPCs from @openscan/metadata via CDN
 * Resolves latest version dynamically, fetches per-network RPC files,
 * and auto-selects RPCs with privacy-first ordering.
 */

const NPM_REGISTRY_URL = "https://registry.npmjs.org/@openscan/metadata";

// Fallback if registry is unreachable
const FALLBACK_VERSION = "1.1.1-alpha.0";

// Known EVM chain IDs to fetch RPCs for
const EVM_CHAIN_IDS = [1, 10, 56, 137, 8453, 42161, 11155111];
const BTC_SLUGS = ["mainnet", "testnet4"];

/**
 * Resolve the latest metadata version from npm registry.
 * Prefers alpha tag (has newest data), falls back to latest, then hardcoded.
 */
export async function resolveMetadataVersion() {
  try {
    const res = await fetch(NPM_REGISTRY_URL, {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return FALLBACK_VERSION;
    const data = await res.json();
    const tags = data["dist-tags"] || {};
    return tags.alpha || tags.latest || FALLBACK_VERSION;
  } catch {
    return FALLBACK_VERSION;
  }
}

/**
 * Build CDN base URL for a given metadata version
 */
export function cdnBase(version) {
  return `https://cdn.jsdelivr.net/npm/@openscan/metadata@${version}/dist`;
}

/**
 * Fetch RPC endpoints for a specific network from CDN
 */
export async function fetchNetworkRpcs(version, path) {
  const url = `${cdnBase(version)}/${path}`;
  const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
  if (!res.ok) return null;
  return res.json();
}

/**
 * Fetch RPCs for all known networks
 * Returns { [chainId]: { endpoints, networkId } }
 */
export async function fetchAllNetworkRpcs(version) {
  const results = {};

  // EVM networks
  const evmPromises = EVM_CHAIN_IDS.map(async (chainId) => {
    try {
      const data = await fetchNetworkRpcs(version, `rpcs/evm/${chainId}.json`);
      if (data?.endpoints) {
        results[String(chainId)] = data;
      }
    } catch { /* skip failed networks */ }
  });

  // BTC networks
  const btcPromises = BTC_SLUGS.map(async (slug) => {
    try {
      const data = await fetchNetworkRpcs(version, `rpcs/btc/${slug}.json`);
      if (data?.endpoints) {
        const key = slug === "mainnet" ? "btc/mainnet" : `btc/${slug}`;
        results[key] = data;
      }
    } catch { /* skip */ }
  });

  await Promise.all([...evmPromises, ...btcPromises]);
  return results;
}

/**
 * Auto-select RPCs from a list of endpoints.
 * Privacy-first, open-source preferred, capped at maxRpcs.
 * 
 * @param {Array} endpoints - Raw endpoints from metadata
 * @param {Object} options - { maxRpcs, privateOnly }
 * @returns {Array} Selected RPC objects with url, tracking, provider, isOpenSource
 */
export function autoSelectRpcs(endpoints, options = {}) {
  const { maxRpcs = 5, privateOnly = false } = options;

  let filtered = endpoints.filter(e => e.isPublic);

  // Exclude wss:// and template URLs
  filtered = filtered.filter(e =>
    !e.url.startsWith("wss://") && !e.url.includes("${")
  );

  if (privateOnly) {
    filtered = filtered.filter(e => e.tracking === "none");
  }

  // Sort: tracking=none > limited > rest, then openSource=true first within tier
  const trackingOrder = { none: 0, limited: 1, unspecified: 2, yes: 3 };
  filtered.sort((a, b) => {
    const ta = trackingOrder[a.tracking] ?? 9;
    const tb = trackingOrder[b.tracking] ?? 9;
    if (ta !== tb) return ta - tb;
    // Open source preferred
    if (a.isOpenSource && !b.isOpenSource) return -1;
    if (!a.isOpenSource && b.isOpenSource) return 1;
    return 0;
  });

  return filtered.slice(0, maxRpcs).map(e => ({
    url: e.url,
    tracking: e.tracking,
    provider: e.provider || "unknown",
    isOpenSource: e.isOpenSource || false,
  }));
}

/**
 * Full sync: resolve version, fetch all RPCs, auto-select, return ready config data.
 * Does NOT save — caller decides whether to merge/save.
 * 
 * @param {Object} options - { maxRpcs, privateOnly, version (override) }
 * @returns { version, networks: { [chainId]: { rpcs: [...], strategy: null } }, allEndpoints: { [chainId]: [...] } }
 */
export async function syncMetadata(options = {}) {
  const version = options.version || await resolveMetadataVersion();
  const allData = await fetchAllNetworkRpcs(version);

  const networks = {};
  const allEndpoints = {};

  for (const [key, data] of Object.entries(allData)) {
    allEndpoints[key] = data.endpoints || [];
    networks[key] = {
      rpcs: autoSelectRpcs(data.endpoints, options),
      strategy: null, // Will use global default
    };
  }

  return { version, networks, allEndpoints };
}

/**
 * Merge synced data into existing config.
 * - Networks with user-configured RPCs are preserved (but we flag removed RPCs)
 * - Networks without config get updated with new auto-selection
 * - metadataVersion and lastFetched are updated
 * 
 * @param {Object} config - Existing config
 * @param {Object} syncResult - From syncMetadata()
 * @returns { config, stats: { updated, unchanged, newRpcs, removedRpcs } }
 */
export function mergeIntoConfig(config, syncResult) {
  const stats = { updated: [], unchanged: [], newRpcs: 0, removedRpcs: 0 };

  for (const [chainId, syncNet] of Object.entries(syncResult.networks)) {
    const existing = config.networks[chainId];

    if (!existing || !existing.rpcs || existing.rpcs.length === 0) {
      // No existing config — use synced data
      config.networks[chainId] = {
        rpcs: syncNet.rpcs,
        strategy: syncNet.strategy, // null = use global default
      };
      stats.updated.push(chainId);
      stats.newRpcs += syncNet.rpcs.length;
    } else {
      // Existing config — check if any RPCs were removed from metadata
      const allUrls = new Set(
        (syncResult.allEndpoints[chainId] || []).map(e => e.url)
      );
      const before = existing.rpcs.length;
      existing.rpcs = existing.rpcs.map(rpc => {
        if (!allUrls.has(rpc.url) && !rpc.url.startsWith("http://localhost")) {
          return { ...rpc, _removed: true }; // Flag as removed from metadata
        }
        return rpc;
      });
      const removedCount = existing.rpcs.filter(r => r._removed).length;
      stats.removedRpcs += removedCount;

      if (removedCount > 0) {
        stats.updated.push(chainId);
      } else {
        stats.unchanged.push(chainId);
      }
    }
  }

  config.metadataVersion = syncResult.version;
  config.lastFetched = new Date().toISOString();

  return { config, stats };
}

export { EVM_CHAIN_IDS, BTC_SLUGS, FALLBACK_VERSION };
