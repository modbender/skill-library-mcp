import fs from "node:fs";
import path from "node:path";
import type { TaskInput } from "../types.js";
import type { TaskManifest } from "./schema.js";
import { MANIFEST_PROTOCOL_VERSION } from "./schema.js";

const MANIFEST_FILENAME = "task.manifest.json";
const OPENCLAW_DIR = ".openclaw";

export function writeManifest(
  taskId: string,
  task: TaskInput,
  worktreePath: string,
  reportPath?: string
): string {
  const openclawPath = path.join(worktreePath, OPENCLAW_DIR);
  if (!fs.existsSync(openclawPath)) {
    fs.mkdirSync(openclawPath, { recursive: true });
  }

  const manifest: TaskManifest = {
    protocol_version: MANIFEST_PROTOCOL_VERSION,
    task_id: taskId,
    context: {
      relevant_files: task.relevantFiles,
      constraints: task.constraints,
      success_criteria: task.successCriteria,
    },
    execution_context: {
      worktree_path: worktreePath,
      report_path:
        reportPath ??
        path.join(worktreePath, OPENCLAW_DIR, "kimi-reports", `${taskId}.json`),
    },
  };

  const manifestPath = path.join(openclawPath, MANIFEST_FILENAME);
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), "utf-8");
  return manifestPath;
}
