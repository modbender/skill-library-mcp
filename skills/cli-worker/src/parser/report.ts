import fs from "node:fs";
import path from "node:path";

export interface WorkerReport {
  protocol_version?: string;
  task_id?: string;
  execution?: {
    status?: string;
    duration_seconds?: number;
    session_id?: string;
  };
  cognitive_state?: {
    confidence?: number;
    certainty_level?: string;
    blockers?: string[];
    assumptions?: string[];
  };
  artifacts?: {
    files_modified?: string[];
    files_created?: string[];
    files_deleted?: string[];
    test_status?: string;
    git_sha?: string;
  };
}

export function parseReport(reportPath: string): WorkerReport {
  const fullPath = path.resolve(reportPath);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`Report not found: ${fullPath}`);
  }
  const raw = fs.readFileSync(fullPath, "utf-8");
  const data = JSON.parse(raw) as unknown;
  if (!data || typeof data !== "object") {
    throw new Error("Invalid report: not an object");
  }
  const r = data as Record<string, unknown>;
  return {
    protocol_version:
      typeof r.protocol_version === "string" ? r.protocol_version : undefined,
    task_id: typeof r.task_id === "string" ? r.task_id : undefined,
    execution:
      r.execution && typeof r.execution === "object"
        ? {
            status: (r.execution as Record<string, unknown>).status as string,
            duration_seconds: (r.execution as Record<string, unknown>)
              .duration_seconds as number,
            session_id: (r.execution as Record<string, unknown>)
              .session_id as string,
          }
        : undefined,
    cognitive_state:
      r.cognitive_state && typeof r.cognitive_state === "object"
        ? {
            confidence: (r.cognitive_state as Record<string, unknown>)
              .confidence as number,
            certainty_level: (r.cognitive_state as Record<string, unknown>)
              .certainty_level as string,
            blockers: (r.cognitive_state as Record<string, unknown>)
              .blockers as string[],
            assumptions: (r.cognitive_state as Record<string, unknown>)
              .assumptions as string[],
          }
        : undefined,
    artifacts:
      r.artifacts && typeof r.artifacts === "object"
        ? {
            files_modified: (r.artifacts as Record<string, unknown>)
              .files_modified as string[],
            files_created: (r.artifacts as Record<string, unknown>)
              .files_created as string[],
            files_deleted: (r.artifacts as Record<string, unknown>)
              .files_deleted as string[],
            test_status: (r.artifacts as Record<string, unknown>)
              .test_status as string,
            git_sha: (r.artifacts as Record<string, unknown>).git_sha as string,
          }
        : undefined,
  };
}
