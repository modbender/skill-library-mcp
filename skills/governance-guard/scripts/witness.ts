/**
 * Hash-chained witness log: tamper-evident audit trail.
 *
 * Every governance decision produces a WitnessRecord appended to a JSONL file.
 * Records are hash-chained: any tampering invalidates all subsequent hashes.
 */

import { readFile, appendFile, writeFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";
import type { ActionIntent } from "./intent.js";
import { computeHash, canonicalize } from "./intent.js";
import type { Verdict } from "./policy-engine.js";

// ── Types ────────────────────────────────────────────────────────────

export type ExecutionStatus =
  | "executed"
  | "blocked"
  | "escalated"
  | "user_approved"
  | "user_denied";

export interface ExecutionResult {
  status: ExecutionStatus;
  timestamp: string;
}

export interface WitnessRecord {
  sequence: number;
  intent: ActionIntent;
  verdict: Verdict;
  execution_result: ExecutionResult;
  prev_hash: string;
  record_hash: string;
}

// ── Constants ────────────────────────────────────────────────────────

const GENESIS_HASH = computeHash("governance-guard:genesis:v0.1");

// ── Hash computation ─────────────────────────────────────────────────

export function computeRecordHash(
  sequence: number,
  intentHash: string,
  verdictHash: string,
  executionResult: ExecutionResult,
  prevHash: string,
): string {
  return computeHash(
    canonicalize({
      execution_result: executionResult,
      intent_hash: intentHash,
      prev_hash: prevHash,
      sequence,
      verdict_hash: verdictHash,
    }),
  );
}

// ── WitnessLog implementation ────────────────────────────────────────

export interface WitnessLog {
  append(
    intent: ActionIntent,
    verdict: Verdict,
    status: ExecutionStatus,
  ): Promise<WitnessRecord>;
  getLatest(): WitnessRecord | null;
  getLast(n: number): WitnessRecord[];
  getByIntentId(id: string): WitnessRecord | null;
  verifyChain(): { valid: boolean; brokenAt?: number; reason?: string };
  getSequence(): number;
}

class WitnessLogImpl implements WitnessLog {
  private records: WitnessRecord[] = [];
  private intentIndex = new Map<string, number>();

  constructor(private filePath: string) {}

  /** Load existing records from JSONL file. Skips malformed trailing lines. */
  async load(): Promise<void> {
    let content: string;
    try {
      content = await readFile(this.filePath, "utf8");
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code === "ENOENT") {
        // File doesn't exist yet — start fresh
        await mkdir(dirname(this.filePath), { recursive: true });
        await writeFile(this.filePath, "", "utf8");
        return;
      }
      throw err;
    }

    if (content.trim() === "") return;

    const lines = content.trim().split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]!.trim();
      if (line === "") continue;
      try {
        const record = JSON.parse(line) as WitnessRecord;
        this.records.push(record);
        this.intentIndex.set(record.intent.id, i);
      } catch {
        // Skip malformed trailing lines (partial write recovery)
        // Only tolerate malformed lines at the end
        if (i < lines.length - 1) {
          throw new Error(`Malformed witness record at line ${i + 1} (not trailing)`);
        }
      }
    }
  }

  async append(
    intent: ActionIntent,
    verdict: Verdict,
    status: ExecutionStatus,
  ): Promise<WitnessRecord> {
    const sequence = this.records.length;
    const prevHash =
      sequence === 0 ? GENESIS_HASH : this.records[sequence - 1]!.record_hash;

    const executionResult: ExecutionResult = {
      status,
      timestamp: new Date().toISOString(),
    };

    const recordHash = computeRecordHash(
      sequence,
      intent.intent_hash,
      verdict.verdict_hash,
      executionResult,
      prevHash,
    );

    const record: WitnessRecord = {
      sequence,
      intent,
      verdict,
      execution_result: executionResult,
      prev_hash: prevHash,
      record_hash: recordHash,
    };

    // Append to file (JSONL: one record per line)
    const line = JSON.stringify(record) + "\n";
    await appendFile(this.filePath, line, "utf8");

    // Update in-memory state
    this.records.push(record);
    this.intentIndex.set(intent.id, sequence);

    return record;
  }

  getLatest(): WitnessRecord | null {
    return this.records.length > 0 ? this.records[this.records.length - 1]! : null;
  }

  getLast(n: number): WitnessRecord[] {
    const start = Math.max(0, this.records.length - n);
    return this.records.slice(start);
  }

  getByIntentId(id: string): WitnessRecord | null {
    const idx = this.intentIndex.get(id);
    return idx !== undefined ? this.records[idx] ?? null : null;
  }

  verifyChain(): { valid: boolean; brokenAt?: number; reason?: string } {
    if (this.records.length === 0) return { valid: true };

    let expectedPrevHash = GENESIS_HASH;

    for (let i = 0; i < this.records.length; i++) {
      const record = this.records[i]!;

      // Verify prev_hash chain
      if (record.prev_hash !== expectedPrevHash) {
        return {
          valid: false,
          brokenAt: i,
          reason: `prev_hash mismatch at sequence ${i}: expected ${expectedPrevHash}, got ${record.prev_hash}`,
        };
      }

      // Verify record_hash
      const computed = computeRecordHash(
        record.sequence,
        record.intent.intent_hash,
        record.verdict.verdict_hash,
        record.execution_result,
        record.prev_hash,
      );

      if (record.record_hash !== computed) {
        return {
          valid: false,
          brokenAt: i,
          reason: `record_hash mismatch at sequence ${i}: expected ${computed}, got ${record.record_hash}`,
        };
      }

      expectedPrevHash = record.record_hash;
    }

    return { valid: true };
  }

  getSequence(): number {
    return this.records.length;
  }
}

// ── Factory ──────────────────────────────────────────────────────────

export async function openWitnessLog(filePath: string): Promise<WitnessLog> {
  const log = new WitnessLogImpl(filePath);
  await log.load();
  return log;
}

export { GENESIS_HASH };
