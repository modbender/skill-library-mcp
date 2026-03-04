/**
 * Default Network Policy — Balanced security for standard OpenClaw skill usage.
 *
 * Allows common development ports (3000-3999, 8000-8999) inbound,
 * standard web ports (80, 443, 8080) outbound, with all detection enabled.
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

export const DEFAULT_NETWORK_POLICY: NetworkPolicyConfig = {
  networkPolicy: 'default',
  allowedInboundPorts: [...range(3000, 3999), ...range(8000, 8999)],
  allowedOutboundPorts: [80, 443, 8080],
  allowedDomains: [],           // No domain restriction (all allowed)
  blockedDomains: [],
  maxConnectionsPerMinute: 60,
  detectPortHijacking: true,
  detectReverseShells: true,
  blockPrivilegedPorts: true,
  blockPrivateNetworks: true,
  logAllActivity: true,
};
