/**
 * Network Monitor — Port state tracking utility for Tork Guardian
 *
 * Tracks port bindings, outbound connections, and shell commands.
 * Detects reverse shell patterns and anomalous network activity.
 */

export interface PortBinding {
  port: number;
  protocol: 'tcp' | 'udp';
  skillId: string;
  boundAt: number;
}

export interface ConnectionRecord {
  host: string;
  port: number;
  skillId: string;
  timestamp: number;
}

export interface ShellRecord {
  command: string;
  skillId: string;
  timestamp: number;
}

export interface NetworkReport {
  timestamp: string;
  activePorts: PortBinding[];
  recentConnections: ConnectionRecord[];
  recentShellCommands: ShellRecord[];
  connectionRatePerMinute: number;
  anomalies: string[];
}

// Reverse shell detection patterns
const REVERSE_SHELL_PATTERNS: RegExp[] = [
  /bash\s+-i\s+.*\/dev\/tcp/i,
  /nc\s+(-e|-c)\s/i,
  /ncat\s+(-e|-c)\s/i,
  /socat\s+.*exec/i,
  /python.*socket.*connect/i,
  /perl.*socket.*connect/i,
  /ruby.*TCPSocket/i,
  /php.*fsockopen/i,
  /powershell.*New-Object\s+Net\.Sockets/i,
  /mkfifo.*nc\s/i,
  /\/dev\/tcp\//i,
];

// Data retention window (5 minutes)
const RETENTION_MS = 5 * 60 * 1000;

export class NetworkMonitor {
  private startupPorts: Set<number> = new Set();
  private portBindings: Map<number, PortBinding> = new Map();
  private connections: ConnectionRecord[] = [];
  private shellCommands: ShellRecord[] = [];

  /**
   * Snapshot active ports at startup for baseline comparison.
   * Ports appearing later that weren't in the snapshot are flagged as anomalies.
   */
  snapshotStartupPorts(ports: number[]): void {
    this.startupPorts = new Set(ports);
  }

  getStartupPorts(): ReadonlySet<number> {
    return this.startupPorts;
  }

  /**
   * Register a port binding for a skill.
   */
  registerPort(port: number, protocol: 'tcp' | 'udp', skillId: string): void {
    this.portBindings.set(port, {
      port,
      protocol,
      skillId,
      boundAt: Date.now(),
    });
  }

  /**
   * Unregister a port binding.
   */
  unregisterPort(port: number): void {
    this.portBindings.delete(port);
  }

  /**
   * Get the current owner of a port.
   */
  getPortOwner(port: number): PortBinding | undefined {
    return this.portBindings.get(port);
  }

  /**
   * Get all currently active port bindings.
   */
  getActivePorts(): PortBinding[] {
    return Array.from(this.portBindings.values());
  }

  /**
   * Record an outbound connection for rate tracking.
   */
  recordConnection(host: string, port: number, skillId: string): void {
    this.pruneOldRecords();
    this.connections.push({
      host,
      port,
      skillId,
      timestamp: Date.now(),
    });
  }

  /**
   * Get the outbound connection rate (connections per minute).
   * Optionally filter by skillId.
   */
  getConnectionsPerMinute(skillId?: string): number {
    const oneMinuteAgo = Date.now() - 60_000;
    const recent = this.connections.filter(
      (c) => c.timestamp > oneMinuteAgo && (!skillId || c.skillId === skillId)
    );
    return recent.length;
  }

  /**
   * Record a shell command execution for reverse shell detection.
   */
  recordShellCommand(command: string, skillId: string): void {
    this.pruneOldRecords();
    this.shellCommands.push({
      command,
      skillId,
      timestamp: Date.now(),
    });
  }

  /**
   * Check recent shell activity for reverse shell patterns.
   * Returns whether suspicious activity was detected and the matching patterns.
   */
  checkRecentShellActivity(skillId?: string): { suspicious: boolean; matches: string[] } {
    const oneMinuteAgo = Date.now() - 60_000;
    const recent = this.shellCommands.filter(
      (s) => s.timestamp > oneMinuteAgo && (!skillId || s.skillId === skillId)
    );

    const matches: string[] = [];
    for (const record of recent) {
      for (const pattern of REVERSE_SHELL_PATTERNS) {
        if (pattern.test(record.command)) {
          matches.push(record.command);
          break;
        }
      }
    }

    return {
      suspicious: matches.length > 0,
      matches,
    };
  }

  /**
   * Generate a comprehensive network report for compliance.
   */
  getNetworkReport(): NetworkReport {
    this.pruneOldRecords();

    const anomalies: string[] = [];

    // Check for ports opened after startup
    for (const binding of this.portBindings.values()) {
      if (!this.startupPorts.has(binding.port)) {
        anomalies.push(
          `Port ${binding.port} opened after startup by skill ${binding.skillId}`
        );
      }
    }

    // Check for high connection rate
    const rate = this.getConnectionsPerMinute();
    if (rate > 100) {
      anomalies.push(`High connection rate: ${rate} connections/min`);
    }

    // Check for reverse shell patterns
    const shellCheck = this.checkRecentShellActivity();
    if (shellCheck.suspicious) {
      anomalies.push(
        `Reverse shell patterns detected: ${shellCheck.matches.length} suspicious commands`
      );
    }

    return {
      timestamp: new Date().toISOString(),
      activePorts: this.getActivePorts(),
      recentConnections: [...this.connections],
      recentShellCommands: [...this.shellCommands],
      connectionRatePerMinute: rate,
      anomalies,
    };
  }

  /**
   * Reset all tracked state.
   */
  reset(): void {
    this.startupPorts.clear();
    this.portBindings.clear();
    this.connections = [];
    this.shellCommands = [];
  }

  /**
   * Remove records older than the retention window.
   */
  private pruneOldRecords(): void {
    const cutoff = Date.now() - RETENTION_MS;
    this.connections = this.connections.filter((c) => c.timestamp > cutoff);
    this.shellCommands = this.shellCommands.filter((s) => s.timestamp > cutoff);
  }
}
