import { loadConfig } from '../config/loader.js';

// Private IP ranges to block
const PRIVATE_IP_PATTERNS = [
  /^127\./, // Loopback
  /^10\./, // Private Class A
  /^172\.(1[6-9]|2[0-9]|3[01])\./, // Private Class B
  /^192\.168\./, // Private Class C
  /^169\.254\./, // Link-local
  /^0\./, // Current network
  /^::1$/, // IPv6 loopback
  /^fc00:/i, // IPv6 unique local
  /^fe80:/i, // IPv6 link-local
];

const BLOCKED_HOSTS = [
  'localhost',
  '*.internal',
  '*.local',
  '*.intranet',
];

export function isHostAllowed(url: string): { allowed: boolean; reason?: string } {
  const config = loadConfig();
  const network = config.security.network;

  try {
    const hostname = new URL(url).hostname.toLowerCase();

    // Check explicit allow-list
    if (network.allowedHosts.length > 0) {
      const isAllowed = network.allowedHosts.some(pattern => {
        if (pattern.startsWith('*.')) {
          const suffix = pattern.slice(2);
          return hostname.endsWith(suffix);
        }
        return hostname === pattern;
      });

      if (!isAllowed) {
        return { allowed: false, reason: `Host "${hostname}" not in allow-list` };
      }
    }

    // Block localhost
    if (network.blockLocalhost) {
      if (hostname === 'localhost') {
        return { allowed: false, reason: 'Localhost connections are blocked' };
      }
    }

    // Block private IPs
    if (network.blockPrivateIps) {
      for (const pattern of PRIVATE_IP_PATTERNS) {
        if (pattern.test(hostname)) {
          return { allowed: false, reason: 'Private IP addresses are blocked' };
        }
      }
    }

    // Block sensitive host patterns
    for (const blocked of BLOCKED_HOSTS) {
      if (blocked.startsWith('*.')) {
        const suffix = blocked.slice(2);
        if (hostname.endsWith(suffix)) {
          return { allowed: false, reason: `Domain pattern "${blocked}" is blocked` };
        }
      } else if (hostname === blocked) {
        return { allowed: false, reason: `Host "${blocked}" is blocked` };
      }
    }

    return { allowed: true };
  } catch (e) {
    return { allowed: false, reason: `Invalid URL: ${url}` };
  }
}

export function validateUrl(url: string): { valid: boolean; error?: string } {
  // Allow welcome page (local file) - it's rendered via setContent, not actually navigated
  if (url.startsWith('file://') && url.includes('welcome.html')) {
    return { valid: true };
  }

  const networkCheck = isHostAllowed(url);
  if (!networkCheck.allowed) {
    return { valid: false, error: networkCheck.reason };
  }

  try {
    const parsed = new URL(url);
    
    // Only allow http/https
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return { valid: false, error: `Protocol "${parsed.protocol}" is not allowed` };
    }

    return { valid: true };
  } catch (e) {
    return { valid: false, error: 'Invalid URL format' };
  }
}
