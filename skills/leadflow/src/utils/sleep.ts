/**
 * Sleep utilities
 */

/**
 * Sleep for a given number of milliseconds
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Sleep for a random duration within a range
 */
export function sleepRandom(minMs: number, maxMs: number): Promise<void> {
  const ms = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  return sleep(ms);
}

/**
 * Add jitter to a base delay
 */
export function addJitter(baseMs: number, jitterPercent: number = 0.2): number {
  const jitter = baseMs * jitterPercent * (Math.random() * 2 - 1);
  return Math.max(0, baseMs + jitter);
}
