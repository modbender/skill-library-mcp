export const MANIFEST_PROTOCOL_VERSION = "1.0";

export interface TaskManifest {
  protocol_version: string;
  task_id: string;
  context: {
    relevant_files?: string[];
    constraints?: string[];
    success_criteria?: string[];
  };
  execution_context: {
    worktree_path: string;
    git_base?: string;
    report_path?: string;
  };
}

export function validateManifest(obj: unknown): obj is TaskManifest {
  if (!obj || typeof obj !== "object") return false;
  const m = obj as Record<string, unknown>;
  if (m.protocol_version !== MANIFEST_PROTOCOL_VERSION) return false;
  if (typeof m.task_id !== "string") return false;
  if (!m.context || typeof m.context !== "object") return false;
  if (!m.execution_context || typeof m.execution_context !== "object")
    return false;
  const ec = m.execution_context as Record<string, unknown>;
  return typeof ec.worktree_path === "string";
}
