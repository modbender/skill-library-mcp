/**
 * URL Normalization and Security (Phase 3.1)
 *
 * Provides functions to:
 * - Normalize URLs to canonical form
 * - Detect and block private IP ranges (SSRF prevention)
 * - Strip tracking parameters
 */

const { URL } = require('url');

// Tracking parameters to strip (common analytics/campaign params)
const TRACKING_PARAMS = new Set([
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
  'fbclid', 'gclid', 'ref', 'referrer', 'source', 'campaign',
  'mc_cid', 'mc_eid', '_ga', '_gid', '_ym_uid', 'yclid',
  'msclkid', 'igshid', 'si', '_kx'
]);

// Private/reserved IP ranges (RFC 1918 and special purpose)
const BLOCKED_IP_PATTERNS = [
  /^127\./,                    // 127.0.0.0/8 (loopback)
  /^10\./,                     // 10.0.0.0/8 (private)
  /^172\.(1[6-9]|2[0-9]|3[0-1])\./,  // 172.16.0.0/12 (private)
  /^192\.168\./,               // 192.168.0.0/16 (private)
  /^169\.254\./,               // 169.254.0.0/16 (link-local)
  /^0\./,                      // 0.0.0.0/8 (current network)
  /^::1$/,                     // IPv6 loopback
  /^fc00:/i,                   // IPv6 unique local (fc00::/7)
  /^fe80:/i,                   // IPv6 link-local
  /^100\.64\./,                // 100.64.0.0/10 (carrier-grade NAT)
  /^192\.0\.0\./               // 192.0.0.0/24 (reserved)
];

/**
 * Normalize a URL to canonical form
 * Steps:
 * 1. Parse URL
 * 2. Lowercase hostname
 * 3. Remove trailing dot from hostname
 * 4. Remove default ports (:80 for http, :443 for https)
 * 5. Resolve relative paths (done before calling this usually)
 * 6. Remove trailing slash from path
 * 7. Strip tracking parameters
 * 8. Remove fragment
 * 9. Convert IDN to punycode (handled by URL constructor)
 *
 * @param {string} urlStr - URL to normalize (absolute)
 * @returns {string|null} Normalized URL or null if invalid
 */
function normalizeUrl(urlStr) {
  try {
    const parsed = new URL(urlStr);

    // Protocol: only allow http/https
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return null;
    }

    // Lowercase hostname
    parsed.hostname = parsed.hostname.toLowerCase();

    // Remove trailing dot (shouldn't happen but be safe)
    if (parsed.hostname.endsWith('.')) {
      parsed.hostname = parsed.hostname.slice(0, -1);
    }

    // Remove default ports
    if ((parsed.protocol === 'http:' && parsed.port === '80') ||
        (parsed.protocol === 'https:' && parsed.port === '443')) {
      parsed.port = '';
    }

    // Remove trailing slash from pathname (except root "/")
    if (parsed.pathname.length > 1 && parsed.pathname.endsWith('/')) {
      parsed.pathname = parsed.pathname.slice(0, -1);
    }

    // Strip tracking parameters
    for (const param of TRACKING_PARAMS) {
      if (parsed.searchParams.has(param)) {
        parsed.searchParams.delete(param);
      }
    }

    // Remove empty query string
    if (parsed.search === '?') {
      parsed.search = '';
    }

    // Remove fragment
    parsed.hash = '';

    return parsed.toString();
  } catch (e) {
    return null;
  }
}

/**
 * Check if a hostname/IP is in a blocked private range
 * @param {string} hostname - Hostname or IP address
 * @returns {boolean} True if blocked
 */
function isBlockedHost(hostname) {
  // If it's an IPv4 address
  if (/^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
    return BLOCKED_IP_PATTERNS.some(pattern => pattern.test(hostname));
  }

  // If it's an IPv6 address (simplified check)
  if (hostname.includes(':') && /^[0-9a-fA-F:]+$/.test(hostname.replace(/:/g, ''))) {
    // For simplicity, check if hostname looks like IPv6 and matches patterns
    // A full IPv6 parser would be better but this catches common private ranges
    // Also catch IPv6 unique local (fc00::/7) by checking for fc/fd prefix
    if (/^f[cd]/i.test(hostname)) return true;
    return BLOCKED_IP_PATTERNS.some(pattern => pattern.test(hostname));
  }

  // Hostnames (domain names) are not blocked
  return false;
}

/**
 * Check if URL's hostname is in a blocked IP range
 * @param {string} urlStr - URL to check
 * @returns {boolean} True if blocked
 */
function isUrlBlocked(urlStr) {
  try {
    const parsed = new URL(urlStr);
    return isBlockedHost(parsed.hostname);
  } catch (e) {
    return true; // Invalid URL is blocked
  }
}

/**
 * Extract hostname from URL and check if it's whitelisted
 * @param {string} urlStr - URL to check
 * @param {Array<string>} whitelist - Array of allowed domains
 * @returns {boolean} True if domain is whitelisted
 */
function isWhitelisted(urlStr, whitelist) {
  try {
    const parsed = new URL(urlStr);
    const hostname = parsed.hostname.toLowerCase();
    
    // Check suffix match: exact or subdomain
    for (const domain of whitelist) {
      const domainLower = domain.toLowerCase();
      if (hostname === domainLower || hostname.endsWith('.' + domainLower)) {
        return true;
      }
    }
    return false;
  } catch (e) {
    return false;
  }
}

module.exports = {
  normalizeUrl,
  isBlockedHost,
  isUrlBlocked,
  isWhitelisted,
  TRACKING_PARAMS,
  BLOCKED_IP_PATTERNS
};
