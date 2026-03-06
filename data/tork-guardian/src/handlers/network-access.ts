/**
 * Network Access Handler — Core network governance for OpenClaw skills.
 *
 * Validates port bindings, egress connections, and DNS lookups against
 * the active network policy. Detects port hijacking, SSRF attempts,
 * reverse shells, and raw IP C2 channels.
 */

import { TorkConfig, NetworkDecision, NetworkActivityLog } from '../config';
import { TorkClient } from '../client';
import { NetworkMonitor } from '../utils/network-monitor';
import { DEFAULT_NETWORK_POLICY } from '../policies/network-default';
import { STRICT_NETWORK_POLICY } from '../policies/network-strict';
import type { NetworkPolicyConfig } from '../config';

/** Resolve the active network policy from TorkConfig. */
function resolvePolicy(config: TorkConfig): NetworkPolicyConfig {
  if (config.networkPolicy === 'strict') return STRICT_NETWORK_POLICY;
  if (config.networkPolicy === 'default') return DEFAULT_NETWORK_POLICY;

  // 'custom' — merge user-supplied values over the default policy
  return {
    ...DEFAULT_NETWORK_POLICY,
    networkPolicy: 'custom' as const,
    ...(config.allowedInboundPorts && { allowedInboundPorts: config.allowedInboundPorts }),
    ...(config.allowedOutboundPorts && { allowedOutboundPorts: config.allowedOutboundPorts }),
    ...(config.allowedDomains && { allowedDomains: config.allowedDomains }),
    ...(config.blockedDomains && { blockedDomains: config.blockedDomains }),
    ...(config.maxConnectionsPerMinute !== undefined && { maxConnectionsPerMinute: config.maxConnectionsPerMinute }),
  };
}

// Private-network CIDRs (for SSRF prevention)
const PRIVATE_NETWORK_PATTERNS: RegExp[] = [
  /^127\./,
  /^10\./,
  /^172\.(1[6-9]|2\d|3[01])\./,
  /^192\.168\./,
  /^169\.254\./,
  /^0\./,
  /^::1$/,
  /^fc00:/i,
  /^fe80:/i,
  /^localhost$/i,
];

function isPrivateNetwork(host: string): boolean {
  return PRIVATE_NETWORK_PATTERNS.some((p) => p.test(host));
}

function isRawIP(host: string): boolean {
  return /^\d{1,3}(\.\d{1,3}){3}$/.test(host) || /^[0-9a-f:]+$/i.test(host);
}

export class NetworkAccessHandler {
  private policy: NetworkPolicyConfig;
  private monitor: NetworkMonitor;
  private client: TorkClient | null;
  private activityLog: NetworkActivityLog[] = [];

  constructor(config: TorkConfig, client?: TorkClient) {
    this.policy = resolvePolicy(config);
    this.monitor = new NetworkMonitor();
    this.client = client ?? null;
  }

  getMonitor(): NetworkMonitor {
    return this.monitor;
  }

  // ── Port binding governance ──────────────────────────────────

  validatePortBind(skillId: string, port: number, protocol: 'tcp' | 'udp' = 'tcp'): NetworkDecision {
    // Block privileged ports
    if (this.policy.blockPrivilegedPorts && port < 1024) {
      return this.deny(skillId, 'port_bind', `Privileged port ${port} is blocked (< 1024)`);
    }

    // Check allowlist
    if (!this.policy.allowedInboundPorts.includes(port)) {
      return this.deny(skillId, 'port_bind', `Port ${port} is not in the inbound allowlist`);
    }

    // Port hijacking detection
    if (this.policy.detectPortHijacking) {
      const existing = this.monitor.getPortOwner(port);
      if (existing && existing.skillId !== skillId) {
        const msg = `Port hijacking detected: port ${port} is owned by skill "${existing.skillId}", attempted by "${skillId}"`;
        this.reportThreat(skillId, 'port_hijacking', msg);
        return this.deny(skillId, 'port_bind', msg);
      }
    }

    // Register the binding
    this.monitor.registerPort(port, protocol, skillId);
    return this.allow(skillId, 'port_bind', `Port ${port}/${protocol} bound`);
  }

  // ── Egress governance ────────────────────────────────────────

  validateEgress(skillId: string, host: string, port: number): NetworkDecision {
    // SSRF prevention — block private networks
    if (this.policy.blockPrivateNetworks && isPrivateNetwork(host)) {
      return this.deny(skillId, 'egress', `Private network access blocked: ${host}`);
    }

    // Outbound port allowlist
    if (!this.policy.allowedOutboundPorts.includes(port)) {
      return this.deny(skillId, 'egress', `Outbound port ${port} is not allowed`);
    }

    // Domain blocklist
    if (this.policy.blockedDomains.length > 0) {
      const blocked = this.policy.blockedDomains.some(
        (d) => host === d || host.endsWith(`.${d}`),
      );
      if (blocked) {
        return this.deny(skillId, 'egress', `Domain "${host}" is blocked`);
      }
    }

    // Domain allowlist (only enforced when non-empty)
    if (this.policy.allowedDomains.length > 0) {
      const allowed = this.policy.allowedDomains.some(
        (d) => host === d || host.endsWith(`.${d}`),
      );
      if (!allowed) {
        return this.deny(skillId, 'egress', `Domain "${host}" is not in the allowlist`);
      }
    }

    // Reverse-shell detection: check recent shell activity
    if (this.policy.detectReverseShells) {
      const shellCheck = this.monitor.checkRecentShellActivity(skillId);
      if (shellCheck.suspicious) {
        const msg = `Reverse shell pattern detected for skill "${skillId}" during egress to ${host}:${port}`;
        this.reportThreat(skillId, 'reverse_shell', msg);
        return this.deny(skillId, 'egress', msg);
      }
    }

    // Rate limiting
    const currentRate = this.monitor.getConnectionsPerMinute(skillId);
    if (currentRate >= this.policy.maxConnectionsPerMinute) {
      return this.deny(
        skillId,
        'egress',
        `Rate limit exceeded: ${currentRate}/${this.policy.maxConnectionsPerMinute} connections/min`,
      );
    }

    // Record the connection
    this.monitor.recordConnection(host, port, skillId);
    return this.allow(skillId, 'egress', `Egress to ${host}:${port} allowed`);
  }

  // ── DNS governance ───────────────────────────────────────────

  validateDNS(skillId: string, hostname: string): NetworkDecision {
    // Flag raw IP usage
    if (isRawIP(hostname)) {
      const decision = this.deny(
        skillId,
        'dns',
        `Raw IP address "${hostname}" used instead of hostname — potential SSRF or C2 channel`,
      );
      this.reportThreat(skillId, 'raw_ip_usage', decision.reason!);
      return decision;
    }

    // Domain blocklist
    if (this.policy.blockedDomains.length > 0) {
      const blocked = this.policy.blockedDomains.some(
        (d) => hostname === d || hostname.endsWith(`.${d}`),
      );
      if (blocked) {
        return this.deny(skillId, 'dns', `DNS lookup for blocked domain: ${hostname}`);
      }
    }

    // Domain allowlist
    if (this.policy.allowedDomains.length > 0) {
      const allowed = this.policy.allowedDomains.some(
        (d) => hostname === d || hostname.endsWith(`.${d}`),
      );
      if (!allowed) {
        return this.deny(skillId, 'dns', `DNS lookup for domain not in allowlist: ${hostname}`);
      }
    }

    return this.allow(skillId, 'dns', `DNS lookup for ${hostname} allowed`);
  }

  // ── Activity log & reporting ─────────────────────────────────

  getActivityLog(): ReadonlyArray<NetworkActivityLog> {
    return this.activityLog;
  }

  clearActivityLog(): void {
    this.activityLog = [];
  }

  // ── Private helpers ──────────────────────────────────────────

  private allow(skillId: string, action: string, reason: string): NetworkDecision {
    const entry: NetworkActivityLog = {
      timestamp: new Date().toISOString(),
      skillId,
      action,
      allowed: true,
      reason,
    };
    if (this.policy.logAllActivity) {
      this.activityLog.push(entry);
    }
    return { allowed: true, reason };
  }

  private deny(skillId: string, action: string, reason: string): NetworkDecision {
    const entry: NetworkActivityLog = {
      timestamp: new Date().toISOString(),
      skillId,
      action,
      allowed: false,
      reason,
    };
    this.activityLog.push(entry); // always log denials
    return { allowed: false, reason };
  }

  private reportThreat(skillId: string, type: string, detail: string): void {
    if (!this.client) return;
    // Fire-and-forget threat report to Tork Cloud
    this.client
      .govern(`[THREAT] skill=${skillId} type=${type} detail=${detail}`)
      .catch(() => {
        /* best-effort */
      });
  }
}

// ── Standalone convenience functions ─────────────────────────────

export function validatePortBind(
  config: TorkConfig,
  skillId: string,
  port: number,
  protocol: 'tcp' | 'udp' = 'tcp',
): NetworkDecision {
  const handler = new NetworkAccessHandler(config);
  return handler.validatePortBind(skillId, port, protocol);
}

export function validateEgress(
  config: TorkConfig,
  skillId: string,
  host: string,
  port: number,
): NetworkDecision {
  const handler = new NetworkAccessHandler(config);
  return handler.validateEgress(skillId, host, port);
}

export function validateDNS(
  config: TorkConfig,
  skillId: string,
  hostname: string,
): NetworkDecision {
  const handler = new NetworkAccessHandler(config);
  return handler.validateDNS(skillId, hostname);
}
