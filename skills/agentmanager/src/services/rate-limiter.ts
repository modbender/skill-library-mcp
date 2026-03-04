export class RateLimitError extends Error {
  readonly code = 'RATE_LIMIT';
  readonly retryable = true;
  readonly suggested_action = 'retry' as const;
  readonly at = 'run';

  constructor(message: string) {
    super(message);
  }
}

import { getConfig } from '../config.js';

export class RateLimiter {
  private readonly runningByOwner = new Map<string, number>();
  private readonly createdByOwner = new Map<string, number[]>();
  private readonly cleanupTimer: NodeJS.Timeout;

  constructor(
    private readonly maxRunningPerOwner = getConfig().TOKENOWNER_MAX_RUNNING,
    private readonly maxPerMinutePerOwner = getConfig().TOKENOWNER_MAX_PER_MINUTE
  ) {
    this.cleanupTimer = setInterval(() => this.cleanup(), 60_000);
    this.cleanupTimer.unref();
  }

  checkAndConsume(owner: string): void {
    const running = this.runningByOwner.get(owner) ?? 0;
    if (running >= this.maxRunningPerOwner) {
      throw new RateLimitError(`Running run limit exceeded for owner ${owner}`);
    }

    const now = Date.now();
    const windowStart = now - 60_000;
    const timestamps = (this.createdByOwner.get(owner) ?? []).filter((ts) => ts >= windowStart);
    if (timestamps.length >= this.maxPerMinutePerOwner) {
      if (timestamps.length === 0 && running === 0) {
        this.createdByOwner.delete(owner);
        this.runningByOwner.delete(owner);
      } else {
        this.createdByOwner.set(owner, timestamps);
      }
      throw new RateLimitError(`Per-minute run creation limit exceeded for owner ${owner}`);
    }

    timestamps.push(now);
    this.createdByOwner.set(owner, timestamps);
    this.runningByOwner.set(owner, running + 1);
  }

  release(owner: string): void {
    const running = Math.max(0, (this.runningByOwner.get(owner) ?? 0) - 1);
    if (running === 0) {
      this.runningByOwner.delete(owner);
    } else {
      this.runningByOwner.set(owner, running);
    }

    const timestamps = (this.createdByOwner.get(owner) ?? []).filter((ts) => ts >= Date.now() - 60_000);
    if (timestamps.length === 0 && running === 0) {
      this.createdByOwner.delete(owner);
    } else {
      this.createdByOwner.set(owner, timestamps);
    }
  }

  private cleanup(): void {
    const windowStart = Date.now() - 60_000;
    for (const owner of new Set([...this.runningByOwner.keys(), ...this.createdByOwner.keys()])) {
      const timestamps = (this.createdByOwner.get(owner) ?? []).filter((ts) => ts >= windowStart);
      const running = this.runningByOwner.get(owner) ?? 0;
      if (timestamps.length === 0) this.createdByOwner.delete(owner);
      else this.createdByOwner.set(owner, timestamps);
      if (running === 0 && timestamps.length === 0) {
        this.runningByOwner.delete(owner);
        this.createdByOwner.delete(owner);
      }
    }
  }
}
