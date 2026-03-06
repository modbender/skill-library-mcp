import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { isSafeTaskId } from "../safe-task-id.js";
import { getWorktreeBasePath } from "./repo.js";
export async function createWorktree(repoPath, taskId, baseBranch = "HEAD") {
    if (!isSafeTaskId(taskId)) {
        throw new Error("Invalid taskId: alphanumeric and hyphens only");
    }
    const basePath = getWorktreeBasePath();
    const worktreeBase = path.join(basePath, taskId);
    if (fs.existsSync(worktreeBase)) {
        throw new Error(`Worktree already exists: ${worktreeBase}`);
    }
    // Use spawnSync with array (no shell) to prevent injection from config-derived basePath or branch names
    const branchName = `openclaw/${taskId}`;
    const result = spawnSync("git", ["worktree", "add", "-b", branchName, worktreeBase, baseBranch], { cwd: repoPath, encoding: "utf-8" });
    if (result.status !== 0) {
        const msg = result.stderr?.trim() || result.error?.message || `exit ${result.status}`;
        throw new Error(`git worktree add failed: ${msg}`);
    }
    return worktreeBase;
}
//# sourceMappingURL=create.js.map