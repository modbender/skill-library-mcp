/** Thrown inside pre-hooks to signal OpenClaw should block the request. */
export class ShieldBlockedError extends Error {
  public readonly verdict: string;
  public readonly threatLevel: string;
  public readonly threats: ReadonlyArray<{ category: string; description: string }>;

  constructor(opts: {
    verdict: string;
    threatLevel: string;
    threats: Array<{ category: string; description: string }>;
    phase: string;
  }) {
    const summary = opts.threats.map(t => t.category).join(", ");
    super(`[ZugaShield] Blocked in ${opts.phase}: ${summary} (${opts.threatLevel})`);
    this.name = "ShieldBlockedError";
    this.verdict = opts.verdict;
    this.threatLevel = opts.threatLevel;
    this.threats = opts.threats;
  }
}

/** Thrown when the MCP server is unreachable and fail_closed is enabled. */
export class ShieldUnavailableError extends Error {
  constructor(reason: string) {
    super(`[ZugaShield] Scanner unavailable: ${reason}`);
    this.name = "ShieldUnavailableError";
  }
}
