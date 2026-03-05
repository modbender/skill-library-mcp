import path from "node:path";
/**
 * TaskIds are generated as UUIDs (execute.ts) or single path segments from
 * git worktree list. Reject anything that could be path traversal.
 * Allowed: alphanumeric and hyphens only, 1–200 chars (UUID is 36).
 */
const SAFE_TASK_ID_REGEX = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,199}$/;
export function isSafeTaskId(taskId) {
    if (typeof taskId !== "string" || taskId.length === 0)
        return false;
    return SAFE_TASK_ID_REGEX.test(taskId);
}
/**
 * Resolve basePath + taskId and ensure the result is under basePath (no path
 * traversal). Returns the resolved path or null if invalid.
 */
export function resolveTaskIdPath(basePath, taskId) {
    if (!isSafeTaskId(taskId))
        return null;
    const base = path.resolve(basePath);
    const resolved = path.resolve(base, taskId);
    const baseWithSep = base.endsWith(path.sep) ? base : base + path.sep;
    if (resolved !== base && !resolved.startsWith(baseWithSep))
        return null;
    return resolved;
}
//# sourceMappingURL=safe-task-id.js.map