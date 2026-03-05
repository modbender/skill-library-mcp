// ============================================================================
// api.js — HTTP request helpers for the OpenClaw Marketplace API
//
// Uses V1 API endpoints for lightweight responses (AssetCompact).
// Uses Node.js built-in fetch (available since Node 18)
// ============================================================================

'use strict';

const config = require('./config.js');

/**
 * Build standard auth headers (token + device ID)
 */
function authHeaders() {
  const headers = {};
  const token = config.getAuthToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const deviceId = config.getDeviceId();
  if (deviceId) headers['X-Device-ID'] = deviceId;
  return headers;
}

/**
 * Make a GET request to the API
 * @param {string} apiPath - API path (e.g., '/api/v1/assets')
 * @param {object} [params] - Query parameters
 * @returns {Promise<object>} Parsed JSON response
 */
async function get(apiPath, params = {}) {
  const url = new URL(apiPath, config.getApiBase());
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') {
      url.searchParams.set(k, String(v));
    }
  }

  const res = await fetch(url.toString(), { headers: authHeaders() });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API error ${res.status}: ${body || res.statusText}`);
  }
  return res.json();
}

/**
 * Make a POST request with JSON body
 * @param {string} apiPath
 * @param {object} body
 * @param {object} [extraHeaders]
 * @returns {Promise<{status: number, data: object}>}
 */
async function post(apiPath, body, extraHeaders = {}) {
  const url = new URL(apiPath, config.getApiBase());

  const headers = {
    'Content-Type': 'application/json',
    ...authHeaders(),
    ...extraHeaders,
  };

  const res = await fetch(url.toString(), {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  return { status: res.status, data };
}

/**
 * POST multipart form data (for publish with file upload)
 * Node 18+ supports FormData natively in fetch
 * @param {string} apiPath
 * @param {FormData} formData
 * @param {object} [extraHeaders]
 * @returns {Promise<{status: number, data: object}>}
 */
async function postMultipart(apiPath, formData, extraHeaders = {}) {
  const url = new URL(apiPath, config.getApiBase());

  const headers = {
    ...authHeaders(),
    ...extraHeaders,
  };

  const res = await fetch(url.toString(), {
    method: 'POST',
    headers,
    body: formData,
  });
  const data = await res.json().catch(() => ({}));
  return { status: res.status, data };
}

/**
 * Download a file (returns Buffer or null if 404)
 * @param {string} apiPath
 * @returns {Promise<Buffer|null>}
 */
async function download(apiPath) {
  const url = new URL(apiPath, config.getApiBase());

  const res = await fetch(url.toString(), { headers: authHeaders() });
  if (!res.ok) return null;
  const arrayBuffer = await res.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

/**
 * Search assets via V1 API (returns lightweight AssetCompact items).
 *
 * V1 response shape: { query, total, items: AssetCompact[], nextCursor }
 * AssetCompact fields: id, name, displayName, type, description, tags,
 *   installs, rating, author (string), authorId, version, installCommand,
 *   updatedAt, category
 *
 * @param {string} query
 * @param {object} [opts] - { type, limit }
 * @returns {Promise<object>} V1 search response
 */
async function searchAssets(query, opts = {}) {
  const params = { q: query, limit: opts.limit || 20 };
  if (opts.type) params.type = opts.type;
  return get('/api/v1/search', params);
}

/**
 * Find an asset by type and slug (with optional author filter).
 * Uses V1 list endpoint for lightweight data.
 *
 * @param {string} type
 * @param {string} slug
 * @param {string} [authorFilter] - author ID or author name to filter by
 * @returns {Promise<object|null>}
 */
async function findAsset(type, slug, authorFilter) {
  const result = await get('/api/v1/assets', { q: slug, type, limit: 50 });
  const assets = result?.items || [];

  // Exact match on name
  let matches = assets.filter(a => a.name === slug);
  if (authorFilter) {
    // authorFilter could be an authorId or author name
    const authorMatches = matches.filter(a =>
      a.authorId === authorFilter || a.author === authorFilter
    );
    if (authorMatches.length > 0) matches = authorMatches;
  }

  // Fallback: partial match on name
  if (matches.length === 0) {
    matches = assets.filter(a => a.name.includes(slug));
    if (authorFilter) {
      const authorMatches = matches.filter(a =>
        a.authorId === authorFilter || a.author === authorFilter
      );
      if (authorMatches.length > 0) matches = authorMatches;
    }
  }

  if (matches.length === 0) return null;

  // Prefer the one with an author ID
  matches.sort((a, b) => (b.authorId || '').localeCompare(a.authorId || ''));
  return matches[0];
}

/**
 * Get asset detail (L2) by ID via V1 API.
 * Returns full detail including readme, files, versions.
 *
 * @param {string} id - Asset ID
 * @returns {Promise<object|null>}
 */
async function getAssetById(id) {
  try {
    return await get(`/api/v1/assets/${id}`);
  } catch (e) {
    if (e.message.includes('404')) return null;
    throw e;
  }
}

/**
 * Make a DELETE request to the API
 * @param {string} apiPath
 * @param {object} [body] - Optional JSON body
 * @returns {Promise<{status: number, data: object}>}
 */
async function del(apiPath, body) {
  const url = new URL(apiPath, config.getApiBase());

  const opts = {
    method: 'DELETE',
    headers: { ...authHeaders() },
  };
  if (body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }

  const res = await fetch(url.toString(), opts);
  const data = await res.json().catch(() => ({}));
  return { status: res.status, data };
}

/**
 * Resolve an asset reference to a full asset object.
 * Accepts:
 *   - Direct ID: "s-abc123", "tr-fc617094de29f938"
 *   - type/@author/slug: "trigger/@xiaoyue/pdf-watcher"
 *
 * Uses V1 API: GET /api/v1/assets/:id for ID lookups,
 * findAsset() (V1 search) for type/slug lookups.
 *
 * @param {string} ref
 * @returns {Promise<object>} asset object with at least { id, name, ... }
 */
async function resolveAssetRef(ref) {
  // Direct ID pattern: prefix + dash + hex
  if (/^[a-z]+-[0-9a-f]{8,}$/.test(ref)) {
    const result = await getAssetById(ref);
    if (!result) throw new Error(`Asset not found: ${ref}`);
    return result;
  }

  // type/@author/slug format
  const parts = ref.split('/');
  if (parts.length < 2) {
    throw new Error(`Invalid asset reference: ${ref}. Use <id> or <type>/@<author>/<slug>`);
  }

  const type = parts[0];
  let slug, authorFilter = '';

  if (parts.length >= 3 && parts[1].startsWith('@')) {
    authorFilter = parts[1].slice(1);
    slug = parts.slice(2).join('/');
  } else {
    slug = parts.slice(1).join('/');
  }

  const asset = await findAsset(type, slug, authorFilter);
  if (!asset) {
    throw new Error(`Asset not found: ${ref}`);
  }
  return asset;
}

module.exports = {
  get,
  post,
  del,
  postMultipart,
  download,
  searchAssets,
  findAsset,
  getAssetById,
  resolveAssetRef,
};
