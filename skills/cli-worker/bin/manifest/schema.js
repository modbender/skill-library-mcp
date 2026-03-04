export const MANIFEST_PROTOCOL_VERSION = "1.0";
export function validateManifest(obj) {
    if (!obj || typeof obj !== "object")
        return false;
    const m = obj;
    if (m.protocol_version !== MANIFEST_PROTOCOL_VERSION)
        return false;
    if (typeof m.task_id !== "string")
        return false;
    if (!m.context || typeof m.context !== "object")
        return false;
    if (!m.execution_context || typeof m.execution_context !== "object")
        return false;
    const ec = m.execution_context;
    return typeof ec.worktree_path === "string";
}
//# sourceMappingURL=schema.js.map