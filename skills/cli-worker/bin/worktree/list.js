import { execSync } from "node:child_process";
import path from "node:path";
/**
 * Parse output of `git worktree list` and return worktrees under basePath.
 */
export function parseWorktreeListOutput(output, basePath, repoPath) {
    const lines = output.trim().split("\n");
    const result = [];
    const normalizedBase = path.resolve(basePath) + path.sep;
    for (const line of lines) {
        const worktreePath = line.split(/\s+/)[0];
        if (!worktreePath)
            continue;
        const resolved = path.isAbsolute(worktreePath)
            ? path.resolve(worktreePath)
            : path.resolve(repoPath, worktreePath);
        if (!resolved.startsWith(normalizedBase))
            continue;
        const relative = path.relative(basePath, resolved);
        const taskId = relative.split(path.sep)[0] || null;
        result.push({ path: resolved, taskId });
    }
    return result;
}
export async function listWorktrees(repoPath, basePath) {
    const out = execSync("git worktree list", {
        cwd: repoPath,
        encoding: "utf-8",
    });
    return parseWorktreeListOutput(out, basePath, repoPath);
}
//# sourceMappingURL=list.js.map