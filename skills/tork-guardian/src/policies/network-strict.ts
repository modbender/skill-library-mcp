/**
 * Strict Network Policy — Enterprise lockdown for high-security environments.
 *
 * Minimal inbound ports (3000-3010), TLS-only outbound (443),
 * explicit domain allowlist, and tight rate limiting.
 */

import { NetworkPolicyConfig } from '../config';

// Generate port ranges
function range(start: number, end: number): number[] {
  const ports: number[] = [];
  for (let i = start; i <= end; i++) {
    ports.push(i);
  }
  return ports;
}

export const STRICT_NETWORK_POLICY: NetworkPolicyConfig = {
  networkPolicy: 'strict',
  allowedInboundPorts: range(3000, 3010),
  allowedOutboundPorts: [443],          // TLS only
  allowedDomains: [
    'api.openai.com',
    'api.anthropic.com',
    'tork.network',
    'tork.network',
    'api.tork.network',
    'registry.npmjs.org',
    'github.com',
    'api.github.com',
  ],
  blockedDomains: [],
  maxConnectionsPerMinute: 20,          // Tight limit
  detectPortHijacking: true,
  detectReverseShells: true,
  blockPrivilegedPorts: true,
  blockPrivateNetworks: true,
  logAllActivity: true,
};
