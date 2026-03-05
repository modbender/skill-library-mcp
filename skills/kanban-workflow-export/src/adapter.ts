import type { WorkItem } from './models.js';

/**
 * Port interface for a platform adapter.
 *
 * Adapters MUST rely on platform CLIs (gh, planka-cli, etc.) for auth/session.
 * The Clawban core never handles HTTP auth tokens directly.
 */
export interface Adapter {
  /** Return the current snapshot of tracked work items (id -> WorkItem). */
  fetchSnapshot(): Promise<ReadonlyMap<string, WorkItem> | Readonly<Record<string, WorkItem>>>;

  /** Human-readable adapter name (for logging/telemetry). */
  name(): string;
}
